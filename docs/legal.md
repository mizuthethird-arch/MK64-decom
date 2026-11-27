# Legal, asset and key policy

This page is the canonical statement of what this project may contain and what it may not. [assets.md](assets.md) is the detailed no-assets policy; this page is the rule, and that page is how it is enforced.

## The ROM is user supplied

The rebuild ships no game data. The player brings their own cartridge image.

| Statement | Meaning |
|---|---|
| User supplied | The player obtains their own image. The project never provides, hosts, links or mirrors one. |
| Never in git | No image and no derived image is ever committed. `rom/` holds only a placeholder `.gitkeep`, and any image there is ignored. |
| Never in a release | No installer, portable archive, package, container image or CI artifact contains the image or any part of it. |
| Read only | Every tool opens the image read only and never modifies, copies or renames the player's file. |

The accepted image and its exact checks are in [rom.md](rom.md) and [rom-contract.md](rom-contract.md).

## No asset is committed

No asset of any kind is committed to this repository or shipped in a release:

| Asset class | Examples |
|---|---|
| Texture | any surface, sprite or skybox image the cartridge draws |
| Display list | any recorded render command stream |
| Sample bank | any collection of audio samples |
| Sequence | any music or sound sequence, and its instrument definitions |
| Track data | any course or arena geometry, collision data, checkpoint table or minimap |
| Font | any glyph atlas or text rendering table |
| Extracted model | any character, kart, item or prop geometry, skeleton or animation |

Everything the game draws or plays is read from the user image **at run time**, in memory. Nothing is extracted to disk, committed, or shipped. [assets.md](assets.md) lists the classes exhaustively, states what a test may and may not contain, and describes the two guards that enforce this rule.

## No key is committed

No key material of any kind:

| Key | Rule |
|---|---|
| Signing key | Lives in the release secret store, never in the tree, never printed, never committed |
| ROM key | No cartridge encryption or decryption key is stored, derived or embedded anywhere |
| Licence key | No licence key, activation key or serial is shipped |
| Secret | No token, password, API key, private key or credential in the tree, logs, tests or images |

A leaked key is rotated first and removed second.

## What enforces this

| Guard | Where | Needs the image |
|---|---|---|
| Fast structural guard | `src/tests/docs/test_no_assets.py`, in the default suite | No |
| Deep content scan | `src/tools/scan-for-rom-content.py`, in the dedicated CI job | Yes, and it fails closed without one |

The fast guard rejects asset-like file names, binary magic at the start of a file and oversized files, and asserts that the deep scan still exists and still runs in CI. The deep scan is exact for any unbroken run of 96 bytes or more of the image, in either byte order, at any offset.

## Limits of these guards

The guards catch accidents, not every conceivable form of game data. Neither guard recognises an asset that has been re-encoded, resized or re-compressed, and the deep scan does not detect ROM data split across several files. Review discipline covers what the scans cannot.

## Incident and takedown procedure

This procedure is written before it is needed. It applies when someone reports that the repository or a release contains game data, or when a rights holder makes contact.

### Contact path

| Route | Use |
|---|---|
| the repository owner via the GitHub security advisory contact | for a report that the repository or a release contains game data, or any rights-holder contact |

That is the only contact path this project publishes. The project does not publish an email address, and this page deliberately contains none: a contact route that can be scraped is a contact route that gets abused, and no address should be invented here.

### Artifact withdrawal steps

Every step names the command that performs it, the owner who performs it, and the time limit. The clock starts when the report arrives.

| Step | Command | Owner | By when |
|---|---|---|---|
| 1. Acknowledge the report | `gh issue comment <issue> --body "Acknowledged; withdrawal under review."` | human owner | within 24 hours |
| 2. Freeze releases | `gh release edit <tag> --draft` | human owner | within 24 hours |
| 3. Identify the artifacts | `gh release view <tag> --json assets -q '.assets[].name'` | human owner | within 48 hours |
| 4. Delete the offending asset | `gh release delete-asset <tag> <asset> --yes` | human owner | within 48 hours |
| 5. Remove it from the tree | `git rm <path> && git commit -m "withdraw: remove reported content" && git push` | human owner | within 48 hours |
| 6. Publish the corrected release | `gh release edit <tag> --draft=false` | human owner | within 5 days |
| 7. Record the outcome | `gh issue close <issue> --comment "<outcome>"` | human owner | within 5 days |

The owner on every step is the human owner, because withdrawal is an irreversible external action and no agent may take one. The commands are the exact GitHub CLI and git invocations; none of them runs automatically.

### The public statement template

The public statement is posted once the artifacts are withdrawn, not before.

> We were notified of [description] in [artifact] published on [date]. The affected artifact has been withdrawn and the issue has been corrected. This project ships no game data: the player supplies their own game image, and no image, asset or key is distributed here. We thank the reporter.

Fill the brackets with facts only. Do not speculate about intent, do not characterise the reporter, and do not describe a rights holder's position beyond what they stated.

### A false report

A report can be wrong. The response must not concede the claim while it is being checked.

| Rule | Meaning |
|---|---|
| Do not concede | never publish a statement that admits the content was infringing before it is verified |
| Do not attack the reporter | a mistaken report is answered with facts, not accusations |
| Verify first | run the same identification steps and record the result |
| Say what was found | if the content is clean, state what was checked, not merely that the claim is denied |

A false report closes with the evidence: what was inspected, what it contained, and why it is not what the reporter described.

### Rehearsal

The withdrawal procedure has **not been rehearsed**. There is no staging release to rehearse it against, so it is not done and this page does not claim it is. A rehearsal requires a disposable release with a disposable artifact, and none exists yet.

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the ROM and asset rules | yes: the fast guard and the deep scanner described in [assets.md](assets.md) |
| the key rule | prose |
| the incident and takedown procedure | prose: the commands are written but nothing runs them, and withdrawal is performed by a human |
| the rehearsal | not done, for the reason above |

## Related

- [assets.md](assets.md): the detailed no-assets and no-keys policy and its guards
- [rom.md](rom.md): the accepted image and the rules that keep it out of git and out of every artifact
- [rom-contract.md](rom-contract.md): the exact acceptance rule and the refusal behaviour
- [release.md](release.md): how a corrected release is cut
