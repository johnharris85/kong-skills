---
name: terraform-kong-gateway
description: Manage self-managed Kong Gateway with Terraform and the official `kong/kong-gateway` provider. Use for HCL-managed Admin API entities such as Services, Routes, Consumers, plugins, upstreams, targets, or certificates.
license: MIT
metadata:
  product: terraform
  category: declarative-gateway
  tags:
    - kong
    - gateway
    - terraform
    - hcl
    - declarative
---

# Terraform for self-managed Kong Gateway

## Goal

Manage self-managed Kong Gateway entities in HCL through the official Gateway
provider while preserving the repository's current Terraform structure and
state ownership.

Use this skill for Admin API-backed self-managed Gateway work. Do not use it as
the default for Konnect platform resources.

## Tool Positioning

- Use this skill when the repository already uses Terraform for self-managed
  Gateway resources or the user explicitly asks for Terraform.
- Preserve existing Terraform modules, variables, backend settings, and
  workspaces.
- Use the official `kong/kong-gateway` provider for self-managed Gateway
  resources reachable through the Admin API.
- Hand off to `deck-gateway` when the user wants file-based Gateway GitOps,
  dump/diff workflows, or a `decK`-native repository.
- Hand off to `terraform-konnect` when the target resources actually belong to
  Konnect rather than a self-managed Admin API surface.

## Preconditions

- Confirm Terraform is installed and runnable: `terraform version`
- Confirm the target Admin API endpoint and auth method already exist
- Inspect provider blocks and module conventions before adding HCL
- Keep Admin API tokens and secrets out of committed files

## Provider Basics

Expected provider inputs usually include:

- `server_url`
- `admin_token` when the Admin API requires token auth

Do not assume one cluster, workspace, or environment. Follow the repository's
existing provider alias and workspace model.

## Operating Rules

- Preserve existing HCL layout, resource grouping, and variable usage.
- Prefer `terraform plan` before `terraform apply` unless the user explicitly
  asks for direct execution.
- Prefer importing existing Gateway resources over recreating them.
- Keep the scope limited to the Gateway entities requested by the user.
- Do not mix self-managed Gateway assumptions into Konnect tasks.
- When the repository already uses `decK`, do not switch it to Terraform unless
  migration is the task.

## Workflow

### 1. Inspect the Terraform shape

Identify:

- root and child modules
- provider aliases
- backend or remote state configuration
- variable files and secrets conventions
- existing ownership boundaries for services, routes, plugins, consumers, or
  certificates

### 2. Confirm the target Gateway surface

Pin down:

- which Admin API endpoint is in scope
- which Gateway entities are being managed
- whether the task is create, update, import, or drift correction

### 3. Choose the Terraform path

Default paths:

- new managed entity: add HCL in the existing module layout
- existing unmanaged entity: import first, then normalize the HCL
- large-scale file-based Gateway GitOps: consider `deck-gateway` instead of
  forcing Terraform if that matches the user's intent better

### 4. Author HCL with minimal churn

When writing HCL:

- reuse existing variables and locals
- keep names and identifiers stable
- avoid broad refactors while making a narrow Gateway change
- add outputs only when another module or pipeline consumes them

### 5. Validate plan impact

Before apply, verify:

- provider endpoint and auth expectations
- import needs for existing resources
- which workspace or environment the plan will touch
- whether the user asked for HCL authoring only or live execution

### 6. Report config and state impact

State:

- which files or modules changed
- which Gateway entities are affected
- whether import is required
- whether the next step is `plan`, `apply`, or external verification

## Kong-Specific Gotchas

- Terraform state is not a substitute for checking what the live Gateway
  already has; import matters.
- Recreating existing plugins, services, or routes can cause avoidable
  identifier churn.
- Some teams use Terraform for infrastructure but `decK` for Gateway entities;
  preserve the established split if it already exists.
- A self-managed Admin API workflow is not the same as a Konnect control plane
  workflow even if the resource names look similar.

## Validation Checklist

Before answering, verify that you can state:

- why Terraform is the right tool for this repository or request
- which Admin API-backed Gateway surface is in scope
- which module or file owns the resources
- whether import is required
- whether the task stops at HCL authoring or continues to `plan/apply`
- whether `deck-gateway` would be a better fit for the user's intent

## Handoffs

- Use `deck-gateway` when the user wants `decK`-native Gateway GitOps or live
  Gateway export/diff workflows.
- Use `terraform-konnect` when the resources actually belong to Konnect.
- Use Gateway or product-specific domain skills when the user first needs
  troubleshooting or design help rather than HCL authoring.
