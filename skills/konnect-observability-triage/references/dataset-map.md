# Dataset Map

Use this file when the operator may be asking the right question in the wrong
observability surface.

## Core Rule

Do not treat Konnect observability as one bucket. Map the question to the
dataset first.

## Fast Mapping

| Question type | Likely surface |
|---|---|
| Gateway/API runtime traffic | gateway or API-oriented analytics/explorer views |
| LLM token, model, or latency behavior | LLM-specific analytics surfaces |
| Request-level debugging | debugger or trace-oriented surface |
| Platform or admin activity | platform-level operational/audit-like surface |

## Common Misroutes

| Operator expectation | Better interpretation |
|---|---|
| "Analytics is broken" | wrong product surface for the question |
| "I cannot see LLM cost-like behavior in normal API analytics" | use LLM-specific observability |
| "Debugger is empty so analytics must be empty too" | aggregate analytics and request debugging are different surfaces |

## Return Shape

Return:

- which surface best matches the question
- why the current surface is the wrong one if applicable
- whether the issue should stay in observability or hand off to gateway health
