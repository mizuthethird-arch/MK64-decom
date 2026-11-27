#!/usr/bin/env python3
"""Run the plan lint over the authored plan and fail on any violation outside the pinned baseline.

The plan data lives outside the repository, so when it is absent this exits 2 and says so. It never
exits 0 without having run the lint over real records, because a skipped check that reports success is
indistinguishable from a passing one.
"""

import json
import sys
from collections import Counter
from pathlib import Path

BASELINE_PROSE_DONE_WHEN = 412
BASELINE_UI_NO_SCREENS = 23
EXPECTED_TASKS = 1036

EXIT_OK = 0
EXIT_VIOLATIONS = 1
EXIT_NO_DATA = 2


def load(root):
    tasks_path = root / "_bp_TASKS.json"
    detail_path = root / "_bp_DETAIL.json"
    if not tasks_path.is_file() or not detail_path.is_file():
        missing = [str(p) for p in (tasks_path, detail_path) if not p.is_file()]
        print(f"PLAN-LINT-SKIP: plan data not present at {root}; missing {', '.join(missing)}", file=sys.stderr)
        print("The blueprint lives outside the repository, so this check runs only where it is mounted.", file=sys.stderr)
        return None
    return json.loads(tasks_path.read_text(encoding="utf-8")), json.loads(detail_path.read_text(encoding="utf-8"))


def records_for(tasks, details):
    records = []
    for phase in tasks.values():
        for task in phase:
            detail = details.get(task["k"], {})
            records.append({
                "id": task["k"],
                "role": task["r"],
                "thread": task["k"],
                "hours": task["h"],
                "steps": [f"{kind}: {text}" for kind, text in detail.get("sub", [])],
                "done_when": detail.get("dw", ""),
                "screens": detail.get("screens") or [],
                "depends_on": detail.get("deps") or [],
            })
    return records


def classify(violations):
    prose = [v for v in violations if "done_when is not measurable" in v]
    ui = [v for v in violations if "shell task must name its screens" in v]
    known = set(prose) | set(ui)
    other = [v for v in violations if v not in known]
    return prose, ui, other


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("..")
    loaded = load(root)
    if loaded is None:
        return EXIT_NO_DATA
    tasks, details = loaded

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "docs"))
    from plan_lint import validate_plan

    records = records_for(tasks, details)
    violations = validate_plan(records)
    prose, ui, other = classify(violations)

    print(f"records: {len(records)} (expected {EXPECTED_TASKS})")
    print(f"violations: {len(violations)}")
    print(f"  {len(prose):4d} prose done_when       (baseline {BASELINE_PROSE_DONE_WHEN})")
    print(f"  {len(ui):4d} UI task with no screens  (baseline {BASELINE_UI_NO_SCREENS})")
    print(f"  {len(other):4d} other")

    failed = False
    if len(records) != EXPECTED_TASKS:
        print(f"PLAN-LINT-FAIL: {len(records)} tasks, expected {EXPECTED_TASKS}", file=sys.stderr)
        failed = True
    if len(prose) > BASELINE_PROSE_DONE_WHEN:
        print(f"PLAN-LINT-FAIL: {len(prose)} prose done_when, baseline is {BASELINE_PROSE_DONE_WHEN}", file=sys.stderr)
        failed = True
    if len(ui) > BASELINE_UI_NO_SCREENS:
        print(f"PLAN-LINT-FAIL: {len(ui)} UI tasks with no screens, baseline is {BASELINE_UI_NO_SCREENS}", file=sys.stderr)
        failed = True
    if other:
        print(f"PLAN-LINT-FAIL: {len(other)} violation(s) outside the known kinds:", file=sys.stderr)
        for line in other:
            print(f"  {line}", file=sys.stderr)
        failed = True

    if failed:
        return EXIT_VIOLATIONS
    print("PLAN-LINT-OK: no violation outside the pinned baseline")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
