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
SKILL = PLUGIN / "skills" / "composio-cli"
LISTING = ROOT / "submission" / "listing.json"
TEST_CASES = ROOT / "submission" / "test-cases.json"


class PluginPackageTests(unittest.TestCase):
    def load_json(self, path):
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_names_and_marketplace_source_match(self):
        manifest = self.load_json(PLUGIN / ".codex-plugin" / "plugin.json")
        marketplace = self.load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
        entry = marketplace["plugins"][0]
        self.assertEqual("composio", manifest["name"])
        self.assertEqual(manifest["name"], entry["name"])
        self.assertEqual("./plugins/composio", entry["source"]["path"])
        self.assertEqual("https://docs.composio.dev/docs/cli", manifest["homepage"])
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertNotIn("[TODO:", json.dumps(manifest))
        self.assertNotIn("ChatGPT", json.dumps(manifest))
        self.assertEqual("./skills/", manifest["skills"])

        interface = manifest["interface"]
        for field in ("composerIcon", "logo"):
            asset = PLUGIN / interface[field]
            self.assertTrue(asset.is_file(), asset)
            self.assertEqual(".png", asset.suffix)

    def test_package_is_skills_only(self):
        manifest = self.load_json(PLUGIN / ".codex-plugin" / "plugin.json")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        self.assertFalse((PLUGIN / ".mcp.json").exists())
        self.assertFalse((PLUGIN / ".app.json").exists())
        self.assertFalse((ROOT / "docs" / "app-wiring.md").exists())
        self.assertTrue(TEST_CASES.is_file())
        self.assertTrue(SKILL.is_dir())

        package_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix in {".md", ".json"}
        )
        self.assertNotIn("export COMPOSIO_API_KEY", package_text)
        self.assertNotIn("env_http_headers", package_text)
        self.assertNotIn("COMPOSIO_SEARCH_TOOLS", package_text)

    def test_bundled_skill_is_complete_and_stable(self):
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: composio-cli", skill_text)
        self.assertIn("release-channel: stable", skill_text)
        self.assertIn("AUTO-GENERATED", skill_text)
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())
        self.assertEqual(
            {"composio-dev.md", "power-user-examples.md", "troubleshooting.md"},
            {path.name for path in (SKILL / "references").glob("*.md")},
        )

    def test_submission_materials_are_complete(self):
        listing = self.load_json(LISTING)
        self.assertEqual("Composio CLI", listing["name"])
        self.assertEqual("https://composio.dev/support", listing["supportUrl"])
        self.assertEqual(["US"], listing["availability"])
        self.assertEqual(3, len(listing["starterPrompts"]))
        self.assertNotIn("MCP", listing["longDescription"])

        cases = self.load_json(TEST_CASES)
        self.assertEqual(5, len(cases["positive"]))
        self.assertEqual(3, len(cases["negative"]))
        for case in cases["positive"]:
            self.assertTrue(
                {"name", "prompt", "expectedBehavior", "expectedResultShape", "fixtures"}
                <= set(case)
            )
        for case in cases["negative"]:
            self.assertTrue(
                {"name", "prompt", "expectedBehavior", "reason"} <= set(case)
            )

    def test_hooks_match_the_cli_plugin_contract(self):
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

    def test_readme_documents_released_install_flow(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("composio login", readme)
        self.assertNotIn("composio --install-skill composio-cli codex", readme)
        self.assertIn("bundles the canonical CLI skill", readme)
        self.assertIn("codex plugin marketplace add ComposioHQ/composio-plugin-openai", readme)
        self.assertIn("codex plugin add composio@composio", readme)
        self.assertIn("/hooks", readme)
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

    def test_session_start_reports_auth_and_warms_cache(self):
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
            self.assertIn("You're signed in to Composio.", output["additionalContext"])
            cache = pathlib.Path(tmpdir) / "composio-plugin-toolkits.cache"
            self.assertEqual({"gmail", "github"}, set(cache.read_text().splitlines()))

    def test_session_start_handles_missing_cli(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            empty = pathlib.Path(tmpdir) / "empty"
            empty.mkdir()
            path = f"{empty}:/usr/bin:/bin"
            result = self.run_hook(
                "session-start.sh", {"hook_event_name": "SessionStart"}, tmpdir, path
            )
            self.assertEqual(0, result.returncode, result.stderr)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("composio.dev/install", context)
            self.assertIn("composio execute <slug>", context)
            self.assertIn("composio search", context)
            self.assertLess(
                context.index("composio execute"), context.index("composio search")
            )

    def test_prompt_hook_fires_only_for_cached_toolkits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = pathlib.Path(tmpdir) / "composio-plugin-toolkits.cache"
            cache.write_text("github\ngoogle calendar\n", encoding="utf-8")

            matched = self.run_hook(
                "user-prompt-submit.sh",
                {"hook_event_name": "UserPromptSubmit", "prompt": "open a github issue"},
                tmpdir,
            )
            self.assertEqual(0, matched.returncode, matched.stderr)
            context = json.loads(matched.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("composio execute <slug>", context)
            self.assertIn("composio search", context)
            self.assertLess(
                context.index("composio execute"), context.index("composio search")
            )

            silent = self.run_hook(
                "user-prompt-submit.sh",
                {"hook_event_name": "UserPromptSubmit", "prompt": "refactor this function"},
                tmpdir,
            )
            self.assertEqual(0, silent.returncode, silent.stderr)
            self.assertEqual("", silent.stdout)


if __name__ == "__main__":
    unittest.main()
