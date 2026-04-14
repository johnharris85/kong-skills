# Developer Guide

This repo keeps authoring simple:

1. add or update a skill under `skills/`
2. sync generated metadata
3. run validation

## Add A Skill

Create:

- `skills/<skill-name>/SKILL.md`

Start with:

```md
---
name: your-skill-name
description: One-line description used for discovery and matching.
---
```

If a skill needs an explicit Codex MCP dependency, add:

- `skills/<skill-name>/agents/openai.yaml`

## Sync And Validate

```bash
mise run sync
mise run check
mise run ci
mise run smoke
mise run release:prepare -- 1.0.1
mise run release -- 1.0.1
```

If `mise` says the repo is not trusted:

```bash
mise trust
```

## What Sync Updates

- the skill arrays in [`.claude-plugin/plugin.json`](/home/john/projects/kong-skills/.claude-plugin/plugin.json)
- the skill arrays in [`.codex-plugin/plugin.json`](/home/john/projects/kong-skills/.codex-plugin/plugin.json)
- the generated skill inventory in [docs/skills.md](/home/john/projects/kong-skills/docs/skills.md)
- the aligned MCP config surfaces
- the curated Codex plugin keywords and capabilities

## What Stays Manual

- explanatory docs
- marketplace positioning text
- harness-specific install prose

## Conventions

- canonical MCP server name: `kong-konnect`
- auth variable: `KONNECT_TOKEN`
- keep shared behavior in `SKILL.md`
- keep harness-specific packaging out of skills

For authoring guidance on what makes a good skill, see [AGENTS.md](/home/john/projects/kong-skills/AGENTS.md).

## Supported Tools

- Claude Code: https://code.claude.com/docs
- Codex: https://developers.openai.com/codex/
- Gemini CLI: https://geminicli.com/docs/
- Cursor: https://docs.cursor.com/
- GitHub Copilot: https://docs.github.com/en/copilot
- Goose: https://block.github.io/goose/docs/
- `npx skills`: https://github.com/vercel-labs/skills

## Smoke Tests

Use:

```bash
mise run smoke
```

The smoke runner is intentionally verbose. It logs:

- tool detection
- each smoke case as it starts
- each external command it runs
- the working directory and timeout for that command
- the exit code or timeout result

The smoke suite is gated on tool availability and currently covers:

- repo validation
- MCP config surface alignment
- `npx skills add` from a local path into a temporary project
- Claude local marketplace add and plugin install through direct CLI commands when `claude` is installed
- Codex personal marketplace projection into a temporary home when `codex` is installed
- Codex personal marketplace projection into your real home, with the marketplace file restored after the test
- Gemini extension validate, install, list, and uninstall from a local path when `gemini` is installed

Claude-specific note:

- the chat slash commands do not need to be automated for smoke testing
- Claude Code also supports direct CLI commands like `claude plugin marketplace add ...` and `claude plugin install ...`
- Claude docs also support `claude --plugin-dir <path>` for local plugin development

That means Claude can be tested from the CLI without scripting the chat UI.

Codex-specific note:

- Codex does not currently expose as clean a plugin install CLI as Claude
- the smoke suite therefore tests the personal marketplace file path that Codex would consume in your real home directory
- it restores the marketplace file after the test finishes

Gemini-specific note:

- Gemini CLI does support local extension workflows directly
- the smoke suite uses `gemini extensions validate`, `gemini extensions install <path> --consent --skip-settings`, `gemini extensions list`, and `gemini extensions uninstall`
- Gemini smoke runs in an isolated temporary `HOME` with a precreated `.gemini/extensions` directory so install and cleanup do not touch your real local Gemini state
- `install --consent` is used instead of `link` because it more closely matches the real user install path and is a better fit for automation
- `--skip-settings` is used because the smoke test is validating installability, not the interactive settings configuration flow
- In local testing with Gemini CLI v0.1x, `gemini extensions list` can return exit code `0` but print no entries even after a successful local install into `~/.gemini/extensions/kong-skills`; the smoke suite therefore treats the installed extension directory as the primary success signal and `list` as informational only

## Release Preparation

Use:

```bash
mise run release:prepare -- 1.0.1
```

That updates the release version across:

- [`.claude-plugin/plugin.json`](/home/john/projects/kong-skills/.claude-plugin/plugin.json)
- [`.codex-plugin/plugin.json`](/home/john/projects/kong-skills/.codex-plugin/plugin.json)
- [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json)

After that, run:

```bash
mise run check
git tag -a v1.0.1 -m "v1.0.1"
```

## Full Release Flow

Use:

```bash
mise run release -- 1.0.1
```

That flow:

- updates versioned manifests
- validates the repo
- commits the release bump
- creates the git tag
- pushes `main`
- pushes the tag
- creates a GitHub release with `gh release create --generate-notes`

Release prerequisites:

- a clean git working tree
- `gh` installed and authenticated
- push access to `origin`

This local release flow is a good fit for this repo because releases are mostly manifest/version management rather than a build artifact pipeline. A GitHub Action on tag push would also work, but it is not required unless you want fully server-side release publishing.
