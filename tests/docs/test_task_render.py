import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from task_render import REQUIRED_FIELDS, render, validation_errors

SOURCE_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = SOURCE_ROOT / "docs" / "task-template.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

PLAN_TASKS = SOURCE_ROOT.parent / "_bp_TASKS.json"
PLAN_DETAIL = SOURCE_ROOT.parent / "_bp_DETAIL.json"
PLAN_REACHABLE = PLAN_TASKS.is_file() and PLAN_DETAIL.is_file()

ENGINE_TASK = {
    "role": "ARCH",
    "thread": "P00-setup",
    "hours": 1.5,
    "steps": ["T: red", "B: green", "E: edge", "D: doc"],
    "done_when": "the sha1 of the two files equals",
}

SHELL_TASK = {
    "role": "UI",
    "thread": "shell",
    "hours": 1,
    "steps": ["T: red", "B: green", "E: edge", "D: doc"],
    "done_when": "every screen is reachable by keyboard",
    "screens": ["title", "options"],
}

POLICY_TASK = {
    "role": "LEG",
    "thread": "legal",
    "hours": 1,
    "steps": ["T: red", "B: green", "E: edge", "D: doc"],
    "done_when": "the contract states zero violations",
}


class MissingFieldTest(unittest.TestCase):
    """T0026 sub-step T: a fixture task missing a done condition must fail."""

    def test_a_task_without_a_done_condition_is_rejected(self):
        task = dict(ENGINE_TASK)
        task.pop("done_when")
        errors = validation_errors(task, {})
        self.assertIn("done_when is empty", errors)

    def test_the_renderer_refuses_and_names_the_field(self):
        task = dict(ENGINE_TASK)
        task.pop("done_when")
        with self.assertRaises(ValueError) as raised:
            render(task, {})
        self.assertIn("done_when", str(raised.exception))

    def test_every_required_field_is_checked(self):
        for field in REQUIRED_FIELDS:
            with self.subTest(field=field):
                task = dict(ENGINE_TASK)
                task.pop(field)
                self.assertIn(field, " ".join(validation_errors(task, {})))

    def test_an_empty_string_counts_as_empty(self):
        task = dict(ENGINE_TASK, thread="")
        self.assertIn("thread is empty", validation_errors(task, {}))

    def test_a_task_with_no_known_family_is_rejected(self):
        task = dict(ENGINE_TASK, role="NOPE")
        self.assertIn("no known family", " ".join(validation_errors(task, {})))

    def test_a_shell_task_without_screens_is_rejected(self):
        task = dict(SHELL_TASK)
        task.pop("screens")
        self.assertIn("screens is empty", " ".join(validation_errors(task, {})))


class RenderTest(unittest.TestCase):
    """T0026 sub-step E: a policy task with no repository path still renders."""

    def test_an_engine_task_renders_with_all_fields(self):
        text = render(ENGINE_TASK, {"repos": ["docs/parity.md"]})
        for expected in ("Role: ARCH", "Family: engine", "Thread: P00-setup", "Done when:"):
            self.assertIn(expected, text)

    def test_a_shell_task_renders_as_shell(self):
        self.assertIn("Family: shell", render(SHELL_TASK, {}))

    def test_a_policy_task_with_no_repository_path_renders(self):
        text = render(POLICY_TASK, {"repos": []})
        self.assertIn("none: this task writes no file", text)

    def test_an_explicit_family_overrides_the_role(self):
        detail = {"family": "shell", "screens": ["diagnostics"]}
        self.assertIn("Family: shell", render(dict(ENGINE_TASK, screens=["x"]), detail))

    def test_the_rendered_steps_come_from_the_detail(self):
        text = render(ENGINE_TASK, {"sub": [["T", "write the red test"], ["B", "make it pass"]]})
        self.assertIn("T - write the red test", text)
        self.assertIn("B - make it pass", text)

    def test_rendering_is_deterministic(self):
        self.assertEqual(render(ENGINE_TASK, {"repos": ["a"]}), render(ENGINE_TASK, {"repos": ["a"]}))


@unittest.skipUnless(PLAN_REACHABLE, "the blueprint task data is not reachable from this checkout")
class RealPlanTest(unittest.TestCase):
    """T0026 sub-step B: render every task in the real 1036-task plan."""

    @classmethod
    def setUpClass(cls):
        import json

        tasks = json.loads(PLAN_TASKS.read_text(encoding="utf-8"))
        details = json.loads(PLAN_DETAIL.read_text(encoding="utf-8"))
        cls.records = []
        for phase in tasks.values():
            for task in phase:
                cls.records.append((task, details.get(task["k"], {})))
        cls.count = len(cls.records)

    def test_the_plan_has_the_expected_number_of_tasks(self):
        self.assertEqual(self.count, 1036)

    def test_every_task_record_can_be_rendered(self):
        """All 1,036 tasks render; the 23 UI tasks with no screens are reported, not silently passed."""
        failures = []
        rejected_for_screens = 0
        for task, detail in self.records:
            record = {
                "role": task["r"],
                "thread": task["k"],
                "hours": task["h"],
                "steps": [kind for kind, _ in detail.get("sub", [])],
                "done_when": detail.get("dw", ""),
                "screens": detail.get("screens") or [],
            }
            detail_with_repos = {"sub": detail.get("sub", []), "repos": detail.get("repos") or []}
            try:
                render(record, detail_with_repos)
            except ValueError as error:
                if "screens is empty" in str(error):
                    rejected_for_screens += 1
                else:
                    failures.append(str(error))
        self.assertEqual(failures, [], "every task must render for reasons other than screens")
        self.assertEqual(rejected_for_screens, 23, "23 UI tasks in the plan name no screens")


class TemplateDocTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TEMPLATE.is_file(), f"{TEMPLATE} must exist")
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_lists_every_required_field(self):
        for field in ("Role", "Family", "Thread", "Hours", "Scope", "Steps", "Done when"):
            self.assertIn(field, self.text)

    def test_states_the_renderer_contract(self):
        self.assertIn("task_render", self.text)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())


class DocIndexRenderTest(unittest.TestCase):
    def test_the_index_records_the_template_behaviour(self):
        lowered = DOC_INDEX.read_text(encoding="utf-8").lower()
        self.assertIn("renderer", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
