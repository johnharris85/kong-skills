---
name: web-search
description: Search the web with Exa MCP, read the best matching pages, and answer with source URLs.
---

# Instructions

Use this skill when the user needs current web research, source gathering, or URL-backed factual answers.

## When To Use Exa

Use Exa when:

- the task depends on current or external web content
- the user asks for sources, links, or citations
- you need to discover relevant pages before reading them

Avoid relying on a single result when the topic is ambiguous, contested, or high stakes.

## Workflow

1. Translate the user's question into 1 to 3 focused search queries.
2. Use the Exa `search` tool to find relevant pages.
3. Prefer strong primary sources, official documentation, company announcements, or reputable publications.
4. Use `get_contents` on the most relevant results before answering.
5. Cross-check important claims across more than one source when accuracy matters.
6. Answer with concise findings and include source URLs.

## Query Construction

Build queries that combine:

- the exact entity, product, or topic name
- the specific fact you need
- a narrowing term like `docs`, `pricing`, `announcement`, `policy`, or a date when useful

Examples:

- `openai responses api docs tools`
- `exa mcp streamable http authentication`
- `company name earnings q1 2026`

If the first search is too broad, tighten it with exact names, dates, site constraints, or official-source language.

## Source Handling

- Read before citing.
- Prefer recent pages for time-sensitive topics.
- Call out uncertainty when sources conflict or coverage is incomplete.
- Link to the specific pages you used.

## Output

Default to:

- short answer
- key supporting points
- source list with URLs
