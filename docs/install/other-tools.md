# Other Tools

![Other Tools](https://img.shields.io/badge/Other_Tools-skills-555555?style=for-the-badge&logo=vercel&logoColor=white)

For tools without a first-class plugin or extension wrapper in this repo, use the shared skills plus the MCP config.

## Skills

`npx skills` and `gh skill` are both supported install paths for the shared skills in this repo.

### `npx skills`

Install the whole repo:

```bash
npx skills add kong/skills
```

Install a single skill from this repo:

```bash
npx skills add kong/skills --skill datakit
```

Update all globally installed skills:

```bash
npx skills update -g -y
```

Update one installed skill:

```bash
npx skills update -g -y datakit
```

`--skill` applies to `npx skills add`. The `update` command takes skill names positionally.

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

Update all installed skills:

```bash
gh skill update --all
```

Update one installed skill:

```bash
gh skill update datakit
```

These skill-only installs do not require `KONNECT_TOKEN`.

## Auto-Update Caution

Be careful with startup auto-update hooks. They can pull newer skill instructions automatically at session start, which may introduce supply-chain or security risk if a skill changes upstream without review.

If you use auto-update, prefer updating one known skill first:

```bash
npx skills update -g -y datakit
```

Or with GitHub CLI:

```bash
gh skill update datakit
```

Claude Code and Gemini CLI both support startup hooks for this workflow. See their install pages for examples.

## MCP Config Reference

Use one of these as the source of truth for the `kong-konnect` MCP server:

- [`.mcp.json`](../../.mcp.json)
- [cursor-mcp.json](../../cursor-mcp.json)
- [`gemini-extension.json`](../../gemini-extension.json)

`KONNECT_TOKEN` is only required if you add and use the MCP server.
