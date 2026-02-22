#!/bin/bash
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

# restore.sh - Restore d3kOS configuration and data from backup
# Part of d3kOS Distribution Preparation
# Session-Dist-2
#
# Restores from backup created by backup.sh
# PRESERVES installation_id by default

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

# Check arguments
if [ $# -lt 1 ]; then
    error "Usage: $0 <backup-file.tar.gz> [--preserve-id]"
    error ""
    error "Options:"
    error "  --preserve-id    Keep current installation_id (default: true)"
    error "  --replace-id     Replace installation_id with backup's ID"
    exit 1
fi

BACKUP_FILE="$1"
PRESERVE_ID="true"

# Parse options
if [ "$2" == "--replace-id" ]; then
    PRESERVE_ID="false"
fi

log "=========================================="
log "d3kOS Restore Starting..."
log "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
    exit 1
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

log "Backup file: $BACKUP_FILE"
log "Preserve installation_id: $PRESERVE_ID"

# Save current installation_id if preserving
CURRENT_INSTALLATION_ID=""
if [ "$PRESERVE_ID" == "true" ] && [ -f "/opt/d3kos/config/license.json" ]; then
    CURRENT_INSTALLATION_ID=$(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo "")
    if [ -n "$CURRENT_INSTALLATION_ID" ]; then
        log "Current installation_id: $CURRENT_INSTALLATION_ID"
        log "  This ID will be preserved after restore"
    fi
fi

# Create temporary extraction directory
TEMP_DIR=$(mktemp -d)
log "Extracting backup to: $TEMP_DIR"

# Extract backup
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the backup directory (handle different archive structures)
BACKUP_DIR=$(find "$TEMP_DIR" -maxdepth 2 -type d -name "d3kos-backup" | head -1)

if [ -z "$BACKUP_DIR" ]; then
    error "Invalid backup archive (d3kos-backup directory not found)"
    rm -rf "$TEMP_DIR"
    exit 1
fi

log "Backup directory found: $BACKUP_DIR"

# Show backup info if available
if [ -f "$BACKUP_DIR/backup-info.json" ]; then
    log ""
    log "Backup information:"
    log "  Date: $(jq -r '.backup_date' "$BACKUP_DIR/backup-info.json" 2>/dev/null || echo 'unknown')"
    log "  Version: $(jq -r '.version' "$BACKUP_DIR/backup-info.json" 2>/dev/null || echo 'unknown')"
    log "  Installation ID: $(jq -r '.installation_id' "$BACKUP_DIR/backup-info.json" 2>/dev/null || echo 'unknown')"
    log "  Files: $(jq -r '.file_count' "$BACKUP_DIR/backup-info.json" 2>/dev/null || echo 'unknown')"
fi

# ==============================================================================
# Confirm restore
# ==============================================================================

log ""
warn "This will overwrite current configuration and data!"
warn "Press Ctrl+C to cancel, or Enter to continue..."
read -r

# ==============================================================================
# Restore files
# ==============================================================================

log ""
log "Restoring files..."

# 1. Configuration
if [ -d "$BACKUP_DIR/config" ]; then
    log "  [1/6] Restoring configuration..."
    mkdir -p /opt/d3kos/config
    cp -rp "$BACKUP_DIR/config/"* /opt/d3kos/config/ 2>/dev/null || warn "  Some config files could not be restored"
    chown -R d3kos:d3kos /opt/d3kos/config/
else
    warn "  No config directory in backup"
fi

# 2. Data
if [ -d "$BACKUP_DIR/data" ]; then
    log "  [2/6] Restoring data files..."
    mkdir -p /opt/d3kos/data
    cp -rp "$BACKUP_DIR/data/"* /opt/d3kos/data/ 2>/dev/null || warn "  Some data files could not be restored"
    chown -R d3kos:d3kos /opt/d3kos/data/
else
    warn "  No data directory in backup"
fi

# 3. Signal K
if [ -d "$BACKUP_DIR/signalk" ]; then
    log "  [3/6] Restoring Signal K configuration..."
    mkdir -p /home/d3kos/.signalk
    cp -rp "$BACKUP_DIR/signalk/"* /home/d3kos/.signalk/ 2>/dev/null || warn "  Some Signal K files could not be restored"
    chown -R d3kos:d3kos /home/d3kos/.signalk/
else
    warn "  No Signal K config in backup"
fi

# 4. Node-RED
if [ -d "$BACKUP_DIR/node-red" ]; then
    log "  [4/6] Restoring Node-RED flows..."
    mkdir -p /home/d3kos/.node-red
    cp -rp "$BACKUP_DIR/node-red/"* /home/d3kos/.node-red/ 2>/dev/null || warn "  Some Node-RED files could not be restored"
    chown -R d3kos:d3kos /home/d3kos/.node-red/
else
    warn "  No Node-RED flows in backup"
fi

# 5. Onboarding state
if [ -d "$BACKUP_DIR/state" ]; then
    log "  [5/6] Restoring onboarding state..."
    mkdir -p /opt/d3kos/state
    cp -rp "$BACKUP_DIR/state/"* /opt/d3kos/state/ 2>/dev/null || warn "  Some state files could not be restored"
    chown -R d3kos:d3kos /opt/d3kos/state/
else
    log "  No onboarding state in backup"
fi

# 6. Nginx
if [ -d "$BACKUP_DIR/nginx" ]; then
    log "  [6/6] Restoring nginx configuration..."
    cp -rp "$BACKUP_DIR/nginx/default" /etc/nginx/sites-enabled/default 2>/dev/null || warn "  Nginx config could not be restored"
else
    warn "  No nginx config in backup"
fi

# ==============================================================================
# Restore or preserve installation_id
# ==============================================================================

log ""
if [ "$PRESERVE_ID" == "true" ] && [ -n "$CURRENT_INSTALLATION_ID" ]; then
    log "Preserving current installation_id..."

    if [ -f "/opt/d3kos/config/license.json" ]; then
        # Update license.json with preserved ID
        jq --arg id "$CURRENT_INSTALLATION_ID" '.installation_id = $id' \
           /opt/d3kos/config/license.json > /tmp/license.json.tmp
        mv /tmp/license.json.tmp /opt/d3kos/config/license.json
        chown d3kos:d3kos /opt/d3kos/config/license.json
        chmod 644 /opt/d3kos/config/license.json

        log "  Installation ID preserved: $CURRENT_INSTALLATION_ID"
    fi
else
    log "Using installation_id from backup"
    RESTORED_ID=$(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo "unknown")
    log "  Installation ID: $RESTORED_ID"
fi

# ==============================================================================
# Clean up
# ==============================================================================

log ""
log "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# ==============================================================================
# Restart services
# ==============================================================================

log ""
log "Restarting services..."

# Restart Signal K
if systemctl is-active --quiet signalk; then
    log "  Restarting Signal K..."
    systemctl restart signalk || warn "  Could not restart signalk"
fi

# Restart Node-RED
if systemctl is-active --quiet nodered; then
    log "  Restarting Node-RED..."
    systemctl restart nodered || warn "  Could not restart nodered"
fi

# Restart nginx
if systemctl is-active --quiet nginx; then
    log "  Restarting nginx..."
    systemctl restart nginx || warn "  Could not restart nginx"
fi

# Restart d3kOS services
log "  Restarting d3kOS services..."
for service in d3kos-license-api d3kos-tier-manager d3kos-tier-api d3kos-export-manager; do
    if systemctl is-active --quiet "$service"; then
        systemctl restart "$service" 2>/dev/null || true
    fi
done

# ==============================================================================
# Summary
# ==============================================================================

log ""
log "=========================================="
log "Restore Complete!"
log "=========================================="
log "Installation ID: $(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo 'ERROR')"
log "Tier: $(jq -r '.tier' /opt/d3kos/config/license.json 2>/dev/null || echo '0')"
log ""
log "Services restarted. System ready to use."
log "=========================================="

exit 0
