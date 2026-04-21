# Other Tools

![Other Tools](https://img.shields.io/badge/Other_Tools-skills-555555?style=for-the-badge&logo=vercel&logoColor=white)

For tools without a first-class plugin or extension wrapper in this repo, use the shared skills plus the MCP config.

## Skills

`npx skills` and `gh skill` are both supported install paths for the shared skills in this repo.

### `npx skills`

```bash
npx skills add kong/skills
```

### `gh skill`

`gh skill` is available in GitHub CLI v2.90.0+ and is currently in public preview.

```bash
gh skill install kong/skills
```

If you want to install the single skill in this repo directly, use:

```bash
gh skill install kong/skills datakit
```

If `gh skill` does not pick the right host automatically, pass `--agent`.

These skill-only installs do not require `KONNECT_TOKEN`.

## MCP Config Reference

Use one of these as the source of truth for the `kong-konnect` MCP server:

- [`.mcp.json`](../../.mcp.json)
- [cursor/mcp.json](../../cursor/mcp.json)
- [`gemini-extension.json`](../../gemini-extension.json)

`KONNECT_TOKEN` is only required if you add and use the MCP server.
