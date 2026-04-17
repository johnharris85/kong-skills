# Kong Skills

Portable Kong skills plus `kong-konnect` MCP configuration for AI coding harnesses.

## Getting Started

- Installation docs: [docs/install/README.md](docs/install/README.md)
- Available skills: [docs/skills.md](docs/skills.md)
- Developer guide: [docs/developer.md](docs/developer.md)
- Repo structure: [docs/structure.md](docs/structure.md)

## Install Targets

[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-111111?style=for-the-badge&logo=anthropic&logoColor=white)](docs/install/claude-code.md)
[![Codex](https://img.shields.io/badge/Codex-plugin-0A0A0A?style=for-the-badge&logo=openai&logoColor=white)](docs/install/codex.md)
[![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-extension-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)](docs/install/gemini-cli.md)
[![Cursor](https://img.shields.io/badge/Cursor-mcp-222222?style=for-the-badge&logo=cursor&logoColor=white)](docs/install/cursor.md)
[![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-mcp-24292F?style=for-the-badge&logo=githubcopilot&logoColor=white)](docs/install/github-copilot.md)
[![Goose](https://img.shields.io/badge/Goose-extension-2E6F40?style=for-the-badge&label=%F0%9F%AA%BF%20Goose)](docs/install/goose.md)
[![Other Tools](https://img.shields.io/badge/Other_Tools-skills-555555?style=for-the-badge&logo=vercel&logoColor=white)](docs/install/other-tools.md)

## Authentication

All install surfaces use the same bearer token model:

```text
Authorization: Bearer ${KONNECT_TOKEN}
```

`KONNECT_TOKEN` is only needed when you install or use the `kong-konnect` MCP server. A skill-only install via `npx skills` does not require it.

Claude Code uses [claude.mcp.json](claude.mcp.json) as its MCP reference shape. Codex-compatible tools use [`.mcp.json`](.mcp.json).
