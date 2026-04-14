# DataKit Node Type Reference

Complete specifications for all 9 explicit node types and 5 implicit nodes.

---

## Explicit Node Types

### call

Send HTTP requests to external or internal APIs. Executes asynchronously; independent call nodes run concurrently.

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `method` | string | `"GET"` | HTTP method (uppercase: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS) |
| `url` | string | *required* | Target URL (max 255 chars). Can be overridden by `inputs.url` |
| `timeout` | integer | none | Request timeout in milliseconds (0–2,147,483,646) |
| `ssl_verify` | boolean | false | Validate TLS certificates |
| `ssl_server_name` | string | none | SNI value for TLS handshake |

**Inputs:**

| Input | Type | Description |
|-------|------|-------------|
| `url` | string | Dynamic URL (overrides `url` field; v3.13+, falls back to field if nil) |
| `body` | any | Request body (auto JSON-encoded if object/map) |
| `headers` | map | Request headers |
| `query` | map | Query string parameters |
| `https_proxy` | string | HTTPS proxy URL |
| `http_proxy` | string | HTTP proxy URL |
| `proxy_auth_username` | string | Proxy auth username |
| `proxy_auth_password` | string | Proxy auth password |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| `status` | number | HTTP response status code |
| `body` | any | Response body (auto JSON-decoded if Content-Type is JSON) |
| `headers` | map | Response headers |

**Behavior notes:**
- Non-2xx responses are treated as node errors by default
- Body is automatically JSON-encoded on send and JSON-decoded on receive when appropriate
- Multiple call nodes with no interdependencies execute concurrently

---

### jq

Transform data using jq filter expressions.

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `jq` | string | *required* | jq filter expression (max 10,240 chars) |

**Inputs:**

Use `input` for a single input or `inputs` for named multiple inputs:

| Input | Type | Description |
|-------|------|-------------|
| `input` | any | Single input value (accessed as `.` in jq) |
| `inputs` | named map | Multiple named inputs (accessed as `.name` in jq) |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| (default) | any | Result of the jq expression |

**Behavior notes:**
- When using `inputs`, each named input becomes a top-level key in the jq input object
- Output type is checked at runtime against downstream expectations
- Use `input: NODE` for single input, `inputs: {key1: NODE1.field, key2: NODE2.field}` for multiple

---

### exit

Terminate the request pipeline and send an early response directly to the client.

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | integer | `200` | HTTP response status code (200–599) |
| `warn_headers_sent` | boolean | false | Warn if headers already sent to client |

**Inputs:**

| Input | Type | Description |
|-------|------|-------------|
| `body` | any | Response body |
| `headers` | map | Response headers |

**Outputs:** None

**Behavior notes:**
- Stops further processing; the proxied upstream is never called
- Use in pre-proxy phase (access phase) to short-circuit requests
- If used post-proxy, `warn_headers_sent` controls whether a warning is logged when headers have already been sent

---

### property

Get or set Kong Gateway internal properties (request/response metadata, shared context, routing info).

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `property` | string | *required* | Property path (max 255 chars) |
| `content_type` | string | none | Content type hint: `application/json`, `application/octet-stream`, or `text/plain` |

**Inputs:**

| Input | Type | Description |
|-------|------|-------------|
| `input` | any | When connected, node operates in SET mode (writes value to property) |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| (default) | any | When no input connected, node operates in GET mode (reads property value) |

**Mode determination:**
- **GET mode**: No `input` connection → reads the property and outputs its value
- **SET mode**: `input` connected → writes the input value to the property

**Common properties:**

*Read (GET):*
- `kong.client.ip`, `kong.client.port`, `kong.client.protocol`
- `kong.client.consumer` (authenticated consumer)
- `kong.router.route`, `kong.router.service`
- `kong.request.forwarded_host`, `kong.request.forwarded_port`
- `kong.service.response.status`
- `kong.ctx.shared.{key}` (shared context between plugins)
- `kong.configuration.{key}` (gateway configuration values)

*Write (SET):*
- `kong.service.target` (override upstream target)
- `kong.service.request_scheme` (override upstream scheme)
- `kong.ctx.plugin.{key}` (plugin-scoped context)
- `kong.ctx.shared.{key}` (shared context between plugins)

---

### static

Emit hardcoded values defined at configuration time.

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `values` | object | *required* | Key-value pairs of static data (freeform) |

**Inputs:** None

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| `output` | object | The entire `values` object |
| `outputs.{key}` | any | Individual value by key name |

**Example:**
```yaml
- name: CREDENTIALS
  type: static
  values:
    api_key: "sk-abc123"
    base_url: "https://api.example.com"
```

Access as `CREDENTIALS.output` (whole object) or `CREDENTIALS.api_key` (single value).

---

### branch

Conditional execution: run different node sets based on a boolean input. (v3.12+)

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `input` | string | *required* | Source of boolean condition (max 255 chars) |
| `outputs.then` | array | `[]` | Node names to execute when condition is truthy (max 64) |
| `outputs.else` | array | `[]` | Node names to execute when condition is falsy (max 64) |

**Inputs:**

| Input | Type | Description |
|-------|------|-------------|
| `input` | boolean | Condition to evaluate |

**Outputs:** None (branch controls execution flow, not data flow)

**Behavior notes:**
- Nodes listed in `then`/`else` arrays and their transitive dependencies are scheduled for execution
- Branch only controls *which* nodes run; data still flows through normal `input`/`inputs` connections
- Nodes not in either branch path may still execute if they are dependencies of other active nodes

---

### cache

Store and retrieve cached data with TTL support. Requires `resources.cache` configuration. (v3.12+)

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ttl` | integer | none | Default time-to-live in seconds |
| `bypass_on_error` | boolean | false | Continue flow execution if cache operation fails |

**Inputs:**

| Input | Type | Description |
|-------|------|-------------|
| `key` | string | Cache key (required, max 255 chars) |
| `data` | any | Data to store (triggers SET operation when connected) |
| `ttl` | number | Per-operation TTL override (seconds) |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| `hit` | boolean | True if cache key was found |
| `miss` | boolean | True if cache key was not found |
| `stored` | boolean | True if data was successfully stored |
| `data` | any | Retrieved cached data |

**Mode determination:**
- **GET mode**: Only `key` input connected → looks up cache
- **SET mode**: Both `key` and `data` inputs connected → stores data

**Usage pattern:** Use two separate cache nodes — one for GET (lookup), one for SET (store) — with a branch node to conditionally execute the SET path on cache miss.

---

### xml_to_json

Convert XML string data to a JSON object. (v3.13+)

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `xpath` | string | none | XPath filter expression (max 256 chars) |
| `recognize_type` | boolean | `true` | Attempt to recognize and convert data types |
| `text_as_property` | boolean | `false` | Treat text content as a property |
| `text_block_name` | string | `"#text"` | Property name for text content |

**Inputs:**

| Input | Type | Description |
|-------|------|-------------|
| `input` | string | XML string to convert |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| (default) | object | Resulting JSON object |

---

### json_to_xml

Convert a JSON object to an XML string. (v3.13+)

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `root_element_name` | string | none | Root XML element name |
| `text_block_name` | string | `"#text"` | Property name mapped to text content |
| `attributes_block_name` | string | none | Property name containing XML attributes |
| `attributes_name_prefix` | string | none | Prefix for attribute properties |

**Inputs:**

| Input | Type | Description |
|-------|------|-------------|
| `input` | any | JSON object or Lua table to convert |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| (default) | string | Resulting XML string |

**Note:** `attributes_block_name` and `attributes_name_prefix` are mutually exclusive — use one or the other to map JSON keys to XML attributes.

---

## Implicit Nodes

Implicit nodes are automatically available in every DataKit flow. They represent the current request/response lifecycle stages. You do not define them in `config.nodes`; reference them directly by name.

### request

The incoming client request (read-only in access phase).

| Output | Type | Description |
|--------|------|-------------|
| `body` | any | Request body |
| `headers` | map | Request headers |
| `query` | map | Query string parameters |

**Usage:** `input: request.body`, `input: request.headers`

### service_request

The request being sent to the upstream service (writable — modify before proxying).

| Input | Type | Description |
|-------|------|-------------|
| `body` | any | Override upstream request body |
| `headers` | map | Override upstream request headers |
| `query` | map | Override upstream query parameters |

**Usage:** Connect a node's output to `service_request.headers` to modify upstream headers.

### service_response

The response received from the upstream service (read-only in response phase).

| Output | Type | Description |
|--------|------|-------------|
| `body` | any | Response body |
| `headers` | map | Response headers |

**Usage:** `input: service_response.body`

### response

The response being sent to the client (writable — modify before sending).

| Input | Type | Description |
|-------|------|-------------|
| `body` | any | Override client response body |
| `headers` | map | Override client response headers |

**Usage:** Connect a node's output to `response.body` to modify what the client receives.

### vault

Access secrets stored in Kong Vault. Requires `resources.vault` configuration. (v3.12+)

| Output | Type | Description |
|--------|------|-------------|
| `{key}` | string | Secret value from vault, keyed by resource name |

**Usage:** Define vault entries in `resources.vault`, then reference as `vault.my_secret`.
