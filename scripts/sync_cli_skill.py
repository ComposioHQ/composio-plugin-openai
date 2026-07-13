#!/usr/bin/env python3
"""Build and verify the vendored Composio CLI skill from a release tag."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "plugins" / "composio" / "skills" / "composio-cli"
LOCK_PATH = ROOT / "skill-source.json"
DEFAULT_SOURCE_REPO = ROOT.parent / "composio"
REPOSITORY = "ComposioHQ/composio"
SOURCE_PATH = "ts/packages/cli/skills-src/composio-cli"
CHANNEL = "stable"


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{detail}")
    return result.stdout.strip()


def extract_source_archive(archive_path: Path, target: Path) -> None:
    with tarfile.open(archive_path) as archive:
        for member in archive.getmembers():
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"Unsafe source archive path: {member.name}")
            base = ("ts", "packages", "cli")
            is_parent_directory = member.isdir() and base[: len(relative.parts)] == relative.parts
            if relative.parts[:3] != base and not is_parent_directory:
                raise RuntimeError(f"Unexpected source archive path: {member.name}")
            if member.issym() or member.islnk() or member.isdev() or member.isfifo():
                raise RuntimeError(f"Unsupported source archive entry: {member.name}")

            destination = target.joinpath(*relative.parts)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise RuntimeError(f"Unsupported source archive entry: {member.name}")

            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"Could not read source archive entry: {member.name}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            destination.chmod(0o644)


def find_tsx(source_repo: Path) -> Path:
    candidates = (
        source_repo / "node_modules" / ".bin" / "tsx",
        source_repo / "ts" / "packages" / "cli" / "node_modules" / ".bin" / "tsx",
    )
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise RuntimeError(
        f"tsx is unavailable in {source_repo}; install the Composio monorepo dependencies first"
    )


def build_skill(source_repo: Path, tag: str, workdir: Path) -> tuple[Path, str]:
    if not (source_repo / ".git").exists():
        raise RuntimeError(f"Not a Composio source checkout: {source_repo}")

    commit = run(["git", "rev-parse", f"{tag}^{{commit}}"], source_repo)
    archive_path = workdir / "source.tar"
    run(
        [
            "git",
            "archive",
            "--format=tar",
            f"--output={archive_path}",
            tag,
            "ts/packages/cli/scripts/build-skills.ts",
            "ts/packages/cli/skills-src/composio-cli",
            "ts/packages/cli/src/experimental-features.ts",
        ],
        source_repo,
    )

    source_root = workdir / "source"
    source_root.mkdir()
    extract_source_archive(archive_path, source_root)
    cli_root = source_root / "ts" / "packages" / "cli"
    output_root = workdir / "output"
    run(
        [
            str(find_tsx(source_repo)),
            "scripts/build-skills.ts",
            "--channel",
            CHANNEL,
            "--output-dir",
            str(output_root),
        ],
        cli_root,
    )

    skill = output_root / "composio-cli"
    skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
    if f"release-channel: {CHANNEL}" not in skill_text:
        raise RuntimeError(f"Generated skill is not from the {CHANNEL} channel")
    return skill, commit


def write_lock(tag: str, commit: str, tree_sha: str) -> None:
    lock = {
        "repository": REPOSITORY,
        "releaseTag": tag,
        "sourceCommit": commit,
        "sourcePath": SOURCE_PATH,
        "channel": CHANNEL,
        "treeSha256": tree_sha,
    }
    temporary = LOCK_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, LOCK_PATH)


def update(tag: str, source_repo: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="composio-cli-skill-") as tmpdir:
        skill, commit = build_skill(source_repo, tag, Path(tmpdir))
        tree_sha = tree_sha256(skill)
        if DESTINATION.exists():
            shutil.rmtree(DESTINATION)
        shutil.copytree(skill, DESTINATION)

    write_lock(tag, commit, tree_sha)
    print(f"Updated {DESTINATION.relative_to(ROOT)} from {tag} ({CHANNEL})")


def check() -> None:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    expected_metadata = {
        "repository": REPOSITORY,
        "sourcePath": SOURCE_PATH,
        "channel": CHANNEL,
    }
    for key, expected in expected_metadata.items():
        if lock.get(key) != expected:
            raise RuntimeError(f"skill-source.json has an invalid {key}")
    if not DESTINATION.is_dir():
        raise RuntimeError(f"Vendored skill is missing: {DESTINATION}")
    actual = tree_sha256(DESTINATION)
    expected = lock.get("treeSha256")
    if actual != expected:
        raise RuntimeError(f"Vendored skill checksum mismatch: expected {expected}, got {actual}")
    print(f"Verified {DESTINATION.relative_to(ROOT)} at {lock['releaseTag']} ({CHANNEL})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="verify the checked-in skill")
    action.add_argument("--update", metavar="TAG", help="build the skill from a release tag")
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=DEFAULT_SOURCE_REPO,
        help=f"Composio source checkout (default: {DEFAULT_SOURCE_REPO})",
    )
    args = parser.parse_args()

    if args.update:
        update(args.update, args.source_repo.resolve())
    else:
        check()


if __name__ == "__main__":
    main()
