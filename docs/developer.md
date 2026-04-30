# Developer Guide

This repo keeps authoring simple:

1. add or update a skill under `skills/`
2. sync generated metadata
3. run repo validation
4. run optional trigger checks when you change routing-sensitive descriptions
5. do manual spot checks only for the install surfaces you changed

This repo is optimized for contributors maintaining the shared source package. Consumers generally see the synced plugin manifests, extension metadata, or installed skill content through their host tool rather than this working tree.

For local guardrails, install the repo hooks once:

```bash
mise run hooks:install
```

That enables the checked-in `pre-commit` and `pre-push` hooks, both of which run `mise run check`.

## Add A Skill

Scaffold the boilerplate with one command:

```bash
mise run skill:new -- your-skill-name
```

That creates:

- `skills/<skill-name>/SKILL.md`
- `tests/trigger-fixtures/<skill-name>.yaml`

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

Optional companion directories are supported:

- `skills/<skill-name>/references/`
- `skills/<skill-name>/assets/`
- `skills/<skill-name>/scripts/`

Keep `SKILL.md` as the only file at the skill root. Companion content should stay lightweight, non-hidden, non-executable, and easy to review.

`mise run skill:new` creates both:

- a starter `SKILL.md` with the required frontmatter and placeholders you are expected to replace
- the trigger fixture with placeholder positive and negative prompts you are expected to tune for routing sensitivity

If you need to add or recreate only the trigger fixture later, use:

```bash
mise run trigger:new -- your-skill-name
```

## Sync And Validate

```bash
mise run deps
mise run skill:new -- your-skill-name
mise run sync
mise run check
mise run trigger:test -- --skill your-skill-name --dry-run
mise run ci
mise run release:prepare -- 1.0.1
mise run release -- 1.0.1
```

If `mise` says the repo is not trusted:

```bash
mise trust
```

If you have not already enabled the repo hooks, do that once as well:

```bash
mise run hooks:install
```

## What Sync Updates

- the skill arrays in [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json)
- the Claude marketplace keywords in [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json)
- the skill arrays in [`.codex-plugin/plugin.json`](../.codex-plugin/plugin.json)
- the Codex marketplace listing in [`.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json)
- the generated Codex plugin keywords and capabilities
- the generated skill inventory in [docs/skills.md](skills.md)
- the aligned MCP config surfaces

## What Stays Manual

- explanatory docs
- marketplace positioning text
- harness-specific install prose
- decisions about whether a skill needs `references/`, `assets/`, or `scripts/`
- decisions about which prompts belong in the trigger fixtures
- replacing scaffold placeholders with real Kong-specific content

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

For routing-only checks, see [docs/trigger-harness.md](trigger-harness.md).

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
```

Use `mise run release:prepare` when you want the version bump staged locally without publishing anything yet.

## Full Release Flow

Use:

```bash
mise run release -- 1.0.1
```

That flow:

- updates versioned manifests
- validates the repo
- commits the release bump
- pushes `main`
- creates the GitHub release and remote tag with `gh release create --target main --generate-notes`
- fetches the created tag back into the local repo

Release prerequisites:

- a clean git working tree
- `gh` installed and authenticated
- push access to `origin`

This local release flow is a good fit for this repo because releases are mostly manifest/version management rather than a build artifact pipeline. A GitHub Action on tag push would also work, but it is not required unless you want fully server-side release publishing.
