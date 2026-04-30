#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
TRIGGER_FIXTURES_DIR = REPO_ROOT / "tests" / "trigger-fixtures"


def normalize_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9-]+", "-", value.strip().lower()).strip("-")
    if not normalized:
        raise ValueError("skill name must contain at least one lowercase letter or digit")
    return normalized


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def ensure_missing(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"{path.relative_to(REPO_ROOT)} already exists")


def skill_template(skill_name: str) -> str:
    title = skill_name.replace("-", " ")
    return textwrap.dedent(
        f"""\
        ---
        name: {skill_name}
        description: One-line description used for discovery and matching. Replace this with a routing-sensitive summary.
        metadata:
          product: kong
          category: workflow
          tags:
            - kong
            - {skill_name}
        ---

        # {title}

        ## When To Use

        Use this skill when:

        - replace this bullet with the request pattern that should trigger the skill
        - keep the trigger scope Kong-specific and operational

        ## Workflow

        1. Identify the Kong-specific goal, system, or resource involved.
        2. Prefer the source-of-truth artifacts and commands for this workflow.
        3. Call out the key edge cases, failure modes, and validation checks.
        4. Return a concise result with concrete next steps.

        ## Guardrails

        - Replace this section with the real do/do-not guidance for the workflow.
        - Remove generic filler before committing the skill.
        """
    )


def trigger_fixture_template(skill_name: str) -> str:
    return textwrap.dedent(
        f"""\
        skill: {skill_name}
        positive_prompts:
          - Replace this with a prompt that should clearly trigger the {skill_name} skill.
          - Add a second routing-sensitive prompt for {skill_name}.
        negative_prompts:
          - Replace this with a prompt that should clearly not trigger the {skill_name} skill.
          - Add a second prompt that belongs to some other Kong workflow.
        notes: Replace this with a short note explaining what routing boundary these prompts are testing.
        """
    )


def scaffold_skill(args: argparse.Namespace) -> int:
    skill_name = normalize_name(args.name)
    skill_dir = SKILLS_DIR / skill_name
    skill_md = skill_dir / "SKILL.md"
    fixture_path = TRIGGER_FIXTURES_DIR / f"{skill_name}.yaml"
    ensure_missing(skill_dir)
    ensure_missing(fixture_path)
    write_text(skill_md, skill_template(skill_name))
    write_text(fixture_path, trigger_fixture_template(skill_name))
    print(skill_md.relative_to(REPO_ROOT))
    print(fixture_path.relative_to(REPO_ROOT))
    return 0


def scaffold_trigger(args: argparse.Namespace) -> int:
    skill_name = normalize_name(args.name)
    fixture_path = TRIGGER_FIXTURES_DIR / f"{skill_name}.yaml"
    ensure_missing(fixture_path)
    write_text(fixture_path, trigger_fixture_template(skill_name))
    print(fixture_path.relative_to(REPO_ROOT))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold Kong skill files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    skill_parser = subparsers.add_parser(
        "skill",
        help="Create a new skill directory plus its trigger fixture boilerplate.",
    )
    skill_parser.add_argument("name", help="Skill name. This becomes the directory name and frontmatter name.")
    skill_parser.set_defaults(handler=scaffold_skill)

    trigger_parser = subparsers.add_parser("trigger", help="Create a trigger fixture boilerplate for a skill.")
    trigger_parser.add_argument("name", help="Skill name for the trigger fixture filename and skill field.")
    trigger_parser.set_defaults(handler=scaffold_trigger)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except (FileExistsError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
