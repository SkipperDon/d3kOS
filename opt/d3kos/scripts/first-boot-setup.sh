#!/bin/bash
# first-boot-setup.sh - First boot initialization for d3kOS
# Part of d3kOS Distribution Preparation
# Session-Dist-2
#
# This script runs once on first boot to:
# 1. Expand filesystem to full SD card
# 2. Generate unique installation ID
# 3. Create license.json (Tier 0)
# 4. Detect timezone
# 5. Initialize directories
# 6. Mark first boot as complete

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="/var/log/d3kos-first-boot.log"

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "d3kOS First Boot Setup Starting..."
log "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root"
    exit 1
fi

# Check if first boot marker exists
FIRST_BOOT_MARKER="/opt/d3kos/.first-boot-complete"

if [ -f "$FIRST_BOOT_MARKER" ]; then
    log "First boot already completed (marker exists)"
    log "Marker: $FIRST_BOOT_MARKER"
    exit 0
fi

log "First boot detected - running initialization..."

# ==============================================================================
# STEP 1: Expand filesystem
# ==============================================================================

log ""
log "STEP 1: Expanding filesystem to full SD card size..."

if command -v raspi-config &>/dev/null; then
    log "  Using raspi-config to expand filesystem..."
    raspi-config nonint do_expand_rootfs
    log "  Filesystem expansion scheduled (will complete after reboot)"
else
    warn "  raspi-config not found, trying manual expansion..."

    # Get root partition
    ROOT_PART=$(findmnt -n -o SOURCE /)
    ROOT_DEV=$(lsblk -no pkname "$ROOT_PART")

    if [ -z "$ROOT_DEV" ]; then
        warn "  Could not detect root device, skipping filesystem expansion"
    else
        log "  Root partition: $ROOT_PART"
        log "  Root device: /dev/$ROOT_DEV"

        # Resize partition
        if command -v parted &>/dev/null; then
            log "  Resizing partition with parted..."
            parted "/dev/$ROOT_DEV" resizepart 2 100% || warn "  parted resize failed"
        fi

        # Resize filesystem
        if command -v resize2fs &>/dev/null; then
            log "  Resizing ext4 filesystem..."
            resize2fs "$ROOT_PART" || warn "  resize2fs failed"
        fi
    fi
fi

# ==============================================================================
# STEP 2: Generate installation ID
# ==============================================================================

log ""
log "STEP 2: Generating unique installation ID..."

if [ -f "/opt/d3kos/scripts/generate-installation-id.sh" ]; then
    log "  Running generate-installation-id.sh..."
    bash /opt/d3kos/scripts/generate-installation-id.sh

    # Verify license.json was created
    if [ -f "/opt/d3kos/config/license.json" ]; then
        INSTALLATION_ID=$(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo "ERROR")
        log "  Installation ID: $INSTALLATION_ID"
    else
        error "  license.json was not created!"
    fi
else
    error "  generate-installation-id.sh not found!"
    error "  Creating minimal license.json..."

    mkdir -p /opt/d3kos/config
    cat > /opt/d3kos/config/license.json <<EOF
{
  "installation_id": "$(uuidgen | tr -d '-' | head -c 16)",
  "tier": 0,
  "reset_count": 0,
  "max_resets": 10,
  "version": "1.0.3",
  "last_update_check": "$(date -Iseconds)",
  "features": {
    "voice_assistant": false,
    "camera": false,
    "unlimited_resets": false,
    "cloud_sync": false
  },
  "subscription_status": "none",
  "subscription_expires_at": null
}
EOF
    chown d3kos:d3kos /opt/d3kos/config/license.json
    chmod 644 /opt/d3kos/config/license.json
fi

# ==============================================================================
# STEP 3: Detect timezone
# ==============================================================================

log ""
log "STEP 3: Detecting timezone..."

if [ -f "/opt/d3kos/scripts/detect-timezone.sh" ]; then
    log "  Running detect-timezone.sh..."
    bash /opt/d3kos/scripts/detect-timezone.sh || warn "  Timezone detection failed"
else
    warn "  detect-timezone.sh not found, keeping default timezone"
    log "  Current timezone: $(timedatectl show -p Timezone --value 2>/dev/null || cat /etc/timezone)"
fi

# ==============================================================================
# STEP 4: Initialize directories
# ==============================================================================

log ""
log "STEP 4: Initializing d3kOS directories..."

DIRECTORIES=(
    "/opt/d3kos/config"
    "/opt/d3kos/data"
    "/opt/d3kos/data/exports"
    "/opt/d3kos/data/backups"
    "/opt/d3kos/data/marine-vision"
    "/opt/d3kos/data/boatlogs"
    "/opt/d3kos/logs"
    "/opt/d3kos/models"
    "/home/d3kos/camera-recordings"
    "/home/d3kos/camera-recordings/captures"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        log "  Creating: $dir"
        mkdir -p "$dir"
        chown d3kos:d3kos "$dir"
        chmod 755 "$dir"
    else
        log "  Exists: $dir"
    fi
done

# ==============================================================================
# STEP 5: Initialize databases
# ==============================================================================

log ""
log "STEP 5: Checking databases..."

# Marine Vision captures database
CAPTURES_DB="/opt/d3kos/data/marine-vision/captures.db"
if [ ! -f "$CAPTURES_DB" ]; then
    log "  Creating captures database..."
    touch "$CAPTURES_DB"
    chown d3kos:d3kos "$CAPTURES_DB"
    chmod 644 "$CAPTURES_DB"
fi

# Conversation history database
CONVERSATION_DB="/opt/d3kos/data/conversation-history.db"
if [ ! -f "$CONVERSATION_DB" ]; then
    log "  Creating conversation history database..."
    touch "$CONVERSATION_DB"
    chown d3kos:d3kos "$CONVERSATION_DB"
    chmod 644 "$CONVERSATION_DB"
fi

# ==============================================================================
# STEP 6: Set permissions
# ==============================================================================

log ""
log "STEP 6: Setting directory permissions..."

chown -R d3kos:d3kos /opt/d3kos/ 2>/dev/null || warn "Could not set ownership on /opt/d3kos/"
chown -R d3kos:d3kos /home/d3kos/ 2>/dev/null || warn "Could not set ownership on /home/d3kos/"

# ==============================================================================
# STEP 7: Mark first boot as complete
# ==============================================================================

log ""
log "STEP 7: Marking first boot as complete..."

mkdir -p "$(dirname "$FIRST_BOOT_MARKER")"
cat > "$FIRST_BOOT_MARKER" <<EOF
First boot completed: $(date -Iseconds)
Installation ID: $(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo "unknown")
Timezone: $(timedatectl show -p Timezone --value 2>/dev/null || cat /etc/timezone)
EOF

chown d3kos:d3kos "$FIRST_BOOT_MARKER"
log "  First boot marker created: $FIRST_BOOT_MARKER"

# ==============================================================================
# Summary
# ==============================================================================

log ""
log "=========================================="
log "First Boot Setup Complete!"
log "=========================================="
log "Installation ID: $(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo 'ERROR')"
log "Tier: $(jq -r '.tier' /opt/d3kos/config/license.json 2>/dev/null || echo '0')"
log "Timezone: $(timedatectl show -p Timezone --value 2>/dev/null || cat /etc/timezone)"
log "Log file: $LOG_FILE"
log ""
log "System ready for onboarding wizard."
log "Reboot recommended to complete filesystem expansion."
log "=========================================="

exit 0
