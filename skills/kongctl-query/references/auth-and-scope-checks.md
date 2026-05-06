# Auth and Scope Checks

Use this file when a read-only query problem may actually be auth, profile,
region, or scope related.

## Core Rule

Do not assume a failed query means the resource path is wrong. Prove auth and
scope first.

## Quick Checks

- `kongctl version`
- `kongctl get organization -o json`
- `kongctl get me -o json`
- inspect `--profile` use and relevant `KONGCTL_*` overrides

## Common Misreads

| Symptom | Likely interpretation |
|---|---|
| Empty results unexpectedly | wrong profile, region, or org slice |
| Query fails broadly | auth or endpoint problem |
| One resource family is visible, another is not | scope/product-surface issue, not always CLI syntax |

## What To Return

Return:

- whether auth/scope is proven
- whether the query issue is environmental rather than structural
- whether another skill should take over once access is understood
