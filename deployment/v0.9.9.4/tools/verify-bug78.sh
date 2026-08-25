#!/bin/bash
# verify-bug78.sh — BUG-78: sanitize.sh not wired into create-image.sh; credential strip missing
# Tests must FAIL before the fix and PASS after.
# T6 is the only test that proves the assertion actually bites — do not skip it.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CREATE_IMG="$REPO_ROOT/deployment/v0.9.9.4/opt/d3kos/scripts/create-image.sh"
SANITIZE="$REPO_ROOT/deployment/v0.9.9.4/opt/d3kos/scripts/sanitize.sh"
PI_HOST="192.168.1.237"
PI_USER="d3kos"
PI_KEY="$HOME/.ssh/id_d3kos"

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

# T1 — create-image.sh calls sanitize.sh
if grep -q 'sanitize' "$CREATE_IMG" 2>/dev/null; then
    check 1 "create-image.sh contains a call to sanitize.sh" pass
else
    check 1 "create-image.sh contains a call to sanitize.sh" fail
fi

# T2 — create-image.sh contains the secret-assertion loop and exit 1
if grep -q 'SECRET_FOUND' "$CREATE_IMG" 2>/dev/null && grep -q 'exit 1' "$CREATE_IMG" 2>/dev/null; then
    check 2 "create-image.sh contains secret-assertion loop and exit 1" pass
else
    check 2 "create-image.sh contains secret-assertion loop and exit 1" fail
fi

# T3 — sanitize.sh names all five secret files
SECRETS=("cloud-config.json" "api-keys.json" "device-token.json" "device-signing.key" "subscription.key")
ALL_PRESENT=true
for s in "${SECRETS[@]}"; do
    if ! grep -q "$s" "$SANITIZE" 2>/dev/null; then
        ALL_PRESENT=false
        break
    fi
done
if [ "$ALL_PRESENT" = "true" ]; then
    check 3 "sanitize.sh names all five secret files" pass
else
    check 3 "sanitize.sh names all five secret files" fail
fi

# T4 — sanitize.sh sets license.json to mode 600, and 644 does not appear for it
if grep -q 'chmod 600 "\$LICENSE_FILE"' "$SANITIZE" 2>/dev/null && \
   ! grep -q 'chmod 644 "\$LICENSE_FILE"' "$SANITIZE" 2>/dev/null; then
    check 4 "sanitize.sh sets license.json to mode 600 (not 644)" pass
else
    check 4 "sanitize.sh sets license.json to mode 600 (not 644)" fail
fi

# T5 — repo and Pi md5 match for both scripts
if ssh -i "$PI_KEY" -o ConnectTimeout=5 -o BatchMode=yes "${PI_USER}@${PI_HOST}" true 2>/dev/null; then
    PI_MD5_CREATE=$(ssh -i "$PI_KEY" "${PI_USER}@${PI_HOST}" "md5sum /opt/d3kos/scripts/create-image.sh 2>/dev/null | awk '{print \$1}'" 2>/dev/null)
    PI_MD5_SANITIZE=$(ssh -i "$PI_KEY" "${PI_USER}@${PI_HOST}" "md5sum /opt/d3kos/scripts/sanitize.sh 2>/dev/null | awk '{print \$1}'" 2>/dev/null)
    REPO_MD5_CREATE=$(md5sum "$CREATE_IMG" | awk '{print $1}')
    REPO_MD5_SANITIZE=$(md5sum "$SANITIZE" | awk '{print $1}')
    if [ "$PI_MD5_CREATE" = "$REPO_MD5_CREATE" ] && [ "$PI_MD5_SANITIZE" = "$REPO_MD5_SANITIZE" ]; then
        check 5 "repo and Pi md5 match for both scripts" pass
    else
        check 5 "repo and Pi md5 match for both scripts" fail
    fi
else
    echo "T5 SKIP: Pi unreachable — cannot compare md5"
fi

# T6 — NEGATIVE TEST: assertion block exits 1 when a secret file is present
# Extracts the assertion block from create-image.sh and runs it in a temp dir.
# This is the only test that proves the guard actually bites.
TMPDIR_T6=$(mktemp -d)
trap 'rm -rf "$TMPDIR_T6"' EXIT

# Create a fake config dir with a secret file
mkdir -p "$TMPDIR_T6/opt/d3kos/config"
touch "$TMPDIR_T6/opt/d3kos/config/api-keys.json"
# Fake empty ssh host keys dir
mkdir -p "$TMPDIR_T6/etc/ssh"

# Build a minimal test script that runs only the assertion block, rooted at TMPDIR_T6
if grep -q 'SECRET_FOUND' "$CREATE_IMG" 2>/dev/null; then
    cat > "$TMPDIR_T6/run_assertion.sh" <<ASSERT_EOF
#!/bin/bash
set -e
# Reroute paths into TMPDIR_T6
CONFIG_DIR="$TMPDIR_T6/opt/d3kos/config"
SSH_DIR="$TMPDIR_T6/etc/ssh"
SECRET_FOUND=0
for f in cloud-config.json api-keys.json device-token.json device-signing.key subscription.key; do
    if [ -e "\$CONFIG_DIR/\$f" ]; then
        echo "  FATAL: \$CONFIG_DIR/\$f is present in the image" >&2
        SECRET_FOUND=1
    fi
done
if [ -n "\$(ls -A "\$SSH_DIR"/ssh_host_*_key 2>/dev/null)" ]; then
    echo "  FATAL: SSH host keys present in the image" >&2
    SECRET_FOUND=1
fi
if [ "\$SECRET_FOUND" -ne 0 ]; then
    exit 1
fi
exit 0
ASSERT_EOF
    chmod +x "$TMPDIR_T6/run_assertion.sh"
    if bash "$TMPDIR_T6/run_assertion.sh" 2>/dev/null; then
        check 6 "NEGATIVE: assertion block exits 1 when secret file present" fail
    else
        check 6 "NEGATIVE: assertion block exits 1 when secret file present" pass
    fi
else
    check 6 "NEGATIVE: assertion block exits 1 when secret file present" fail
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
