import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
GITIGNORE_PATH = SOURCE_ROOT / ".gitignore"

ROM_FILE = "rom/Mario Kart 64 (Europe) (Rev A).n64"
BYTESWAPPED_COPY = "Mario Kart 64 (Europe) (Rev A).z64"
SOURCE_FILE = "c/src/main.c"


def gitignore_rules(gitignore):
    return [
        line.strip()
        for line in gitignore.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def is_ignored(path, rules):
    for rule in rules:
        pattern = rule.rstrip("/")
        if path == pattern or path.startswith(pattern + "/") or Path(path).match(pattern):
            return True
    return False


class RomIgnoreTest(unittest.TestCase):
    def setUp(self):
        self.rules = gitignore_rules(GITIGNORE_PATH.read_text(encoding="utf-8"))

    def test_the_rom_folder_is_ignored(self):
        self.assertTrue(is_ignored(ROM_FILE, self.rules))

    def test_a_byteswapped_copy_is_ignored(self):
        self.assertTrue(is_ignored(BYTESWAPPED_COPY, self.rules))

    def test_source_files_are_not_ignored(self):
        self.assertFalse(is_ignored(SOURCE_FILE, self.rules))


if __name__ == "__main__":
    unittest.main(verbosity=2)
