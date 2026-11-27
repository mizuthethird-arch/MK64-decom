#!/bin/sh
# Container-side proof that the MK64 Rust image carries rustc, cargo, rustfmt and clippy and that rustfmt and clippy actually work, with no network access.
set -u

missing=""
fail=0
if ! work=$(mktemp -d 2>/dev/null); then
    echo "FAIL: cannot create a writable temp dir (TMPDIR=${TMPDIR:-/tmp}); run with --tmpfs /tmp" >&2
    exit 1
fi
trap 'rm -rf "$work"' EXIT

report() {
    name=$1
    version_cmd=$2
    if version=$($version_cmd 2>/dev/null); then
        echo "$name: $version"
    else
        echo "$name: MISSING"
        missing="$missing $name"
    fi
}

echo "user: $(id -un 2>/dev/null || echo unknown) uid=$(id -u 2>/dev/null || echo unknown)"
echo "os: $(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || echo unknown)"

report rustc "rustc --version"
report cargo "cargo --version"
report rustfmt "rustfmt --version"
report clippy "cargo clippy --version"

if [ -n "$missing" ]; then
    echo "MISSING-TOOLS:$missing" >&2
    echo "FAIL: required Rust tools missing from this image:$missing" >&2
    exit 1
fi

if [ "$(id -u)" = "0" ]; then
    echo "FAIL: image runs as root; a non-root user is required" >&2
    exit 1
fi

printf 'fn unformatted( ) ->u8{\n1\n}\n' > "$work/bad.rs"
if rustfmt --check "$work/bad.rs" > "$work/rustfmt-bad.log" 2>&1; then
    echo "FAIL: rustfmt --check accepted an unformatted file" >&2
    fail=1
else
    echo "rustfmt-check-unformatted: nonzero (rejected as expected)"
fi

printf 'fn formatted() -> u8 {\n    1\n}\n' > "$work/good.rs"
if rustfmt --check "$work/good.rs" > "$work/rustfmt-good.log" 2>&1; then
    echo "rustfmt-check-formatted: exit=0 (accepted as expected)"
else
    echo "FAIL: rustfmt --check rejected an already formatted file" >&2
    fail=1
fi

mkdir -p "$work/clippy/src"
printf '[package]\nname = "clippy-fixture"\nversion = "0.1.0"\nedition = "2021"\n' > "$work/clippy/Cargo.toml"
printf '#[allow(dead_code)]\npub fn ok() -> u8 {\n    1\n}\n' > "$work/clippy/src/lib.rs"
if (cd "$work/clippy" && CARGO_TARGET_DIR="$work/target" cargo clippy --offline -- -D warnings) > "$work/clippy-good.log" 2>&1; then
    echo "clippy-clean-fixture: exit=0 (accepted as expected)"
else
    echo "FAIL: clippy flagged a clean fixture" >&2
    sed 's/^/  /' "$work/clippy-good.log" >&2
    fail=1
fi

printf 'pub fn bad() -> u8 {\n    let unused = 1;\n    2.0 as u8\n}\n' > "$work/clippy/src/lib.rs"
if (cd "$work/clippy" && CARGO_TARGET_DIR="$work/target" cargo clippy --offline -- -D warnings) > "$work/clippy-bad.log" 2>&1; then
    echo "FAIL: clippy -D warnings accepted a fixture with a warning" >&2
    fail=1
else
    echo "clippy-violation-fixture: nonzero (rejected as expected)"
fi

if [ "$fail" -ne 0 ]; then
    echo "FAIL: rustfmt or clippy misbehaved on fixtures" >&2
    exit 1
fi

echo "REQUIRED-OK rustc cargo rustfmt clippy as $(id -un)"
exit 0
