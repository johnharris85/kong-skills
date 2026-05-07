# Region, Org, and Team Checks

Use this file when the access symptom may really be the wrong Konnect slice.

## Core Rule

Prove the caller is pointed at the intended region and organization before
reasoning about roles or permissions.

## Common Misroutes

| Symptom | Likely interpretation |
|---|---|
| "Resource does not exist" | wrong region or org |
| "My teammate can see it, I cannot" | wrong org/team context or real permission difference |
| Similar control planes appear missing | wrong environment or ownership slice |

## What To Return

Return:

- whether the caller is in the right region and org
- whether team or environment slicing explains the symptom
- whether permission analysis should continue after that
