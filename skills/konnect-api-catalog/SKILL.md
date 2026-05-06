---
name: konnect-api-catalog
description: Operate Konnect API Catalog and API packages. Use when creating or versioning APIs, attaching specs or docs, linking APIs to Gateway Services, building API packages, or separating catalog-readiness problems from Dev Portal publication problems.
license: MIT
metadata:
  product: konnect
  category: api-catalog
  tags:
    - kong
    - konnect
    - catalog
    - api
    - governance
---

# Konnect API catalog workflow

## Goal

Help an operator create, shape, and troubleshoot Catalog APIs and API packages
before they become a Dev Portal publishing or consumer-access problem.

Use this skill for Catalog object modeling, versioning, specifications,
documentation, implementations, and packages. Do not collapse it into generic
Dev Portal help.

## Tool Selection

- Use the shared `kong-konnect` MCP server first for live inspection of APIs,
  versions, specs, documents, implementations, packages, and portal
  publications.
- Prefer Catalog-oriented MCP reads before changing config. Useful live
  surfaces include API, version, implementation, package, and publication
  listings.
- Preserve the repository's chosen declarative toolchain when catalog objects
  need to change: use `terraform-konnect` for HCL-managed Catalog resources and
  `kongctl-declarative` only when the repo already manages the surrounding
  Konnect workflow that way.
- Use `deck-gateway` only when the real missing link is Gateway-entity config
  behind an implementation or linked service.
- If live Konnect state matters and `kong-konnect` MCP is not connected, say so
  early and continue with user-provided artifacts or adjacent CLI/config
  sources.

## Workflow

### 1. Identify the catalog object that is actually missing

Clarify whether the operator is missing:

- the API object itself
- an API version
- a valid specification or generated documentation
- API documents or page structure
- a Gateway implementation link
- an API package
- a portal publication that should happen after the catalog object is ready

Do not jump straight to Portal troubleshooting if the Catalog object model is
incomplete.

### 2. Confirm API identity and versioning model

Inspect:

- API name
- current version
- slug or URL identity
- whether the API should be modeled as one API with multiple spec versions or
  distinct APIs for major versions

Default guidance:

- semantic versioning is the safest default when the user has not chosen a
  version style
- create a distinct API per major version when that matches the lifecycle
  boundary

### 3. Check spec and documentation readiness

Verify:

- a spec exists when generated docs are expected
- the spec version matches the intended current version
- validation issues are understood before blaming downstream publishing
- documentation pages, slugs, parent pages, and status match the intended
  structure

Treat invalid-but-accepted specs as degraded inputs, not as healthy state.

### 4. Check implementation and service linkage

If developers should be able to consume the API through registration, inspect:

- whether the API is linked to a Gateway Service or control-plane-backed
  implementation
- whether the implementation shape is 1:1 service linkage or a broader package
  / control plane scenario
- whether the linked service is the right operational surface

Do not call the API consumer-ready until the implementation story is clear.

### 5. Separate packages from individual APIs

When API packages are involved, verify:

- whether the operator should publish an individual API or a package
- which operations belong in the package
- whether the package boundary is business-facing or merely technical

Packages are for grouping and presentation, not for hiding a broken API model.

### 6. Hand off only after Catalog readiness is clear

Once API shape, docs, implementations, and packages are understood, hand off:

- to `konnect-api-publish` for Portal publication and audience-facing issues
- to `konnect-app-auth` when the API exists but developer registration or auth
  behavior is the real blocker
- to `deck-gateway`, `terraform-konnect`, or `kongctl-declarative` when the
  operator wants to codify or change the resulting config

## Konnect-Specific Gotchas

- Catalog readiness and Portal publication are related but not identical.
- APIs should include a spec or documentation when developer-facing docs are
  expected; missing docs often start upstream of the Portal.
- API versioning and spec versioning are related but not interchangeable.
- Developer self-service depends on implementation linkage, not only on the API
  object existing in Catalog.
- Packages can clarify consumption boundaries, but they do not fix a confused
  underlying API model.

## Validation Checklist

Before answering, verify that you can state:

- which Catalog object is missing or malformed
- whether API identity and versioning are correct
- whether spec and documentation readiness are complete
- whether an implementation or linked service exists where needed
- whether the problem belongs in Catalog, Portal publication, or app auth
- which declarative tool skill owns the needed change

## Handoffs

- Use `konnect-api-publish` when the Catalog object is ready and the remaining
  problem is publication to Portal.
- Use `konnect-app-auth` when the issue is developer self-service, application
  registration, or auth strategy behavior.
- Use `deck-gateway`, `terraform-konnect`, or `kongctl-declarative` when the
  operator wants to encode or apply the resulting change as config.
