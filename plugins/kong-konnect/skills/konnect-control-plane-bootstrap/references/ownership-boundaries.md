# Ownership Boundaries

Use this file when naming, labels, region, repo ownership, or durable
management path are the real bootstrap questions.

## Core Rule

Bootstrap boundaries become long-lived operational boundaries. Treat them as
first-class decisions, not as afterthoughts.

## Boundary Questions

- which region should own this control plane
- how will names distinguish environment or purpose
- which labels or slices separate ownership
- which repo and automation path will manage the control plane
- which tool owns durable config: Terraform or `kongctl`

## Common Risks

| Risk | Why it matters |
|---|---|
| Region chosen casually | later symptoms look like auth or drift issues |
| Similar control plane names | operators debug the wrong environment |
| No explicit owner | bootstrap succeeds but durable management is unclear |

## What To Return

Return:

- the intended ownership boundary
- the durable management path
- the specific bootstrap decision that must be fixed before moving on
