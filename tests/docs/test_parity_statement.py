import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
DOCS = SOURCE_ROOT / "docs"
STATEMENT = DOCS / "parity-statement.md"
MARKER = "{{include:parity-statement}}"

PARAPHRASE_MARKERS = (
    "bit-exact against the frozen reference",
    "bit exact against the frozen reference",
    "the rom is user supplied and",
    "display scaling is outside the claim",
)


def doc_pages():
    return sorted(page for page in DOCS.glob("*.md") if page.name != "README.md")


class NoParaphraseTest(unittest.TestCase):
    """T0014 sub-step T: the statement lives in one file and everyone else includes it by marker."""

    def test_every_page_that_cites_the_statement_uses_the_include_marker(self):
        offenders = []
        for page in doc_pages():
            if page.name == "parity-statement.md":
                continue
            text = page.read_text(encoding="utf-8").lower()
            for phrase in PARAPHRASE_MARKERS:
                if phrase in text and MARKER not in page.read_text(encoding="utf-8"):
                    offenders.append(f"{page.name}: {phrase}")
        self.assertEqual(offenders, [])

    def test_no_page_restates_the_statement_in_its_own_words(self):
        offenders = []
        for page in doc_pages():
            if page.name == "parity-statement.md":
                continue
            text = page.read_text(encoding="utf-8")
            if MARKER in text:
                continue
            lowered = text.lower()
            if "bit-exact against the frozen reference" in lowered:
                offenders.append(page.name)
        self.assertEqual(offenders, [])


class StatementContentTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(STATEMENT.is_file(), f"{STATEMENT} must exist")
        self.text = STATEMENT.read_text(encoding="utf-8")

    def test_is_the_single_statement_not_a_list_of_variants(self):
        self.assertEqual(len(re.findall(r"^> ", self.text, re.MULTILINE)), 1)

    def test_gives_the_exact_scope_wording(self):
        lowered = self.text.lower()
        self.assertIn("mario kart 64", lowered)
        self.assertIn("europe", lowered)
        self.assertIn("rev a", lowered)

    def test_references_the_scenario_set(self):
        self.assertIn("scenario set", self.text.lower())

    def test_references_the_deviations_list(self):
        self.assertIn("deviation", self.text.lower())

    def test_states_the_rom_is_user_supplied(self):
        self.assertIn("user supplied", self.text.lower())

    def test_states_coverage_not_a_promise(self):
        lowered = self.text.lower()
        self.assertIn("coverage", lowered)
        self.assertIn("promise", lowered)

    def test_records_the_affiliation_check_honestly(self):
        lowered = self.text.lower()
        self.assertIn("nintendo", lowered)
        self.assertIn("affiliation", lowered)
        self.assertIn("checked", lowered)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())


class StatementMarkerTest(unittest.TestCase):
    def test_the_include_marker_is_documented_somewhere(self):
        self.assertIn(MARKER, STATEMENT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
