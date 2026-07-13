import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "composio"


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

        interface = manifest["interface"]
        for field in ("composerIcon", "logo"):
            asset = PLUGIN / interface[field]
            self.assertTrue(asset.is_file(), asset)
            self.assertEqual(".png", asset.suffix)

    def test_package_is_cli_only(self):
        manifest = self.load_json(PLUGIN / ".codex-plugin" / "plugin.json")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        self.assertFalse((PLUGIN / ".mcp.json").exists())
        self.assertFalse((PLUGIN / ".app.json").exists())
        self.assertFalse((ROOT / "docs" / "app-wiring.md").exists())
        self.assertFalse((ROOT / "submission" / "test-cases.json").exists())

        package_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix in {".md", ".json"}
        )
        self.assertNotIn("export COMPOSIO_API_KEY", package_text)
        self.assertNotIn("env_http_headers", package_text)
        self.assertNotIn("COMPOSIO_SEARCH_TOOLS", package_text)

    def test_bundles_only_the_stable_cli_skill(self):
        skills = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertEqual([PLUGIN / "skills" / "composio-cli" / "SKILL.md"], skills)

        skill = skills[0].read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\nname: composio-cli\n"))
        self.assertIn("\ndescription:", skill)
        self.assertIn("source: @composio/cli@0.2.31, stable channel", skill)
        self.assertIn("GITHUB_CREATE_AN_ISSUE", skill)
        self.assertNotIn("GITHUB_CREATE_ISSUE", skill)
        self.assertNotIn("composio setup", skill)
        self.assertNotIn("composio listen", skill)
        self.assertNotIn("--no-browser", skill)

        references = PLUGIN / "skills" / "composio-cli" / "references"
        self.assertEqual(
            {"composio-dev.md", "power-user-examples.md", "troubleshooting.md"},
            {path.name for path in references.glob("*.md")},
        )
        troubleshooting = (references / "troubleshooting.md").read_text(encoding="utf-8")
        composio_dev = (references / "composio-dev.md").read_text(encoding="utf-8")
        self.assertNotIn("composio link gmail --no-browser", troubleshooting)
        self.assertNotIn("composio dev orgs", composio_dev)

    def test_readme_documents_released_install_flow(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("composio login", readme)
        self.assertIn("codex plugin marketplace add ComposioHQ/composio-plugin-openai", readme)
        self.assertIn("codex plugin add composio@composio", readme)
        self.assertNotIn("composio setup", readme)
        self.assertNotIn("/path/to/plugin-creator", readme)


if __name__ == "__main__":
    unittest.main()
