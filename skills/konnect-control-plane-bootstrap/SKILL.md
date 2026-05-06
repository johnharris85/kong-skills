---
name: konnect-control-plane-bootstrap
description: Bootstrap Konnect Gateway control planes and first-run topology choices. Use when creating a new control plane, choosing hosted or self-hosted data planes, setting initial naming and ownership boundaries, or turning a quickstart into a durable setup.
license: MIT
metadata:
  product: konnect
  category: control-plane-bootstrap
  tags:
    - kong
    - konnect
    - control-plane
    - bootstrap
    - gateway
---

# Konnect control plane bootstrap

## Goal

Help an operator stand up a new Konnect Gateway control plane with the right
bootstrap assumptions before the problem becomes Gateway drift or runtime
troubleshooting.

Use this skill for initial setup, first-run topology choices, naming, labels,
ownership boundaries, and “what should we create first?” decisions. Do not use
it for ongoing incident triage.

## Tool Selection

- Use the shared `kong-konnect` MCP server first for live inspection of
  existing control planes, groups, and adjacent Konnect Gateway resources.
- Preserve the repository's chosen declarative toolchain when bootstrap should
  be codified: use `terraform-konnect` for HCL-managed control planes,
  `kongctl-declarative` for `kongctl` YAML, and `deck-gateway` only after the
  control plane exists and the task becomes Gateway-entity configuration.
- If the user is following an official quickstart path, keep the quickstart and
  the durable repo-managed setup distinct in your explanation.
- If live Konnect state matters and `kong-konnect` MCP is not connected, say so
  early and continue with user-provided artifacts or repo context.

## Workflow

### 1. Identify the intended deployment shape

Clarify:

- whether the user needs a quick local bootstrap, a durable shared environment,
  or both
- whether data planes will be self-hosted, Dedicated Cloud Gateways, or
  serverless / Kong-managed where applicable
- whether the environment is dev, staging, prod, or a shared platform slice

Do not treat a tutorial quickstart as the final production shape by default.

### 2. Confirm region, naming, and ownership boundaries

Decide:

- Konnect region
- control plane naming convention
- labels or environment boundaries
- which team, repo, or automation path will own the control plane

Bootstrap errors here cause long-lived confusion later, especially when several
control planes look similar.

### 3. Separate platform bootstrap from Gateway config

For a new control plane, keep these concerns distinct:

- creating the control plane
- attaching or provisioning data planes
- verifying connectivity and heartbeat
- applying the first Gateway entities

The control plane is not “done” just because it exists in Konnect.

### 4. Choose the first durable management path

Default decision rule:

- if the team already manages Konnect with Terraform, bootstrap in
  `terraform-konnect`
- if the team already manages Konnect with `kongctl`, bootstrap in
  `kongctl-declarative`
- if the task is only to get a local quickstart running, explain the quickstart
  separately and then point to the durable management path

Do not force migration between tools during bootstrap unless the user asked for
it.

### 5. Validate the first-post-bootstrap state

Before calling the bootstrap complete, verify:

- the control plane exists in the intended region
- the target data plane hosting model is correct
- the connection path is understood
- the ownership boundary and next automation path are explicit
- the user knows whether the next step is Gateway entity config, Portal work,
  or runtime verification

### 6. Hand off to the next operational surface

Common next steps:

- `konnect-gateway-triage` if the control plane exists but connectivity or
  rollout is unhealthy
- `deck-gateway` for first Gateway-entity config in a `decK` repo
- `terraform-konnect` or `kongctl-declarative` for durable control-plane
  codification

## Konnect-Specific Gotchas

- Quickstart success does not mean the durable environment model is decided.
- Control plane creation, data plane hosting, and Gateway config are separate
  milestones.
- Region mistakes are expensive because many later symptoms look like auth or
  drift failures.
- A healthy control plane object does not prove the data plane is attached or
  the first config rollout will succeed.
- `decK` is not the control-plane bootstrap tool; it becomes relevant after the
  control plane exists.

## Validation Checklist

Before answering, verify that you can state:

- which deployment shape the user actually needs
- the intended region, name, and ownership boundary
- whether the data plane hosting model is correct
- whether the next step is bootstrap, connectivity, or Gateway config
- which declarative tool skill should own the durable setup

## Handoffs

- Use `konnect-gateway-triage` when the bootstrap is complete enough that the
  remaining problem is health, connectivity, or rollout.
- Use `terraform-konnect` or `kongctl-declarative` when the user wants the
  control plane managed as code.
- Use `deck-gateway` once the control plane exists and the task becomes Gateway
  entity configuration.
