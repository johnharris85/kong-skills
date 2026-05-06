# Topology Choice

Use this file when the main bootstrap decision is what kind of environment is
being built.

## Core Rule

Separate quick proof-of-life from durable environment design. A local or guided
quickstart is not automatically the right shared operating model.

## Questions To Clarify

- is this a local proof-of-capability or a long-lived team environment
- are data planes self-hosted, Dedicated Cloud Gateways, or another managed
  hosting shape
- is this dev, staging, prod, or a shared platform slice

## Common Decision Patterns

| Situation | Default interpretation |
|---|---|
| Tutorial or first-time setup | quickstart plus later durable codification |
| Shared team environment | explicit region, ownership, and durable toolchain from the start |
| Production bootstrap | avoid treating quickstart defaults as final architecture |

## What To Return

Return:

- the intended topology shape
- whether the current path is quickstart-only or durable
- which next skill or tool should own codification
