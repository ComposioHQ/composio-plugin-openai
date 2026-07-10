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
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertNotIn("[TODO:", json.dumps(manifest))

        interface = manifest["interface"]
        for field in ("composerIcon", "logo"):
            asset = PLUGIN / interface[field]
            self.assertTrue(asset.is_file(), asset)
            self.assertEqual(".png", asset.suffix)

    def test_local_package_uses_cli_auth_without_raw_mcp(self):
        manifest = self.load_json(PLUGIN / ".codex-plugin" / "plugin.json")
        self.assertNotIn("mcpServers", manifest)
        self.assertFalse((PLUGIN / ".mcp.json").exists())

        package_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix in {".md", ".json"}
        )
        self.assertNotIn("export COMPOSIO_API_KEY", package_text)
        self.assertNotIn("env_http_headers", package_text)

    def test_app_binding_is_not_fabricated(self):
        manifest = self.load_json(PLUGIN / ".codex-plugin" / "plugin.json")
        self.assertNotIn("apps", manifest)
        self.assertFalse((PLUGIN / ".app.json").exists())

        handoff = (ROOT / "docs" / "app-wiring.md").read_text(encoding="utf-8")
        self.assertIn('"apps": "./.app.json"', handoff)
        self.assertIn('"id": "<OPENAI_ASSIGNED_APP_ID>"', handoff)
        self.assertIn("Do not add `.mcp.json`", handoff)

    def test_skills_have_frontmatter(self):
        skills = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertEqual(2, len(skills))
        for skill in skills:
            text = skill.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\nname:"), skill)
            self.assertIn("\ndescription:", text, skill)

    def test_submission_case_counts(self):
        cases = self.load_json(ROOT / "submission" / "test-cases.json")
        self.assertEqual(5, len(cases["positive"]))
        self.assertEqual(3, len(cases["negative"]))
        self.assertEqual(
            8,
            len({case["id"] for group in ("positive", "negative") for case in cases[group]}),
        )
        self.assertEqual(
            {"connected-app"},
            {case["surface"] for case in cases["positive"]},
        )


if __name__ == "__main__":
    unittest.main()
