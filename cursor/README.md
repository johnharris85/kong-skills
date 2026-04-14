# Cursor

Cursor supports MCP servers and can install them from config snippets or an Add to Cursor flow.

## Manual Install

Copy [mcp.json](/home/john/projects/kong-skills/cursor/mcp.json) into `.cursor/mcp.json`:

```bash
mkdir -p .cursor
cp cursor/mcp.json .cursor/mcp.json
```

The configured server is:

- name: `kong-konnect`
- URL: `https://us.mcp.konghq.com`
- header: `Authorization: Bearer ${KONNECT_TOKEN}`

## Skills

Install the shared skills separately:

```bash
npx skills add johnharris85/kong-skills
```

That currently installs the `datakit` skill from this repo.

## Add To Cursor

Cursor also supports an "Add to Cursor" flow for MCP server installation. Use [mcp.json](/home/john/projects/kong-skills/cursor/mcp.json) as the source of truth if you later publish a one-click install link for this server.
