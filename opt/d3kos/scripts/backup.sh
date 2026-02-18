#!/bin/bash
# backup.sh - Backup d3kOS configuration and data
# Part of d3kOS Distribution Preparation
# Session-Dist-2
#
# Creates timestamped backup of:
# - /opt/d3kos/config/
# - /opt/d3kos/data/
# - /home/d3kos/.signalk/
# - /home/d3kos/.node-red/flows.json

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Configuration
BACKUP_DIR="${1:-/opt/d3kos/data/backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="d3kos-backup-${TIMESTAMP}.tar.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

log "=========================================="
log "d3kOS Backup Starting..."
log "=========================================="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Temporary directory for staging
TEMP_DIR=$(mktemp -d)
STAGING_DIR="${TEMP_DIR}/d3kos-backup"
mkdir -p "$STAGING_DIR"

log "Backup destination: $BACKUP_PATH"
log "Staging directory: $STAGING_DIR"

# ==============================================================================
# Collect files to backup
# ==============================================================================

log ""
log "Collecting files to backup..."

# 1. Configuration files
log "  [1/6] Configuration files (/opt/d3kos/config/)..."
if [ -d "/opt/d3kos/config" ]; then
    mkdir -p "${STAGING_DIR}/config"
    cp -rp /opt/d3kos/config/* "${STAGING_DIR}/config/" 2>/dev/null || warn "  Some config files could not be copied"
    FILE_COUNT=$(find "${STAGING_DIR}/config/" -type f | wc -l)
    log "    Copied $FILE_COUNT files"
else
    warn "  /opt/d3kos/config/ not found"
fi

# 2. Data files (excluding large media files)
log "  [2/6] Data files (/opt/d3kos/data/)..."
if [ -d "/opt/d3kos/data" ]; then
    mkdir -p "${STAGING_DIR}/data"

    # Copy databases and JSON files
    find /opt/d3kos/data/ -type f \( -name "*.db" -o -name "*.json" \) -exec cp -p {} "${STAGING_DIR}/data/" \; 2>/dev/null || true

    # Copy exports
    if [ -d "/opt/d3kos/data/exports" ]; then
        mkdir -p "${STAGING_DIR}/data/exports"
        cp -rp /opt/d3kos/data/exports/*.json "${STAGING_DIR}/data/exports/" 2>/dev/null || true
    fi

    FILE_COUNT=$(find "${STAGING_DIR}/data/" -type f | wc -l)
    log "    Copied $FILE_COUNT files (databases and JSON only)"
else
    warn "  /opt/d3kos/data/ not found"
fi

# 3. Signal K configuration
log "  [3/6] Signal K configuration..."
if [ -d "/home/d3kos/.signalk" ]; then
    mkdir -p "${STAGING_DIR}/signalk"

    # Copy settings
    [ -f "/home/d3kos/.signalk/settings.json" ] && cp -p /home/d3kos/.signalk/settings.json "${STAGING_DIR}/signalk/"

    # Copy plugin configs
    if [ -d "/home/d3kos/.signalk/plugin-config-data" ]; then
        cp -rp /home/d3kos/.signalk/plugin-config-data "${STAGING_DIR}/signalk/"
    fi

    FILE_COUNT=$(find "${STAGING_DIR}/signalk/" -type f | wc -l)
    log "    Copied $FILE_COUNT files"
else
    warn "  /home/d3kos/.signalk/ not found"
fi

# 4. Node-RED flows
log "  [4/6] Node-RED flows..."
if [ -f "/home/d3kos/.node-red/flows.json" ]; then
    mkdir -p "${STAGING_DIR}/node-red"
    cp -p /home/d3kos/.node-red/flows.json "${STAGING_DIR}/node-red/"
    [ -f "/home/d3kos/.node-red/settings.js" ] && cp -p /home/d3kos/.node-red/settings.js "${STAGING_DIR}/node-red/"
    log "    Copied Node-RED flows and settings"
else
    warn "  Node-RED flows not found"
fi

# 5. Onboarding configuration (if exists)
log "  [5/6] Onboarding configuration..."
if [ -f "/opt/d3kos/state/onboarding-config.json" ]; then
    mkdir -p "${STAGING_DIR}/state"
    cp -p /opt/d3kos/state/onboarding-config.json "${STAGING_DIR}/state/"
    log "    Copied onboarding config"
else
    log "    No onboarding config (system not initialized)"
fi

# 6. Nginx configuration
log "  [6/6] Nginx configuration..."
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    mkdir -p "${STAGING_DIR}/nginx"
    cp -p /etc/nginx/sites-enabled/default "${STAGING_DIR}/nginx/"
    log "    Copied nginx config"
fi

# ==============================================================================
# Create backup metadata
# ==============================================================================

log ""
log "Creating backup metadata..."

cat > "${STAGING_DIR}/backup-info.json" <<EOF
{
  "backup_date": "$(date -Iseconds)",
  "backup_timestamp": "$TIMESTAMP",
  "installation_id": "$(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo 'unknown')",
  "tier": $(jq -r '.tier' /opt/d3kos/config/license.json 2>/dev/null || echo '0'),
  "version": "$(cat /opt/d3kos/VERSION 2>/dev/null || echo '1.0.3')",
  "hostname": "$(hostname)",
  "backup_size_bytes": 0,
  "file_count": 0
}
EOF

# ==============================================================================
# Create tar.gz archive
# ==============================================================================

log ""
log "Creating compressed archive..."

cd "$TEMP_DIR"
tar -czf "$BACKUP_PATH" d3kos-backup/

# Calculate size
BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
FILE_COUNT=$(tar -tzf "$BACKUP_PATH" | wc -l)

log "  Archive created: $BACKUP_PATH"
log "  Size: $BACKUP_SIZE"
log "  Files: $FILE_COUNT"

# Update metadata with actual size
jq --arg size "$BACKUP_SIZE" --arg count "$FILE_COUNT" \
   '.backup_size_bytes = $size | .file_count = ($count|tonumber)' \
   "${STAGING_DIR}/backup-info.json" > /tmp/backup-info.json.tmp 2>/dev/null || true

# Clean up
rm -rf "$TEMP_DIR"

# Set permissions
chown d3kos:d3kos "$BACKUP_PATH"
chmod 644 "$BACKUP_PATH"

# ==============================================================================
# Summary
# ==============================================================================

log ""
log "=========================================="
log "Backup Complete!"
log "=========================================="
log "Backup file: $BACKUP_PATH"
log "Size: $BACKUP_SIZE"
log "Files: $FILE_COUNT"
log ""
log "To restore this backup:"
log "  sudo /opt/d3kos/scripts/restore.sh $BACKUP_PATH"
log "=========================================="

exit 0
