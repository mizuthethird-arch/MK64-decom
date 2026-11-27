# ROM acceptance contract

This is the rule the importer obeys and the rule task T0002 is measured against. [rom.md](rom.md) records why the project has a ROM contract at all; this page records exactly what is accepted, what is refused and why.

Only the pinned image is accepted. There is no second accepted image, no "close enough" revision and no fallback.

## The acceptance rule

A file is accepted when and only when all of the following hold. The importer reports which check failed, in this order, and refuses the file as soon as one fails.

| Order | Check | Required value |
|---|---|---|
| 1 | Size | exactly 12,582,912 bytes (12582912) |
| 2 | Byte order | the file converts to z64 by the rule below |
| 3 | Canonical z64 sha1 | `f6b5f519dd57ea59e9f013cc64816e9d273b2329` |
| 4 | Header name | MARIOKART64 at offset 0x20 |
| 5 | Cartridge id | NKT at offset 0x3B |
| 6 | Country | P (Europe) at offset 0x3E |
| 7 | Revision | 1 (Rev A) at offset 0x3F |

Checks 4 to 7 restate what check 3 already implies for this one image. They exist so that a refusal explains itself in the player's terms rather than only as a hash.

The importer must implement the seven-check table above and must be tested against it.

## The three byte orders

The same cartridge circulates in three byte orders, and the importer must tell them apart.

| Order | What it is | This project |
|---|---|---|
| z64, also written .n64, big-endian | the natural console order, header magic `80371240` | accepted directly, this is the pin |
| v64, 16-bit byteswapped | every adjacent byte pair exchanged | accepted after the conversion below |
| 32-bit byteswapped, word-swapped | every adjacent 4-byte group reversed | **rejected**: no cartridge dump this project supports is stored that way, and a 32-bit swap does not reach the pinned sha1, so accepting it would mean guessing |

The 32-bit variant is the trap. It is a real dump order in the emulation world, it is the same length, and a naive importer that "tries swaps until something works" will silently accept a corrupted derivation. It must be refused. The test suite proves that reversing every 4-byte group of the delivered image does not reach the pinned sha1 and does not produce the z64 header magic.

No legitimate dump of this cartridge uses the 32-bit order: this is measured, not assumed, because that reversal of the delivered image does not reach the pin, while the z64 and v64 forms do.

## The conversion rule

The conversion is one documented transformation, applied to a copy in memory:

```
swapped[i] = raw[i ^ 1]    for every byte index i
```

A 16-bit byteswap, nothing else. The length does not change.

The derived z64 image exists only at run time, in memory. It is never committed, never written into the repository, never used as a cache on disk and never shipped. A `.gitignore` entry for the derived extension is a backstop, not the policy: the policy is that the derived image is not written at all.

## Mismatch behaviour

The importer refuses, explains and never guesses.

| Condition | What the importer does |
|---|---|
| Wrong size | Refuses. Reports the expected 12,582,912 bytes and the size found. The path is not stored. |
| Right size, header already in z64 order, wrong sha1 | Refuses. Reports the expected sha1 and the sha1 found. The path is not stored. |
| Right size, v64 order, sha1 after the 16-bit byteswap is wrong | Refuses, naming the sha1 the conversion produced. The path is not stored. |
| Right size, 32-bit byteswapped order | Refuses, naming the byte order as the failed check. |
| Correct image, header field disagreeing | Refuses at the first disagreeing field, by name. |
| Missing or unreadable file | Refuses before any check, naming the path. |
| A different revision of the same cartridge | Refuses. No substitute image is generated and none will be. |

The importer never applies a second transformation after a failed check, never retries with a looser rule, never offers to "fix" the file by rewriting it, and never accepts a file because it is close.

## What is stored

Only the path is stored. The file itself is never copied, never moved, never renamed, never modified and never re-encoded.

| Stored | Not stored |
|---|---|
| the absolute path to the player's file | a copy of the image, partial or whole |
| the pinned sha1 the path was verified against | any extracted game data taken from the image |
| the time the path was last verified | the image bytes in any database, cache or artifact |

The player's file stays where the player put it. The rebuild reads it where it is, read only, every launch.

## Which parts of this are executable today

This page is a contract, not an implementation. Today the only executable parts are the hash and header facts below, proved by `src/tests/docs/test_rom_contract.py` against the real file at `src/rom/Mario Kart 64 (Europe) (Rev A).n64`:

| Fact | Executable today |
|---|---|
| the delivered file is 12,582,912 bytes and hashes to the delivered sha1 | yes |
| the 16-bit byteswap of that file reaches the pinned sha1 and the pinned header | yes |
| a 32-bit byteswap of that file does not reach the pin | yes |
| the importer's refusal behaviour, message ordering and stored fields | prose only: no importer code exists yet |

Everything in the mismatch tables above is prose. It becomes executable when the importer is built; until then the contract is the specification that implementation will be tested against.

## Names still awaiting cartridge confirmation

Track, arena and character names in [scope.md](scope.md) are marked `(unverified: awaiting cartridge check)`. They came from the blueprint and from general knowledge of the retail cartridge, not from reading this image. That task belongs to T0002 because it owns the ROM facts.

The rule: a marker may be removed only when the name has been confirmed against the image or a running cartridge, and the confirmation is recorded. Until then the markers stay as they are.

## Related

- [rom.md](rom.md): the pin, the delivered file, and the rules that keep the image out of git and out of every artifact
- [scope.md](scope.md): what the rebuild ships and which names are still unverified
