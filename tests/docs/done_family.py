"""Which definition of done applies to a task, chosen by its role.

Shell tasks are proven by reachability, externalised strings, readable failures and accessibility
checks. Engine tasks are proven by hashes. A task that touches both is owned by the engine definition,
because a hash failure is objective and must never be waived by a shell checklist.
"""

SHELL_ROLES = {"UI"}
ENGINE_ROLES = {"RDP", "RSP", "RT", "GAME", "PLAT", "ARCH", "TOOL", "LEG", "PM", "QA"}


def family_of_role(role):
    """Returns "shell" or "engine" for a known role, and None for an unknown one."""
    if role in SHELL_ROLES:
        return "shell"
    if role in ENGINE_ROLES:
        return "engine"
    return None


def definition_of_done_for(role, touches_engine=False):
    """Returns the name of the definition of done the task must satisfy."""
    family = family_of_role(role)
    if family is None:
        raise ValueError(f"unknown role: {role}")
    if family == "engine" or touches_engine:
        return "engine definition of done (hashes)"
    return "shell definition of done (reachability, strings, failures, accessibility)"
