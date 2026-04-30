#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
GENERATED_TARGETS = [
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".mcp.json",
    "claude.mcp.json",
    "copilot-mcp.json",
    "cursor-mcp.json",
    "docs/skills.md",
    "gemini-extension.json",
]


def run(*args: str) -> None:
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def capture(*args: str) -> str:
    return subprocess.run(args, cwd=REPO_ROOT, check=True, text=True, capture_output=True).stdout.strip()


def preflight(version: str, tag: str) -> int:
    status = capture("git", "status", "--short")
    if status:
        print("working tree must be clean before release", file=sys.stderr)
        print(status, file=sys.stderr)
        return 1

    existing_local_tag = capture("git", "tag", "--list", tag)
    if existing_local_tag:
        print(f"tag already exists locally: {tag}", file=sys.stderr)
        return 1

    remote_tags = capture("git", "ls-remote", "--tags", "origin", tag)
    if remote_tags:
        print(f"tag already exists on origin: {tag}", file=sys.stderr)
        return 1

    try:
        capture("gh", "auth", "status")
    except subprocess.CalledProcessError as exc:
        print("gh must be installed and authenticated before release", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr.strip(), file=sys.stderr)
        return 1

    try:
        capture("gh", "release", "view", tag)
    except subprocess.CalledProcessError:
        return 0

    print(f"GitHub release already exists: {tag}", file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/release.py <version>", file=sys.stderr)
        return 1

    version = sys.argv[1].strip()
    if not VERSION_RE.match(version):
        print(f"invalid version: {version!r} (expected semver like 1.2.3)", file=sys.stderr)
        return 1

    tag = f"v{version}"
    if preflight(version, tag) != 0:
        return 1

    run(sys.executable, "scripts/release_prepare.py", version)
    run(sys.executable, "scripts/check_repo.py")
    run("git", "add", *GENERATED_TARGETS)
    run("git", "commit", "-m", f"Release {tag}")
    run("git", "push", "origin", "main")
    run("gh", "release", "create", tag, "--target", "main", "--generate-notes")
    run("git", "fetch", "--tags", "origin")
    print(f"released {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
