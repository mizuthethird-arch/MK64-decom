import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
SCOPE_PATH = SOURCE_ROOT / "docs" / "scope.md"
SCOPE_LINK = "docs/scope.md"

IN_SCOPE_HEADINGS = (
    "In scope: modes",
    "In scope: tracks",
    "In scope: arenas",
    "In scope: characters",
    "In scope: items",
    "In scope: time trial ghosts",
    "In scope: save files",
    "In scope: options screens",
    "In scope: the shell around it",
    "In scope: builds",
)
PARKED_HEADING = "Parked: not in this rebuild"
CROSSING_TERMS = ("netplay", "texture", "macos", "mobile", "achievement")


def read_scope():
    return SCOPE_PATH.read_text(encoding="utf-8")


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


def parked_features(markdown):
    return [row[0] for row in table_rows(section_of(markdown, PARKED_HEADING))]


def in_scope_names(markdown):
    names = []
    for heading in IN_SCOPE_HEADINGS:
        rows = table_rows(section_of(markdown, heading))
        names.extend(cell for row in rows for cell in row)
    return names


class DuplicateScopeTest(unittest.TestCase):
    def test_no_in_scope_name_is_listed_twice(self):
        names = in_scope_names(read_scope())
        self.assertNotEqual(names, [], "the in-scope lists must have rows")
        self.assertEqual(sorted({name for name in names if names.count(name) > 1}), [])

    def test_no_parked_feature_is_listed_twice(self):
        features = parked_features(read_scope())
        self.assertNotEqual(features, [], "the parked list must have rows")
        self.assertEqual(sorted({name for name in features if features.count(name) > 1}), [])

    def test_no_parked_feature_appears_in_the_in_scope_lists(self):
        parked_lower = {name.lower() for name in parked_features(read_scope())}
        clashes = [name for name in in_scope_names(read_scope()) if name.lower() in parked_lower]
        self.assertEqual(clashes, [])

    def test_no_in_scope_section_names_a_parked_crossing_feature(self):
        markdown = read_scope()
        suspected = {}
        for heading in IN_SCOPE_HEADINGS:
            text = section_of(markdown, heading).lower()
            hits = [term for term in CROSSING_TERMS if term in text]
            if hits:
                suspected[heading] = hits
        self.assertEqual(suspected, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
