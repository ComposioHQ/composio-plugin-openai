# Composio for Codex

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

Start a new Codex task after installation so the bundled skill is loaded.

To test a local checkout instead, run `codex plugin marketplace add .` from the repository root before installing the plugin.

## How it works

This is a CLI-only plugin. It bundles a `composio-cli` skill aligned with stable Composio CLI 0.2.31 and does not run background hooks or configure an MCP server.

When a task involves an external app, Codex:

1. Uses `composio execute <slug>` when the tool is already known.
2. Uses `composio search "<task>"` when it needs to discover the tool.
3. Runs `composio link <app>` if the required account is not connected.
4. Uses `composio run` for control flow, parallel work, or multi-step scripts.

Authentication stays in the Composio CLI. The plugin does not require `COMPOSIO_API_KEY` in your shell profile or duplicate credentials in Codex.

Hosted ChatGPT and Codex app support is intentionally out of scope for this release and can be added separately with an approved app binding.

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
