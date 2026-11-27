import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
SCOPE_PATH = SOURCE_ROOT / "docs" / "scope.md"
SCOPE_LINK = "docs/scope.md"
PINNED_IMAGE = (
    "python:3.12-slim@sha256:"
    "5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b"
)


def read(path):
    return path.read_text(encoding="utf-8")


def markdown_links(markdown):
    links = []
    for raw in markdown.splitlines():
        start = raw.find("](")
        while start >= 0:
            end = raw.find(")", start)
            links.append(raw[start + 2:end].strip())
            start = raw.find("](", end)
    return links


def relative_links(markdown):
    return [
        link
        for link in markdown_links(markdown)
        if not link.startswith(("http://", "https://", "#"))
    ]


class ScopeLinkTest(unittest.TestCase):
    def test_readme_links_to_the_scope_page(self):
        readme = SOURCE_ROOT / "README.md"
        self.assertTrue(readme.is_file(), f"{readme} must exist")
        self.assertIn(SCOPE_LINK, markdown_links(read(readme)))

    def test_every_relative_readme_link_resolves(self):
        readme = SOURCE_ROOT / "README.md"
        self.assertEqual(
            [link for link in relative_links(read(readme)) if not (SOURCE_ROOT / link).exists()], []
        )


class TestRunImageTest(unittest.TestCase):
    def test_the_documentation_runner_pins_one_image(self):
        self.assertIn(PINNED_IMAGE, read(SOURCE_ROOT / "tests" / "docs" / "run.sh"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
