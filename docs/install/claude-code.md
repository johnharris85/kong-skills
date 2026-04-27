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

Install only one skill from this repo:

```bash
npx skills add kong/skills --skill datakit
```

That does not require `KONNECT_TOKEN`.

If you installed via `gh skill`, you can also update one installed skill with `gh skill update datakit`.

## Optional Startup Auto-Update Hook

Claude Code supports hooks in `~/.claude/settings.json` or `.claude/settings.json`.

Update all globally installed skills at session startup:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "npx skills update -g -y 2>/dev/null"
          }
        ]
      }
    ]
  }
}
```

Update one installed skill instead:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "npx skills update -g -y datakit 2>/dev/null"
          }
        ]
      }
    ]
  }
}
```

Be careful with startup auto-update hooks. They can pull newer skill instructions automatically at session start, which may introduce supply-chain or security risk if a skill changes upstream without review.

If you also want the MCP server without using the plugin wrapper, add the `kong-konnect` server manually using [`.mcp.json`](../../.mcp.json) as the reference shape. That is when `KONNECT_TOKEN` is required.
If you are configuring Claude directly, use [claude.mcp.json](../../claude.mcp.json) as the Claude-specific MCP reference shape.
