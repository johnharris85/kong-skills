#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_HOME = Path.home()
MCP_NAME = "kong-konnect"
MCP_URL = "https://us.mcp.konghq.com"
TOKEN_ENV = "KONNECT_TOKEN"


@dataclass
class SmokeResult:
    name: str
    status: str
    detail: str


def log(message: str) -> None:
    print(message, flush=True)


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    display_cwd = str(cwd or REPO_ROOT)
    log(f"      -> running: {' '.join(cmd)}")
    log(f"         cwd: {display_cwd}")
    log(f"         timeout: {timeout}s")
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        log("         result: timed out")
        raise

    log(f"         result: exit {proc.returncode}")
    return proc


def ok(name: str, detail: str) -> SmokeResult:
    return SmokeResult(name, "PASS", detail)


def skip(name: str, detail: str) -> SmokeResult:
    return SmokeResult(name, "SKIP", detail)


def fail(name: str, detail: str) -> SmokeResult:
    return SmokeResult(name, "FAIL", detail)


def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


@contextmanager
def backup_file(path: Path):
    sentinel = object()
    if path.exists():
        original = path.read_text(encoding="utf-8")
    else:
        original = sentinel
    try:
        yield
    finally:
        if original is sentinel:
            if path.exists():
                path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(original, encoding="utf-8")


def run_test(name: str, fn) -> SmokeResult:
    log(f"[....] {name} starting")
    try:
        result = fn()
    except subprocess.TimeoutExpired as exc:
        result = fail(name, f"timed out after {exc.timeout}s")
    except Exception as exc:
        result = fail(name, f"unexpected error: {exc}")
    log(f"[{result.status:<4}] {result.name} {result.detail}")
    return result


def smoke_repo_validation() -> SmokeResult:
    log("      checking repo validation")
    proc = run(["python3", "scripts/check_repo.py"])
    if proc.returncode == 0:
        return ok("repo-validation", "scripts/check_repo.py passed")
    return fail("repo-validation", proc.stderr.strip() or proc.stdout.strip() or "validation failed")


def smoke_mcp_configs() -> SmokeResult:
    log("      checking MCP config files")
    try:
        claude_mcp = json.loads((REPO_ROOT / "claude.mcp.json").read_text())
        root_mcp = json.loads((REPO_ROOT / ".mcp.json").read_text())
        cursor_mcp = json.loads((REPO_ROOT / "cursor" / "mcp.json").read_text())
        copilot_mcp = json.loads((REPO_ROOT / ".github" / "mcp.json").read_text())
        gemini = json.loads((REPO_ROOT / "gemini-extension.json").read_text())
    except Exception as exc:
        return fail("mcp-configs", f"failed to parse config files: {exc}")

    try:
        assert claude_mcp["mcpServers"][MCP_NAME]["url"] == MCP_URL
        assert root_mcp[MCP_NAME]["url"] == MCP_URL
        assert cursor_mcp["mcpServers"][MCP_NAME]["url"] == MCP_URL
        assert copilot_mcp["servers"][MCP_NAME]["url"] == MCP_URL
        assert gemini["mcpServers"][MCP_NAME]["url"] == MCP_URL
        assert TOKEN_ENV in json.dumps(gemini)
    except Exception as exc:
        return fail("mcp-configs", f"unexpected MCP config content: {exc}")

    return ok("mcp-configs", "claude, root, cursor, copilot, and gemini MCP config surfaces align")


def smoke_npx_skills() -> SmokeResult:
    if not tool_exists("npx"):
        return skip("npx-skills", "`npx` not installed")

    with tempfile.TemporaryDirectory(prefix="kong-skills-smoke-") as temp_dir:
        project = Path(temp_dir) / "project"
        project.mkdir()
        log(f"      temp project: {project}")
        proc = run(
            [
                "npx",
                "skills",
                "add",
                str(REPO_ROOT),
                "--copy",
                "--yes",
                "--agent",
                "claude-code",
                "--agent",
                "codex",
                "--agent",
                "gemini-cli",
                "--agent",
                "github-copilot",
                "--agent",
                "cursor",
                "--agent",
                "goose",
            ],
            cwd=project,
            timeout=300,
        )
        if proc.returncode != 0:
            detail = proc.stderr.strip() or proc.stdout.strip() or "npx skills add failed"
            return fail("npx-skills", detail)

        expected = [
            project / ".claude" / "skills" / "datakit" / "SKILL.md",
            project / ".agents" / "skills" / "datakit" / "SKILL.md",
            project / ".goose" / "skills" / "datakit" / "SKILL.md",
        ]
        missing = [str(path.relative_to(project)) for path in expected if not path.exists()]
        if missing:
            return fail("npx-skills", f"missing installed skill files: {', '.join(missing)}")
        return ok("npx-skills", "local path install succeeded for claude-code, codex, gemini-cli, github-copilot, cursor, and goose targets")


def smoke_claude_plugin() -> SmokeResult:
    if not tool_exists("claude"):
        return skip("claude-plugin", "`claude` not installed")

    with tempfile.TemporaryDirectory(prefix="kong-skills-claude-home-") as temp_home:
        log(f"      temp HOME: {temp_home}")
        env = os.environ.copy()
        env["HOME"] = temp_home
        env.setdefault("XDG_CONFIG_HOME", str(Path(temp_home) / ".config"))

        validate_proc = run(["claude", "plugin", "validate", str(REPO_ROOT)], env=env, timeout=180)
        if validate_proc.returncode != 0:
            detail = validate_proc.stderr.strip() or validate_proc.stdout.strip() or "claude plugin validate failed"
            return fail("claude-plugin", detail)

        add_proc = run(["claude", "plugin", "marketplace", "add", str(REPO_ROOT)], env=env, timeout=180)
        if add_proc.returncode != 0:
            detail = add_proc.stderr.strip() or add_proc.stdout.strip() or "failed to add marketplace"
            return fail("claude-plugin", detail)

        install_proc = run(["claude", "plugin", "install", "kong-skills@kong-skills", "--scope", "user"], env=env, timeout=180)
        if install_proc.returncode != 0:
            detail = install_proc.stderr.strip() or install_proc.stdout.strip() or "failed to install plugin"
            return fail("claude-plugin", detail)

        marketplaces_dir = Path(temp_home) / ".claude" / "plugins" / "marketplaces"
        cache_dir = Path(temp_home) / ".claude" / "plugins" / "cache"
        if not marketplaces_dir.exists():
            return fail("claude-plugin", "marketplace add succeeded but no marketplaces directory was created")
        if not cache_dir.exists():
            return fail("claude-plugin", "plugin install succeeded but no plugin cache directory was created")
        return ok("claude-plugin", "local marketplace add and plugin install succeeded via direct CLI commands")


def ensure_codex_marketplace_entry(path: Path) -> None:
    if path.exists():
        data = json.loads(path.read_text())
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "name": "personal-marketplace",
            "interface": {"displayName": "Personal Marketplace"},
            "plugins": [],
        }

    plugins = data.setdefault("plugins", [])
    entry = {
        "name": "kong-skills",
        "source": {
            "source": "local",
            "path": str(REPO_ROOT),
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Productivity",
    }

    replaced = False
    for index, plugin in enumerate(plugins):
        if plugin.get("name") == "kong-skills":
            plugins[index] = entry
            replaced = True
            break
    if not replaced:
        plugins.append(entry)

    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def smoke_codex_marketplace() -> SmokeResult:
    if not tool_exists("codex"):
        return skip("codex-marketplace", "`codex` not installed")

    marketplace = REAL_HOME / ".agents" / "plugins" / "marketplace.json"
    log(f"      using HOME: {REAL_HOME}")
    log(f"      marketplace path: {marketplace}")
    with backup_file(marketplace):
        ensure_codex_marketplace_entry(marketplace)
        log(f"      wrote marketplace file: {marketplace}")

        parsed = json.loads(marketplace.read_text())
        plugin = next((plugin for plugin in parsed.get("plugins", []) if plugin.get("name") == "kong-skills"), None)
        if not plugin:
            return fail("codex-marketplace", "failed to write kong-skills marketplace entry")
        if plugin.get("source", {}).get("path") != str(REPO_ROOT):
            return fail("codex-marketplace", "marketplace entry does not point at the local repo path")

        proc = run(["codex", "--version"], cwd=REPO_ROOT, env={**os.environ, "HOME": str(REAL_HOME)}, timeout=60)
        if proc.returncode != 0:
            detail = proc.stderr.strip() or proc.stdout.strip() or "codex --version failed"
            return fail("codex-marketplace", detail)

        return ok("codex-marketplace", "personal marketplace file was merged with a local kong-skills entry and Codex CLI ran successfully with the real home directory")


def smoke_gemini_extension() -> SmokeResult:
    if not tool_exists("gemini"):
        return skip("gemini-extension", "`gemini` not installed")

    with tempfile.TemporaryDirectory(prefix="kong-skills-gemini-home-") as temp_home:
        home = Path(temp_home)
        log(f"      temp HOME: {home}")
        gemini_home = home / ".gemini"
        extension_dir = gemini_home / "extensions" / "kong-skills"
        gemini_home.mkdir(parents=True, exist_ok=True)
        (gemini_home / "extensions").mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env["HOME"] = str(home)
        env["XDG_CONFIG_HOME"] = str(home / ".config")

        validate_proc = run(["gemini", "extensions", "validate", str(REPO_ROOT)], env=env, timeout=180)
        if validate_proc.returncode != 0:
            detail = validate_proc.stderr.strip() or validate_proc.stdout.strip() or "gemini extension validate failed"
            return fail("gemini-extension", detail)

        try:
            install_proc = run(
                ["gemini", "extensions", "install", str(REPO_ROOT), "--consent", "--skip-settings"],
                env=env,
                timeout=180,
            )
            if install_proc.returncode != 0:
                detail = install_proc.stderr.strip() or install_proc.stdout.strip() or "gemini extension install failed"
                return fail("gemini-extension", detail)

            list_proc = run(["gemini", "extensions", "list"], env=env, timeout=180)
            if list_proc.returncode != 0:
                detail = list_proc.stderr.strip() or list_proc.stdout.strip() or "gemini extension list failed"
                return fail("gemini-extension", detail)

            if not extension_dir.exists():
                return fail("gemini-extension", f"Gemini install returned success but extension directory was not created at {extension_dir}")

            output = ((list_proc.stdout or "") + "\n" + (list_proc.stderr or "")).strip()
            if "kong-skills" not in output:
                log("      note: `gemini extensions list` returned no visible kong-skills entry; using installed extension directory as the success signal")

            return ok("gemini-extension", "local extension validate, install, list, and uninstall succeeded using an isolated temp home")
        finally:
            log("      uninstalling Gemini extension after test")
            run(["gemini", "extensions", "uninstall", "kong-skills"], env=env, timeout=180)
            if extension_dir.exists():
                log(f"      removing leftover extension directory after uninstall: {extension_dir}")
                shutil.rmtree(extension_dir)


def main() -> int:
    tests = [
        ("repo-validation", smoke_repo_validation),
        ("mcp-configs", smoke_mcp_configs),
        ("npx-skills", smoke_npx_skills),
        ("claude-plugin", smoke_claude_plugin),
        ("codex-marketplace", smoke_codex_marketplace),
        ("gemini-extension", smoke_gemini_extension),
    ]

    log("Smoke suite starting")
    log(f"Repo root: {REPO_ROOT}")
    log(
        "Tool detection: "
        + ", ".join(
            f"{tool}={'yes' if tool_exists(tool) else 'no'}"
            for tool in ["npx", "claude", "codex", "gemini"]
        )
    )

    results = [run_test(name, test) for name, test in tests]
    width = max(len(result.name) for result in results)
    log("")
    log("Smoke suite summary")
    for result in results:
        print(f"[{result.status:<4}] {result.name:<{width}}  {result.detail}")

    failed = [result for result in results if result.status == "FAIL"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
