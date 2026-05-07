# DataKit Common Flow Patterns

Complete YAML examples for frequently needed DataKit configurations. Each pattern shows the `config.nodes` array (and `resources` when needed). Wrap in the standard plugin config structure:

```yaml
plugins:
  - name: datakit
    service: YOUR_SERVICE    # or route: YOUR_ROUTE
    config:
      nodes: [...]           # patterns below
      resources: {}          # when needed
```

---

## 1. Combine Multiple APIs

Fetch data from two APIs concurrently, merge results with jq, and return a combined response.

```yaml
nodes:
  - name: USERS
    type: call
    url: https://api.example.com/users

  - name: ORDERS
    type: call
    url: https://api.example.com/orders

  - name: MERGE
    type: jq
    inputs:
      users: USERS.body
      orders: ORDERS.body
    jq: |
      {
        users: .users,
        orders: .orders,
        summary: {
          total_users: (.users | length),
          total_orders: (.orders | length)
        }
      }

  - name: EXIT
    type: exit
    inputs:
      body: MERGE
    status: 200
```

**How it works:** USERS and ORDERS execute concurrently (no dependency between them). MERGE waits for both, combines their bodies, and EXIT returns the result to the client.

---

## 2. Third-Party Authentication (Token Injection)

Fetch an auth token from an identity provider and inject it as a header on the upstream request.

```yaml
nodes:
  - name: CREDENTIALS
    type: static
    values:
      client_id: "my-client-id"
      client_secret: "my-client-secret"

  - name: BUILD_AUTH_BODY
    type: jq
    input: CREDENTIALS
    jq: |
      {
        grant_type: "client_credentials",
        client_id: .client_id,
        client_secret: .client_secret
      }

  - name: GET_TOKEN
    type: call
    method: POST
    url: https://auth.example.com/oauth/token
    inputs:
      body: BUILD_AUTH_BODY

  - name: BUILD_HEADER
    type: jq
    input: GET_TOKEN.body
    jq: |
      { "Authorization": ("Bearer " + .access_token) }

  - name: SET_AUTH_HEADER
    type: property
    property: kong.ctx.shared.auth_headers
    input: BUILD_HEADER
```

**How it works:** Static credentials feed into a jq node that builds the OAuth request body. The call node fetches a token. Another jq node formats the Authorization header. Finally, a property node sets it on the shared context (or connect to `service_request.headers` to set directly).

**Variant — using vault for secrets:**
```yaml
resources:
  vault:
    client_id: "{vault://env/my-client-id}"
    client_secret: "{vault://env/my-client-secret}"

nodes:
  - name: BUILD_AUTH_BODY
    type: jq
    inputs:
      cid: vault.client_id
      csecret: vault.client_secret
    jq: |
      {
        grant_type: "client_credentials",
        client_id: .cid,
        client_secret: .csecret
      }
  # ... rest of flow same as above
```

---

## 3. Conditional Caching

Check cache before making an expensive API call. On miss, call the API and store the result.

```yaml
resources:
  cache:
    strategy: memory

nodes:
  - name: CACHE_KEY
    type: jq
    input: request.query
    jq: |
      "product:" + .product_id

  - name: CACHE_GET
    type: cache
    inputs:
      key: CACHE_KEY

  - name: CHECK_MISS
    type: branch
    input: CACHE_GET.miss
    outputs:
      then:
        - FETCH_DATA
        - CACHE_SET
      else: []

  - name: FETCH_DATA
    type: call
    url: https://api.example.com/products
    inputs:
      query: request.query

  - name: CACHE_SET
    type: cache
    ttl: 300
    inputs:
      key: CACHE_KEY
      data: FETCH_DATA.body

  - name: PICK_RESULT
    type: jq
    inputs:
      cached: CACHE_GET.data
      fresh: FETCH_DATA.body
      was_hit: CACHE_GET.hit
    jq: |
      if .was_hit then .cached else .fresh end

  - name: EXIT
    type: exit
    inputs:
      body: PICK_RESULT
    status: 200
```

**How it works:** A jq node builds the cache key from query params. CACHE_GET does a lookup. The branch node checks `.miss` — on miss, it schedules FETCH_DATA and CACHE_SET. PICK_RESULT selects either cached or fresh data. EXIT returns the result.

---

## 4. XML/JSON Conversion

Call an XML API, convert to JSON, transform, and return.

```yaml
nodes:
  - name: FETCH_XML
    type: call
    url: https://api.example.com/data.xml
    method: GET

  - name: PARSE_XML
    type: xml_to_json
    input: FETCH_XML.body

  - name: TRANSFORM
    type: jq
    input: PARSE_XML
    jq: |
      {
        items: [.catalog.products[].product | {
          name: .name,
          price: .price | tonumber,
          in_stock: (.quantity | tonumber) > 0
        }]
      }

  - name: EXIT
    type: exit
    inputs:
      body: TRANSFORM
    status: 200
```

**Reverse direction (JSON to XML):**
```yaml
nodes:
  - name: BUILD_PAYLOAD
    type: jq
    input: request.body
    jq: |
      {
        order: {
          id: .order_id,
          items: [.items[] | {item: {name: .name, qty: .quantity}}]
        }
      }

  - name: TO_XML
    type: json_to_xml
    input: BUILD_PAYLOAD
    root_element_name: "OrderRequest"

  - name: SEND_XML
    type: call
    method: POST
    url: https://legacy.example.com/orders
    inputs:
      body: TO_XML
      headers:
        content_type: "application/xml"
```

---

## 5. Dynamic URL Resolution

Build a URL dynamically from request parameters and call it.

```yaml
nodes:
  - name: BUILD_URL
    type: jq
    inputs:
      query: request.query
      headers: request.headers
    jq: |
      "https://api.example.com/v2/"
      + .query.resource_type
      + "/"
      + .query.resource_id
      + "?format=json&locale="
      + (.headers["Accept-Language"] // "en")

  - name: FETCH
    type: call
    method: GET
    url: https://api.example.com/fallback
    inputs:
      url: BUILD_URL

  - name: EXIT
    type: exit
    inputs:
      body: FETCH.body
      headers: FETCH.headers
    status: 200
```

**How it works:** The jq node constructs a URL from query parameters and headers. The call node uses `inputs.url` to override its static `url` field (the static URL serves as a fallback if the dynamic input is nil, v3.13+).

---

## 6. Header Manipulation

Read incoming request headers, transform them, and set on the upstream service request.

**Add/modify headers before proxying:**
```yaml
nodes:
  - name: TRANSFORM_HEADERS
    type: jq
    input: request.headers
    jq: |
      . + {
        "X-Request-Source": "datakit",
        "X-Forwarded-Client-Ip": .["X-Real-Ip"],
        "Authorization": ("Basic " + (.["X-Api-Key"] | @base64))
      }
      | del(.["X-Api-Key"])
```

Connect the output to `service_request.headers`:
```yaml
  # In the same nodes array, service_request is implicit:
  # TRANSFORM_HEADERS output → service_request.headers
```

The connection is made by referencing `TRANSFORM_HEADERS` as the input to `service_request.headers`. Since `service_request` is an implicit node, you wire it like:

```yaml
nodes:
  - name: TRANSFORM_HEADERS
    type: jq
    input: request.headers
    jq: |
      . + {
        "X-Request-Source": "datakit",
        "X-Correlation-Id": (now | tostring)
      }
```

Then in the top-level flow, `service_request.headers` receives from `TRANSFORM_HEADERS`:

```yaml
# Full example: modify upstream headers
nodes:
  - name: ADD_HEADERS
    type: jq
    input: request.headers
    jq: |
      . + {
        "X-Gateway": "kong-datakit",
        "X-Timestamp": (now | tostring)
      }

  - name: SET_UPSTREAM_HEADERS
    type: property
    property: kong.ctx.shared.modified_headers
    input: ADD_HEADERS
```

**Strip sensitive headers from response:**
```yaml
nodes:
  - name: CLEAN_RESPONSE_HEADERS
    type: jq
    input: service_response.headers
    jq: |
      del(
        .["X-Powered-By"],
        .["Server"],
        .["X-Debug-Info"]
      )
```

Wire `CLEAN_RESPONSE_HEADERS` → `response.headers` to apply the cleaned headers to the client response.
