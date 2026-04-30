# Trigger Harness

This repo includes a lightweight trigger harness for one question only:

- would the proxy host route a prompt to a skill at all

It does not test whether the real skill does useful work after it triggers.

## Why Codex

The skill format is shared across modern agent harnesses, but host integration and observability differ.

This harness uses Codex because it offers a non-interactive `codex exec` path plus an isolated skills home via `CODEX_HOME/skills`.

## How It Works

Each real skill has a fixture file under [`tests/trigger-fixtures`](../tests/trigger-fixtures).

A fixture defines:

- the skill name
- positive prompts that should trigger the skill
- negative prompts that should not trigger the skill

`mise run skill:new -- your-skill-name` already creates the matching trigger fixture.

If you need to scaffold or recreate only the fixture, use:

```bash
mise run trigger:new -- your-skill-name
```

At runtime the harness does not load the full shipped skill body. It generates a synthetic mini-skill with:

- the real skill frontmatter from `skills/<name>/SKILL.md`
- a tiny body that replies with a deterministic marker if the skill is used

The base probe prompt tells Codex to reply with `NO_SKILL` when no skill applies. That gives a cheap routing signal:

- positive case output matches the marker: triggered
- negative case output is `NO_SKILL`: not triggered
- anything else: indeterminate

Codex may also return the selected skill identifier directly, such as `datakit` or `kong-skills:datakit`. The harness normalizes those forms as `triggered` for the matching skill.

## Commands

List trigger fixtures:

```bash
mise run trigger:list
```

Run all trigger fixtures with Codex:

```bash
mise run trigger:test
```

Run faster with bounded parallelism:

```bash
mise run trigger:test -- --jobs 3
```

Run one skill only:

```bash
mise run trigger:test -- --skill datakit
```

Build the runtime plan without calling Codex:

```bash
mise run trigger:test -- --dry-run
```

Keep the generated temporary runtime for debugging:

```bash
mise run trigger:test -- --keep-temp
```

Show more frequent live heartbeats while a case is in flight:

```bash
mise run trigger:test -- --progress-interval-seconds 5
```

## Auth And Isolation

The harness creates a temporary `CODEX_HOME` under `.tmp/trigger-harness/` and copies only the Codex auth files it needs from the current `CODEX_HOME` or `~/.codex`.

It does not reuse the real user skill directory.

Temporary runtime directories are deleted automatically after each case unless you pass `--keep-temp`.

If you prefer API-key auth, set `OPENAI_API_KEY` before running the harness.

The Python dependency for this harness is managed through `uv`. Run `mise run deps` once to sync `PyYAML` and the rest of the repo's Python dependencies.

Live progress reports are written to `stderr`, so they remain visible even when `--json` is used for machine-readable results on `stdout`.

## Limits

- This is a routing proxy, not proof of cross-host behavior.
- This is not a semantic quality test for the real skill.
- Failures may indicate heuristic drift in the host, not necessarily a broken skill.
- Network and auth are still required for live Codex runs.
- Cases run with bounded parallelism. Use `--jobs` to control concurrency and trade off wall-clock time against concurrent Codex calls.
- `--dry-run` validates the planned probe matrix and command shape only. It does not report routing pass/fail results.
