# No-assets and no-keys policy

The repository and every release contain no game data and no key. Everything the game draws or plays is read from the player's own image at run time.

This rule is enforced by a test, not only by this page: `src/tests/docs/test_no_assets.py` scans the tree and fails when an asset appears.

## The rule

| Statement | Meaning |
|---|---|
| No game data in the repository | Not in code, not in tests, not in fixtures, not in documentation, not in git history |
| No game data in a release | Not in an installer, a portable archive, an AppImage, a container image or a CI artifact |
| Read at run time | Every byte the game draws or plays comes from the user image while the program runs |
| Extract to memory only | Anything derived from the image lives in memory for as long as it is used and is never written to disk |
| No keys of any kind | No signing key, no ROM key, no licence key, no token, no secret and no credential |

## What counts as an asset

Every one of these is game data and must never appear in the repository or in a release:

| Asset class | What it is |
|---|---|
| Texture | Any image, tile, or palette the cartridges uses to draw a surface, a sprite or a skybox |
| Display list | Any recorded render command stream the game feeds to the RDP |
| Sample bank | Any collection of audio samples the game plays |
| Sequence | Any music or sound sequence, and any instrument definition it refers to |
| Track data | Any course or arena geometry, collision data, course layout, checkpoint table or minimap |
| Font | Any glyph atlas, character texture or text rendering table |
| Extracted model | Any character, kart, item or prop geometry, skeleton or animation lifted from the image |
| Any other payload | Any other byte sequence taken out of the image, whatever its name or file extension |

A file needs none of these to be forbidden. A blob of unexplained bytes is treated as an asset until it is proved otherwise.

## How the data is used at run time

| Step | Where the data lives |
|---|---|
| The player picks their own image | The player's own file, wherever they keep it |
| The importer verifies it | See [rom-contract.md](rom-contract.md); only the path is stored |
| The game boots and reads its own data | From the user image, through the emulated memory map, at run time |
| Anything decoded on the way | In memory, for as long as it is needed |
| Nothing is written back | The image is read only, and no derived file is ever produced |

The rebuild does not ship a data pack, a rip, a texture replacement, a re-encoded soundtrack or a resource bundle. An install that needs one of those to start is a bug in the rebuild, not a packaging decision.

## The no-keys rule

No key material of any kind lives in this repository or in any artifact.

| Key | Rule |
|---|---|
| Signing key | The Windows and Linux signing keys live in the release secret store, never in the tree, and are never printed or committed |
| ROM key | No cartridge encryption or decryption key is stored, derived or embedded anywhere |
| Licence key | No licence key, activation key or serial is shipped with the rebuild |
| Secret of any kind | No token, password, API key, private key or credential is written to the tree, logs, tests or images |

A leaked key is rotated first and removed second. Report any key material found in the tree at once.

## What a test may contain

| A test may | A test may not |
|---|---|
| hold a hand-written header of at most 64 bytes, chosen for a rule about offsets | contain any ROM bytes, even a short slice |
| use a hash or a size of the real image | contain a hash of an extracted asset as a lookup table |
| check that a planted fixture is rejected, removing it afterwards | keep a binary blob as a fixture, even if it is small |
| describe an asset class in words | embed a converted, compressed, encrypted or encoded form of any asset |

"No ROM bytes" is literal. A 96-byte slice of the image is still game data, and a file that merely looks like text can still carry one. The test scanner compares file contents against the image itself for exactly this reason.

## What the enforcement checks

There are two guards, one fast and one deep.

The fast guard runs in the default documentation suite (`src/tests/docs/test_no_assets.py`) and needs no ROM. It fails when it finds:

- a file name with an asset-like extension (`.png`, `.jpg`, `.bin`, `.z64`, `.v64`, `.n64`, `.ogg`, `.wav`, `.seq`, `.ctl`, `.tbl`, `.otr`, `.zip`, `.7z`);
- a file starting with binary magic (PNG, ELF, Ogg, RIFF, Matroska, PE, WebAssembly);
- a file larger than 2 MiB.

It also asserts that the deep scan still exists and is still wired into CI, so the stronger check cannot silently disappear.

The deep guard is a separate tool, `src/tools/scan-for-rom-content.py`, run by the dedicated `deep-scan` CI job rather than on every fast test run. It needs the user-supplied image, builds an exact index of that image once, and reports every file containing an unbroken run of at least **96 bytes** of the image, at any offset and in either byte order. Exit 0 means clean, exit 1 names each offending file, and exit 2 means the scan could not run. A missing image is exit 2, never a silent pass.

The detected minimum is 96 bytes, enforced by that tool, and it holds in both byte orders.

The fast guard is a guard against accidents, not a proof of the absence of all game data. The deep scan is exact for contiguous runs of 96 bytes or more, but it cannot recognise an asset that has been re-encoded, resized or re-compressed, and it does not detect ROM data split across several files. Review discipline covers what the scans cannot.

## Related

- [rom.md](rom.md): the accepted image and the rules that keep it out of git and out of every artifact
- [rom-contract.md](rom-contract.md): the exact acceptance rule and the refusal behaviour
- [scope.md](scope.md): what the rebuild ships and what is parked
