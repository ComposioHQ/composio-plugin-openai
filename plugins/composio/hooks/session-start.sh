#!/usr/bin/env bash
# Add surface-neutral Composio context and refresh the local CLI toolkit cache.

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
