#!/usr/bin/env python3
"""Validate the plugin's shared contract with the canonical product skill."""

import argparse
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCAL_SKILL = ROOT / "plugins" / "composio" / "skills" / "composio"
PROVENANCE = LOCAL_SKILL / "provenance.json"


def fail(message):
    print(f"::error::{message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("upstream_root", type=pathlib.Path)
    parser.add_argument("--expect-pinned", action="store_true")
    args = parser.parse_args()

    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    source = provenance["source"]
    upstream_root = args.upstream_root.resolve()
    upstream_skill = upstream_root / source["path"]
    if not upstream_skill.is_file():
        fail(f"Canonical skill is missing: {upstream_skill}")

    if args.expect_pinned:
        result = subprocess.run(
            ["git", "-C", str(upstream_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        actual_commit = result.stdout.strip()
        if actual_commit != source["commit"]:
            fail(
                "Canonical checkout does not match provenance pin: "
                f"expected {source['commit']}, got {actual_commit}"
            )

    upstream_text = upstream_skill.read_text(encoding="utf-8")
    local_text = (LOCAL_SKILL / "SKILL.md").read_text(encoding="utf-8")
    failures = []
    for contract in provenance["sharedContracts"]:
        if contract["sourceContains"] not in upstream_text:
            failures.append(f"{contract['id']}: canonical source contract changed")
        if contract["localContains"] not in local_text:
            failures.append(f"{contract['id']}: plugin contract changed")

    if failures:
        fail("Shared skill contract drifted:\n- " + "\n- ".join(failures))

    print(
        f"Shared skill contract passed ({len(provenance['sharedContracts'])} checks; "
        f"relationship={provenance['relationship']})."
    )


if __name__ == "__main__":
    main()
