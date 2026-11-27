import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_lint import coverage_report, ownership, unowned_screens, unknown_screens

SOURCE_ROOT = Path(__file__).resolve().parents[2]
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"
BACKLOG = SOURCE_ROOT / "docs" / "backlog.md"

BLUEPRINT = SOURCE_ROOT.parent / "MK64-Native-Rebuild-Blueprint.html"
PLAN_TASKS = SOURCE_ROOT.parent / "_bp_TASKS.json"
PLAN_DETAIL = SOURCE_ROOT.parent / "_bp_DETAIL.json"
BLUEPRINT_REACHABLE = BLUEPRINT.is_file() and PLAN_TASKS.is_file() and PLAN_DETAIL.is_file()

CATALOGUE = ["boot", "title", "options-video", "diagnostics"]


class UnownedScreenTest(unittest.TestCase):
    """T0030 sub-step T: a screen no task owns fails, naming it."""

    def test_an_unowned_screen_fails_and_is_named(self):
        tasks = {"T1": ["boot", "title", "options-video"]}
        result = coverage_report(CATALOGUE, tasks)
        self.assertFalse(result["covered"])
        self.assertIn("'diagnostics'", " ".join(result["reasons"]))

    def test_the_unowned_screen_is_listed_by_name(self):
        tasks = {"T1": ["boot"]}
        self.assertEqual(unowned_screens(CATALOGUE, tasks), ["title", "options-video", "diagnostics"])


class CoveragePassTest(unittest.TestCase):
    """T0030 sub-step E: one owner and many owners both pass."""

    def test_a_screen_owned_by_exactly_one_task_passes(self):
        tasks = {"T1": ["boot"], "T2": ["title"], "T3": ["options-video"], "T4": ["diagnostics"]}
        self.assertTrue(coverage_report(CATALOGUE, tasks)["covered"])

    def test_a_screen_owned_by_many_tasks_passes(self):
        tasks = {
            "T1": ["boot", "title"],
            "T2": ["boot", "diagnostics"],
            "T3": ["boot", "title", "options-video", "diagnostics"],
        }
        self.assertTrue(coverage_report(CATALOGUE, tasks)["covered"])

    def test_ownership_lists_every_owning_task(self):
        tasks = {"T1": ["boot"], "T2": ["boot"], "T3": ["title"]}
        self.assertEqual(ownership(CATALOGUE, tasks)["boot"], ["T1", "T2"])


class MalformedInputTest(unittest.TestCase):
    def test_an_empty_catalogue_fails_with_a_reason(self):
        result = coverage_report([], {})
        self.assertFalse(result["covered"])
        self.assertIn("catalogue is empty", result["reasons"][0])

    def test_a_non_mapping_task_set_fails_naming_the_type(self):
        result = coverage_report(CATALOGUE, ["T1"])
        self.assertFalse(result["covered"])
        self.assertIn("list", result["reasons"][0])

    def test_a_screen_named_by_a_task_but_not_in_the_catalogue_is_reported(self):
        tasks = {"T1": ["boot", "title", "options-video", "diagnostics", "typo-screen"]}
        result = coverage_report(CATALOGUE, tasks)
        self.assertFalse(result["covered"])
        self.assertIn("not in the catalogue", " ".join(result["reasons"]))

    def test_unknown_screens_are_listed(self):
        self.assertEqual(unknown_screens(CATALOGUE, {"T1": ["nope"]}), ["nope"])


@unittest.skipUnless(BLUEPRINT_REACHABLE, "the blueprint screen catalogue is not reachable from this checkout")
class RealCatalogueTest(unittest.TestCase):
    """Runs the lint over the real 24-screen catalogue and the real task data."""

    @classmethod
    def setUpClass(cls):
        import json
        import re

        source = BLUEPRINT.read_text(encoding="utf-8")
        start = source.index("const SCREENS=") + len("const SCREENS=")
        depth = 0
        end = start
        while True:
            char = source[end]
            if char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    break
            end += 1
        cls.screens = [screen["id"] for screen in json.loads(source[start:end + 1])]
        tasks = json.loads(PLAN_TASKS.read_text(encoding="utf-8"))
        detail = json.loads(PLAN_DETAIL.read_text(encoding="utf-8"))
        cls.task_screens = {}
        for phase in tasks.values():
            for task in phase:
                cls.task_screens[task["k"]] = detail.get(task["k"], {}).get("screens") or []

    def test_the_catalogue_has_24_screens(self):
        self.assertEqual(len(self.screens), 24)

    def test_every_screen_is_owned_by_at_least_one_task(self):
        result = coverage_report(self.screens, self.task_screens)
        self.assertTrue(result["covered"], result["reasons"])

    def test_every_screen_has_at_least_one_owner_listed(self):
        result = coverage_report(self.screens, self.task_screens)
        empty = [screen for screen, owners in result["ownership"].items() if not owners]
        self.assertEqual(empty, [])


class CoverageDocTest(unittest.TestCase):
    def test_the_index_records_the_coverage_lint(self):
        lowered = DOC_INDEX.read_text(encoding="utf-8").lower()
        self.assertIn("coverage", lowered)
        self.assertIn("coverage_lint", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
