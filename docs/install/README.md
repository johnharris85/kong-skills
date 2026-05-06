# Installation

Choose the install path that matches the tool you use.

These pages document the generated install surfaces that this source repo maintains. Most users will follow one tool-specific page and will not need any contributor context from the rest of the repository.

[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-111111?style=for-the-badge&logo=anthropic&logoColor=white)](./claude-code.md)
[![Codex](https://img.shields.io/badge/Codex-plugin-0A0A0A?style=for-the-badge&logo=openai&logoColor=white)](./codex.md)
[![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-extension-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)](./gemini-cli.md)
[![Cursor](https://img.shields.io/badge/Cursor-mcp-222222?style=for-the-badge&logo=cursor&logoColor=white)](./cursor.md)
[![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-mcp-24292F?style=for-the-badge&logo=githubcopilot&logoColor=white)](./github-copilot.md)
[![Other Tools](https://img.shields.io/badge/Other_Tools-skills-555555?style=for-the-badge&logo=vercel&logoColor=white)](./other-tools.md)

All routes use the same MCP server:

- name: `kong-konnect`
- URL: `https://us.mcp.konghq.com`
- auth: `Authorization: Bearer ${KONNECT_TOKEN}`

`KONNECT_TOKEN` is only required for MCP-backed installs. If you only install the shared skills with `npx skills` or `gh skill`, you do not need the token.

For skill-only installs from GitHub, prefer previewing before install:

```bash
gh skill preview kong/skills gateway-plugin-datakit
```
