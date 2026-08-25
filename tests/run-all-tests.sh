#!/bin/bash
# run-all-tests.sh — DEPRECATED: renamed to run-all.sh (PHASE1-test-harness.md T8)
# This shim exists so that historical docs and any Pi scripts that invoke
# run-all-tests.sh continue to work without silent failure.
#
# The canonical runner is tests/run-all.sh — all work should target that file.

echo ""
echo "[DEPRECATED] run-all-tests.sh is superseded by run-all.sh (PHASE1-test-harness.md)"
echo "Redirecting to: $(dirname "$0")/run-all.sh"
echo ""

exec "$(dirname "$0")/run-all.sh" "$@"
