# Backlog and critical path

The backlog is the plan's task data: every task with its role, its hours, its steps and its dependencies. This page records how that data is turned into a readable backlog, which tasks are on the critical path, and how the backlog is reviewed each week.

## Where the backlog comes from

| Item | Value |
|---|---|
| Source of truth | the blueprint task data, outside this repository, parsed as JSON |
| Tasks in the plan | 1,036 |
| Phases | 14 |
| Steps per task | 4 or 5 |
| Hours per task | 0.5 to 3 |
| Dependencies pointing outside the plan | 0 |

The backlog is generated, never hand-typed, so it cannot drift from the plan.

## How it is generated

The generator reads the plan's task records and emits this page's tables. It is deliberately a separate step from the documentation suite, because the plan data is not shipped with this repository and a public checkout does not have it.

```sh
# Generate docs/backlog.md from the plan data.
# Exit 0 means the backlog was regenerated and every task passed the backlog lint.
python tools/generate-backlog.py --plan _bp_TASKS.json --detail _bp_DETAIL.json --out docs/backlog.md
```

A task record carries these fields, which are exactly the fields the lint checks:

| Field | Meaning | Rule |
|---|---|---|
| `id` | the task id, for example `T0013` | unique |
| `role` | the owning lane | one of the lanes in the plan |
| `hours` | the budgeted hours | 0.5 to 3 |
| `steps` | the steps, each starting with a kind letter | 4 to 7, at least one `T` step |
| `depends_on` | the ids this task waits for | every id must exist in the backlog |

## The critical path

The critical path is the chain of tasks where a slip moves the whole plan. It is computed from the data, not chosen by hand.

| Order | Task | Why it is on the path |
|---|---|---|
| 1 | T0002 verify the ROM pin | every parity claim is measured against one image |
| 2 | T0005 freeze the oracle contract | every comparison needs a frozen reference |
| 3 | T0006 define bit-exact | the comparison rules before any comparison |
| 4 | T0008 parity order and layer gates | which layer is at fault before anyone fixes a bug |

The chain is marked in the generated table with a `critical` column. A task is critical when its own finish date, plus every dependent's duration, equals the longest possible chain in the plan.

## Weekly review template

Every week the review asks for measured hours, never estimates.

| Question | Answer |
|---|---|
| Which tasks finished since the last review? | task ids and the date each was marked done |
| What did each take, measured? | the recorded hours per task, from the task's own evidence log |
| Where does the measured time differ from the budget, and by how much? | the difference per task, in hours |
| Which tasks are on the critical path and are they on time? | the critical tasks and whether each is ahead or behind |
| What blocked, and what unblocked it? | the blocker, who cleared it, and when |

A review that reports an estimate instead of a measured number is not a review. The measurement comes from the task's recorded evidence, and a task with no evidence is reported as unknown rather than guessed.

## When a task grows past three hours

A task that is still not done after three hours is split, in the same session, not carried forward as one oversized task.

| Step | What happens |
|---|---|
| 1 | stop at the three hour mark |
| 2 | record both halves as their own tasks, each with its own hours budget, its own steps and its own done condition |
| 3 | record what the first half actually finished, in hours and in output, so the second half starts from evidence |
| 4 | the second half's first step is a `T` step like any other task |

Both halves keep the backlog rules: 4 to 7 steps, 0.5 to 3 hours, at least one test step, and no dependency outside the backlog. Splitting a task never produces a task that the lint would reject.

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the backlog fields and their rules | yes: `src/tests/docs/backlog_lint.py` rejects a task that breaks any of them |
| the weekly review template | prose |
| the critical path rule | prose, computed from the data when the generator exists |
| the three hour split rule | prose, enforced after the fact by the lint's step and hour bounds |
| the generator command above | specification, not yet implemented: `tools/generate-backlog.py` does not exist, and the plan data is not shipped in this repository |

The counts in the first table were read from the plan data on 2026-11-27 and are recorded here as a snapshot. When the generator exists, they are produced by it rather than typed.

## Related

- [agent-rules.md](agent-rules.md): the rules a task must follow
- [scope.md](scope.md): what the plan is building
- [parity.md](parity.md): what a measurable done condition means
