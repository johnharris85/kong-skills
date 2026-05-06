---
name: kong-skill-authoring
description: Create or revise skills for this Kong skills repo. Use when adding a skill, deciding extend-versus-create, classifying domain versus tool skills, tightening trigger descriptions, or structuring Kong-specific authoring guidance for this repo.
license: MIT
metadata:
  product: repo
  category: skill-authoring
  tags:
    - kong
    - skills
    - authoring
    - konnect
    - workflow
---

# Kong skill authoring

## Goal

Help contributors create or revise high-signal skills for this repository
without creating overlap, generic filler, or tool-boundary confusion.

Use this skill to drive the authoring process progressively. Keep repo policy in
`AGENTS.md` as the source of truth, but use this skill to decide what to build,
how to scope it, and how to structure the resulting skill.

## First Principles

- Treat `AGENTS.md` as the canonical repo policy.
- Use this skill for authoring workflow and decision-making, not as a
  replacement for repo rules.
- Prefer extending an existing skill over creating a near-duplicate.
- Prefer narrow operational skills over broad informational umbrellas.
- Preserve the repo's layered model:
  - domain skills own Kong-specific diagnosis, workflow, and judgment
  - tool skills own `decK`, `kongctl`, or Terraform config authoring and
    execution

## Authoring Workflow

### 1. Check for overlap first

Before creating a new skill:

- inspect `docs/skills.md`
- inspect `skills/`
- look for an existing skill with the same trigger class, same layer, or same
  operator workflow

Default decision:

- extend an existing skill if the new request fits the same trigger surface and
  operating procedure
- create a new skill only if the boundary is materially different

Call out overlap plainly. Do not create a second skill with only naming or
wording differences.

### 2. Classify the skill boundary

Decide which kind of skill this is:

- domain skill: product surface, troubleshooting flow, operator workflow,
  publication flow, observability flow, access flow, Event Gateway flow
- tool skill: `decK`, `kongctl`, Terraform, import/adopt/plan/apply workflow,
  HCL/YAML/file-shape ownership
- existing-skill revision: same trigger class, same workflow, same owner

Decision rule:

- if the main difference is diagnosis order or product reasoning, use a domain
  skill
- if the main difference is file format, plan/apply behavior, or config tool,
  use a tool skill
- if both apply, keep diagnosis in the domain skill and hand off
  implementation to the tool skill

### 3. Define the trigger surface

Write down:

- what a user would actually ask
- what terms should activate the skill
- which nearby requests should not activate it
- whether the request is Konnect-specific, Gateway-specific, or generic enough
  to stay out of this repo

Treat the `description` field as the primary trigger surface. Write it so an
agent can decide to use the skill without reading the full body first.

Description defaults:

- front-load the key trigger words and main boundary
- keep most descriptions under roughly 260 characters
- prefer concise trigger phrases over long lists of examples
- if another skill already sounds similar, tighten the boundary before adding
  more wording

### 4. Decide what belongs in the skill body

Keep only always-needed operational guidance in `SKILL.md`:

- inspection order
- decision rules
- defaults and constraints
- common mistakes
- validation checklist
- handoffs to neighboring skills

Move conditional bulk detail out of the root body:

- `references/` for large command references, schemas, or troubleshooting
- `scripts/` only when a checked-in helper is materially better than inline
  logic
- `assets/` only when the skill needs output-side templates or lightweight
  bundled files

### 5. Make tool and MCP boundaries explicit

For Konnect-oriented skills:

- prefer the shared `kong-konnect` MCP server for live inspection when
  available
- do not make MCP a hard dependency for the skill to remain useful
- preserve fallback paths through `kongctl`, declarative config, logs, or
  user-provided artifacts

For domain skills:

- keep tool guidance short
- state which tool skills should take over when config changes are needed
- preserve the user's existing toolchain

For tool skills:

- state which Kong product or resource surface they cover
- state which neighboring tools they do not replace
- preserve the repository's current toolchain instead of forcing migration

### 6. Write the smallest skill that changes behavior

Prefer:

- direct instructions
- short checklists
- explicit defaults
- narrow gotchas
- validation loops

Avoid:

- long product summaries
- generic best practices
- repeated policy text that already lives in `AGENTS.md`
- bloated examples that do not change agent behavior

## Output Shape

When creating or revising a skill, produce:

1. a clear decision: extend existing skill, create new domain skill, or create
   new tool skill
2. the proposed skill name
3. the exact trigger surface for the `description`
4. the minimum sections the `SKILL.md` body needs
5. any justified companion files
6. the repo validation steps to run afterward

If the task does not justify a new skill, say so and propose the narrow update
to the existing skill instead.

## Validation Checklist

Before finishing authoring work, verify:

- there is no existing skill that should have been extended instead
- the skill boundary is clearly domain, tool, or existing-skill revision
- the `description` is activation-grade, not just a label
- the `description` stays within the repo's budget and front-loads trigger
  words
- the body gives a real Kong-specific workflow
- the skill preserves MCP and toolchain boundaries correctly
- the skill avoids generic filler
- companion files are justified
- the new or revised skill does not overlap too heavily with another skill's
  trigger surface
- the repo loop is complete: update the skill, run `mise run sync`, run
  `mise run check`

## Handoffs

- Use the host environment's built-in generic skill-authoring helper first when
  it materially improves structure, then apply this repo's `AGENTS.md` rules as
  the final authority.
- Use domain or tool skills in `skills/` as examples of good boundaries, not as
  templates to copy blindly.
