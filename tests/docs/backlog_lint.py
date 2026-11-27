"""Lint for the blueprint task backlog against the session rules in docs/agent-rules.md.

The blueprint data lives outside src/ and is not shipped; the lint is given already-parsed task
records so it can run in the documentation suite without the blueprint present.
"""

MIN_HOURS = 0.5
MAX_HOURS = 3
MIN_STEPS = 4
MAX_STEPS = 7


def validate_backlog(tasks):
    """Returns a list of errors; an empty list means every task obeys the backlog rules."""
    errors = []
    known = {task["id"] for task in tasks}

    for task in tasks:
        task_id = task.get("id", "<no id>")
        hours = task.get("hours")
        if not isinstance(hours, (int, float)) or not MIN_HOURS <= hours <= MAX_HOURS:
            errors.append(f"{task_id}: hours {hours!r} outside {MIN_HOURS}..{MAX_HOURS}")

        steps = task.get("steps") or []
        if not MIN_STEPS <= len(steps) <= MAX_STEPS:
            errors.append(f"{task_id}: {len(steps)} steps, must be {MIN_STEPS}..{MAX_STEPS}")

        if not any(str(step).strip().upper().startswith("T") for step in steps):
            errors.append(f"{task_id}: no test step")

        for dependency in task.get("depends_on") or []:
            if dependency not in known:
                errors.append(f"{task_id}: depends on {dependency}, which is not in the backlog")
    return errors
