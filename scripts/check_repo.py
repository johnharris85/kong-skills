#!/usr/bin/env python3
"""Validate checked-in skills, generated metadata, and key repo docs.

This script intentionally keeps all repo-level sync and validation in one place.
It is long, but the behavior is narrowly scoped: discover skills, regenerate the
derived manifests/docs, then apply package-policy and drift checks.
"""
from __future__ import annotations

import argparse
import json
import re
import stat
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
MCP_NAME = "kong-konnect"
MCP_URL = "https://us.mcp.konghq.com"
TOKEN_ENV = "KONNECT_TOKEN"
PLUGIN_NAME = "kong-skills"
REPO_URL = "https://github.com/kong/skills"
AVAILABLE_SKILLS_START = "<!-- generated:available-skills:start -->"
AVAILABLE_SKILLS_END = "<!-- generated:available-skills:end -->"
SKILLS_DOC = REPO_ROOT / "docs" / "skills.md"
ALLOWED_SKILL_ROOT_FILES = {"SKILL.md"}
ALLOWED_SKILL_DIRS = {"references", "assets", "scripts"}
MAX_COMPANION_FILE_BYTES = 1_000_000
MAX_SKILL_MD_LINES = 500
MAX_DESCRIPTION_CHARS = 260
MAX_INITIAL_SKILLS_LIST_CHARS = 6_500
TEXT_FILE_EXTENSIONS = {
    ".json",
    ".js",
    ".md",
    ".py",
    ".sh",
    ".text",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bkpat_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bspat_[A-Za-z0-9]{20,}\b"),
]
SCAFFOLD_PLACEHOLDER_SNIPPETS = [
    "Replace this with a real summary.",
    "replace this bullet with the request pattern that should trigger the skill",
    "Replace this section with the real do/do-not guidance for the workflow.",
    "Remove generic filler before committing the skill.",
]
DESCRIPTION_STOPWORDS = {
    "a",
    "an",
    "and",
    "any",
    "are",
    "as",
    "asks",
    "by",
    "can",
    "classify",
    "configuration",
    "config",
    "control",
    "create",
    "current",
    "decide",
    "declarative",
    "does",
    "existing",
    "for",
    "from",
    "gateway",
    "help",
    "how",
    "in",
    "instead",
    "into",
    "is",
    "it",
    "its",
    "kong",
    "konnect",
    "manage",
    "managed",
    "new",
    "of",
    "on",
    "or",
    "out",
    "plugin",
    "repo",
    "repository",
    "resource",
    "resources",
    "revise",
    "same",
    "self",
    "setup",
    "skill",
    "skills",
    "state",
    "the",
    "their",
    "this",
    "to",
    "tool",
    "tools",
    "troubleshoot",
    "update",
    "use",
    "user",
    "users",
    "using",
    "wants",
    "when",
    "with",
    "workflow",
    "workflows",
}
SIMILARITY_ALLOWLIST = {
    frozenset({"terraform-konnect", "terraform-kong-gateway"}),
}


@dataclass
class Skill:
    dir_name: str
    name: str
    description: str
    license: str
    product: str
    category: str
    tags: list[str]

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


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def normalize_term(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.strip().lower()).strip("-")


def derived_keywords(skills: list[Skill]) -> list[str]:
    values = ["kong", "skills", "mcp"]
    for skill in skills:
        values.extend([skill.name, skill.product, skill.category])
        values.extend(skill.tags)
    return ordered_unique([term for term in (normalize_term(value) for value in values) if term])


def derived_capabilities(skills: list[Skill]) -> list[str]:
    values = ["kong"]
    for skill in skills:
        values.extend([skill.product, skill.category])
        values.extend(skill.tags)
    return ordered_unique([term for term in (normalize_term(value) for value in values) if term])


def parse_frontmatter(path: Path) -> dict[str, object]:
    text = read_text(path)
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter start")

    try:
        _, rest = text.split("---\n", 1)
        raw_frontmatter, _ = rest.split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: malformed YAML frontmatter") from exc

    try:
        parsed = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML frontmatter") from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"{path}: frontmatter must be a YAML mapping")
    return parsed


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
        license_value = frontmatter.get("license")
        if not isinstance(name, str) or not isinstance(description, str) or not name.strip() or not description.strip():
            raise ValueError(f"{skill_md}: frontmatter requires name and description")
        if name != entry.name:
            raise ValueError(f"{skill_md}: frontmatter name {name!r} must match directory {entry.name!r}")
        if not isinstance(license_value, str) or not license_value.strip():
            raise ValueError(f"{skill_md}: frontmatter requires license")

        metadata = frontmatter.get("metadata")
        if not isinstance(metadata, dict):
            raise ValueError(f"{skill_md}: frontmatter requires metadata mapping")

        product = metadata.get("product")
        category = metadata.get("category")
        tags = metadata.get("tags")
        if not isinstance(product, str) or not product.strip():
            raise ValueError(f"{skill_md}: metadata.product must be a non-empty string")
        if not isinstance(category, str) or not category.strip():
            raise ValueError(f"{skill_md}: metadata.category must be a non-empty string")
        if not isinstance(tags, list) or not tags:
            raise ValueError(f"{skill_md}: metadata.tags must be a non-empty list")
        if not all(isinstance(tag, str) and tag.strip() for tag in tags):
            raise ValueError(f"{skill_md}: metadata.tags entries must be non-empty strings")

        skills.append(
            Skill(
                dir_name=entry.name,
                name=name.strip(),
                description=description.strip(),
                license=license_value.strip(),
                product=product.strip(),
                category=category.strip(),
                tags=[tag.strip() for tag in tags],
            )
        )
    return skills


# Generated-file sync helpers.
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
    data["mcpServers"] = "./.mcp.json"
    return data


def sync_claude_marketplace(skills: list[Skill]) -> object:
    path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    data = load_json(path)
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise ValueError(".claude-plugin/marketplace.json: plugins list is missing")
    plugin = plugins[0]
    if not isinstance(plugin, dict):
        raise ValueError(".claude-plugin/marketplace.json: first plugin entry is invalid")
    plugin["keywords"] = derived_keywords(skills)
    return data


def sync_codex_marketplace(skills: list[Skill]) -> object:
    path = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
    data = load_json(path)
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise ValueError(".agents/plugins/marketplace.json: plugins list is missing")
    plugin = plugins[0]
    if not isinstance(plugin, dict):
        raise ValueError(".agents/plugins/marketplace.json: first plugin entry is invalid")
    plugin["name"] = PLUGIN_NAME
    plugin["source"] = {
        "source": "local",
        "path": "./",
    }
    plugin["policy"] = {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }
    plugin["category"] = "Productivity"
    plugin["keywords"] = derived_keywords(skills)
    return data


def sync_codex_plugin(skills: list[Skill]) -> object:
    path = REPO_ROOT / ".codex-plugin" / "plugin.json"
    data = load_json(path)
    data["keywords"] = derived_keywords(skills)
    data["skills"] = [skill.rel_path for skill in skills]
    data["mcpServers"] = [MCP_NAME]
    data["interface"]["capabilities"] = derived_capabilities(skills)
    return data


def sync_root_mcp() -> object:
    return {
        "mcpServers": {
            MCP_NAME: {
                "type": "http",
                "url": MCP_URL,
                "headers": {"Authorization": f"Bearer ${{{TOKEN_ENV}}}"},
            }
        }
    }


def sync_cursor_plugin(skills: list[Skill]) -> object:
    path = REPO_ROOT / ".cursor-plugin" / "plugin.json"
    data = load_json(path)
    data["skills"] = "skills"
    data["mcpServers"] = ".mcp.json"
    data["keywords"] = derived_keywords(skills)
    return data


def sync_cursor_marketplace() -> object:
    path = REPO_ROOT / ".cursor-plugin" / "marketplace.json"
    data = load_json(path)
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise ValueError(".cursor-plugin/marketplace.json: plugins list is missing")
    plugin = plugins[0]
    if not isinstance(plugin, dict):
        raise ValueError(".cursor-plugin/marketplace.json: first plugin entry is invalid")
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(".cursor-plugin/marketplace.json: metadata is missing")
    metadata["version"] = plugin.get("version", metadata.get("version"))
    plugin["name"] = PLUGIN_NAME
    plugin["source"] = "./"
    plugin["skills"] = "skills"
    return data


# Validation helpers.
def validate_static_metadata() -> list[str]:
    errors: list[str] = []

    codex_marketplace = load_json(REPO_ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_marketplace = load_json(REPO_ROOT / ".claude-plugin" / "marketplace.json")
    cursor_marketplace = load_json(REPO_ROOT / ".cursor-plugin" / "marketplace.json")
    codex_plugin = load_json(REPO_ROOT / ".codex-plugin" / "plugin.json")
    claude_plugin = load_json(REPO_ROOT / ".claude-plugin" / "plugin.json")
    cursor_plugin = load_json(REPO_ROOT / ".cursor-plugin" / "plugin.json")

    if codex_plugin.get("name") != PLUGIN_NAME:
        errors.append(".codex-plugin/plugin.json: unexpected plugin name")
    if claude_plugin.get("name") != PLUGIN_NAME:
        errors.append(".claude-plugin/plugin.json: unexpected plugin name")
    if cursor_plugin.get("name") != PLUGIN_NAME:
        errors.append(".cursor-plugin/plugin.json: unexpected plugin name")
    expected_versions = {
        ".codex-plugin/plugin.json": codex_plugin.get("version"),
        ".claude-plugin/plugin.json": claude_plugin.get("version"),
        ".cursor-plugin/plugin.json": cursor_plugin.get("version"),
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
    if cursor_marketplace.get("name") != PLUGIN_NAME:
        errors.append(".cursor-plugin/marketplace.json: unexpected marketplace name")
    if claude_marketplace.get("plugins", [{}])[0].get("name") != PLUGIN_NAME:
        errors.append(".claude-plugin/marketplace.json: plugin listing name drift")
    if codex_marketplace.get("plugins", [{}])[0].get("name") != PLUGIN_NAME:
        errors.append(".agents/plugins/marketplace.json: plugin listing name drift")
    if cursor_marketplace.get("plugins", [{}])[0].get("name") != PLUGIN_NAME:
        errors.append(".cursor-plugin/marketplace.json: plugin listing name drift")
    return errors


def validate_skill_contents(skills: list[Skill]) -> list[str]:
    errors: list[str] = []
    for skill in skills:
        skill_dir = SKILLS_DIR / skill.dir_name
        skill_md = skill_dir / "SKILL.md"
        skill_md_text = read_text(skill_md)
        skill_md_lines = skill_md_text.count("\n") + 1

        if skill_md_lines > MAX_SKILL_MD_LINES:
            errors.append(
                f"{skill_md.relative_to(REPO_ROOT)}: SKILL.md is too long ({skill_md_lines} lines > {MAX_SKILL_MD_LINES})"
            )

        if len(skill.description) > MAX_DESCRIPTION_CHARS:
            errors.append(
                f"{skill_md.relative_to(REPO_ROOT)}: description is too long ({len(skill.description)} chars > {MAX_DESCRIPTION_CHARS}); front-load trigger words and tighten scope"
            )

        for entry in sorted(skill_dir.iterdir()):
            if entry.name.startswith("."):
                errors.append(f"{entry.relative_to(REPO_ROOT)}: hidden files and directories are not allowed in skill packages")
                continue
            if entry.is_symlink():
                errors.append(f"{entry.relative_to(REPO_ROOT)}: symlinks are not allowed in skill packages")
                continue
            if entry.is_file() and entry.name not in ALLOWED_SKILL_ROOT_FILES:
                errors.append(
                    f"{entry.relative_to(REPO_ROOT)}: unexpected root file; keep only SKILL.md at skill root"
                )
                continue
            if entry.is_dir() and entry.name not in ALLOWED_SKILL_DIRS:
                errors.append(
                    f"{entry.relative_to(REPO_ROOT)}: unexpected directory; allowed companion directories are assets/, references/, scripts/"
                )
                continue

        for path in sorted(skill_dir.rglob("*")):
            if path == skill_dir:
                continue

            if path.name.startswith("."):
                errors.append(f"{path.relative_to(REPO_ROOT)}: hidden files and directories are not allowed in skill packages")
                continue
            if path.is_symlink():
                errors.append(f"{path.relative_to(REPO_ROOT)}: symlinks are not allowed in skill packages")
                continue
            if path.is_dir():
                continue

            if path.stat().st_size > MAX_COMPANION_FILE_BYTES:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)}: file is too large for a skill package ({path.stat().st_size} bytes > {MAX_COMPANION_FILE_BYTES})"
                )

            if path != skill_dir / "SKILL.md" and path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                errors.append(f"{path.relative_to(REPO_ROOT)}: executable files are not allowed in skill packages")

            if path.suffix.lower() in TEXT_FILE_EXTENSIONS or path.name == "SKILL.md":
                text = read_text(path)
                for pattern in SECRET_PATTERNS:
                    if pattern.search(text):
                        errors.append(f"{path.relative_to(REPO_ROOT)}: possible secret material matched {pattern.pattern!r}")
                        break

    return errors


def validate_no_generic_skills(skills: list[Skill]) -> list[str]:
    errors: list[str] = []
    forbidden = {"web-search", "research-assistant"}
    present = forbidden.intersection({skill.name for skill in skills})
    for name in sorted(present):
        errors.append(f"skills/{name}: generic skill should not be present in this repo")
    return errors


def validate_no_scaffold_placeholders(skills: list[Skill]) -> list[str]:
    errors: list[str] = []
    for skill in skills:
        skill_path = SKILLS_DIR / skill.dir_name / "SKILL.md"
        text = read_text(skill_path)
        for snippet in SCAFFOLD_PLACEHOLDER_SNIPPETS:
            if snippet in text:
                errors.append(f"{skill_path.relative_to(REPO_ROOT)}: scaffold placeholder remains: {snippet!r}")
    return errors


def description_terms(skill: Skill) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", skill.description.lower())
    return {
        token
        for token in tokens
        if len(token) >= 4 and token not in DESCRIPTION_STOPWORDS
    }


def similarity_ratio(left: Skill, right: Skill) -> float:
    left_text = re.sub(r"\s+", " ", left.description.lower()).strip()
    right_text = re.sub(r"\s+", " ", right.description.lower()).strip()
    return SequenceMatcher(a=left_text, b=right_text).ratio()


def validate_skill_trigger_overlap(skills: list[Skill]) -> list[str]:
    errors: list[str] = []
    for index, left in enumerate(skills):
        left_terms = description_terms(left)
        for right in skills[index + 1 :]:
            if frozenset({left.name, right.name}) in SIMILARITY_ALLOWLIST:
                continue
            right_terms = description_terms(right)
            if not left_terms or not right_terms:
                continue
            overlap = left_terms & right_terms
            union = left_terms | right_terms
            jaccard = len(overlap) / len(union)
            ratio = similarity_ratio(left, right)
            if jaccard >= 0.68 and ratio >= 0.72:
                errors.append(
                    " / ".join(
                        [
                            f"skills/{left.name}",
                            f"skills/{right.name}",
                            f"trigger overlap looks too high (term overlap={jaccard:.2f}, text similarity={ratio:.2f}); consider merging or tightening descriptions",
                        ]
                    )
                )
    return errors


def validate_skills_list_budget(skills: list[Skill]) -> list[str]:
    total = sum(len(skill.name) + len(skill.description) + len(skill.rel_path) + 10 for skill in skills)
    if total > MAX_INITIAL_SKILLS_LIST_CHARS:
        return [
            "skills list budget exceeded "
            f"({total} chars > {MAX_INITIAL_SKILLS_LIST_CHARS}); shorten descriptions or split shipped skills so the initial discovery list stays compact"
        ]
    return []


def validate_repo_files() -> list[str]:
    errors: list[str] = []
    required = [
        REPO_ROOT / ".dockerignore",
        REPO_ROOT / "SECURITY.md",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"{path.relative_to(REPO_ROOT)}: required repo file is missing")
    return errors


def validate_text_files() -> list[str]:
    errors: list[str] = []
    checks: dict[Path, list[str]] = {
        REPO_ROOT / "README.md": ["docs/install/README.md", "npx skills add kong/skills --skill gateway-plugin-datakit", "supply-chain or security risk", "contributor-facing source of truth", "SECURITY.md"],
        REPO_ROOT / "docs" / "install" / "README.md": [MCP_NAME, MCP_URL, TOKEN_ENV, "gh skill"],
        REPO_ROOT / "docs" / "install" / "cursor.md": [MCP_NAME, MCP_URL, TOKEN_ENV, ".cursor-plugin/plugin.json", "npx skills add kong/skills"],
        REPO_ROOT / "docs" / "install" / "claude-code.md": ["Claude Code", "kong-skills", MCP_NAME],
        REPO_ROOT / "docs" / "install" / "codex.md": ["Codex", "npx skills add kong/skills", MCP_NAME],
        REPO_ROOT / "docs" / "install" / "other-tools.md": ["gh skill install kong/skills", "gh skill preview", "npx skills add kong/skills", MCP_NAME],
        REPO_ROOT / "docs" / "release.md": ["workflow_dispatch", "mise run ci", "mise run artifact:check", "Release OCI Skills Artifact"],
        REPO_ROOT / "docs" / "structure.md": [".cursor-plugin/plugin.json", ".mcp.json", "contributor file map", "CLAUDE.md", "AGENTS.md"],
        REPO_ROOT / "docs" / "developer.md": ["assets/", "references/", "scripts/", "mise install", "mise run preflight", "mise run gen", "mise run deps", "skill:new", "artifact:check", "gh skill publish --dry-run", "Consumers generally see", "GitHub Actions workflow is the only publishing path", "kong-skill-authoring", "description budget", "overlap", ".cursor-plugin/plugin.json"],
        REPO_ROOT / "docs" / "testing.md": ["mise run preflight", "mise run deps", "mise run lint", "mise run artifact:check", "gh skill publish --dry-run", "scratch project", "KONNECT_TOKEN", "docs/install/other-tools.md", "description budget", "overlap", "docs/install/cursor.md"],
        REPO_ROOT / "SECURITY.md": ["vulnerability@konghq.com", "Do not open a public GitHub issue"],
    }
    for path, snippets in checks.items():
        text = read_text(path)
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{path.relative_to(REPO_ROOT)}: missing {snippet!r}")
    return errors


# Compare expected generated content with checked-in files.
def compare_or_write(path: Path, expected: str, fix: bool, errors: list[str]) -> None:
    actual = read_text(path)
    if actual == expected:
        return
    if fix:
        write_text(path, expected)
    else:
        errors.append(f"{path.relative_to(REPO_ROOT)} is out of sync; run `mise run gen`")


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
    compare_or_write(REPO_ROOT / ".agents" / "plugins" / "marketplace.json", dump_json(sync_codex_marketplace(skills)), args.fix, errors)
    compare_or_write(REPO_ROOT / ".claude-plugin" / "marketplace.json", dump_json(sync_claude_marketplace(skills)), args.fix, errors)
    compare_or_write(REPO_ROOT / ".claude-plugin" / "plugin.json", dump_json(sync_claude_plugin(skills)), args.fix, errors)
    compare_or_write(REPO_ROOT / ".codex-plugin" / "plugin.json", dump_json(sync_codex_plugin(skills)), args.fix, errors)
    compare_or_write(REPO_ROOT / ".mcp.json", dump_json(sync_root_mcp()), args.fix, errors)
    compare_or_write(REPO_ROOT / ".cursor-plugin" / "plugin.json", dump_json(sync_cursor_plugin(skills)), args.fix, errors)
    compare_or_write(REPO_ROOT / ".cursor-plugin" / "marketplace.json", dump_json(sync_cursor_marketplace()), args.fix, errors)

    errors.extend(validate_static_metadata())
    errors.extend(validate_skill_contents(skills))
    errors.extend(validate_no_generic_skills(skills))
    errors.extend(validate_no_scaffold_placeholders(skills))
    errors.extend(validate_skill_trigger_overlap(skills))
    errors.extend(validate_skills_list_budget(skills))
    errors.extend(validate_repo_files())
    errors.extend(validate_text_files())

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("repo-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
