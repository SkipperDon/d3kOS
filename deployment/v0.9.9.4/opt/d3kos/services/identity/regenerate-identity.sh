#!/bin/bash
# d3kOS first-boot identity regeneration (BUG-39)
# Runs ONCE on a freshly cloned SD card to give it its own identity.
# NEVER RUN MANUALLY on the master system.

set -u

LOG_FILE="/var/log/d3kos-identity-regen.log"

log_action() {
    local msg="$1"
    echo "$(date -Iseconds) $msg" | tee -a "$LOG_FILE"
}

# Sentinel FIRST: if already regenerated, exit immediately
if [[ -f /opt/d3kos/config/.identity-regenerated ]]; then
    log_action "identity already regenerated, nothing to do"
    exit 0
fi

# Require root
if [[ $EUID -ne 0 ]]; then
    log_action "ERROR: must be run as root"
    exit 1
fi

log_action "=== Starting d3kOS identity regeneration ==="

# 1. Regenerate machine-id
log_action "Regenerating /etc/machine-id"
if [[ -f /etc/machine-id ]]; then
    OLD_MACHINE_ID=$(cat /etc/machine-id)
    log_action "  Old machine-id: $OLD_MACHINE_ID"
fi

systemd-machine-id-setup --print | tee /etc/machine-id >/dev/null 2>&1 || {
    log_action "WARNING: systemd-machine-id-setup failed, trying direct generation"
    cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id
}

NEW_MACHINE_ID=$(cat /etc/machine-id)
log_action "  New machine-id: $NEW_MACHINE_ID"

# Also regenerate /var/lib/dbus/machine-id if it exists
if [[ -f /var/lib/dbus/machine-id ]]; then
    log_action "Regenerating /var/lib/dbus/machine-id"
    cp /etc/machine-id /var/lib/dbus/machine-id
    log_action "  Copied from /etc/machine-id"
fi

# 2. Regenerate SSH host keys
log_action "Regenerating SSH host keys"

SSH_KEYS=(
    "/etc/ssh/ssh_host_rsa_key"
    "/etc/ssh/ssh_host_ecdsa_key"
    "/etc/ssh/ssh_host_ed25519_key"
)

SSH_REGEN_FAILED=0

for key_path in "${SSH_KEYS[@]}"; do
    if [[ -f "$key_path" ]]; then
        KEY_TYPE=""
        if [[ "$key_path" == *"rsa"* ]]; then
            KEY_TYPE="rsa"
        elif [[ "$key_path" == *"ecdsa"* ]]; then
            KEY_TYPE="ecdsa"
        elif [[ "$key_path" == *"ed25519"* ]]; then
            KEY_TYPE="ed25519"
        fi

        log_action "  Regenerating $key_path"
        # Read fingerprints of old key
        if [[ -f "${key_path}.pub" ]]; then
            OLD_FP=$(ssh-keygen -l -f "${key_path}.pub" 2>/dev/null || echo "N/A")
            log_action "    Old fingerprint: $OLD_FP"
        fi

        # Generate new key to a TEMPORARY path first
        TEMP_KEY="${key_path}.tmp"
        ssh-keygen -t "$KEY_TYPE" -f "$TEMP_KEY" -N "" -C "d3kOS key generated on $(date -Iseconds)" 2>/dev/null || {
            log_action "WARNING: ssh-keygen failed for $KEY_TYPE"
            SSH_REGEN_FAILED=1
            continue
        }

        # Verify the new key and .pub exist and are non-empty
        if [[ -f "$TEMP_KEY" ]] && [[ -s "$TEMP_KEY" ]] && [[ -f "${TEMP_KEY}.pub" ]] && [[ -s "${TEMP_KEY}.pub" ]]; then
            # Only delete and replace after verification
            rm -f "$key_path" "${key_path}.pub"
            mv "$TEMP_KEY" "$key_path"
            mv "${TEMP_KEY}.pub" "${key_path}.pub"

            # Read fingerprint of new key
            NEW_FP=$(ssh-keygen -l -f "${key_path}.pub" 2>/dev/null || echo "N/A")
            log_action "    New fingerprint: $NEW_FP"
        else
            log_action "WARNING: New $KEY_TYPE key failed verification, keeping original"
            rm -f "$TEMP_KEY" "${TEMP_KEY}.pub"
            SSH_REGEN_FAILED=1
        fi
    fi
done

# 3. Regenerate device-token.json
log_action "Regenerating device-token.json"
TOKEN_FILE="/opt/d3kos/config/device-token.json"

if [[ -f "$TOKEN_FILE" ]]; then
    OLD_TOKEN=$(python3 -c "import json; print(json.load(open('$TOKEN_FILE')).get('device_token', 'N/A'))" 2>/dev/null || echo "N/A")
    log_action "  Old device_token: $OLD_TOKEN"

    # Back up before rewriting
    cp "$TOKEN_FILE" "${TOKEN_FILE}.pre-regen"
    log_action "  Backup created: ${TOKEN_FILE}.pre-regen"
fi

# Generate new UUID4 from kernel source
NEW_TOKEN=$(cat /proc/sys/kernel/random/uuid)
CREATED_AT=$(python3 -c "from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))")

log_action "  New device_token: $NEW_TOKEN"
log_action "  New created_at: $CREATED_AT"

# Write new device-token.json with python3 to ensure valid JSON
python3 << EOF
import json
from pathlib import Path

token_file = Path('$TOKEN_FILE')
new_data = {
    'device_token': '$NEW_TOKEN',
    'created_at': '$CREATED_AT'
}

# Preserve file mode if it existed
mode = None
if token_file.exists():
    mode = token_file.stat().st_mode & 0o777

token_file.write_text(json.dumps(new_data) + '\n')

# Restore file mode
if mode:
    token_file.chmod(mode)

print("device-token.json written successfully")
EOF

# NEVER write license.json
log_action "Checking license.json (read-only)"
if [[ -f /opt/d3kos/config/license.json ]]; then
    INST_ID=$(python3 -c "import json; print(json.load(open('/opt/d3kos/config/license.json')).get('installation_id', 'N/A'))" 2>/dev/null || echo "N/A")
    log_action "  Current installation_id: $INST_ID (preserved)"
else
    log_action "  license.json not found (expected on first install)"
fi

# 4. Generate Ed25519 device signing keypair (BUG-66 Phase B)
# Key is generated on EVERY fresh clone — never baked into the shipped image (BUG-78).
# Private key is 32 bytes raw, mode 0600, owner root. Never logged.
# Public key is written separately for the enrolment call (device_sign.get_public_key_b64()).
log_action "Generating Ed25519 device signing keypair"
SIGNING_KEY_FAILED=0
SIGNING_KEY_PATH="/opt/d3kos/config/device-signing.key"
SIGNING_PUB_PATH="/opt/d3kos/config/device-signing.pub"

if ! python3 -c "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey" 2>/dev/null; then
    log_action "ERROR: Python 'cryptography' package not available — cannot generate signing keypair"
    SIGNING_KEY_FAILED=1
else
    python3 << 'PYEOF'
import os, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

priv_path = '/opt/d3kos/config/device-signing.key'
pub_path  = '/opt/d3kos/config/device-signing.pub'

try:
    key     = Ed25519PrivateKey.generate()
    priv_raw = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    pub_raw  = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

    # Mode 0600 set at open time — private key is never world-readable, even briefly.
    fd = os.open(priv_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(priv_raw)

    # Public key is not secret; 0644 for readability by unprivileged services.
    with open(pub_path, 'wb') as f:
        f.write(pub_raw)
    os.chmod(pub_path, 0o644)

    priv_len = len(priv_raw)
    pub_len  = len(pub_raw)
    print(f"device-signing.key: {priv_len} bytes, mode 0600")
    print(f"device-signing.pub: {pub_len} bytes, mode 0644")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
    if [[ $? -ne 0 ]]; then
        log_action "ERROR: Ed25519 keypair generation failed"
        SIGNING_KEY_FAILED=1
    else
        log_action "  device-signing.key written (32 bytes, mode 0600)"
        log_action "  device-signing.pub written (32 bytes, mode 0644)"
    fi
fi

# Create sentinel LAST, only if all steps succeeded
if [[ $SSH_REGEN_FAILED -ne 0 ]] || [[ $SIGNING_KEY_FAILED -ne 0 ]]; then
    log_action "ERROR: one or more steps failed, NOT creating sentinel (re-run to retry)"
    exit 1
fi

log_action "Creating identity regeneration sentinel"
mkdir -p /opt/d3kos/config
touch /opt/d3kos/config/.identity-regenerated
log_action "=== Identity regeneration complete ==="
