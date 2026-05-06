# IdP and Role Model

Use this file when SSO, SCIM, external groups, or additive roles are the main
access boundary.

## Core Rule

Treat externally mastered identity data as read-only from the Konnect side
unless proven otherwise.

## Useful Distinctions

| Branch | Meaning |
|---|---|
| Additive roles | multiple memberships can expand access |
| Resource-scoped roles | access may differ by control plane, portal, or other surface |
| IdP-managed groups | changes may need to happen outside Konnect |
| SCIM-provisioned identity | lifecycle and membership may be externally controlled |

## What To Return

Return:

- whether the issue is role layering or external identity mastery
- whether the next action belongs in Konnect or the IdP
- whether resource-scoped access differs from org-wide assumptions
