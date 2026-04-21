# Developer Guide

This repo keeps authoring simple:

1. add or update a skill under `skills/`
2. sync generated metadata
3. run repo validation
4. do manual spot checks only for the install surfaces you changed

## Add A Skill

Create:

- `skills/<skill-name>/SKILL.md`

Start with:

```md
---
name: your-skill-name
description: One-line description used for discovery and matching.
metadata:
  product: product-name
  category: workflow-category
  tags:
    - kong
    - example-tag
---
```

If a skill needs an explicit Codex MCP dependency, add:

- `skills/<skill-name>/agents/openai.yaml`

## Sync And Validate

```bash
mise run sync
mise run check
mise run ci
mise run release:prepare -- 1.0.1
mise run release -- 1.0.1
```

If `mise` says the repo is not trusted:

```bash
mise trust
```

## What Sync Updates

- the skill arrays in [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json)
- the skill arrays in [`.codex-plugin/plugin.json`](../.codex-plugin/plugin.json)
- the generated skill inventory in [docs/skills.md](skills.md)
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

For authoring guidance on what makes a good skill, see [AGENTS.md](../AGENTS.md).

## Supported Tools

- Claude Code: https://code.claude.com/docs
- Codex: https://developers.openai.com/codex/
- Gemini CLI: https://geminicli.com/docs/
- Cursor: https://docs.cursor.com/
- GitHub Copilot: https://docs.github.com/en/copilot
- GitHub CLI `gh skill`: https://cli.github.com/
- `npx skills`: https://github.com/vercel-labs/skills

## Manual Verification

This repo intentionally keeps automated testing narrow.

- Keep CI on `mise run check`.
- Use manual verification when you change install docs, plugin manifests, or MCP config surfaces.
- Prefer scratch projects and disposable user profiles over repo-managed install automation.

See [docs/testing.md](testing.md) for the lightweight verification checklist per supported tool.

## Release Preparation

Use:

```bash
mise run release:prepare -- 1.0.1
```

That updates the release version across:

- [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json)
- [`.codex-plugin/plugin.json`](../.codex-plugin/plugin.json)
- [`gemini-extension.json`](../gemini-extension.json)

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
