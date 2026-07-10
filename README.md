# Composio plugin for ChatGPT and Codex

This repository packages Composio as a universal OpenAI plugin: authenticated local CLI workflows for Codex today, plus connected-app workflow guidance for the future hosted ChatGPT and Codex app.

The plugin currently ships as **skills only**, so it is installable without asking users to manage a second API-key path. Its intended submitted shape is **app plus skills**. The final app binding must be added by the OpenAI submission owner after OpenAI assigns a real app ID; see [App wiring handoff](docs/app-wiring.md).

## What is included

- `plugins/composio/.codex-plugin/plugin.json` — plugin metadata and component paths.
- `plugins/composio/skills/composio-connect` — efficient, safe workflows when the connected Composio app is present.
- `plugins/composio/skills/composio-cli` — local Codex guidance for the published `composio` CLI.
- `plugins/composio/assets/logo.png` — the Composio marketplace and composer icon.
- `.agents/plugins/marketplace.json` — repo-scoped Composio marketplace.
- `submission/test-cases.json` — exactly five positive and three negative review fixtures.

## Install locally in Codex

From a checkout of this repository:

```bash
codex plugin marketplace add .
codex plugin add composio@composio --json
```

Start a new Codex task after installation so the skills are loaded.

The intended one-command path is:

```bash
composio setup --target codex --yes
```

Setup establishes or restores the Composio identity and installs this plugin. Local tool calls then run through the authenticated `composio` CLI; no `COMPOSIO_API_KEY` export, shell-profile mutation, or plugin-specific credential copy is required.

ChatGPT and hosted Codex authorization belongs to the app binding described in `docs/app-wiring.md`.

## Validate

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/composio
python3 -m unittest discover -s tests -v
```

## Publishing handoff

The repository URL in the plugin manifest assumes this local package will be published as `ComposioHQ/composio-plugin-openai`. Creating or pushing that GitHub repository is intentionally outside this scaffold.

Before OpenAI submission:

1. Add the assigned OpenAI app binding described in `docs/app-wiring.md`.
2. Verify every production MCP tool has accurate read-only, open-world, and destructive annotations.
3. Prepare reviewer credentials that do not require MFA or private network access.
4. Run all cases in `submission/test-cases.json` against the final package.
5. Re-run package validation and clean-install smoke tests.

Do not add a raw remote MCP configuration to make the pre-submission package appear app-enabled. The final `.app.json` binding is the source of truth for hosted MCP transport and authentication.

## License

MIT. See [LICENSE](LICENSE).
