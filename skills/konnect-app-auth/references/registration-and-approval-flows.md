# Registration and Approval Flows

Use this file when the strategy is plausible but developers still cannot get
through the self-service workflow.

## Core Rule

Treat "published but unusable" as a workflow-state problem until proven
otherwise.

## Common Flow States

| State | Meaning |
|---|---|
| pending | approval or manual action is still required |
| approved | the next blocker is likely credentials or enforcement |
| revoked/rejected | the workflow failed by policy or admin action |

## Useful Distinctions

- developer approval versus application approval
- registration state versus credential issuance
- RBAC/team gating versus auth-strategy mismatch

## What To Return

Return:

- which workflow state is blocking consumption
- whether the problem is approvals, registration, or RBAC/team gating
- whether another skill now owns the next step
