#!/usr/bin/env bash
# Add Composio session context and refresh the prompt hook's toolkit cache.

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
  auth="Install the CLI: curl -fsSL https://composio.dev/install | bash, then composio login."
else
  auth="Run \`composio login\` to connect."
  if whoami_output="$(composio whoami 2>&1)" \
      && [ -n "$(printf '%s' "$whoami_output" | tr -d '[:space:]')" ] \
      && ! printf '%s' "$whoami_output" | grep -Eiq \
        '"authenticated"[[:space:]]*:[[:space:]]*false|not[[:space:]-]+logged[[:space:]-]+in'; then
    auth="You're signed in to Composio."
  fi
fi

[ -n "$cache_pid" ] && wait "$cache_pid" 2>/dev/null

line="Composio is available in this session. For any task involving an external app or service (email, calendar, GitHub, Slack, CRMs, docs — 1,000+ apps), resolve the tool just-in-time with \`composio search \"<task>\"\`, then run it with \`composio execute\`. Auth is fully managed. ${auth} Run \`composio --help\` for full usage; install detailed Codex guidance with \`composio --install-skill composio-cli codex\`."

if command -v jq >/dev/null 2>&1; then
  jq -n --arg c "$line" \
    '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}'
else
  esc="$(printf '%s' "$line" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
fi

exit 0
