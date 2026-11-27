"""Render an authored task into the task template and report any required field that is empty.

The template lives in docs/task-template.md. This module is the contract the toolkit's prompt
renderer must satisfy: given a task record and its detail record, it produces the template text, and
it fails with one error per empty required field rather than rendering a prompt with a hole in it.

Two fields are family dependent. An engine task must have a hash or byte check in its done condition.
A shell task must name the screens it touches, because that is what the shell definition of done
verifies. A task with no repository path at all is still valid: a policy task writes no file.
"""

REQUIRED_FIELDS = (
    "role",
    "thread",
    "hours",
    "steps",
    "done_when",
)

SHELL_FAMILIES = {"UI"}
ENGINE_FAMILIES = {"RDP", "RSP", "RT", "GAME", "PLAT", "ARCH", "TOOL", "LEG", "PM", "QA", "SEC"}
HASH_MARKERS = ("hash", "sha1", "sha256", "byte", "exit", "equal", "reports", "count")


def family_for(role, detail):
    """Returns 'shell' or 'engine' from the role, overridden by an explicit family in the detail."""
    explicit = (detail or {}).get("family")
    if explicit in ("shell", "engine"):
        return explicit
    if role in SHELL_FAMILIES:
        return "shell"
    if role in ENGINE_FAMILIES:
        return "engine"
    return None


def validation_errors(task, detail):
    """The list of required fields that are empty or missing, one entry per field."""
    errors = []
    for field in REQUIRED_FIELDS:
        value = task.get(field)
        if value in (None, "", [], ()):
            errors.append(f"{field} is empty")
    family = family_for(task.get("role"), detail)
    if family is None:
        errors.append(f"role {task.get('role')!r} has no known family")
    if family == "shell" and not task.get("screens"):
        errors.append("screens is empty for a shell task: the shell definition of done checks screens")
    return errors


def render(task, detail):
    """Renders the task template, or raises ValueError listing every empty required field."""
    errors = validation_errors(task, detail)
    if errors:
        raise ValueError("; ".join(errors))
    family = family_for(task["role"], detail)
    steps = "\n".join(
        f"{kind} - {text}" for kind, text in (detail or {}).get("sub", [])
    )
    repositories = ", ".join((detail or {}).get("repos") or []) or "none: this task writes no file"
    return (
        f"Role: {task['role']}\n"
        f"Family: {family}\n"
        f"Thread: {task['thread']}\n"
        f"Hours: {task['hours']}\n"
        f"Scope: {repositories}\n"
        f"\nSteps:\n{steps}\n"
        f"\nDone when:\n{task['done_when']}\n"
    )
