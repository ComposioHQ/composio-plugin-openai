# App wiring handoff

This repository intentionally does not contain `.app.json`, and `plugin.json` intentionally omits both `apps` and `mcpServers`.

That makes the package truthful and fully usable before platform submission: local Codex uses the authenticated `composio` CLI through the bundled skill, with no duplicated secret storage. The future hosted ChatGPT and Codex experience uses the Composio app binding. Its ID must be assigned by OpenAI; it must not be guessed or copied from another app.

The submission owner should complete this handoff:

1. In ChatGPT developer mode, create the Composio app from `https://connect.composio.dev/mcp`, or create a new MCP-backed plugin submission from that server in the OpenAI Platform.
2. Copy the assigned app ID. Current IDs may begin with `plugin_asdk_app` or use a connector ID; use exactly what the platform provides.
3. At `plugins/composio/.app.json`, add the current app mapping using the assigned ID:

   ```json
   {
     "apps": {
       "composio": {
         "id": "<OPENAI_ASSIGNED_APP_ID>"
       }
     }
   }
   ```

4. Add `"apps": "./.app.json"` to `.codex-plugin/plugin.json`.
5. Do not add `.mcp.json` or `mcpServers`; the app binding owns hosted MCP transport and authentication.
6. Run the plugin validator, install from an isolated marketplace, and test in a new ChatGPT/Codex task.
7. Confirm MCP tool annotations, content security policy, reviewer credentials, starter prompts, and all eight cases in `submission/test-cases.json` before submission.

The local CLI skill and the hosted app are intentionally separate authentication surfaces. `composio setup` owns local identity and plugin installation; the OpenAI app owns authorization in ChatGPT and hosted Codex.
