---
name: konnect-app-auth
description: Operate Konnect Dev Portal application auth and registration flows. Use for auth strategies, developer self-service, approvals, registrations, app credentials, DCR or OIDC choices, or APIs that are published but still unusable by developers.
license: MIT
metadata:
  product: konnect
  category: application-auth
  tags:
    - kong
    - konnect
    - dev-portal
    - authentication
    - application-registration
---

# Konnect application auth workflow

## Goal

Help an operator configure or troubleshoot how developers register applications,
receive credentials, and use APIs through Konnect Dev Portal and Konnect
Application Auth.

Use this skill when the problem is not merely “is the API published?” but
“can developers actually register and authenticate the way we intended?”

## Tool Selection

- Use the shared `kong-konnect` MCP server first for live inspection of portals,
  publications, application auth strategies, applications, registrations, and
  related approvals.
- Preserve the repository's chosen declarative toolchain when auth resources
  need to change: use `terraform-konnect` for HCL-managed resources and
  `kongctl-declarative` only when the surrounding repo already uses `kongctl`
  for this Konnect workflow.
- Use `deck-gateway` only when the real change is downstream Gateway-entity
  config rather than Portal app-auth configuration.
- If live Konnect state matters and `kong-konnect` MCP is not connected, say so
  early and continue with user-provided artifacts or repo context.

## Workflow

### 1. Separate user auth from application auth

Clarify whether the problem is:

- developer sign-in or SSO into the Portal
- application creation or registration approval
- API-specific registration
- credential issuance
- runtime authorization at the linked Gateway Service

Do not use one answer path for all of these.

### 2. Confirm the self-service chain is complete

For developer self-service to work as intended, inspect:

- Portal security and user-auth settings
- application auth strategy existence
- API linkage to a Gateway Service
- API publication to the intended Portal
- auth strategy selection on that publication

If any link is missing, stop there before debugging credentials.

### 3. Choose the right auth strategy model

Interpret the strategy shape explicitly:

- `key-auth` for built-in API key flows
- self-managed OIDC when developers bring pre-registered clients
- DCR when the Portal should create and manage IdP clients dynamically

Remember:

- strategies are reusable across APIs and Portals
- a developer can use only one auth strategy per application

### 4. Check approvals, RBAC, and registration status

If the strategy is correct but access still fails, inspect:

- whether developer approval is required
- whether application approval is required
- whether the registration is pending, approved, revoked, or rejected
- whether team or RBAC assignment is blocking consumption

Treat “published but unusable” as a workflow-state problem until proven
otherwise.

### 5. Check linked-service enforcement assumptions

Application auth only works the intended way when the API is linked to a
Gateway Service and the auth strategy can be enforced there.

If there is no linked service, or the wrong service is linked, fix that model
before changing strategy details.

### 6. Return the narrowest failure point

Classify the primary issue as:

- missing or wrong Portal user-auth setup
- missing auth strategy
- wrong strategy type for the use case
- missing Gateway Service linkage
- missing or mis-scoped publication
- approval / registration state mismatch
- RBAC or team assignment mismatch

## Konnect-Specific Gotchas

- User auth and application auth are different layers.
- Selecting an auth strategy during publication applies it to the linked
  Gateway Service path, not just to Portal presentation.
- A Gateway Service must be linked for auth strategies to be enforced as
  intended.
- One application can use only one auth strategy.
- Published APIs can still be unusable because approvals, registrations, or
  linked-service enforcement are incomplete.

## Validation Checklist

Before answering, verify that you can state:

- whether the issue is user auth, app auth, registration, approval, or runtime
  enforcement
- whether the self-service chain is complete end to end
- whether the selected strategy type matches the intended developer flow
- whether approvals or RBAC are the real blocker
- whether another skill should own the next step

## Handoffs

- Use `konnect-api-publish` when the API is not yet published or is published to
  the wrong audience.
- Use `konnect-api-catalog` when the API or implementation model itself is not
  ready.
- Use `konnect-access-scope` when the problem is mainly who can view or
  administer the Portal or auth resources.
- Use `terraform-konnect` or `kongctl-declarative` when the operator wants to
  encode or apply the resulting auth changes as config.
