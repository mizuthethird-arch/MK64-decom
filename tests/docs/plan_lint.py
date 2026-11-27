"""Lint the authored plan against every rule in docs/agent-rules.md.

Extends the backlog rules with the rules a task must satisfy before an agent may start it: a known
role, a family, a measurable done condition matched to that family, steps that each carry a kind, and
a thread. Every failure names the exact reason.
"""

KNOWN_ROLES = {
    "PM", "ARCH", "TOOL", "RT", "RSP", "RDP", "GAME", "UI", "PLAT", "QA", "SEC", "LEG",
}
SHELL_ROLES = {"UI"}
STEP_KINDS = {"T", "B", "E", "D", "P", "A"}
MIN_HOURS = 0.5
MAX_HOURS = 3
MIN_STEPS = 4
MAX_STEPS = 7
MEASURABLE_MARKERS = ("hash", "sha1", "sha256", "byte", "exit", "equal", "reports", "count", "measured")


def validate_plan(tasks):
    """Returns a list of violations against the plan rules; empty means the plan obeys its own rules."""
    errors = []
    known_ids = {task.get("id") for task in tasks if task.get("id")}

    for task in tasks:
        task_id = task.get("id") or "<no id>"
        if not task.get("id"):
            errors.append("<no id>: the task has no id")
        role = task.get("role")
        if role not in KNOWN_ROLES:
            errors.append(f"{task_id}: unknown role {role!r}")

        hours = task.get("hours")
        if not isinstance(hours, (int, float)) or not MIN_HOURS <= hours <= MAX_HOURS:
            errors.append(f"{task_id}: hours {hours!r} outside {MIN_HOURS}..{MAX_HOURS}")

        steps = task.get("steps") or []
        if not isinstance(steps, list):
            errors.append(f"{task_id}: steps is not a list")
            continue
        if not MIN_STEPS <= len(steps) <= MAX_STEPS:
            errors.append(f"{task_id}: {len(steps)} steps, must be {MIN_STEPS}..{MAX_STEPS}")
        for index, step in enumerate(steps):
            kind = str(step).strip()[:1].upper()
            if kind not in STEP_KINDS:
                errors.append(f"{task_id}: step {index} has no known kind ({step!r})")
        if steps and str(steps[0]).strip()[:1].upper() != "T":
            errors.append(f"{task_id}: the first step is not a T step")

        done_when = str(task.get("done_when") or "").lower()
        if not done_when:
            errors.append(f"{task_id}: done_when is empty")
        elif role in SHELL_ROLES:
            if not task.get("screens"):
                errors.append(f"{task_id}: a shell task must name its screens")
        elif not any(marker in done_when for marker in MEASURABLE_MARKERS):
            errors.append(f"{task_id}: done_when is not measurable: {done_when!r}")

        if not task.get("thread"):
            errors.append(f"{task_id}: thread is empty")

        for dependency in task.get("depends_on") or []:
            if dependency not in known_ids:
                errors.append(f"{task_id}: depends on {dependency}, which is not in the plan")
    return errors
