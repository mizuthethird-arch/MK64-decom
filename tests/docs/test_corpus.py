import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus_retention import CEILING_BYTES, REFUSE_CEILING, report, plan_prune

SOURCE_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DOC = SOURCE_ROOT / "docs" / "corpus.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

GB = 1024 * 1024 * 1024


def scene(name, size_gb, release_gate=False):
    return {"name": name, "bytes": int(size_gb * GB), "release_gate": release_gate}


class CeilingTest(unittest.TestCase):
    """T0017 sub-step T: the tool refuses a corpus above the ceiling and names the largest scenes."""

    def test_a_corpus_over_the_ceiling_is_reported_as_over(self):
        result = report([scene("boot", 15), scene("race", 10)])
        self.assertTrue(result["over_ceiling"])

    def test_a_corpus_under_the_ceiling_is_reported_as_fine(self):
        self.assertFalse(report([scene("boot", 1), scene("race", 2)])["over_ceiling"])

    def test_the_report_names_the_largest_scenes(self):
        result = report([scene("small", 1), scene("huge", 9), scene("medium", 5)])
        self.assertEqual(result["largest_scenes"][0][0], "huge")
        self.assertEqual([name for name, _ in result["largest_scenes"]], ["huge", "medium", "small"])

    def test_the_report_names_the_ceiling(self):
        self.assertEqual(report([])["ceiling_bytes"], CEILING_BYTES)

    def test_pruning_stops_at_the_release_gate_scene(self):
        scenes = [scene("boot", 2), scene("race", 8, release_gate=True)]
        chosen, _ = plan_prune(scenes, 10 * GB)
        self.assertNotIn("race", chosen)

    def test_pruning_that_cannot_free_enough_refuses(self):
        scenes = [scene("boot", 2), scene("race", 8, release_gate=True)]
        chosen, refusals = plan_prune(scenes, 10 * GB)
        self.assertIn(REFUSE_CEILING, refusals)
        self.assertEqual(chosen, ["boot"])

    def test_prune_removes_the_smallest_until_enough_is_freed(self):
        scenes = [scene("a", 1), scene("b", 2), scene("c", 4)]
        chosen, _ = plan_prune(scenes, 3 * GB)
        self.assertEqual(chosen, ["a", "b"])

    def test_a_fully_prunable_corpus_reports_no_refusal(self):
        chosen, refusals = plan_prune([scene("a", 5)], 4 * GB)
        self.assertEqual(chosen, ["a"])
        self.assertEqual(refusals, [])


class CorpusDocTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CORPUS_DOC.is_file(), f"{CORPUS_DOC} must exist")
        self.text = CORPUS_DOC.read_text(encoding="utf-8")

    def test_states_the_retention_rule(self):
        self.assertIn("retention", self.text.lower())

    def test_states_a_concrete_size_ceiling(self):
        self.assertIn("20", self.text)
        self.assertIn("gib", self.text.lower())

    def test_states_the_regeneration_path(self):
        self.assertIn("regenerat", self.text.lower())

    def test_states_the_release_gate_exemption(self):
        lowered = self.text.lower()
        self.assertIn("release gate", lowered)
        self.assertIn("never pruned", lowered)

    def test_says_the_real_corpus_tool_does_not_exist_yet(self):
        self.assertIn("not yet implemented", self.text.lower())

    def test_names_the_policy_module_the_tool_must_call(self):
        self.assertIn("corpus_retention", self.text)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())


class CorpusIndexTest(unittest.TestCase):
    def test_the_index_records_the_corpus_behaviour(self):
        self.assertIn("corpus", DOC_INDEX.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
