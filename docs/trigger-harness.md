# Trigger Harness

This repo includes a lightweight trigger harness for one question only:

- would the proxy host route a prompt to a skill at all

It does not test whether the real skill does useful work after it triggers.

## Why One Proxy Host

The skill format is shared across modern agent harnesses, but host integration and observability differ.

This harness uses Codex as the proxy host because it offers:

- a non-interactive `codex exec` path
- JSON output for repeatable automation
- an isolated skills home via `CODEX_HOME/skills`

Claude remains a future comparison candidate, but Codex is the default routing proxy in this repo.

## How It Works

Each real skill has a fixture file under [`tests/trigger-fixtures`](../tests/trigger-fixtures).

A fixture defines:

- the skill name
- positive prompts that should trigger the skill
- negative prompts that should not trigger the skill

At runtime the harness does not load the full shipped skill body. It generates a synthetic mini-skill with:

- the real skill frontmatter from `skills/<name>/SKILL.md`
- a tiny body that replies with a deterministic marker if the skill is used

The base probe prompt tells Codex to reply with `NO_SKILL` when no skill applies. That gives a cheap routing signal:

- positive case output matches the marker: triggered
- negative case output is `NO_SKILL`: not triggered
- anything else: indeterminate

## Commands

Inspect the proxy-host decision and local CLI capabilities:

```bash
mise run trigger:spike
```

List trigger fixtures:

```bash
mise run trigger:list
```

Run all trigger fixtures with Codex:

```bash
mise run trigger:test
```

Run one skill only:

```bash
mise run trigger:test -- --skill datakit
```

Build the runtime plan without calling Codex:

```bash
mise run trigger:test -- --dry-run
```

## Auth And Isolation

The harness creates a temporary `CODEX_HOME` under `.tmp/trigger-harness/` and copies only the Codex auth files it needs from the current `CODEX_HOME` or `~/.codex`.

It does not reuse the real user skill directory.

If you prefer API-key auth, set `OPENAI_API_KEY` before running the harness.

## Limits

- This is a routing proxy, not proof of cross-host behavior.
- This is not a semantic quality test for the real skill.
- Failures may indicate heuristic drift in the host, not necessarily a broken skill.
- Network and auth are still required for live Codex runs.
