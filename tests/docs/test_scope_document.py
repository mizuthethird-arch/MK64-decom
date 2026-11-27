import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
SCOPE_PATH = SOURCE_ROOT / "docs" / "scope.md"

MODES = ("Grand Prix", "Time Trial", "Versus", "Battle")
CUPS = ("Mushroom Cup", "Flower Cup", "Star Cup", "Special Cup")
UNVERIFIED_MARKER = "(unverified: awaiting cartridge check)"
IN_SCOPE_DELIVERABLES = ("match-proven decompilation", "frozen C oracle", "100% Rust rebuild")
NAME_SECTIONS = (
    "In scope: tracks",
    "In scope: arenas",
    "In scope: characters",
)


def section_of(markdown, heading):
    pattern = re.compile(
        r"^## " + re.escape(heading) + r"\s*$(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
    )
    match = pattern.search(markdown)
    return match.group(1) if match else ""


def table_rows(text):
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or set(stripped) <= set("|-: "):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows[1:]


def name_cells(markdown, heading):
    return [cell for row in table_rows(section_of(markdown, heading)) for cell in row]


class ScopeDocumentTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCOPE_PATH.is_file(), f"{SCOPE_PATH} must exist")
        self.markdown = SCOPE_PATH.read_text(encoding="utf-8")

    def test_has_a_h1_title(self):
        h1_lines = [line for line in self.markdown.splitlines() if line.startswith("# ")]
        self.assertEqual(len(h1_lines), 1)

    def test_names_the_pinned_revision(self):
        self.assertIn("Mario Kart 64 (Europe) (Rev A)", self.markdown)

    def test_names_the_three_deliverables(self):
        for deliverable in IN_SCOPE_DELIVERABLES:
            self.assertIn(deliverable, self.markdown)

    def test_changes_nothing_else(self):
        self.assertIsNotNone(re.search(r"and nothing else", self.markdown, re.IGNORECASE))

    def test_lists_exactly_the_four_modes(self):
        modes = re.findall(
            r"exactly four modes \(([^)]*)\)", self.markdown, re.IGNORECASE
        )
        self.assertEqual(len(modes), 1)
        listed = [name.strip() for name in modes[0].split(",")]
        self.assertEqual(sorted(listed), sorted(MODES))

    def test_lists_every_mode_in_the_modes_section(self):
        section = section_of(self.markdown, "In scope: modes")
        for mode in MODES:
            self.assertIn(f"| {mode} |", section)

    def test_lists_four_cups_of_four_tracks(self):
        rows = table_rows(section_of(self.markdown, "In scope: tracks"))
        self.assertEqual([row[0].split(" (")[0] for row in rows], list(CUPS))
        for row in rows:
            self.assertEqual(len(row[1].split(",")), 4, row[0])

    def test_lists_four_arenas(self):
        self.assertEqual(len(table_rows(section_of(self.markdown, "In scope: arenas"))), 4)

    def test_lists_eight_characters(self):
        self.assertEqual(len(table_rows(section_of(self.markdown, "In scope: characters"))), 8)

    def test_every_listed_name_is_marked_unverified(self):
        for heading in NAME_SECTIONS:
            cells = name_cells(self.markdown, heading)
            self.assertNotEqual(cells, [], heading)
            for cell in cells:
                self.assertIn(UNVERIFIED_MARKER, cell, f"{heading}: {cell} needs a marker")

    def test_lists_the_item_set(self):
        self.assertNotEqual(
            len(table_rows(section_of(self.markdown, "In scope: items"))), 0
        )

    def test_lists_ghosts_saves_and_options(self):
        for heading in (
            "In scope: time trial ghosts",
            "In scope: save files",
            "In scope: options screens",
        ):
            self.assertTrue(section_of(self.markdown, heading).strip(), heading)

    def test_lists_every_parked_feature_with_reason_and_decider(self):
        rows = table_rows(section_of(self.markdown, "Parked: not in this rebuild"))
        features = [row[0] for row in rows]
        for feature in (
            "Netplay",
            "Mods",
            "Texture packs",
            "macOS gate",
            "Mobile",
            "Achievements",
        ):
            self.assertIn(feature, features)
        self.assertTrue(rows, "the parked table must list features")
        for row in rows:
            self.assertEqual(len(row), 4, row)
            self.assertTrue(row[1].strip(), f"{row[0]} needs a decision")
            self.assertTrue(row[2].strip(), f"{row[0]} needs a decision date")
            self.assertTrue(row[3].strip(), f"{row[0]} needs a decider")
            self.assertNotIn("[assign", row[3], f"{row[0]} still holds a placeholder")

    def test_every_parked_feature_carries_one_sentence_of_reasoning(self):
        reasons = table_rows(section_of(self.markdown, "Why each is parked"))
        self.assertEqual(len(reasons), 6)
        for row in reasons:
            self.assertEqual(len(row), 2, row[0])
            self.assertTrue(row[1].strip(), f"{row[0]} needs a reason")


if __name__ == "__main__":
    unittest.main(verbosity=2)
