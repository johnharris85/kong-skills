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


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/release.py <version>", file=sys.stderr)
        return 1

    version = sys.argv[1].strip()
    if not VERSION_RE.match(version):
        print(f"invalid version: {version!r} (expected semver like 1.2.3)", file=sys.stderr)
        return 1

    tag = f"v{version}"
    status = capture("git", "status", "--short")
    if status:
        print("working tree must be clean before release", file=sys.stderr)
        print(status, file=sys.stderr)
        return 1

    existing = capture("git", "tag", "--list", tag)
    if existing:
        print(f"tag already exists: {tag}", file=sys.stderr)
        return 1

    run("python", "scripts/release_prepare.py", version)
    run("python", "scripts/check_repo.py")
    run("git", "add", *GENERATED_TARGETS)
    run("git", "commit", "-m", f"Release {tag}")
    run("git", "tag", "-a", tag, "-m", tag)
    run("git", "push", "origin", "main")
    run("git", "push", "origin", tag)
    run("gh", "release", "create", tag, "--generate-notes")
    print(f"released {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
