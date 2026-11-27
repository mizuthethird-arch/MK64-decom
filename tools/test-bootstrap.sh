#!/bin/sh
# Runs tools/bootstrap.sh against a fresh copy of the repo in a container and asserts both smoke checks pass.
set -u

ROOT=${TEST_BOOTSTRAP_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)}
LOGS="$ROOT/src/logs"
BOOTSTRAP="$ROOT/src/tools/bootstrap.sh"
DOCS_IMAGE="python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b"
RUST_IMAGE="${RUST_IMAGE:-mk64-rust:1.89.0}"
OUT="$LOGS/test-bootstrap.txt"

mkdir -p "$LOGS"
: > "$OUT"
fail=0

record() {
    echo "$*" | tee -a "$OUT"
}

record "=== bootstrap test ==="
record "bootstrap: $BOOTSTRAP"
record "rust image: $RUST_IMAGE"

if [ ! -f "$BOOTSTRAP" ]; then
    record "RESULT FAIL missing bootstrap script: $BOOTSTRAP"
    record "OVERALL FAIL"
    exit 1
fi

record "docs image: $DOCS_IMAGE"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

cp -a "$ROOT/src/." "$scratch/repo/"
rm -rf "$scratch/repo/logs"
find "$scratch/repo" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
rm -f "$scratch/repo/rom/Mario Kart 64 (Europe) (Rev A).n64"

record "fresh copy: $scratch/repo (no ROM, no logs, no caches)"

record ""
record "--- running tools/bootstrap.sh ---"
start=$(date +%s)
if sh "$scratch/repo/tools/bootstrap.sh" >> "$OUT" 2>&1; then
    rc=0
else
    rc=$?
fi
end=$(date +%s)
record "bootstrap exit: $rc"
record "bootstrap elapsed: $((end - start))s"

if [ "$rc" -ne 0 ]; then
    record "RESULT FAIL bootstrap exited $rc"
    fail=1
fi

for marker in "BOOTSTRAP-OK" "docs suite" "REQUIRED-OK"; do
    if grep -q -- "$marker" "$OUT"; then
        record "RESULT PASS saw marker: $marker"
    else
        record "RESULT FAIL missing marker: $marker"
        fail=1
    fi
done

record ""
if [ "$fail" -ne 0 ]; then
    record "OVERALL FAIL"
    exit 1
fi
record "OVERALL PASS"
exit 0
