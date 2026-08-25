#!/bin/bash
# verify-bug66-phase-d.sh — BUG-66 Phase D: remove blind UPSERT from version-heartbeat.php
# Tests FAIL before the fix; PASS after.
#
# T8 is the BUG-66 regression test: an unknown device_token cannot create a row.
# The UPSERT was deliberate (SESSION_LOG S33/S37 — pre-pairing auto-registration).
# Now safe to remove because Phase C auth (verify_device_request) rejects unknown
# devices at 401 before the SQL is ever reached.
#
# NOTE: Phase D requires the approval handler (Phase A wp-admin queue) to INSERT
# the initial amboat_devices row when approving a device. Without that, every
# approved device gets a 404 on first heartbeat. Tracked as Phase A gap.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
HEARTBEAT="$REPO_ROOT/deployment/features/autonomous-agents/php/version-heartbeat.php"

PASS=0
FAIL=0

check() {
    local num="$1" desc="$2" result="$3"
    if [ "$result" = "pass" ]; then
        echo "T${num} PASS: ${desc}"
        PASS=$((PASS + 1))
    else
        echo "T${num} FAIL: ${desc}"
        FAIL=$((FAIL + 1))
    fi
}

# T1 — NEGATIVE: INSERT ... ON DUPLICATE KEY UPDATE no longer present
if ! grep -q 'ON DUPLICATE KEY UPDATE' "$HEARTBEAT" 2>/dev/null; then
    check 1 "NEGATIVE: blind UPSERT (INSERT … ON DUPLICATE KEY UPDATE) removed" pass
else
    check 1 "NEGATIVE: blind UPSERT (INSERT … ON DUPLICATE KEY UPDATE) removed" fail
fi

# T2 — UPDATE statement (not INSERT) used for heartbeat record
if grep -q 'UPDATE amboat_devices SET\|UPDATE.*amboat_devices' "$HEARTBEAT" 2>/dev/null; then
    check 2 "UPDATE used in place of INSERT (heartbeat writes to existing row only)" pass
else
    check 2 "UPDATE used in place of INSERT (heartbeat writes to existing row only)" fail
fi

# T3 — 404 unknown_device returned when UPDATE affects 0 rows
if grep -q 'unknown_device\|affected_rows.*=== 0\|affected_rows.*==.*0\|404' "$HEARTBEAT" 2>/dev/null; then
    check 3 "404 returned when device_token not found in amboat_devices (T8 BUG-66)" pass
else
    check 3 "404 returned when device_token not found in amboat_devices (T8 BUG-66)" fail
fi

# T4 — the old comment ("safe against duplicate rows") is removed with the statement
if ! grep -q 'device_token has UNIQUE constraint\|safe.*duplicate' "$HEARTBEAT" 2>/dev/null; then
    check 4 "NEGATIVE: misleading 'safe' comment removed along with UPSERT statement" pass
else
    check 4 "NEGATIVE: misleading 'safe' comment removed along with UPSERT statement" fail
fi

# T5 — verify_device_request() still present (Phase C not regressed)
if grep -q 'verify_device_request' "$HEARTBEAT" 2>/dev/null; then
    check 5 "Phase C regression guard: verify_device_request() still called" pass
else
    check 5 "Phase C regression guard: verify_device_request() still called" fail
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
echo "Note: Phase A gap — approval handler must INSERT into amboat_devices on device approval."
echo "Note: Without that, approved devices get 404 on first heartbeat until row is pre-seeded."
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
