# Composio for ChatGPT and Codex

[![CI](https://github.com/ComposioHQ/composio-plugin-openai/actions/workflows/ci.yml/badge.svg)](https://github.com/ComposioHQ/composio-plugin-openai/actions/workflows/ci.yml)
&nbsp;[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

Composio connects agents to [1,000+ apps](https://composio.dev/toolkits), including Google Workspace, Slack, GitHub, Notion, Linear, Jira, and HubSpot. This plugin combines two complementary surfaces:

- The hosted Composio app provides MCP-backed tools for direct SaaS reads and actions with managed authentication.
- The local [Composio CLI](https://docs.composio.dev/docs/cli) handles workflows that need local files, scripts, pipelines, or reproducible automation.

The bundled skill chooses between them from the capabilities available in the task. An uncertain write is never retried automatically through the other surface.

In terminal and Codex environments, the skill prefers the CLI. In ChatGPT web/app or another environment without a usable terminal, it uses the hosted app.

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

Refresh or restart the ChatGPT desktop app after installation, then start a new task so the app and skill are loaded. Open `/hooks` and review the two Composio hooks before trusting them; the hooks report local CLI state and provide environment-aware routing guidance.

The CLI is optional for hosted app workflows and preferred in terminal or Codex environments:

```bash
curl -fsSL https://composio.dev/install | bash
composio login
```

## What's included

| Component | Purpose |
|---|---|
| `.app.json` | Points local plugin installs at the team-owned Composio Developer Mode app. |
| `skills/composio` | Routes work by capability and defines safety boundaries across hosted app and CLI surfaces. |
| `skills/composio/references/mcp.md` | Covers hosted discovery, connection recovery, execution, and uncertain-write handling. |
| `skills/composio/references/cli.md` | Covers local discovery, execution, files, scripting, and auth. |
| `hooks/session-start.sh` | Reports local CLI availability and authentication without forcing it over the hosted app. |
| `hooks/user-prompt-submit.sh` | Adds a short surface-aware nudge for recognized services. |

## Routing examples

- “What is on my calendar tomorrow?” uses the hosted app in ChatGPT web/app and prefers the CLI in a terminal or Codex session.
- “Upload this local report and keep the workflow as a script” uses the CLI when it is available.
- “Create this confirmed issue” executes once on the selected surface and returns the created identifier.
- If a write times out, the next step is a read or status check, not replaying it through the other surface.

## Local development

Run the package tests and validators:

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/composio
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/composio/skills/composio
```

For a local checkout, add this repository as a marketplace and install the plugin:

```bash
codex plugin marketplace add .
codex plugin add composio@composio
```

The checked-in app manifest contains the current Developer Mode app ID. The public submission is separate: OpenAI scans `https://connect.composio.dev/mcp` rather than reusing this development app reference.

Test app loading in the ChatGPT desktop app, not only through the CLI:

1. Refresh or restart ChatGPT and enable the locally installed Composio plugin.
2. Start a new task and confirm the hosted app exposes exactly these seven tools: `COMPOSIO_MANAGE_CONNECTIONS`, `COMPOSIO_MULTI_EXECUTE_TOOL`, `COMPOSIO_REMOTE_BASH_TOOL`, `COMPOSIO_REMOTE_WORKBENCH`, `COMPOSIO_SEARCH_TOOLS`, `COMPOSIO_WAIT_FOR_CONNECTIONS`, and `COMPOSIO_GET_TOOL_SCHEMAS`.
3. Complete OAuth and run a read-only discovery call before testing any write.
4. In a terminal/Codex task, confirm the plugin prefers a signed-in local CLI and retains the hosted app as its bounded fallback.

## License

MIT — see [LICENSE](./LICENSE).
