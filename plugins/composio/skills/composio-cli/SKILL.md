---
name: composio-cli
description: Operate the local Composio CLI from Codex to find tools, connect apps, inspect schemas, execute actions, and script workflows. Use when the `composio` binary is available or the user explicitly asks for `composio`, `composio dev`, `composio link`, `composio execute`, `composio run`, or `composio proxy`.
---

# Composio CLI

Use this skill only where local shell commands are available. For ChatGPT or hosted Codex app workflows, use `composio-connect` only when the current session already exposes the connected Composio app tools.

## Default workflow

1. If the slug is known, start with `composio execute <slug>`.
2. If arguments are unclear, inspect them with `--get-schema` or preview with `--dry-run` before guessing.
3. If the slug is unknown, use `composio search "<task>"`. Batch related discovery queries into one command when useful.
4. If the toolkit is not connected, run `composio link <toolkit>` and retry the original command.
5. Use `composio execute --parallel` for a few independent calls. Use `composio run` for control flow, loops, output plumbing, or programmatic workflows.

## Execute a tool

```bash
composio execute GITHUB_GET_THE_AUTHENTICATED_USER -d '{}'
composio execute GITHUB_CREATE_ISSUE --get-schema
composio execute GITHUB_CREATE_ISSUE --skip-connection-check --dry-run \
  -d '{ owner: "acme", repo: "app", title: "Bug report" }'
```

Inputs can come from a file or standard input:

```bash
composio execute GITHUB_CREATE_ISSUE -d @issue.json
composio execute GITHUB_CREATE_ISSUE -d - < issue.json
```

Run independent calls in parallel:

```bash
composio execute --parallel \
  GMAIL_SEND_EMAIL -d '{ recipient_email: "person@example.com", subject: "Hello" }' \
  GITHUB_CREATE_ISSUE -d '{ owner: "acme", repo: "app", title: "Bug" }'
```

## Discover and connect

```bash
composio search "create a github issue" "send an email"
composio search "send an email" --toolkits gmail
composio link gmail
composio link googlecalendar
```

Retry the original execution after linking succeeds.

## Programmatic workflows

`composio run` executes inline ESM JavaScript or TypeScript with authenticated `execute()`, `search()`, and `proxy()` helpers.

```bash
composio run '
  const [me, emails] = await Promise.all([
    execute("GITHUB_GET_THE_AUTHENTICATED_USER"),
    execute("GMAIL_FETCH_EMAILS", { max_results: 5 }),
  ]);
  console.log({ login: me.data.login, emailCount: emails.data.messages?.length });
'
```

Use `composio proxy` for a raw API operation when it is clearer than finding a dedicated slug:

```bash
composio proxy https://api.github.com/user --toolkit github -X GET </dev/null
```

## Authentication and developer mode

Check the current identity with `composio whoami`. If it is unauthenticated, run `composio setup --target codex --yes`, then return to the original command. Setup establishes the human or agent identity and idempotently ensures this plugin is installed. If an older CLI does not recognize `setup`, update the CLI; `composio login` is the temporary fallback for human sessions.

Never ask the user to export or persist `COMPOSIO_API_KEY` for local Codex. The CLI reads its own authenticated identity.

Reserve `composio dev` for developer projects, auth configs, connected-account administration, triggers, logs, organizations, or project context. Ordinary end-user work should stay on top-level `execute`, `search`, `link`, `run`, and `proxy` commands.
