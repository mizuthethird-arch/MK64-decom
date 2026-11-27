import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
RUST_ONLY = SOURCE_ROOT / "docs" / "rust-only.md"
README = SOURCE_ROOT / "README.md"


class RustOnlyPageTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(RUST_ONLY.is_file(), f"{RUST_ONLY} must exist")
        self.text = RUST_ONLY.read_text(encoding="utf-8")

    def test_states_the_rule_that_every_shipped_crate_is_rust(self):
        lowered = self.text.lower()
        self.assertIn("every shipped crate", lowered)
        self.assertIn("rust", lowered)

    def test_states_that_the_transpiler_and_tooling_are_rust(self):
        lowered = self.text.lower()
        self.assertIn("transpiler", lowered)
        self.assertIn("tooling", lowered)

    def test_names_the_single_exception(self):
        lowered = self.text.lower()
        self.assertIn("oracle", lowered)
        self.assertIn("cmake", lowered)
        self.assertIn("never shipped", lowered)

    def test_gives_an_exact_command_that_fails_on_a_non_rust_object(self):
        fences = self.text.split("```")
        commands = [block for block in fences[1::2]]
        self.assertNotEqual(commands, [], "the page must contain at least one fenced command")
        self.assertTrue(
            any("exit" in block.lower() or "grep" in block.lower() or "nm " in block.lower()
                for block in commands),
            "a fenced command must show how the check fails",
        )

    def test_marks_what_is_specification_and_not_yet_implemented(self):
        self.assertIn("not yet implemented", self.text.lower())


class RustOnlyLinkTest(unittest.TestCase):
    def test_is_linked_from_the_readme(self):
        self.assertIn("rust-only.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
