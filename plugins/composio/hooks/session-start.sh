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
  cli_status="The local Composio CLI is not available. Use hosted Composio app tools when callable. Install the CLI only if the task needs local files, scripting, pipelines, or reproducible automation: https://composio.dev/install."
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

line="Composio may be available through hosted app tools, the local CLI, or both. Use callable, authorized hosted Composio app tools for direct SaaS reads and actions. Use the local Composio CLI for local files, scripts, pipelines, or reproducible automation. If both are available, choose by task requirements without asking unless the outcome would materially change. Never automatically retry an uncertain write through the other surface. ${cli_status}"

if command -v jq >/dev/null 2>&1; then
  jq -n --arg c "$line" \
    '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}'
else
  esc="$(printf '%s' "$line" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
fi

exit 0
