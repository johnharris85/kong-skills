---
name: research-assistant
description: Run a structured research workflow with the Kong-hosted MCP endpoint, cross-check claims, and synthesize cited findings.
---

# Instructions

Use this skill for deeper research tasks where the user wants analysis, comparison, or a compact briefing rather than a single fact lookup.

## When To Use This Skill

Use it when the user asks for:

- research
- a deep dive
- competitor or market analysis
- comparison across sources
- synthesis of a topic with citations

## Research Workflow

1. Clarify the research question, constraints, and desired output.
2. Break the question into subtopics or claims to verify.
3. Use MCP `search` to identify strong sources for each subtopic.
4. Use MCP `get_contents` to read the best sources, not just headlines or snippets.
5. Compare sources and note agreement, disagreement, and missing evidence.
6. Synthesize the findings into a structured response with citations.

## Evaluating Sources

- Prefer primary sources first.
- Use secondary sources to add context or independent confirmation.
- Treat marketing pages, summaries, and opinion pieces as lower-confidence evidence.
- For conflicting claims, state which source is stronger and why.

## Handling Conflicts

When sources disagree:

- do not flatten the disagreement into a false certainty
- identify the contested claim explicitly
- favor the source with better proximity, evidence, or recency
- tell the user what remains uncertain

## Output Format

Structure the answer with:

- brief conclusion
- key findings
- notable uncertainties or conflicts
- sources with URLs

If the user asks for recommendations, separate evidence from judgment.
