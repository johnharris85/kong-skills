# Gemini CLI

![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-extension-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)

Gemini CLI uses [`gemini-extension.json`](../../gemini-extension.json) and [`GEMINI.md`](../../GEMINI.md).

The extension configures the `kong-konnect` MCP server at `https://us.mcp.konghq.com`.

## Install

```bash
gemini extensions install https://github.com/kong/skills
```

To enable Gemini's native extension auto-update at install time:

```bash
gemini extensions install https://github.com/kong/skills --auto-update
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
npx skills add kong/skills --skill gateway-plugin-datakit
```

That does not require `KONNECT_TOKEN`.

If you installed via `gh skill`, you can also update one installed skill with `gh skill update gateway-plugin-datakit`.

## Auto-Update

Prefer Gemini CLI's native extension update flow over a custom startup hook.

Update one installed extension explicitly:

```bash
gemini extensions update kong-skills
```

Update all installed extensions:

```bash
gemini extensions update --all
```

Be careful with auto-update. It can pull newer skill instructions automatically, which may introduce supply-chain or security risk if content changes upstream without review.

If you want the MCP server without the full extension wrapper, configure `kong-konnect` manually using [`.mcp.json`](../../.mcp.json) or the server block in [`gemini-extension.json`](../../gemini-extension.json). That is when `KONNECT_TOKEN` is required.
