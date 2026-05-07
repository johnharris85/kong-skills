# Auth and Policy Order

Use this file when clients can reach the listener but fail afterward due to
auth or policy behavior.

## Core Rule

Do not debug policy before proving the path is correct, and do not treat a
denial as a listener failure once reachability is known.

## Useful Distinctions

| Branch | Meaning |
|---|---|
| Auth mismatch | credentials or identity do not match expectations |
| Policy attachment issue | policy is bound to the wrong listener/hostname/path |
| Policy evaluation issue | the right policy is attached but the outcome is still wrong |

## What To Return

Return:

- whether the failure is auth or policy first
- whether attachment order or evaluation order is the likely cause
- whether `konnect-access-scope` should own the next step
