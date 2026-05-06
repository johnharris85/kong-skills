---
name: konnect-event-gateway
description: Operate and troubleshoot Konnect Event Gateway. Use for Event Gateway control planes, listeners, virtual or backend clusters, policies, auth setup, hostname mapping, or listener paths that connect but still fail routing, auth, or policy checks.
license: MIT
metadata:
  product: konnect
  category: event-gateway
  tags:
    - kong
    - konnect
    - event-gateway
    - listeners
    - policies
---

# Event Gateway operator workflow

## Goal

Troubleshoot Event Gateway using its own entity model instead of forcing it
into standard gateway assumptions.

Default to following the request path end to end:
client -> listener -> virtual cluster -> backend cluster -> policy and auth

## Tool Selection

- Use the shared `kong-konnect` MCP server first for live Event Gateway
  inspection.
- Use `kongctl-query` for read-only resource checks and concise summaries where
  the CLI surface is available.
- Preserve the repository's chosen declarative toolchain when Event Gateway
  resources need to change. Prefer `kongctl-declarative` for `kongctl` YAML
  and `terraform-konnect` when the required Event Gateway resources are already
  managed in HCL.
- If live Konnect state matters and `kong-konnect` MCP is not connected, say
  so early and continue with CLI or user-provided artifacts.

Do not reuse generic gateway triage blindly. Event Gateway deserves a dedicated
inspection order because the operator objects differ.

## Inspection Order

### 1. Identify the failing event path

Clarify:

- which Event Gateway control plane is in scope
- which listener the client reaches
- which hostname or endpoint the client uses
- which virtual cluster and backend cluster should receive the traffic
- whether the failure is connection, routing, auth, or policy related

Keep the path concrete before inspecting objects.

### 2. Confirm control plane and object presence

Verify the required objects exist in the same intended environment:

- Event Gateway control plane
- backend cluster
- virtual cluster
- listener
- policy objects
- auth-related objects or bindings

If these objects do not line up in the same scope, stop there and call out the
broken chain.

### 3. Validate listener reachability and mapping

For connection-oriented symptoms, inspect:

- listener hostname or endpoint mapping
- protocol or port assumptions
- TLS or certificate expectations
- whether the listener is attached to the expected virtual cluster path

Do not treat a TCP or protocol-level connect as proof that the request is
authorized or routed correctly.

### 4. Check cluster routing intent

Once the listener is correct, verify that the virtual cluster points at the
intended backend cluster and that the backend target is the one the operator
expects.

Use this step to separate:

- wrong-cluster routing
- missing backend associations
- healthy reachability with broken policy enforcement

### 5. Evaluate auth and policy separately from connectivity

If clients can reach the listener but fail afterward, inspect:

- auth setup and credential expectations
- policy bindings and evaluation order
- hostname- or listener-specific policy attachment
- whether the client identity matches the policy assumptions

This is the default path for "connects but gets denied" reports.

### 6. Return a single failure domain

Diagnose one primary operator break:

- wrong control plane or environment
- missing object in the Event Gateway chain
- listener or hostname mapping problem
- backend or virtual cluster routing problem
- auth mismatch
- policy attachment or evaluation problem

## Konnect-Specific Gotchas

- Successful connection to a listener does not prove policy success.
- Hostname and listener mismatches can look like auth failures from the client
  side.
- Virtual cluster and backend cluster confusion can produce correct-looking
  listeners with wrong downstream routing.
- Generic gateway debugging often misses Event Gateway-specific object
  relationships and leads to noisy advice.
- The right operator question is often "which hop failed?" rather than
  "is Event Gateway up?"

## Validation Checklist

Before answering, verify that you can state:

- the full intended event path
- which Event Gateway objects are present
- whether the listener mapping is correct
- whether the failure is routing, auth, or policy related
- whether the next action belongs in `kongctl-declarative`,
  `terraform-konnect`, or `konnect-access-scope`

## Handoffs

- Use `konnect-access-scope` when the issue is who can view or administer Event
  Gateway resources.
- Use `kongctl-declarative` or `terraform-konnect` when the operator wants to
  encode or apply the Event Gateway fix declaratively. Match the repository's
  current toolchain.
- Use `kongctl-query` for exact read-only command selection while inspecting
  Event Gateway resources.
