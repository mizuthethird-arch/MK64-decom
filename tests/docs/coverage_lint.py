"""Coverage of the screen catalogue by authored tasks.

Every screen in the blueprint catalogue must be owned by at least one task, or it can never be built
and never be proven. A screen owned by one task and a screen owned by many are both fine; a screen
owned by none fails, naming it.
"""


def ownership(screen_ids, task_screens):
    """Maps each screen id to the task ids that name it, in the order the tasks were given."""
    owned = {screen: [] for screen in screen_ids}
    for task_id, screens in task_screens.items():
        for screen in screens or []:
            if screen in owned:
                owned[screen].append(task_id)
    return owned


def unowned_screens(screen_ids, task_screens):
    """The screen ids that no task names."""
    owned = ownership(screen_ids, task_screens)
    return [screen for screen in screen_ids if not owned[screen]]


def unknown_screens(screen_ids, task_screens):
    """The screen ids a task names that are not in the catalogue: a typo or a stale name."""
    catalogue = set(screen_ids)
    unknown = set()
    for screens in task_screens.values():
        for screen in screens or []:
            if screen not in catalogue:
                unknown.add(screen)
    return sorted(unknown)


def coverage_report(screen_ids, task_screens):
    """A dict describing the coverage, with a named reason for every failure."""
    if not isinstance(screen_ids, list) or not screen_ids:
        return {
            "covered": False,
            "reasons": ["the screen catalogue is empty or not a list: nothing can be proven"],
            "ownership": {},
        }
    if not isinstance(task_screens, dict):
        return {
            "covered": False,
            "reasons": [f"task screens are not a mapping, got {type(task_screens).__name__}"],
            "ownership": {},
        }

    owned = ownership(screen_ids, task_screens)
    reasons = []
    for screen in screen_ids:
        if not owned[screen]:
            reasons.append(f"screen {screen!r} is owned by no task")
    for screen in unknown_screens(screen_ids, task_screens):
        reasons.append(f"screen {screen!r} is named by a task but is not in the catalogue")
    return {"covered": not reasons, "reasons": reasons, "ownership": owned}
