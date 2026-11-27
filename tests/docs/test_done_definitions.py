import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from done_family import definition_of_done_for, family_of_role

SOURCE_ROOT = Path(__file__).resolve().parents[2]
AGENT_RULES = SOURCE_ROOT / "docs" / "agent-rules.md"
TEMPLATE = SOURCE_ROOT / "docs" / "task-template.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

SHELL_ROLES = ("UI",)
ENGINE_ROLES = ("RDP", "RSP", "RT", "GAME", "PLAT", "ARCH", "TOOL", "LEG", "PM", "QA")


class FamilySelectionTest(unittest.TestCase):
    """T0016 sub-step T: a shell task points at the shell definition, an engine task at the hash one."""

    def test_a_ui_role_selects_the_shell_family(self):
        self.assertEqual(family_of_role("UI"), "shell")

    def test_an_engine_role_selects_the_engine_family(self):
        self.assertEqual(family_of_role("RDP"), "engine")

    def test_the_shell_definition_is_named_for_a_shell_task(self):
        self.assertIn("shell", definition_of_done_for("UI").lower())

    def test_the_engine_definition_is_named_for_an_engine_task(self):
        self.assertIn("hash", definition_of_done_for("GAME").lower())

    def test_every_known_role_resolves_to_a_family(self):
        for role in SHELL_ROLES + ENGINE_ROLES:
            self.assertIn(family_of_role(role), ("shell", "engine"), role)

    def test_an_unknown_role_is_rejected_rather_than_guessed(self):
        self.assertIsNone(family_of_role("NOPE"))

    def test_a_mixed_task_is_owned_by_the_engine_definition(self):
        self.assertEqual(definition_of_done_for("UI", touches_engine=True).split()[0].lower(), "engine")


class AgentRulesTest(unittest.TestCase):
    def setUp(self):
        self.assertEqual(AGENT_RULES.is_file(), True, f"{AGENT_RULES} must exist")
        self.text = AGENT_RULES.read_text(encoding="utf-8")

    def test_has_a_shell_definition_of_done(self):
        lowered = self.text.lower()
        self.assertIn("definition of done: shell", lowered)

    def test_has_an_engine_definition_of_done(self):
        lowered = self.text.lower()
        self.assertIn("definition of done: engine", lowered)

    def test_the_shell_definition_names_each_criterion_with_its_tool(self):
        lowered = self.text.lower()
        for criterion in ("keyboard", "gamepad", "strings", "failure", "accessibility"):
            self.assertIn(criterion, lowered, criterion)

    def test_the_engine_definition_points_at_the_hash_rule(self):
        self.assertIn("parity.md", self.text)

    def test_ties_a_role_to_a_family(self):
        self.assertIn("family_of_role", self.text)

    def test_states_which_definition_wins_for_a_mixed_task(self):
        lowered = self.text.lower()
        self.assertIn("both families", lowered)
        self.assertIn("wins", lowered)


class TemplateFamilyTest(unittest.TestCase):
    def test_the_template_asks_for_the_family(self):
        self.assertIn("family", TEMPLATE.read_text(encoding="utf-8").lower())


class DocIndexDoneTest(unittest.TestCase):
    def test_records_the_two_definitions(self):
        self.assertIn("definition of done", DOC_INDEX.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
