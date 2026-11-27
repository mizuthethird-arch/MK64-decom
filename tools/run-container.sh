#!/bin/sh
# Host-side helper: run a script inside a pinned project image against the workspace, capturing all output to file.
set -u

usage() {
    echo "usage: run-container.sh <script-path-in-workspace> [image] [log-name]" >&2
    echo "  example: run-container.sh src/tools/verify-docker.sh mk64-rust:1.89.0 verify-docker" >&2
    exit 2
}

[ "$#" -ge 1 ] || usage

SCRIPT=$1
IMAGE=${2:-mk64-rust:1.89.0}
NAME=${3:-$(basename "$SCRIPT" .sh)}

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
LOGS="$ROOT/src/logs"
mkdir -p "$LOGS"
LOG="$LOGS/$NAME.txt"

case "$SCRIPT" in
    /*) SCRIPT_REL=${SCRIPT#"$ROOT"/} ;;
    *) SCRIPT_REL=$SCRIPT ;;
esac

if [ ! -f "$ROOT/$SCRIPT_REL" ]; then
    echo "error: script not found in workspace: $SCRIPT_REL" >&2
    exit 2
fi
if [ ! -x "$ROOT/$SCRIPT_REL" ]; then
    echo "error: script is not executable: $SCRIPT_REL (run chmod +x)" >&2
    exit 2
fi

: > "$LOG"

export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL='*'

{
    echo "# image: $IMAGE"
    echo "# script: /work/$SCRIPT_REL (workspace mounted read-only, network disabled, image user mk64)"
    docker run --rm \
        --network=none \
        --read-only \
        --cap-drop ALL \
        --security-opt no-new-privileges \
        --tmpfs "/tmp:rw,noexec,nosuid,size=64m" \
        -v "$ROOT:/work:ro" \
        -w /work \
        --entrypoint "/bin/sh" "$IMAGE" "/work/$SCRIPT_REL"
    echo "[exit code: $?]"
} >> "$LOG" 2>&1

exit_code=$(tail -n 1 "$LOG" | sed -n 's/^\[exit code: \(.*\)\]$/\1/p')
echo "exit code: ${exit_code:-unknown}"
echo "log: $LOG"
exit "${exit_code:-1}"