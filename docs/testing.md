# Testing

This repo favors lightweight checks over tool-driven install automation.

## Default Workflow

1. Run `mise run check`.
2. If you changed install docs, plugin manifests, or MCP config surfaces, manually verify only the affected tools.
3. Use a scratch project or disposable user profile when a tool writes local state.

## Trigger Harness

For routing-only regression checks, use the Codex proxy harness described in [docs/trigger-harness.md](./trigger-harness.md).

Useful commands:

- `mise run trigger:spike`
- `mise run trigger:list`
- `mise run trigger:test`
- `mise run trigger:test -- --skill datakit`
- `mise run trigger:test -- --dry-run`

The trigger harness uses synthetic mini-skills and only checks whether a prompt appears to route to a skill. It does not test the real skill body.

## Shared Skill Installers

### `npx skills`

- Prerequisite: `node` and `npx`
- Command: `npx skills add kong/skills`
- Expected result: install completes without errors and the `datakit` skill is available in the target host
- Quick prompt: `When should you use the datakit skill?`
- Cleanup: remove the installed skill from the scratch project or discard the scratch project

### `gh skill`

- Prerequisite: GitHub CLI `v2.90.0+`
- Note: `gh skill` is in public preview
- Command: `gh skill install kong/skills`
- Single-skill command: `gh skill install kong/skills datakit`
- Host-specific command: `gh skill install kong/skills datakit --agent codex`
- Expected result: install completes without errors and the `datakit` skill is available in the target host
- Quick prompt: `When should you use the datakit skill?`
- Cleanup: remove the installed skill from the target host or discard the scratch profile

## Tool Spot Checks

### Claude Code

- Install path: [docs/install/claude-code.md](./install/claude-code.md)
- Verify after install: `kong-skills` appears as installed and `datakit` is available in a fresh session
- MCP check when using the plugin path: confirm `kong-konnect` is configured
- Quick prompt: `What Kong-specific skills are available in this environment?`
- Cleanup: uninstall the plugin or discard the scratch profile

### Codex

- Install path: [docs/install/codex.md](./install/codex.md)
- Recommended lightweight check: use the skill-only path first
- Verify after install: `datakit` is available in a fresh session
- MCP check when using the marketplace/plugin path: confirm `kong-konnect` is configured
- Quick prompt: `Explain what the datakit skill is for in one paragraph.`
- Cleanup: remove the skill install or discard the scratch profile

### Gemini CLI

- Install path: [docs/install/gemini-cli.md](./install/gemini-cli.md)
- Verify after install: the extension or skill install completes and `datakit` is available in a fresh session
- MCP check when using the extension path: confirm the session can see `kong-konnect`
- Quick prompt: `When should you reach for the datakit skill instead of generic reasoning?`
- Cleanup: uninstall the extension or remove the skill install from the scratch profile

### Cursor

- Install path: [docs/install/cursor.md](./install/cursor.md)
- Verify after install: the MCP config is present and `datakit` is available to the project
- MCP check: confirm the session can see `kong-konnect`
- Quick prompt: `Summarize the datakit skill in two sentences.`
- Cleanup: remove the copied MCP config and installed skill from the scratch project

### GitHub Copilot

- Install path: [docs/install/github-copilot.md](./install/github-copilot.md)
- Verify after install: `.vscode/mcp.json` is present and the shared skill install completes
- MCP check: confirm the session can see `kong-konnect`
- Quick prompt: `What task category should trigger the datakit skill?`
- Cleanup: remove the copied MCP config and installed skill from the scratch project

## When To Stop

You do not need to manually verify every tool for every change.

- Skill text only: `mise run check` is usually enough.
- Tool-specific manifest or install doc: verify only that tool.
- Shared MCP config changes: verify one plugin-style path and one skill-plus-MCP path.
- Release prep: run `mise run check` and spot-check the tools affected by the release.
- Trigger tuning: run `mise run trigger:test` for the affected skill before doing broader manual checks.
