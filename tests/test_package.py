import json
import os
import pathlib
import shlex
import stat
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "composio"
HOOKS = PLUGIN / "hooks"
SKILL = PLUGIN / "skills" / "composio"


class PluginPackageTests(unittest.TestCase):
    def load_json(self, path):
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def package_text(self):
        paths = [ROOT / "README.md"]
        paths.extend(
            path
            for path in PLUGIN.rglob("*")
            if path.is_file() and path.suffix in {".json", ".md", ".sh", ".yaml"}
        )
        return "\n".join(path.read_text(encoding="utf-8") for path in paths)

    def test_names_and_marketplace_source_match(self):
        manifest = self.load_json(PLUGIN / ".codex-plugin" / "plugin.json")
        marketplace = self.load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
        entry = marketplace["plugins"][0]
        self.assertEqual("composio", manifest["name"])
        self.assertEqual(manifest["name"], entry["name"])
        self.assertEqual("./plugins/composio", entry["source"]["path"])
        self.assertEqual("https://composio.dev", manifest["homepage"])
        self.assertRegex(
            manifest["version"],
            r"^\d+\.\d+\.\d+(?:\+codex\.[0-9A-Za-z.-]+)?$",
        )
        self.assertNotIn("[TODO:", json.dumps(manifest))
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual("./.app.json", manifest["apps"])

        interface = manifest["interface"]
        for field in ("composerIcon", "logo"):
            asset = PLUGIN / interface[field]
            self.assertTrue(asset.is_file(), asset)
            self.assertEqual(".png", asset.suffix)

    def test_app_plus_skills_wiring(self):
        app_path = PLUGIN / ".app.json"
        self.assertTrue(app_path.is_file())
        app_manifest = self.load_json(app_path)
        self.assertEqual({"composio"}, set(app_manifest["apps"]))
        app = app_manifest["apps"]["composio"]
        self.assertEqual(
            "plugin_asdk_app_6a57f13d63988191ae58e8494105a461",
            app["id"],
        )
        self.assertEqual("Productivity", app["category"])

        self.assertFalse((PLUGIN / ".mcp.json").exists())
        self.assertTrue(SKILL.is_dir())

    def test_bundled_skill_is_surface_aware_and_plugin_owned(self):
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: composio", skill_text)
        self.assertNotIn("AUTO-GENERATED", skill_text)
        self.assertNotIn("[TODO:", skill_text)
        self.assertFalse(
            (PLUGIN / "skills" / "composio-cli" / "SKILL.md").exists()
        )
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())
        self.assertIn(
            "$composio",
            (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            {"mcp.md", "cli.md"},
            {path.name for path in (SKILL / "references").glob("*.md")},
        )

    def test_skill_encodes_the_routing_and_write_contract(self):
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "In a terminal or Codex environment",
            "prefer the local Composio CLI",
            "In ChatGPT web/app",
            "local Composio CLI",
            "If both surfaces are available",
            "If neither surface is available",
            "hosted-only environment",
            "execute it exactly once",
            "Never automatically retry an uncertain write through the other surface",
        ):
            self.assertIn(phrase, skill_text)

        mcp_reference = (SKILL / "references" / "mcp.md").read_text(
            encoding="utf-8"
        )
        cli_reference = (SKILL / "references" / "cli.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("tool-discovery", mcp_reference)
        self.assertIn("connection-management", mcp_reference)
        self.assertIn("Do not replay", mcp_reference)
        self.assertIn("composio execute", cli_reference)
        self.assertIn("composio search", cli_reference)
        self.assertIn("composio link", cli_reference)
        self.assertIn("composio listen", cli_reference)
        self.assertIn("composio run", cli_reference)
        self.assertIn("composio dev", cli_reference)
        self.assertIn("Do not replay", cli_reference)

    def test_package_content_scan_is_scoped_to_shipped_files(self):
        package_text = self.package_text()
        self.assertNotIn("export COMPOSIO_API_KEY", package_text)
        self.assertNotIn("env_http_headers", package_text)
        self.assertNotIn("[TODO:", package_text)
        self.assertNotIn("AUTO-GENERATED", package_text)

    def test_hooks_match_the_surface_aware_contract(self):
        config = self.load_json(HOOKS / "hooks.json")["hooks"]
        self.assertEqual({"SessionStart", "UserPromptSubmit"}, set(config))
        self.assertEqual(8, config["SessionStart"][0]["hooks"][0]["timeout"])
        self.assertEqual(5, config["UserPromptSubmit"][0]["hooks"][0]["timeout"])

        for groups in config.values():
            for group in groups:
                for hook in group["hooks"]:
                    command = hook["command"]
                    self.assertIn("${PLUGIN_ROOT}", command)
                    relative = command.replace('"', "").replace(
                        "${PLUGIN_ROOT}/", ""
                    )
                    script = PLUGIN / relative
                    self.assertTrue(script.is_file(), script)
                    self.assertTrue(script.stat().st_mode & stat.S_IXUSR, script)

        hook_text = "\n".join(
            (HOOKS / name).read_text(encoding="utf-8")
            for name in ("session-start.sh", "user-prompt-submit.sh")
        )
        self.assertIn("hosted Composio app tools", hook_text)
        self.assertIn("local Composio CLI", hook_text)
        self.assertIn("Prefer", hook_text)
        self.assertIn("uncertain write", hook_text)
        self.assertNotIn("run `composio execute <slug>` directly", hook_text)

    def test_readme_documents_the_combined_local_flow(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("hosted Composio app", readme)
        self.assertIn("Composio CLI", readme)
        self.assertIn("codex plugin marketplace add ComposioHQ/composio-plugin-openai", readme)
        self.assertIn("codex plugin add composio@composio", readme)
        self.assertIn("ChatGPT desktop app", readme)
        self.assertIn("Start a new task", readme)
        self.assertIn("exactly these seven tools", readme)
        self.assertIn("https://connect.composio.dev/mcp", readme)
        self.assertIn("uncertain write", readme)
        self.assertNotIn("requires the real `plugin_asdk_app", readme)
        self.assertNotIn("bundles the canonical CLI skill", readme)
        self.assertNotIn("composio setup", readme)
        self.assertNotIn("/path/to/plugin-creator", readme)


class HookBehaviorTests(unittest.TestCase):
    def run_hook(self, script, payload, tmpdir, path=None):
        env = dict(os.environ, TMPDIR=tmpdir)
        if path is not None:
            env["PATH"] = path
        return subprocess.run(
            ["bash", str(HOOKS / script)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
            check=False,
        )

    def fake_composio(self, tmpdir, stdout="", exit_code=0, toolkits=None):
        bindir = pathlib.Path(tmpdir) / "bin"
        bindir.mkdir(exist_ok=True)
        script = bindir / "composio"
        lines = ["#!/usr/bin/env bash"]
        if toolkits is not None:
            lines.extend(
                [
                    'if [ "$1" = "dev" ] && [ "$2" = "toolkits" ]; then',
                    f"  printf '%s\\n' {shlex.quote(json.dumps(toolkits))}",
                    "  exit 0",
                    "fi",
                ]
            )
        if stdout:
            lines.append(f"printf '%s\\n' {shlex.quote(stdout)}")
        lines.append(f"exit {exit_code}")
        script.write_text("\n".join(lines) + "\n", encoding="utf-8")
        script.chmod(0o755)
        return f"{bindir}:{os.environ.get('PATH', '')}"

    def test_session_start_reports_local_auth_and_warms_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self.fake_composio(
                tmpdir,
                stdout='{"authenticated": true}',
                toolkits=[
                    {"slug": "gmail", "name": "Gmail"},
                    {"slug": "github", "name": "GitHub"},
                ],
            )
            result = self.run_hook(
                "session-start.sh", {"hook_event_name": "SessionStart"}, tmpdir, path
            )
            self.assertEqual(0, result.returncode, result.stderr)
            output = json.loads(result.stdout)["hookSpecificOutput"]
            self.assertEqual("SessionStart", output["hookEventName"])
            context = output["additionalContext"]
            self.assertIn("hosted Composio app tools", context)
            self.assertIn("local Composio CLI is available and signed in", context)
            self.assertIn("Prefer the local Composio CLI", context)
            self.assertIn("uncertain write", context)
            cache = pathlib.Path(tmpdir) / "composio-plugin-toolkits.cache"
            self.assertEqual({"gmail", "github"}, set(cache.read_text().splitlines()))

    def test_session_start_offers_cli_install_in_terminal_context(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            empty = pathlib.Path(tmpdir) / "empty"
            empty.mkdir()
            path = f"{empty}:/usr/bin:/bin"
            result = self.run_hook(
                "session-start.sh", {"hook_event_name": "SessionStart"}, tmpdir, path
            )
            self.assertEqual(0, result.returncode, result.stderr)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("hosted Composio app tools", context)
            self.assertIn("local Composio CLI is not installed", context)
            self.assertIn("Ask before installing", context)
            self.assertLess(
                context.index("Ask before installing"), context.index("hosted Composio app tools")
            )
            self.assertNotIn("composio execute", context)
            self.assertNotIn("composio search", context)

    def test_prompt_hook_is_surface_aware_for_cached_toolkits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = pathlib.Path(tmpdir) / "composio-plugin-toolkits.cache"
            cache.write_text("github\ngoogle calendar\n", encoding="utf-8")
            path = self.fake_composio(tmpdir)

            matched = self.run_hook(
                "user-prompt-submit.sh",
                {"hook_event_name": "UserPromptSubmit", "prompt": "open a github issue"},
                tmpdir,
                path,
            )
            self.assertEqual(0, matched.returncode, matched.stderr)
            context = json.loads(matched.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("hosted Composio app tools", context)
            self.assertIn("prefer it for the task", context)
            self.assertIn("uncertain write", context)
            self.assertNotIn("composio execute", context)
            self.assertNotIn("composio search", context)

            silent = self.run_hook(
                "user-prompt-submit.sh",
                {"hook_event_name": "UserPromptSubmit", "prompt": "refactor this function"},
                tmpdir,
                path,
            )
            self.assertEqual(0, silent.returncode, silent.stderr)
            self.assertEqual("", silent.stdout)


if __name__ == "__main__":
    unittest.main()
