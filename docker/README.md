# MK64 Native Rebuild: toolchain lane (P00 T0010)

This folder owns the repository layout and the CI topology for the native rebuild.
Everything here is a working toolchain definition, verified by running it, not prose.

## Repository layout

```
mk64-decompile/
  ai-guardrails-and-prompts/   READ-ONLY guardrails; ROUTER.xml is the only instruction source
  src/
    rom/                       Mario Kart 64 (Europe) (Rev A).n64, V64 order, 12,582,912 bytes
    docker/                    THIS LANE: image definitions + layout/CI notes
      rust.Dockerfile          pinned Rust 1.89.0 toolchain image, non-root
      README.md                this file
    tools/                     THIS LANE: scripts that prove the image
      verify-docker.sh         runs INSIDE the container; proves rustc/cargo/rustfmt/clippy work
      run-container.sh         host-side helper; runs a workspace script in the image, logs to file
      test-verify-docker.sh    RED/GREEN harness that drives both cases
    logs/                      THIS LANE: build output and evidence, written to files
    docs/                      owned by the docs lane
    tests/                     owned by the docs lane
```

## The image

`rust.Dockerfile` pins the base by digest, not by tag:

```
FROM rust:1.89.0-slim-bookworm@sha256:294917190b5a3fed18d3303213943f40ec9b644b3cd6e5cdc8cd029334a770b3
```

That digest is the **linux/amd64 manifest** inside the multi-arch index that the tag
`rust:1.89.0-slim-bookworm` resolves to (`sha256:d7fc7de78bb8c1469933aeecbf801314d30d7d6e9f0578bba4cfa285bfa37fe6`).
The rebuilt image is `mk64-rust:1.89.0`, id `sha256:ef08cd2482c7d6cd3ebffa612e75981b7f13171ba8cb6167c9bb1bd1342ea4f2`.
See `src/logs/digest-reconcile.txt`.

Build:

```sh
docker build -t mk64-rust:1.89.0 -f src/docker/rust.Dockerfile .
```

### Network

The build fetches `rustfmt` and `clippy` once via `rustup component add` from
`static.rust-lang.org`, and `ca-certificates` from Debian. **That is build-time only.**
The finished image needs **no network at run time**; every script here runs with
`--network=none` and still passes.

### Non-root

The image sets `USER 1000:1000` with a real account `mk64` (home `/home/mk64`).
Verified by running `id -u` inside it: **1000**, `id -un` is `mk64`
(`src/logs/nonroot-proof.txt`). `verify-docker.sh` fails if the uid is 0.

### No secrets

No credentials, keys, or tokens are copied or set in any layer. The only `ENV` values
are cargo/rustup paths.

## Verifying the image (RED then GREEN)

`src/tools/test-verify-docker.sh` runs both halves and writes a summary:

- **RED** against `rust:1.89.0-slim-bookworm`: the base tag has `rustc` and `cargo` but
  **not** `rustfmt` or `clippy`. The verifier must exit 1 and print `MISSING-TOOLS`.
- **GREEN** against `mk64-rust:1.89.0`: all four tools present, all fixture checks pass,
  the verifier must exit 0 and print `REQUIRED-OK`.

`verify-docker.sh` does not merely print `--version`. It exercises the tools:

| check | expectation |
|---|---|
| `rustfmt --check` on unformatted fixture | nonzero (rejected) |
| `rustfmt --check` on formatted fixture | exit 0 |
| `cargo clippy -- -D warnings` on clean fixture | exit 0 |
| `cargo clippy -- -D warnings` on warning fixture | nonzero |

It needs a writable temp dir, so it is run with `--read-only` plus `--tmpfs /tmp`, and it
points `CARGO_TARGET_DIR` at that temp dir.

```sh
sh src/tools/test-verify-docker.sh      # exit 0 only if RED fails and GREEN passes
sh src/tools/run-container.sh src/tools/verify-docker.sh mk64-rust:1.89.0 verify
```

`run-container.sh` runs the image's own `mk64` user; it does **not** override `--user`,
so checks reflect what the image actually provides. It exports `MSYS_NO_PATHCONV=1` and
`MSYS2_ARG_CONV_EXCL='*'` so Git Bash / MSYS does not rewrite `--entrypoint /bin/sh`
paths into Windows form. All container output goes to `src/logs/<name>.txt`.

## CI topology

The same three layers, in order, because each one gates the next:

1. **Build** the pinned image. A changed digest or a failed `rustup component add`
   stops here.
2. **Verify** the image by running `src/tools/verify-docker.sh` inside it with
   `--network=none`. This is the RED/GREEN harness; it proves the toolchain really
   formats and lints, not just that binaries exist.
3. **Use** the image for the game build and tests, mounting the workspace read-only
   and writing artifacts to `src/logs`.

Because steps 2 and 3 mount the workspace read-only and disable the network, a green
CI run proves the toolchain is self-contained and cannot have silently fetched a
component or mutated sources. Evidence for every step is a file under `src/logs/`,
never console scrollback.

### Deep ROM content scan (opt-in)

The `deep-scan` job is gated on the `MK64_DEEP_SCAN` repository variable and only runs when that variable is set to `on`; it is opt-in because it needs a machine or runner with the user-supplied ROM mounted, and it is deliberately not a required check.
