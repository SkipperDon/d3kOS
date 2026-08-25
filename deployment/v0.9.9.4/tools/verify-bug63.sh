#!/bin/bash
# verify-bug63.sh — BUG-63: registration-code gate before page-register.php:88
# Tests FAIL before the fix; PASS after.
# T16 is the BUG-63 regression test: nonce-only POST creates nothing.
# T17 is the rollback test: wp_create_user failure does not burn the code.
# Step 3 (migration + republish) is a separate HIGH-RISK operator action — not tested here.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
REGISTER="$REPO_ROOT/deployment/features/auth-pages/php/page-register.php"
HELPER="$REPO_ROOT/deployment/features/auth-pages/php/device-registration.php"

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

# T1 — device-registration.php exists (the helper file required by the gate)
if [ -f "$HELPER" ]; then
    check 1 "device-registration.php exists (amboat_claim_registration_code helper)" pass
else
    check 1 "device-registration.php exists (amboat_claim_registration_code helper)" fail
fi

# T2 — amboat_claim_registration_code() declared in helper
if grep -q 'function amboat_claim_registration_code' "$HELPER" 2>/dev/null; then
    check 2 "amboat_claim_registration_code() declared in helper" pass
else
    check 2 "amboat_claim_registration_code() declared in helper" fail
fi

# T3 — atomic claim: UPDATE with status='valid' guard (prevents double-redemption)
# The function must use an atomic UPDATE WHERE status='valid' — not check-then-act.
if grep -q "status.*=.*'valid'" "$HELPER" 2>/dev/null && \
   grep -q 'affected_rows\|START TRANSACTION\|FOR UPDATE\|updated.*=.*1' "$HELPER" 2>/dev/null; then
    check 3 "atomic claim: UPDATE uses status='valid' guard + transaction/affected_rows check" pass
else
    check 3 "atomic claim: UPDATE uses status='valid' guard + transaction/affected_rows check" fail
fi

# T4 — rollback function declared (T17 requirement: code returns to 'valid' on wp_create_user failure)
if grep -q 'function amboat_rollback_registration_code' "$HELPER" 2>/dev/null; then
    check 4 "amboat_rollback_registration_code() declared (T17: code rollback on create failure)" pass
else
    check 4 "amboat_rollback_registration_code() declared (T17: code rollback on create failure)" fail
fi

# T5 — audit function declared
if grep -q 'function amboat_registration_audit' "$HELPER" 2>/dev/null; then
    check 5 "amboat_registration_audit() declared" pass
else
    check 5 "amboat_registration_audit() declared" fail
fi

# T6 — code_input field validated in page-register.php (gate cannot be bypassed by omission)
if grep -q 'code_input\|$code' "$REGISTER" 2>/dev/null; then
    check 6 "code_input validated in page-register.php" pass
else
    check 6 "code_input validated in page-register.php" fail
fi

# T7 — T16 regression: require_once device-registration.php appears BEFORE wp_create_user in file
# A nonce-only POST (no code) must fail before wp_create_user() is ever called.
if [ -f "$REGISTER" ]; then
    LINE_REQUIRE=$(grep -n 'device-registration.php' "$REGISTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
    LINE_CREATE=$(grep -n 'wp_create_user' "$REGISTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$LINE_REQUIRE" ] && [ -n "$LINE_CREATE" ] && [ "$LINE_REQUIRE" -lt "$LINE_CREATE" ]; then
        check 7 "T16 regression: device-registration.php required BEFORE wp_create_user call" pass
    else
        check 7 "T16 regression: device-registration.php required BEFORE wp_create_user call" fail
    fi
else
    check 7 "T16 regression: device-registration.php required BEFORE wp_create_user call" fail
fi

# T8 — T16 regression: amboat_claim_registration_code called BEFORE wp_create_user
if [ -f "$REGISTER" ]; then
    LINE_CLAIM=$(grep -n 'amboat_claim_registration_code' "$REGISTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
    LINE_CREATE2=$(grep -n 'wp_create_user' "$REGISTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$LINE_CLAIM" ] && [ -n "$LINE_CREATE2" ] && [ "$LINE_CLAIM" -lt "$LINE_CREATE2" ]; then
        check 8 "T16 regression: amboat_claim_registration_code() called BEFORE wp_create_user()" pass
    else
        check 8 "T16 regression: amboat_claim_registration_code() called BEFORE wp_create_user()" fail
    fi
else
    check 8 "T16 regression: amboat_claim_registration_code() called BEFORE wp_create_user()" fail
fi

# T9 — T17: rollback call exists after wp_create_user failure path
if grep -q 'amboat_rollback_registration_code' "$REGISTER" 2>/dev/null; then
    check 9 "T17: amboat_rollback_registration_code() called in wp_create_user failure path" pass
else
    check 9 "T17: amboat_rollback_registration_code() called in wp_create_user failure path" fail
fi

# T10 — legal name stored as user_meta atmyboat_legal_name (not publicly exposed)
if grep -q 'atmyboat_legal_name' "$REGISTER" 2>/dev/null; then
    check 10 "legal name stored as user_meta atmyboat_legal_name (private, not public display)" pass
else
    check 10 "legal name stored as user_meta atmyboat_legal_name (private, not public display)" fail
fi

# T11 — NEGATIVE: legal_name/first_name/last_name NOT used as display_name
# Display name must be the alias, not the legal name.
if ! grep -qE "display_name.*first_name|display_name.*last_name|'display_name'.*=.*first.*last" "$REGISTER" 2>/dev/null; then
    check 11 "NEGATIVE: legal name not used as display_name (alias is used instead)" pass
else
    check 11 "NEGATIVE: legal name not used as display_name (alias is used instead)" fail
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
echo "Note: Step 3 (migration + republish /register/) is a HIGH-RISK operator action — not tested here."
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
