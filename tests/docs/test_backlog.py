import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backlog_lint import validate_backlog

SOURCE_ROOT = Path(__file__).resolve().parents[2]
BACKLOG = SOURCE_ROOT / "docs" / "backlog.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

GOOD_TASK = {
    "id": "T9999",
    "hours": 1.5,
    "steps": ["T: red", "B: green", "E: edge", "D: doc"],
    "depends_on": [],
}


class BacklogLintTest(unittest.TestCase):
    """T0013 sub-step T: the lint must reject each broken rule."""

    def test_a_conforming_task_reports_no_errors(self):
        self.assertEqual(validate_backlog([GOOD_TASK]), [])

    def test_eight_steps_are_rejected(self):
        bad = dict(GOOD_TASK, steps=["T: a"] + ["B: b"] * 7)
        self.assertIn("steps", " ".join(validate_backlog([bad])))

    def test_three_steps_are_rejected(self):
        bad = dict(GOOD_TASK, steps=["T: a", "B: b", "D: c"])
        self.assertIn("steps", " ".join(validate_backlog([bad])))

    def test_four_hours_are_rejected(self):
        bad = dict(GOOD_TASK, hours=4)
        self.assertIn("hours", " ".join(validate_backlog([bad])))

    def test_no_test_step_is_rejected(self):
        bad = dict(GOOD_TASK, steps=["B: a", "B: b", "E: c", "D: d"])
        self.assertIn("no test step", " ".join(validate_backlog([bad])))

    def test_a_dependency_outside_the_backlog_is_rejected(self):
        bad = dict(GOOD_TASK, depends_on=["T0000"])
        self.assertIn("not in the backlog", " ".join(validate_backlog([bad])))

    def test_a_dependency_inside_the_backlog_is_accepted(self):
        second = dict(GOOD_TASK, id="T9998", depends_on=["T9999"])
        self.assertEqual(validate_backlog([GOOD_TASK, second]), [])


class BacklogPageTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BACKLOG.is_file(), f"{BACKLOG} must exist")
        self.text = BACKLOG.read_text(encoding="utf-8")

    def test_marks_the_critical_path(self):
        self.assertIn("critical path", self.text.lower())

    def test_states_how_the_backlog_is_generated(self):
        lowered = self.text.lower()
        self.assertIn("generat", lowered)

    def test_marks_whether_generation_is_executable(self):
        self.assertIn("prose", self.text.lower())

    def test_contains_the_weekly_review_template(self):
        lowered = self.text.lower()
        self.assertIn("weekly review", lowered)
        self.assertIn("measured", lowered)
        self.assertIn("estimate", lowered)

    def test_states_the_rule_for_a_task_that_grows_past_three_hours(self):
        lowered = self.text.lower()
        self.assertIn("past", lowered)
        self.assertIn("split", lowered)
        self.assertIn("both halves", lowered)


class DocIndexTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(DOC_INDEX.is_file(), f"{DOC_INDEX} must exist")
        self.text = DOC_INDEX.read_text(encoding="utf-8")

    def test_links_every_doc_page(self):
        for page in sorted(p.name for p in (SOURCE_ROOT / "docs").glob("*.md")):
            if page == "README.md":
                continue
            self.assertIn(page, self.text, page)

    def test_records_the_backlog_behaviour(self):
        lowered = self.text.lower()
        self.assertIn("backlog", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
