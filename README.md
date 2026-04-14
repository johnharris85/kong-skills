# Kong Skills

Portable `SKILL.md` workflows plus Kong remote MCP configuration for the main AI coding harnesses.

This repo is designed to do two things:

- distribute shared skills from `skills/` that can be installed across many agents
- bundle the Kong MCP server at `https://us.mcp.konghq.com` as `kong-konnect` with bearer-token auth using `KONNECT_TOKEN`

The shared skills are the source of truth. Platform-specific wrapper files only tell each harness how to load those same skills and how to connect to the Kong MCP endpoint.

## What This Repo Contains

- `skills/datakit`: Kong DataKit design, YAML authoring, debugging, and reference material
- `.claude-plugin/plugin.json`: Claude Code plugin manifest
- `.codex-plugin/plugin.json`: Codex plugin manifest
- `.mcp.json`: Codex MCP config
- `.agents/plugins/marketplace.json`: Codex marketplace entry
- `gemini-extension.json`: Gemini CLI extension manifest
- `.github/mcp.json`: GitHub Copilot project-level MCP config
- `copilot/mcp.json`: Copilot reference snippet
- `copilot/README.md`: Copilot install notes
- `goose/README.md`: Goose extension install notes
- `goose/config.yaml`: Goose config reference
- `cursor/mcp.json`: drop-in Cursor MCP config
- `cursor/README.md`: Cursor install notes
- `mise.toml`: local task runner for sync, validation, and hook setup
- `scripts/check_repo.py`: lightweight Python sync and validation script

## Authentication

All examples in this repo assume the Kong MCP server expects a bearer token:

```text
Authorization: Bearer ${KONNECT_TOKEN}
```

Set `KONNECT_TOKEN` in the harness or plugin install flow you use. Where a format supports explicit MCP headers, this repo already includes the header.

## Install By Harness

### Claude Code

This repo includes [`.claude-plugin/plugin.json`](/home/john/projects/kong-skills/.claude-plugin/plugin.json) and [`marketplace.json`](/home/john/projects/kong-skills/marketplace.json).

Add the repo as a plugin marketplace, then install the plugin:

```bash
/plugin marketplace add johnharris85/kong-skills
/plugin install kong-skills@kong-skills
```

What Claude Code gets from this:

- the shared skills from `skills/`
- the `kong-konnect` MCP server entry from the plugin manifest

### Codex

This repo includes [`.codex-plugin/plugin.json`](/home/john/projects/kong-skills/.codex-plugin/plugin.json), [`.mcp.json`](/home/john/projects/kong-skills/.mcp.json), and [`.agents/plugins/marketplace.json`](/home/john/projects/kong-skills/.agents/plugins/marketplace.json).

There are two useful installation paths:

Plugin and marketplace path:

- add this repo to a Codex plugin marketplace
- install the `kong-skills` plugin from that marketplace
- Codex will load the shared skills and the `kong-konnect` MCP server entry

Skill-only path:

```bash
npx skills add johnharris85/kong-skills
```

If you use the skill-only path, you still need to add the Kong MCP server separately using [`.mcp.json`](/home/john/projects/kong-skills/.mcp.json) as the reference shape.

### Gemini CLI

This repo includes [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json) and [`GEMINI.md`](/home/john/projects/kong-skills/GEMINI.md).

Install the extension directly from GitHub:

```bash
gemini extensions install https://github.com/johnharris85/kong-skills
```

Gemini CLI should prompt for `KONNECT_TOKEN` from the `settings` block and use that for the MCP header configuration in the extension manifest.

### Cursor

Cursor does not use the same plugin packaging flow here, so install it in two parts:

1. Add the MCP server config:

```bash
mkdir -p .cursor
cp cursor/mcp.json .cursor/mcp.json
```

2. Install the shared skills:

```bash
npx skills add johnharris85/kong-skills
```

See [cursor/README.md](/home/john/projects/kong-skills/cursor/README.md) for the Cursor-specific notes, including the Add to Cursor direction.

### GitHub Copilot

GitHub Copilot supports MCP in Copilot CLI and IDE integrations. This repo includes:

- [`.github/mcp.json`](/home/john/projects/kong-skills/.github/mcp.json) for project-level Copilot CLI setup
- [copilot/mcp.json](/home/john/projects/kong-skills/copilot/mcp.json) as a reference snippet for manual MCP configuration
- [copilot/README.md](/home/john/projects/kong-skills/copilot/README.md) with install notes

Project-level Copilot CLI support is already wired by [`.github/mcp.json`](/home/john/projects/kong-skills/.github/mcp.json).

Install the shared skills separately:

```bash
npx skills add johnharris85/kong-skills
```

### Goose

Goose supports MCP-based extensions, including remote Streamable HTTP extensions. This repo includes:

- [goose/README.md](/home/john/projects/kong-skills/goose/README.md) with the recommended install flow
- [goose/config.yaml](/home/john/projects/kong-skills/goose/config.yaml) as a config reference

Install the shared skills separately:

```bash
npx skills add johnharris85/kong-skills
```

### Other Harnesses

Most other coding agents can consume the shared skills through:

```bash
npx skills add johnharris85/kong-skills
```

Then copy the Kong MCP settings from one of the repo configs into that harness's MCP configuration format:

- [`.mcp.json`](/home/john/projects/kong-skills/.mcp.json)
- [cursor/mcp.json](/home/john/projects/kong-skills/cursor/mcp.json)
- [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json)

## Local Validation

This repo uses `mise` as the task runner so local checks match CI.

Common commands:

```bash
mise run sync
mise run check
mise run ci
mise run hooks:install
```

What they do:

- `mise run sync`: rewrites generated metadata to keep the repo in sync
- `mise run check`: validates manifests, skills, MCP naming, and generated sections
- `mise run ci`: same validation entrypoint used by GitHub Actions
- `mise run hooks:install`: installs the repo-local pre-commit hook

After `mise run hooks:install`, commits will run `mise run check` automatically through [`.githooks/pre-commit`](/home/john/projects/kong-skills/.githooks/pre-commit).

## Available Skills

<!-- generated:available-skills:start -->
- `datakit`: Build and debug Kong DataKit plugin flows. Use when users want to create, modify, debug, or understand DataKit YAML configurations — including designing node-based API workflows, writing jq transformations, configuring caching or branching, or troubleshooting flow execution. Triggers on mentions of DataKit, Kong API orchestration, or decK plugin config with workflow nodes.
<!-- generated:available-skills:end -->

## Developer Guide

### Add A New Skill

1. Create a new folder under `skills/<skill-name>/`.
2. Add `skills/<skill-name>/SKILL.md`.
3. Start the skill with YAML frontmatter:

```md
---
name: your-skill-name
description: One-line discovery description for agent matching.
---
```

4. Write the markdown body with:

- when the skill should be used
- the workflow the agent should follow
- any tool or MCP expectations
- output guidance when the format matters

5. If a skill depends on the Kong MCP server in Codex, you can add `skills/<skill-name>/agents/openai.yaml` to declare that MCP dependency for Codex explicitly.
6. Run `mise run sync` after adding the skill.

That is the normal path for future skill additions. In practice, adding a new skill should be:

1. add `skills/<skill-name>/SKILL.md`
2. run `mise run sync`
3. run `mise run check`

### What Sync Updates

`mise run sync` currently keeps these in sync:

- the `skills` arrays in [`.claude-plugin/plugin.json`](/home/john/projects/kong-skills/.claude-plugin/plugin.json) and [`.codex-plugin/plugin.json`](/home/john/projects/kong-skills/.codex-plugin/plugin.json)
- the generated "Available Skills" section in [README.md](/home/john/projects/kong-skills/README.md)
- the MCP server name and auth shape in [`.mcp.json`](/home/john/projects/kong-skills/.mcp.json), [cursor/mcp.json](/home/john/projects/kong-skills/cursor/mcp.json), and [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json)
- the Codex plugin keywords and capabilities so they stay aligned with the repo's current purpose

Marketplace listings are plugin-level metadata, not per-skill metadata, so they do not need to change when you add a new skill unless the plugin's user-facing description or release version changes.

Sync is intentionally conservative. It auto-updates structured metadata that should not drift, but it does not try to invent marketing copy or broad capability tags from skill text. That is deliberate, because auto-derived keywords tend to get noisy and misleading.

### What Check Validates

`mise run check` validates:

- every `skills/*/SKILL.md` exists and has `name` and `description` frontmatter
- each skill directory matches its frontmatter name
- plugin manifests reference the full discovered skill set
- generated README skill listings are in sync
- JSON config files are well-formed and use the `kong-konnect` MCP name
- Copilot MCP config snippets stay in sync with the primary MCP definition
- support docs for Copilot, Goose, and Cursor keep the expected MCP name, URL, and token references
- any `skills/**/agents/openai.yaml` files reference `kong-konnect` and the expected MCP URL
- plugin names, versions, repo URLs, and marketplace entries remain consistent

### Update MCP Wiring

If the remote MCP endpoint or auth contract changes, update these files together:

- [`.mcp.json`](/home/john/projects/kong-skills/.mcp.json)
- [`.claude-plugin/plugin.json`](/home/john/projects/kong-skills/.claude-plugin/plugin.json)
- [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json)
- [cursor/mcp.json](/home/john/projects/kong-skills/cursor/mcp.json)
- any skill-level `agents/openai.yaml` files that declare MCP dependencies

### Keep The Repo Coherent

- treat `skills/` as the canonical content
- avoid copying the same skill into multiple wrapper directories
- keep naming consistent across manifests: the current MCP server name is `kong-konnect`
- keep auth examples aligned on `KONNECT_TOKEN`
- run `mise run sync` before committing structural changes

## CI

GitHub Actions runs [`.github/workflows/validate.yml`](/home/john/projects/kong-skills/.github/workflows/validate.yml), which installs `mise` and executes:

```bash
mise run ci
```

That gives you the same validation path locally and in CI.

## Repo Layout

```text
.
├── .github/workflows/validate.yml
├── .github/mcp.json
├── .githooks/pre-commit
├── copilot/
│   ├── README.md
│   └── mcp.json
├── goose/
│   ├── README.md
│   └── config.yaml
├── scripts/check_repo.py
├── mise.toml
├── skills/
│   └── datakit/
│       ├── SKILL.md
│       └── references/
├── .claude-plugin/plugin.json
├── marketplace.json
├── .codex-plugin/plugin.json
├── .mcp.json
├── .agents/plugins/marketplace.json
├── cursor/README.md
├── gemini-extension.json
├── GEMINI.md
└── cursor/mcp.json
```
