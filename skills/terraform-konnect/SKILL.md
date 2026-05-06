---
name: terraform-konnect
description: Manage Konnect with Terraform and the official `kong/konnect` provider. Use for HCL-managed control planes, Gateway entities in Konnect, APIs, portals, teams, roles, publications, or Terraform plan/apply/import workflows.
license: MIT
metadata:
  product: terraform
  category: declarative-konnect
  tags:
    - kong
    - konnect
    - terraform
    - hcl
    - declarative
---

# Terraform for Konnect

## Goal

Author and maintain Konnect resources in HCL using the official Terraform
provider while preserving the repository's existing module, state, and CI
conventions.

Use this skill for Terraform-managed Konnect work. Do not turn a `kongctl` or
`decK` repository into Terraform unless the user asks for that migration.

## Tool Positioning

- Use the shared `kong-konnect` MCP server first for live Konnect inspection
  when the requested change depends on current state and MCP is available.
- Use this skill when the repository already uses Terraform for Konnect or the
  user explicitly asks for HCL, Terraform Cloud, plan/apply, or provider-based
  management.
- Preserve existing Terraform layout, backend configuration, module structure,
  and variable conventions.
- Prefer the official `kong/konnect` provider by default.
- Use `kong/konnect-beta` only when the user explicitly needs beta-only
  coverage that is not available in the supported provider.
- Hand off to `deck-gateway` when the user wants file-based Gateway GitOps or
  `decK` export/diff workflows.
- Hand off to `kongctl-declarative` when the repository already uses `kongctl`
  YAML instead of HCL.

## Preconditions

- Confirm Terraform is installed and runnable: `terraform version`
- Confirm the repo's backend and workspace expectations before editing files
- Confirm Konnect auth is already supplied through secure variables, not
  checked-in literals
- Inspect existing provider blocks, modules, and variable names before writing
  new HCL

## Provider Basics

Default provider choice:

- `kong/konnect` for supported Konnect resources
- `kong/konnect-beta` only for explicitly requested beta coverage

Common auth inputs:

- `KONNECT_TOKEN` or `KONNECT_SPAT`
- `KONNECT_SERVER_URL` when the environment does not use the default endpoint

Never hardcode tokens into committed `.tf` files.

## Operating Rules

- Preserve the repo's existing Terraform style: root-module layout, child
  modules, variable files, naming, and output shape.
- Prefer `terraform plan` before `terraform apply` unless the user explicitly
  requests direct execution.
- Treat Terraform state as authoritative for what it manages. Do not recreate
  resources that should be imported or adopted.
- Keep Gateway entities and surrounding Konnect platform resources in the same
  Terraform approach only when the repository already does so or the user wants
  that composition.
- When the repository already manages only part of Konnect in Terraform, follow
  that boundary instead of broadening scope casually.
- Preserve imports, `moved` blocks, and module addresses when refactoring.
- Avoid mixing one-off UI edits with Terraform-managed resources without
  calling out drift.

## Workflow

### 1. Inspect the Terraform shape

Identify:

- root modules and child modules
- provider aliases and version constraints
- backend configuration and workspace selection
- variable conventions and secrets handling
- whether Konnect resources are already organized by environment, team, or
  control plane

Match the existing shape before adding resources.

### 2. Confirm the Konnect scope

Pin down:

- which Konnect product surface is in scope
- whether the task concerns platform resources, Gateway entities inside a
  Konnect control plane, or both
- whether the request is create, update, import, or drift correction

Do not assume every requested resource belongs in the same module.

### 3. Choose the Terraform path

Default paths:

- new managed resource: author HCL in the existing module layout
- existing unmanaged resource: prefer import or adoption over recreation
- repo migration from live Gateway entities: use `deck file kong2tf` as the
  default starting point when Gateway config already exists in `decK` or live
  Gateway state
- beta-only feature: use `kong/konnect-beta` only when explicitly required

### 4. Author HCL with stable ownership boundaries

When writing HCL:

- keep related resources grouped by the repository's current convention
- reuse variables and locals rather than duplicating environment-specific
  literals
- preserve stable names and identifiers where the repo already has them
- add outputs only when downstream modules or CI actually need them

### 5. Validate state interactions

Before apply, verify:

- provider selection and version constraints
- backend and workspace target
- import needs for existing resources
- whether the change affects only HCL or also live state

### 6. Report both config and state impact

State:

- which files or modules changed
- which Konnect resources are managed or updated
- whether import is required
- whether the next step is `plan`, `apply`, or a separate verification step

## Common Patterns

### Manage Konnect resources in an existing Terraform repo

Use for:

- add or update control planes
- manage APIs, portals, teams, or publication-related resources
- keep Konnect managed alongside surrounding infrastructure

Preferred sequence:

1. inspect current module boundaries
2. add or update HCL in the right module
3. run `terraform fmt` and validation steps used by the repo
4. run `terraform plan`
5. apply only when requested

### Adopt existing resources

Use for:

- resources created manually in Konnect
- partial migration from `decK` or UI-managed state into Terraform

Preferred defaults:

- use Terraform import for existing managed identities in scope
- use `deck file kong2tf` when the starting point is Gateway-entity config and
  the user wants a Terraform representation
- clean up generated HCL to match repo conventions before treating it as final

### Compose Konnect with other infrastructure

Use for:

- repositories that already manage cloud networking, secrets, or deployment
  dependencies in Terraform
- workflows that require a single plan across Kong and non-Kong resources

Keep module boundaries clear so Kong-specific drift is still understandable.

## Kong-Specific Gotchas

- `kong/konnect` is the default supported provider; beta coverage should be an
  explicit exception, not the baseline.
- Recreating an existing Konnect resource in Terraform instead of importing it
  can cause avoidable churn and broken references.
- A repository may manage Gateway entities in Terraform while still inspecting
  live state through MCP or `kongctl`; those are complementary, not conflicting.
- Generated `kong2tf` output is a starting point, not a guarantee that the HCL
  matches repo style or ownership boundaries.
- If the repo already standardizes on `kongctl` YAML or `decK`, forcing HCL is
  usually the wrong move unless migration is the task.

## Validation Checklist

Before answering, verify that you can state:

- why Terraform is the right tool for this repository or request
- whether `kong/konnect` or `kong/konnect-beta` is actually needed
- which module or file owns the target resources
- whether import or adoption is required
- whether the change should stop at HCL authoring or continue to `plan/apply`
- whether another tool skill should own the implementation instead

## Handoffs

- Use `deck-gateway` when the user wants Gateway-entity GitOps through `decK`
  rather than Terraform state.
- Use `kongctl-declarative` when the repository already uses `kongctl` YAML for
  Konnect changes.
- Use `konnect-access-scope`, `konnect-api-publish`, `konnect-gateway-triage`,
  or other domain skills when the user first needs diagnosis of the Konnect
  problem rather than HCL authoring.
