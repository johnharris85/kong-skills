# Developer Guide

This repo keeps authoring simple:

1. add or update a skill under `skills/`
2. sync generated metadata
3. run repo validation
4. manually spot-check only the install surfaces you changed
5. prepare release-versioned manifests in git, then publish from GitHub Actions

This repo is optimized for contributors maintaining the shared source package. Consumers generally see the synced plugin manifests, extension metadata, or installed skill content through their host tool rather than this working tree.

The GitHub Actions workflow is the only publishing path for public releases. Local tooling prepares and validates release content, but it does not tag or publish.

For the full release preparation and trigger sequence, see [docs/release.md](release.md).

## Prerequisites

Install `mise` first:

- `mise`: https://mise.jdx.dev/
- `uv`: https://docs.astral.sh/uv/

Then bootstrap the repo:

```bash
mise trust
mise install
mise run preflight
mise run deps
```

`mise install` provisions the repo-managed Python toolchain from [mise.toml](../mise.toml). `uv` is still required separately. Additional tools are only needed for the flows that use them:

- `docker` for `mise run artifact:check`
- `gh` for `gh skill publish --dry-run`
- `node` and `npx` for shared-installer verification

## Typical Loops

Use the smallest workflow that matches the change:

- Skill text only: `mise run preflight`, `mise run check`
- New skill or frontmatter change: `mise run preflight`, `mise run check`, and `gh skill publish --dry-run`
- Packaging or shared MCP/install surface change: `mise run preflight`, `mise run check`, and `mise run artifact:check`
- Release prep: `mise run preflight`, `mise run ci`, and `mise run artifact:check`

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

Start with:

```md
---
name: your-skill-name
description: One-line description used for discovery and matching.
license: MIT
metadata:
  product: product-name
  category: workflow-category
  tags:
    - kong
    - example-tag
---
```

Optional companion directories are supported:

- `skills/<skill-name>/references/`
- `skills/<skill-name>/assets/`
- `skills/<skill-name>/scripts/`

Keep `SKILL.md` as the only file at the skill root. Companion content should stay lightweight, non-hidden, non-executable, and easy to review.
Set `license: MIT` for skills in this repo unless you have an explicit reason to ship different terms.

This repo does not currently allow per-skill MCP dependency declarations. Keep shared MCP wiring at the repo level for v1.

## Sync And Validate

```bash
mise install
mise run preflight
mise run deps
mise run skill:new -- your-skill-name
mise run sync
mise run check
mise run artifact:check
gh skill publish --dry-run
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
- replacing scaffold placeholders with real Kong-specific content
- any rationale for exceptions to the default `license: MIT`

## Conventions

- canonical public repo: `https://github.com/kong/skills`
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

- Keep CI on `mise run ci` plus the OCI packaging check.
- Use manual verification when you change install docs, plugin manifests, or MCP config surfaces.
- Prefer scratch projects and disposable user profiles over repo-managed install automation.
- Run `gh skill publish --dry-run` before release-oriented changes to catch Agent Skills spec drift and GitHub-side publishability issues.

## Security Notes

- Prefer `gh skill preview` before `gh skill install` when you are validating the public GitHub install path.
- Keep Konnect credentials in host-managed secure settings or environment variables, not in checked-in files.
- Treat startup or auto-update features as opt-in convenience, not the default recommendation.
- The OCI artifact is a `scratch` image that only copies the checked-in `skills/` payload. The release workflow currently disables SBOM and CIS actions for that artifact because there is no package manager or base OS layer to inventory, and the repo relies on checked-in skill review plus explicit packaging validation instead.

See [docs/testing.md](testing.md) for the lightweight verification checklist per supported tool.

## Release Preparation

Use:

```bash
mise run release:prepare -- 1.0.1
mise run preflight
mise run ci
mise run artifact:check
```

Commit the version bump, get it reviewed, and merge it to `main`.

For how the GitHub Actions release is triggered and what it does, see [docs/release.md](release.md).
