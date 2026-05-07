# Cursor

![Cursor](https://img.shields.io/badge/Cursor-plugin-222222?style=for-the-badge&logo=cursor&logoColor=white)

This repo now includes a native Cursor plugin surface:

- [`.cursor-plugin/plugin.json`](../../.cursor-plugin/plugin.json)
- [`.cursor-plugin/marketplace.json`](../../.cursor-plugin/marketplace.json)

The bundled MCP server is `kong-konnect` at `https://us.mcp.konghq.com`.

## Install

If your Cursor build supports installing a plugin from a repository or local
checkout, point it at this repo and install `kong-skills`.

Local checkout path:

```bash
git clone https://github.com/kong/skills.git ~/plugins/kong-skills
mkdir -p ~/.cursor/plugins/local
ln -s ~/plugins/kong-skills ~/.cursor/plugins/local/kong-skills
```

Restart Cursor after installing the local plugin.

## Skill-Only Path

If you only want the shared skills:

```bash
npx skills add kong/skills
```

If you also want the MCP server outside the plugin wrapper, use
[`mcp.json`](../../mcp.json) as the checked-in reference shape.

`KONNECT_TOKEN` is only used by the MCP server config. If you only install the
shared skills, it is not needed.
