# Kong Skills

Template repository for distributing portable `SKILL.md` workflows plus remote MCP configuration across Claude Code, Codex, Gemini CLI, Cursor, and other agents that support `npx skills`.

This repo now targets Kong's remote MCP endpoint, `https://us.mcp.konghq.com`, and includes bearer-token configuration examples using `KONG_API_KEY`.

## Quick Start

### Claude Code

```bash
/plugin marketplace add johnharris85/kong-skills
/plugin install kong-skills@kong-skills
```

### Codex

```bash
npx skills add johnharris85/kong-skills
```

### Gemini CLI

```bash
gemini extensions install https://github.com/johnharris85/kong-skills
```

### Cursor

```bash
mkdir -p .cursor
cp cursor/mcp.json .cursor/mcp.json
npx skills add johnharris85/kong-skills
```

### Any Other Agent

```bash
npx skills add johnharris85/kong-skills
```

Then add the same Kong MCP server from this repo into that agent's native MCP config.

## Installation

### Claude Code

Use [`.claude-plugin/plugin.json`](/home/john/projects/kong-skills/.claude-plugin/plugin.json) and [`marketplace.json`](/home/john/projects/kong-skills/marketplace.json):

```bash
/plugin marketplace add johnharris85/kong-skills
/plugin install kong-skills@kong-skills
```

### Codex

This repo includes [`.codex-plugin/plugin.json`](/home/john/projects/kong-skills/.codex-plugin/plugin.json), [`.mcp.json`](/home/john/projects/kong-skills/.mcp.json), and [`.agents/plugins/marketplace.json`](/home/john/projects/kong-skills/.agents/plugins/marketplace.json).

For skills only:

```bash
npx skills add johnharris85/kong-skills
```

### Gemini CLI

Use [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json) and [`GEMINI.md`](/home/john/projects/kong-skills/GEMINI.md):

```bash
gemini extensions install https://github.com/johnharris85/kong-skills
```

### Cursor

Use [cursor/mcp.json](/home/john/projects/kong-skills/cursor/mcp.json) as `.cursor/mcp.json`, then install the shared skills:

```bash
npx skills add johnharris85/kong-skills
```

## Available Skills

- `web-search`: Current web research workflow using the Kong-hosted MCP endpoint.
- `research-assistant`: Multi-step research and synthesis workflow with source checking.
- `datakit`: Kong DataKit design, YAML authoring, debugging, and reference guidance.

## Configuration

This repo does not include any live credentials.

Use `KONG_API_KEY` and send it as a bearer token:

```text
Authorization: Bearer ${KONG_API_KEY}
```

Repo configs that support explicit headers already include that pattern:

- [`.mcp.json`](/home/john/projects/kong-skills/.mcp.json)
- [cursor/mcp.json](/home/john/projects/kong-skills/cursor/mcp.json)
- [`.claude-plugin/plugin.json`](/home/john/projects/kong-skills/.claude-plugin/plugin.json)
- [`gemini-extension.json`](/home/john/projects/kong-skills/gemini-extension.json)

If a client does not honor header templating in its extension format, use the platform's normal secret or MCP auth flow and keep the same bearer-token shape.

## Repo Layout

```text
.
├── skills/
│   ├── web-search/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── research-assistant/
│   │   └── SKILL.md
│   └── datakit/
│       ├── SKILL.md
│       └── references/
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

Extend the shared skills under `skills/`, keep the platform wrappers pointing at those shared directories, and update the remote MCP endpoint or auth wiring only in the shared platform config files.
