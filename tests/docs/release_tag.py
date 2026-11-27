"""Release tag parsing and validation.

There is no release workflow yet and the workflow files are not in the docs lane, so the rule lives
here as a tested pure function that the future workflow step must call.
"""

import re

SCHEME_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
MINOR_RELEASE = "vMAJOR.MINOR.0"
PATCH_RELEASE = "vMAJOR.MINOR.PATCH"
RELEASE_BRANCH = "main"
HOTFIX_PREFIX = "hotfix/"


def parse_tag(tag):
    """Returns (major, minor, patch) for a valid tag, or None when the tag is malformed."""
    match = SCHEME_PATTERN.match(tag or "")
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def validate_tag(tag, is_ancestor_of_release_branch):
    """Returns (ok, reason). A tag must be well formed and reachable from the release branch."""
    if parse_tag(tag) is None:
        return False, f"malformed tag: {tag!r} does not match vMAJOR.MINOR.PATCH"
    if not is_ancestor_of_release_branch:
        return False, f"commit for {tag} is not an ancestor of {RELEASE_BRANCH}"
    return True, "ok"


def release_kind(tag):
    """Returns 'patch', 'minor' or None for a well-formed tag."""
    parsed = parse_tag(tag)
    if parsed is None:
        return None
    major, minor, patch = parsed
    return "patch" if patch else "minor"


def hotfix_branch(tag):
    """The branch a hotfix is cut on, or None for a malformed tag."""
    return None if parse_tag(tag) is None else f"{HOTFIX_PREFIX}{tag}"
