# What a pull request may not contain

Every rule below is enforced by a check that runs on the pull request, or it says plainly that it is not yet enforced. A rule with no check is a wish, so each enforced rule names the job or tool that enforces it.

The jobs named here are the real ones in the CI workflow: **no ROM in tracked files**, **documentation suite**, **deep ROM content scan**, **rust toolchain image**, and **secret scan**.

## The rules

| # | Rule | Why | Enforcing check |
|---|---|---|---|
| 1 | No ROM or ROM image may be added, in any byte order | the image is the player's own copyrighted file, and shipping it is the one thing that would sink the project | no ROM in tracked files |
| 2 | No extracted asset may be added: no texture, display list, sample bank, sequence, track data, font or model | everything the game draws is read from the player's image at run time | deep ROM content scan (names any file carrying 96 bytes or more of the image); the fast structural guard in the documentation suite catches asset-like names and binary packages |
| 3 | No secret may be added: no private key, no token, no client secret, no credential | a committed secret is a leaked secret, even if it is deleted in a later commit | secret scan, enforced once that job lands: the job is being added by the toolkit lane, and the rule set it must apply is executable today in `src/tests/docs/secret_scan.py` |
| 4 | No licence-incompatible dependency may be added | every shipped dependency must be permissive, and the licence set is documented | not yet enforced: the rust toolchain image job builds the pinned image and verifies rustfmt and clippy, but performs no licence scan and no cargo-deny configuration exists. The eventual check is a cargo-deny licence check over the dependency tree once the first Cargo.toml exists |
| 5 | No C or C++ may reach a shipped artifact | the shipped program is 100% Rust; the only C++ is the frozen oracle, which never ships | not yet enforced, see [rust-only.md](rust-only.md) and the toolkit follow-up below |
| 6 | No test may be deleted, weakened or skipped to make a change pass | a green suite that no longer checks the thing is a false green | not yet enforced: the documentation suite fails on a zero-test run but cannot detect a deleted test. The follow-up is that the docs job must compare the discovered test count against the count on the base branch and fail if it decreased |
| 7 | No policy, hook, agent definition or CI workflow may be edited except by the owner | the rules must not be editable by the agent they constrain | not yet enforced; a reviewer check today |
| 8 | The pull request must reference a blueprint task id | every change traces to a planned task, or it is scope creep | not yet enforced; a reviewer check today |
| 9 | No unverified claim in the pull request body | a claim that was not run is worse than no claim | not yet enforced; a reviewer check today |

## What each check actually does

| Check | What it inspects |
|---|---|
| no ROM in tracked files | `git ls-files`, failing on any `rom/` path or any `.n64`, `.v64` or `.z64` file |
| documentation suite | the documentation tests, failing on an empty discovery and on any failure |
| deep ROM content scan | every file in the tree, compared against the user-supplied image |
| rust toolchain image | builds the pinned Rust image and verifies rustfmt and clippy work inside it. It performs no licence scan. |
| secret scan | gitleaks pinned by digest, blocking on every pull request; see [secrets.md](secrets.md) |

## Enforcement status

| Status | Rules |
|---|---|
| enforced | 1, 2 |
| enforced once the secret scan job lands | 3 |
| not yet enforced | 4, 5, 6, 7, 8, 9 |

## Rules that are not yet enforced

Six rules have no automatic check today. They are listed rather than dropped, because a rule nobody has automated is still a rule a reviewer applies, and labelling it honestly is better than claiming enforcement that does not exist.

| Rule | Toolkit follow-up needed |
|---|---|
| 4 | a cargo-deny licence check over the dependency tree, once the first Cargo.toml exists |
| 5 | a release-job step that runs the `nm` and `ldd` check from [rust-only.md](rust-only.md) against the shipped binary and fails on any C++ symbol |
| 6 | the documentation job must compare the discovered test count against the count on the base branch and fail if it decreased, so a deleted test cannot pass |
| 7 | a path-based check that fails a pull request touching the policy pages, hooks, agent definitions or workflows without an owner label |
| 8 | a pull request template field requiring a blueprint task id, validated by a job |
| 9 | a reviewer checklist item; no automatic check is proposed, because judging whether a claim was verified is not mechanical |

## Prose and executable

| Part of this page | Executable today |
|---|---|
| rules 1 and 2 | yes, each by a named CI job that exists today |
| rule 3 | the rule set is executable in `src/tests/docs/secret_scan.py`; the CI job that runs it is being added by the toolkit lane |
| rules 4, 5, 6, 7, 8 and 9 | prose only, marked "not yet enforced" above |
| the check descriptions in the middle table | prose, describing jobs that exist or are being added |
| the toolkit follow-ups | proposals, not implemented |

## Related

- [secrets.md](secrets.md): what counts as a secret and how the scan behaves
- [rust-only.md](rust-only.md): the C and C++ rule that rule 5 enforces
- [assets.md](assets.md): the asset classes rule 2 forbids
- [agent-rules.md](agent-rules.md): the rules a task must follow before it becomes a pull request
