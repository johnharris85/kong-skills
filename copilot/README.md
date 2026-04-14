# GitHub Copilot

GitHub Copilot supports MCP in IDEs and Copilot CLI.

Use [mcp.json](/home/john/projects/kong-skills/copilot/mcp.json) as the reference snippet for manual setup. This repo also includes [`.github/mcp.json`](/home/john/projects/kong-skills/.github/mcp.json) as a project-level configuration file for Copilot CLI-compatible layouts.

## Copilot CLI

Copilot CLI supports project-level MCP config in `.github/mcp.json`, `.mcp.json`, or `.vscode/mcp.json`. This repo ships `.github/mcp.json` already.

You can also copy the snippet directly into your user-level or project-level MCP config if needed.

## IDEs

For IDEs that expose an `mcp.json` editor, use the same structure from [mcp.json](/home/john/projects/kong-skills/copilot/mcp.json):

- server name: `kong-konnect`
- URL: `https://us.mcp.konghq.com`
- header: `Authorization: Bearer ${KONNECT_TOKEN}`

## Skills

Install the shared skills separately:

```bash
npx skills add johnharris85/kong-skills
```

That currently installs the `datakit` skill from this repo.
