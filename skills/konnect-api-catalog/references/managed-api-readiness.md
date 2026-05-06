# Managed API Readiness

Use this file when the operator says an API is missing or incomplete in Catalog
and the main question is which upstream object is actually missing.

## Core Rule

Do not treat Catalog readiness as one object. Separate API identity, versions,
specs, docs, implementations, and packages.

## Readiness Questions

- does the API object exist
- does the intended version exist
- is there a usable spec and metadata set
- is the implementation story clear
- is a package involved or is this an individual API workflow

## Return Shape

Return the first incomplete stage and stop there rather than jumping to Portal
or consumer-facing conclusions.
