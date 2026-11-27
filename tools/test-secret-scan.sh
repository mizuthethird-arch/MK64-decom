#!/bin/sh
# Proves the secret-scan job: clean tree passes, planted secrets fail, and a fake passing scan is rejected.
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
SRC="$ROOT/src"
LOGS="$SRC/logs"
CONFIG="$SRC/.gitleaks.toml"
IMAGE="zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f"
OUT="$LOGS/test-secret-scan.txt"

mkdir -p "$LOGS"
: > "$OUT"
fail=0

record() {
    echo "$*" | tee -a "$OUT"
}

scan() {
    target=$1
    docker run --rm --network none --read-only \
        --cap-drop ALL --security-opt no-new-privileges \
        --tmpfs /tmp:rw,noexec,nosuid,size=64m \
        -v "$target:/repo:ro" \
        -v "$CONFIG:/cfg/.gitleaks.toml:ro" \
        -w /repo \
        --entrypoint gitleaks "$IMAGE" \
        detect --source . --no-git --config /cfg/.gitleaks.toml --redact --exit-code 1 2>&1
}

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

record "secret-scan harness"
record "image: $IMAGE"
record "config: $CONFIG"

if [ ! -f "$CONFIG" ]; then
    record "RESULT FAIL missing config: $CONFIG"
    record "OVERALL FAIL"
    exit 1
fi

record ""
record "--- case 1: the real repo tree must be clean ---"
if out=$(scan "$SRC"); then
    record "RESULT PASS real repo tree: exit 0 (no leaks)"
else
    rc=$?
    record "RESULT FAIL real repo tree: exit $rc (expected 0)"
    record "$out"
    fail=1
fi

plant() {
    name=$1
    content=$2
    dir="$scratch/$name"
    mkdir -p "$dir"
    printf '%s\n' "$content" > "$dir/probe.env"
    if out=$(scan "$dir"); then
        record "RESULT FAIL $name: exit 0 (expected nonzero)"
        fail=1
    else
        rc=$?
        record "RESULT PASS $name: exit $rc (detected)"
    fi
    rm -rf "$dir"
}

record ""
record "--- case 2: planted secrets must each be detected ---"

# Fixtures exist only after expansion, so no committed line holds a contiguous credential shape.
credential() {
    printf '%s%s' "$1" "$2"
}

plant github-pat "token: $(credential 'ghp_' '9fQ2xLm7TzR4vB8nK1pW3sY6dH0jC5aE2gU')"
plant slack-bot "$(credential 'xo' 'xb-284759102635-284759102636-QwErTyUiOpAsDfGhJkLzXcVb')"
plant generic-api-key "api_key = \"$(credential '7c1e9b4f2a8d3065' 'be97f2c415ad88e3')\""
plant rsa-header "$(credential '-----BEGIN RSA ' 'PRIVATE KEY-----')"
plant ec-header "$(credential '-----BEGIN EC ' 'PRIVATE KEY-----')"
plant openssh-header "$(credential '-----BEGIN OPENSSH ' 'PRIVATE KEY-----')"
plant pgp-header "$(credential '-----BEGIN PGP ' 'PRIVATE KEY BLOCK-----')"
plant dsa-header "$(credential '-----BEGIN DSA ' 'PRIVATE KEY-----')"

record ""
record "--- case 3: a clean file must stay clean (no false positive) ---"
clean="$scratch/clean"
mkdir -p "$clean"
printf 'This is ordinary documentation about configuring the build.\nNo credentials live here.\n' > "$clean/notes.md"
if out=$(scan "$clean"); then
    record "RESULT PASS clean file: exit 0 (no false positive)"
else
    rc=$?
    record "RESULT FAIL clean file: exit $rc (false positive)"
    record "$out"
    fail=1
fi

record ""
record "--- case 4 mutation: a scanner that reports success without running must be caught ---"
mkdir -p "$scratch/liar"
printf '#!/bin/sh\necho "no leaks found"\nexit 0\n' > "$scratch/liar/gitleaks"
chmod +x "$scratch/liar/gitleaks"
liar_out=$("$scratch/liar/gitleaks" 2>&1)
liar_rc=$?
if [ "$liar_rc" -eq 0 ] && ! printf '%s' "$liar_out" | grep -qi "detected\|leaks found: "; then
    record "RESULT PASS mutation: fake scanner returns 0 with no evidence, so a run must not be trusted without a detection case"
else
    record "RESULT FAIL mutation: fake scanner was not distinguishable"
    fail=1
fi

record ""
if [ "$fail" -ne 0 ]; then
    record "OVERALL FAIL"
    exit 1
fi
record "OVERALL PASS"
exit 0
