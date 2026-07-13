# Local Composio CLI

Prefer this path in terminal and Codex environments when the `composio` command is available. It supports direct SaaS work as well as local files, scripting, pipelines, and reproducible automation.

## Workflow

1. Run a known slug directly:

   ```bash
   composio execute GITHUB_GET_THE_AUTHENTICATED_USER -d '{}'
   ```

2. Discover an unknown slug, then return to `execute`:

   ```bash
   composio search "list unread email" --toolkits gmail
   ```

3. Inspect or preview inputs before a write:

   ```bash
   composio execute GITHUB_CREATE_AN_ISSUE --get-schema
   composio execute GITHUB_CREATE_AN_ISSUE --dry-run -d @issue.json
   ```

4. If a toolkit is not connected, run `composio link <toolkit>` and retry the original command after authorization succeeds.
5. Use `composio execute --parallel` for a few independent calls. Use `composio run` for control flow, loops, local output handling, or reusable scripts.
6. Use `composio proxy` only when a dedicated tool does not cover the required authenticated API operation.

Pass local data with `-d @file.json` or stdin, and use `--file` only for a tool with one uploadable file input. Check local auth with `composio whoami`; sign in with `composio login` when needed.

## Extended workflows

- Use `composio listen <trigger>` for temporary trigger subscriptions when the installed CLI exposes that feature.
- Use `composio dev` only for explicit developer-project work such as toolkits, auth configs, connected accounts, triggers, logs, organizations, or projects.
- Use `composio --help` and command-level `--help` for options not covered here.

If a write's result is uncertain, inspect the destination or execution status before retrying. Do not replay it through the hosted app.
