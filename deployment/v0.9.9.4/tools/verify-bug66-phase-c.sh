#!/bin/bash
# verify-bug66-phase-c.sh — BUG-66 Phase C: 12-endpoint Ed25519 migration
# Tests FAIL before migration (old AMBOAT_API_KEY auth); PASS after.
#
# Phase C applies to the 6 Pi→Server endpoints that authenticate with AMBOAT_API_KEY.
# Fleet endpoints (fleet-create/join/status/map/analytics/leave) use PWA JWT auth, not
# the shared key — they are out of scope for AMBOAT_API_KEY replacement (confirmed grep).
# Logged as OBSERVATION in EXECUTION-ORDER notes.
#
# T13: device-auth.php has server-side verify_device_request_server() (no WP_REST_Request)
# T14: legacy key path exists in device-auth.php (transition requirement)
# T15: legacy key usage is audited (amboat_registration_audit insert in legacy path)
# T1-T6: per-endpoint checks for 6 AMBOAT_API_KEY endpoints

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FEATURES="$REPO_ROOT/deployment/features"
DEVICE_AUTH="$REPO_ROOT/deployment/v0.9.9.4-server/mobile/device-auth.php"

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

# ── device-auth.php infrastructure ───────────────────────────────────────────

# T13 — server-side path: verify_device_request_server() declared
if grep -q 'function verify_device_request_server' "$DEVICE_AUTH" 2>/dev/null; then
    check 13 "device-auth.php: verify_device_request_server() declared (plain PHP path)" pass
else
    check 13 "device-auth.php: verify_device_request_server() declared (plain PHP path)" fail
fi

# T14 — legacy key path exists in device-auth.php (transition period, not yet removed)
if grep -q 'AMBOAT_API_KEY' "$DEVICE_AUTH" 2>/dev/null && \
   grep -q 'legacy_key_used\|legacy.*key.*path\|Legacy.*Bearer' "$DEVICE_AUTH" 2>/dev/null; then
    check 14 "device-auth.php: legacy Bearer-key path exists (transition period)" pass
else
    check 14 "device-auth.php: legacy Bearer-key path exists (transition period)" fail
fi

# T15 — legacy key usage is audited (amboat_registration_audit insert)
if grep -q "legacy_key_used" "$DEVICE_AUTH" 2>/dev/null && \
   grep -q "amboat_registration_audit\|registration_audit" "$DEVICE_AUTH" 2>/dev/null; then
    check 15 "device-auth.php: legacy key use written to amboat_registration_audit" pass
else
    check 15 "device-auth.php: legacy key use written to amboat_registration_audit" fail
fi

# ── Per-endpoint migration checks ────────────────────────────────────────────
# For each endpoint:
#   (a) require_once device-auth.php present
#   (b) verify_device_request() called
#   (c) NEGATIVE: old hash_equals(AMBOAT_API_KEY pattern absent

check_endpoint() {
    local tnum="$1" name="$2" file="$3"
    if [ ! -f "$file" ]; then
        check "$tnum" "$name: file exists" fail
        return
    fi
    local has_require has_verify no_legacy
    grep -q 'device-auth\.php' "$file" 2>/dev/null && has_require=1 || has_require=0
    grep -q 'verify_device_request\b' "$file" 2>/dev/null && has_verify=1 || has_verify=0
    # NEGATIVE: old auth pattern must be gone from this file
    ! grep -q 'hash_equals(AMBOAT_API_KEY' "$file" 2>/dev/null && no_legacy=1 || no_legacy=0

    if [ "$has_require" -eq 1 ] && [ "$has_verify" -eq 1 ] && [ "$no_legacy" -eq 1 ]; then
        check "$tnum" "$name: require device-auth + verify_device_request + no old shared key" pass
    else
        local detail=""
        [ "$has_require" -eq 0 ] && detail="${detail}[no require_once device-auth.php] "
        [ "$has_verify" -eq 0 ]  && detail="${detail}[no verify_device_request call] "
        [ "$no_legacy" -eq 0 ]   && detail="${detail}[hash_equals(AMBOAT_API_KEY) still present] "
        check "$tnum" "$name: ${detail}" fail
    fi
}

check_endpoint 1 "version-heartbeat.php" "$FEATURES/autonomous-agents/php/version-heartbeat.php"
check_endpoint 2 "failure-report.php"    "$FEATURES/autonomous-agents/php/failure-report.php"
check_endpoint 3 "fix-confirmed.php"     "$FEATURES/autonomous-agents/php/fix-confirmed.php"
check_endpoint 4 "community-markers-write.php" "$FEATURES/v0941-plan/php/community-markers-write.php"
check_endpoint 5 "community-position.php"      "$FEATURES/v0941-plan/php/community-position.php"
check_endpoint 6 "config-backup.php"           "$FEATURES/fi4-config-backup/php/config-backup.php"

echo ""
echo "Results: $PASS passed, $FAIL failed"
echo "Note: fleet-create/join/status/map/analytics/leave use PWA JWT auth — out of scope for AMBOAT_API_KEY replacement."
echo "Note: Legacy key path in device-auth.php is INTENTIONAL (transition period) — remove after fleet migration."
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
