# Publication Chain

Use this file when the operator says "the API is not published" but the missing
stage is unclear.

## Core Rule

Do not treat publication as one step. Separate:

1. managed API existence
2. version/spec readiness
3. catalog or package readiness
4. portal publication association
5. consumer-facing access

## Stage Map

| Stage | What must exist |
|---|---|
| Managed API | API object and intended identity exist |
| Version/spec | version objects and usable spec/metadata exist |
| Catalog readiness | asset is complete enough for catalog/governance workflows |
| Portal publication | the API is associated to the intended portal audience |
| Consumer use | developers can discover, register, authenticate, and call it |

## Common Misclassifications

| What operator says | What it often means |
|---|---|
| "Portal bug" | managed API/version/spec is incomplete upstream |
| "Not published" | publication exists, but visibility or access is wrong |
| "Catalog is stale" | wrong version/spec or metadata source |
| "It works internally" | runtime presence without managed/categorized publication state |

## Return Shape

Return the first broken stage in the chain and stop there. Do not mix multiple
speculative stages into one diagnosis.
