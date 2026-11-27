import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from handover import REQUIRED_FIELDS, validate_handovers, validate_note

SOURCE_ROOT = Path(__file__).resolve().parents[2]
HANDOVER_DOC = SOURCE_ROOT / "docs" / "handover.md"
TEMPLATE = SOURCE_ROOT / "docs" / "task-template.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

GOOD_NOTE = {
    "producer": "RT",
    "consumer": "RSP",
    "settled_decisions": ["the memory map is fixed at boot"],
    "open_questions": [],
}


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


class MissingFieldTest(unittest.TestCase):
    """T0027 sub-step T: a note missing any of the four fields is rejected, naming the field."""

    def test_a_complete_note_is_accepted(self):
        self.assertEqual(validate_note("RT-MEM", GOOD_NOTE), [])

    def test_each_missing_field_is_named(self):
        for field in REQUIRED_FIELDS:
            with self.subTest(field=field):
                note = dict(GOOD_NOTE)
                note.pop(field)
                reasons = validate_note("RT-MEM", note)
                self.assertEqual(len(reasons), 1)
                self.assertIn(field, reasons[0])

    def test_an_empty_string_is_named(self):
        note = dict(GOOD_NOTE, producer="   ")
        self.assertIn("producer is empty", validate_note("RT-MEM", note)[0])

    def test_an_empty_decision_list_is_rejected(self):
        note = dict(GOOD_NOTE, settled_decisions=[])
        self.assertIn("settled_decisions is empty", validate_note("RT-MEM", note)[0])

    def test_open_questions_may_be_an_empty_list(self):
        self.assertEqual(validate_note("RT-MEM", GOOD_NOTE), [])

    def test_a_non_mapping_note_names_the_type(self):
        reasons = validate_note("RT-MEM", "just a string")
        self.assertIn("not a mapping", reasons[0])
        self.assertIn("str", reasons[0])

    def test_an_empty_handover_set_has_no_reasons(self):
        self.assertEqual(validate_handovers({}), [])

    def test_reasons_are_reported_for_every_broken_contract(self):
        broken = {
            "RT-MEM": dict(GOOD_NOTE, consumer=""),
            "RT-OS": dict(GOOD_NOTE),
            "RDP-DL": dict(GOOD_NOTE, open_questions="x", producer=""),
        }
        reasons = validate_handovers(broken)
        self.assertEqual(len(reasons), 2)
        self.assertTrue(any("RT-MEM" in reason for reason in reasons))
        self.assertTrue(any("RDP-DL" in reason for reason in reasons))


class HandoverDocTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(HANDOVER_DOC.is_file(), f"{HANDOVER_DOC} must exist")
        self.text = HANDOVER_DOC.read_text(encoding="utf-8")

    def test_lists_the_settled_contracts(self):
        rows = table_rows(section_of(self.text, "Settled contracts"))
        self.assertNotEqual(rows, [])

    def test_every_contract_row_has_the_four_fields(self):
        rows = table_rows(section_of(self.text, "Settled contracts"))
        for row in rows:
            self.assertEqual(len(row), 5, row)

    def test_every_contract_names_a_producer_and_a_consumer(self):
        rows = table_rows(section_of(self.text, "Settled contracts"))
        for row in rows:
            self.assertTrue(row[1].strip(), row[0])
            self.assertTrue(row[2].strip(), row[0])

    def test_names_the_interface_list_source_honestly(self):
        self.assertIn("INTERFACES", self.text)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())

    def test_links_the_handover_doc_for_consumer_tasks(self):
        self.assertIn("handover.md", TEMPLATE.read_text(encoding="utf-8"))


class DocIndexHandoverTest(unittest.TestCase):
    def test_the_index_records_the_handover_behaviour(self):
        self.assertIn("handover", DOC_INDEX.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
