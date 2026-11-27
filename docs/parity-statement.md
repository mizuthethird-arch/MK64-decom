# The parity statement

This is the single statement of what the rebuild claims. It lives here and only here. Every other page includes it by writing the marker `{{include:parity-statement}}` rather than paraphrasing it, because a claim repeated in two places drifts into two different claims.

## The statement

> MK64 Native Rebuild is a from-scratch reimplementation of Mario Kart 64 (Europe) (Rev A) for Windows and Linux. For the recorded scenario set it is bit-exact against the frozen reference: the framebuffer, the audio buffers, the VI and RSP logs, the save image and the input frames all match byte for byte. The statement is about the scenario set that has been recorded and proven, not about the whole game: it states coverage, and it is not a promise about behaviour that has not been recorded and compared. The game image is user supplied; the rebuild ships none. Display scaling, aspect ratio and presentation rate are outside this claim: they are documented deviations with their own opt-in flags, listed in the deviations table in [parity.md](parity.md), and the claim is made about runs where they are off. This project is not affiliated with, endorsed by or sponsored by Nintendo. Mario Kart 64 is a trademark of Nintendo.

## What the statement refers to

| Reference | Where it is defined |
|---|---|
| the scenario set | [parity.md](parity.md), the six artifacts and the recorded scenarios that produce them |
| the deviations list | [parity.md](parity.md), the deviations allowed by design and their opt-in flags |
| the accepted image | [rom.md](rom.md) and [rom-contract.md](rom-contract.md) |
| the asset and key policy | [legal.md](legal.md) and [assets.md](assets.md) |

## Using the statement

| Rule | Meaning |
|---|---|
| One copy | the exact words live in this page only |
| Include by marker | another page that needs the statement writes `{{include:parity-statement}}` |
| Never paraphrase | a shortened or reworded version is a defect, because two versions of a claim are two claims |
| Quote it whole | a release note, the legal screen and the release page all carry the full statement, not parts of it |

## Coverage, not a promise

A release may be partially proven. When it is, the statement still says "for the recorded scenario set", and the release records which scenarios were included. The statement never promises that untested behaviour matches.

| Situation | What the release says |
|---|---|
| Every recorded scenario passes | the full statement |
| Some scenarios are unproven | the full statement, plus the list of scenarios not yet recorded |
| A scenario regressed | the full statement is not used; the release names the failure instead |

## Affiliation check

Every phrase of the statement was checked against [legal.md](legal.md) for wording that could be read as affiliation with Nintendo.

| Check | Result |
|---|---|
| Names a trademark without a disclaimer | no: the statement names Mario Kart 64 and states it is a trademark of Nintendo |
| Claims endorsement, sponsorship or approval | no: the statement says the project is not affiliated with, endorsed by or sponsored by Nintendo |
| Implies the project distributes game data | no: the statement says the image is user supplied and the rebuild ships none |
| Implies a complete reimplementation of the whole game | no: the statement limits the claim to the recorded scenario set |

This check was performed by reading the statement against [legal.md](legal.md) phrase by phrase. It was not reviewed by an outside reviewer, and no reviewer is claimed.

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the statement text | prose |
| the one-copy rule and the no-paraphrase rule | yes: `src/tests/docs/test_parity_statement.py` fails when a page contains a paraphrase without the include marker |
| the include marker | specification, not yet implemented: nothing expands `{{include:parity-statement}}` yet, so a page carrying the marker renders it literally until the docs build expands it |
| the affiliation check | prose, recorded here as performed by reading, not by a tool |

## Related

- [parity.md](parity.md): the artifacts, the pyramid and the deviations
- [legal.md](legal.md): the legal, asset and key policy
- [rom.md](rom.md): the accepted image
