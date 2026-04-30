#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
FIXTURES_DIR = REPO_ROOT / "tests" / "trigger-fixtures"
RUNTIME_ROOT = REPO_ROOT / ".tmp" / "trigger-harness"
NO_SKILL_SENTINEL = "NO_SKILL"
AUTH_FILES = ("auth.json", "installation_id", "version.json")
PROGRESS_LOCK = threading.Lock()
ANSI_RESET = "\033[0m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"


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
    duration_seconds: float | None


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


def codex_plugin_name() -> str:
    plugin_path = REPO_ROOT / ".codex-plugin" / "plugin.json"
    try:
        data = json.loads(read_text(plugin_path))
    except (OSError, json.JSONDecodeError, KeyError):
        return "kong-skills"
    name = data.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return "kong-skills"


def expected_trigger_outputs(skill_name: str, marker: str) -> set[str]:
    plugin_name = codex_plugin_name()
    return {
        marker,
        skill_name,
        f"{plugin_name}:{skill_name}",
    }


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


def cleanup_temp_root(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


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


def classify_output(case: ProbeCase, output: str, returncode: int | None) -> str:
    normalized = output.strip()
    if returncode not in (0, None) and not normalized:
        return "error"
    if normalized in expected_trigger_outputs(case.fixture, case.marker):
        return "triggered"
    if normalized == NO_SKILL_SENTINEL:
        return "not_triggered"
    return "indeterminate"


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    return f"{seconds:.1f}s"


def progress_bar(completed: int, total: int, width: int = 24) -> str:
    if total <= 0:
        return "[" + ("-" * width) + "]"
    filled = int(width * completed / total)
    filled = max(0, min(width, filled))
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


def emit_progress(enabled: bool, message: str) -> None:
    if not enabled:
        return
    with PROGRESS_LOCK:
        print(message, file=sys.stderr, flush=True)


def colorize(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_progress_status(status: str, use_color: bool) -> str:
    color = None
    if status in {"PASS"}:
        color = ANSI_GREEN
    elif status in {"FAIL", "TIMEOUT", "ERROR"}:
        color = ANSI_RED
    elif status in {"DRY-RUN", "START", "RUNNING"}:
        color = ANSI_YELLOW
    return colorize(status, color, use_color) if color else status


def progress_tty() -> bool:
    return sys.stderr.isatty()


def format_progress_event(event: str, **fields: object) -> str:
    parts = [f"event={event}"]
    for key, value in fields.items():
        if value is None:
            continue
        text = str(value)
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        parts.append(f'{key}="{escaped}"')
    return " ".join(parts)


def run_codex_case(
    case: ProbeCase,
    timeout_seconds: int,
    dry_run: bool,
    keep_temp: bool,
    progress_enabled: bool,
    progress_interval_seconds: int,
    case_index: int,
    total_cases: int,
) -> ProbeResult:
    skill = load_skill_metadata(case.fixture)
    start_time = time.monotonic()
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

    label = f"{case.fixture} {case.kind}"
    emit_progress(
        progress_enabled,
        format_progress_event(
            "case_start",
            status=format_progress_status("START", progress_tty()),
            case=f"{case_index}/{total_cases}",
            skill=case.fixture,
            kind=case.kind,
            expected=case.expected,
            timeout_seconds=timeout_seconds,
        ),
    )

    if dry_run:
        result = ProbeResult(
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
            temp_root=str(temp_root) if keep_temp else None,
            duration_seconds=time.monotonic() - start_time,
        )
        if not keep_temp:
            cleanup_temp_root(temp_root)
        return result

    try:
        process = subprocess.Popen(
            command,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        result = ProbeResult(
            fixture=case.fixture,
            kind=case.kind,
            prompt=case.prompt,
            expected=case.expected,
            actual="error",
            passed=False,
            harness="codex",
            command=command,
            marker=case.marker,
            output="",
            returncode=None,
            stderr_tail=str(exc),
            stdout_tail=None,
            temp_root=str(temp_root) if keep_temp else None,
            duration_seconds=time.monotonic() - start_time,
        )
        if not keep_temp:
            cleanup_temp_root(temp_root)
        return result

    next_heartbeat_seconds = progress_interval_seconds
    while True:
        returncode = process.poll()
        elapsed = time.monotonic() - start_time
        if returncode is not None:
            break
        if elapsed >= timeout_seconds:
            process.kill()
            stdout, stderr = process.communicate()
            emit_progress(
                progress_enabled,
                format_progress_event(
                    "case_timeout",
                    status=format_progress_status("TIMEOUT", progress_tty()),
                    case=f"{case_index}/{total_cases}",
                    skill=case.fixture,
                    kind=case.kind,
                    duration=format_duration(elapsed),
                ),
            )
            result = ProbeResult(
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
                stderr_tail=command_tail(stderr or ""),
                stdout_tail=command_tail(stdout or ""),
                temp_root=str(temp_root) if keep_temp else None,
                duration_seconds=elapsed,
            )
            if not keep_temp:
                cleanup_temp_root(temp_root)
            return result
        if progress_interval_seconds > 0 and elapsed >= next_heartbeat_seconds:
            emit_progress(
                progress_enabled,
                format_progress_event(
                    "case_running",
                    status=format_progress_status("RUNNING", progress_tty()),
                    case=f"{case_index}/{total_cases}",
                    skill=case.fixture,
                    kind=case.kind,
                    elapsed=format_duration(elapsed),
                    timeout_seconds=timeout_seconds,
                ),
            )
            next_heartbeat_seconds += progress_interval_seconds
        time.sleep(1)

    stdout, stderr = process.communicate()

    output = output_path.read_text(encoding="utf-8").strip() if output_path.exists() else ""
    elapsed = time.monotonic() - start_time
    actual = classify_output(case, output, process.returncode)

    result = ProbeResult(
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
        returncode=process.returncode,
        stderr_tail=command_tail(stderr),
        stdout_tail=command_tail(stdout),
        temp_root=str(temp_root) if keep_temp else None,
        duration_seconds=elapsed,
    )
    if not keep_temp:
        cleanup_temp_root(temp_root)
    return result


def run_probe_cases(
    cases: list[ProbeCase],
    timeout_seconds: int,
    dry_run: bool,
    keep_temp: bool,
    progress_enabled: bool,
    progress_interval_seconds: int,
    jobs: int,
) -> list[ProbeResult]:
    total_cases = len(cases)
    if total_cases == 0:
        return []

    worker_count = max(1, min(jobs, total_cases))
    emit_progress(
        progress_enabled,
        format_progress_event(
            "run_start",
            status=format_progress_status("START", progress_tty()),
            total_cases=total_cases,
            jobs=worker_count,
        ),
    )

    indexed_results: list[ProbeResult | None] = [None] * total_cases
    completed_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_index = {
            executor.submit(
                run_codex_case,
                case,
                timeout_seconds,
                dry_run,
                keep_temp,
                progress_enabled,
                progress_interval_seconds,
                index,
                total_cases,
            ): index - 1
            for index, case in enumerate(cases, start=1)
        }
        for future in concurrent.futures.as_completed(future_to_index):
            result_index = future_to_index[future]
            result = future.result()
            indexed_results[result_index] = result
            completed_count += 1
            case = cases[result_index]
            bar = progress_bar(completed_count, total_cases)
            verdict = "DRY-RUN" if result.actual == "dry-run" else ("PASS" if result.passed else "FAIL")
            emit_progress(
                progress_enabled,
                format_progress_event(
                    "case_done",
                    progress=bar,
                    status=format_progress_status(verdict, progress_tty()),
                    completed=f"{completed_count}/{total_cases}",
                    skill=case.fixture,
                    kind=case.kind,
                    expected=result.expected,
                    actual=result.actual,
                    duration=format_duration(result.duration_seconds),
                ),
            )

    return [result for result in indexed_results if result is not None]


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
    use_color = sys.stdout.isatty()
    if results and all(result.actual == "dry-run" for result in results):
        print(colorize(f"Dry-run planned {len(results)} cases", ANSI_YELLOW, use_color))
        print(json.dumps({"summary": summarize_results(results)}, indent=2))
        return

    failures: list[ProbeResult] = []
    for result in results:
        if result.actual != "dry-run" and result.passed:
            continue
        failures.append(result)

    if failures:
        print(f"Detailed failures: {len(failures)}")
    else:
        print(colorize("All cases passed", ANSI_GREEN, use_color))

    for result in failures:
        if result.actual == "dry-run":
            verdict = colorize("DRY-RUN", ANSI_YELLOW, use_color)
        else:
            verdict = colorize("PASS", ANSI_GREEN, use_color) if result.passed else colorize("FAIL", ANSI_RED, use_color)
        print(f"[{verdict}] {result.fixture} {result.kind}")
        print(f"  expected: {result.expected}")
        print(f"  result: {result.actual}")
        print(f"  prompt: {result.prompt}")
        print(f"  llm output: {result.output if result.output else '<empty>'}")

    print(json.dumps({"summary": summarize_results(results)}, indent=2))


def list_fixtures() -> None:
    fixtures = load_fixtures()
    payload = [asdict(fixture) for fixture in fixtures]
    print(json.dumps(payload, indent=2))

def run_command(args: argparse.Namespace) -> int:
    fixtures = load_fixtures(selected_skill=args.skill)
    cases = build_probe_cases(fixtures)
    if args.limit is not None:
        cases = cases[: args.limit]
    results = run_probe_cases(
        cases,
        timeout_seconds=args.timeout_seconds,
        dry_run=args.dry_run,
        keep_temp=args.keep_temp,
        progress_enabled=not args.no_progress,
        progress_interval_seconds=args.progress_interval_seconds,
        jobs=args.jobs,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "harness": "codex",
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

    run_parser = subparsers.add_parser("run", help="Run trigger fixtures with the default proxy harness.")
    run_parser.add_argument("--skill", help="Run only one skill fixture by name.")
    run_parser.add_argument("--limit", type=int, help="Run only the first N cases after filtering.")
    run_parser.add_argument("--dry-run", action="store_true", help="Build the runtime plan without executing Codex.")
    run_parser.add_argument("--keep-temp", action="store_true", help="Preserve temporary CODEX_HOME and workspace directories for debugging.")
    run_parser.add_argument("--json", action="store_true", help="Print results as JSON.")
    run_parser.add_argument("--jobs", type=int, default=3, help="Run up to N probe cases in parallel.")
    run_parser.add_argument("--no-progress", action="store_true", help="Disable live progress reports on stderr.")
    run_parser.add_argument(
        "--progress-interval-seconds",
        type=int,
        default=10,
        help="Emit a still-running progress heartbeat every N seconds while a case is in flight.",
    )
    run_parser.add_argument("--timeout-seconds", type=int, default=90, help="Per-case Codex timeout in seconds.")
    run_parser.set_defaults(handler=run_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
