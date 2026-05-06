# Resource Discovery

Use this file when the main issue is which `kongctl get` path should be used.

## Core Rule

Use help and the live CLI surface to discover the correct read path instead of
guessing resource names or child-resource patterns.

## Discovery Order

1. `kongctl help`
2. `kongctl get --help`
3. `kongctl get <resource> --help`
4. inspect child-resource forms only after the parent resource type is proven

## Common Cases

| Need | Default pattern |
|---|---|
| List resources | `kongctl get <resource> -o json` |
| Get one resource | `kongctl get <resource> "<name-or-id>" -o json` |
| Query child resources | `kongctl get <parent> <child> --<parent>-name "<name>" -o json` |

## What To Return

Return:

- which resource path is the right one
- whether the operator needs parent-child context
- whether a domain skill should own the diagnosis after the read
