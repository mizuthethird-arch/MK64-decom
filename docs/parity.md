# Parity: bit-exact, measured

Bit-exact means byte equality on recorded artifacts. It does not mean visual similarity. Two images that a person cannot tell apart are not equal here unless their bytes are.

This page defines what is compared for each artifact, and orders the layers so a mismatch is always blamed on one owner.

## The six artifacts

Every artifact below is recorded by the frozen oracle and replayed against the rebuild. The hash is the comparison unit; the comparison rule says what counts as equal.

| Artifact | Source | Format | Hash | Comparison rule | Compared by |
|---|---|---|---|---|---|
| Framebuffer (RGBA5551 words) | the RDP output of one finished frame | RGBA5551 words, 320 by 240, two buffers | sha256 over the raw words in draw order | exact equality per frame, then the first differing word | the corpus comparator |
| Audio buffer (16-bit stereo samples) | one AI DMA buffer handed to the audio interface | 16-bit stereo samples, 32 kHz | sha256 over the sample bytes | exact equality per buffer, in dispatch order | the corpus comparator |
| VI log (register writes per frame) | the video interface register writes of one frame | ordered (register, value) pairs with the frame index | sha256 over the canonical text form | exact equality of the ordered sequence | the corpus comparator |
| RSP log (task dispatch and cycles) | each SP task dispatch and its cycle count | task type, boot address, cycle count, per frame | sha256 over the canonical text form | exact equality of the sequence, including cycle counts | the corpus comparator |
| Save (0x200 byte EEPROM image) | the EEPROM image after a session | the 0x200 byte EEPROM image | sha256 over all 512 bytes | exact equality of all 512 bytes | the corpus comparator |
| Input (buttons and stick per frame) | the controller state sampled each frame | buttons plus stick X and Y, per frame, per port | sha256 over the per-frame tuples | exact equality of every frame in order | the corpus comparator |

The six kinds are the framebuffer, the audio buffer, the VI log, the RSP log, the save and the input frames.

Comparison granularity is always the whole artifact, never a subset and never a sampled portion. A rule that compares "most" of an artifact is not a parity rule.

## Comparison rules

| Rule | Meaning |
|---|---|
| Exact equality | the sha256 of the recorded artifact and of the rebuilt artifact are identical |
| First differing byte | when they differ, report the offset and both values of the earliest difference, so the diff tool can name the owning layer |
| Documented deviation | a difference is not a bug only if it is listed in the deviations table below and its opt-in flag is on for that run |

A mismatch that is not an exact equality and is not a documented deviation is a bug, whatever it looks like.

## The parity pyramid

Layers are proven from the bottom up. A gate must pass before the layer above is investigated, because a wrong value at the bottom makes every layer above it wrong for the same reason.

| Order | Layer | Gate that must pass before the next layer is investigated |
|---|---|---|
| 1 | Input and memory | every recorded input frame and every memory read matches the oracle exactly |
| 2 | RSP | every task dispatch and cycle count matches the oracle log exactly |
| 3 | RDP | every framebuffer matches byte for byte for the recorded scenarios |
| 4 | VI | every VI register log matches, so the image reaches the display identically |
| 5 | Audio | every audio DMA buffer matches byte for byte |
| 6 | Content | every mode, track, arena, character and item matches under the five gates above |

Investigating a layer above a failing gate is wasted work: the same bytes at the bottom explain the symptom at the top. Fix the lowest failing gate before moving up.

## Who owns a mismatch

Each kind of mismatch has exactly one owning layer. The diff tool and every agent quote this table, so two people never fix the same bug in two layers.

| Mismatch kind | Owning layer |
|---|---|
| Pixel colour in the wrong place | RDP |
| Audio sample value or timing | Audio |
| VI timing or the frame the display sees | VI |
| RSP task dispatch or cycle count | RSP |
| Save field value after a session | Content |
| Input frame value or stick reading | Input and memory |

The owner is unique by construction: one row per kind, and no kind appears twice.

## Ambiguous cases

Two cases look like they belong to several layers at once. They do not.

| Case | Where it belongs | Why |
|---|---|---|
| A mismatch caused by the game reading an uninitialised word | Input and memory | the read is uninitialised, so the fault is below every layer that consumes it; the harness settles the value rather than guessing an owner |
| A mismatch visible only after a save reload | Content | the save image round trips, so the divergence appears when the game re-reads its own saved state; the save artifact and the re-read content are both compared before blaming a layer |

When two layers both show a difference, the lower one in the pyramid owns it.

## Cases that look nondeterministic

These are not nondeterministic once the harness removes the cause. The rule: the harness must make the value recorded, not random.

| Source of apparent nondeterminism | How the harness removes it |
|---|---|
| Uninitialised memory | the harness pre-fills guest memory with a recorded fill pattern before boot, so an uninitialised read yields the same value every run |
| Reads of the host clock | the host clock is replaced by a virtual clock advanced only by the guest, so a timing read is a function of the recorded input |
| Read of an uninitialised register or DMA buffer | the register file and DMA buffers are filled from a recorded pattern before each scenario |
| Collection order | every comparison is order-explicit; nothing relies on dictionary or filesystem ordering |
| Unset environment values | the harness passes a fixed, empty environment to the guest |

If a run still differs between two executions of the same scenario, that is a bug in the harness, not a parity result, and it is fixed before any parity claim is made.

## Deviations allowed by design

A deviation is a difference the rebuild is allowed to have on purpose. Each one has its own opt-in flag and is off unless the player turns it on. A deviation not in this table is a bug.

| Deviation | What changes | Opt-in flag | Default |
|---|---|---|---|
| Display scaling | the output is scaled from the native size to the window | `scale` | off |
| Aspect ratio | the 320 by 240 image is presented at a different aspect | `aspect` | off |
| Presentation rate | the host presents at a rate other than the console's | `present_rate` | off |

Every parity run records which deviations were on. A parity claim is always about the deviations that were off.

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the six artifact definitions and their hashes | prose, until the corpus and the oracle exist |
| the comparison rules and the failure reporting | prose, until the corpus comparator exists |
| the pyramid, the gates and the mismatch-to-layer table | prose, quoted by the diff tool when it is built |
| documented deviations | prose |

Nothing on this page runs yet. It is the specification that the corpus, the comparator and the diff tool are built against, and later phases quote it rather than restating it.

## Related

- [scope.md](scope.md): what the rebuild ships and what is parked
- [rust-only.md](rust-only.md): the 100% Rust rule for the shipped crates
- [rom-contract.md](rom-contract.md): the accepted image the parity runs are made against
