---
name: deck-gateway
description: Manage Kong Gateway entities with decK. Use for `deck gateway` state files, diff/sync/dump workflows, OpenAPI-to-Gateway generation, or GitOps-style Gateway config in self-managed Gateway or Konnect control planes.
license: MIT
metadata:
  product: deck
  category: declarative-gateway
  tags:
    - kong
    - deck
    - gateway
    - gitops
    - declarative
---

# decK gateway workflows

## Goal

Generate, inspect, and apply Kong Gateway entity configuration with `decK`
without losing track of live state, scope, or deployment model.

Use this skill for Gateway entities and Gateway-oriented GitOps. Do not use it
as a replacement for Konnect platform workflows that belong in `kongctl` or
Terraform.

## Tool Positioning

- Use the shared `kong-konnect` MCP server first for live Konnect inspection
  when the target Gateway entities live in Konnect and MCP is available.
- Use this skill when the repository already uses `decK`, `_format_version`,
  or `deck gateway` commands, or when the user explicitly asks for `decK`.
- Preserve the existing `decK` layout, file split, tags, and CI patterns in
  the repository.
- Do not convert a Terraform or `kongctl` repository to `decK` unless the user
  explicitly asks for that migration.
- Hand off to `terraform-kong-gateway`, `terraform-konnect`, or
  `kongctl-declarative` when the user wants HCL or `kongctl` rather than
  `decK`.

## Preconditions

- Confirm `deck` is installed and runnable: `deck version`
- Confirm the target deployment model:
  - self-managed Gateway via Admin API
  - Konnect-managed control plane via the appropriate Konnect auth flags
- Confirm credentials are already available through environment variables,
  config files, or secure host settings. Never echo or commit secrets.
- Inspect the current file structure before writing new files.

## Operating Rules

- Treat `decK` as the source-controlled representation of Gateway entities, not
  as proof that the live Gateway currently matches it.
- Prefer `diff` or validation before `sync` unless the user explicitly requests
  immediate mutation.
- Preserve existing file segmentation and tags when the repository already has
  them.
- Prefer additive or scoped changes over broad re-dumps of an entire control
  plane unless the user asks for a full export.
- Keep Konnect platform resources out of `decK` files. `decK` is for Gateway
  entities, not the full Konnect product surface.
- Use OpenAPI-driven generation when the user is starting from an API spec and
  wants Gateway entities derived from it.
- Do not assume `decK` is the right answer for DB-less runtime loading,
  identity or team management, or non-Gateway Konnect resources.

## Workflow

### 1. Inspect the existing `decK` shape

Identify:

- whether the repo already has one or more `decK` state files
- whether config is split by environment, workspace, or service
- whether tags are used to scope ownership
- whether CI uses `deck gateway diff`, `deck gateway sync`, or wrapper scripts

Match the existing conventions before adding new files or commands.

### 2. Confirm the target Gateway surface

Pin down:

- self-managed Gateway versus Konnect control plane
- which Gateway entities are in scope: services, routes, plugins, consumers,
  consumer groups, upstreams, targets, certificates, or vault-related config
- whether the task is create, update, dump, validate, drift review, or import

Do not treat platform resources such as teams, portals, or access rules as
Gateway entities.

### 3. Choose the right `decK` path

Default paths:

- validate structure or command shape: `deck file` or `deck gateway validate`
- inspect drift: `deck gateway diff`
- apply intended state: `deck gateway sync`
- export live Gateway config: `deck gateway dump`
- generate Gateway config from OpenAPI: the relevant `deck file` workflow

Prefer the smallest path that answers the user request.

### 4. Author or update state files

When editing state:

- preserve the repository's existing split-by-file or split-by-domain layout
- keep entity names and tags stable when possible
- avoid unnecessary reordering or formatting churn
- add only the entities needed for the requested change

### 5. Validate before applying

Before mutation, verify:

- target environment and credentials
- file paths and include patterns
- tag scoping or selective sync boundaries
- whether the user expects a preview, a diff, or direct execution

### 6. Report the exact effect

State:

- which files changed
- which Gateway entities are affected
- whether the result is only declarative authoring, a drift review, or a live
  sync
- what the next user-visible verification step is

## Common Patterns

### Add or update Gateway entities

Use for:

- add a service, route, or plugin
- update consumer auth or upstream configuration
- introduce tags or ownership boundaries

Preferred sequence:

1. inspect existing `decK` files
2. update only the relevant entities
3. validate
4. run `deck gateway diff`
5. run `deck gateway sync` only when the user asks to execute

### Export or review drift

Use for:

- compare repo state with live Gateway state
- capture a control plane baseline
- understand what changed outside Git

Preferred sequence:

1. dump or diff the relevant Gateway slice
2. compare the live result with the checked-in files
3. call out drift before proposing further edits

### Generate config from OpenAPI

Use for:

- initial service and route scaffolding from a spec
- API onboarding into a Gateway config repo

Prefer generated scaffolding as a starting point, then normalize it to the
repo's conventions before finalizing.

## Kong-Specific Gotchas

- `decK` is strongest for Gateway entities, not the broader Konnect platform.
- A `decK` file in Git does not prove the live control plane matches it.
- Broad `sync` runs can overwrite adjacent entity changes when file scope or
  tag scope is too loose.
- Konnect control planes still use `decK` for Gateway-entity workflows, but
  the surrounding platform resources may belong in another tool.
- If a user really wants HCL plus Terraform state, forcing `decK` adds
  unnecessary translation.

## Validation Checklist

Before answering, verify that you can state:

- why `decK` is the right tool for this repository or request
- which Gateway entities are in scope
- whether the task is authoring, diffing, dumping, or syncing
- which environment the commands should target
- whether a live mutation was requested or only a declarative change
- whether another tool skill should own the implementation instead

## Handoffs

- Use `terraform-kong-gateway` when the repository already manages
  self-managed Gateway config in HCL.
- Use `terraform-konnect` when the repository already manages Konnect-hosted
  Gateway entities or surrounding Konnect resources in HCL.
- Use `kongctl-declarative` when the task is really Konnect platform YAML
  rather than Gateway-entity `decK`.
- Use `kongctl-query` or the relevant domain skill when the user first needs
  live inspection rather than config authoring.
