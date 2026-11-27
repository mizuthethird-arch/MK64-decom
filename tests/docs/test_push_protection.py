import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
TESTS_DOCS = SOURCE_ROOT / "tests" / "docs"
DOCS = SOURCE_ROOT / "docs"

PUSH_PROTECTION_PATTERN = re.compile(
    "ghp_"
    + "[A-Za-z0-9]{36}"
    + "|xok[bp]-"
    + "|xo"
    + "xb-"
    + "|AKIA"
    + "[A-Z0-9]{16,}"
    + "|-----BEGIN (RSA|EC|DSA|OPENSSH|PGP) "
    + "PRIVATE KEY"
)


def committed_files():
    files = list(TESTS_DOCS.glob("*.py")) + list(DOCS.glob("*.md")) + [SOURCE_ROOT / "README.md"]
    return [path for path in files if path.is_file()]


class PushProtectionTest(unittest.TestCase):
    """No committed file in the docs lane may hold a contiguous secret-shaped literal."""

    def test_no_committed_file_matches_the_push_protection_pattern(self):
        offenders = []
        for path in committed_files():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if PUSH_PROTECTION_PATTERN.search(line):
                    offenders.append(f"{path.relative_to(SOURCE_ROOT)}:{number}")
        self.assertEqual(offenders, [], "contiguous secret-shaped literals must be built at run time")

    def test_the_fixtures_are_still_visibly_fake(self):
        self.assertIn("TEST", (TESTS_DOCS / "test_secrets.py").read_text(encoding="utf-8"))

    def test_the_detection_patterns_are_still_present_after_the_split(self):
        text = (TESTS_DOCS / "secret_scan.py").read_text(encoding="utf-8")
        self.assertIn("PRIVATE KEY", text)
        self.assertIn("BEGIN", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
