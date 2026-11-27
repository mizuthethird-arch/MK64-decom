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
| `ci/plan_lint_run.py` | runs the plan lint over the blueprint plan against a pinned violation baseline |
| `ci/coverage_lint_run.py` | fails naming any screen in the catalogue that no task owns |
| `ci/prompt.py` | renders one task prompt from the plan data; see `tools/prompt/README.md` |
| `bootstrap.sh` | the one command above |

```sh
sh tools/test-verify-docker.sh   # image proof, writes src/logs/test-verify-docker.txt
sh tools/test-bootstrap.sh       # bootstrap proof, writes src/logs/test-bootstrap.txt
sh tools/test-secret-scan.sh     # secret-scan proof, writes src/logs/test-secret-scan.txt
```

## Plan and coverage checks

Two CI jobs read data that lives **outside** this repository, because the blueprint
directory is not part of the public repo:

| job | display name | step | timeout |
|---|---|---|---|
| plan lint | `plan lint` | `python tools/ci/plan_lint_run.py "$MK64_PLAN_DIR"` | 10 min |
| screen coverage | `screen coverage` | `python tools/ci/coverage_lint_run.py "$MK64_PLAN_DIR"` | 10 min |

Both jobs are **opt-in and intentionally not required checks**. They run only when the
repository variable `MK64_PLAN_CHECK` is set to `on` **and** a blueprint directory is
mounted on the runner at `MK64_PLAN_DIR`; otherwise they are skipped, because the plan
data is not part of this public repository and a check that is red only because the data
is absent would teach everyone to ignore red.

When the variable is on, the runners still fail closed: if the mount is missing they exit
**2** and print which files they could not find. They never exit 0 without having read the
real data, so an opted-in run can never report success from a missing blueprint.

The plan lint pins the known baseline in the runner:

```
records: 1036 (expected 1036)
violations: 435
   412 prose done_when       (baseline 412)
    23 UI task with no screens  (baseline 23)
     0 other
PLAN-LINT-OK: no violation outside the pinned baseline
```

A new violation of either known kind, or any violation of a third kind, fails and is
named. The screen coverage job fails and names any catalogue screen that no task owns.

The baseline fails only when a count **exceeds** it, because a drop is an improvement and
must not break the build. When the counts drop, lower the pinned baseline in the same pull
request, otherwise a later regression back to the old number will not be caught.

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
