# ROM contract

The rebuild ships no game data. Every player supplies their own cartridge image, and this page is the only accepted image, the checks applied to it and the rules that keep it out of this repository. The image is user supplied, mounted or opened read only, never committed and never shipped.

## The pin

| Field | Value |
|---|---|
| Title from the header | MARIOKART64 |
| Cartridge id | NKT |
| Country code | P (Europe) |
| Revision | 1 (Rev A) |
| Size | 12,582,912 bytes |
| Canonical z64 sha1 | f6b5f519dd57ea59e9f013cc64816e9d273b2329 |

The header fields above were read from the image, from 0x20 (the title, 20 bytes), 0x3B to 0x3D (the cartridge id), 0x3E (the country) and 0x3F (the revision).

The canonical sha1 is over the image in z64 byte order, and it is the only hash the project pins. Every other number below is a property of how a file happens to be stored, never an acceptance test of its own.

## The image a player may hold

Cartridge dumps circulate in several byte orders, and the same cartridge therefore produces several file hashes with different extensions. This project accepts one of them, after one documented conversion.

| Stored form | Extension | sha1 of that file | Accepted |
|---|---|---|---|
| z64, big-endian word order | .z64 | f6b5f519dd57ea59e9f013cc64816e9d273b2329 | Yes, this is the pin |
| V64, 16-bit byteswapped | .v64 or .n64 | f18317bfd7fbcaea6cfbfcb9c4ae3c7c7d1d66c7 | Only after the conversion below |

The local development image is the second row: `Mario Kart 64 (Europe) (Rev A).n64`, 12,582,912 bytes, sha1 f18317bfd7fbcaea6cfbfcb9c4ae3c7c7d1d66c7, in V64 byte order.

The conversion that turns it into the pinned image is a 16-bit byteswap: swap every adjacent byte pair, leaving the length unchanged. After that swap the file's sha1 is f6b5f519dd57ea59e9f013cc64816e9d273b2329 and the header reads MARIOKART64, id NKT, country P, revision 1. Any other transformation that reaches the pin is equally acceptable; any that does not reach the pin is rejected.

## The rules

| Rule | Statement |
|---|---|
| User supplied | The player provides the image. The project does not obtain, copy, download or generate one. |
| Read only | Every tool that touches the image opens it read only. No byte of the player's file is ever written. |
| Never committed | The image and any derived image are excluded by `.gitignore` (`rom/`, `*.n64`, `*.v64`, `*.z64`) and are never in git history. |
| Never shipped | No release artifact, installer, container image, corpus or test fixture contains the image or any part of it. |
| Path only | The importer stores the path to the image, and the loader reads the player's file at run time. |
| Verified every launch | The stored path is checked against the size and the pinned sha1 on every launch, so an edited or swapped file is reported rather than played. |

## What happens on a mismatch

| Condition | Behaviour |
|---|---|
| Missing file | The game does not start; the importer explains which image is expected and why. |
| Wrong size | Rejected with the expected size; the path is not stored. |
| Right size, wrong sha1 | Rejected with the expected sha1; the path is not stored. The importer offers the conversion above when the header suggests a different byte order. |
| A different revision of the same cartridge | Rejected. There is no substitute image and none will be generated. |

The implementation of these checks lives in `tools/rom-check` and is specified by task T0002. This page records the pin and the policy; the exact acceptance rule, the three byte orders and the refusal behaviour are in [rom-contract.md](rom-contract.md), and the tool proves it.

## Related

- [scope.md](scope.md): what the rebuild ships and what is parked
- [rom-contract.md](rom-contract.md): the exact acceptance rule, the byte orders and the mismatch behaviour
- `docs/legal.md`: the legal and asset policy (written by its own task)
