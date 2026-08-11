# OpenAI plugin execution

Use this guide when the canonical `composio` skill is bundled with the official OpenAI plugin. The plugin supplies hosted Composio app tools; Codex environments may also have the local Composio CLI.

## Choose one execution surface

1. In ChatGPT web, Work, mobile, or another environment without a usable terminal, use callable and authorized hosted Composio app tools.
2. In a terminal or Codex environment, prefer a signed-in local Composio CLI for direct SaaS actions and workflows involving local files, scripts, pipelines, or reproducible automation.
3. When both surfaces are available, keep the workflow on the selected surface unless the user explicitly requests the other one or the required capability exists only there.
4. When neither surface is available, explain the smallest applicable setup: enable or authorize the hosted app, or ask before installing the CLI and then run `composio login`.

Do not tell a hosted-only user to install the CLI when the plugin's app tools can complete the task.

## Hosted app workflow

1. Call a known capability directly.
2. For an unknown capability, discover the narrowest tool and inspect its schema before execution.
3. When a connection is missing, use the hosted connection-management flow, let the user authorize it, and resume the original operation.
4. Parallelize independent reads only. Resolve dependent inputs before later calls.
5. Before a write, resolve the exact target, scope, and payload. Execute it once and report the returned identifier or URL.

The hosted tool descriptions and schemas are the source of truth. Do not assume fixed tool names.

## Local CLI workflow

For a generic app outcome selected by the canonical skill:

1. Run a known tool slug with `composio execute`.
2. Discover an unknown capability with `composio search`, inspect the schema, and return to `composio execute`.
3. Use `composio link <toolkit>` when a connection is missing, then resume the original task.
4. Use `composio run` for control flow, loops, and local output handling. Use `composio proxy` only when a dedicated tool does not cover the authenticated API operation.

Use the separate `composio-cli` skill, when available, for detailed CLI installation, flags, commands, scripting, developer mode, triggers, and troubleshooting.

## Safety boundary

- Use the narrowest read that answers the request.
- Never expose credentials, tokens, connection secrets, or raw authentication material.
- Confirm ambiguous recipients, targets, scope, and payload before consequential writes.
- After a timeout or unclear write result, verify the target state or execution status with a non-mutating read.
- Never replay an uncertain write through the other surface.
- Reject unbounded destructive work until the user narrows and confirms the affected resources.
