# Documentation index

Every page that governs this repository, and the one thing to know about each. The rules page is the entry point for anyone doing work here.

## Read first

| Page | What it settles |
|---|---|
| [agent-rules.md](agent-rules.md) | how a task is sized, shaped and proven, and the two definitions of done |
| [task-template.md](task-template.md) | the shape every prompt and issue uses |
| [scope.md](scope.md) | what the rebuild ships, and every parked feature with its owner |
| [parity.md](parity.md) | what bit-exact means per artifact, the pyramid and who owns a mismatch |

## Contracts and policy

| Page | What it settles |
|---|---|
| [rom.md](rom.md) | the one accepted image and the rules that keep it out of git and out of every artifact |
| [rom-contract.md](rom-contract.md) | the exact acceptance rule, the byte orders and the refusal behaviour |
| [legal.md](legal.md) | the legal, asset and key policy in one page |
| [assets.md](assets.md) | the detailed no-assets and no-keys policy and its two guards |
| [rust-only.md](rust-only.md) | every shipped crate is Rust, and the one C++ exception that never ships |
| [parity-statement.md](parity-statement.md) | the single parity statement, included by reference everywhere else |
| [backlog.md](backlog.md) | the backlog, its critical path and the weekly review template |
| [corpus.md](corpus.md) | corpus retention, the 20 GiB ceiling and the release-gate exemption |
| [release.md](release.md) | the version scheme, the tag rule, hotfixes and the support window |
| [measurement.md](measurement.md) | the command behind every reported metric |
| [handover.md](handover.md) | the four-field handover note for every settled contract |

## Behaviour settled by recent tasks

These are the decisions a later agent would otherwise re-derive. Each one is enforced by a test.

| Behaviour | Where it is recorded | Enforced by |
|---|---|---|
| The backlog is generated from the authored task data, never hand-typed, and the lint rejects a task with the wrong step count, the wrong hours, no test step, or a dependency outside the backlog. | [backlog.md](backlog.md) | `src/tests/docs/backlog_lint.py` |
| A task that grows past three hours is split in the same session and both halves are recorded. | [backlog.md](backlog.md) | the backlog lint's step and hour bounds |
| A parked item must carry a feature, a No, a decision date and the decider, or the scope lint fails. | [scope.md](scope.md) | `src/tests/docs/test_scope_parked.py` |
| Two definitions of done exist. A shell task is proven by reachability, strings, failures and accessibility; an engine task is proven by hashes. A task touching both is owned by the engine definition (the engine definition of done wins). | [agent-rules.md](agent-rules.md) | `src/tests/docs/done_family.py` |
| The parity statement exists once, in [parity-statement.md](parity-statement.md), and every other page includes it by marker rather than paraphrasing it. | [parity-statement.md](parity-statement.md) | `src/tests/docs/test_parity_statement.py` |
| No page is named after the agent-file convention that some harnesses auto-load as instructions; the rules page is `agent-rules.md` for that reason. | [agent-rules.md](agent-rules.md) | `src/tests/docs/test_agents.py` |
| The corpus is capped at 20 GiB. A release-gate scene is never pruned, and a prune that cannot free enough space refuses and names the largest scenes. | [corpus.md](corpus.md) | `src/tests/docs/corpus_retention.py` |
| A release tag must be `vMAJOR.MINOR.PATCH` and must be an ancestor of the release branch. A hotfix is cut on `hotfix/vX.Y.Z` from the tag, never from the head of the release branch. | [release.md](release.md) | `src/tests/docs/release_tag.py` |
| Support window: only the latest MINOR and the versions inside its window are supported. A security fix is backported only inside the window, and there is no backport to unsupported versions. The bug report form requires the version and cites the support window. | [release.md](release.md) | `src/tests/docs/test_release.py` |
| An incident follows a written procedure: every withdrawal step names a command, an owner and a time limit, the only contact path is the GitHub security advisory contact, and a false report is answered without conceding the claim. The rehearsal is not done because no staging release exists. | [legal.md](legal.md) | `src/tests/docs/test_incident.py` |
| Every reported number has a command behind it, and a machine-dependent number is reported with its machine. A metric measured on one machine is stated as such. | [measurement.md](measurement.md) | `src/tests/docs/test_measurement.py` |
| A task prompt is rendered from the template, never hand-assembled, and an empty required field rejects the task instead of producing a prompt with a hole. All 1,036 authored tasks render. | [task-template.md](task-template.md) | `src/tests/docs/task_render.py` |
| Every settled contract carries a handover note naming producer, consumer, settled decisions and open questions. A consumer task reads it before starting and never starts from an unsettled contract. | [handover.md](handover.md) | `src/tests/docs/handover.py` |
| The plan lint checks the full rule set from the rules page and reports the real plan's violations rather than hiding them: 450 of 1,036 done conditions are prose without a measurable marker. | [agent-rules.md](agent-rules.md) | `src/tests/docs/plan_lint.py` |

## Toolkit follow-up needed

These items belong to the toolkit lane and are recorded here because the docs lane cannot do them.

| Item | Where it belongs |
|---|---|
| Wire the prompt renderer to the plan data and make it the source of every task prompt, so no prompt is hand-assembled. | `tools/prompt/README.md` |
| Run `src/tests/docs/plan_lint.py` over the plan data in CI, and fail the job on any violation other than the known unmeasurable done conditions. | the CI workflow |
| Read the blueprint `INTERFACES` registry at build time so `docs/handover.md` is generated rather than snapshotted. | the corpus or docs tooling |

## Prose and executable

Every page states which parts are executable and which are specification. Nothing on this list runs unless the page says it does.

