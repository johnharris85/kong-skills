# GitHub Copilot

![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-mcp-24292F?style=for-the-badge&logo=githubcopilot&logoColor=white)

GitHub Copilot can use the project-level MCP config or a copied manual snippet.

The MCP server configured here is `kong-konnect` at `https://us.mcp.konghq.com`.

## Project-Level MCP

This repo includes [`.github/mcp.json`](../../.github/mcp.json) for Copilot-compatible project setups.

## Manual MCP Snippet

Use [copilot/mcp.json](../../copilot/mcp.json) as the reference snippet for manual Copilot configuration.

## Skills

```bash
npx skills add johnharris85/kong-skills
```

`KONNECT_TOKEN` is only needed if you also enable the `kong-konnect` MCP server for Copilot.
