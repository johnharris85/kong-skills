# Goose

![Goose](https://img.shields.io/badge/Goose-extension-2E6F40?style=for-the-badge&label=%F0%9F%AA%BF%20Goose)

Goose supports MCP-based extensions, including remote Streamable HTTP.

## Interactive Install

```bash
goose configure
```

Then choose:

1. `Add Extension`
2. `Remote Extension (Streamable HTTP)`
3. Name: `kong-konnect`
4. URL: `https://us.mcp.konghq.com`

If Goose exposes header or auth fields for the extension, use:

```text
Authorization: Bearer ${KONNECT_TOKEN}
```

## Session-Only Usage

```bash
goose session --with-streamable-http-extension "https://us.mcp.konghq.com"
```

## Skills

```bash
npx skills add johnharris85/kong-skills
```

`KONNECT_TOKEN` is only needed when the Goose `kong-konnect` MCP extension is enabled.

## Reference Config

- [goose/config.yaml](../../goose/config.yaml)
