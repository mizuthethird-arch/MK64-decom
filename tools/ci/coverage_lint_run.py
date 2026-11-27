#!/usr/bin/env python3
"""Run the screen coverage lint over the blueprint catalogue and the authored plan.

A screen no task owns can never be built or proven, so it fails this check by name. The catalogue and
plan live outside the repository, so when they are absent this exits 2 and says so rather than passing.
"""

import json
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_UNCOVERED = 1
EXIT_NO_DATA = 2

SCREENS_MARKER = "const SCREENS="


def catalogue_ids(blueprint_text):
    start = blueprint_text.index(SCREENS_MARKER) + len(SCREENS_MARKER)
    depth = 0
    end = start
    while True:
        char = blueprint_text[end]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                break
        end += 1
    return [screen["id"] for screen in json.loads(blueprint_text[start:end + 1])]


def load(root):
    blueprint = root / "MK64-Native-Rebuild-Blueprint.html"
    tasks_path = root / "_bp_TASKS.json"
    detail_path = root / "_bp_DETAIL.json"
    missing = [str(p) for p in (blueprint, tasks_path, detail_path) if not p.is_file()]
    if missing:
        print(f"COVERAGE-SKIP: blueprint catalogue not present at {root}; missing {', '.join(missing)}", file=sys.stderr)
        print("The blueprint lives outside the repository, so this check runs only where it is mounted.", file=sys.stderr)
        return None
    return (blueprint.read_text(encoding="utf-8"),
            json.loads(tasks_path.read_text(encoding="utf-8")),
            json.loads(detail_path.read_text(encoding="utf-8")))


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("..")
    loaded = load(root)
    if loaded is None:
        return EXIT_NO_DATA
    blueprint_text, tasks, detail = loaded

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "docs"))
    from coverage_lint import coverage_report

    try:
        screen_ids = catalogue_ids(blueprint_text)
    except (ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"COVERAGE-FAIL: cannot read the screen catalogue from the blueprint: {error}", file=sys.stderr)
        return EXIT_UNCOVERED

    task_screens = {}
    for phase in tasks.values():
        for task in phase:
            task_screens[task["k"]] = detail.get(task["k"], {}).get("screens") or []

    report = coverage_report(screen_ids, task_screens)
    print(f"catalogue screens: {len(screen_ids)}")
    print(f"tasks naming screens: {sum(1 for v in task_screens.values() if v)} of {len(task_screens)}")

    if not report["covered"]:
        print(f"COVERAGE-FAIL: {len(report['reasons'])} problem(s):", file=sys.stderr)
        for reason in report["reasons"]:
            print(f"  {reason}", file=sys.stderr)
        return EXIT_UNCOVERED

    print(f"COVERAGE-OK: all {len(screen_ids)} screens are owned by at least one task")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
