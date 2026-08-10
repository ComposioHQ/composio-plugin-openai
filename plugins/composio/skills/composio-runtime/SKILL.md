---
name: composio-runtime
description: Route Composio work between the hosted MCP-backed app and the local Composio CLI, then execute it safely. Use when the OpenAI Composio plugin is available and a user wants to act on connected apps, discover a tool, recover a connection, combine services, or automate app work with local files and scripts.
---

# Composio runtime

Choose a surface from the capabilities available in the current task, then keep the workflow on that surface unless the task itself requires the other one.

## Choose the surface

1. In a terminal or Codex environment, prefer the local Composio CLI for Composio work. If `composio` is missing, explain how to install and sign in before choosing it; do not install software without user approval. Read [references/cli.md](references/cli.md) before using that surface.
2. In ChatGPT web/app or another environment without a usable terminal, use callable, authorized hosted Composio app tools. Read [references/mcp.md](references/mcp.md) before using that surface.
3. If both surfaces are available in a terminal or Codex environment, use the CLI unless the user explicitly requests the hosted surface or the required capability exists only there.
4. If neither surface is available, explain both setup paths: authorize or enable the hosted app for ChatGPT work, or install and sign in to the CLI for terminal automation.

Do not tell a user in ChatGPT web/app or another hosted-only environment to install the CLI before using callable hosted app tools.

## Execute safely

- For a read, use the narrowest suitable tool and summarize only the requested data.
- For an unknown capability, discover the tool first, inspect its schema, and then execute it.
- For a missing connection, complete authorization on the selected surface and resume the original operation there.
- Before a write, resolve ambiguous recipients, targets, scope, and payload. Once the write is confirmed, execute it exactly once.
- After a timeout or unclear write result, verify the target state or execution status before doing anything else. Never automatically retry an uncertain write through the other surface.
- Reject unbounded destructive work until the user narrows the scope and confirms the affected resources.
- Never expose credentials, tokens, connection secrets, or raw authentication material.
