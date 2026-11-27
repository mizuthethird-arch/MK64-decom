#!/bin/sh
# Test-first harness: the verifier must fail on an image without rustfmt/clippy and pass on the pinned toolchain image.
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
TOOLS="$ROOT/src/tools"
LOGS="$ROOT/src/logs"
RED_IMAGE=${RED_IMAGE:-rust:1.89.0-slim-bookworm}
GREEN_IMAGE=${GREEN_IMAGE:-mk64-rust:1.89.0}
SUMMARY="$LOGS/test-verify-docker.txt"

mkdir -p "$LOGS"
: > "$SUMMARY"
fail=0

run_case() {
    label=$1
    image=$2
    want_exit=$3
    want_marker=$4
    log="$LOGS/$label.txt"

    docker run --rm --network=none --read-only --cap-drop ALL --security-opt no-new-privileges \
        --tmpfs /tmp:rw,noexec,nosuid,size=64m \
        -v "$TOOLS:/tools:ro" \
        --entrypoint /bin/sh "$image" /tools/verify-docker.sh > "$log" 2>&1
    actual_exit=$?
    echo "case=$label image=$image expected_exit=$want_exit actual_exit=$actual_exit" >> "$SUMMARY"

    if [ "$actual_exit" -ne "$want_exit" ]; then
        echo "RESULT FAIL case=$label wrong exit code (want $want_exit got $actual_exit)" >> "$SUMMARY"
        fail=1
        return
    fi
    if ! grep -q "$want_marker" "$log"; then
        echo "RESULT FAIL case=$label exit matched but marker '$want_marker' absent from $log" >> "$SUMMARY"
        fail=1
        return
    fi
    echo "RESULT PASS case=$label marker=$want_marker" >> "$SUMMARY"
}

run_case red-image-without-rustfmt-clippy "$RED_IMAGE" 1 "MISSING-TOOLS"
run_case green-pinned-toolchain-image "$GREEN_IMAGE" 0 "REQUIRED-OK"

if [ "$fail" -ne 0 ]; then
    echo "OVERALL FAIL" >> "$SUMMARY"
    cat "$SUMMARY"
    exit 1
fi
echo "OVERALL PASS" >> "$SUMMARY"
cat "$SUMMARY"
exit 0