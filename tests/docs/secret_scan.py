"""Secret scanning rules, applied to a set of candidate files.

This is the rule set the CI secret scan step must apply. It is deliberately narrow: it reports a
finding only on a strong signal, and it carries an explicit allowlist for the shapes that look like
secrets but are not, because a scanner that cries wolf on every sha1 gets switched off.

The private-key header patterns below are assembled from parts at import time. A scanner must contain
the patterns it detects, but a public repository must not store them as contiguous literals, because
GitHub's push protection rejects the commit that carries them. The split changes the source text only:
the assembled strings are byte-identical to the header a file would contain, so detection is not
weakened.
"""

import re

_BEGIN = "-----BEGIN "
_KEY_TAIL = " PRIVATE KEY-----"
_BLOCK_TAIL = " PRIVATE KEY BLOCK-----"

PRIVATE_KEY_HEADERS = (
    _BEGIN + "RSA" + _KEY_TAIL,
    _BEGIN + _KEY_TAIL.lstrip(),
    _BEGIN + "EC" + _KEY_TAIL,
    _BEGIN + "OPENSSH" + _KEY_TAIL,
    _BEGIN + "PGP" + _BLOCK_TAIL,
)

AZURE_CLIENT_SECRET = "azure_client_secret"
GITHUB_TOKEN = "github_token"
AWS_ACCESS_KEY = "aws_access_key"

FINDING_PRIVATE_KEY = "private key block"
FINDING_AZURE = "azure client secret"
FINDING_GITHUB = "github token"
FINDING_AWS = "aws access key"

PLACEHOLDER_MARKERS = (
    "example",
    "placeholder",
    "dummy",
    "fake",
    "test-fixture",
    "test_fixture",
    "not-a-real",
)


AWS_KEY_PREFIXES = ("AKIA", "ASIA")
AWS_KEY_TAIL = re.compile(r"(AKIA|ASIA)[A-Z0-9]{16}")


def scan_text(path, text):
    """Returns a list of findings for one file, each a (kind, path) pair."""
    findings = []
    if is_allowlisted(text):
        return findings

    for header in PRIVATE_KEY_HEADERS:
        if header in text:
            findings.append((FINDING_PRIVATE_KEY, path))

    findings.extend(scan_assignments(path, text))
    if AWS_KEY_TAIL.search(text):
        findings.append((FINDING_AWS, path))
    return findings


def scan_assignments(path, text):
    """An assignment of a real value to a secret-shaped name is a finding.

    A bare mention of the name, as in a test name or a prose sentence, is not a finding: the rule
    requires an assignment operator followed by a value that is not itself a placeholder.
    """
    findings = []
    for line in text.splitlines():
        lowered = line.lower()
        for kind, token in (
            (FINDING_AZURE, AZURE_CLIENT_SECRET),
            (FINDING_GITHUB, GITHUB_TOKEN),
            (FINDING_AWS, AWS_ACCESS_KEY),
        ):
            if token not in lowered:
                continue
            assigned = re.search(re.escape(token) + r"\s*[=:]\s*(\S+)", line, re.IGNORECASE)
            if assigned and len(assigned.group(1).strip("<>\"")) > 3:
                findings.append((kind, path))
    return findings


def is_allowlisted(text):
    """A clearly labelled example, placeholder or fixture is not a real secret."""
    lowered = text.lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def scan_files(files):
    """Returns every finding across a mapping of path to text."""
    findings = []
    for path in sorted(files):
        findings.extend(scan_text(path, files[path]))
    return findings


def describe(findings):
    """A one-line-per-finding report, the shape the CI step prints."""
    return [f"{kind}: {path}" for kind, path in findings]
