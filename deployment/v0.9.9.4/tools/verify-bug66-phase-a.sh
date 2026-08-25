#!/bin/bash
# verify-bug66-phase-a.sh — BUG-66 Phase A: server-side device auth tables + endpoints
# Tests must FAIL before the files exist and PASS after they are written.
# T3 is the BUG-66 regression test: unknown token cannot create a DB row.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SERVER_ROOT="$REPO_ROOT/deployment/v0.9.9.4-server"
SQL_FILE="$SERVER_ROOT/sql/device-auth-tables.sql"
DEVICE_AUTH="$SERVER_ROOT/mobile/device-auth.php"
ENROL="$SERVER_ROOT/mobile/enrol.php"
STATUS_PHP="$SERVER_ROOT/mobile/status.php"
REQ_CODE="$SERVER_ROOT/mobile/request-code.php"
PLUGIN="$SERVER_ROOT/plugins/d3kos-device-auth/d3kos-device-auth.php"

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

# T1 — SQL file exists and contains all 4 required table names
ALL_TABLES=true
for t in amboat_device_enrolments amboat_registration_codes amboat_device_accounts amboat_registration_audit; do
    if ! grep -q "$t" "$SQL_FILE" 2>/dev/null; then
        ALL_TABLES=false
        break
    fi
done
[ "$ALL_TABLES" = "true" ] && check 1 "SQL file contains all 4 table definitions" pass \
                           || check 1 "SQL file contains all 4 table definitions" fail

# T2 — SQL stores code_hash CHAR(64) (SHA256 of the code, not the plaintext code)
if grep -q 'code_hash' "$SQL_FILE" 2>/dev/null && \
   grep -q 'CHAR(64)' "$SQL_FILE" 2>/dev/null; then
    check 2 "SQL uses code_hash CHAR(64) (SHA256 stored, not plaintext code)" pass
else
    check 2 "SQL uses code_hash CHAR(64) (SHA256 stored, not plaintext code)" fail
fi

# T3 — device-auth.php does NOT contain any INSERT or ON DUPLICATE KEY UPDATE
# (the BUG-66 fix: unknown tokens cannot self-register via the auth path)
if [ -f "$DEVICE_AUTH" ] && ! grep -qE 'INSERT|ON DUPLICATE KEY' "$DEVICE_AUTH" 2>/dev/null; then
    check 3 "NEGATIVE: device-auth.php contains no INSERT or UPSERT (BUG-66 regression test)" pass
else
    check 3 "NEGATIVE: device-auth.php contains no INSERT or UPSERT (BUG-66 regression test)" fail
fi

# T4 — device-auth.php contains verify_device_request and verify_device_signature
if grep -q 'verify_device_request' "$DEVICE_AUTH" 2>/dev/null && \
   grep -q 'verify_device_signature' "$DEVICE_AUTH" 2>/dev/null; then
    check 4 "device-auth.php declares verify_device_request() and verify_device_signature()" pass
else
    check 4 "device-auth.php declares verify_device_request() and verify_device_signature()" fail
fi

# T5 — device-auth.php uses sodium_crypto_sign_verify_detached (libsodium, not openssl)
if grep -q 'sodium_crypto_sign_verify_detached' "$DEVICE_AUTH" 2>/dev/null; then
    check 5 "device-auth.php uses sodium_crypto_sign_verify_detached (libsodium)" pass
else
    check 5 "device-auth.php uses sodium_crypto_sign_verify_detached (libsodium)" fail
fi

# T6 — device-auth.php uses WordPress transients for nonce replay cache
if grep -q 'get_transient' "$DEVICE_AUTH" 2>/dev/null && \
   grep -q 'set_transient' "$DEVICE_AUTH" 2>/dev/null; then
    check 6 "device-auth.php uses get_transient/set_transient for nonce replay cache" pass
else
    check 6 "device-auth.php uses get_transient/set_transient for nonce replay cache" fail
fi

# T7 — enrol.php returns 409 on re-enrolment (key must never be overwritten)
if grep -q '409' "$ENROL" 2>/dev/null; then
    check 7 "enrol.php returns 409 on re-enrolment of existing device_token" pass
else
    check 7 "enrol.php returns 409 on re-enrolment of existing device_token" fail
fi

# T8 — enrol.php does NOT use ON DUPLICATE KEY UPDATE (no blind UPSERT)
if [ -f "$ENROL" ] && ! grep -q 'ON DUPLICATE KEY' "$ENROL" 2>/dev/null; then
    check 8 "NEGATIVE: enrol.php does not use ON DUPLICATE KEY UPDATE" pass
else
    check 8 "NEGATIVE: enrol.php does not use ON DUPLICATE KEY UPDATE" fail
fi

# T9 — request-code.php checks already_registered before issuing a code
if grep -q 'already_registered' "$REQ_CODE" 2>/dev/null; then
    check 9 "request-code.php checks already_registered (D4: one account per device)" pass
else
    check 9 "request-code.php checks already_registered (D4: one account per device)" fail
fi

# T10 — plugin registers all three REST routes
ALL_ROUTES=true
for route in 'amboat-device/v1' 'enrol' 'status' 'request-code'; do
    if ! grep -q "$route" "$PLUGIN" 2>/dev/null; then
        ALL_ROUTES=false
        break
    fi
done
[ "$ALL_ROUTES" = "true" ] && check 10 "plugin registers amboat-device/v1 with enrol/status/request-code routes" pass \
                           || check 10 "plugin registers amboat-device/v1 with enrol/status/request-code routes" fail

# T11 — plugin uses register_rest_route (WordPress REST API, not direct PHP)
if grep -q 'register_rest_route' "$PLUGIN" 2>/dev/null; then
    check 11 "plugin uses register_rest_route (WordPress REST API)" pass
else
    check 11 "plugin uses register_rest_route (WordPress REST API)" fail
fi

# T12 — plugin uses dbDelta for table creation (WordPress-safe schema management)
if grep -q 'dbDelta' "$PLUGIN" 2>/dev/null; then
    check 12 "plugin uses dbDelta for table creation" pass
else
    check 12 "plugin uses dbDelta for table creation" fail
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
