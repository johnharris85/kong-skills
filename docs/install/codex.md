# Codex

![Codex](https://img.shields.io/badge/Codex-plugin-0A0A0A?style=for-the-badge&logo=openai&logoColor=white)

Codex can use this repo in two ways:

- skill install via `npx skills` plus MCP config
- plugin install via a personal or team marketplace

## Skill-Only Path

This is the preferred public install path:

```bash
npx skills add kong/skills
```

Install only one skill from this repo:

```bash
npx skills add kong/skills --skill datakit
```

If you only use the skill-only path, you do not need `KONNECT_TOKEN`.

If you installed via `gh skill`, you can also update one installed skill with `gh skill update datakit`.

Codex does not currently have a documented SessionStart-style startup hook equivalent in the official docs I checked, so this repo does not document automatic `npx skills update` hooks for Codex.

If you also want the `kong-konnect` MCP server, add the MCP config from [`.mcp.json`](../../.mcp.json). That is when `KONNECT_TOKEN` is required.

## Personal Marketplace Path

Use this when you want the checked-in local plugin wrapper rather than the shared-skill install:

```bash
mkdir -p ~/plugins ~/.agents/plugins
git clone https://github.com/kong/skills.git ~/plugins/kong-skills
```

Use [`.agents/plugins/marketplace.json`](../../.agents/plugins/marketplace.json) as the checked-in reference shape for the marketplace entry. If you already have a marketplace file, merge the `kong-skills` plugin entry into it instead of overwriting unrelated plugins.

Then install `kong-skills` from your personal marketplace in Codex.
