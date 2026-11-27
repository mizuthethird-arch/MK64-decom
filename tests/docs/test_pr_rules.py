import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
PR_RULES = SOURCE_ROOT / "docs" / "pr-rules.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"
README = SOURCE_ROOT / "README.md"

CI_JOBS = ("no ROM in tracked files", "documentation suite", "rust toolchain image", "secret scan")


def rule_rows(text):
    """The rows of the numbered rule table only, stopping at the first non-table line."""
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(set(cell) <= set("-: ") for cell in cells):
            continue
        if cells[0].isdigit():
            rows.append(cells)
    return rows


class RuleListTest(unittest.TestCase):
    """T0020: every rule carries the rule, why, and the enforcing check."""

    def setUp(self):
        self.assertTrue(PR_RULES.is_file(), f"{PR_RULES} must exist")
        self.text = PR_RULES.read_text(encoding="utf-8")

    def test_the_rule_table_has_rows(self):
        self.assertNotEqual(rule_rows(self.text), [])

    def test_every_rule_is_numbered(self):
        rows = rule_rows(self.text)
        self.assertEqual([row[0] for row in rows], [str(n) for n in range(1, len(rows) + 1)])

    def test_every_rule_has_four_columns(self):
        for row in rule_rows(self.text):
            self.assertEqual(len(row), 4, row)

    def test_every_rule_names_an_enforcing_check_or_is_marked_unenforced(self):
        for row in rule_rows(self.text):
            enforcing = row[3].lower()
            self.assertTrue(
                enforcing.strip() and ("not yet enforced" in enforcing or len(enforcing) > 3),
                row[0],
            )

    def test_covers_the_required_rules(self):
        lowered = self.text.lower()
        for topic in (
            "rom",
            "extracted asset",
            "secret",
            "licence",
            "c++",
            "test",
            "policy",
            "blueprint task",
            "unverified",
        ):
            self.assertIn(topic, lowered, topic)

    def test_references_the_real_ci_job_names(self):
        for job in CI_JOBS:
            self.assertIn(job, self.text, job)

    def test_references_rust_only_for_the_cpp_rule(self):
        self.assertIn("rust-only.md", self.text)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())

    def test_states_that_an_unenforced_rule_carries_a_follow_up(self):
        self.assertIn("toolkit follow-up", self.text.lower())

    def test_the_enforcement_status_is_stated_per_rule(self):
        """Rules 1 and 2 are enforced, 3 awaits the secret scan job, and 4 to 9 are not yet enforced."""
        by_number = {row[0]: row[3].lower() for row in rule_rows(self.text)}
        self.assertEqual(len(by_number), 9)
        for number in ("1", "2"):
            self.assertNotIn("not yet enforced", by_number[number], number)
        self.assertIn("once that job lands", by_number["3"])
        for number in ("4", "5", "6", "7", "8", "9"):
            self.assertIn("not yet enforced", by_number[number], number)

    def test_rule_6_follow_up_compares_against_the_base_branch(self):
        lowered = {row[0]: row for row in rule_rows(self.text)}["6"][3].lower()
        self.assertIn("base branch", lowered)
        self.assertIn("decreased", lowered)

    def test_rule_4_follow_up_names_cargo_deny(self):
        self.assertIn("cargo-deny", {row[0]: row for row in rule_rows(self.text)}["4"][3].lower())


class PrRulesLinkTest(unittest.TestCase):
    def test_is_linked_from_the_readme(self):
        self.assertIn("pr-rules.md", README.read_text(encoding="utf-8"))

    def test_is_linked_from_the_docs_index(self):
        self.assertIn("pr-rules.md", DOC_INDEX.read_text(encoding="utf-8"))


class ToolkitFollowUpTest(unittest.TestCase):
    def test_the_index_carries_a_toolkit_follow_up_for_the_secret_scan(self):
        lowered = DOC_INDEX.read_text(encoding="utf-8").lower()
        self.assertIn("toolkit follow-up needed", lowered)
        self.assertIn("secret scan", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
