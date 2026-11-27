import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
LEGAL = SOURCE_ROOT / "docs" / "legal.md"
ASSETS = SOURCE_ROOT / "docs" / "assets.md"
ROM_DOC = SOURCE_ROOT / "docs" / "rom.md"
SCOPE = SOURCE_ROOT / "docs" / "scope.md"
README = SOURCE_ROOT / "README.md"


class LegalPageTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(LEGAL.is_file(), f"{LEGAL} must exist")
        self.text = LEGAL.read_text(encoding="utf-8")

    def test_states_the_rom_is_user_supplied_and_never_in_git_or_a_release(self):
        lowered = self.text.lower()
        self.assertIn("user supplied", lowered)
        self.assertIn("never in git", lowered)
        self.assertIn("never in a release", lowered)

    def test_names_every_asset_class(self):
        for asset in (
            "texture",
            "display list",
            "sample bank",
            "sequence",
            "track data",
            "font",
            "extracted model",
        ):
            self.assertIn(asset, self.text.lower(), asset)

    def test_names_every_key_class(self):
        for key in ("signing key", "rom key", "licence key", "secret"):
            self.assertIn(key, self.text.lower(), key)

    def test_states_the_run_time_read_rule(self):
        lowered = self.text.lower()
        self.assertIn("run time", lowered)
        self.assertIn("user image", lowered)

    def test_links_the_no_assets_policy(self):
        self.assertIn("assets.md", self.text)


class LegalLinkTest(unittest.TestCase):
    def test_the_assets_policy_exists_for_the_legal_page_to_point_at(self):
        self.assertTrue(ASSETS.is_file(), f"{ASSETS} must exist")

    def test_the_rom_page_reference_to_legal_resolves(self):
        self.assertIn("legal.md", ROM_DOC.read_text(encoding="utf-8"))
        self.assertTrue(LEGAL.is_file(), "rom.md points at docs/legal.md, so it must exist")

    def test_the_legal_page_is_linked_from_the_scope_page_or_the_readme(self):
        self.assertIn("legal.md", SCOPE.read_text(encoding="utf-8") + README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
