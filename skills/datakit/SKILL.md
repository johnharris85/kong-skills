---
name: datakit
description: Build and debug Kong DataKit plugin flows. Use when users want to create, modify, debug, or understand DataKit YAML configurations — including designing node-based API workflows, writing jq transformations, configuring caching or branching, or troubleshooting flow execution. Triggers on mentions of DataKit, Kong API orchestration, or decK plugin config with workflow nodes.
---

# DataKit Flow Builder

You are an expert assistant for Kong DataKit — the API orchestration plugin for Kong Gateway Enterprise. You help users design, build, debug, and iterate on DataKit flows.

## What is DataKit?

DataKit (Kong Gateway Enterprise 3.11+) orchestrates complex API workflows through composable **nodes** that form a directed acyclic graph (DAG). Instead of writing custom code, users declare nodes in YAML (via decK declarative config) that call APIs, transform data, branch conditionally, cache results, and manipulate request/response properties.

**Execution model:**
- Nodes with no interdependencies execute **concurrently**
- A node executes only after all its input dependencies resolve
- The DAG is optimized at config time; execution order may differ from declaration order
- Flows run in the **access phase** (pre-proxy) or **response phase** (post-proxy)

**Target version:** Kong Gateway 3.13+ (all 9 node types available). Earlier versions lack: branch/cache (pre-3.12), xml_to_json/json_to_xml (pre-3.13), dynamic URL inputs (pre-3.13).

## Workflow

When a user asks for help with DataKit, follow this approach:

### 1. Clarify the Goal
- What APIs are involved? (URLs, methods, auth requirements)
- What transformations are needed? (merge, filter, reshape, convert format)
- Pre-proxy or post-proxy? (modify request before upstream, or transform response after)
- Any caching, branching, or conditional logic needed?

### 2. Identify Node Types
Select from the 9 explicit node types based on what each step needs to do. See the Quick Reference below.

### 3. Design the DAG
- Map out which nodes depend on which (input connections)
- Identify independent nodes that can run concurrently
- Ensure no circular dependencies
- Keep the node count minimal — avoid unnecessary intermediaries

### 4. Generate YAML Config
- Use the top-level config structure shown below
- Follow naming conventions (UPPER_SNAKE_CASE is conventional for node names)
- Wire inputs/outputs correctly using connection syntax

### 5. Validate
- Check type compatibility between connected nodes
- Verify all referenced node names exist
- Confirm implicit node fields are used correctly (e.g., `request.body` not `request.data`)
- Ensure exit nodes have appropriate status codes
- Verify resource blocks exist for cache/vault nodes

## Quick Reference: Node Types

| Type | Purpose | Key Fields | Inputs | Outputs | Since |
|------|---------|-----------|--------|---------|-------|
| **call** | HTTP request to external/internal API | `method`, `url`, `timeout`, `ssl_verify` | `url`, `body`, `headers`, `query`, proxy fields | `status`, `body`, `headers` | 3.11 |
| **jq** | Transform data with jq expressions | `jq` (max 10240 chars) | `input` or named `inputs` | single output (any type) | 3.11 |
| **exit** | Short-circuit and return response to client | `status` (200–599), `warn_headers_sent` | `body`, `headers` | none | 3.11 |
| **property** | Get/set Kong internal properties | `property`, `content_type` | `input` (SET mode) | value (GET mode) | 3.11 |
| **static** | Emit hardcoded config-time values | `values` (key-value object) | none | `output` (whole), or by key name | 3.11 |
| **branch** | Conditional execution paths | `input` | boolean condition | none (controls flow via `then`/`else`) | 3.12 |
| **cache** | Store/retrieve cached data | `ttl`, `bypass_on_error` | `key`, `data`, `ttl` | `hit`, `miss`, `stored`, `data` | 3.12 |
| **xml_to_json** | Convert XML string to JSON | `xpath`, `recognize_type` | XML string | JSON object | 3.13 |
| **json_to_xml** | Convert JSON to XML string | `root_element_name`, `text_block_name` | JSON object | XML string | 3.13 |

For complete field specifications, see `references/node-reference.md`.

## Quick Reference: Implicit Nodes

These nodes exist automatically in every flow. Do not declare them in `config.nodes`.

| Node | Phase | Readable Fields | Writable Fields |
|------|-------|----------------|-----------------|
| **request** | access | `body`, `headers`, `query` | — |
| **service_request** | access | — | `body`, `headers`, `query` |
| **service_response** | response | `body`, `headers` | — |
| **response** | response | — | `body`, `headers` |
| **vault** | any | `{key}` (from `resources.vault`) | — |

**Phase rules:**
- Access phase (pre-proxy): Read `request`, write `service_request`, or use `exit` to short-circuit
- Response phase (post-proxy): Read `service_response`, write `response`

## Connection Rules

### Syntax

Three ways to wire node connections:

```yaml
# 1. Whole-node input (receives entire output)
input: NODE_NAME

# 2. Field-level input (receives a specific output field)
input: NODE_NAME.field_name

# 3. Multiple named inputs (for jq and other multi-input nodes)
inputs:
  my_key: NODE_NAME.field_name
  other_key: OTHER_NODE
```

### Type Compatibility

| Source → Target | Result |
|----------------|--------|
| Same type → Same type | Allowed |
| `string` → `number` | Allowed (runtime conversion) |
| `any` → specific type | Allowed (runtime check) |
| `object` → `object` | Allowed (field-by-field on common fields) |
| `object` → `map` | **Rejected** |
| `number` → `object` | **Rejected** |

### Common Connection Mistakes

- **Wrong implicit field name:** `request.data` does not exist — use `request.body`
- **Connecting to non-existent output:** Check node type outputs before wiring
- **Circular dependency:** Node A inputs from Node B which inputs from Node A → config rejected
- **Missing dependency in branch:** Nodes in `then`/`else` must be declared in `config.nodes`
- **object → map:** Struct-like objects cannot connect to dynamic maps

## Top-Level Config Structure

```yaml
_format_version: "3.0"

plugins:
  - name: datakit
    service: example-service          # bind to service, route, consumer, or global
    config:
      debug: false                    # set true for development
      nodes:
        - name: NODE_NAME
          type: call                  # one of the 9 node types
          # ... node-specific fields, inputs, outputs
      resources:                      # optional — needed for cache and vault nodes
        cache:
          strategy: memory            # or redis
        vault:
          my_secret: "{vault://env/MY_SECRET}"
```

**Binding options:** `service`, `route`, `consumer`, `consumer_group`, or omit all for global scope.
**Protocols:** `http`, `https`, `grpc`, `grpcs` (default: all four).

## Starter Example: Combine Two APIs

This flow calls two APIs concurrently, merges their responses with jq, and returns the combined result directly to the client (bypassing the upstream service).

```yaml
_format_version: "3.0"

plugins:
  - name: datakit
    service: example-service
    config:
      nodes:
        # Two independent API calls — execute concurrently
        - name: AUTHORS
          type: call
          url: https://httpbin.konghq.com/json

        - name: UUIDS
          type: call
          url: https://httpbin.konghq.com/uuid

        # Merge results — waits for both calls to complete
        - name: COMBINE
          type: jq
          inputs:
            authors: AUTHORS.body
            ids: UUIDS.body
          jq: |
            {
              author: .authors.slideshow.author,
              uuid: .ids.uuid,
              generated_at: now | todate
            }

        # Return merged result to client (short-circuits upstream)
        - name: RESPOND
          type: exit
          inputs:
            body: COMBINE
          status: 200
```

**Apply with decK:**
```bash
deck gateway apply config.yaml
```

**Test:**
```bash
curl -s http://localhost:8000/anything | jq .
# → {"author": "Yours Truly", "uuid": "...", "generated_at": "..."}
```

## Common Patterns Index

These patterns have complete YAML examples in `references/patterns.md`:

1. **Combine multiple APIs** — Concurrent calls + jq merge + exit
2. **Third-party authentication** — OAuth token fetch + header injection (with vault variant)
3. **Conditional caching** — Cache GET + branch on miss + call + cache SET
4. **XML/JSON conversion** — Call XML API + xml_to_json + jq transform (and reverse)
5. **Dynamic URL resolution** — Build URL from request params with jq + call with dynamic input
6. **Header manipulation** — Read/transform/set headers on service_request or response

## Debugging & Validation

### Enable Debug Mode

```yaml
config:
  debug: true
```

With debug on:
- Node errors include node name, type, and error message in the response
- Send `X-DataKit-Debug-Trace: true` header to get full execution timeline

### Reading the Trace

The trace shows events like `NODE_COMPLETE`, `NODE_ERROR`, `NODE_CANCELED` with timestamps. Look for:
- **NODE_ERROR**: Check the error message — common causes are bad URLs, jq syntax errors, type mismatches
- **NODE_CANCELED**: An upstream dependency failed — fix that node first
- **Missing nodes**: May indicate a branch excluded them — check branch conditions

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Type mismatch | Incompatible connection types | Check source output type vs target input type |
| Circular dependency | Nodes reference each other | Restructure DAG to break the cycle |
| Unknown node reference | Typo in node name | Verify spelling matches exactly |
| jq compilation error | Invalid jq syntax | Test jq expression independently with `jq` CLI |
| Cache miss always | Wrong key or no SET | Verify key construction and SET node wiring |
| Exit after headers sent | Exit in response phase | Use `warn_headers_sent: true` or move to access phase |

For cache/vault resource configuration and Redis setup details, see `references/resources-and-debugging.md`.

## Constraints & Limits

| Constraint | Limit |
|-----------|-------|
| Max nodes per flow | 64 |
| Node name length | 1–255 characters |
| Node name format | Letters, digits, underscores, hyphens |
| jq expression length | 10,240 characters |
| URL length | 255 characters |
| Exit status code range | 200–599 |
| Call timeout range | 0–2,147,483,646 ms |
| Vault entries | 64 max |
| Branch then/else arrays | 64 entries each |
| XPath filter length | 256 characters |

**Reserved node names:** `request`, `service_request`, `service_response`, `response`, `vault` — do not use these as explicit node names.
