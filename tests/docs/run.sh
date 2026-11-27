#!/usr/bin/env bash
# Runs the documentation consistency tests inside the pinned image; the caller reads the log file.
set -u
image="python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b"
log_path="${1:-/src/tests/docs/evidence/run.txt}"
docker run --rm --network none \
  --env PYTHONDONTWRITEBYTECODE=1 \
  --volume "$(pwd)/src:/src" \
  --workdir /src/tests/docs \
  "$image" \
  sh -c "python -m unittest discover -s /src/tests/docs -p 'test_*.py' -v > '${log_path}' 2>&1"
echo "documentation test exit code: $?"
