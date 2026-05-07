# Spec, Version, and Metadata

Use this file when the hard part is versioning style, spec quality, or metadata
alignment.

## Core Rule

Treat specs and version metadata as the governing input for Catalog quality,
not as optional decoration.

## Common Branches

| Question | Default guidance |
|---|---|
| No version style chosen | semantic versioning is the safest default |
| Major lifecycle split unclear | separate APIs per major version when the lifecycle boundary is real |
| Docs look wrong downstream | check spec and metadata before blaming publication |

## What To Return

Return:

- whether the versioning model itself is sound
- whether the spec/docs inputs are good enough
- whether metadata drift is the real issue
