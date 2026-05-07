# Dump, Diff, and Sync Safety

Use this file when the operator needs a safe inspection-first path before
mutating live Gateway state.

## Core Rule

Do not let `sync` become the first diagnostic move.

## Safety Defaults

- prefer `diff` before `sync`
- prefer scoped changes before broad converge
- prefer checking environment, includes, and tag boundaries before any mutate
- treat a full `dump` as evidence-gathering, not an automatic replacement for
  curated repo state

## Common Risk Patterns

| Risk | Why it matters |
|---|---|
| Broad `sync` on wrong target | accidental deletion or unintended overwrite |
| Full `dump` merged blindly | repo churn and hidden ownership breakage |
| Missing tag boundary | wrong slice of Gateway gets changed |

## What To Return

Return:

- the safest next command path
- the main boundary to verify before mutation
- whether the user should stop at inspection or proceed to apply
