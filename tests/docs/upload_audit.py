"""Decide what the corpus CI job may upload.

The audited artifact list is an allowlist, not a blocklist: a kind that is not explicitly shareable is
blocked, so a new artifact kind cannot be uploaded by default. One forbidden item blocks the entire
upload, because a partial upload of an audited set is worse than no upload.

This is the policy the workflow's audit step must apply. The workflow itself is not in the docs lane.
"""

SHAREABLE_KINDS = (
    "hash",
    "counter",
    "log",
    "report",
)

FORBIDDEN_KINDS = (
    "rom",
    "payload",
    "asset",
    "recording",
    "blob",
)

REASON_ALLOWED = "shareable: {kind}"
REASON_FORBIDDEN = "forbidden kind {kind!r}: never uploaded"
REASON_UNKNOWN = "unknown kind {kind!r}: not on the shareable allowlist"
REASON_MISSING_KIND = "artifact {name!r} has no kind"
REASON_NOT_A_LIST = "artifact list is not a list, got {type}"
REASON_EMPTY = "artifact list is empty: an upload with nothing audited is refused"
REASON_BLOCKED = "upload blocked because {blocked} artifact(s) failed the audit"

MAX_REPORT_BYTES = 1024 * 1024


def audit_artifact(artifact):
    """Returns (allowed, reason) for one artifact item."""
    if not isinstance(artifact, dict):
        return False, REASON_UNKNOWN.format(kind=type(artifact).__name__)
    name = artifact.get("name", "<unnamed>")
    kind = artifact.get("kind")
    if not kind:
        return False, REASON_MISSING_KIND.format(name=name)
    if kind in FORBIDDEN_KINDS:
        return False, REASON_FORBIDDEN.format(kind=kind)
    if kind not in SHAREABLE_KINDS:
        return False, REASON_UNKNOWN.format(kind=kind)
    size = artifact.get("bytes")
    if isinstance(size, int) and size > MAX_REPORT_BYTES and kind in ("report", "log"):
        return False, f"artifact {name!r} is {size} bytes, over the {MAX_REPORT_BYTES} byte cap for {kind}"
    return True, REASON_ALLOWED.format(kind=kind)


def audit_upload(artifacts):
    """Returns a dict with allowed, blocked and the reasons; the upload is permitted only if blocked is empty."""
    if not isinstance(artifacts, list):
        return {
            "allowed": False,
            "blocked": [],
            "reasons": [REASON_NOT_A_LIST.format(type=type(artifacts).__name__)],
        }
    if not artifacts:
        return {"allowed": False, "blocked": [], "reasons": [REASON_EMPTY]}

    reasons = []
    blocked = []
    for artifact in artifacts:
        allowed, reason = audit_artifact(artifact)
        reasons.append(reason)
        if not allowed:
            blocked.append(artifact.get("name") if isinstance(artifact, dict) else artifact)

    if blocked:
        reasons.append(REASON_BLOCKED.format(blocked=len(blocked)))
    return {"allowed": not blocked, "blocked": blocked, "reasons": reasons}
