#!/usr/bin/env bash
# Fails when plugins/** changed relative to the merge-base with <base-ref>
# but the plugin.json version was not bumped.
# Usage: scripts/check-version-bump.sh <base-ref>   (e.g. origin/main)
set -euo pipefail

PLUGIN_JSON="plugins/composio/.codex-plugin/plugin.json"
BASE_REF="${1:?usage: check-version-bump.sh <base-ref>}"

merge_base="$(git merge-base "$BASE_REF" HEAD)"

if git diff --quiet "$merge_base" HEAD -- plugins/; then
  echo "No changes under plugins/ vs merge-base $merge_base; version bump not required."
  exit 0
fi

version_at() {
  local content
  content="$(git show "$1:$PLUGIN_JSON" 2>/dev/null)" || return 1
  printf '%s' "$content" | python3 -c 'import json, sys; print(json.load(sys.stdin)["version"])'
}

head_version="$(version_at HEAD)"
if ! printf '%s' "$head_version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "::error::$PLUGIN_JSON version '$head_version' is not X.Y.Z semver."
  exit 1
fi

if ! base_version="$(version_at "$merge_base")"; then
  echo "$PLUGIN_JSON absent at merge-base; accepting initial version $head_version."
  exit 0
fi

if [ "$head_version" = "$base_version" ]; then
  echo "::error::plugins/** changed but $PLUGIN_JSON version is still $base_version. Plugin updates only propagate on a version bump — bump the version in this PR."
  exit 1
fi

if [ "$(printf '%s\n%s\n' "$base_version" "$head_version" | sort -V | tail -n1)" != "$head_version" ]; then
  echo "::error::$PLUGIN_JSON version went backwards: $base_version -> $head_version."
  exit 1
fi

echo "Version bump OK: $base_version -> $head_version"
