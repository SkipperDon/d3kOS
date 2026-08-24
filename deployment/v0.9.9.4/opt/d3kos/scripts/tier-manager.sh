#!/bin/bash
# tier-manager.sh - Manage license tiers and feature restrictions
# Part of d3kOS Tier Management System

set -e

LICENSE_FILE="/opt/d3kos/config/license.json"
SCRIPT_DIR="$(dirname "$0")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/d3kos-tier-manager.log
}

# Check if license.json exists
if [ ! -f "$LICENSE_FILE" ]; then
    log "ERROR: license.json not found at $LICENSE_FILE"
    log "ERROR: Run generate-installation-id.sh first (Task #1)"
    exit 1
fi

# Read current tier
current_tier=$(jq -r '.tier' "$LICENSE_FILE")
log "Current tier: $current_tier"

# Detect OpenCPN installation
opencpn_installed=$("$SCRIPT_DIR/detect-opencpn.sh")
log "OpenCPN installed: $opencpn_installed"

# Auto-upgrade to Tier 2 if OpenCPN is installed
if [ "$opencpn_installed" = "true" ] && [ "$current_tier" -lt 2 ]; then
    log "OpenCPN detected! Upgrading to Tier 2..."

    # Update license.json
    jq '.tier = 2 |
        .features.voice_assistant = true |
        .features.camera = true |
        .features.unlimited_resets = true |
        .max_resets = 9999 |
        .upgrade_method = "opencpn_detect" |
        .upgraded_at = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' \
        "$LICENSE_FILE" > "$LICENSE_FILE.tmp"

    mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
    chmod 644 "$LICENSE_FILE"
    chown d3kos:d3kos "$LICENSE_FILE"

    log "Upgraded to Tier 2 successfully!"
    current_tier=2
fi

# Check if paid tier (subscription)
is_paid=$(jq -r '.is_paid_tier // false' "$LICENSE_FILE")
subscription_status=$(jq -r '.subscription_status // "none"' "$LICENSE_FILE")

if [ "$is_paid" = "true" ] && [ "$subscription_status" = "active" ]; then
    paid_tier=$(jq -r '.paid_tier_level // 0' "$LICENSE_FILE")

    if [ "$paid_tier" -eq 2 ] && [ "$current_tier" -lt 2 ]; then
        log "Active Tier 2 subscription detected! Upgrading..."
        jq '.tier = 2 |
            .features.voice_assistant = true |
            .features.camera = true |
            .features.unlimited_resets = true |
            .max_resets = 9999' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        current_tier=2
    fi

    if [ "$paid_tier" -eq 3 ] && [ "$current_tier" -lt 3 ]; then
        log "Active Tier 3 subscription detected! Upgrading..."
        jq '.tier = 3 |
            .features.voice_assistant = true |
            .features.camera = true |
            .features.unlimited_resets = true |
            .features.cloud_sync = true |
            .max_resets = 9999' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        current_tier=3
    fi
fi

# Update feature flags based on tier
case $current_tier in
    0)
        log "Tier 0: Disabling voice assistant and camera"
        jq '.features.voice_assistant = false |
            .features.camera = false |
            .features.unlimited_resets = false |
            .features.cloud_sync = false |
            .max_resets = 10' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
    1)
        log "Tier 1: Disabling voice assistant and camera (mobile app integration only)"
        jq '.features.voice_assistant = false |
            .features.camera = false |
            .features.unlimited_resets = false |
            .features.cloud_sync = false |
            .max_resets = 10' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
    2)
        log "Tier 2: Enabling voice assistant and camera"
        jq '.features.voice_assistant = true |
            .features.camera = true |
            .features.unlimited_resets = true |
            .features.cloud_sync = false |
            .max_resets = 9999' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
    3)
        log "Tier 3: Enabling all features (voice, camera, cloud sync)"
        jq '.features.voice_assistant = true |
            .features.camera = true |
            .features.unlimited_resets = true |
            .features.cloud_sync = true |
            .max_resets = 9999' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
esac

log "Tier management complete. Current tier: $current_tier"

# Output tier for systemd services to use
echo "$current_tier"
