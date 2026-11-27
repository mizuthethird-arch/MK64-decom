# Toolkit scripts

Everything here runs inside Docker. No local Rust, Python or Node is needed.

## Start work in one command

From the repository root (`src/`):

```sh
sh tools/bootstrap.sh
```

It runs the two smoke checks from a clean checkout: the docs suite in the pinned
`python:3.12-slim` image, then `tools/verify-docker.sh` inside the pinned Rust image
(building that image first if it is absent). It prints `BOOTSTRAP-OK` and exits 0 only
when both pass.

Measured on Windows 11 + Docker Desktop, executed through WSL Ubuntu-26.04
(docker server 29.9.0, linux/amd64), against a fresh copy with no ROM, no logs and no
Python caches:

| case | wall clock |
|---|---|
| warm images (normal run) | **2.44s - 2.50s** over three runs |
| Rust image absent, built on the fly | **4.22s** |

The docs suite itself is ~0.18s of that (288 tests, 13 skipped without a ROM); the rest
is docker CLI overhead across three container operations.

### Per-platform notes

- **Linux / WSL / macOS**: `sh tools/bootstrap.sh` works as written.
- **Windows with Git Bash / MSYS**: works, and `MSYS_NO_PATHCONV=1` is already exported
  by `tools/run-container.sh`; `bootstrap.sh` passes only absolute host paths, which MSYS
  rewrites unless that variable is set, so prefer Git Bash over cmd.exe.
- **Windows without a POSIX shell**: run it inside WSL, e.g.
  `wsl -d Ubuntu-26.04 -- bash -lc 'cd /mnt/d/.../src && sh tools/bootstrap.sh'`.
  There is no PowerShell port; Docker Desktop supplies the engine, WSL supplies `sh`.
- **CI**: nothing to install - the GitHub runner already has docker and bash.

### Overrides and failure behaviour

`DOCS_IMAGE`, `RUST_IMAGE` and `DOCKERFILE` can be overridden from the environment.
`DOCS_IMAGE` must be pinned by digest (`name@sha256:<64 lowercase hex>`). An unset
variable takes the default; an explicitly empty or malformed one fails with a message
naming the exact reason, for example:

```
BOOTSTRAP-FAIL: DOCS_IMAGE is empty; set it to a pinned python:3.12-slim digest reference
BOOTSTRAP-FAIL: DOCS_IMAGE must be pinned by digest (name@sha256:<64 hex>), got 'python:3.12-slim'
BOOTSTRAP-FAIL: DOCS_IMAGE digest must be 64 hex chars, got 8
BOOTSTRAP-FAIL: RUST_IMAGE must be a plain image tag (no spaces, no digest), got 'a b'
```

Every failure line starts with `BOOTSTRAP-FAIL:` and names one reason, so CI logs a cause
rather than a stack of guesses.

## The other scripts

| script | role |
|---|---|
| `verify-docker.sh` | runs **inside** the container; proves rustc, cargo, rustfmt and clippy work on fixtures and fails if the uid is 0 |
| `run-container.sh` | host helper; runs a workspace script in the image as the image's own `mk64` user, logs to `src/logs/<name>.txt` |
| `test-verify-docker.sh` | RED/GREEN harness for the image: fails on an image lacking rustfmt/clippy, passes on the pinned one |
| `test-bootstrap.sh` | copies the repo to a scratch dir and asserts `bootstrap.sh` reaches `BOOTSTRAP-OK` |
| `test-secret-scan.sh` | proves the secret scan: clean tree passes, eight planted secrets are each detected, a clean file stays clean |
| `scan-for-rom-content.py` | opt-in deep scan for resident ROM content in tracked files |
| `bootstrap.sh` | the one command above |

```sh
sh tools/test-verify-docker.sh   # image proof, writes src/logs/test-verify-docker.txt
sh tools/test-bootstrap.sh       # bootstrap proof, writes src/logs/test-bootstrap.txt
sh tools/test-secret-scan.sh     # secret-scan proof, writes src/logs/test-secret-scan.txt
```

## Secret scan

`.gitleaks.toml` at the repository root configures the scan. It keeps gitleaks' default
rules and adds `mk64-private-key-header`, which catches a bare
`-----BEGIN RSA|EC|OPENSSH|PGP|DSA PRIVATE KEY-----` header — the default rules miss
that on its own, and a leaked header is the first line of a key.

Two CI jobs use it, both with the image pinned by digest and run with `--network none`:

| job | display name | when | timeout |
|---|---|---|---|
| working tree scan | `secret scan` | every push and pull request | 10 min |
| history scan | `secret history scan` | only when `vars.MK64_HISTORY_SCAN == 'on'`, or a manual run | 20 min |

The working tree scan is the required check. The history scan is opt-in because a secret
committed once stays exposed in a public repository's history, but rescanning all of it on
every pull request is slow and gets ignored.

Scans run with `--source .` so reported paths are relative; the allowlist in
`.gitleaks.toml` matches **paths**, never patterns, so the shapes it tolerates inside the
scanner and its fixtures are still detected anywhere else in the tree. Every gitleaks
error exits nonzero, so the step fails closed rather than passing quietly.

## Toolkit follow-up needed (for the docs lane)

Resolved on 2026-11-27: `tests/docs/test_plan_lint.py` now guards `RealPlanTest` with
`@unittest.skipUnless(PLAN_REACHABLE, ...)`, so the bootstrap is green on a clean clone
(288 tests, `OK (skipped=13)`). Before that guard existed the suite failed with
`FileNotFoundError: '/_bp_TASKS.json'` because the class read
`SOURCE_ROOT.parent / "_bp_TASKS.json"`, a path outside the repository.
