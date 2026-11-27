import fnmatch
import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
README_PATH = SOURCE_ROOT / "README.md"
SCOPE_PATH = SOURCE_ROOT / "docs" / "scope.md"
ROM_CONTRACT_PATH = SOURCE_ROOT / "docs" / "rom-contract.md"

ROM_NAME = "Mario Kart 64 (Europe) (Rev A).n64"
ROM_SIZE = "12,582,912"
PINNED_Z64_SHA1 = "f6b5f519dd57ea59e9f013cc64816e9d273b2329"
LOCAL_V64_SHA1 = "f18317bfd7fbcaea6cfbfcb9c4ae3c7c7d1d66c7"


def markdown_link_targets(markdown):
    return [target.split("#")[0] for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", markdown)]


def is_ignored(path, rules):
    for rule in rules:
        if rule.endswith("/") and (path.startswith(rule) or ("/" + rule) in path):
            return True
        if fnmatch.fnmatchcase(path, rule) or fnmatch.fnmatchcase(Path(path).name, rule):
            return True
    return False


class ReadmeLinksScopeTest(unittest.TestCase):
    def test_readme_exists(self):
        self.assertTrue(README_PATH.is_file(), f"{README_PATH} must exist")

    def test_readme_links_the_scope_page(self):
        self.assertIn("docs/scope.md", markdown_link_targets(README_PATH.read_text(encoding="utf-8")))

    def test_readme_links_the_rom_page(self):
        self.assertIn("docs/rom.md", markdown_link_targets(README_PATH.read_text(encoding="utf-8")))

    def test_every_relative_link_resolves(self):
        for name in (README_PATH, SCOPE_PATH, ROM_CONTRACT_PATH):
            for target in markdown_link_targets(name.read_text(encoding="utf-8")):
                if "://" in target:
                    continue
                self.assertTrue((name.parent / target).is_file(), f"{name.name} links missing {target}")

    def test_the_rom_page_links_the_contract(self):
        rom_page = (SOURCE_ROOT / "docs" / "rom.md").read_text(encoding="utf-8")
        self.assertIn("rom-contract.md", markdown_link_targets(rom_page))


class RomPolicyTest(unittest.TestCase):
    def setUp(self):
        self.gitignore = SOURCE_ROOT / ".gitignore"
        self.rom_doc = SOURCE_ROOT / "docs" / "rom.md"
        self.assertTrue(self.gitignore.is_file(), f"{self.gitignore} must exist")
        self.assertTrue(self.rom_doc.is_file(), f"{self.rom_doc} must exist")
        self.ignored = {
            line.strip()
            for line in self.gitignore.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
        self.rom_text = self.rom_doc.read_text(encoding="utf-8")

    def test_gitignore_excludes_the_rom_directory(self):
        self.assertTrue(
            any(rule.startswith("rom") for rule in self.ignored), sorted(self.ignored)
        )

    def test_gitignore_excludes_any_derived_z64_image(self):
        self.assertIn("*.z64", self.ignored)

    def test_the_rom_image_is_ignored_wherever_it_sits(self):
        for path in (
            f"rom/{ROM_NAME}",
            "rom/nested/deeper/Mario Kart 64 (Europe) (Rev A).z64",
            "Mario Kart 64 (Europe) (Rev A).z64",
            "Mario Kart 64 (Europe) (Rev A).v64",
        ):
            self.assertTrue(is_ignored(path, self.ignored), path)

    def test_star_source_survives_the_ignore_rules(self):
        self.assertFalse(is_ignored("c/src/main.c", self.ignored))
        self.assertFalse(is_ignored("docs/scope.md", self.ignored))
        self.assertFalse(is_ignored("README.md", self.ignored))

    def test_rom_page_records_the_pinned_z64_sha1(self):
        self.assertIn(PINNED_Z64_SHA1, self.rom_text)

    def test_rom_page_records_the_local_v64_sha1(self):
        self.assertIn(LOCAL_V64_SHA1, self.rom_text)

    def test_rom_page_records_the_size_and_header(self):
        self.assertIn(ROM_SIZE, self.rom_text)
        for field in ("MARIOKART64", "NKT", "P (Europe)", "1 (Rev A)"):
            self.assertIn(field, self.rom_text)

    def test_rom_page_names_the_byteswap_conversion(self):
        self.assertIn("16-bit byteswap", self.rom_text)

    def test_rom_page_states_the_user_supplied_rules(self):
        for rule in ("user supplied", "read only", "never committed", "never shipped"):
            self.assertIn(rule, self.rom_text)

    def test_rom_page_links_the_pinned_image_name(self):
        self.assertIn(ROM_NAME, self.rom_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
