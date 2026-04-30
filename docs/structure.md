# Structure

This file maps the install/config surfaces generated or maintained in this repo, including manual reference snippets.

This is a contributor file map, not an end-user guide. The goal is to keep the repo minimal and self-contained: shared skill content lives once under `skills/`, generated install metadata stays near repo root, and tool-specific docs point back to those checked-in reference shapes.

## Shared Skills

- `skills/`
  - Canonical shared skills used by `npx skills` and plugin installs that bundle shared skills.
- `tests/trigger-fixtures/`
  - Prompt fixtures used by the synthetic mini-skill trigger harness.

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

## GitHub Copilot

- `copilot-mcp.json`
  - Manual reference snippet for workspace MCP config such as `.vscode/mcp.json`

## Cursor

- `cursor-mcp.json`
  - Manual reference snippet for `.cursor/mcp.json`
