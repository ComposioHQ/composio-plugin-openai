#!/usr/bin/env bash
# Add surface-aware guidance when the prompt names a locally cached toolkit.

set -u

CACHE="${TMPDIR:-/tmp}/composio-plugin-toolkits.cache"

[ -f "$CACHE" ] && [ -s "$CACHE" ] || exit 0
command -v composio >/dev/null 2>&1 || exit 0

payload="$(cat)"

if command -v jq >/dev/null 2>&1; then
  prompt="$(printf '%s' "$payload" | jq -r '.prompt // empty' 2>/dev/null)"
else
  prompt=""
fi
[ -n "$prompt" ] || prompt="$payload"

norm="$(printf '%s' "$prompt" \
  | tr '[:upper:]' '[:lower:]' \
  | tr -c 'a-z0-9' ' ')"
norm=" $norm "

matched=0
while IFS= read -r kw; do
  [ -n "$kw" ] || continue
  case "$norm" in
    *" $kw "*) matched=1; break ;;
  esac
done <"$CACHE"

[ "$matched" -eq 1 ] || exit 0

line="You mentioned a service Composio can act on. Use callable, authorized hosted Composio app tools for direct SaaS work. The local Composio CLI is also available; choose it when local files, scripts, pipelines, or reproducible automation matter. If both surfaces fit, choose by task requirements. Never replay an uncertain write through the other surface."

if command -v jq >/dev/null 2>&1; then
  jq -n --arg c "$line" \
    '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:$c}}'
else
  esc="$(printf '%s' "$line" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' "$esc"
fi

exit 0
