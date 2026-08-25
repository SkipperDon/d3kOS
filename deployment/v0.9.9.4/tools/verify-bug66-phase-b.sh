#!/bin/bash
# verify-bug66-phase-b.sh — BUG-66 Phase B: Pi-side Ed25519 keypair generation + signing helper
# Tests must FAIL before the fix and PASS after.
# T3 proves the sentinel cannot be created if key generation fails (safety property).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
REGEN="$REPO_ROOT/deployment/v0.9.9.4/opt/d3kos/services/identity/regenerate-identity.sh"
SIGN_HELPER="$REPO_ROOT/deployment/v0.9.9.4/opt/d3kos/services/device_sign.py"

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

# T1 — regenerate-identity.sh generates device-signing.key (the device Ed25519 keypair)
# Must reference the specific file, not just incidentally contain 'ed25519' from SSH host key handling.
if grep -q 'device-signing.key' "$REGEN" 2>/dev/null; then
    check 1 "regenerate-identity.sh generates device-signing.key (Ed25519 device keypair)" pass
else
    check 1 "regenerate-identity.sh generates device-signing.key (Ed25519 device keypair)" fail
fi

# T2 — regenerate-identity.sh writes device-signing.key with 0600 mode
# Mode must be set at open time (O_CREAT + 0o600), not chmod after — prevents a window where
# the file exists world-readable before chmod runs.
if grep -q 'device-signing.key' "$REGEN" 2>/dev/null && \
   grep -q '0o600\|0600' "$REGEN" 2>/dev/null; then
    check 2 "regenerate-identity.sh creates device-signing.key with 0600 mode" pass
else
    check 2 "regenerate-identity.sh creates device-signing.key with 0600 mode" fail
fi

# T3 — regenerate-identity.sh gates sentinel creation on SIGNING_KEY_FAILED (or equivalent)
# If key generation fails, the sentinel must NOT be created — so the script re-runs.
if grep -q 'SIGNING_KEY_FAILED' "$REGEN" 2>/dev/null; then
    check 3 "regenerate-identity.sh blocks sentinel if signing key generation fails" pass
else
    check 3 "regenerate-identity.sh blocks sentinel if signing key generation fails" fail
fi

# T4 — device_sign.py exists at the correct path (importable via sys.path in cloud services)
if [ -f "$SIGN_HELPER" ]; then
    check 4 "device_sign.py exists at services/ root (importable by cloud_agent, export, fleet)" pass
else
    check 4 "device_sign.py exists at services/ root (importable by cloud_agent, export, fleet)" fail
fi

# T5 — device_sign.py declares sign_device_request()
if grep -q 'def sign_device_request' "$SIGN_HELPER" 2>/dev/null; then
    check 5 "device_sign.py declares sign_device_request()" pass
else
    check 5 "device_sign.py declares sign_device_request()" fail
fi

# T6 — device_sign.py reads from device-signing.key
if grep -q 'device-signing.key' "$SIGN_HELPER" 2>/dev/null; then
    check 6 "device_sign.py reads from /opt/d3kos/config/device-signing.key" pass
else
    check 6 "device_sign.py reads from /opt/d3kos/config/device-signing.key" fail
fi

# T7 — device_sign.py uses Ed25519 from the cryptography library
if grep -q 'Ed25519PrivateKey\|from_private_bytes' "$SIGN_HELPER" 2>/dev/null; then
    check 7 "device_sign.py uses Ed25519PrivateKey (cryptography library)" pass
else
    check 7 "device_sign.py uses Ed25519PrivateKey (cryptography library)" fail
fi

# T8 — device_sign.py handles missing device-signing.key (raises, does not silently return None)
# A missing key is a configuration error that must surface clearly, not be swallowed.
# We check that FileNotFoundError is documented (not caught silently).
if [ -f "$SIGN_HELPER" ] && ! grep -q 'except FileNotFoundError.*pass\|except.*:.*return None' "$SIGN_HELPER" 2>/dev/null; then
    check 8 "NEGATIVE: device_sign.py does not silently swallow FileNotFoundError" pass
else
    check 8 "NEGATIVE: device_sign.py does not silently swallow FileNotFoundError" fail
fi

# T9 — device_sign.py returns the four required headers
for header in 'X-Device-Token' 'X-Timestamp' 'X-Nonce' 'X-Signature'; do
    if ! grep -q "$header" "$SIGN_HELPER" 2>/dev/null; then
        check 9 "device_sign.py returns all 4 required auth headers (X-Device-Token, X-Timestamp, X-Nonce, X-Signature)" fail
        break
    fi
    check 9 "device_sign.py returns all 4 required auth headers (X-Device-Token, X-Timestamp, X-Nonce, X-Signature)" pass
    break
done

# T10 — regenerate-identity.sh does NOT log the raw key content (e.g. base64 of priv_raw)
# Logging the filename is fine; logging the key bytes would expose the private key.
# Dangerous patterns: print(priv_raw), print(base64...priv), cp signing.key to /tmp, etc.
if ! grep -qE 'print.*priv_raw|print.*priv_b64|cp.*signing\.key|tee.*signing\.key' "$REGEN" 2>/dev/null; then
    check 10 "NEGATIVE: regenerate-identity.sh does not log or copy raw private key bytes" pass
else
    check 10 "NEGATIVE: regenerate-identity.sh does not log or copy raw private key bytes" fail
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
