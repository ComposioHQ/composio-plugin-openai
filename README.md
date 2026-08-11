# Composio for ChatGPT and Codex

[![CI](https://github.com/ComposioHQ/composio-plugin-openai/actions/workflows/ci.yml/badge.svg)](https://github.com/ComposioHQ/composio-plugin-openai/actions/workflows/ci.yml)
&nbsp;[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

Composio connects agents to [1,000+ apps](https://composio.dev/toolkits), including Google Workspace, Slack, GitHub, Notion, Linear, Jira, and HubSpot. This canonical OpenAI plugin combines two complementary surfaces:

- The hosted Composio app provides MCP-backed tools for direct SaaS reads and actions with managed authentication.
- The local [Composio CLI](https://docs.composio.dev/docs/cli) handles workflows that need local files, scripts, pipelines, or reproducible automation.

The bundled `composio` skill is the OpenAI distribution of the canonical Composio product-and-job router. It first distinguishes Composio For You from Composio Platform, then chooses the available execution surface. An uncertain write is never retried automatically through the other surface.

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

## Skill and tool discovery

| Installed surface | What becomes discoverable |
|---|---|
| This OpenAI plugin | The hosted Composio app and a bundled snapshot of the canonical `composio` skill. This is the supported installation for ChatGPT and Codex plugin users. |
| Raw Composio MCP connection | Callable tools and schemas only; MCP does not install an agent skill. |
| Standalone `ComposioHQ/composio` skill | The same canonical skill for clients outside the OpenAI plugin. Do not install it separately when this plugin is installed. |
| Composio CLI agent setup | The separate `composio-cli` skill for CLI-specific installation, commands, scripting, development, and troubleshooting. |

There are two semantic skills, not three. `composio` owns product selection, integrations, and generic app outcomes; `composio-cli` owns detailed CLI operation. The plugin copy and standalone copy of `composio` are two distributions of the same skill and should not be installed together on an OpenAI surface.

## What's included

| Component | Purpose |
|---|---|
| `.app.json` | Points local plugin installs at the team-owned Composio Developer Mode app. |
| `skills/composio` | Versioned OpenAI snapshot of the canonical Composio product-and-job router. |
| `skills/composio/references/for-you.md` | Covers personal agents, MCP clients, connections, and CLI-backed app work. |
| `skills/composio/references/platform.md` | Covers SDK sessions and products whose users connect accounts. |
| `skills/composio/references/errors.md` | Covers shared failure boundaries and provider gotchas. |
| `skills/composio/references/openai.md` | Adds OpenAI-specific hosted-app versus local-CLI routing and write safety. |
| `skills/composio/provenance.json` | Records the canonical source commit and the small OpenAI packaging overlay. |
| `hooks/session-start.sh` | Reports local CLI availability and authentication without forcing it over the hosted app. |
| `hooks/user-prompt-submit.sh` | Adds a short surface-aware nudge for recognized services. |

## Routing examples

- “What is on my calendar tomorrow?” uses the hosted app in ChatGPT web/app and prefers the CLI in a terminal or Codex session.
- “Upload this local report and keep the workflow as a script” uses the CLI when it is available.
- “Why does `composio execute` reject this payload?” uses `composio-cli` when that separate skill is available.
- “Create this confirmed issue” executes once on the selected surface and returns the created identifier.
- If a write times out, the next step is a read or status check, not replaying it through the other surface.

## Canonical skill snapshot

The bundled skill is sourced from [`ComposioHQ/composio/skills/composio`](https://github.com/ComposioHQ/composio/tree/c1fca392de349439e184696d96c1cbd6a170e7b4/skills/composio) at commit `c1fca392de349439e184696d96c1cbd6a170e7b4`. The plugin adds only OpenAI invocation metadata, execution-surface guidance, and the OpenAI installation note recorded in `provenance.json`.

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
