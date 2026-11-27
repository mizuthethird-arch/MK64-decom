# Scope and non-goals

This page states what the MK64 Native Rebuild ships and what it deliberately does not, so that no agent, reviewer or release note proposes work the project has already declined.

## Pinned target

| Item | Value |
|---|---|
| Game | Mario Kart 64 (Europe) (Rev A) |
| Cartridge id | NKT |
| Country code | P (Europe) |
| Revision | 1 (Rev A, the "A" file) |
| Image size | 12,582,912 bytes |
| Canonical z64 sha1 | f6b5f519dd57ea59e9f013cc64816e9d273b2329 |

The image is user supplied and is never stored in this repository, never committed, never shipped in an artifact and never redistributed. See [rom.md](rom.md) for the accepted image, the byte order and the checks the importer performs.

## In scope: what ships

The rebuild ships full game parity for that one revision in exactly four modes (Grand Prix, Time Trial, Versus, Battle), the shell around it, signed Windows and Linux builds, and nothing else.

"Full game parity" is measured, not assumed. It is a byte comparison of recorded artifacts against the frozen C oracle for the same input trace and the same revision; `docs/parity.md` defines the comparison, and [assets.md](assets.md) records the no-assets and no-keys policy: no game data and no key is ever in the repository or in a release.

The three deliverables the plan exists for:

| Deliverable | What it is | Ships to the player |
|---|---|---|
| match-proven decompilation | The C source that rebuilds the pinned cartridge byte for byte | No: it is a build-time proof |
| frozen C oracle | The decompilation tree, frozen by commit, that records reference frames, audio and save images | No: it is a measurement instrument |
| 100% Rust rebuild | The player-facing program: runtime, renderer, game logic, shell, tooling | Yes |

## In scope: modes

| Mode | What parity means here |
|---|---|
| Grand Prix | The four cups, four races each, with standings, points, trophy and save progress as the cartridge produces them |
| Time Trial | A single track against the clock, with records and ghost storage in the save file |
| Versus | Two to four players on any track, with the item set and the original split-screen presentation |
| Battle | Balloon and coin modes on the four arenas below, at up to four players on one machine (unverified: awaiting cartridge check) |

There is no fifth mode, no bonus mode and no shell-invented mode. Reaching these four is the whole parity claim.

## In scope: tracks

Grand Prix and Versus reach 16 tracks, in four cups of four. The cup names and their contents are unverified: awaiting cartridge check.

| Cup | Tracks |
|---|---|
| Mushroom Cup (unverified: awaiting cartridge check) | Luigi Raceway (unverified: awaiting cartridge check), Moo Moo Farm (unverified: awaiting cartridge check), Koopa Troopa Beach (unverified: awaiting cartridge check), Kalimari Desert (unverified: awaiting cartridge check) |
| Flower Cup (unverified: awaiting cartridge check) | Toad's Turnpike (unverified: awaiting cartridge check), Frappe Snowland (unverified: awaiting cartridge check), Choco Mountain (unverified: awaiting cartridge check), Mario Raceway (unverified: awaiting cartridge check) |
| Star Cup (unverified: awaiting cartridge check) | Wario Stadium (unverified: awaiting cartridge check), Sherbet Land (unverified: awaiting cartridge check), Royal Raceway (unverified: awaiting cartridge check), Bowser's Castle (unverified: awaiting cartridge check) |
| Special Cup (unverified: awaiting cartridge check) | D.K.'s Jungle Parkway (unverified: awaiting cartridge check), Yoshi Valley (unverified: awaiting cartridge check), Banshee Boardwalk (unverified: awaiting cartridge check), Rainbow Road (unverified: awaiting cartridge check) |

## In scope: arenas

Battle reaches four arenas. The arena names are unverified: awaiting cartridge check.

| Arena |
|---|
| Big Donut (unverified: awaiting cartridge check) |
| Block Fort (unverified: awaiting cartridge check) |
| Double Deck (unverified: awaiting cartridge check) |
| Skyscraper (unverified: awaiting cartridge check) |

Both battle variants, balloons and coins (unverified: awaiting cartridge check), are played on each of the four arenas. The arenas themselves are listed once, above.

## In scope: characters

The eight characters, whose differing acceleration, top speed, weight and handling must reproduce the original for a recorded input trace. The character names are unverified: awaiting cartridge check.

| Character |
|---|
| Mario (unverified: awaiting cartridge check) |
| Luigi (unverified: awaiting cartridge check) |
| Peach (unverified: awaiting cartridge check) |
| Toad (unverified: awaiting cartridge check) |
| Yoshi (unverified: awaiting cartridge check) |
| Donkey Kong (unverified: awaiting cartridge check) |
| Wario (unverified: awaiting cartridge check) |
| Bowser (unverified: awaiting cartridge check) |

Which engine class and which kart each character may pick is the game's own rule, read from the image, and is not restated here.

## In scope: items

The item system is in scope as the game implements it: the item boxes, the roulette, the held item slot and the effect of every item the game can hand out. The item identities are the game's own and are read from the user image at run time; the rebuild does not invent, remove or rebalance an item.

| Behaviour | Parity target |
|---|---|
| Item box pickup and roulette | Same roulette timing and same item probabilities for the same race state |
| Held item and rear use | Same fire, drop and swap rules, including holding one item behind the kart |
| Trajectories and lifetimes | Same positions, bounce frames, homing and removal frames as the oracle trace |
| Status effects | Same invulnerability and shrink windows, same spin and squash frames |

## In scope: time trial ghosts

| Item | Parity target |
|---|---|
| Ghost recording | A new personal best writes the same ghost data into the same save slot as the cartridge |
| Ghost replay | The ghost replays its recorded inputs with the same kart path and the same visible result |
| Records screen | Time trial records and the ghost list render from save data, drawn by the game, never re-skinned |

## In scope: save files

| Item | Parity target |
|---|---|
| Save slots | The game's own file select with its slot count and contents |
| Persistence | The save image survives a clean quit and a forced kill, and a write interrupted by a full disk leaves the previous image intact |
| Compatibility | A save written by the original cartridge loads with every field interpreted the same way |

## In scope: options screens

The shell owns the options screens, and the game keeps its own look.

| Screen | Contents |
|---|---|
| Engine class | The 50, 100 and 150 cc selection and its mapping to the game options |
| Controls | Keyboard and gamepad mapping, with the original controller layout as the reference |
| Video | Window mode, resolution, integer scaling, filter plan and vsync |
| Audio | Output device, buffer size, volume and the bit-exact output toggle |
| Gameplay and data | Save export and import, diagnostics, and the privacy switches: telemetry off by default with no toggle that turns it on silently |

## In scope: the shell around it

| Surface | In scope |
|---|---|
| ROM import | First run explains why an image is needed, verifies size and sha1, and stores the path only |
| Legal notice | The not-legal-advice banner, the non-commercial statement and the zero-asset policy |
| Failure surfaces | A crash screen that writes a local report and never loses a save, and a corrupt-save screen that offers the backup rather than a reset |
| Accessibility | Keyboard and gamepad reach every screen, announced state changes, text scaling, reduced motion and high contrast |

## In scope: builds

The rebuild ships signed builds for Windows and Linux.

| Platform | Format |
|---|---|
| Windows | An installer and a portable archive, both signed |
| Linux | A portable bundle and a distribution package, with detached signatures published next to them |

Every release publishes a checksum per artifact and a bill of materials. A build without a valid signature is not a release.

## Parked: not in this rebuild

These features are named so no agent proposes them. Each has one reason and the person who said no.

| Parked feature | Reason | Decider |
|---|---|---|
| Netplay | The parity claim is a byte comparison against the oracle for local frame timing, and a network path makes every comparison depend on a clock the project does not control. | human owner (P00 decision record, no individual named) |
| Mods | Content replacement would make "the rebuilt frame equals the oracle frame" false for any modded install, which is the one property the whole plan is measured by. | human owner (P00 decision record, no individual named) |
| Texture packs | A replaced texture breaks the byte equality of the rendered frame, and no asset is shipped or extracted, so a texture pack would also be the first repository-hosted game data. | human owner (P00 decision record, no individual named) |
| macOS gate | There is no macOS build in this plan, so there is no gate to prove, and an unproven platform must not be listed as supported. | human owner (P00 decision record, no individual named) |
| Mobile | The shell assumes a keyboard or gamepad and a windowed desktop surface, and a touch rebuild would be a second product rather than a port. | human owner (P00 decision record, no individual named) |
| Achievements | Achievements are a parallel shell-invented progression that contradicts the shell rule of never re-skinning or extending the game's own progression. | human owner (P00 decision record, no individual named) |
