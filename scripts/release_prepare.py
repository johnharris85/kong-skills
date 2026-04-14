#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def update_version(path: Path, version: str) -> None:
    data = load_json(path)
    if "version" in data:
        data["version"] = version
    write_json(path, data)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/release_prepare.py <version>", file=sys.stderr)
        return 1

    version = sys.argv[1].strip()
    if not VERSION_RE.match(version):
        print(f"invalid version: {version!r} (expected semver like 1.2.3)", file=sys.stderr)
        return 1

    targets = [
        REPO_ROOT / ".claude-plugin" / "plugin.json",
        REPO_ROOT / ".codex-plugin" / "plugin.json",
        REPO_ROOT / "gemini-extension.json",
    ]
    for target in targets:
        update_version(target, version)

    print(f"prepared release {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
