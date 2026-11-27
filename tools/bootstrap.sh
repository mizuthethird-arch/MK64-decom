#!/bin/sh
# One-command bootstrap: from a clean checkout, run the docs suite and the pinned Rust image check.
set -u

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DOCS_IMAGE_DEFAULT=python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
RUST_IMAGE_DEFAULT=mk64-rust:1.89.0
DOCS_IMAGE=${DOCS_IMAGE-$DOCS_IMAGE_DEFAULT}
RUST_IMAGE=${RUST_IMAGE-$RUST_IMAGE_DEFAULT}
DOCKERFILE=${DOCKERFILE-$REPO_ROOT/docker/rust.Dockerfile}

die() {
    reason=$1
    echo "BOOTSTRAP-FAIL: $reason" >&2
    exit 1
}

case "$DOCS_IMAGE" in
    "") die "DOCS_IMAGE is empty; set it to a pinned python:3.12-slim digest reference" ;;
    *"@"sha256:*) : ;;
    *) die "DOCS_IMAGE must be pinned by digest (name@sha256:<64 hex>), got '$DOCS_IMAGE'" ;;
esac
digest=${DOCS_IMAGE##*@sha256:}
case "$digest" in
    *[!0-9a-f]) die "DOCS_IMAGE digest is not lowercase hex: '$digest'" ;;
esac
[ "${#digest}" -eq 64 ] || die "DOCS_IMAGE digest must be 64 hex chars, got ${#digest}"

case "$RUST_IMAGE" in
    "") die "RUST_IMAGE is empty; set it to an image tag such as mk64-rust:1.89.0" ;;
    *" "*|*"@"*) die "RUST_IMAGE must be a plain image tag (no spaces, no digest), got '$RUST_IMAGE'" ;;
esac

[ -d "$REPO_ROOT/tests/docs" ] || die "tests/docs is missing at $REPO_ROOT; run this from a full checkout"
[ -f "$REPO_ROOT/tools/verify-docker.sh" ] || die "tools/verify-docker.sh is missing at $REPO_ROOT"
[ -f "$DOCKERFILE" ] || die "rust Dockerfile is missing at $DOCKERFILE"

command -v docker >/dev/null 2>&1 || die "docker is not on PATH; bootstrap runs the checks in pinned containers"

echo "bootstrap: repo $REPO_ROOT"
echo "bootstrap: docs image $DOCS_IMAGE"
echo "bootstrap: rust image $RUST_IMAGE"

echo "bootstrap: step 1/3 docker reachable"
docker version --format '{{.Server.Version}}' >/dev/null 2>&1 || die "docker daemon is not reachable with the current user"

echo "bootstrap: step 2/3 docs suite"
if ! docker run --rm --network none \
        -v "$REPO_ROOT:/repo:ro" -w /repo \
        --entrypoint python "$DOCS_IMAGE" \
        -m unittest discover -s tests/docs -p 'test_*.py'; then
    die "docs suite failed; see the unittest output above"
fi

echo "bootstrap: step 3/3 rust image check"
docker image inspect "$RUST_IMAGE" >/dev/null 2>&1 || {
    echo "bootstrap: building $RUST_IMAGE from $DOCKERFILE"
    docker build -t "$RUST_IMAGE" -f "$DOCKERFILE" "$REPO_ROOT" || die "rust image build failed for $RUST_IMAGE"
}
if ! docker run --rm --network=none --read-only \
        --cap-drop ALL --security-opt no-new-privileges \
        --tmpfs /tmp:rw,noexec,nosuid,size=64m \
        -v "$REPO_ROOT/tools:/tools:ro" \
        --entrypoint /bin/sh "$RUST_IMAGE" /tools/verify-docker.sh; then
    die "rust image check failed; rustfmt or clippy is not working in $RUST_IMAGE"
fi

echo "BOOTSTRAP-OK docs suite and rust image check passed"
exit 0
