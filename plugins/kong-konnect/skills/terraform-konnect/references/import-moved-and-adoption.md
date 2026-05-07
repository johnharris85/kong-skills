# Import, Moved, and Adoption

Use this file when Konnect resources already exist and the job is to bring them
under Terraform without unnecessary churn.

## Core Rule

Prefer importing or preserving existing addresses over recreating resources.
State continuity matters more than fast greenfield-looking HCL.

## Common Cases

| Situation | Preferred default |
|---|---|
| Resource exists in Konnect but not in state | import it |
| Resource moved between modules/addresses | preserve history with `moved` blocks where the repo already uses them |
| Gateway entities already exist in `decK` or live state | use `deck file kong2tf` as a starting point, then normalize |
| Repo only partially manages Konnect | import only the intended boundary, do not broaden casually |

## What To Check

- whether the resource already exists live
- whether the repo already tracks it under another module or address
- whether references to that resource would break if recreated
- whether a generated HCL starting point still needs cleanup to match repo
  conventions

## Return Shape

Return:

- whether import is required
- whether address preservation or `moved` handling is needed
- whether generated HCL is only a starting point
