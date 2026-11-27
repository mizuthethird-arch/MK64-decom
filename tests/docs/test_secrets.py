import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from secret_scan import (
    FINDING_AWS,
    FINDING_AZURE,
    FINDING_GITHUB,
    FINDING_PRIVATE_KEY,
    describe,
    scan_files,
    scan_text,
)

SOURCE_ROOT = Path(__file__).resolve().parents[2]
SECRETS_DOC = SOURCE_ROOT / "docs" / "secrets.md"
DOC_INDEX = SOURCE_ROOT / "docs" / "README.md"
README = SOURCE_ROOT / "README.md"


def _credential(*parts):
    """Builds a credential shape at run time so the public repository never stores a literal secret-shaped string."""
    return "".join(parts)


RSA_HEADER = _credential("-----BEGIN RSA ", "PRIVATE KEY-----")
RSA_FOOTER = _credential("-----END RSA ", "PRIVATE KEY-----")
EC_HEADER = _credential("-----BEGIN EC ", "PRIVATE KEY-----")
OPENSSH_HEADER = _credential("-----BEGIN OPENSSH ", "PRIVATE KEY-----")
AWS_TEST_KEY = _credential("AKIA", "ZZ7Q4TEST6KEY9ZZ")

PRIVATE_KEY_FIXTURE = (
    "some text\n" + RSA_HEADER + "\n"
    "MIIEowIBAAKCAQEA0000000000000000000000000000000000000000000000\n"
    + RSA_FOOTER + "\n"
)

AZURE_FIXTURE = "AZURE_CLIENT_SECRET=abc123def456ghi789jkl012\n"
SHA1_FIXTURE = "sha1 = f6b5f519dd57ea59e9f013cc64816e9d273b2329\n"
PLACEHOLDER_FIXTURE = "AZURE_CLIENT_SECRET=<example placeholder value>\n"
BASE64_FIXTURE = "test-fixture base64: QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo=\n"


class PrivateKeyTest(unittest.TestCase):
    """T0011 sub-step T: a private key block in a file is a finding."""

    def test_a_private_key_block_is_reported(self):
        findings = scan_text("leaked.pem", PRIVATE_KEY_FIXTURE)
        self.assertIn((FINDING_PRIVATE_KEY, "leaked.pem"), findings)

    def test_every_private_key_header_variant_is_reported(self):
        for header in (
            _credential("-----BEGIN ", "PRIVATE KEY-----"),
            EC_HEADER,
            OPENSSH_HEADER,
        ):
            with self.subTest(header=header):
                self.assertEqual(len(scan_text("k.txt", header)), 1)

    def test_a_bare_key_header_with_no_body_is_still_reported(self):
        self.assertEqual(len(scan_text("k.txt", _credential("-----BEGIN ", "PRIVATE KEY-----"))), 1)


class AzureSecretTest(unittest.TestCase):
    def test_an_azure_client_secret_is_reported(self):
        findings = scan_text("ci.env", AZURE_FIXTURE)
        self.assertIn((FINDING_AZURE, "ci.env"), findings)

    def test_a_github_token_is_reported(self):
        self.assertEqual(len(scan_text("x.txt", "github_token: abcdef")), 1)

    def test_an_aws_access_key_is_reported(self):
        findings = scan_text("x.txt", "aws_access_key = " + AWS_TEST_KEY)
        self.assertIn((FINDING_AWS, "x.txt"), findings)

    def test_an_aws_key_id_prefix_is_reported_on_its_own(self):
        self.assertEqual(len(scan_text("x.txt", AWS_TEST_KEY)), 1)

    def test_a_placeholder_aws_key_is_not_a_finding(self):
        self.assertEqual(scan_text("docs/x.md", "aws_access_key = <example placeholder>"), [])


class FalsePositiveTest(unittest.TestCase):
    """T0011 sub-step E: shapes that look like secrets but must not fail the scan."""

    def test_a_sha1_literal_is_not_a_finding(self):
        self.assertEqual(scan_text("rom.md", SHA1_FIXTURE), [])

    def test_a_named_placeholder_is_not_a_finding(self):
        self.assertEqual(scan_text("secrets.md", PLACEHOLDER_FIXTURE), [])

    def test_a_clearly_named_base64_test_fixture_is_not_a_finding(self):
        self.assertEqual(scan_text("fixture.txt", BASE64_FIXTURE), [])

    def test_example_values_in_the_docs_are_not_findings(self):
        self.assertEqual(scan_text("docs/secrets.md", "set it to <example value>"), [])

    def test_a_clean_text_file_has_no_findings(self):
        self.assertEqual(scan_text("README.md", "# title\n\nplain prose\n"), [])


class ScanFilesTest(unittest.TestCase):
    def test_findings_across_files_are_all_reported(self):
        findings = scan_files({"a.pem": PRIVATE_KEY_FIXTURE, "b.env": AZURE_FIXTURE, "c.txt": "clean"})
        self.assertEqual(len(findings), 2)

    def test_a_clean_file_set_has_no_findings(self):
        self.assertEqual(scan_files({"a.txt": "clean", "b.md": SHA1_FIXTURE}), [])

    def test_describe_renders_one_line_per_finding(self):
        lines = describe(scan_files({"a.pem": PRIVATE_KEY_FIXTURE}))
        self.assertEqual(len(lines), 1)
        self.assertIn("a.pem", lines[0])


class SecretsDocTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SECRETS_DOC.is_file(), f"{SECRETS_DOC} must exist")
        self.text = SECRETS_DOC.read_text(encoding="utf-8")

    def test_lists_every_secret_with_storage_owner_rotation_and_failure(self):
        for field in ("Storage", "Owner", "Rotation", "If missing or leaked"):
            self.assertIn(field, self.text, field)

    def test_names_the_windows_signing_key(self):
        self.assertIn("signing", self.text.lower())

    def test_states_the_rom_is_not_a_secret_but_is_never_committed(self):
        lowered = self.text.lower()
        self.assertIn("not a secret", lowered)
        self.assertIn("never committed", lowered)

    def test_states_the_no_secret_in_repo_rule(self):
        self.assertIn("no secret", self.text.lower())

    def test_states_the_ci_requirement_precisely(self):
        lowered = self.text.lower()
        self.assertIn("gitleaks", lowered)
        self.assertIn("digest", lowered)
        self.assertIn("mk64_history_scan", lowered)
        self.assertIn("private-key", lowered)

    def test_names_the_scan_step_the_jobs_run(self):
        self.assertIn("secret scan", self.text.lower())

    def test_marks_prose_versus_executable(self):
        self.assertIn("prose", self.text.lower())

    def test_contains_no_live_secret_shape(self):
        self.assertNotIn(RSA_HEADER, self.text)
        self.assertNotRegex(self.text, r"[\w.+-]+@[\w-]+\.[\w.]+")


class SecretsLinkTest(unittest.TestCase):
    def test_is_linked_from_the_readme(self):
        self.assertIn("secrets.md", README.read_text(encoding="utf-8"))

    def test_is_linked_from_the_docs_index(self):
        self.assertIn("secrets.md", DOC_INDEX.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
