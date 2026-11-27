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

## Prose and executable

Every page states which parts are executable and which are specification. Nothing on this list runs unless the page says it does.

