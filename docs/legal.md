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

## Related

- [assets.md](assets.md): the detailed no-assets and no-keys policy and its guards
- [rom.md](rom.md): the accepted image and the rules that keep it out of git and out of every artifact
- [rom-contract.md](rom-contract.md): the exact acceptance rule and the refusal behaviour
