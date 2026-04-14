# Installation

Choose the install path that matches the tool you use.

[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-111111?style=for-the-badge&logo=anthropic&logoColor=white)](/home/john/projects/kong-skills/docs/install/claude-code.md)
[![Codex](https://img.shields.io/badge/Codex-plugin-0A0A0A?style=for-the-badge&logo=openai&logoColor=white)](/home/john/projects/kong-skills/docs/install/codex.md)
[![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-extension-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)](/home/john/projects/kong-skills/docs/install/gemini-cli.md)
[![Cursor](https://img.shields.io/badge/Cursor-mcp-222222?style=for-the-badge&logo=cursor&logoColor=white)](/home/john/projects/kong-skills/docs/install/cursor.md)
[![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-mcp-24292F?style=for-the-badge&logo=githubcopilot&logoColor=white)](/home/john/projects/kong-skills/docs/install/github-copilot.md)
[![Goose](https://img.shields.io/badge/Goose-extension-2E6F40?style=for-the-badge&label=%F0%9F%AA%BF%20Goose)](/home/john/projects/kong-skills/docs/install/goose.md)
[![Other Tools](https://img.shields.io/badge/Other_Tools-skills-555555?style=for-the-badge&logo=vercel&logoColor=white)](/home/john/projects/kong-skills/docs/install/other-tools.md)

All routes use the same MCP server:

- name: `kong-konnect`
- URL: `https://us.mcp.konghq.com`
- auth: `Authorization: Bearer ${KONNECT_TOKEN}`

`KONNECT_TOKEN` is only required for MCP-backed installs. If you only install the shared skills with `npx skills`, you do not need the token.
