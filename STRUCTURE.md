# Repo Structure

This file maps the installable or tool-consumed parts of this repo to the downstream harnesses that use them.

## Shared Skills

- `skills/`
  - Canonical shared skills shipped by this repo.
  - Used by: `npx skills`, Claude Code plugin installs, Codex plugin installs, and any other harness that installs this repo's skills.

## Claude Code

- `.claude-plugin/plugin.json`
  - Claude Code plugin manifest.
  - Used by: Claude Code plugin install flow.

- `marketplace.json`
  - Claude Code marketplace listing for this repo/plugin.
  - Used by: Claude Code plugin marketplace flow.

## Codex

- `.codex-plugin/plugin.json`
  - Codex plugin manifest.
  - Used by: Codex plugin installation.

- `.mcp.json`
  - Root MCP config for Codex-compatible setups.
  - Used by: Codex, and as a reference shape for other MCP-capable harnesses.

- `.agents/plugins/marketplace.json`
  - Codex marketplace entry metadata.
  - Used by: Codex marketplace/repo plugin distribution.

## Gemini CLI

- `gemini-extension.json`
  - Gemini CLI extension manifest.
  - Used by: Gemini CLI extension installation.

- `GEMINI.md`
  - Gemini CLI context file referenced by the extension manifest.
  - Used by: Gemini CLI.

## GitHub Copilot

- `.github/mcp.json`
  - Project-level MCP configuration for Copilot-compatible flows.
  - Used by: GitHub Copilot CLI and repo-level Copilot MCP setups.

- `copilot/mcp.json`
  - Reference snippet for manual Copilot MCP configuration.
  - Used by: contributors configuring Copilot manually.

- `copilot/README.md`
  - Copilot-specific setup notes.
  - Used by: GitHub Copilot users.

## Cursor

- `cursor/mcp.json`
  - Cursor MCP config snippet.
  - Used by: Cursor project or user MCP setup.

- `cursor/README.md`
  - Cursor-specific setup notes.
  - Used by: Cursor users.

## Goose

- `goose/README.md`
  - Goose-specific install instructions.
  - Used by: Goose users.

- `goose/config.yaml`
  - Reference Goose config shape for the remote MCP extension.
  - Used by: contributors configuring Goose manually.
