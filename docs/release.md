# Release cadence and version scheme

This page states how versions are numbered, what a tag must look like, how a hotfix is cut, and how long a release is supported.

## The version scheme

A version is `MAJOR.MINOR.PATCH`, tagged as `vMAJOR.MINOR.PATCH`. There are no prefixes, suffixes or build metadata in a tag: `v1.2.3` is a version, `v1.2.3-rc1` is not.

| Part | Bumped when |
|---|---|
| MAJOR | a change that a player must act on: a save format break, or a change that breaks an existing configuration |
| MINOR | a new behaviour, a newly proven mode or track set, or a parity claim that reaches a new artifact |
| PATCH | a fix that changes no promised behaviour: a bug fix, a performance fix, a documentation fix that ships |

| Example tag | Kind | Why |
|---|---|---|
| `v0.1.0` | minor | the first release that boots and proves one scenario |
| `v0.2.0` | minor | a new layer is proven |
| `v0.2.1` | patch | a fix to an already proven layer |
| `v1.0.0` | major | the first release that makes the full parity statement |
| `v1.1.0` | minor | a new mode or track set is proven |
| `v1.3.0` | minor | a further layer is proven, so the MINOR moves again |
| `v1.3.1` | patch | a fix inside an already proven area |

The tag format is not decoration: the release job reads it, and a tag it cannot parse stops the release before anything is built.

## The tag validation rule

A tag is valid only when both of these hold:

| Rule | Meaning |
|---|---|
| Well formed | the tag matches `vMAJOR.MINOR.PATCH` exactly |
| Reachable | the tagged commit is an ancestor of the release branch (`main`) |

A tag on a commit that is not an ancestor of `main` is refused. That case is how an untested branch gets released by accident: the commit builds, the tests that ran on it passed, but it carries work that never reached the release branch.

## The workflow step that must call it

The release job must validate the tag as its first step, before checkout of build inputs, before any build and before any artifact is produced.

| Order | Step | Behaviour on failure |
|---|---|---|
| 1 | `validate-release-tag` | the job stops, nothing is built, nothing is published |
| 2 | build | only reached when the tag validated |

That step does not exist yet, because there is no release workflow. The rule it must apply is executable today in `src/tests/docs/release_tag.py`: `validate_tag(tag, is_ancestor_of_release_branch)` returns `(ok, reason)`, and `src/tests/docs/test_release.py` proves that a malformed tag and a non-ancestor commit are both refused.

## Cutting a hotfix

A hotfix is cut from the release tag, never from the current head of `main`.

| Step | What happens |
|---|---|
| 1 | branch from the release tag: the branch is named `hotfix/vX.Y.Z` |
| 2 | make the smallest fix that solves the reported problem |
| 3 | bump PATCH: the new tag is `vX.Y.(Z+1)` |
| 4 | tag that commit, and validate it exactly like any other release |
| 5 | merge the fix back to `main` so the next release carries it |

A hotfix branch never carries unrelated work. If a fix needs more than a patch, it is a minor release cut from `main` instead.

## Version support window

| Release kind | Supported for |
|---|---|
| the latest MINOR release | until the next MINOR release ships, then a further 6 months |
| older MINOR releases | not supported once a newer MINOR has shipped |
| PATCH releases | share their MINOR's window; only the newest PATCH of a MINOR is supported |

A released version is supported while its window is open. A player who reports a bug on an unsupported version is told which version is supported and asked to reproduce there, and the report is closed as unsupported rather than silently ignored.

## Security fixes on an unsupported version

| Situation | Rule |
|---|---|
| A security fix lands | the fix is backported to every release inside its support window |
| The affected version is outside its window | there is no backport; the player is pointed at the supported release |

There is no policy of backporting security fixes to unsupported versions. That is stated plainly so that nobody assumes it is coming.

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the tag format and the ancestor rule | yes: `src/tests/docs/release_tag.py` with `src/tests/docs/test_release.py` |
| the hotfix branch naming | yes: `hotfix_branch` in the same module |
| the `validate-release-tag` workflow step | spec, not implemented: no release workflow exists and the workflow files are outside the docs lane |
| the support window and the backport rule | prose |
| the issue template that asks for the version | yes: `.github/ISSUE_TEMPLATE/bug_report.yml` |

## Related

- [measurement.md](measurement.md): how the numbers a release reports are produced
- [backlog.md](backlog.md): where the release workflow is scheduled
- [legal.md](legal.md): the incident procedure if a release contains something it should not
