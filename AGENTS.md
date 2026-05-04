# Skill Authoring Guide

This repo is for high-signal Kong skills. If you are using an LLM to add a new skill here, the main job is not to create more text. The job is to create a skill that helps an agent do Kong-specific work better than general model knowledge already would.

If your host environment exposes a built-in skill-authoring helper or skill such as `skill-creator`, `build-a-skill`, or similar, consult it before drafting or revising a skill. Use it to improve structure and calibration, then apply this repo's Kong-specific rules as the final authority. If the helper conflicts with this file, follow this file.

## What Belongs Here

A skill in this repo should do at least one of these well:

- encode Kong-specific workflows that are easy to get wrong without guidance
- capture product or platform conventions that are not obvious from generic reasoning
- turn a broad request into a repeatable operating procedure
- point agents toward the right artifacts, constraints, or failure modes

Good examples:

- designing or debugging DataKit flows
- working with Konnect concepts, APIs, or configuration patterns
- handling Kong-specific deployment, gateway, plugin, or control-plane workflows

Weak examples:

- generic web research
- generic coding advice
- generic debugging advice that is not Kong-specific

If the skill would be equally useful in any repo, it probably does not belong here.

## What A Good Skill Does

A strong skill is narrow, operational, and reusable.

It should:

- trigger on a clear class of user requests
- reduce ambiguity about how to approach the task
- give the agent a reliable workflow, not just background information
- highlight key constraints, edge cases, and common mistakes
- help the agent produce better outputs with less guesswork

It should not:

- try to document an entire product surface
- read like marketing copy
- duplicate large amounts of reference material inline
- prescribe steps that are too vague to change model behavior

## Scope Before Writing

Before drafting the skill, decide:

- what user requests should activate it
- what the agent should actually do once it activates
- what Kong-specific knowledge is essential
- what should remain outside the skill because it is generic or unstable

Prefer one clearly-scoped skill over one large umbrella skill.

If you find yourself writing "this skill can also help with..." many times, the scope is probably too broad.

Also decide whether the task should become a skill at all. Prefer a skill when:

- you keep repeating the same playbook, checklist, or multi-step procedure
- the useful part is procedural, not just factual
- the agent needs Kong-specific defaults, gotchas, or validation steps

Do not create a skill just to restate generic best practices.

## Source Material First

Start from real Kong-specific source material whenever possible, not only from generic model knowledge.

Prefer inputs such as:

- existing runbooks, design docs, and internal conventions
- API specs, config files, and checked-in examples
- issue history, review comments, and bug fixes
- real failure cases and the steps that resolved them

The strongest skills are extracted from real execution traces, corrections, and repeated review feedback.

## How To Structure The Skill

Each skill should start with frontmatter:

```md
---
name: skill-name
description: One-line description used for discovery and matching.
license: MIT
metadata:
  product: product-name
  category: workflow-category
  tags:
    - kong
    - example-tag
---
```

Use these fields consistently in this repo:

- `name`
- `description`
- `license`
- `metadata.product`
- `metadata.category`
- `metadata.tags`

Set `license` to `MIT` unless the skill is intentionally shipped under different terms and that exception has been reviewed.

Optional companion directories are allowed when they support the skill:

- `references/` for supporting reference material
- `assets/` for lightweight images or other bundled assets
- `scripts/` for helper scripts an agent may inspect or run explicitly

This repo does not currently allow per-skill MCP dependency declarations such as `agents/openai.yaml`. For v1, keep MCP configuration shared at the repo level and keep skills portable.

Keep the package shape simple:

- keep `SKILL.md` as the only file at the skill root
- do not add hidden files or directories
- do not add symlinks
- do not add executable files
- keep companion files lightweight and reviewable

After that, write for agent behavior, not human browsing.

Keep `SKILL.md` tight. As a rule of thumb, keep the main file under roughly 500 lines and move bulk reference material into companion files.

Useful sections usually look like:

- when to use this skill
- how to approach the task
- what to prefer or avoid
- what to validate before answering
- how to present the result

Not every skill needs the same headings, but every skill should make those concerns clear.

## Writing Style

Use direct instructions.

Prefer:

- "Use this skill when..."
- "First identify..."
- "Prefer..."
- "Do not..."
- "If X is unclear, ask or verify..."

Avoid:

- long product overviews
- unnecessary historical context
- aspirational language
- repeating the same idea in multiple forms

The skill should change agent behavior quickly. Dense, generic prose weakens that.

Prefer concrete defaults over menus. If several tools or approaches could work, tell the agent which one to use by default and mention alternatives only as escape hatches.

Prefer reusable procedures over one-off answers. Teach the agent how to approach a class of Kong problems, not just the output for one example.

## Focus On Workflow, Not Reference Dumps

A skill is most useful when it tells the agent how to proceed.

For example, instead of only listing concepts, tell the agent:

- what order to inspect things in
- which artifacts matter most
- what common failure modes to check first
- what output shape is expected

Reference material is useful, but it should support the workflow, not replace it.

If large reference content is needed, keep it in companion files under the skill directory and let the skill point to them selectively.

When you point to a companion file, tell the agent exactly when to load it. Prefer:

- "Load `references/troubleshooting.md` if the request is about auth or region errors."
- "Load `references/commands.md` when you need exact command syntax."

Avoid vague directions like "see references for more."

## Encode Judgment

The best skills carry judgment, not just facts.

Include guidance like:

- when to choose one Kong approach over another
- what tradeoffs matter
- which sources of truth are more reliable
- which mistakes are common in real usage

This is often the difference between a skill that is merely informative and a skill that is operationally valuable.

Make sure the skill captures the Kong-specific corrections an agent would not infer on its own. These often belong in short "gotchas", "prefer", or "do not" sections.

## Prefer Stable Guidance

Skills should avoid depending on details that change often unless the change is the point of the skill.

Prefer:

- patterns
- workflows
- naming and configuration conventions
- common debugging sequences

Be careful with:

- volatile version-specific claims
- UI click paths
- fast-changing product matrices

If a detail is likely to drift, either omit it, frame it as version-specific, or place it in a reference file that can be updated cleanly.

Prefer stable operating patterns in `SKILL.md` and push volatile details into references.

## Progressive Disclosure

Use the skill root for the always-needed instructions and companion files for conditional detail.

- Keep activation-critical instructions in `SKILL.md`
- Put bulky examples, command references, and troubleshooting detail in `references/`
- Put templates or structured output examples in `assets/` when they are only needed for certain tasks
- Put helper code in `scripts/` only when running it is materially better than restating the logic inline

Only include a companion file if the main skill tells the agent when and why to load it.

## Instruction Patterns

Useful patterns for this repo include:

- short gotchas sections for non-obvious Kong constraints
- checklists for multi-step workflows
- validation loops that tell the agent what to verify before answering
- output templates when response shape matters

Prefer one clear default path with validation over a long menu of possibilities.

## Fit The Skill To This Repo

This repo already has shared installation wrappers for multiple harnesses. The skill itself should stay portable.

That means:

- put reusable behavior in `SKILL.md`
- keep harness-specific packaging out of the skill body
- avoid writing the skill as if it belongs only to one client

The repo tooling will sync the shared skill inventory into the relevant plugin manifests and generated documentation.

Treat this repo as the contributor-facing source package, not the end-user product surface.

- keep reusable skill behavior in `skills/`
- keep checked-in install metadata and context files aligned with the skills that actually ship
- prefer pointing docs at checked-in reference files over duplicating large inline config snippets that can drift

If you touch harness-specific context files such as `GEMINI.md` or install snippets under `docs/install/`, verify that they only mention current skills and current checked-in config shapes.

## Quality Bar For Submission

Before considering the skill done, check:

- is the scope clear
- is the trigger condition obvious
- does the skill prescribe a real workflow
- does it contain Kong-specific value
- does it avoid generic filler
- does the description make activation likely for the right requests and unlikely for the wrong ones
- does the skill choose defaults clearly instead of presenting equal-option menus
- does it tell the agent what to validate before answering
- were all scaffold placeholders replaced with real content
- would an agent using this skill likely perform better than without it

If the answer to the last question is not clearly yes, the skill probably needs to be narrowed or rewritten.

## Practical Authoring Heuristics

- Prefer concrete verbs over abstract nouns.
- Prefer decision rules over encyclopedic explanation.
- Prefer a few strong constraints over many soft suggestions.
- Prefer examples when they clarify a pattern, not when they just restate the rule.
- Prefer companion reference files when the main skill starts becoming long and hard to follow.

## Working In This Repo

When you add or substantially change a skill, keep the authoring loop simple:

1. write or revise the skill
2. sync the generated repo metadata
3. run validation

If you have access to a skill-authoring helper in your host tool, use it before step 1 or during revision, then review the result against this file before committing.

The exact commands and file map are documented elsewhere in this repo. This file is intentionally focused on writing better skills, not on repeating procedural details.
