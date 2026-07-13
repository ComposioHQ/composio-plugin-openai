---
name: composio
description: Route Composio work between the hosted MCP-backed app and the local Composio CLI. Use when a user wants to read or act on external services such as email, calendars, GitHub, Slack, Notion, Linear, Jira, or CRMs; discover an integration or tool; recover a missing connection; combine multiple apps; or automate those actions with local files and scripts.
---

# Composio

Choose a surface from the capabilities available in the current task, then keep the workflow on that surface unless the task itself requires the other one.

## Choose the surface

1. Use callable, authorized hosted Composio app tools for direct SaaS reads and actions. Read [references/mcp.md](references/mcp.md) before using that surface.
2. Use the local Composio CLI when a shell and `composio` are available and the task needs local files, scripts, pipelines, or reproducible automation. Read [references/cli.md](references/cli.md) before using that surface.
3. If both surfaces are available, choose by task requirements. Do not ask the user to choose unless the difference materially changes the outcome.
4. If neither surface is available, explain both setup paths: authorize or enable the hosted app for direct SaaS work, or install and sign in to the CLI for local automation.

Do not tell a user in an MCP-only environment to install the CLI before using callable hosted app tools.

## Execute safely

- For a read, use the narrowest suitable tool and summarize only the requested data.
- For an unknown capability, discover the tool first, inspect its schema, and then execute it.
- For a missing connection, complete authorization on the selected surface and resume the original operation there.
- Before a write, resolve ambiguous recipients, targets, scope, and payload. Once the write is confirmed, execute it exactly once.
- After a timeout or unclear write result, verify the target state or execution status before doing anything else. Never automatically retry an uncertain write through the other surface.
- Reject unbounded destructive work until the user narrows the scope and confirms the affected resources.
- Never expose credentials, tokens, connection secrets, or raw authentication material.
