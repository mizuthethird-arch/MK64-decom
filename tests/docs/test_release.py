import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_tag import hotfix_branch, parse_tag, release_kind, validate_tag

SOURCE_ROOT = Path(__file__).resolve().parents[2]
RELEASE_DOC = SOURCE_ROOT / "docs" / "release.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"
ISSUE_TEMPLATE = SOURCE_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"


class TagFormatTest(unittest.TestCase):
    """T0019 sub-step T: a malformed tag fails before any build step."""

    def test_a_malformed_tag_is_rejected(self):
        ok, reason = validate_tag("1.2.3", True)
        self.assertFalse(ok)
        self.assertIn("malformed", reason)

    def test_a_tag_without_patch_is_rejected(self):
        self.assertIsNone(parse_tag("v1.2"))

    def test_a_tag_with_a_suffix_is_rejected(self):
        self.assertIsNone(parse_tag("v1.2.3-rc1"))

    def test_a_well_formed_tag_is_accepted_on_an_ancestor_commit(self):
        self.assertEqual(validate_tag("v1.2.3", True), (True, "ok"))

    def test_a_well_formed_tag_on_a_non_ancestor_commit_is_refused(self):
        ok, reason = validate_tag("v1.2.3", False)
        self.assertFalse(ok)
        self.assertIn("not an ancestor", reason)

    def test_parse_returns_the_components(self):
        self.assertEqual(parse_tag("v2.10.4"), (2, 10, 4))

    def test_a_zero_patch_is_a_minor_release(self):
        self.assertEqual(release_kind("v1.3.0"), "minor")

    def test_a_non_zero_patch_is_a_patch_release(self):
        self.assertEqual(release_kind("v1.3.1"), "patch")

    def test_the_hotfix_branch_is_named_after_the_tag(self):
        self.assertEqual(hotfix_branch("v1.3.1"), "hotfix/v1.3.1")

    def test_a_malformed_tag_has_no_hotfix_branch(self):
        self.assertIsNone(hotfix_branch("1.3.1"))


class ReleaseDocTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(RELEASE_DOC.is_file(), f"{RELEASE_DOC} must exist")
        self.text = RELEASE_DOC.read_text(encoding="utf-8")

    def test_states_the_version_scheme_with_examples(self):
        self.assertIn("vMAJOR.MINOR.PATCH", self.text)
        self.assertIn("v1.3.0", self.text)

    def test_states_the_hotfix_branch_rule(self):
        self.assertIn("hotfix/", self.text)

    def test_names_the_validation_module(self):
        self.assertIn("release_tag", self.text)

    def test_names_the_exact_workflow_step_that_must_call_it(self):
        self.assertIn("validate-release-tag", self.text)

    def test_states_the_ancestor_rule(self):
        self.assertIn("ancestor", self.text.lower())

    def test_states_the_support_window(self):
        self.assertIn("support window", self.text.lower())

    def test_states_the_security_backport_rule(self):
        lowered = self.text.lower()
        self.assertIn("security", lowered)
        self.assertIn("backport", lowered)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())


class IssueTemplateTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(ISSUE_TEMPLATE.is_file(), f"{ISSUE_TEMPLATE} must exist")
        self.text = ISSUE_TEMPLATE.read_text(encoding="utf-8")

    def test_has_a_required_version_field(self):
        self.assertIn("version", self.text.lower())
        self.assertIn("required: true", self.text)

    def test_references_the_support_window(self):
        self.assertIn("support window", self.text.lower())

    def test_is_a_github_issue_form(self):
        self.assertIn("body:", self.text)
        self.assertIn("type:", self.text)


class ReleaseIndexTest(unittest.TestCase):
    def test_the_index_records_the_release_and_support_behaviour(self):
        lowered = DOC_INDEX.read_text(encoding="utf-8").lower()
        self.assertIn("release", lowered)
        self.assertIn("support", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
