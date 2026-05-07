# Listener and Hostname Mapping

Use this file when the likely issue is how clients reach the Event Gateway
listener.

## Core Rule

Treat listener reachability as separate from downstream authorization and
routing correctness.

## Questions To Clarify

- which hostname or endpoint the client uses
- which listener should receive that traffic
- whether protocol/port/TLS expectations match the listener configuration
- whether the listener is attached to the intended virtual cluster path

## Common Misreads

| Symptom | Better interpretation |
|---|---|
| TCP connect succeeds | does not prove auth or policy success |
| Client says auth failed | may still be wrong hostname or wrong listener path |
| TLS error | listener/certificate assumption first, not policy |

## What To Return

Return:

- whether the listener mapping is correct
- whether hostname/protocol/TLS is the blocker
- whether the next branch is routing or auth/policy
