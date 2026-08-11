# Composio For You

Use this product when someone wants their own AI client or terminal agent to use their own connected apps. Route by task: answer a question, configure an MCP client, operate through the CLI, connect an app, or debug an existing setup.

## Stable product contract

- MCP endpoint: `https://connect.composio.dev/mcp`
- Consumer key when a client needs a header: `ck_...`
- Header name: `x-consumer-api-key`
- Key location: Dashboard → For You → AI Clients → select the client

The removed `mcp.composio.dev` endpoint and Platform MCP URLs are not substitutes. The `ck_...` key and Platform's `COMPOSIO_API_KEY` are not interchangeable.

## Choose MCP or CLI

Default to MCP for desktop and hosted AI clients. Use the CLI for terminal agents that can execute commands and operate tools directly.

### Know what each surface installs

These surfaces are complementary. Installing one does not automatically install the others.

| Surface | What the agent discovers |
|---|---|
| Raw Composio MCP connection | Callable tools and their schemas. MCP does not install an agent skill. |
| Standalone `composio` skill | The canonical product-and-job router for clients outside the OpenAI plugin. Install it explicitly from `ComposioHQ/composio`. |
| Composio CLI | The `composio` command plus the separately maintained `composio-cli` skill when the CLI's agent setup flow installs it. That skill owns current command usage. |
| OpenAI plugin | The hosted Composio app plus a bundled snapshot of the canonical `composio` skill. This is the supported installation for ChatGPT and Codex plugin users. |
| Claude Code plugin | Commands and hooks. It does not bundle a skill; CLI login/setup installs `composio-cli` separately. |

The OpenAI-bundled and standalone `composio` copies are two distributions of the same semantic skill. Do not install both on the same OpenAI surface. Use `composio` for product selection, integrations, and generic app outcomes. Use `composio-cli` for CLI-specific installation, commands, scripting, development, and troubleshooting. The canonical skill may still select the CLI to execute a generic app task.

### MCP clients

Claude Desktop and ChatGPT use browser OAuth and do not need a consumer key. Header-based clients use the endpoint and header above.

Client configuration changes over time. Before giving client-specific steps, fetch the current source of truth:

```text
https://docs.composio.dev/docs/composio-connect.md
```

For any other MCP-capable client, configure HTTP transport with the endpoint and, when required, the `x-consumer-api-key` header. Keep credentials out of committed configuration.

### Terminal agents

Install and authenticate the CLI only when the task needs it:

```bash
curl -fsSL https://composio.dev/install | bash
composio login
```

For a real task:

```bash
composio search "<what the user wants>"
composio link <toolkit>
composio execute <TOOL_SLUG> -d '{...}'
```

Use `composio login --no-wait | jq` when the agent cannot open a browser. Give the returned login URL to the user and complete authentication with the returned key. Once installed, prefer the bundled `composio-cli` skill for current command and flag details.

## Connect apps when the task needs them

Do not pre-connect every app. Start the requested task. When an integration is required, Composio returns an authorization link and the connection persists for future runs.

For setup or an operational request, verify the selected path with one safe real call when authorization is available. For a question or configuration explanation, answer it without forcing execution.

## Debugging

First confirm that the client is connected to the correct MCP endpoint or that the CLI is authenticated. Then get the Composio log or request ID and read [Errors and provider gotchas](errors.md).

Common product-specific checks:

- If MCP tools do not appear, confirm the connector is enabled, clear its cache when the client supports that, and reconnect it.
- If browser OAuth repeatedly selects the wrong account, retry in a clean browser profile with one Composio account signed in.
- If an authorization link expired, request a new link rather than reusing it.
- If a connected app action returns an auth error, reconnect that app and retry without regenerating the consumer key.

Manage connections in Dashboard → For You → Connect Apps. Manage consumer keys and MCP or CLI sessions in Settings → Sessions & API Key.
