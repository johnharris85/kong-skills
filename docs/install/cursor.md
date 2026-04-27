# Cursor

![Cursor](https://img.shields.io/badge/Cursor-mcp-222222?style=for-the-badge&logo=cursor&logoColor=white)

Cursor is an MCP-plus-skills install rather than a native plugin bundle here.

The MCP server configured here is `kong-konnect` at `https://us.mcp.konghq.com`.

## Install

```bash
mkdir -p .cursor
cp cursor-mcp.json .cursor/mcp.json
npx skills add kong/skills
```

`KONNECT_TOKEN` is only used by the MCP server config. If you only install the shared skills, it is not needed.

## Config Files

- MCP config: [cursor-mcp.json](../../cursor-mcp.json)
