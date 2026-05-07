# Output Shaping

Use this file when the main problem is how to return read results cleanly.

## Core Rule

Prefer structured output for inspection, then summarize only the fields the
user actually needs.

## Defaults

- use JSON unless YAML is explicitly requested
- use explicit `-o json` or `-o yaml` to avoid profile/env surprises
- summarize IDs, names, states, timestamps, and the minimum fields needed to
  answer the question

## Decision Rules

- If the user wants machine-shaped results, preserve structure.
- If the user wants a concise explanation, summarize after inspection instead
  of switching to text-mode guessing.
- If the result is large, filter conceptually in the response even if the CLI
  output is structured and verbose.

## What To Return

Return:

- the output format used
- the key fields that answer the question
- any profile/env caveat that may have affected formatting
