# Provider Routing

Use this file when the main issue is where AI traffic is being sent and why.

## Core Rule

Separate provider routing from higher-level governance. If traffic is hitting
the wrong model or provider, fix that layer before reasoning about guardrails
or prompt policy.

## Routing Questions

- Is the request reaching the intended service and route first?
- Is the provider/model target what the operator expects?
- Is fallback or alternate routing happening implicitly?
- Is the problem actually provider authentication rather than routing?

## Common Patterns

| Symptom | Likely branch |
|---|---|
| Wrong model/provider receives traffic | route targeting, plugin config, fallback assumptions |
| Requests never reach provider | baseline proxy/auth problem |
| Only some model families misbehave | provider-specific routing branch, not universal AI Gateway failure |

## Return Shape

Return:

- whether the issue is route targeting, provider selection, or provider auth
- whether fallback behavior is expected or accidental
- whether the next step stays in AI Gateway or moves to generic gateway health
