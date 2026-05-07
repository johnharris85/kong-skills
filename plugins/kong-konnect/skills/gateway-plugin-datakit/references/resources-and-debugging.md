# DataKit Resources & Debugging

Configuration details for cache resources, vault resources, debug mode, and deployment considerations.

---

## Cache Resource Configuration

Cache nodes require a `resources.cache` block. Two strategies are available.

### Memory Strategy

Stores cached data in Kong's shared memory (Lua shared dict).

```yaml
resources:
  cache:
    strategy: memory
    memory:
      dictionary_name: kong_db_cache    # default; shared with Kong's own cache
```

**Production recommendation:** Define a dedicated `lua_shared_dict` via Nginx directive injection to avoid contention with Kong's internal cache:

```nginx
# In kong.conf or custom Nginx template:
nginx_http_lua_shared_dict = datakit_cache 128m
```

Then reference it:
```yaml
resources:
  cache:
    strategy: memory
    memory:
      dictionary_name: datakit_cache
```

**Serverless gateways:** Memory is the only available strategy (no external Redis access).

### Redis Strategy — Standalone

```yaml
resources:
  cache:
    strategy: redis
    redis:
      host: redis.example.com        # required
      port: 6379                      # default
      username: ""                    # optional (Redis 6+ ACL)
      password: ""                    # optional
      database: 0                     # default
      ssl: false                      # enable TLS
      ssl_verify: false               # verify TLS certificate
      server_name: ""                 # SNI for TLS
      timeout:
        connect_timeout: 2000        # ms
        read_timeout: 2000           # ms
        send_timeout: 2000           # ms
      connection_pool:
        pool_size: 256               # default
        backlog: 0                   # max queued connections
```

### Redis Strategy — Cluster

```yaml
resources:
  cache:
    strategy: redis
    redis:
      cluster_nodes:
        - ip: redis-1.example.com
          port: 6379
        - ip: redis-2.example.com
          port: 6379
        - ip: redis-3.example.com
          port: 6379
      cluster_max_redirections: 5    # default
```

### Redis Strategy — Sentinel

```yaml
resources:
  cache:
    strategy: redis
    redis:
      sentinel_master: mymaster
      sentinel_role: master           # or "slave" for read replicas
      sentinel_username: ""           # optional
      sentinel_password: ""           # optional
      sentinel_nodes:
        - host: sentinel-1.example.com
          port: 26379
        - host: sentinel-2.example.com
          port: 26379
```

### Redis Strategy — Cloud Providers

**AWS ElastiCache (IAM auth):**
```yaml
resources:
  cache:
    strategy: redis
    redis:
      host: my-cluster.abc123.use1.cache.amazonaws.com
      port: 6379
      ssl: true
      cloud_authentication:
        auth_provider: aws
        access_key_id: AKIAXXXXXXXXXXXXXXXX
        secret_access_key: "wJalrXUtnFEMI/K7MDENG..."
        region: us-east-1
```

**Azure Managed Redis (Entra ID):**
```yaml
resources:
  cache:
    strategy: redis
    redis:
      host: my-cache.redis.cache.windows.net
      port: 6380
      ssl: true
      cloud_authentication:
        auth_provider: azure
        service_principal:
          tenant_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          client_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          client_secret: "your-client-secret"
```

**Google Cloud Memorystore:**
```yaml
resources:
  cache:
    strategy: redis
    redis:
      host: 10.0.0.5
      port: 6379
      ssl: true
      cloud_authentication:
        auth_provider: gcp
        service_account_json: '{"type":"service_account",...}'
```

---

## Vault Resource Configuration

Vault resources let nodes access secrets without hardcoding them. Values use Kong's `vault://` reference syntax.

```yaml
resources:
  vault:
    api_key: "{vault://env/MY_API_KEY}"
    db_password: "{vault://hcv/secrets/db/password}"
    cert_data: "{vault://aws/my-secret}"
```

**Constraints:**
- Maximum 64 vault entries
- Values are referenceable and encrypted at rest
- Reference format: `{vault://PROVIDER/PATH}`
- Supported providers depend on Kong Gateway configuration (env, HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)

**Usage in nodes:**
```yaml
nodes:
  - name: CALL_API
    type: call
    url: https://api.example.com/data
    inputs:
      headers:
        type: jq
        # Reference vault values as outputs of the implicit vault node
  - name: AUTH_HEADER
    type: jq
    input: vault.api_key
    jq: |
      { "Authorization": ("Bearer " + .) }
```

---

## Debug Mode

### Enabling Debug

Set `debug: true` in the plugin config:

```yaml
plugins:
  - name: datakit
    config:
      debug: true
      nodes: [...]
```

### Error Exposure

With debug enabled, node execution errors are included in the client response body with:
- Node name
- Node type
- Node index in the config array
- Error message

This helps identify which node failed and why without checking Kong logs.

### Execution Trace

Send a request with the `X-DataKit-Debug-Trace: true` header to get a detailed execution timeline:

```bash
curl -H "X-DataKit-Debug-Trace: true" http://localhost:8000/your-route
```

The trace includes:
- **Timeline events** for each node: scheduled, started, completed/errored/canceled
- **Node status codes**: `NODE_COMPLETE`, `NODE_ERROR`, `NODE_CANCELED`
- **Execution order**: Shows which nodes ran concurrently vs. sequentially
- **Duration**: Per-node execution time

**Important:** The trace format is non-deterministic and intended for development use only. Do not parse it programmatically or rely on it in production.

### Common Debug Scenarios

| Symptom | Likely Cause | What to Check |
|---------|-------------|---------------|
| Node shows `NODE_ERROR` | Failed HTTP call or jq error | Check URL, method, jq syntax |
| Node shows `NODE_CANCELED` | Dependency node failed | Fix the upstream dependency |
| Unexpected output type | Type mismatch in connection | Verify input/output types match |
| Node never executes | Missing dependency or branch exclusion | Check DAG wiring and branch paths |
| Cache always misses | Key mismatch or TTL=0 | Verify cache key construction |

---

## Deployment Topologies

DataKit works across all Kong Gateway deployment modes:

- **Traditional (database-backed):** Config stored in PostgreSQL; apply via Admin API or decK
- **DB-less (declarative):** Config loaded from YAML file; apply via `deck gateway apply` or mount as config file
- **Hybrid mode:** Control plane manages config; data planes execute DataKit flows. Ensure all data planes have network access to any URLs referenced in call nodes
- **Konnect (SaaS control plane):** Configure via Konnect UI or decK with Konnect flags

### Protocol Support

DataKit triggers on these protocols (configurable per plugin instance):
- `http` / `https`
- `grpc` / `grpcs`

### Phase Considerations

- **Access phase (pre-proxy):** Nodes can read `request`, write to `service_request`, or call `exit` to short-circuit
- **Response phase (post-proxy):** Nodes can read `service_response`, write to `response`. Exit nodes in this phase may warn about headers already sent
