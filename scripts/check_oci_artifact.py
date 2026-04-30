#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
DOCKERFILE = REPO_ROOT / "Dockerfile.skills"
DEFAULT_IMAGE_TAG = "kong-skills:local-check"


def run(*args: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def capture(*args: str) -> str:
    return run(*args, capture_output=True).stdout.strip()


def current_git_sha() -> str:
    return capture("git", "rev-parse", "HEAD")


def build_image(image_tag: str, version: str, revision: str, repo_url: str) -> None:
    run(
        "docker",
        "build",
        "-f",
        str(DOCKERFILE),
        "-t",
        image_tag,
        "--build-arg",
        f"APP_VERSION={version}",
        "--build-arg",
        "BUILD_DATETIME=1970-01-01T00:00:00Z",
        "--build-arg",
        f"GIT_COMMIT={revision}",
        "--build-arg",
        f"REPO_URL={repo_url}",
        ".",
    )


def inspect_labels(image_tag: str) -> dict[str, str]:
    raw = capture("docker", "image", "inspect", image_tag)
    data = json.loads(raw)
    if not isinstance(data, list) or not data:
        raise ValueError(f"failed to inspect image {image_tag}")
    labels = data[0].get("Config", {}).get("Labels", {})
    if not isinstance(labels, dict):
        raise ValueError(f"image {image_tag} labels are not a mapping")
    return {str(key): str(value) for key, value in labels.items()}


def extract_image_rootfs(image_tag: str, destination: Path) -> None:
    container_id = capture("docker", "create", image_tag)
    try:
        run("docker", "cp", f"{container_id}:/.", str(destination))
    finally:
        subprocess.run(
            ("docker", "rm", "-f", container_id),
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )


def host_skill_files() -> list[Path]:
    return sorted(path for path in SKILLS_DIR.rglob("*") if path.is_file())


def image_skill_files(extracted_root: Path) -> list[Path]:
    return sorted(path for path in extracted_root.rglob("*") if path.is_file())


def assert_expected_layout(extracted_root: Path) -> None:
    if (extracted_root / "skills").exists():
        raise ValueError("artifact should contain skill directories at the root, not a top-level skills/ directory")

    expected_dirs = sorted(path.name for path in SKILLS_DIR.iterdir() if path.is_dir())
    actual_dirs = sorted(path.name for path in extracted_root.iterdir() if path.is_dir())
    if actual_dirs != expected_dirs:
        raise ValueError(f"top-level directories differ: expected {expected_dirs}, got {actual_dirs}")


def compare_file_contents(extracted_root: Path) -> None:
    expected_files = host_skill_files()
    actual_files = image_skill_files(extracted_root)

    expected_rel = sorted(path.relative_to(SKILLS_DIR) for path in expected_files)
    actual_rel = sorted(path.relative_to(extracted_root) for path in actual_files)
    if actual_rel != expected_rel:
        raise ValueError(
            f"artifact file set differs from repo skills directory:\nexpected={expected_rel}\nactual={actual_rel}"
        )

    for rel_path in expected_rel:
        source = SKILLS_DIR / rel_path
        extracted = extracted_root / rel_path
        if source.read_bytes() != extracted.read_bytes():
            raise ValueError(f"file content mismatch for {rel_path}")


def validate_labels(labels: dict[str, str], version: str, revision: str, repo_url: str) -> None:
    expected = {
        "org.opencontainers.image.version": version,
        "org.opencontainers.image.revision": revision,
        "org.opencontainers.image.source": repo_url,
        "org.opencontainers.image.title": "kong-skills OCI volume",
    }
    for key, value in expected.items():
        actual = labels.get(key)
        if actual != value:
            raise ValueError(f"label {key} mismatch: expected {value!r}, got {actual!r}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and validate the local OCI skills artifact image.")
    parser.add_argument("--version", default="dev", help="Artifact version label to embed. Default: dev")
    parser.add_argument(
        "--image-tag",
        default=DEFAULT_IMAGE_TAG,
        help=f"Local Docker image tag to build. Default: {DEFAULT_IMAGE_TAG}",
    )
    parser.add_argument(
        "--revision",
        default=current_git_sha(),
        help="Git revision label to embed. Default: current HEAD",
    )
    parser.add_argument(
        "--repo-url",
        default="https://github.com/kong-konnect/kong-skills",
        help="Source repository URL label to embed.",
    )
    parser.add_argument(
        "--keep-image",
        action="store_true",
        help="Keep the local image after validation instead of deleting it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if shutil.which("docker") is None:
        print("docker is required to build and validate the OCI artifact", file=sys.stderr)
        return 1

    build_image(args.image_tag, args.version, args.revision, args.repo_url)
    try:
        labels = inspect_labels(args.image_tag)
        validate_labels(labels, args.version, args.revision, args.repo_url)

        with tempfile.TemporaryDirectory() as tmpdir:
            extracted_root = Path(tmpdir)
            extract_image_rootfs(args.image_tag, extracted_root)
            assert_expected_layout(extracted_root)
            compare_file_contents(extracted_root)

        print(f"validated OCI artifact {args.image_tag}")
        return 0
    finally:
        if not args.keep_image:
            subprocess.run(
                ("docker", "image", "rm", "-f", args.image_tag),
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )


if __name__ == "__main__":
    raise SystemExit(main())
