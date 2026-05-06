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

## References To Load

Load only the reference file that matches the active branch:

- `references/command-paths.md`
  - Load when choosing between validate, diff, sync, dump, or file-generation
    paths.
- `references/openapi-generation.md`
  - Load when the user is starting from an OpenAPI document and wants Gateway
    entities derived from it.
- `references/state-shaping-and-tags.md`
  - Load when file split, tags, include boundaries, or ownership shape matters
    more than the entity content itself.
- `references/dump-diff-sync-safety.md`
  - Load when the main question is how to inspect live state safely before
    mutating it.

## Validation Contract

### Preflight

Before editing files or proposing a live sync:

- Confirm `deck` is installed and runnable: `deck version`
- Confirm the target deployment model:
  - self-managed Gateway via Admin API
  - Konnect-managed control plane via the appropriate Konnect auth flags
- Confirm credentials are already available through environment variables,
  config files, or secure host settings. Never echo or commit secrets.
- Inspect the current file structure before writing new files.
- Confirm the ownership boundary:
  - which state file, directory, include path, or wrapper script is in scope
  - whether tags are used to scope ownership
  - which environment or control plane the commands should touch

### Preview

- Run `deck gateway validate` against the exact file, directory, or include
  path being edited.
- Run the smallest scoped `deck gateway diff` that shows only the intended
  entity slice.
- Use scoped `deck gateway dump` only when live inspection is required.
- Check file scope, include boundaries, tag scope, and unintended deletes
  before any `sync`.

### Execute

- Describe the intended live effect before any mutating command.
- Run `deck gateway sync` only when the user explicitly asked for mutation.
- Keep `sync` aligned with the already previewed file, directory, tags, or
  include boundary.

### Prove

- Rerun the same scoped `deck gateway diff` and expect no remaining intended
  changes.
- Verify the exact entity slice touched when the change is narrower than the
  whole repo.
- Do not treat sync success alone as proof that the live Gateway now matches
  intent.

## Operating Rules

- Treat `decK` as the source-controlled representation of Gateway entities, not
  as proof that the live Gateway currently matches it.
- Treat `deck gateway validate` plus a scoped `deck gateway diff` as the
  required preview surface before `sync`.
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

### 3. Preview with `decK`'s native safety surface

Default paths:

- validate structure or command shape: `deck file` or `deck gateway validate`
- inspect drift before mutation: `deck gateway diff`
- export live Gateway config only when inspection needs it: scoped
  `deck gateway dump`
- apply intended state only when requested: `deck gateway sync`
- generate Gateway config from OpenAPI: the relevant `deck file` workflow

Preview expectations:

- run `deck gateway validate` against the exact file, directory, or include
  path being edited
- run the smallest scoped `deck gateway diff` that shows only the intended
  entity slice
- use `deck gateway dump` only when live inspection is required and keep the
  dump scoped to the target slice when possible
- check for unintended deletes, tag-scope mistakes, include-boundary mistakes,
  or environment mismatches before any `sync`

Prefer the smallest preview path that answers the user request.

Load `references/command-paths.md` when several `decK` paths could fit and you
need a sharper decision rule.

### 4. Author or update state files

When editing state:

- preserve the repository's existing split-by-file or split-by-domain layout
- keep entity names and tags stable when possible
- avoid unnecessary reordering or formatting churn
- add only the entities needed for the requested change

Load `references/state-shaping-and-tags.md` when the repo's split, tags, or
include boundaries are the main constraint.

### 5. Execute only when requested

- State the intended live effect before presenting or running a mutating
  command.
- Use `deck gateway sync` only when the user explicitly asked for live
  mutation.
- Keep the command scoped to the file, tags, select-tags, or include boundary
  already previewed.

Load `references/dump-diff-sync-safety.md` when the user needs a safer
inspection-first path or is about to use a broad dump/sync flow.

### 6. Prove the result with `decK`

After any requested `sync`:

- rerun the same scoped `deck gateway diff` and expect no remaining intended
  changes
- when the task is narrower than the repo, verify the target entity slice
  rather than trusting a broad sync success message
- call out any remaining drift outside the owned slice instead of hiding it
- do not treat `sync` exit status alone as proof that the live Gateway now
  matches the intended state

### 7. Report the exact effect

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
3. run `deck gateway validate`
4. run scoped `deck gateway diff`
5. run `deck gateway sync` only when the user asks to execute
6. rerun scoped `deck gateway diff` to prove the live slice is clean

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
- which `deck` preview commands prove the intended change safely
- whether the task is authoring, diffing, dumping, or syncing
- which environment the commands should target
- whether a live mutation was requested or only a declarative change
- how the post-change proof step will confirm the exact affected slice
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
