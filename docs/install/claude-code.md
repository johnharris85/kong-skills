# Claude Code

![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-111111?style=for-the-badge&logo=anthropic&logoColor=white)

Claude Code uses the plugin manifest in [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) and the marketplace catalog in [`.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json).

## Install

```bash
/plugin marketplace add kong/skills
/plugin install kong-skills@kong-skills
```

## What Gets Installed

- the shared skills from `skills/`
- the `kong-konnect` MCP server entry

## Components Instead Of The Full Plugin

Skill-only install:

```bash
npx skills add kong/skills
```

That does not require `KONNECT_TOKEN`.

If you also want the MCP server without using the plugin wrapper, add the `kong-konnect` server manually using [`.mcp.json`](../../.mcp.json) as the reference shape. That is when `KONNECT_TOKEN` is required.
If you are configuring Claude directly, use [claude.mcp.json](../../claude.mcp.json) as the Claude-specific MCP reference shape.
