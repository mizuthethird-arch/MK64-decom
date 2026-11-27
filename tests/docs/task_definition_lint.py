"""Lint for authored task definitions against the session rules in docs/agent-rules.md.

A task definition is a plain dict. The rules are: 0.5 up to but not including 3 hours, 4 to 7 steps,
the first step is a failing test, and the done condition is a hash or a measurable check.
"""

MIN_HOURS = 0.5
MAX_HOURS = 3
MIN_STEPS = 4
MAX_STEPS = 7
MEASURABLE_MARKERS = ("hash", "exit", "count", "sha1", "equals", "measured", "reports", "zero", "byte")


def validate(definition):
    """Returns a list of human-readable errors; an empty list means the definition follows the rules."""
    errors = []
    hours = definition.get("hours")
    if not isinstance(hours, (int, float)) or not MIN_HOURS <= hours < MAX_HOURS:
        errors.append(f"hours must be at least {MIN_HOURS} and under {MAX_HOURS}, got {hours!r}")

    steps = definition.get("steps") or []
    if not MIN_STEPS <= len(steps) <= MAX_STEPS:
        errors.append(f"steps must number between {MIN_STEPS} and {MAX_STEPS}, got {len(steps)}")
    elif steps and not str(steps[0]).lstrip().lower().startswith("t"):
        errors.append("the first step must be a failing test (a T step)")

    done_when = str(definition.get("done_when") or "").lower()
    if not any(marker in done_when for marker in MEASURABLE_MARKERS):
        errors.append(
            "done_when must be a hash or a measurable check, got: " + (done_when or "<empty>")
        )

    if not definition.get("role"):
        errors.append("role is required")
    return errors
