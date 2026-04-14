#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
MCP_NAME = "kong-konnect"
MCP_URL = "https://us.mcp.konghq.com"
TOKEN_ENV = "KONNECT_TOKEN"
PLUGIN_NAME = "kong-skills"
REPO_URL = "https://github.com/johnharris85/kong-skills"
AVAILABLE_SKILLS_START = "<!-- generated:available-skills:start -->"
AVAILABLE_SKILLS_END = "<!-- generated:available-skills:end -->"
SKILLS_DOC = REPO_ROOT / "docs" / "skills.md"


@dataclass
class Skill:
    dir_name: str
    name: str
    description: str

    @property
    def rel_path(self) -> str:
        return f"./skills/{self.dir_name}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def load_json(path: Path) -> object:
    return json.loads(read_text(path))


def dump_json(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=True) + "\n"


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter start")

    try:
        _, rest = text.split("---\n", 1)
        raw_frontmatter, _ = rest.split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: malformed YAML frontmatter") from exc

    result: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"{path}: invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def discover_skills() -> list[Skill]:
    if not SKILLS_DIR.exists():
        raise ValueError("skills directory is missing")

    skills: list[Skill] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            raise ValueError(f"{entry}: missing SKILL.md")
        frontmatter = parse_frontmatter(skill_md)
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not name or not description:
            raise ValueError(f"{skill_md}: frontmatter requires name and description")
        if name != entry.name:
            raise ValueError(f"{skill_md}: frontmatter name {name!r} must match directory {entry.name!r}")
        skills.append(Skill(dir_name=entry.name, name=name, description=description))
    return skills


def replace_generated_section(text: str, start: str, end: str, body: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{body}\n{end}"
    if not pattern.search(text):
        raise ValueError(f"missing generated section markers: {start} ... {end}")
    return pattern.sub(replacement, text, count=1)


def expected_available_skills(skills: list[Skill]) -> str:
    return "\n".join(f"- `{skill.name}`: {skill.description}" for skill in skills)


def sync_skills_doc(skills: list[Skill]) -> str:
    path = SKILLS_DOC
    text = read_text(path)
    return replace_generated_section(text, AVAILABLE_SKILLS_START, AVAILABLE_SKILLS_END, expected_available_skills(skills))


def sync_claude_plugin(skills: list[Skill]) -> object:
    path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    data = load_json(path)
    data["skills"] = [skill.rel_path for skill in skills]
    data["mcpServers"] = "./claude.mcp.json"
    return data


def sync_codex_plugin(skills: list[Skill]) -> object:
    path = REPO_ROOT / ".codex-plugin" / "plugin.json"
    data = load_json(path)
    data["keywords"] = [
        "kong",
        "datakit",
        "mcp",
    ]
    data["skills"] = [skill.rel_path for skill in skills]
    data["mcpServers"] = [MCP_NAME]
    data["interface"]["capabilities"] = [
        "kong",
        "datakit",
    ]
    return data


def sync_root_mcp() -> object:
    return {
        MCP_NAME: {
            "type": "streamable_http",
            "url": MCP_URL,
            "headers": {"Authorization": f"Bearer ${{{TOKEN_ENV}}}"},
        }
    }


def sync_cursor_mcp() -> object:
    return {
        "mcpServers": {
            MCP_NAME: {
                "url": MCP_URL,
                "headers": {"Authorization": f"Bearer ${{{TOKEN_ENV}}}"},
            }
        }
    }


def sync_gemini_extension() -> object:
    path = REPO_ROOT / "gemini-extension.json"
    data = load_json(path)
    data["mcpServers"] = {
        MCP_NAME: {
            "url": MCP_URL,
            "headers": {"Authorization": f"Bearer ${{{TOKEN_ENV}}}"},
        }
    }
    data["settings"] = [
        {
            "name": "Konnect Bearer Token",
            "description": "Bearer token used to authenticate requests to the Kong MCP server.",
            "envVar": TOKEN_ENV,
            "sensitive": True,
        }
    ]
    return data


def sync_copilot_mcp() -> object:
    return {
        "servers": {
            MCP_NAME: {
                "type": "http",
                "url": MCP_URL,
                "requestInit": {
                    "headers": {"Authorization": f"Bearer ${{{TOKEN_ENV}}}"}
                },
            }
        }
    }


def sync_claude_mcp() -> object:
    return {
        "mcpServers": {
            MCP_NAME: {
                "type": "http",
                "url": MCP_URL,
                "headers": {"Authorization": f"Bearer ${{{TOKEN_ENV}}}"},
            }
        }
    }


def validate_static_metadata() -> list[str]:
    errors: list[str] = []

    codex_marketplace = load_json(REPO_ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_marketplace = load_json(REPO_ROOT / ".claude-plugin" / "marketplace.json")
    codex_plugin = load_json(REPO_ROOT / ".codex-plugin" / "plugin.json")
    claude_plugin = load_json(REPO_ROOT / ".claude-plugin" / "plugin.json")
    gemini_extension = load_json(REPO_ROOT / "gemini-extension.json")

    if codex_plugin.get("name") != PLUGIN_NAME:
        errors.append(".codex-plugin/plugin.json: unexpected plugin name")
    if claude_plugin.get("name") != PLUGIN_NAME:
        errors.append(".claude-plugin/plugin.json: unexpected plugin name")
    expected_versions = {
        ".codex-plugin/plugin.json": codex_plugin.get("version"),
        ".claude-plugin/plugin.json": claude_plugin.get("version"),
        "gemini-extension.json": gemini_extension.get("version"),
    }
    versions = {value for value in expected_versions.values()}
    if len(versions) != 1:
        errors.append(f"release versions must match across manifests: {expected_versions}")
    if codex_plugin.get("homepage") != REPO_URL or codex_plugin.get("repository") != REPO_URL:
        errors.append(".codex-plugin/plugin.json: homepage/repository drift")
    if claude_marketplace.get("name") != PLUGIN_NAME:
        errors.append(".claude-plugin/marketplace.json: unexpected marketplace name")
    if codex_marketplace.get("name") != PLUGIN_NAME:
        errors.append(".agents/plugins/marketplace.json: unexpected marketplace name")
    if claude_marketplace.get("plugins", [{}])[0].get("name") != PLUGIN_NAME:
        errors.append(".claude-plugin/marketplace.json: plugin listing name drift")
    if codex_marketplace.get("plugins", [{}])[0].get("name") != PLUGIN_NAME:
        errors.append(".agents/plugins/marketplace.json: plugin listing name drift")
    return errors


def validate_openai_yaml(skills: list[Skill]) -> list[str]:
    errors: list[str] = []
    for skill in skills:
        yaml_path = SKILLS_DIR / skill.dir_name / "agents" / "openai.yaml"
        if not yaml_path.exists():
            continue
        text = read_text(yaml_path)
        required_snippets = [
            f'value: "{MCP_NAME}"',
            f'url: "{MCP_URL}"',
        ]
        for snippet in required_snippets:
            if snippet not in text:
                errors.append(f"{yaml_path.relative_to(REPO_ROOT)}: missing {snippet}")
    return errors


def validate_no_generic_skills(skills: list[Skill]) -> list[str]:
    errors: list[str] = []
    forbidden = {"web-search", "research-assistant"}
    present = forbidden.intersection({skill.name for skill in skills})
    for name in sorted(present):
        errors.append(f"skills/{name}: generic skill should not be present in this repo")
    return errors


def validate_text_files() -> list[str]:
    errors: list[str] = []
    checks: dict[Path, list[str]] = {
        REPO_ROOT / "docs" / "install" / "github-copilot.md": [MCP_NAME, MCP_URL, TOKEN_ENV, "npx skills add johnharris85/kong-skills"],
        REPO_ROOT / "docs" / "install" / "goose.md": [MCP_NAME, MCP_URL, TOKEN_ENV, "goose configure"],
        REPO_ROOT / "goose" / "config.yaml": [MCP_NAME, MCP_URL, TOKEN_ENV, "streamable_http"],
        REPO_ROOT / "docs" / "install" / "cursor.md": [MCP_NAME, MCP_URL, TOKEN_ENV, "npx skills add johnharris85/kong-skills"],
        REPO_ROOT / "docs" / "install" / "claude-code.md": ["Claude Code", "kong-skills", MCP_NAME],
        REPO_ROOT / "docs" / "install" / "codex.md": ["Codex", "npx skills add johnharris85/kong-skills", MCP_NAME],
        REPO_ROOT / "docs" / "install" / "gemini-cli.md": ["Gemini CLI", TOKEN_ENV, MCP_NAME],
    }
    for path, snippets in checks.items():
        text = read_text(path)
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{path.relative_to(REPO_ROOT)}: missing {snippet!r}")
    return errors


def compare_or_write(path: Path, expected: str, fix: bool, errors: list[str]) -> None:
    actual = read_text(path)
    if actual == expected:
        return
    if fix:
        write_text(path, expected)
    else:
        errors.append(f"{path.relative_to(REPO_ROOT)} is out of sync; run `mise run sync`")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and sync repo metadata.")
    parser.add_argument("--fix", action="store_true", help="Rewrite generated files in place.")
    args = parser.parse_args()

    try:
        skills = discover_skills()
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    errors: list[str] = []

    compare_or_write(SKILLS_DOC, sync_skills_doc(skills), args.fix, errors)
    compare_or_write(REPO_ROOT / ".claude-plugin" / "plugin.json", dump_json(sync_claude_plugin(skills)), args.fix, errors)
    compare_or_write(REPO_ROOT / "claude.mcp.json", dump_json(sync_claude_mcp()), args.fix, errors)
    compare_or_write(REPO_ROOT / ".codex-plugin" / "plugin.json", dump_json(sync_codex_plugin(skills)), args.fix, errors)
    compare_or_write(REPO_ROOT / ".mcp.json", dump_json(sync_root_mcp()), args.fix, errors)
    compare_or_write(REPO_ROOT / "cursor" / "mcp.json", dump_json(sync_cursor_mcp()), args.fix, errors)
    compare_or_write(REPO_ROOT / "gemini-extension.json", dump_json(sync_gemini_extension()), args.fix, errors)
    compare_or_write(REPO_ROOT / ".github" / "mcp.json", dump_json(sync_copilot_mcp()), args.fix, errors)
    compare_or_write(REPO_ROOT / "copilot" / "mcp.json", dump_json(sync_copilot_mcp()), args.fix, errors)

    errors.extend(validate_static_metadata())
    errors.extend(validate_openai_yaml(skills))
    errors.extend(validate_no_generic_skills(skills))
    errors.extend(validate_text_files())

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("repo-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
