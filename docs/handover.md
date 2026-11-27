# Contract handover notes

A contract is handed from its producer to its consumer. This page records, for every settled contract, who produces it, who consumes it, what was decided, and what is still open. A consumer task reads the note before it starts, so it never re-derives a contract from scratch.

## Where the contract list comes from

The contract list is the `INTERFACES` registry in the blueprint at the repository root, read on 2026-11-27. It names **22 contracts**. That registry is outside `src/` and is not shipped, so this page records the settled subset rather than re-deriving it at run time.

Two of the 22 are settled and carry a full note. The rest are listed with their producer and consumer lanes so nobody assumes a settled contract where there is none.

## Settled contracts

A settled contract has a handover note with all four fields, enforced by `src/tests/docs/handover.py` and `src/tests/docs/test_handover.py`.

| Contract | Producer | Consumer | Settled decisions | Open questions |
|---|---|---|---|---|
| IMP-ROM | UI | RT, TOOL | the accepted image is one revision, checked by size, byte order and sha1; only the path is stored; a mismatch is refused rather than repaired | none |
| COR-DB | TOOL | QA, ARCH | artifacts are content-addressed; the corpus is capped at 20 GiB; release-gate scenes are never pruned | none |

## Contracts named but not yet settled

These contracts exist in the blueprint registry. Their producer and consumer lanes are recorded so the contract is not duplicated, but there is no note yet because the contract is not settled. A consumer task that hits one of these stops and asks rather than inventing it.

| Contract | Producer lane | Consumer lane |
|---|---|---|
| RT-MEM | RT | RSP, RDP, GAME |
| RT-REGS | RT | RSP, RDP |
| RT-OS | RT | GAME, GAME |
| RT-ERR | RT | all |
| REC-EMIT | TOOL | RT |
| REC-MAP | TOOL | RT |
| RSP-TASK | RSP | RT |
| RSP-DMA | RSP | RDP |
| RDP-DL | RDP | RSP |
| RDP-OUT | RDP | RDP, VI |
| VI-REG | RDP | RT |
| VI-SWAP | RDP | RT |
| AUD-AI | RSP | RT |
| AUD-OUT | RSP | RT |
| INP-PIF | RT | UI |
| INP-MAP | UI | RT |
| SAV-EEP | RT | GAME |
| GLB-FRAME | ARCH | all |
| SHELL-UI | UI | PLAT |
| PKG-ART | PLAT | UI |

## What a handover note must contain

| Field | Meaning | Rejected when |
|---|---|---|
| producer | the contract id and the lane that writes it | missing or empty |
| consumer | every lane that reads it | missing or empty |
| settled decisions | the decisions a consumer may rely on, one per line | missing, empty, or not a list |
| open questions | what is unresolved, or an explicit empty list | missing |

An empty `open_questions` list is valid and meaningful: it says the contract has no known gaps. Omission is not valid, because a reader cannot tell omission from an unstated gap.

## How a consumer uses it

| Step | What the consumer does |
|---|---|
| 1 | finds its contract in the settled table |
| 2 | reads the settled decisions as the specification |
| 3 | checks the open questions before relying on an edge case |
| 4 | if the contract is not settled, stops and asks rather than inventing it |

This is the same rule as "agents never invent contracts" in [agent-rules.md](agent-rules.md), applied to the specific contract in front of the consumer.

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the four required fields and their rejections | yes: `src/tests/docs/handover.py`, with `test_handover.py` covering a missing field, an empty field, an empty decision list, and a non-mapping note, each naming the exact reason |
| the settled-contract table | prose |
| the not-yet-settled list | prose, a snapshot of the blueprint registry read on 2026-11-27 |
| reading the registry at run time | not implemented: the registry is outside `src/` and is not shipped |

## Related

- [task-template.md](task-template.md): the template consumer tasks use, which links here
- [agent-rules.md](agent-rules.md): the no-invented-contracts rule
- [parity.md](parity.md): the artifacts the contracts produce
