import fnmatch
import hashlib
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DOC = SOURCE_ROOT / "docs" / "assets.md"
SCOPE_DOC = SOURCE_ROOT / "docs" / "scope.md"
README = SOURCE_ROOT / "README.md"
ROM_PATH = SOURCE_ROOT / "rom" / "Mario Kart 64 (Europe) (Rev A).n64"
SCANNER = SOURCE_ROOT / "tools" / "scan-for-rom-content.py"
WORKFLOW = SOURCE_ROOT / ".github" / "workflows" / "ci.yml"

ROM_PRESENT = ROM_PATH.is_file()
ROM_ABSENT_REASON = "user-supplied ROM not present: this check reads the real image"

EXCLUDED_TREES = ("rom", "logs", "__pycache__")
BINARY_MAGIC = (
    b"\x89PNG",
    b"\x7fELF",
    b"OggS",
    b"RIFF",
    b"\x1aE\xdf\xa3",
    b"MZ",
    b"\x00asm",
)
ASSET_EXTENSIONS = (
    "*.png",
    "*.jpg",
    "*.bin",
    "*.z64",
    "*.v64",
    "*.n64",
    "*.ogg",
    "*.wav",
    "*.seq",
    "*.ctl",
    "*.tbl",
    "*.otr",
    "*.zip",
    "*.7z",
)
SIZE_CAP_BYTES = 2 * 1024 * 1024
PINNED_SIZE = 12582912
PINNED_V64_SHA1 = "f18317bfd7fbcaea6cfbfcb9c4ae3c7c7d1d66c7"


def tracked_files(root=SOURCE_ROOT):
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(root).parts
        if any(part in EXCLUDED_TREES for part in parts):
            continue
        files.append(path)
    return files


def is_asset_like(path):
    return any(fnmatch.fnmatchcase(path.name.lower(), pattern) for pattern in ASSET_EXTENSIONS)


def starts_with_binary_magic(path):
    head = path.read_bytes()[:16]
    return any(head.startswith(magic) for magic in BINARY_MAGIC)


class NoAssetsInTreeTest(unittest.TestCase):
    def test_the_tree_has_no_asset_like_file_name(self):
        found = [str(p.relative_to(SOURCE_ROOT)) for p in tracked_files() if is_asset_like(p)]
        self.assertEqual(found, [])

    def test_the_tree_has_no_file_with_binary_magic(self):
        found = [str(p.relative_to(SOURCE_ROOT)) for p in tracked_files() if starts_with_binary_magic(p)]
        self.assertEqual(found, [])

    def test_no_tracked_file_exceeds_the_size_cap(self):
        found = [
            f"{p.relative_to(SOURCE_ROOT)}={p.stat().st_size}"
            for p in tracked_files()
            if p.stat().st_size > SIZE_CAP_BYTES
        ]
        self.assertEqual(found, [])

    def test_the_rom_directory_is_never_scanned_as_tracked(self):
        self.assertNotIn("rom", {p.relative_to(SOURCE_ROOT).parts[0] for p in tracked_files()})


class DeepScanGuardTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCANNER.is_file(), f"{SCANNER} must exist")
        self.text = SCANNER.read_text(encoding="utf-8")

    def test_the_deep_scan_script_exists_and_is_not_empty(self):
        self.assertGreater(len(self.text), 500)

    def test_the_deep_scan_runs_the_exact_96_byte_check(self):
        self.assertIn("MIN_RUN_BYTES = 96", self.text)

    def test_the_deep_scan_defines_all_three_exit_codes(self):
        for constant in ("EXIT_CLEAN = 0", "EXIT_FOUND = 1", "EXIT_ERROR = 2"):
            self.assertIn(constant, self.text)

    def test_the_deep_scan_fails_closed_without_a_rom(self):
        self.assertIn("fails instead of passing", self.text)

    def test_ci_runs_the_deep_scan_in_a_dedicated_job(self):
        self.assertTrue(WORKFLOW.is_file(), f"{WORKFLOW} must exist")
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("scan-for-rom-content.py", workflow)


@unittest.skipUnless(ROM_PRESENT, ROM_ABSENT_REASON)
class PinnedImageHeaderTest(unittest.TestCase):
    def test_the_local_rom_is_the_pinned_size(self):
        self.assertEqual(ROM_PATH.stat().st_size, PINNED_SIZE)

    def test_the_local_rom_hashes_to_the_pinned_v64_sha1(self):
        self.assertEqual(hashlib.sha1(ROM_PATH.read_bytes()).hexdigest(), PINNED_V64_SHA1)


class AssetPolicyPageTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(ASSETS_DOC.is_file(), f"{ASSETS_DOC} must exist")
        self.text = ASSETS_DOC.read_text(encoding="utf-8")

    def test_names_every_asset_class(self):
        for asset in (
            "texture",
            "display list",
            "sample bank",
            "sequence",
            "track data",
            "font",
            "model",
        ):
            self.assertIn(asset, self.text.lower(), asset)

    def test_states_the_run_time_read_rule(self):
        self.assertIn("run time", self.text.lower())
        self.assertIn("user image", self.text.lower())

    def test_states_the_no_keys_rule(self):
        for key in ("signing key", "rom key", "licence key", "secret"):
            self.assertIn(key, self.text.lower(), key)

    def test_states_what_a_test_may_contain(self):
        self.assertIn("fixture", self.text.lower())
        self.assertIn("no rom bytes", self.text.lower())

    def test_is_linked_from_the_scope_page(self):
        self.assertIn("assets.md", SCOPE_DOC.read_text(encoding="utf-8"))

    def test_is_linked_from_the_readme(self):
        self.assertIn("assets.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
