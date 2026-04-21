# Codex

![Codex](https://img.shields.io/badge/Codex-plugin-0A0A0A?style=for-the-badge&logo=openai&logoColor=white)

Codex can use this repo in two ways:

- plugin install via a personal or team marketplace
- skill install via `npx skills` plus MCP config

## Personal Marketplace Path

```bash
mkdir -p ~/plugins ~/.agents/plugins
git clone git@github.com:kong/skills.git ~/plugins/kong-skills
cat > ~/.agents/plugins/marketplace.json <<'EOF'
{
  "name": "personal-marketplace",
  "interface": {
    "displayName": "Personal Marketplace"
  },
  "plugins": [
    {
      "name": "kong-skills",
      "source": {
        "source": "local",
        "path": "./plugins/kong-skills"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
EOF
```

Then install `kong-skills` from your personal marketplace in Codex.

## Skill-Only Path

```bash
npx skills add kong/skills
```

If you only use the skill-only path, you do not need `KONNECT_TOKEN`.

If you also want the `kong-konnect` MCP server, add the MCP config from [`.mcp.json`](../../.mcp.json). That is when `KONNECT_TOKEN` is required.
