# Kong Skills

Portable Kong skills plus `kong-konnect` MCP configuration for Claude Code,
Codex, Cursor, and shared skill installers.

This repo is the contributor-facing source of truth for the packaged skills and
install metadata. End users normally consume these assets through plugin
catalogs, plugin bundles, or shared-skill installers rather than by reading
this repo directly.

## Getting Started

- Installation docs: [docs/install/README.md](docs/install/README.md)
- Available skills: [docs/skills.md](docs/skills.md)
- Developer guide: [docs/developer.md](docs/developer.md)
- Release process: [docs/release.md](docs/release.md)
- Testing guide: [docs/testing.md](docs/testing.md)
- Security policy: [SECURITY.md](SECURITY.md)
- Repo structure: [docs/structure.md](docs/structure.md)

## Contributor Prerequisites

For repo maintenance, install:

- `mise`: https://mise.jdx.dev/
- `git`
- `uv`: https://docs.astral.sh/uv/

Then bootstrap the repo:

```bash
mise trust
mise install
mise run preflight
mise run deps
```

`mise install` provisions the repo-managed Python toolchain from [mise.toml](mise.toml). `uv` remains an explicit prerequisite, and additional tools such as Docker, GitHub CLI, Node.js, or host-specific agent CLIs are only needed for the corresponding optional verification flows.

For release gating and recommended GitHub repository protections, see [docs/release.md](docs/release.md) and [SECURITY.md](SECURITY.md).

## Install Targets

[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-111111?style=for-the-badge&logo=anthropic&logoColor=white)](docs/install/claude-code.md)
[![Codex](https://img.shields.io/badge/Codex-plugin-0A0A0A?style=for-the-badge&logo=openai&logoColor=white)](docs/install/codex.md)
[![Cursor](https://img.shields.io/badge/Cursor-plugin-222222?style=for-the-badge&logo=cursor&logoColor=white)](docs/install/cursor.md)
[![Other Tools](https://img.shields.io/badge/Other_Tools-skills-555555?style=for-the-badge&logo=vercel&logoColor=white)](docs/install/other-tools.md)

## Authentication

All install surfaces use the same bearer token model:

```text
Authorization: Bearer ${KONNECT_TOKEN}
```

`KONNECT_TOKEN` is only needed when you install or use the `kong-konnect` MCP
server. A skill-only install via `npx skills` or `gh skill` does not require
it.

## Skill Install Notes

- Install the whole repo with `npx skills add kong/skills`.
- Install one skill with `npx skills add kong/skills --skill gateway-plugin-datakit`.
- Update one installed skill with `npx skills update -g -y gateway-plugin-datakit` or `gh skill update gateway-plugin-datakit`.
- Prefer native plugin update flows in Claude Code and Cursor over custom startup hooks.
- Be careful with any automatic update path: it can pull newer skill instructions automatically and may introduce supply-chain or security risk.
- For `gh skill`, preview before install with `gh skill preview kong/skills gateway-plugin-datakit`.

Use [`.mcp.json`](.mcp.json) as the shared checked-in reference shape for the
`kong-konnect` MCP server.
