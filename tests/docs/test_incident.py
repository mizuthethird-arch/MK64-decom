import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
LEGAL = SOURCE_ROOT / "docs" / "legal.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"


def section_of(markdown, heading):
    lines = markdown.splitlines()
    collected = []
    inside = False
    for line in lines:
        if line.startswith("## ") or line.startswith("### "):
            if inside:
                break
            inside = line.lstrip("#").strip() == heading
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


class WithdrawalChecklistTest(unittest.TestCase):
    """T0021 sub-step T: every withdrawal step names a command and an owner."""

    def setUp(self):
        self.assertTrue(LEGAL.is_file(), f"{LEGAL} must exist")
        self.text = LEGAL.read_text(encoding="utf-8")
        self.rows = table_rows(section_of(self.text, "Artifact withdrawal steps"))

    def test_the_withdrawal_table_has_rows(self):
        self.assertNotEqual(self.rows, [])

    def test_every_withdrawal_step_names_a_command(self):
        missing = [row[0] for row in self.rows if "`" not in row[1]]
        self.assertEqual(missing, [])

    def test_every_withdrawal_step_names_an_owner(self):
        missing = [row[0] for row in self.rows if not row[2].strip()]
        self.assertEqual(missing, [])

    def test_every_withdrawal_step_has_a_time_limit(self):
        missing = [row[0] for row in self.rows if not row[3].strip()]
        self.assertEqual(missing, [])


class IncidentProcedureTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(LEGAL.is_file(), f"{LEGAL} must exist")
        self.text = LEGAL.read_text(encoding="utf-8")

    def test_has_the_procedure(self):
        self.assertIn("Incident and takedown procedure", self.text)

    def test_names_the_contact_path_without_inventing_an_address(self):
        lowered = self.text.lower()
        self.assertIn("github security advisory", lowered)
        self.assertNotRegex(self.text, r"[\w.+-]+@[\w-]+\.[\w.]+")

    def test_covers_the_public_statement_template(self):
        self.assertIn("public statement", self.text.lower())

    def test_covers_a_false_report_without_conceding(self):
        lowered = self.text.lower()
        self.assertIn("false report", lowered)
        self.assertIn("concede", lowered)

    def test_states_the_rehearsal_is_not_done(self):
        lowered = self.text.lower()
        self.assertIn("rehears", lowered)
        self.assertIn("not done", lowered)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())


class LegalIndexTest(unittest.TestCase):
    def test_the_index_records_the_incident_behaviour(self):
        self.assertIn("incident", DOC_INDEX.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
