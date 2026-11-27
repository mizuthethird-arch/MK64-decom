# Prompt renderer

Prompts are generated from the plan data, never hand-assembled. The contract is
`tests/docs/task_render.py`: given a task record and its detail record it produces the
task template from `docs/task-template.md`, or fails naming every empty required field
instead of emitting a prompt with a hole.

## One command

```sh
python tools/ci/prompt.py T0001 ../blueprint
```

The second argument is the directory holding `_bp_TASKS.json` and `_bp_DETAIL.json`.
Omitted, it defaults to `..`, which is right when the plan sits beside the repository.

Output for `T0001` starts with the title and family, then the template:

```
Title: Write the scope and non-goals page
Family: engine
Role: LEG
Family: engine
Thread: T0001
Hours: 1
Scope: docs/scope.md, README.md

Steps:
T - Write a link check that fails while docs/scope.md is missing, then create the file with a header and the mode list only.
...
Done when:
docs/scope.md is merged, lists every in-scope mode ...
```

## Failure behaviour

| input | exit | message |
|---|---|---|
| no task id | 1 | `usage: prompt.py <task-id> [plan-root]` |
| an id not in the plan | 1 | `RENDER-FAIL: task T9999 is not in the plan` |
| a task with an empty required field | 1 | `RENDER-FAIL: <id> cannot be rendered: <field> is empty; ...` |
| plan data absent | 2 | `RENDER-SKIP: plan data not present at <path>; missing ...` |

Exit 0 is only ever produced after a successful render. Nothing is printed to stdout on
failure, so a broken render cannot be pasted into a task by accident.

## Why a script and not a template

A hand-assembled prompt drifts from the plan the moment a task changes. Rendering from
the same records `tests/docs/test_task_render.py` validates means a prompt and its lint
can never disagree: if the record is renderable the tests pass, and if it is not, both
the renderer and the lint say so with the same reason.

## Related runners

| script | role |
|---|---|
| `tools/ci/plan_lint_run.py` | runs the plan lint over the real data against a pinned violation baseline |
| `tools/ci/coverage_lint_run.py` | fails naming any screen in the catalogue that no task owns |
| `tools/ci/prompt.py` | renders one task prompt (this document) |
