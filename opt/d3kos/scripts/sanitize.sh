#!/bin/bash
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

# sanitize.sh - Remove all user-specific data for d3kOS distribution
# Part of d3kOS Distribution Preparation
# Session-Dist-2
#
# WARNING: This script removes ALL user data and configuration!
# Use this to prepare a clean image for distribution.
#
# What gets removed:
# - All logs
# - Shell history
# - SSH keys
# - WiFi passwords
# - Browser cache/cookies
# - User-created boatlogs
# - Camera recordings
# - Installation ID (reset to blank)
# - Onboarding configuration
# - Signal K history
# - Node-RED credentials

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

log "=========================================="
log "d3kOS System Sanitization"
log "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
    exit 1
fi

# Safety confirmation
warn ""
warn "╔════════════════════════════════════════════════════════════╗"
warn "║                    ⚠️  WARNING  ⚠️                          ║"
warn "║                                                            ║"
warn "║  This will DELETE ALL USER DATA AND CONFIGURATION!        ║"
warn "║                                                            ║"
warn "║  - Installation ID will be reset                          ║"
warn "║  - All logs and history will be deleted                   ║"
warn "║  - SSH keys will be removed                               ║"
warn "║  - WiFi passwords will be cleared                         ║"
warn "║  - User data will be permanently erased                   ║"
warn "║                                                            ║"
warn "║  This is ONLY for creating distribution images!           ║"
warn "╚════════════════════════════════════════════════════════════╝"
warn ""
warn "Type 'SANITIZE' (in uppercase) to confirm: "
read -r CONFIRM

if [ "$CONFIRM" != "SANITIZE" ]; then
    error "Confirmation failed. Exiting."
    exit 1
fi

log "Confirmation received. Starting sanitization..."

# ==============================================================================
# STEP 1: Stop all d3kOS services
# ==============================================================================

log ""
log "STEP 1: Stopping d3kOS services..."

for service in $(systemctl list-units --type=service --state=running | grep d3kos | awk '{print $1}'); do
    log "  Stopping $service..."
    systemctl stop "$service" 2>/dev/null || true
done

# ==============================================================================
# STEP 2: Remove logs
# ==============================================================================

log ""
log "STEP 2: Removing logs..."

# d3kOS logs
if [ -d "/opt/d3kos/logs" ]; then
    log "  Removing /opt/d3kos/logs/*"
    rm -rf /opt/d3kos/logs/*
fi

# System logs
log "  Truncating system logs..."
journalctl --rotate 2>/dev/null || true
journalctl --vacuum-time=1s 2>/dev/null || true

# Nginx logs
if [ -d "/var/log/nginx" ]; then
    log "  Removing nginx logs..."
    rm -f /var/log/nginx/*.log*
fi

# Signal K logs
if [ -d "/home/d3kos/.signalk/logs" ]; then
    log "  Removing Signal K logs..."
    rm -rf /home/d3kos/.signalk/logs/*
fi

# ==============================================================================
# STEP 3: Remove shell history
# ==============================================================================

log ""
log "STEP 3: Removing shell history..."

for user_home in /root /home/*; do
    if [ -d "$user_home" ]; then
        log "  Removing history for: $user_home"
        rm -f "$user_home/.bash_history"
        rm -f "$user_home/.zsh_history"
        rm -f "$user_home/.history"
    fi
done

# ==============================================================================
# STEP 4: Remove SSH keys
# ==============================================================================

log ""
log "STEP 4: Removing SSH keys..."

for user_home in /root /home/*; do
    if [ -d "$user_home/.ssh" ]; then
        log "  Removing SSH keys: $user_home/.ssh/"
        rm -f "$user_home/.ssh/id_"*
        rm -f "$user_home/.ssh/known_hosts"
        rm -f "$user_home/.ssh/authorized_keys"
    fi
done

# Remove host keys (will be regenerated on first boot)
log "  Removing SSH host keys..."
rm -f /etc/ssh/ssh_host_*_key*

# ==============================================================================
# STEP 5: Remove WiFi passwords
# ==============================================================================

log ""
log "STEP 5: Removing WiFi passwords and connections..."

if [ -d "/etc/NetworkManager/system-connections" ]; then
    log "  Removing WiFi connection profiles (keeping d3kOS AP)..."

    # Keep only the d3kOS AP connection
    for connection in /etc/NetworkManager/system-connections/*.nmconnection; do
        if [ -f "$connection" ]; then
            conn_name=$(basename "$connection")
            if [[ "$conn_name" != "d3kos.nmconnection" ]] && [[ "$conn_name" != "Wired connection 1.nmconnection" ]]; then
                log "    Removing: $conn_name"
                rm -f "$connection"
            fi
        fi
    done
fi

# ==============================================================================
# STEP 6: Remove browser cache
# ==============================================================================

log ""
log "STEP 6: Removing browser cache and cookies..."

if [ -d "/home/d3kos/.config/chromium" ]; then
    log "  Removing Chromium cache..."
    rm -rf /home/d3kos/.config/chromium/Default/Cache
    rm -rf /home/d3kos/.config/chromium/Default/Cookies*
    rm -rf /home/d3kos/.config/chromium/Default/History*
    rm -rf /home/d3kos/.config/chromium/Default/Sessions
fi

# ==============================================================================
# STEP 7: Remove user data
# ==============================================================================

log ""
log "STEP 7: Removing user data..."

# Boatlogs
if [ -d "/opt/d3kos/data/boatlogs" ]; then
    log "  Removing boatlogs..."
    rm -rf /opt/d3kos/data/boatlogs/*
fi

# Camera recordings
if [ -d "/home/d3kos/camera-recordings" ]; then
    log "  Removing camera recordings..."
    rm -rf /home/d3kos/camera-recordings/*.mp4
    rm -rf /home/d3kos/camera-recordings/*.jpg
    rm -rf /home/d3kos/camera-recordings/captures/*
fi

# Marine vision captures database
if [ -f "/opt/d3kos/data/marine-vision/captures.db" ]; then
    log "  Removing marine vision captures database..."
    rm -f /opt/d3kos/data/marine-vision/captures.db
fi

# Conversation history
if [ -f "/opt/d3kos/data/conversation-history.db" ]; then
    log "  Removing AI conversation history..."
    rm -f /opt/d3kos/data/conversation-history.db
fi

# Exports
if [ -d "/opt/d3kos/data/exports" ]; then
    log "  Removing data exports..."
    rm -rf /opt/d3kos/data/exports/*
fi

# Backups
if [ -d "/opt/d3kos/data/backups" ]; then
    log "  Removing backups..."
    rm -rf /opt/d3kos/data/backups/*
fi

# ==============================================================================
# STEP 8: Reset license.json (clear installation ID)
# ==============================================================================

log ""
log "STEP 8: Resetting license.json..."

LICENSE_FILE="/opt/d3kos/config/license.json"

if [ -f "$LICENSE_FILE" ]; then
    log "  Clearing installation_id and resetting to Tier 0..."

    cat > "$LICENSE_FILE" <<'EOF'
{
  "installation_id": "",
  "tier": 0,
  "reset_count": 0,
  "max_resets": 10,
  "version": "1.0.3",
  "last_update_check": null,
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

    chown d3kos:d3kos "$LICENSE_FILE"
    chmod 644 "$LICENSE_FILE"
    log "  License file reset to defaults"
fi

# ==============================================================================
# STEP 9: Remove onboarding configuration
# ==============================================================================

log ""
log "STEP 9: Removing onboarding configuration..."

if [ -f "/opt/d3kos/state/onboarding-config.json" ]; then
    log "  Removing onboarding config..."
    rm -f /opt/d3kos/state/onboarding-config.json
fi

# Remove first-boot marker so setup runs again
if [ -f "/opt/d3kos/.first-boot-complete" ]; then
    log "  Removing first-boot marker..."
    rm -f /opt/d3kos/.first-boot-complete
fi

# ==============================================================================
# STEP 10: Clear Signal K data
# ==============================================================================

log ""
log "STEP 10: Clearing Signal K data..."

if [ -d "/home/d3kos/.signalk" ]; then
    # Keep settings.json structure but remove sensitive data
    if [ -f "/home/d3kos/.signalk/settings.json" ]; then
        log "  Resetting Signal K settings..."
        # Create minimal settings
        cat > /home/d3kos/.signalk/settings.json <<'EOF'
{
  "settings": {
    "loglevel": "warn"
  },
  "pipedProviders": []
}
EOF
        chown d3kos:d3kos /home/d3kos/.signalk/settings.json
    fi

    # Remove security config
    if [ -f "/home/d3kos/.signalk/security.json" ]; then
        log "  Removing Signal K security config..."
        rm -f /home/d3kos/.signalk/security.json
    fi
fi

# ==============================================================================
# STEP 11: Clear Node-RED credentials
# ==============================================================================

log ""
log "STEP 11: Clearing Node-RED credentials..."

if [ -f "/home/d3kos/.node-red/flows_cred.json" ]; then
    log "  Removing Node-RED credentials..."
    rm -f /home/d3kos/.node-red/flows_cred.json
fi

# ==============================================================================
# STEP 12: Zero free space (optional, for smaller images)
# ==============================================================================

log ""
warn "STEP 12: Zero free space (optional - reduces image size)..."
warn "This can take a LONG time (10-30 minutes)!"
warn "Skip this step? [Y/n]: "
read -r SKIP_ZERO

if [[ "$SKIP_ZERO" != "n" ]] && [[ "$SKIP_ZERO" != "N" ]]; then
    log "  Skipping free space zeroing"
else
    log "  Zeroing free space (this will take a while)..."
    dd if=/dev/zero of=/tmp/zero.dat bs=1M 2>/dev/null || true
    rm -f /tmp/zero.dat
    log "  Free space zeroed"
fi

# ==============================================================================
# STEP 13: Fix permissions
# ==============================================================================

log ""
log "STEP 13: Fixing permissions..."

chown -R d3kos:d3kos /opt/d3kos/ 2>/dev/null || true
chown -R d3kos:d3kos /home/d3kos/ 2>/dev/null || true

# ==============================================================================
# Summary
# ==============================================================================

log ""
log "=========================================="
log "Sanitization Complete!"
log "=========================================="
log "✓ Logs removed"
log "✓ Shell history cleared"
log "✓ SSH keys removed"
log "✓ WiFi passwords cleared"
log "✓ Browser cache cleared"
log "✓ User data removed"
log "✓ Installation ID reset"
log "✓ Onboarding reset"
log "✓ Signal K data cleared"
log "✓ Node-RED credentials removed"
log ""
log "System is ready for imaging!"
log ""
log "IMPORTANT NEXT STEPS:"
log "  1. Shutdown the system: sudo shutdown -h now"
log "  2. Create image: dd if=/dev/sdX of=d3kos.img bs=4M status=progress"
log "  3. Compress image: gzip d3kos.img"
log "=========================================="

exit 0
