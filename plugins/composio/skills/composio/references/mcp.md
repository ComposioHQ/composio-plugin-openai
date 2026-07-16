# Hosted Composio app

Use this path in ChatGPT web/app, when no usable terminal exists, or when the user explicitly requests the hosted surface. The runtime's tool descriptions and schemas are the source of truth; do not assume fixed tool names.

## Workflow

1. For a known capability, call the matching read or action tool directly.
2. For an unknown capability, use the available Composio tool-discovery operation, choose the narrowest match, and inspect its input schema when needed.
3. If execution reports a missing connection, use the hosted connection-management operation, let the user authorize, poll when the surface supports it, and resume the original call.
4. For multi-app reads, keep independent calls on the hosted surface and parallelize only when their inputs do not depend on one another.
5. For a write, confirm the exact target and payload, make one execution call, and report the returned identifier or URL.

## Failure boundaries

- If a read fails safely, correct its inputs or select a better tool and try again.
- If a write times out or returns an unclear result, use a non-mutating lookup or execution-status operation to verify the outcome.
- Do not replay an uncertain hosted write through the CLI.
- Do not request CLI installation when the hosted surface can complete the task.
