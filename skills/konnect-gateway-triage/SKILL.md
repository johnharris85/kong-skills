---
name: konnect-gateway-triage
description: Troubleshoot Konnect Gateway Manager control planes and data planes. Use when a data plane is disconnected, config is not applying, labels or drift look wrong, or the problem must be separated into control-plane, data-plane, network, or rollout failures.
license: MIT
metadata:
  product: konnect
  category: gateway-operations
  tags:
    - kong
    - konnect
    - gateway
    - control-plane
    - data-plane
---

# Konnect gateway triage

## Goal

Reduce ambiguous "gateway is broken" reports into a concrete failing layer:
control plane state, data plane registration, network path, config drift, or
traffic behavior.

Default to live inspection first. Use repo config only as intended state, not
as proof of deployed behavior.

## Tool Selection

- Use the shared `kong-konnect` MCP server first for current control plane and
  data plane state.
- Use `kongctl-query` for concise, read-only checks when CLI output is easier
  to summarize or filter.
- Preserve the repository's chosen declarative toolchain for fixes: use
  `deck-gateway` for Gateway-entity `decK` repos, `terraform-konnect` for
  HCL-managed Konnect Gateway resources, `terraform-kong-gateway` for
  self-managed Gateway HCL, and `kongctl-declarative` for `kongctl` YAML.
- If live Konnect state matters and `kong-konnect` MCP is not connected, say
  so early and continue with CLI or user-provided artifacts.

Prefer to inspect before suggesting restarts, reprovisioning, or config
rewrites.

## Inspection Order

### 1. Define the observed symptom

Classify the problem up front:

- data plane disconnected or never joined
- config not reaching the data plane
- control plane exists but resources are missing or stale
- traffic fails even though connectivity looks healthy
- labels, tags, or environment boundaries look wrong

Do not investigate all paths at once. Pick the failing operator symptom and
follow it.

### 2. Confirm the target control plane

Verify:

- control plane identity and region
- expected cluster type or deployment model
- whether the resource the user cares about belongs to this control plane
- whether the control plane is the intended source of truth for the service,
  route, plugin, or upstream under discussion

Many "gateway" issues are actually wrong-control-plane issues.

### 3. Check data plane attachment before config details

For disconnected or stale behavior, inspect data plane registration and current
association first.

Look for:

- registration present or absent
- connected versus disconnected status
- last-seen or heartbeat recency
- label or environment mismatches
- version skew that could affect expected behavior

If the data plane is not healthy, stop treating the problem as a config bug.

### 4. Separate network bootstrap from Konnect state

If a data plane will not connect, isolate whether the blocker is:

- bootstrap or registration configuration
- network reachability to Konnect
- TLS or certificate trust
- hostname or DNS mismatch
- firewall or proxy behavior

Do not jump to service or route debugging until the control-plane connection is
healthy.

### 5. Compare intended config with live state

Once the control plane and data plane are healthy, inspect the live resources
that should be deployed:

- services
- routes
- plugins
- upstreams or targets
- labels used to partition ownership or environment

If repo config disagrees with live state, call that drift explicitly.
If live state is correct but traffic still fails, move to request-path
troubleshooting instead of deployment troubleshooting.

### 6. Classify the failure domain

Use one primary diagnosis:

- wrong control plane or environment
- data plane registration problem
- network or TLS connectivity problem
- config drift or incomplete rollout
- traffic-path issue despite healthy connectivity

This keeps the answer operational instead of producing a mixed list of guesses.

## Konnect-Specific Gotchas

- A connected data plane does not prove the intended config is present.
- A declarative repo diff does not prove the live control plane matches it.
- Label mismatches can make healthy resources look missing because operators are
  inspecting the wrong slice.
- Solving a traffic issue by editing config manually can hide the real drift if
  a declarative source of truth exists elsewhere.
- Empty or partial resource listings often mean wrong control plane selection,
  not global platform failure.

## Validation Checklist

Before answering, verify that you can state:

- the exact failing gateway symptom
- the control plane in scope
- whether the data plane is attached and healthy
- whether the problem is network, registration, drift, or traffic behavior
- which resource or live-state check supports that conclusion
- which declarative tool skill owns the required fix

## Handoffs

- Use `kongctl-query` for exact resource inspection commands and filtered reads.
- Use `deck-gateway`, `terraform-konnect`, `terraform-kong-gateway`, or
  `kongctl-declarative` when the operator wants to fix drift or apply planned
  gateway changes. Match the repository's current toolchain.
- Use `konnect-access-scope` if the root problem becomes access to the control
  plane rather than gateway health.
- Use `konnect-observability-triage` if the control plane is healthy and the
  main question is missing analytics or debugging data.
