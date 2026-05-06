# Auth Strategy Selection

Use this file when the main decision is which application-auth strategy model
fits the use case.

## Core Rule

Choose the strategy based on the developer workflow, not on what is easiest to
name in the UI.

## Strategy Map

| Strategy | Best fit |
|---|---|
| `key-auth` | built-in API key flows |
| self-managed OIDC | developers bring pre-registered clients |
| DCR | the Portal should create and manage IdP clients dynamically |

## Important Constraints

- strategies are reusable across APIs and Portals
- one application can use only one auth strategy
- the strategy decision is separate from whether the API is published at all

## What To Return

Return:

- which strategy best fits the intended self-service model
- why the alternatives are worse for this workflow
- whether the next issue is publication, registration, or enforcement
