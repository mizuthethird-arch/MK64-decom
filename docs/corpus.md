# Corpus retention and storage policy

The corpus is the recorded reference data the parity claim is measured against: framebuffers, audio buffers, VI and RSP logs, save images and input traces. This page states how long it is kept, how large it may grow and how it is rebuilt.

## The retention rule

| Rule | Value |
|---|---|
| Retention | a recorded scene is kept until it is either superseded by a newer recording of the same scenario or pruned under this policy |
| Size ceiling | 20 GiB in total for the stored corpus |
| Growth | a recording that would push the corpus over the ceiling is pruned first, never stored over the limit |
| Immutability | a scene required by the release gate is never pruned, whatever the ceiling says |

## The size ceiling

20 GiB is the ceiling for the whole corpus: every scene, every artifact, every recorded minute.

| Situation | What happens |
|---|---|
| The corpus is under 20 GiB | recordings are added normally |
| The corpus is over 20 GiB | pruning is required before anything new is stored |
| Pruning cannot free enough because the release-gate scenes alone exceed the ceiling | the prune refuses, and the excess is reported with the largest scenes named, rather than silently deleting protected data |

The report names the largest scenes, so the decision about what to cut is made from numbers rather than from a directory listing.

## The release-gate exemption

A scene that the release gate depends on is immutable.

| Rule | Meaning |
|---|---|
| Never pruned | no retention operation may remove a release-gate scene |
| Refuse rather than guess | if freeing enough space would require removing one, the operation refuses and reports why |
| Recorded, not inferred | a scene is release-gate only when it is marked as such in the corpus index, never by guessing from its name |

## The regeneration path

The corpus is derived data, not source. It can always be rebuilt from the user's image and the recorded scenario scripts.

| Step | What it does |
|---|---|
| 1 | take the accepted image, per [rom-contract.md](rom-contract.md) |
| 2 | run the scenario scripts against the frozen oracle |
| 3 | record the artifacts defined in [parity.md](parity.md) |
| 4 | store them content-addressed, so the same buffer recorded twice costs one copy |
| 5 | record the scene's hash in the corpus index |

A corpus that cannot be regenerated this way is not a corpus this project keeps: the recordings are re-derivable, and the row order never matters.

## Sharing the corpus, and what CI may upload

The corpus is derived data, but it is derived from copyrighted game data. Sharing it is therefore a policy decision, not a convenience, and the CI job that uploads artifacts is the place where a mistake becomes permanent.

### What may be uploaded

Only audited artifacts leave the machine, and only these kinds:

| Shareable kind | What it is | Cap |
|---|---|---|
| hash | the per-artifact hashes of a run | none beyond the corpus ceiling |
| counter | frame counts, cycle counts, draw counters, dropped frames | none |
| log | a text log of a run or a comparison | 1 MiB, because a log is a report, not a payload |
| report | a summary of a comparison, in text | 1 MiB |

The list is an allowlist. A kind that is not on it is refused even if it looks harmless, so a new artifact kind cannot be uploaded by accident.

### What may never be uploaded

| Forbidden kind | Why |
|---|---|
| the game image | the image is the player's own copyrighted file; it never leaves their machine |
| any payload blob | a recording that embeds game bytes is the game data by another name |
| any extracted asset | a texture, display list, sample bank, sequence, track data or font taken from the image |
| any recording that embeds game bytes | a framebuffer dump or audio buffer is game data even when it is not a whole asset |
| any file whose kind is not on the allowlist | an unaudited artifact is refused rather than guessed |

One forbidden item blocks the entire upload. A partial upload of an audited set is worse than no upload, because the partial set looks complete.

### The audit-before-upload rule

The CI corpus job must run an **audit step before any upload step**, and a failed audit must block the upload.

| Requirement | Exact statement a reviewer can check |
|---|---|
| Ordering | the audit step runs before the upload step, and the upload step does not run when the audit fails |
| Decision | the audit applies the allowlist in `src/tests/docs/upload_audit.py` to the declared artifact list |
| Failure | a single forbidden, unknown or malformed item fails the job and names that item; nothing is uploaded |
| Empty list | an empty artifact list is refused, because an upload with nothing audited is not an audit |

The audit's own rules are executable today: `upload_audit.py` takes an artifact list and returns allowed or blocked with a named reason per item, and refuses the whole upload when any item is forbidden.

## What is stored, and what never is

| Stored | Never stored |
|---|---|
| artifact blobs, content-addressed | the game image |
| the scenario scripts | any extracted asset beyond what a scenario reads |
| a hash and metadata per row | a file path to the image |

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the ceiling, the refusal and the release-gate exemption | yes: `src/tests/docs/corpus_retention.py` is the policy as a pure function, and `src/tests/docs/test_corpus.py` checks the ceiling report, the pruning order and the refusal |
| the sharing allowlist and the audit decision | yes: `src/tests/docs/upload_audit.py` with `src/tests/docs/test_upload_audit.py`, covering the shareable kinds, every forbidden kind, one-item-blocks-all, and empty or malformed input |
| the audit-before-upload ordering in the workflow | not implemented: the corpus CI job does not exist yet, and the workflow files are outside the docs lane |
| the regeneration path | prose |
| the storage layout | prose |

The real corpus tool is built in a later phase and **is not yet implemented**. It must call the policy in `src/tests/docs/corpus_retention.py` for retention and `src/tests/docs/upload_audit.py` for sharing, rather than reimplementing either. Until it exists, both policies are proven by tests and nothing enforces them at run time.

## Related

- [parity.md](parity.md): the artifacts the corpus records
- [rom-contract.md](rom-contract.md): the accepted image the corpus is rebuilt from
- [backlog.md](backlog.md): where the corpus tool is scheduled
