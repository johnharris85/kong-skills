# GitHub Copilot

![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-mcp-24292F?style=for-the-badge&logo=githubcopilot&logoColor=white)

GitHub Copilot can use the manual MCP snippet plus the shared skills install.

The MCP server configured here is `kong-konnect` at `https://us.mcp.konghq.com`.

## Manual MCP Snippet

For workspace-level MCP configuration in VS Code and GitHub Copilot Chat:

```bash
mkdir -p .vscode
cp copilot-mcp.json .vscode/mcp.json
```

Use [copilot-mcp.json](../../copilot-mcp.json) as the checked-in reference snippet. Adjust it if your local Copilot setup needs additional servers or settings.

This repo does not automate GitHub.com coding-agent MCP settings. Treat `copilot-mcp.json` as the IDE/workspace config shape.

## Skills

```bash
npx skills add kong/skills
```

`KONNECT_TOKEN` is only needed if you also enable the `kong-konnect` MCP server for Copilot.
