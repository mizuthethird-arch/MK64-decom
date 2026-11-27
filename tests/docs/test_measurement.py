import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SOURCE_ROOT = Path(__file__).resolve().parents[2]
MEASUREMENT = SOURCE_ROOT / "docs" / "measurement.md"
PARITY = SOURCE_ROOT / "docs" / "parity.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

PARITY_METRICS = (
    "framebuffer",
    "audio buffer",
    "vi log",
    "rsp log",
    "save",
    "input",
)


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


class MeasurementTableTest(unittest.TestCase):
    """T0024 sub-step T: every metric named in parity.md exists here with a command."""

    def setUp(self):
        self.assertTrue(MEASUREMENT.is_file(), f"{MEASUREMENT} must exist")
        self.text = MEASUREMENT.read_text(encoding="utf-8")
        self.rows = table_rows(section_of(self.text, "The metric table"))

    def test_the_metric_table_has_rows(self):
        self.assertNotEqual(self.rows, [])

    def test_every_parity_metric_appears_in_the_table(self):
        names = " ".join(row[0].lower() for row in self.rows)
        for metric in PARITY_METRICS:
            self.assertIn(metric, names, metric)

    def test_every_metric_names_a_command(self):
        missing = [row[0] for row in self.rows if "`" not in row[1]]
        self.assertEqual(missing, [])

    def test_every_metric_names_the_page_it_feeds(self):
        missing = [row[0] for row in self.rows if not row[2].strip()]
        self.assertEqual(missing, [])

    def test_the_metric_names_match_the_parity_page(self):
        parity = PARITY.read_text(encoding="utf-8").lower()
        for metric in PARITY_METRICS:
            self.assertIn(metric, parity, metric)


class MeasurementHonestyTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MEASUREMENT.is_file(), f"{MEASUREMENT} must exist")
        self.text = MEASUREMENT.read_text(encoding="utf-8")

    def test_marks_a_command_that_does_not_exist_yet(self):
        self.assertIn("not implemented yet", self.text.lower())

    def test_states_a_metric_measured_on_one_machine_only(self):
        lowered = self.text.lower()
        self.assertIn("one machine", lowered)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())


class MeasurementIndexTest(unittest.TestCase):
    def test_the_index_records_the_measurement_behaviour(self):
        self.assertIn("measurement", DOC_INDEX.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
