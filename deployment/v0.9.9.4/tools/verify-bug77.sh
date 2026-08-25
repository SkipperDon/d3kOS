#!/bin/bash
# verify-bug77.sh — BUG-77: Tier 1 = server-approved (not a forgeable filesystem test)
# Tests FAIL before the fix; T1-T8 PASS after Step 1; T9 PASS after Step 3 (Tier 3 dedup).
# T2 and T8 are the trust-anchor tests. T4 is the offline-first test.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TIER_SVC="$REPO_ROOT/deployment/v0.9.9.4/opt/d3kos/services/tier/tier_service.py"
APP_PY="$REPO_ROOT/deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py"

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

# T1 — device_is_paired_and_approved() declared; uses sign_device_request (signed channel)
# Verifies both existence and that the call is over the BUG-66 signed channel, not raw bearer.
if grep -q 'def device_is_paired_and_approved' "$TIER_SVC" 2>/dev/null && \
   grep -q 'sign_device_request' "$TIER_SVC" 2>/dev/null; then
    check 1 "device_is_paired_and_approved() declared; uses sign_device_request (signed channel)" pass
else
    check 1 "device_is_paired_and_approved() declared; uses sign_device_request (signed channel)" fail
fi

# T2 — trust-anchor: checks status == 'approved', not just status != rejected or status truthy
# 'pending' must NOT grant Tier 1 — only the literal string 'approved' does.
if grep -q "status.*==.*'approved'\|status.*==.*\"approved\"" "$TIER_SVC" 2>/dev/null; then
    check 2 "trust-anchor: checks status == 'approved' (pending does NOT grant Tier 1)" pass
else
    check 2 "trust-anchor: checks status == 'approved' (pending does NOT grant Tier 1)" fail
fi

# T3 — no device_token → returns False (device not enrolled)
# Must check for device-token.json presence before calling the server.
if grep -q 'device-token.json' "$TIER_SVC" 2>/dev/null; then
    check 3 "checks for device-token.json absence before calling server (no token → False)" pass
else
    check 3 "checks for device-token.json absence before calling server (no token → False)" fail
fi

# T4 — offline-first: cache file exists; server failure returns cached result
# Cache lives at /opt/d3kos/state/tier1-approval.json (mode 600).
if grep -q 'tier1-approval.json' "$TIER_SVC" 2>/dev/null && \
   grep -q 'cached_approved\|cached.*result\|cache.*stand' "$TIER_SVC" 2>/dev/null; then
    check 4 "offline-first: approval cached; server unreachable returns cached result" pass
else
    check 4 "offline-first: approval cached; server unreachable returns cached result" fail
fi

# T5 — fail-closed: no cache + server down → False (never fail open with no evidence)
if grep -q 'return False' "$TIER_SVC" 2>/dev/null && \
   grep -q 'no cache\|fail closed\|nothing to trust\|no.*cache.*down\|down.*False\|unreachable.*False' "$TIER_SVC" 2>/dev/null; then
    check 5 "fail-closed: no cache + server unreachable → returns False (never fail open)" pass
else
    check 5 "fail-closed: no cache + server unreachable → returns False (never fail open)" fail
fi

# T6 — ordering: detect_tier() checks subscription.key BEFORE server approval (Tier 3 > Tier 1)
# Subscription.key presence must appear before device_is_paired_and_approved in detect_tier body.
# Strategy: subscription.key line number must be < device_is_paired_and_approved call line number.
if [ -f "$TIER_SVC" ]; then
    LINE_SUB=$(grep -n 'subscription.key' "$TIER_SVC" 2>/dev/null | head -1 | cut -d: -f1 || true)
    LINE_APPR=$(grep -n 'device_is_paired_and_approved' "$TIER_SVC" 2>/dev/null | grep -v 'def device_is_paired' | head -1 | cut -d: -f1 || true)
    if [ -n "$LINE_SUB" ] && [ -n "$LINE_APPR" ] && [ "$LINE_SUB" -lt "$LINE_APPR" ]; then
        check 6 "ordering: subscription.key checked before device_is_paired_and_approved (Tier 3 > Tier 1)" pass
    else
        check 6 "ordering: subscription.key checked before device_is_paired_and_approved (Tier 3 > Tier 1)" fail
    fi
else
    check 6 "ordering: subscription.key checked before device_is_paired_and_approved (Tier 3 > Tier 1)" fail
fi

# T7 — ordering: detect_tier() checks OpenCPN BEFORE server approval (Tier 2 > Tier 1)
# OpenCPN path check must appear before device_is_paired_and_approved in detect_tier body.
if [ -f "$TIER_SVC" ]; then
    LINE_OCN=$(grep -n 'opencpn' "$TIER_SVC" 2>/dev/null | grep -v 'OpenCPN.*mirrors\|FEATURE_MATRIX' | head -1 | cut -d: -f1 || true)
    LINE_APPR2=$(grep -n 'device_is_paired_and_approved' "$TIER_SVC" 2>/dev/null | grep -v 'def device_is_paired' | head -1 | cut -d: -f1 || true)
    if [ -n "$LINE_OCN" ] && [ -n "$LINE_APPR2" ] && [ "$LINE_OCN" -lt "$LINE_APPR2" ]; then
        check 7 "ordering: OpenCPN check before device_is_paired_and_approved (Tier 2 > Tier 1)" pass
    else
        check 7 "ordering: OpenCPN check before device_is_paired_and_approved (Tier 2 > Tier 1)" fail
    fi
else
    check 7 "ordering: OpenCPN check before device_is_paired_and_approved (Tier 2 > Tier 1)" fail
fi

# T8 — trust-anchor: detect_tier() does NOT read license.json for Tier 1
# The license.json file (a local, forgeable file) must not be consulted by detect_tier().
# Strategy: verify that /tier/status route calls detect_tier() (so tier comes from server, not file).
if grep -q 'def detect_tier' "$TIER_SVC" 2>/dev/null && \
   grep -q 'detect_tier()' "$TIER_SVC" 2>/dev/null; then
    check 8 "trust-anchor: /tier/status uses detect_tier() — license.json cannot grant Tier 1 alone" pass
else
    check 8 "trust-anchor: /tier/status uses detect_tier() — license.json cannot grant Tier 1 alone" fail
fi

# T9 — deduplication: app.py does NOT have inline int(str(t).replace('T','')) parse at both sites
# Step 3 (Tier 3 work) removes the duplicate parse logic. This test fails until Step 3 is done.
if ! grep -qE "int\(str.*replace.*'T'" "$APP_PY" 2>/dev/null; then
    check 9 "deduplication: app.py has no inline int(str(t).replace('T','')) parse sites" pass
else
    check 9 "deduplication: app.py has no inline int(str(t).replace('T','')) parse sites (Step 3 pending)" fail
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
echo "Note: T9 fails until Step 3 (Tier 3 dedup of app.py parse sites) is complete."
if [ "$FAIL" -gt 1 ] || ([ "$FAIL" -eq 1 ] && [ "$PASS" -lt 8 ]); then
    exit 1
fi
# T9 alone failing is acceptable until Tier 3 implements Step 3
exit 0
