# Linked Service and Enforcement

Use this file when Portal-side configuration seems complete but runtime auth is
not being enforced as intended.

## Core Rule

Application auth only works as intended when the API is linked to the correct
Gateway Service and the strategy can actually be enforced on that path.

## Quick Questions

- is the API linked to a Gateway Service at all
- is it the right service
- is the publication carrying the intended auth strategy
- is the issue portal-side workflow or runtime Gateway-side enforcement

## Common Misreads

| Symptom | Better interpretation |
|---|---|
| Publication looks correct but calls still bypass auth | linked service or enforcement path issue |
| Strategy exists but no runtime effect | wrong service linkage or wrong publication boundary |

## What To Return

Return:

- whether the linked service path is complete
- whether the issue is portal/workflow state or Gateway-side enforcement
- whether a tool skill or gateway skill should take over
