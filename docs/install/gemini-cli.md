# Gemini CLI

![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-extension-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)

Gemini CLI uses [`gemini-extension.json`](../../gemini-extension.json) and [`GEMINI.md`](../../GEMINI.md).

The extension configures the `kong-konnect` MCP server at `https://us.mcp.konghq.com`.

## Install

```bash
gemini extensions install https://github.com/kong/skills
```

## Authentication

Gemini CLI should prompt for `KONNECT_TOKEN` from the extension settings and send:

```text
Authorization: Bearer ${KONNECT_TOKEN}
```

## Components Instead Of The Full Extension

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

Gemini CLI supports hooks in `~/.gemini/settings.json` or `.gemini/settings.json`.

Update all globally installed skills at session startup:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "name": "skills-update",
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
            "name": "skills-update-datakit",
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

If you want the MCP server without the full extension wrapper, configure `kong-konnect` manually using [`.mcp.json`](../../.mcp.json) or the server block in [`gemini-extension.json`](../../gemini-extension.json). That is when `KONNECT_TOKEN` is required.
