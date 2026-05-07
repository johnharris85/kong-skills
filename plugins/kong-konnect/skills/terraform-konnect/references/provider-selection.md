# Provider Selection

Use this file when the main question is whether to use `kong/konnect` or
`kong/konnect-beta`.

## Default Rule

Prefer `kong/konnect`. Treat `kong/konnect-beta` as an explicit exception for
beta-only coverage the user actually needs.

## Decision Rules

- If the repository already standardizes on `kong/konnect`, keep it unless the
  task is blocked by missing coverage.
- If the user asks for a beta-only feature, say that the exception is about
  coverage, not preference.
- If the repo already uses both providers, preserve the existing alias and
  module pattern rather than collapsing them casually.

## Return Shape

Return:

- which provider should own the change
- why the supported provider is sufficient or insufficient
- whether the exception affects only one module or the broader repo shape
