# Visibility vs Ingestion

Use this file when the main question is whether data truly is missing or merely
not visible to this caller or in this surface yet.

## Core Rule

Keep these separate:

- no underlying traffic/events
- data exists but is permission-limited
- data exists but the user is in the wrong scope
- data is delayed or partial
- data is genuinely absent because configuration or association is wrong

## Diagnostic Split

| Signal | Likely branch |
|---|---|
| Some users see it, others do not | permissions or visibility |
| Some datasets have data, others do not | wrong surface or configuration boundary |
| Small delay after known traffic | delay/partial visibility first, not immediate outage claims |
| Nothing appears anywhere for proven traffic | configuration, association, or ingestion path problem |

## Return Shape

Return one primary explanation:

- no traffic/events
- visibility-limited
- delayed/partial
- mis-scoped
- configuration or association issue
