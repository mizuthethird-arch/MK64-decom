# Measurement methodology

Every number this project reports comes from a command. This page names the command behind each metric and the page the metric feeds. A number typed by hand is a defect, because it cannot follow the data.

## The metric table

| Metric | Command | Feeds |
|---|---|---|
| framebuffer hash | `cargo run -p mk64-parity -- hash-framebuffer --scene <scene> --frame <n>` | [parity.md](parity.md) |
| audio buffer hash | `cargo run -p mk64-parity -- hash-audio --scene <scene> --buffer <n>` | [parity.md](parity.md) |
| VI log | `cargo run -p mk64-parity -- dump-vi-log --scene <scene> --frame <n>` | [parity.md](parity.md) |
| RSP log | `cargo run -p mk64-parity -- dump-rsp-log --scene <scene> --frame <n>` | [parity.md](parity.md) |
| save | `cargo run -p mk64-parity -- hash-save --scene <scene>` | [parity.md](parity.md) |
| input | `cargo run -p mk64-parity -- dump-input --scene <scene>` | [parity.md](parity.md) |

Each command above is **not implemented yet**: the parity tool does not exist, so nothing produces these numbers today. They are the exact commands the corpus tool and the parity tool must expose, written down now so the tool is built to them rather than the numbers being invented later.

## What each metric means

| Metric | Granularity |
|---|---|
| framebuffer hash | one hash per finished frame, over the RGBA5551 words in draw order |
| audio buffer hash | one hash per AI DMA buffer, over the 16-bit stereo samples |
| VI log | one ordered list of register writes per frame |
| RSP log | one ordered list of task dispatches with cycle counts per frame |
| save | one hash over the 512 byte EEPROM image |
| input | one hash over the per-frame button and stick tuples |

## Measurements made on one machine only

Some numbers are machine dependent and are recorded as such, never as a general claim.

| Measurement | Scope |
|---|---|
| boot time, frame cost, compile time | measured on one machine only: the engineer's machine, with the machine named in the record |
| frame rate | measured on one machine only, and reported as a measurement, not a target; this plan does not promise a frame rate |
| binary size, build time | measured on one machine only, and compared only against prior runs on the same machine |

A number measured on one machine is reported with that machine's identity attached. A machine-dependent number reported without its machine is a defect.

## Rules for a reported number

| Rule | Meaning |
|---|---|
| Every number has a command | the command that produced it is quoted next to it |
| Every hash records its input | scene, frame or buffer index, and the scenario that produced it |
| A missing measurement is reported as unknown | never estimated, never filled in from a similar run |
| Comparing two numbers requires the same machine | a cross-machine comparison is not a measurement, it is a guess |

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the metric list | prose, taken from [parity.md](parity.md) |
| the commands in the table | specification, not implemented yet: the parity tool does not exist |
| the one-machine scope rule | prose |
| every rule in the last table | prose |

Nothing on this page runs. It is the specification the parity tool and the corpus tool are built against, and it exists so that the first reported number already has a command behind it.

## Related

- [parity.md](parity.md): the artifacts these metrics are taken from
- [corpus.md](corpus.md): where the recorded artifacts are stored
- [release.md](release.md): the releases that quote these numbers
