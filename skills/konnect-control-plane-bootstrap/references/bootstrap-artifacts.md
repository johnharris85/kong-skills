# Bootstrap Artifacts

Use this file when the operator needs the bootstrap milestones separated into
concrete stages.

## Core Rule

Control plane creation, data plane attachment, and first Gateway config are
different milestones. Do not call bootstrap complete after only the first one.

## Milestone Split

| Milestone | What it proves |
|---|---|
| Control plane exists | the platform object was created in the intended region |
| Data plane attachment works | the connectivity and hosting path are viable |
| First Gateway config applies | the environment is ready for runtime config workflows |

## Common Misreads

| Symptom | Better interpretation |
|---|---|
| Control plane exists | not enough; attachment and config still unproven |
| Quickstart worked once | not enough; durable ownership path may still be undefined |
| First config failed | bootstrap is incomplete, not just a normal Gateway drift issue |

## What To Return

Return:

- which milestone is complete
- which milestone is still missing
- whether the next step is bootstrap, gateway triage, or declarative codification
