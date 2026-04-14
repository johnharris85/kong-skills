# Goose

Goose supports installing MCP servers as extensions, including remote Streamable HTTP extensions.

## Interactive Install

Run:

```bash
goose configure
```

Then choose:

1. `Add Extension`
2. `Remote Extension (Streamable HTTP)`
3. Name: `kong-konnect`
4. URL: `https://us.mcp.konghq.com`

If your Goose build exposes header or auth fields for remote extensions, set:

```text
Authorization: Bearer ${KONNECT_TOKEN}
```

## Session-Only Usage

To enable the remote extension for a single session:

```bash
goose session --with-streamable-http-extension "https://us.mcp.konghq.com"
```

## Sample Config Reference

See [config.yaml](/home/john/projects/kong-skills/goose/config.yaml) for a documented sample shape you can adapt in your Goose config.

## Skills

Install the shared skills separately:

```bash
npx skills add johnharris85/kong-skills
```

That currently installs the `datakit` skill from this repo.
