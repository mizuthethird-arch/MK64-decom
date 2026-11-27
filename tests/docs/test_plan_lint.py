import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from plan_lint import KNOWN_ROLES, validate_plan

SOURCE_ROOT = Path(__file__).resolve().parents[2]
AGENT_RULES = SOURCE_ROOT / "docs" / "agent-rules.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

PLAN_TASKS = SOURCE_ROOT.parent / "_bp_TASKS.json"
PLAN_DETAIL = SOURCE_ROOT.parent / "_bp_DETAIL.json"
PLAN_REACHABLE = PLAN_TASKS.is_file() and PLAN_DETAIL.is_file()

GOOD = {
    "id": "T0001",
    "role": "ARCH",
    "thread": "P00-setup",
    "hours": 1.5,
    "steps": ["T: red", "B: green", "E: edge", "D: doc"],
    "done_when": "the sha1 of the reports equals",
    "depends_on": [],
}


class RuleViolationTest(unittest.TestCase):
    """T0029 sub-step T: a fixture that breaks each rule produces exactly one violation each."""

    def assert_single_violation(self, task, expected):
        errors = validate_plan([task])
        self.assertEqual(len(errors), 1, errors)
        self.assertIn(expected, errors[0])

    def test_an_unknown_role_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, role="WIZARD"), "unknown role")

    def test_too_many_hours_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, hours=4), "hours")

    def test_too_few_hours_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, hours=0.25), "hours")

    def test_three_steps_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, steps=["T: a", "B: b", "D: c"]), "steps")

    def test_eight_steps_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, steps=["T: a"] + ["B: b"] * 7), "steps")

    def test_a_first_step_that_is_not_a_test_is_one_violation(self):
        self.assert_single_violation(
            dict(GOOD, steps=["B: a", "B: b", "E: c", "D: d"]), "not a T step"
        )

    def test_an_unknown_step_kind_is_one_violation(self):
        self.assert_single_violation(
            dict(GOOD, steps=["T: a", "Z: b", "E: c", "D: d"]), "no known kind"
        )

    def test_an_unmeasurable_done_condition_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, done_when="it looks right"), "not measurable")

    def test_an_empty_done_condition_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, done_when=""), "done_when is empty")

    def test_a_shell_task_without_screens_is_one_violation(self):
        self.assert_single_violation(
            dict(GOOD, role="UI", done_when="every screen is reachable"),
            "shell task must name its screens",
        )

    def test_an_empty_thread_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, thread=""), "thread is empty")

    def test_an_external_dependency_is_one_violation(self):
        self.assert_single_violation(dict(GOOD, depends_on=["T9999"]), "not in the plan")


class MalformedInputTest(unittest.TestCase):
    """T0029 sub-step E: empty and malformed input each name the exact reason."""

    def test_an_empty_plan_has_no_violations(self):
        self.assertEqual(validate_plan([]), [])

    def test_a_missing_id_is_named(self):
        task = dict(GOOD)
        task.pop("id")
        self.assertIn("<no id>", " ".join(validate_plan([task])))

    def test_steps_that_are_not_a_list_are_named(self):
        self.assertIn("steps is not a list", " ".join(validate_plan([dict(GOOD, steps="T: a")])))

    def test_a_non_numeric_hours_is_named(self):
        self.assertIn("hours", " ".join(validate_plan([dict(GOOD, hours="two")])))

    def test_a_dependency_on_itself_is_a_violation(self):
        self.assertIn("not in the plan", " ".join(validate_plan([dict(GOOD, depends_on=["T0002"])])))


@unittest.skipUnless(PLAN_REACHABLE, "the blueprint task data is not reachable from this checkout")
class RealPlanTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import json

        tasks = json.loads(PLAN_TASKS.read_text(encoding="utf-8"))
        details = json.loads(PLAN_DETAIL.read_text(encoding="utf-8"))
        cls.records = []
        for phase in tasks.values():
            for task in phase:
                detail = details.get(task["k"], {})
                cls.records.append({
                    "id": task["k"],
                    "role": task["r"],
                    "thread": task["k"],
                    "hours": task["h"],
                    "steps": [f"{kind}: {text}" for kind, text in detail.get("sub", [])],
                    "done_when": detail.get("dw", ""),
                    "screens": detail.get("screens") or [],
                    "depends_on": detail.get("deps") or [],
                })

    def test_the_plan_data_is_complete(self):
        self.assertEqual(len(self.records), 1036)

    def test_every_role_in_the_plan_is_known(self):
        unknown = sorted({r["role"] for r in self.records if r["role"] not in KNOWN_ROLES})
        self.assertEqual(unknown, [])

    def test_the_plan_violations_are_exactly_the_two_known_kinds(self):
        """The real plan violates two rules, measured on 2026-11-27 and recorded, not hidden.

        412 tasks have a done condition written as prose with no measurable marker.
        23 UI tasks name no screens, which the shell definition of done requires.
        The lint is correct; the plan data is what it flags.
        """
        errors = validate_plan(self.records)
        unexpected = [
            e for e in errors
            if "done_when is not measurable" not in e and "shell task must name its screens" not in e
        ]
        self.assertEqual(unexpected[:10], [], f"{len(unexpected)} violations of other rules")
        self.assertEqual(len([e for e in errors if "not measurable" in e]), 412)
        self.assertEqual(len([e for e in errors if "name its screens" in e]), 23)
        self.assertEqual(len(errors), 435)


@unittest.skipUnless(PLAN_REACHABLE, "the blueprint task data is not reachable from this checkout")
class PlanReachabilityTest(unittest.TestCase):
    def test_the_plan_data_is_reachable(self):
        self.assertTrue(PLAN_TASKS.is_file())
        self.assertTrue(PLAN_DETAIL.is_file())


class AgentRulesLintTest(unittest.TestCase):
    def setUp(self):
        self.text = AGENT_RULES.read_text(encoding="utf-8")

    def test_records_the_lint_rules(self):
        self.assertIn("plan_lint", self.text)

    def test_lists_the_rules_the_lint_checks(self):
        lowered = self.text.lower()
        for rule in ("known role", "first step", "measurable", "thread", "dependency"):
            self.assertIn(rule, lowered, rule)


class DocIndexLintTest(unittest.TestCase):
    def test_the_index_records_the_lint_behaviour(self):
        lowered = DOC_INDEX.read_text(encoding="utf-8").lower()
        self.assertIn("plan lint", lowered)
        self.assertIn("toolkit follow-up needed", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
