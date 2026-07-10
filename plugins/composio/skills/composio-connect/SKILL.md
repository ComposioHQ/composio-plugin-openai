---
name: composio-connect
description: Use already-connected Composio app or MCP tools to discover, connect, and run actions across supported apps. Trigger only when Composio tools are present in the current ChatGPT or Codex session.
---

# Composio Connect

Use Composio to complete app work rather than merely explaining how a user could do it. This skill describes the connected-app workflow; it does not install or authenticate an MCP server.

## Default workflow

1. Translate the request into the smallest set of app operations and identify which are reads, writes, or destructive actions.
2. Call `COMPOSIO_SEARCH_TOOLS` once with all related operations when tool slugs are unknown. Prefer a single batched discovery call over one search per app.
3. Use `COMPOSIO_GET_TOOL_SCHEMAS` only when the search result does not provide enough input detail. Never guess required fields.
4. If an app is not connected, use `COMPOSIO_MANAGE_CONNECTIONS` to start authorization, show the returned authorization link to the user, and use `COMPOSIO_WAIT_FOR_CONNECTIONS` before retrying.
5. Execute independent operations together with `COMPOSIO_MULTI_EXECUTE_TOOL`. Preserve dependency order when one result supplies another operation's input.
6. Use `COMPOSIO_REMOTE_WORKBENCH` for loops, joins, bulk transformations, or large tool responses. Use `COMPOSIO_REMOTE_BASH_TOOL` only when shell-based file processing is genuinely useful.
7. Inspect tool results and report what actually happened. Never claim an action succeeded from a plan, preview, or authorization response.

## Safety and user intent

- Read-only discovery may proceed when it is necessary to answer the request.
- Before an external communication, deletion, purchase, permission change, or other consequential action, confirm the user supplied the intended target and material content. Ask a focused clarification when either is missing.
- Treat broad destructive requests such as “delete everything” as underspecified. Narrow the scope and obtain explicit confirmation.
- Do not expose access tokens, authorization secrets, raw credential payloads, or unrelated personal data.
- If authorization fails or the requested app is unavailable, state the limitation and give the smallest recovery step. Do not invent results.

## Efficient cross-app patterns

For a workflow such as “find new GitHub issues and create Linear tickets”:

1. Search for the GitHub read operation and Linear write operation together.
2. Connect either toolkit if needed.
3. Fetch the source issues.
4. Map only the requested fields into ticket inputs.
5. Create tickets, parallelizing independent writes when safe.
6. Return created ticket identifiers and any per-item failures.

When the user requests a preview or draft, stop before the write operation and present the proposed payload.

## Tool availability

Use this workflow only when the current session already exposes Composio tools such as `COMPOSIO_SEARCH_TOOLS`. If they are absent:

- In local Codex, use the `composio-cli` skill and the authenticated `composio` binary instead.
- In ChatGPT or hosted Codex, tell the user that the connected Composio app must be installed or authorized.

Do not request, export, or persist `COMPOSIO_API_KEY` as a workaround. App authentication belongs to the platform app binding, while local authentication belongs to the Composio CLI.
