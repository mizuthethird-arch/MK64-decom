# MK64 Native Rebuild

A 100% Rust rebuild of Mario Kart 64 (Europe) (Rev A), proven byte for byte against a frozen C oracle built from a match-proven decompilation. The game image is user supplied and is never in this repository.

## Read this first

- [docs/scope.md](docs/scope.md): what the rebuild ships, and every feature that is parked so nobody re-proposes it.
- [docs/rom.md](docs/rom.md): the one accepted image, the checks applied to it, and the rules that keep it out of git and out of every artifact.
- [docs/rom-contract.md](docs/rom-contract.md): the exact acceptance rule, the byte orders and the refusal behaviour.
- [docs/assets.md](docs/assets.md): no game data and no key in the repository or in any release, enforced by a test.
- [docs/legal.md](docs/legal.md): the legal, asset and key policy in one page.
- [docs/rust-only.md](docs/rust-only.md): every shipped crate is Rust, and the one C++ exception that never ships.
- [docs/parity.md](docs/parity.md): what bit-exact means per artifact, the parity pyramid and who owns a mismatch.
- [docs/agent-rules.md](docs/agent-rules.md): the task and session rules every agent follows, and the task template.
- [docs/README.md](docs/README.md): the index of every documentation page and the behaviour it settles.
- [docs/backlog.md](docs/backlog.md): the backlog, its critical path and the weekly review template.
- [docs/parity-statement.md](docs/parity-statement.md): the single parity statement, included elsewhere by reference.

## Layout

| Path | Contents |
|---|---|
| `docs/` | Policy and contracts. Start with scope and the ROM contract. |
| `c/` | The decompilation. Build time only; never shipped. |
| `oracle/` | The frozen C build used to record reference frames, audio and saves. |
| `rust/` | The shipped program: runtime, renderer, game logic, shell. |
| `tools/` | Tooling, including the ROM check every job runs first. |
| `tests/docs/` | Tests that keep these documents honest: links, and the scope lists. |
| `rom/` | Where a developer's own image may sit. Ignored by git. |
| `docker/` | Container definitions for the pinned toolchain. |

## The ROM

No cartridge image, extracted asset or key is stored, committed or shipped here; see [docs/rom.md](docs/rom.md). Put your own image in `rom/` and let the importer verify it. `rom/*` and `*.z64` are ignored by git.

## Documentation tests

The documentation is tested like code, inside the pinned container image. From `src/`:

```
docker run --rm --network none \
  -v "$PWD:/src" -w /src/tests/docs \
  python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b \
  python -m unittest discover -s . -p 'test_*.py' -v
```

The tests fail when a relative link points at a missing file, when a scope list loses an entry, and when an entry is listed twice or contradicts a parked feature.
