# Event Path Map

Use this file when the operator starts with a symptom instead of a clear Event
Gateway failure hop.

## Core Rule

Follow the event path end to end:

client -> listener -> virtual cluster -> backend cluster -> auth/policy

## Symptom Map

| Symptom | Start here |
|---|---|
| Cannot connect at all | listener and hostname branch |
| Connects but wrong backend behavior | cluster routing branch |
| Connects but denied | auth/policy branch |
| Objects seem present but nothing lines up | control plane and object-chain verification first |

## What To Return

Return:

- which hop is most likely failing
- which deeper reference branch should be loaded next
- whether this is still Event Gateway-specific or has become a broader access problem
