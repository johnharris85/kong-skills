# Gemini CLI

![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-extension-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)

Gemini CLI uses [`gemini-extension.json`](../../gemini-extension.json) and [`GEMINI.md`](../../GEMINI.md).

The extension configures the `kong-konnect` MCP server at `https://us.mcp.konghq.com`.

## Install

```bash
gemini extensions install https://github.com/johnharris85/kong-skills
```

## Authentication

Gemini CLI should prompt for `KONNECT_TOKEN` from the extension settings and send:

```text
Authorization: Bearer ${KONNECT_TOKEN}
```

## Components Instead Of The Full Extension

Skill-only install:

```bash
npx skills add johnharris85/kong-skills
```

That does not require `KONNECT_TOKEN`.

If you want the MCP server without the full extension wrapper, configure `kong-konnect` manually using [`.mcp.json`](../../.mcp.json) or the server block in [`gemini-extension.json`](../../gemini-extension.json). That is when `KONNECT_TOKEN` is required.
