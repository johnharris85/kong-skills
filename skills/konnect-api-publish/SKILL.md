---
name: konnect-api-publish
description: Operate Konnect API publication from managed API through Catalog and Dev Portal. Use when an API is missing from Catalog or Portal, publication is mis-scoped, or developer registration and access do not match the intended publishing flow.
license: MIT
metadata:
  product: konnect
  category: api-publication
  tags:
    - kong
    - konnect
    - api
    - portal
    - catalog
---

# Konnect API publish workflow

## Goal

Help an operator trace an API from runtime and managed-API presence through
cataloging, portal publication, and consumer-facing access.

Use workflow language: inspect, trace, publish, validate, and approve.
Do not turn this into generic Portal documentation.

## Tool Selection

- Use the shared `kong-konnect` MCP server first for live inspection of
  managed API, catalog, and portal state.
- Use `kongctl-query` for read-only checks on API, portal, and adjacent
  resources.
- Preserve the repository's chosen declarative toolchain when publication
  resources need to change: prefer `kongctl-declarative` for `kongctl` YAML,
  `terraform-konnect` for HCL-managed Konnect resources, and `deck-gateway`
  only when the missing link is in Gateway-entity config within the target
  control plane.
- If live Konnect state matters and `kong-konnect` MCP is not connected, say
  so early and continue with CLI or user-provided artifacts.

Default to read-first inspection. Only move to mutation when the missing link
in the publication chain is understood.

## Inspection Order

### 1. Identify the missing outcome

Clarify what "not published" means:

- API missing from managed inventory
- spec or version missing
- Catalog entry missing or stale
- publication missing from a portal
- portal page visible but registration or access fails
- API exists internally but is not ready for developer consumption

Do not use one answer path for all of these.

### 2. Confirm the managed API and version exist

Start with the operator source objects:

- managed API identity
- version objects
- attached spec or descriptive metadata
- association to the intended control plane or runtime surface where relevant

If the API object or version does not exist, do not continue to portal
debugging yet.

### 3. Check catalog and governance readiness

Inspect whether the API is actually ready for cataloging:

- the expected API asset is present
- the spec or version information is usable
- the intended metadata is attached
- the API is in the right lifecycle stage for publication

If the managed asset is incomplete, explain that publication is blocked
upstream rather than treating Portal as the problem.

### 4. Trace publication into the developer-facing surface

Verify:

- portal target is the intended one
- publication object or equivalent association exists
- expected visibility aligns with the audience
- the API should appear in the specific portal view the user is checking

Separate "API is published" from "viewer can currently find it."

### 5. Check registration and access workflow

If the API is visible but unusable, inspect the consumer path:

- developer app or registration prerequisites
- auth or credential expectations
- visibility or audience gates
- any portal-specific access constraints that explain why discovery succeeds
  but use fails

This is where many "publish" issues become access or onboarding issues.

### 6. Return the missing link in the chain

Diagnose one primary break:

- managed API missing
- version or spec missing
- catalog or governance readiness incomplete
- portal publication missing or mis-scoped
- developer registration or access flow incomplete
- visibility issue rather than publication issue

## Konnect-Specific Gotchas

- Runtime presence does not automatically mean catalog or portal publication.
- A managed API can exist without being visible to the intended portal audience.
- Publication and access are separate: an API can be listed but still blocked
  by registration or auth requirements.
- Portal debugging is wasted effort when the underlying managed API or version
  is absent or stale.
- Operators often call a cataloging gap a "portal bug" when the missing link is
  earlier in the chain.

## Validation Checklist

Before answering, verify that you can state:

- which publication-stage outcome is missing
- whether the managed API and version exist
- whether catalog readiness is complete
- whether portal publication exists for the intended audience
- whether the issue is publication, visibility, or consumer access
- which declarative tool skill owns the required change

## Handoffs

- Use `kongctl-declarative` or `terraform-konnect` when the user wants to
  create or update APIs, portals, or related publication resources as code.
- Use `deck-gateway` when the publication issue is downstream of missing or
  stale Gateway-entity config inside the control plane.
- Use `konnect-access-scope` when the API likely exists but the caller cannot
  see or administer it.
- Use `kongctl-query` for exact read-only command syntax during investigation.
