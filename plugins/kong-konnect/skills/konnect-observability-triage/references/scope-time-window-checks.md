# Scope and Time Window Checks

Use this file when missing data may be explained by the slice being inspected
rather than by broken ingestion.

## Core Rule

Prove that the operator is looking at the intended control plane, entity, and
time range before concluding that telemetry is absent.

## Quick Questions

- Which control plane or entity is in scope?
- Is the expectation for all traffic or only one API, service, route, or
  portal slice?
- Is the time window aligned with when traffic actually occurred?
- Is the user expecting org-wide visibility from a narrower view?

## Common Patterns

| Symptom | Likely interpretation |
|---|---|
| Empty dashboard for one plane, data elsewhere | wrong plane or entity scope |
| "It was there yesterday" | time window or traffic recency mismatch first |
| Only some APIs show data | scoped entity mismatch or partial usage pattern |

## Return Shape

Return:

- which scope variable is wrong, if any
- whether the time window itself explains the symptom
- whether the issue can be resolved without treating it as ingestion failure
