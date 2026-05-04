# Structure

This file maps the install/config surfaces generated or maintained in this repo, including manual reference snippets.

This is a contributor file map, not an end-user guide. The goal is to keep the repo minimal and self-contained: shared skill content lives once under `skills/`, generated install metadata stays near repo root, and tool-specific docs point back to those checked-in reference shapes.

## Shared Skills

- `skills/`
  - Canonical shared skills used by `npx skills` and plugin installs that bundle shared skills.
- `docs/skills.md`
  - Generated inventory of the currently shipped skills.

## Claude Code

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `claude.mcp.json`

## Codex

- `.codex-plugin/plugin.json`
- `.mcp.json`
- `.agents/plugins/marketplace.json`

## Gemini CLI

- `gemini-extension.json`
- `GEMINI.md`
  - Shipped extension context file referenced by `contextFileName`.

## Contributor Helpers

- `AGENTS.md`
  - Contributor-facing skill authoring guide used in this repo.
- `CLAUDE.md`
  - Symlink to `AGENTS.md` for Claude-friendly local discovery. This is a helper, not part of the OCI artifact payload.

## GitHub Copilot

- `copilot-mcp.json`
  - Manual reference snippet for workspace MCP config such as `.vscode/mcp.json`

## Cursor

- `cursor-mcp.json`
  - Manual reference snippet for `.cursor/mcp.json`

## Release And Validation

- `.github/workflows/validate.yml`
  - Validates generated metadata and the OCI artifact packaging path on pull requests and `main`.
- `.github/workflows/release-oci.yml`
  - Canonical publishing workflow for tags, GitHub releases, and the OCI artifact.
- `docs/release.md`
  - Contributor-facing release preparation and trigger process.
- `.dockerignore`
  - Narrows the OCI build context to the shipped skill payload.
