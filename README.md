# Exa Research Agent Template

Template repository for distributing portable `SKILL.md` workflows plus remote MCP configuration across Claude Code, Codex, Gemini CLI, Cursor, and any agent that supports `npx skills`.

It uses Exa's remote MCP endpoint, `https://mcp.exa.ai/mcp`, as the example web research backend.

## Quick Start

### Claude Code

Add this repo as a plugin marketplace, then install the plugin:

```bash
/plugin marketplace add yourorg/exa-research-agent-template
/plugin install exa-research-agent-template@exa-research-agent-template
```

### Codex

Install from a repo marketplace, or copy the plugin into your local plugins directory. The shared skills can also be installed directly:

```bash
npx skills add yourorg/exa-research-agent-template
```

### Gemini CLI

Install the extension from GitHub:

```bash
gemini extensions install https://github.com/yourorg/exa-research-agent-template
```

### Cursor

Copy [cursor/mcp.json](/home/john/projects/kong-skills/cursor/mcp.json) into `.cursor/mcp.json`, then install the skills:

```bash
npx skills add yourorg/exa-research-agent-template
```

### Any Other Agent

Install the shared skills:

```bash
npx skills add yourorg/exa-research-agent-template
```

Then add the Exa MCP server using that agent's native MCP configuration format and the same endpoint URL used in this template.

## Installation

### Claude Code

This repo includes:

- [`.claude-plugin/plugin.json`](/home/john/projects/kong-skills/.claude-plugin/plugin.json)
- [`marketplace.json`](/home/john/projects/kong-skills/marketplace.json)

Typical flow:

```bash
/plugin marketplace add yourorg/exa-research-agent-template
/plugin install exa-research-agent-template@exa-research-agent-template
```

The plugin installs both shared skills and the Exa MCP server entry.

### Codex

This repo includes:

- [`.codex-plugin/plugin.json`](/home/john/projects/kong-skills/.codex-plugin/plugin.json)
- [`.mcp.json`](/home/john/projects/kong-skills/.mcp.json)
- [`.agents/plugins/marketplace.json`](/home/john/projects/kong-skills/.agents/plugins/marketplace.json)

For skill-only installs:

```bash
npx skills add yourorg/exa-research-agent-template
```

For plugin-based installs, publish or copy this repo into a Codex plugin marketplace and keep `.mcp.json` at the plugin root.

### Gemini CLI

This repo includes:

- [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json)
- [`GEMINI.md`](/home/john/projects/kong-skills/GEMINI.md)

Install:

```bash
gemini extensions install https://github.com/yourorg/exa-research-agent-template
```

### Cursor

Cursor does not currently have a self-serve plugin manifest for this use case. Use:

- [cursor/mcp.json](/home/john/projects/kong-skills/cursor/mcp.json) as the drop-in MCP snippet
- `npx skills add yourorg/exa-research-agent-template` for shared skills

Example:

```bash
mkdir -p .cursor
cp cursor/mcp.json .cursor/mcp.json
npx skills add yourorg/exa-research-agent-template
```

## Available Skills

- `web-search`: Exa-backed search workflow for finding sources, reading pages, and citing URLs.
- `research-assistant`: Multi-step research workflow for deeper analysis, source comparison, and synthesis.

## Configuration

This template intentionally does not include API keys.

Exa MCP authentication depends on the client platform. In practice, configure an Exa API key through the platform's normal secret or MCP auth flow and send it to `https://mcp.exa.ai/mcp`.

Common patterns:

- Claude Code: configure auth when installing or editing the MCP server entry.
- Codex: configure the MCP server in `.mcp.json` or marketplace install flow and provide credentials through the platform's MCP auth mechanism.
- Gemini CLI: add a secret during extension install using the `EXA_API_KEY` setting in [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json).
- Cursor and other agents: add the MCP server manually and provide the Exa token or header in that client's supported auth format.

If your target platform prefers environment variables, use `EXA_API_KEY`.

## Repo Layout

```text
.
├── skills/
│   ├── web-search/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   └── research-assistant/
│       └── SKILL.md
├── .claude-plugin/plugin.json
├── marketplace.json
├── .codex-plugin/plugin.json
├── .mcp.json
├── .agents/plugins/marketplace.json
├── gemini-extension.json
├── GEMINI.md
└── cursor/mcp.json
```

## Contributing

Fork the repo, replace the example branding with your own project name, update the shared skills under `skills/`, and swap the Exa MCP endpoint for your production MCP service if needed.

Keep the root `skills/` directory as the source of truth so every platform wrapper points at the same portable skill definitions.
