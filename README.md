# Composio for ChatGPT and Codex

[![CI](https://github.com/ComposioHQ/composio-plugin-openai/actions/workflows/ci.yml/badge.svg)](https://github.com/ComposioHQ/composio-plugin-openai/actions/workflows/ci.yml)
&nbsp;[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

Composio connects agents to [1,000+ apps](https://composio.dev/toolkits), including Google Workspace, Slack, GitHub, Notion, Linear, Jira, and HubSpot. This plugin combines two complementary surfaces:

- The hosted Composio app provides MCP-backed tools for direct SaaS reads and actions with managed authentication.
- The local [Composio CLI](https://docs.composio.dev/docs/cli) handles workflows that need local files, scripts, pipelines, or reproducible automation.

The bundled skill chooses between them from the capabilities available in the task. An uncertain write is never retried automatically through the other surface.

## What you can do

- Read and act on connected apps without installing a local CLI when hosted app tools are available.
- Discover an unfamiliar capability, authorize a missing connection, and resume the original task.
- Use local files in uploads and scripted cross-app workflows through the CLI.
- Combine multiple services while keeping confirmed writes single-execution and destructive work bounded.

## Install

Add the marketplace and install the plugin:

```bash
codex plugin marketplace add ComposioHQ/composio-plugin-openai
codex plugin add composio@composio
```

Start a new task after installation so the app and skill are loaded. Open `/hooks` and review the two Composio hooks before trusting them; the hooks report local CLI state and provide surface-neutral routing guidance.

The CLI is optional for hosted app workflows. Install it only when local automation is useful:

```bash
curl -fsSL https://composio.dev/install | bash
composio login
```

## What's included

| Component | Purpose |
|---|---|
| `.app.json` | Points the plugin at the team-owned Composio developer-mode app. |
| `skills/composio` | Routes work by capability and defines safety boundaries across hosted app and CLI surfaces. |
| `skills/composio/references/mcp.md` | Covers hosted discovery, connection recovery, execution, and uncertain-write handling. |
| `skills/composio/references/cli.md` | Covers local discovery, execution, files, scripting, and auth. |
| `hooks/session-start.sh` | Reports local CLI availability and authentication without forcing it over the hosted app. |
| `hooks/user-prompt-submit.sh` | Adds a short surface-aware nudge for recognized services. |

## Routing examples

- “What is on my calendar tomorrow?” uses the hosted app when its tools are callable and authorized.
- “Upload this local report and keep the workflow as a script” uses the CLI when it is available.
- “Create this confirmed issue” executes once on the selected surface and returns the created identifier.
- If a write times out, the next step is a read or status check, not replaying it through the other surface.

## Local development

Run the package tests:

```bash
python3 -m unittest discover -s tests -v
```

For a local checkout, add this repository as a marketplace, install the plugin, and start a new task:

```bash
codex plugin marketplace add .
codex plugin add composio@composio
```

A working local app install requires the real `plugin_asdk_app...` ID in `plugins/composio/.app.json`; the public submission uses the production MCP URL rather than that developer-mode ID.

## License

MIT — see [LICENSE](./LICENSE).
