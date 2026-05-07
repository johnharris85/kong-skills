---
name: kongctl-query
description: Inspect Konnect with read-only kongctl commands. Use to list or get resources, verify authentication, discover command syntax, or shape output as text, JSON, or YAML. Do not use for declarative YAML authoring or plan/apply workflows.
license: MIT
metadata:
  product: kongctl
  category: query
  tags:
    - kongctl
    - konnect
    - read-only
---

# kongctl query commands

## Goal

Use read-only `kongctl` commands to inspect Konnect resource state and return
concise, structured results.

## Tool Positioning

- If the session already has the shared `kong-konnect` MCP server and the user
  needs live Konnect inspection rather than exact CLI syntax, suggest MCP
  first.
- Use this skill when the user wants read-only `kongctl` commands, CLI-shaped
  verification, or filtered output.
- If live state matters and `kong-konnect` MCP is not connected, say so early
  and continue with `kongctl` as the fallback inspection path.
- For mutation requests, preserve the repository's existing toolchain and hand
  off to `kongctl-declarative`, `deck-gateway`, `terraform-konnect`, or
  `terraform-kong-gateway` as appropriate.
- Do not use this skill for manifest authoring, `kongctl` `plan`/`apply`/`sync`
  workflows, or CI/CD scaffolding.

## References To Load

Load only the reference file that matches the active branch:

- `references/resource-discovery.md`
  - Load when the main question is which `kongctl get` resource or child
    resource path should be queried.
- `references/output-shaping.md`
  - Load when the user cares more about JSON/YAML/text shaping and concise
    summarization than raw command discovery.
- `references/auth-and-scope-checks.md`
  - Load when the real problem may be auth, profile, region, or scope rather
    than the resource query itself.

## Validation Contract

### Preflight

- Confirm CLI is installed and runnable: `kongctl version`
- Authenticate with one of:
  - `kongctl login` — preferred for interactive use (browser-based OAuth)
  - `export KONGCTL_DEFAULT_KONNECT_PAT=<token>` — for non-interactive or CI
- PAT tokens are sensitive credentials. Never echo, log, or commit them.
  Prefer `kongctl login` for interactive sessions.
- Select configuration profile when needed: `--profile <name>`
- Verify authentication works: `kongctl get organization -o json`
  This works with all token types (PAT, SPAT, browser login). If it
  returns organization info, auth is confirmed. Do not guess or try other
  commands to check auth.
- Confirm the organization, region, profile, or parent resource scope before
  interpreting a read result as proof.

### Preview

- Choose the smallest read-only command that proves the point:
  - `kongctl help` or `kongctl get <resource> --help` for command shape
  - `kongctl get <resource> -o json` for list proof
  - `kongctl get <resource> "<name-or-id>" -o json` for exact object proof
  - child-resource reads when the proof depends on a parent boundary
- State the expected output shape before relying on it, especially when `--jq`
  filtering or parent-child paths narrow the slice.

### Execute

- Do not mutate. This skill never runs `apply`, `sync`, `adopt`, `patch`, or
  `delete`.
- When another workflow changes state, use this skill only to provide the
  read-only verification commands that should be run afterward.

### Prove

- After another tool mutates state, rerun the exact `get` command that shows
  the affected live object now exists or now has the intended fields.
- Confirm the exact resource slice touched instead of treating org-level auth
  success as proof of the resulting object.
- If the result is empty, distinguish "no resources found" from auth or scope
  failure.

## Config and Environment Overrides

- `kongctl` flags can be defaulted by profile config and environment variables.
- Environment variable pattern: `KONGCTL_<PROFILE>_<PATH>` 
- Example: `KONGCTL_DEFAULT_OUTPUT=yaml` sets `--output` default for the
  `default` profile.
- For this skill, pass explicit `-o json` or `-o yaml` on query commands to
  avoid unexpected profile/env defaults.
- When troubleshooting output behavior, inspect relevant env vars:
  - `env | grep '^KONGCTL_.*OUTPUT'`
  - `env | grep '^KONGCTL_PROFILE'`

## Operating Rules

- Use only read-only operations in this skill.
- Prefer `get`, `list`, and `help` commands.
- Do not run mutating commands such as `create`, `apply`, `patch`, `delete`,
  or `adopt`.
- Treat this skill as the CLI-shaped verification companion for other Konnect
  workflows when the user wants exact read-only proof.
- Hand off mutation requests to the tool skill that matches the repository:
  `kongctl-declarative`, `deck-gateway`, `terraform-konnect`, or
  `terraform-kong-gateway`.

## Workflow

1. Identify the resource type and the exact proof the user needs.
2. Run preflight checks for CLI availability, auth, and scope.
3. Discover command shape when unsure:
   - `kongctl help`
   - `kongctl get --help`
   - `kongctl get <resource> --help`
   - Extract current `kongctl get` subcommands from help output:
     ```bash
     kongctl get --help | awk '
     /^Available Commands:/ {capture=1; next}
     capture && NF==0 {exit}
     capture && $1 ~ /^[a-z0-9-]+$/ {print $1}
     '
     ```
4. Preview the smallest read-only command that proves the intended slice:
   - Default to JSON output unless YAML is explicitly requested.
   - List resources: `kongctl get <resource> -o json`
   - Get one resource by name or ID:
     `kongctl get <resource> "<name-or-id>" -o json`
   - Query child resources:
     `kongctl get <parent> <child> --<parent>-name "<name>" -o json`
5. Summarize the proof with IDs, names, and timestamps when available.
6. For post-change verification, state the exact `kongctl get` command that
   proves the mutated resource slice now matches intent.

If command shape, output shaping, or auth-scope diagnosis remains unclear after
the first pass, load the matching reference file.

## Common Commands

```bash
# list portals in json format
kongctl get portals -o json

# get organization details as yaml
kongctl get organization -o yaml

# inspect current identity as json
kongctl get me -o json

# get a specific resource by name or ID
kongctl get portals <portal-name> -o json
kongctl get portals <portal-id-uuid> -o json

# query child resources (portal pages)
kongctl get portals pages --portal-name <portal-name> -o json

# query api resources
kongctl get apis -o json

# query api child documents
kongctl get apis documents --api-name <api-name> -o json
```

## Example: List Portals

Use this command to list Developer Portal instances:

```bash
kongctl get portals -o json
```

Expect fields like:
- `id`
- `name`
- `display_name`
- `canonical_domain`
- `created_at`
- `updated_at`
- `labels`

To fetch one portal instead of a list, provide a name or ID:

```bash
kongctl get portals "portal-auth" -o json
kongctl get portals "35fefe98-f098-4a65-9807-d76f40b620cf" -o json
```

## Child Resources

Use parent-child `get` patterns for nested resources.

```bash
# list pages for a specific portal
kongctl get portals pages --portal-name "portal-auth" -o json
```

Discover child commands under a parent by checking parent help:

```bash
kongctl get portals --help
```

If the response is an empty array (`[]`), treat it as a valid "no resources
found" result, not an execution error.

## Output Guidance

- Prefer `-o json` for filtering and automation.
- Use `-o yaml` for human-readable structured output.
- Use `-o text` only when jq filtering is not active.
- If you see `--jq is only supported with --output json or --output yaml`,
  rerun the same command with `-o json`. This error usually means jq is active
  via command flag or profile configuration.

## Built-in jq Filtering

- Use `--jq <expression>` on `get` and `list` commands to filter response data.
- `kongctl` uses built-in `gojq` support, so external `jq` is not required.
- Use `--jq` with `-o json` or `-o yaml` output.
- Quote expressions with single quotes to avoid shell parsing issues.
- Because jq can be enabled from config, prefer explicit `-o json` for `get`
  and `list` commands to avoid output-format errors.

```bash
# select key fields from a list response
kongctl get portals -o json --jq 'map({id, name, display_name})'

# return only portal names
kongctl get portals -o json --jq '.[].name'

# pick selected fields from the current user record
kongctl get me -o json --jq '{id, email}'
```

## Failure Handling

- If `kongctl` is missing, request installation (https://developer.konghq.com/kongctl/) and rerun preflight checks.
- If authentication fails, have user run `kongctl login` or set
  `KONGCTL_DEFAULT_KONNECT_PAT`.
- If a command fails with `--jq is only supported with --output json or --output yaml`,
  rerun the command with `-o json`.
- If output format is unexpected, check for env overrides like
  `KONGCTL_DEFAULT_OUTPUT`.
- If access is denied, report the exact command and resource.
- If no resources are found, report an empty result without treating it as an
  execution error.

## Validation Checklist

Before answering, verify that you can state:

- which auth and scope checks prove the read is happening in the right Konnect
  context
- which exact `kongctl get` or `help` command is the smallest safe proof
- whether the request is pure read-only inspection or a post-change
  verification handoff from another tool
- how an empty result would be distinguished from a scope or auth failure

## Online Documentation

If this skill's guidance is not sufficient, consult or direct users to:

- kongctl docs: https://developer.konghq.com/kongctl/
