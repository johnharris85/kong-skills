# Cluster Routing Boundaries

Use this file when the main ambiguity is how a listener path maps through
virtual and backend clusters.

## Core Rule

Once listener reachability is sound, verify that the virtual cluster points to
the intended backend cluster before blaming policy.

## Common Branches

| Symptom | Likely interpretation |
|---|---|
| Right listener, wrong downstream behavior | wrong virtual/backend cluster relationship |
| Listener looks healthy but nothing useful happens | missing backend association |
| Some routes behave, others do not | partial cluster mapping or object-chain mismatch |

## What To Return

Return:

- whether the virtual cluster is correct
- whether the backend target is the intended one
- whether policy should still be evaluated after routing is proven
