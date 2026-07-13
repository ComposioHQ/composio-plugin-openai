#!/usr/bin/env bash
# Nudge only when the prompt names a toolkit cached by the session hook.

set -u

CACHE="${TMPDIR:-/tmp}/composio-plugin-toolkits.cache"

[ -f "$CACHE" ] && [ -s "$CACHE" ] || exit 0

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

line="You mentioned an app Composio can act on. Resolve the tool just-in-time: \`composio search \"<task>\"\` then \`composio execute\` (managed auth)."

if command -v jq >/dev/null 2>&1; then
  jq -n --arg c "$line" \
    '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:$c}}'
else
  esc="$(printf '%s' "$line" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' "$esc"
fi

exit 0
