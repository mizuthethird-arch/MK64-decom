import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from upload_audit import (
    MAX_REPORT_BYTES,
    REASON_EMPTY,
    REASON_FORBIDDEN,
    REASON_MISSING_KIND,
    REASON_NOT_A_LIST,
    REASON_UNKNOWN,
    audit_artifact,
    audit_upload,
)

SOURCE_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DOC = SOURCE_ROOT / "docs" / "corpus.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"

SHAREABLE = [
    {"name": "frames.jsonl", "kind": "hash", "bytes": 4096},
    {"name": "counters.json", "kind": "counter", "bytes": 512},
    {"name": "run.log", "kind": "log", "bytes": 8192},
    {"name": "report.md", "kind": "report", "bytes": 2048},
]


class ShareableTest(unittest.TestCase):
    """T0023 sub-step T: the audit allows only the shareable kinds."""

    def test_every_shareable_kind_is_allowed(self):
        for artifact in SHAREABLE:
            with self.subTest(kind=artifact["kind"]):
                allowed, _ = audit_artifact(artifact)
                self.assertTrue(allowed)

    def test_an_all_shareable_list_is_uploaded(self):
        self.assertTrue(audit_upload(SHAREABLE)["allowed"])

    def test_a_report_under_the_cap_is_allowed(self):
        allowed, _ = audit_artifact({"name": "r.md", "kind": "report", "bytes": MAX_REPORT_BYTES})
        self.assertTrue(allowed)

    def test_a_report_over_the_cap_is_blocked_with_the_size_named(self):
        allowed, reason = audit_artifact(
            {"name": "huge.md", "kind": "report", "bytes": MAX_REPORT_BYTES + 1}
        )
        self.assertFalse(allowed)
        self.assertIn("over the", reason)


class ForbiddenTest(unittest.TestCase):
    def test_a_rom_artifact_is_blocked_and_named(self):
        result = audit_upload(SHAREABLE + [{"name": "game.z64", "kind": "rom"}])
        self.assertFalse(result["allowed"])
        self.assertEqual(result["blocked"], ["game.z64"])
        self.assertTrue(any(REASON_FORBIDDEN.format(kind="rom") == r for r in result["reasons"]))

    def test_every_forbidden_kind_is_blocked(self):
        for kind in ("rom", "payload", "asset", "recording", "blob"):
            with self.subTest(kind=kind):
                allowed, reason = audit_artifact({"name": "x", "kind": kind})
                self.assertFalse(allowed)
                self.assertIn("never uploaded", reason)

    def test_one_forbidden_item_blocks_the_whole_upload(self):
        result = audit_upload(SHAREABLE + [{"name": "rip.png", "kind": "asset"}])
        self.assertFalse(result["allowed"])
        self.assertEqual(len(result["blocked"]), 1)


class MalformedInputTest(unittest.TestCase):
    """T0023 sub-step E: empty and malformed input each name the exact reason."""

    def test_an_empty_list_is_refused(self):
        result = audit_upload([])
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reasons"], [REASON_EMPTY])

    def test_a_non_list_is_refused_naming_the_type(self):
        result = audit_upload("frames.jsonl")
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reasons"], [REASON_NOT_A_LIST.format(type="str")])

    def test_a_none_list_is_refused(self):
        self.assertFalse(audit_upload(None)["allowed"])

    def test_an_artifact_without_a_kind_is_blocked_and_named(self):
        allowed, reason = audit_artifact({"name": "mystery.bin"})
        self.assertFalse(allowed)
        self.assertEqual(reason, REASON_MISSING_KIND.format(name="mystery.bin"))

    def test_an_unknown_kind_is_blocked_not_uploaded(self):
        allowed, reason = audit_artifact({"name": "x", "kind": "something_new"})
        self.assertFalse(allowed)
        self.assertEqual(reason, REASON_UNKNOWN.format(kind="something_new"))

    def test_a_non_dict_artifact_is_blocked(self):
        self.assertFalse(audit_artifact("frames.jsonl")[0])

    def test_a_blocked_result_counts_the_failures(self):
        result = audit_upload([{"name": "a.z64", "kind": "rom"}, {"name": "b.z64", "kind": "rom"}])
        self.assertIn("2 artifact(s)", result["reasons"][-1])


class CorpusDocTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CORPUS_DOC.is_file(), f"{CORPUS_DOC} must exist")
        self.text = CORPUS_DOC.read_text(encoding="utf-8")

    def test_states_what_may_be_uploaded(self):
        lowered = self.text.lower()
        for kind in ("hash", "counter", "log", "report"):
            self.assertIn(kind, lowered, kind)

    def test_states_what_may_never_be_uploaded(self):
        lowered = self.text.lower()
        for kind in ("rom", "payload", "extracted asset", "recording"):
            self.assertIn(kind, lowered, kind)

    def test_states_the_audit_before_upload_rule(self):
        lowered = self.text.lower()
        self.assertIn("audit", lowered)
        self.assertIn("before", lowered)
        self.assertIn("blocks", lowered)

    def test_names_the_policy_module(self):
        self.assertIn("upload_audit", self.text)

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())


class DocIndexUploadTest(unittest.TestCase):
    def test_the_index_records_the_upload_behaviour(self):
        lowered = DOC_INDEX.read_text(encoding="utf-8").lower()
        self.assertIn("upload", lowered)
        self.assertIn("toolkit follow-up needed", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
