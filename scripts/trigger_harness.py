#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
FIXTURES_DIR = REPO_ROOT / "tests" / "trigger-fixtures"
RUNTIME_ROOT = REPO_ROOT / ".tmp" / "trigger-harness"
NO_SKILL_SENTINEL = "NO_SKILL"
DEFAULT_HARNESS = "codex"
AUTH_FILES = ("auth.json", "installation_id", "version.json")


@dataclass
class SkillMetadata:
    name: str
    description: str
    product: str
    category: str
    tags: list[str]


@dataclass
class TriggerFixture:
    skill: str
    positive_prompts: list[str]
    negative_prompts: list[str]
    notes: str | None = None


@dataclass
class ProbeCase:
    fixture: str
    kind: Literal["positive", "negative"]
    prompt: str
    expected: Literal["triggered", "not_triggered"]
    marker: str


@dataclass
class ProbeResult:
    fixture: str
    kind: str
    prompt: str
    expected: str
    actual: str
    passed: bool
    harness: str
    command: list[str]
    marker: str
    output: str
    returncode: int | None
    stderr_tail: str | None
    stdout_tail: str | None
    temp_root: str | None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict[str, object]:
    text = read_text(path)
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter start")

    try:
        _, rest = text.split("---\n", 1)
        raw_frontmatter, _ = rest.split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: malformed YAML frontmatter") from exc

    parsed = yaml.safe_load(raw_frontmatter)
    if not isinstance(parsed, dict):
        raise ValueError(f"{path}: frontmatter must be a YAML mapping")
    return parsed


def load_skill_metadata(skill_name: str) -> SkillMetadata:
    skill_md = SKILLS_DIR / skill_name / "SKILL.md"
    data = parse_frontmatter(skill_md)
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"{skill_md}: metadata block is required")
    return SkillMetadata(
        name=str(data["name"]).strip(),
        description=str(data["description"]).strip(),
        product=str(metadata["product"]).strip(),
        category=str(metadata["category"]).strip(),
        tags=[str(tag).strip() for tag in metadata["tags"]],
    )


def load_fixture(path: Path) -> TriggerFixture:
    data = yaml.safe_load(read_text(path))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: fixture must be a YAML mapping")

    skill = data.get("skill")
    positive = data.get("positive_prompts")
    negative = data.get("negative_prompts")
    notes = data.get("notes")

    if not isinstance(skill, str) or not skill.strip():
        raise ValueError(f"{path}: skill must be a non-empty string")
    if not isinstance(positive, list) or not positive or not all(isinstance(item, str) and item.strip() for item in positive):
        raise ValueError(f"{path}: positive_prompts must be a non-empty list of strings")
    if not isinstance(negative, list) or not negative or not all(isinstance(item, str) and item.strip() for item in negative):
        raise ValueError(f"{path}: negative_prompts must be a non-empty list of strings")
    if notes is not None and not isinstance(notes, str):
        raise ValueError(f"{path}: notes must be a string when present")

    return TriggerFixture(
        skill=skill.strip(),
        positive_prompts=[item.strip() for item in positive],
        negative_prompts=[item.strip() for item in negative],
        notes=notes.strip() if isinstance(notes, str) and notes.strip() else None,
    )


def load_fixtures(selected_skill: str | None = None) -> list[TriggerFixture]:
    fixtures: list[TriggerFixture] = []
    for path in sorted(FIXTURES_DIR.glob("*.yaml")):
        fixture = load_fixture(path)
        if selected_skill and fixture.skill != selected_skill:
            continue
        fixtures.append(fixture)

    if selected_skill and not fixtures:
        raise ValueError(f"no trigger fixture found for skill {selected_skill!r}")
    return fixtures


def marker_for_skill(skill_name: str) -> str:
    normalized = skill_name.upper().replace("-", "_")
    return f"TRIGGER::{normalized}"


def build_probe_cases(fixtures: list[TriggerFixture]) -> list[ProbeCase]:
    cases: list[ProbeCase] = []
    for fixture in fixtures:
        marker = marker_for_skill(fixture.skill)
        for prompt in fixture.positive_prompts:
            cases.append(
                ProbeCase(
                    fixture=fixture.skill,
                    kind="positive",
                    prompt=prompt,
                    expected="triggered",
                    marker=marker,
                )
            )
        for prompt in fixture.negative_prompts:
            cases.append(
                ProbeCase(
                    fixture=fixture.skill,
                    kind="negative",
                    prompt=prompt,
                    expected="not_triggered",
                    marker=marker,
                )
            )
    return cases


def mini_skill_text(skill: SkillMetadata, marker: str) -> str:
    frontmatter = {
        "name": skill.name,
        "description": skill.description,
        "metadata": {
            "product": skill.product,
            "category": skill.category,
            "tags": skill.tags,
        },
    }
    body = "---\n"
    body += yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
    body += "---\n\n"
    body += textwrap.dedent(
        f"""\
        # Trigger Probe

        If this skill is used for the current request, reply with exactly `{marker}`.
        Do not use tools.
        Do not add any other text.
        """
    )
    return body


def codex_probe_prompt(user_prompt: str) -> str:
    return textwrap.dedent(
        f"""\
        You are running a skill routing probe.
        If no installed skill specifically applies to the user's request, reply with exactly {NO_SKILL_SENTINEL}.
        Do not use tools.
        Do not explain your reasoning.

        User request:
        {user_prompt}
        """
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_codex_auth(dest_codex_home: Path) -> list[str]:
    source_codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    copied: list[str] = []

    if os.environ.get("OPENAI_API_KEY"):
        return copied

    if not source_codex_home.exists():
        raise RuntimeError(
            "no OPENAI_API_KEY is set and no Codex auth home was found; set OPENAI_API_KEY or sign in with codex first"
        )

    for name in AUTH_FILES:
        source = source_codex_home / name
        if source.exists():
            shutil.copy2(source, dest_codex_home / name)
            copied.append(name)

    if "auth.json" not in copied:
        raise RuntimeError(
            f"no OPENAI_API_KEY is set and {source_codex_home / 'auth.json'} was not found; sign in with codex first"
        )
    return copied


def build_codex_runtime(case: ProbeCase, skill: SkillMetadata, copy_auth: bool) -> tuple[Path, Path, Path]:
    ensure_dir(RUNTIME_ROOT)
    temp_root = Path(tempfile.mkdtemp(prefix=f"{case.fixture}-", dir=RUNTIME_ROOT))
    codex_home = temp_root / "codex-home"
    workspace = temp_root / "workspace"
    skill_dir = codex_home / "skills" / skill.name

    ensure_dir(skill_dir)
    ensure_dir(workspace)
    ensure_dir(codex_home)

    if copy_auth:
        copy_codex_auth(codex_home)
    (skill_dir / "SKILL.md").write_text(mini_skill_text(skill, case.marker), encoding="utf-8")
    return temp_root, codex_home, workspace


def command_tail(text: str, max_lines: int = 12) -> str | None:
    stripped = text.strip()
    if not stripped:
        return None
    lines = stripped.splitlines()
    return "\n".join(lines[-max_lines:])


def run_codex_case(case: ProbeCase, timeout_seconds: int, dry_run: bool) -> ProbeResult:
    skill = load_skill_metadata(case.fixture)
    temp_root, codex_home, workspace = build_codex_runtime(case, skill, copy_auth=not dry_run)
    output_path = temp_root / "last-message.txt"

    command = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "--ignore-user-config",
        "--json",
        "-o",
        str(output_path),
        "-C",
        str(workspace),
        codex_probe_prompt(case.prompt),
    ]
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)

    if dry_run:
        return ProbeResult(
            fixture=case.fixture,
            kind=case.kind,
            prompt=case.prompt,
            expected=case.expected,
            actual="dry-run",
            passed=False,
            harness="codex",
            command=command,
            marker=case.marker,
            output="",
            returncode=None,
            stderr_tail=None,
            stdout_tail=None,
            temp_root=str(temp_root),
        )

    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return ProbeResult(
            fixture=case.fixture,
            kind=case.kind,
            prompt=case.prompt,
            expected=case.expected,
            actual="timeout",
            passed=False,
            harness="codex",
            command=command,
            marker=case.marker,
            output="",
            returncode=None,
            stderr_tail=command_tail(exc.stderr or ""),
            stdout_tail=command_tail(exc.stdout or ""),
            temp_root=str(temp_root),
        )

    output = output_path.read_text(encoding="utf-8").strip() if output_path.exists() else ""
    if completed.returncode != 0 and not output:
        actual = "error"
    elif output == case.marker:
        actual = "triggered"
    elif output == NO_SKILL_SENTINEL:
        actual = "not_triggered"
    else:
        actual = "indeterminate"

    return ProbeResult(
        fixture=case.fixture,
        kind=case.kind,
        prompt=case.prompt,
        expected=case.expected,
        actual=actual,
        passed=actual == case.expected,
        harness="codex",
        command=command,
        marker=case.marker,
        output=output,
        returncode=completed.returncode,
        stderr_tail=command_tail(completed.stderr),
        stdout_tail=command_tail(completed.stdout),
        temp_root=str(temp_root),
    )


def run_probe_cases(cases: list[ProbeCase], timeout_seconds: int, dry_run: bool) -> list[ProbeResult]:
    results: list[ProbeResult] = []
    for case in cases:
        results.append(run_codex_case(case, timeout_seconds=timeout_seconds, dry_run=dry_run))
    return results


def codex_support_report() -> dict[str, object]:
    codex_path = shutil.which("codex")
    if not codex_path:
        return {
            "available": False,
            "reason": "codex binary not found in PATH",
        }

    help_output = subprocess.run(
        ["codex", "exec", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout = help_output.stdout
    source_codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()

    return {
        "available": True,
        "path": codex_path,
        "supports_json": "--json" in stdout,
        "supports_output_last_message": "--output-last-message" in stdout or "-o, --output-last-message" in stdout,
        "supports_ephemeral": "--ephemeral" in stdout,
        "supports_ignore_user_config": "--ignore-user-config" in stdout,
        "auth_source": str(source_codex_home),
        "auth_present": (source_codex_home / "auth.json").exists() or bool(os.environ.get("OPENAI_API_KEY")),
        "skills_home": "$CODEX_HOME/skills",
        "selection_reason": "Codex provides a writable isolated skills home plus non-interactive JSON output.",
    }


def claude_support_report() -> dict[str, object]:
    claude_path = shutil.which("claude")
    if not claude_path:
        return {
            "available": False,
            "reason": "claude binary not found in PATH",
        }

    help_output = subprocess.run(
        ["claude", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout = help_output.stdout
    claude_home = Path.home() / ".claude"

    return {
        "available": True,
        "path": claude_path,
        "supports_print": "--print" in stdout or "-p, --print" in stdout,
        "supports_output_format_json": "--output-format <format>" in stdout,
        "supports_plugin_dir": "--plugin-dir <path>" in stdout,
        "credentials_present": (claude_home / ".credentials.json").exists(),
        "note": "Claude remains a candidate for future comparison, but Codex is the default proxy harness.",
    }


def summarize_results(results: list[ProbeResult]) -> dict[str, int]:
    summary = {
        "passed": 0,
        "failed": 0,
        "triggered": 0,
        "not_triggered": 0,
        "indeterminate": 0,
        "error": 0,
        "timeout": 0,
        "dry-run": 0,
    }
    for result in results:
        if result.actual == "dry-run":
            pass
        elif result.passed:
            summary["passed"] += 1
        else:
            summary["failed"] += 1
        if result.actual in summary:
            summary[result.actual] += 1
    return summary


def print_text_results(results: list[ProbeResult]) -> None:
    for result in results:
        if result.actual == "dry-run":
            verdict = "DRY-RUN"
        else:
            verdict = "PASS" if result.passed else "FAIL"
        print(f"[{verdict}] {result.fixture} {result.kind}: expected={result.expected} actual={result.actual}")
        print(f"  prompt: {result.prompt}")
        if result.output:
            print(f"  output: {result.output}")
        if result.stderr_tail:
            print("  stderr tail:")
            print(textwrap.indent(result.stderr_tail, "    "))
        if result.stdout_tail:
            print("  stdout tail:")
            print(textwrap.indent(result.stdout_tail, "    "))
        if result.temp_root:
            print(f"  temp root: {result.temp_root}")
        print(f"  command: {' '.join(result.command)}")

    print(json.dumps({"summary": summarize_results(results)}, indent=2))


def list_fixtures() -> None:
    fixtures = load_fixtures()
    payload = [asdict(fixture) for fixture in fixtures]
    print(json.dumps(payload, indent=2))


def run_spike(as_json: bool) -> int:
    payload = {
        "selected_proxy_harness": DEFAULT_HARNESS,
        "codex": codex_support_report(),
        "claude": claude_support_report(),
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, indent=2))
    return 0


def run_command(args: argparse.Namespace) -> int:
    fixtures = load_fixtures(selected_skill=args.skill)
    cases = build_probe_cases(fixtures)
    if args.limit is not None:
        cases = cases[: args.limit]
    results = run_probe_cases(cases, timeout_seconds=args.timeout_seconds, dry_run=args.dry_run)

    if args.json:
        print(
            json.dumps(
                {
                    "harness": DEFAULT_HARNESS,
                    "results": [asdict(result) for result in results],
                    "summary": summarize_results(results),
                },
                indent=2,
            )
        )
    else:
        print_text_results(results)

    if args.dry_run:
        return 0
    return 0 if all(result.passed for result in results) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run lightweight trigger probes against synthetic mini-skills.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-fixtures", help="List available trigger fixtures.")
    list_parser.set_defaults(handler=lambda _args: list_fixtures() or 0)

    spike_parser = subparsers.add_parser("spike", help="Report local CLI capabilities for the proxy harness decision.")
    spike_parser.add_argument("--json", action="store_true", help="Print the spike report as JSON.")
    spike_parser.set_defaults(handler=lambda ns: run_spike(as_json=ns.json))

    run_parser = subparsers.add_parser("run", help="Run trigger fixtures with the default proxy harness.")
    run_parser.add_argument("--skill", help="Run only one skill fixture by name.")
    run_parser.add_argument("--limit", type=int, help="Run only the first N cases after filtering.")
    run_parser.add_argument("--dry-run", action="store_true", help="Build the runtime plan without executing Codex.")
    run_parser.add_argument("--json", action="store_true", help="Print results as JSON.")
    run_parser.add_argument("--timeout-seconds", type=int, default=90, help="Per-case Codex timeout in seconds.")
    run_parser.set_defaults(handler=run_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
