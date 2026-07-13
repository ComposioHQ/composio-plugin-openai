# Composio CLI for Codex

[![CI](https://github.com/ComposioHQ/composio-plugin-openai/actions/workflows/ci.yml/badge.svg)](https://github.com/ComposioHQ/composio-plugin-openai/actions/workflows/ci.yml)
&nbsp;[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

Composio lets Codex connect and act on [1,000+ apps](https://composio.dev/toolkits), including Google Workspace, Slack, GitHub, Notion, Linear, Jira, and HubSpot, through the authenticated [Composio CLI](https://docs.composio.dev/docs/cli).

Composio handles OAuth, permissions, tool discovery, and execution. Codex finds the right tool just in time with `composio search`, then runs it with `composio execute` instead of loading a fixed toolset into every task.

## What you can do

- Act on connected apps: send a Slack message, list GitHub pull requests, or add a calendar event.
- Run cross-app workflows: turn a GitHub issue into a Linear ticket and announce it in Slack.
- Connect apps on demand through Composio-managed OAuth with `composio link`.
- Script multi-step workflows with `composio run` and call authenticated APIs with `composio proxy`.

## Install

Install the Composio CLI and sign in:

```bash
curl -fsSL https://composio.dev/install | bash
composio login
```

Add this marketplace and install the plugin:

```bash
codex plugin marketplace add ComposioHQ/composio-plugin-openai
codex plugin add composio@composio
```

Start a new Codex task, open `/hooks`, and review and trust the two Composio hooks. Codex skips plugin hooks until their current definitions are trusted.

To test a local checkout instead, run `codex plugin marketplace add .` from the repository root before installing the plugin.

## What's included

This is a CLI-based plugin. It bundles the canonical CLI skill and does not configure an MCP server.

| Component | Purpose |
|---|---|
| `skills/composio-cli` | Guides tool discovery, account linking, schema inspection, execution, scripting, and troubleshooting. |
| `hooks/session-start.sh` | Adds the Composio workflow and current auth status to session context, then warms a top-50 toolkit cache. |
| `hooks/user-prompt-submit.sh` | Nudges Codex toward `composio search` when a prompt names a toolkit from that cache. |

## How it works

1. The bundled `composio-cli` skill supplies the detailed commands and troubleshooting workflow.
2. `SessionStart` tells Codex that Composio is available, reports whether the CLI is signed in, and warms the toolkit cache.
3. `UserPromptSubmit` stays silent unless the prompt names a cached toolkit, then adds a one-line search-and-execute nudge.
4. The authenticated CLI performs search, account linking, tool execution, and scripting.

Authentication stays in the Composio CLI. The plugin does not require `COMPOSIO_API_KEY` in your shell profile or duplicate credentials in Codex.

## Examples

```text
What's on my Google Calendar tomorrow? Add lunch at 12 PM.
```

```text
Take the latest merged PR in acme/app, open a Linear issue summarizing it,
and post the issue link to #eng in Slack.
```

```text
In parallel, fetch my last 10 Gmail emails, my open Linear issues, and today's
Google Calendar events, then give me a concise summary.
```

## Development

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](./LICENSE).
