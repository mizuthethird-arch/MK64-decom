import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from task_definition_lint import validate

SOURCE_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DOC = SOURCE_ROOT / "docs" / "agent-rules.md"
TEMPLATE = SOURCE_ROOT / "docs" / "task-template.md"
README = SOURCE_ROOT / "README.md"

BAD_DEFINITION = {
    "role": "ARCH",
    "hours": 3,
    "steps": ["B: write the page"],
    "done_when": "the page looks right",
}


class BadDefinitionTest(unittest.TestCase):
    """T0007 sub-step T: a 3 hour, one step, no-failing-test definition must produce three errors."""

    def test_a_bad_definition_reports_three_errors(self):
        errors = validate(BAD_DEFINITION)
        self.assertEqual(len(errors), 3, errors)

    def test_the_three_errors_name_the_three_broken_rules(self):
        errors = " ".join(validate(BAD_DEFINITION)).lower()
        self.assertIn("hours", errors)
        self.assertIn("steps", errors)
        self.assertIn("measurable", errors)

    def test_a_good_definition_reports_no_errors(self):
        good = {
            "role": "ARCH",
            "hours": 2,
            "steps": ["T: red", "B: x", "B: y", "D: z"],
            "done_when": "the sha1 of the rebuilt image equals the pinned sha1",
        }
        self.assertEqual(validate(good), [])

    def test_a_four_step_definition_without_a_test_first_step_is_rejected(self):
        bad = {
            "role": "QA",
            "hours": 2,
            "steps": ["B: a", "B: b", "B: c", "B: d"],
            "done_when": "the hash matches",
        }
        errors = validate(bad)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("failing test", errors[0])

    def test_eight_steps_are_rejected(self):
        bad = {
            "role": "QA",
            "hours": 2,
            "steps": ["T: a"] + ["B: b"] * 7,
            "done_when": "the hash matches",
        }
        self.assertIn("steps", " ".join(validate(bad)))

    def test_a_missing_role_is_rejected(self):
        bad = {
            "hours": 1,
            "steps": ["T: a", "B: b", "B: c", "B: d"],
            "done_when": "exit code 0",
        }
        self.assertIn("role", " ".join(validate(bad)))


class AgentsPageTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(AGENTS_DOC.is_file(), f"{AGENTS_DOC} must exist")
        self.text = AGENTS_DOC.read_text(encoding="utf-8")

    def test_states_the_session_length_rule(self):
        lowered = self.text.lower()
        self.assertIn("0.5", lowered)
        self.assertIn("3 hours", lowered)

    def test_states_the_step_count_rule(self):
        self.assertIn("4 to 7", self.text)

    def test_states_the_first_step_is_a_failing_test(self):
        self.assertIn("failing test", self.text.lower())

    def test_states_the_measurable_done_condition(self):
        self.assertIn("measurable", self.text.lower())

    def test_states_the_no_invented_contracts_rule(self):
        self.assertIn("invent", self.text.lower())

    def test_names_the_step_kinds(self):
        for kind in ("T:", "B:", "E:", "D:"):
            self.assertIn(kind, self.text)

    def test_covers_the_three_borderline_cases(self):
        lowered = self.text.lower()
        self.assertIn("documentation-only", lowered)
        self.assertIn("corpus case", lowered)
        self.assertIn("audit", lowered)

    def test_records_the_sec_review_as_open_not_done(self):
        lowered = self.text.lower()
        self.assertIn("sec review pending", lowered)
        self.assertIn("open", lowered)

    def test_points_at_the_lint(self):
        self.assertIn("task_definition_lint", self.text)


class TaskTemplateTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TEMPLATE.is_file(), f"{TEMPLATE} must exist")
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_carries_every_required_field(self):
        for field in ("Role", "Hours", "Steps", "Done when", "Scope"):
            self.assertIn(field, self.text)

    def test_treats_content_as_data_not_instructions(self):
        self.assertIn("data", self.text.lower())
        self.assertIn("instruction", self.text.lower())

    def test_is_referenced_by_the_agents_page(self):
        self.assertIn("task-template", AGENTS_DOC.read_text(encoding="utf-8"))


class AgentsLinkTest(unittest.TestCase):
    def test_is_linked_from_the_readme(self):
        self.assertIn("agent-rules.md", README.read_text(encoding="utf-8"))

    def test_no_file_named_agents_md_is_reachable_under_docs(self):
        self.assertFalse((SOURCE_ROOT / "docs" / "agents.md").exists(), "docs/agents.md must not exist")

    def test_no_page_references_agents_md(self):
        offenders = [
            str(path.relative_to(SOURCE_ROOT))
            for path in (SOURCE_ROOT / "docs").glob("*.md")
            if "agents.md" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)


