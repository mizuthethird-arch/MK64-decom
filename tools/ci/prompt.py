#!/usr/bin/env python3
"""Render one task prompt from the authored plan data, never hand-assembled.

The contract is tests/docs/task_render.py: given a task record and its detail record it produces the
task template, or fails naming every empty required field rather than emitting a prompt with a hole.
"""

import json
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_RENDER_FAILED = 1
EXIT_NO_DATA = 2


def load(root):
    tasks_path = root / "_bp_TASKS.json"
    detail_path = root / "_bp_DETAIL.json"
    missing = [str(p) for p in (tasks_path, detail_path) if not p.is_file()]
    if missing:
        print(f"RENDER-SKIP: plan data not present at {root}; missing {', '.join(missing)}", file=sys.stderr)
        print("The blueprint lives outside the repository, so rendering works only where it is mounted.", file=sys.stderr)
        return None
    return json.loads(tasks_path.read_text(encoding="utf-8")), json.loads(detail_path.read_text(encoding="utf-8"))


def find_task(tasks, details, task_id):
    for phase in tasks.values():
        for task in phase:
            if task.get("k") == task_id:
                return task, details.get(task_id, {})
    return None, None


def to_record(task, detail):
    return {
        "id": task["k"],
        "role": task["r"],
        "thread": task["k"],
        "hours": task["h"],
        "steps": [f"{kind}: {text}" for kind, text in detail.get("sub", [])],
        "done_when": detail.get("dw", ""),
        "screens": detail.get("screens") or [],
        "depends_on": detail.get("deps") or [],
        "title": task.get("t", ""),
    }


def main():
    if len(sys.argv) < 2:
        print("usage: prompt.py <task-id> [plan-root]", file=sys.stderr)
        print("  example: prompt.py T0025 ..", file=sys.stderr)
        return EXIT_RENDER_FAILED
    task_id = sys.argv[1]
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("..")

    loaded = load(root)
    if loaded is None:
        return EXIT_NO_DATA
    tasks, details = loaded

    task, detail = find_task(tasks, details, task_id)
    if task is None:
        print(f"RENDER-FAIL: task {task_id} is not in the plan", file=sys.stderr)
        return EXIT_RENDER_FAILED

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "docs"))
    from task_render import family_for, render

    record = to_record(task, detail)
    try:
        text = render(record, detail)
    except ValueError as error:
        print(f"RENDER-FAIL: {task_id} cannot be rendered: {error}", file=sys.stderr)
        return EXIT_RENDER_FAILED

    print(f"Title: {task.get('t', '')}")
    print(f"Family: {family_for(record['role'], detail)}")
    print(text, end="")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
