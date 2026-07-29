#!/usr/bin/env bash

set -u
cat >/dev/null 2>&1 || true

CACHE="${TMPDIR:-/tmp}/composio-plugin-toolkits.cache"

cache_pid=""
if command -v composio >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  (
    tmp="$(mktemp "${CACHE}.XXXXXX" 2>/dev/null)" || exit 0
    ( composio dev toolkits list --limit 50 2>/dev/null \
        | jq -r '.[] | .slug, .name' \
        | tr '[:upper:]' '[:lower:]' >"$tmp" 2>/dev/null ) &
    fpid=$!
    if wait "$fpid" 2>/dev/null && [ -s "$tmp" ]; then
      mv -f "$tmp" "$CACHE" 2>/dev/null || rm -f "$tmp" 2>/dev/null
    else
      rm -f "$tmp" 2>/dev/null
    fi
  ) &
  cache_pid=$!
fi

# Plugin self-update: converge a stale install to the latest published version.
# SessionStart has an 8s timeout and its stdout is parsed as JSON, so this job
# is fully detached — never waited on, all fds redirected. `codex plugin ...`
# subcommands don't fire hooks (no recursion); the updated version only
# activates at the next session launch. Codex marketplaces are snapshots:
# `marketplace upgrade` refreshes ours, then a re-add installs the newest
# cached version (add is idempotent when already current).
SELF_UPDATE_STATE="${HOME:-}/.composio/plugin-codex-self-update.json"
if [ -n "${HOME:-}" ] && command -v codex >/dev/null 2>&1; then
  now="$(date +%s)"
  last="$(sed -n 's/.*"lastAttempt"[[:space:]]*:[[:space:]]*\([0-9]\{1,\}\).*/\1/p' "$SELF_UPDATE_STATE" 2>/dev/null | head -n 1)"
  if [ -z "$last" ] || [ "$((now - last))" -ge 86400 ]; then
    own_version="$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
      "$(dirname "$0")/../.codex-plugin/plugin.json" 2>/dev/null | head -n 1)"
    (
      # Stamp before updating: doubles as the throttle lock. Concurrent
      # session starts can race past it — worst case two idempotent runs.
      mkdir -p "${SELF_UPDATE_STATE%/*}" || exit 0
      printf '{"lastAttempt":%s,"lastResult":"running"}\n' "$now" >"$SELF_UPDATE_STATE" || exit 0
      result="error"
      if codex plugin marketplace upgrade composio; then
        added="$(codex plugin add composio@composio --json 2>/dev/null \
          | sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
        if [ -n "$added" ]; then
          if [ "$added" = "$own_version" ]; then result="current"; else result="updated"; fi
        fi
      fi
      printf '{"lastAttempt":%s,"lastResult":"%s"}\n' "$now" "$result" >"$SELF_UPDATE_STATE"
    ) >/dev/null 2>&1 </dev/null &
  fi
fi

if ! command -v composio >/dev/null 2>&1; then
  cli_status="The local Composio CLI is not installed. Ask before installing it from https://composio.dev/install, then run \`composio login\`. Until it is available, use hosted Composio app tools when callable."
else
  cli_status="The local Composio CLI is available but is not signed in; run \`composio login\` before choosing it."
  if whoami_output="$(composio whoami 2>&1)" \
      && [ -n "$(printf '%s' "$whoami_output" | tr -d '[:space:]')" ] \
      && ! printf '%s' "$whoami_output" | grep -Eiq \
        '"authenticated"[[:space:]]*:[[:space:]]*false|not[[:space:]-]+logged[[:space:]-]+in'; then
    cli_status="The local Composio CLI is available and signed in."
  fi

  # Upgrade nudge from the CLI's local release cache — never the network.
  # Stable X.Y.Z versions only; anything missing or malformed stays silent.
  update_cache="${HOME:-}/.composio/update-check.json"
  if [ -f "$update_cache" ]; then
    latest="$(sed -n 's/.*"latestVersion"[[:space:]]*:[[:space:]]*"\([0-9]\{1,\}\.[0-9]\{1,\}\.[0-9]\{1,\}\)".*/\1/p' "$update_cache" 2>/dev/null | head -n 1)"
    installed="$(composio version 2>/dev/null | tail -n 1 | tr -d '[:space:]')"
    if [ -n "$latest" ] && [ "$installed" != "$latest" ] \
        && printf '%s' "$installed" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' \
        && [ "$(printf '%s\n%s\n' "$installed" "$latest" \
              | sort -t. -k1,1n -k2,2n -k3,3n | head -n 1)" = "$installed" ]; then
      cli_status="${cli_status} A newer Composio CLI (${latest}) is available — run \`composio upgrade\`."
    fi
  fi
fi

[ -n "$cache_pid" ] && wait "$cache_pid" 2>/dev/null

line="This is a terminal/Codex session. Prefer the local Composio CLI for Composio work, including direct SaaS actions and workflows involving local files, scripts, pipelines, or reproducible automation. ${cli_status} Use callable hosted Composio app tools when the CLI is unavailable, the user explicitly requests them, or the needed capability exists only there. Never automatically retry an uncertain write through the other surface."

if command -v jq >/dev/null 2>&1; then
  jq -n --arg c "$line" \
    '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}'
else
  esc="$(printf '%s' "$line" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
fi

exit 0
