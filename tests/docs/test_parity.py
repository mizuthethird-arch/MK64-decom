import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
PARITY = SOURCE_ROOT / "docs" / "parity.md"

ARTIFACTS = (
    "framebuffer",
    "audio buffer",
    "VI log",
    "RSP log",
    "save",
    "input",
)
PYRAMID_LAYERS = ("input and memory", "RSP", "RDP", "VI", "audio", "content")
MISMATCH_KINDS = (
    "pixel colour",
    "audio sample",
    "VI timing",
    "RSP task",
    "save field",
    "input frame",
)


def parity_text():
    return PARITY.read_text(encoding="utf-8")


def section_of(markdown, heading):
    lines = markdown.splitlines()
    collected = []
    inside = False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip() == heading
            continue
        if inside:
            collected.append(line)
    return "\n".join(collected)


def table_rows(section):
    rows = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(set(cell) <= set("-: ") for cell in cells):
            continue
        rows.append(cells)
    return rows[1:]


class ParityPageExistsTest(unittest.TestCase):
    def test_the_parity_page_exists(self):
        self.assertTrue(PARITY.is_file(), f"{PARITY} must exist")


class ArtifactTableTest(unittest.TestCase):
    """T0006: every artifact kind carries a source, a format, a hash, a comparison rule and a tool."""

    def setUp(self):
        self.assertTrue(PARITY.is_file(), f"{PARITY} must exist")
        self.rows = table_rows(section_of(parity_text(), "The six artifacts"))

    def test_the_artifact_table_lists_all_six_kinds(self):
        names = [row[0].lower() for row in self.rows]
        for artifact in ARTIFACTS:
            self.assertTrue(
                any(artifact.lower() in name for name in names), artifact
            )

    def test_every_artifact_row_has_all_five_columns_filled(self):
        self.assertNotEqual(self.rows, [])
        for row in self.rows:
            self.assertEqual(len(row), 6, row[0])
            for cell in row[1:]:
                self.assertTrue(cell.strip(), f"{row[0]} has an empty column")

    def test_every_artifact_names_a_hash_and_a_comparison_rule(self):
        header = None
        for line in section_of(parity_text(), "The six artifacts").splitlines():
            if line.startswith("|"):
                header = [c.strip().lower() for c in line.strip().strip("|").split("|")]
                break
        self.assertIsNotNone(header)
        self.assertIn("hash", header)
        self.assertIn("comparison rule", header)


class ComparisonRulesTest(unittest.TestCase):
    """T0006: exact equality, first differing byte, documented deviations."""

    def setUp(self):
        self.assertTrue(PARITY.is_file(), f"{PARITY} must exist")
        self.text = parity_text().lower()

    def test_states_byte_equality_not_visual_similarity(self):
        self.assertIn("byte equality", self.text)
        self.assertIn("visual similarity", self.text)

    def test_defines_the_first_differing_byte(self):
        self.assertIn("first differing byte", self.text)

    def test_defines_what_counts_as_a_documented_deviation(self):
        self.assertIn("documented deviation", self.text)

    def test_covers_nondeterminism_and_how_the_harness_removes_it(self):
        self.assertIn("uninitialised", self.text)
        self.assertIn("timing", self.text)

    def test_lists_the_design_deviations_with_an_opt_in_flag(self):
        self.assertIn("display scaling", self.text)
        self.assertIn("aspect ratio", self.text)
        self.assertIn("opt-in", self.text)


class PyramidTest(unittest.TestCase):
    """T0008: the parity pyramid, one gate per layer, and a mismatch-to-layer table."""

    def setUp(self):
        self.assertTrue(PARITY.is_file(), f"{PARITY} must exist")
        self.text = parity_text()

    def test_the_pyramid_lists_every_layer_in_order(self):
        section = section_of(self.text, "The parity pyramid").lower()
        self.assertNotEqual(section.strip(), "")
        positions = [section.find(layer.lower()) for layer in PYRAMID_LAYERS]
        for layer, position in zip(PYRAMID_LAYERS, positions):
            self.assertGreaterEqual(position, 0, layer)
        self.assertEqual(positions, sorted(positions), "layers must be in pyramid order")

    def test_every_layer_has_a_gate(self):
        section = section_of(self.text, "The parity pyramid")
        self.assertIn("gate", section.lower())
        self.assertEqual(len(table_rows(section)), len(PYRAMID_LAYERS))

    def test_the_mismatch_table_assigns_an_owner_for_every_kind(self):
        rows = table_rows(section_of(self.text, "Who owns a mismatch"))
        self.assertNotEqual(rows, [])
        self.assertEqual(len(rows), len(MISMATCH_KINDS))

    def test_the_owning_layer_for_each_mismatch_kind_is_unique(self):
        rows = table_rows(section_of(self.text, "Who owns a mismatch"))
        owners = [row[1].strip() for row in rows]
        self.assertEqual(len(owners), len(set(owners)), f"owners must be unique, got {owners}")

    def test_covers_the_two_ambiguous_cases(self):
        text = parity_text().lower()
        self.assertIn("uninitialised word", text)
        self.assertIn("save reload", text)


class ParityHonestyTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(PARITY.is_file(), f"{PARITY} must exist")

    def test_marks_what_is_prose_and_what_is_executable(self):
        self.assertIn("prose", parity_text().lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
