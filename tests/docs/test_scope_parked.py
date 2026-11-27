import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
SCOPE = SOURCE_ROOT / "docs" / "scope.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

PARKED_HEADING = "Parked: not in this rebuild"
DECIDER = "human owner (P00 decision record, no individual named)"
DECISION_DATE = "2026-11-27"
PARKED_FEATURES = ("Netplay", "Mods", "Texture packs", "macOS gate", "Mobile", "Achievements")


def section_of(markdown, heading):
    lines = markdown.splitlines()
    collected = []
    inside = False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip() == heading
            continue
        if inside:
            collected.append(line)
    return "\n".join(collected)


def table_rows(section):
    rows = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(set(cell) <= set("-: ") for cell in cells):
            continue
        rows.append(cells)
    return rows[1:]


class ParkedTableTest(unittest.TestCase):
    """T0015 sub-step T: the lint fails while any parked item lacks a date or an owner."""

    def setUp(self):
        self.assertTrue(SCOPE.is_file(), f"{SCOPE} must exist")
        self.text = SCOPE.read_text(encoding="utf-8")
        self.rows = table_rows(section_of(self.text, PARKED_HEADING))

    def test_the_parked_table_has_rows(self):
        self.assertNotEqual(self.rows, [])

    def test_every_parked_row_carries_four_columns(self):
        for row in self.rows:
            self.assertEqual(len(row), 4, row[0])

    def test_every_parked_row_names_a_decision_date(self):
        missing = [row[0] for row in self.rows if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[2])]
        self.assertEqual(missing, [])

    def test_every_parked_row_names_an_owner(self):
        missing = [row[0] for row in self.rows if row[3].strip() != DECIDER]
        self.assertEqual(missing, [])

    def test_every_parked_row_says_no(self):
        missing = [row[0] for row in self.rows if row[1].strip().lower() != "no"]
        self.assertEqual(missing, [])

    def test_every_parked_row_has_one_sentence_of_reasoning(self):
        for row in self.rows:
            reason = row[0]
            self.assertNotEqual(reason.strip(), "", "a row needs a feature name")

    def test_every_parked_feature_decided_on_the_recorded_date(self):
        for row in self.rows:
            self.assertEqual(row[2], DECISION_DATE, row[0])

    def test_all_six_parked_features_are_present(self):
        features = [row[0] for row in self.rows]
        for feature in PARKED_FEATURES:
            self.assertIn(feature, features)


class ParkedTemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = SCOPE.read_text(encoding="utf-8")

    def test_gives_a_template_for_adding_a_parked_item_later(self):
        lowered = self.text.lower()
        self.assertIn("adding a parked item", lowered)

    def test_the_template_names_the_same_fields(self):
        section = section_of(self.text, "Adding a parked item")
        lowered = section.lower()
        self.assertIn("date", lowered)
        self.assertIn("owner", lowered)
        self.assertIn("reason", lowered)


class DocIndexParkedTest(unittest.TestCase):
    def test_records_the_parked_behaviour(self):
        self.assertTrue(DOC_INDEX.is_file(), f"{DOC_INDEX} must exist")
        self.assertIn("parked", DOC_INDEX.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
