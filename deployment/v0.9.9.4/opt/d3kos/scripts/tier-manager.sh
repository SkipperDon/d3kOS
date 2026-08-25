#!/bin/bash
# tier-manager.sh - Manage license tiers and feature restrictions
# Part of d3kOS Tier Management System
#
# Ordering (MASTER_SYSTEM_SPEC §6.3.1 v4.0 — BUG-77 fix):
#   Tier 3: subscription.key present OR paid subscription active
#   Tier 2: OpenCPN installed
#   Tier 1: server-approved (reads tier1-approval.json cache written by tier_service.py)
#   Tier 0: none of the above
#
# IMPORTANT: Runtime Tier 1 detection (server call + cache update) is handled by
# tier_service.py::detect_tier() at /tier/status. This script reads the cache for
# boot-time setup only — it does not make a new network call.

set -e

LICENSE_FILE="/opt/d3kos/config/license.json"
SUBSCRIPTION_KEY="/opt/d3kos/config/subscription.key"
APPROVAL_CACHE="/opt/d3kos/state/tier1-approval.json"
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

# Ordering: highest tier wins. Test Tier 3 first.
current_tier=0

# Tier 3a: subscription.key present (filesystem sentinel — BUG-65 tracks hardening)
if [ -f "$SUBSCRIPTION_KEY" ]; then
    log "subscription.key present — Tier 3"
    current_tier=3
fi

# Tier 3b: active paid subscription in license.json (only if not already Tier 3)
if [ "$current_tier" -lt 3 ]; then
    is_paid=$(jq -r '.is_paid_tier // false' "$LICENSE_FILE")
    subscription_status=$(jq -r '.subscription_status // "none"' "$LICENSE_FILE")

    if [ "$is_paid" = "true" ] && [ "$subscription_status" = "active" ]; then
        paid_tier=$(jq -r '.paid_tier_level // 0' "$LICENSE_FILE")
        if [ "$paid_tier" -ge 3 ]; then
            log "Active Tier 3 paid subscription — Tier 3"
            current_tier=3
        elif [ "$paid_tier" -eq 2 ] && [ "$current_tier" -lt 2 ]; then
            log "Active Tier 2 paid subscription"
            current_tier=2
        fi
    fi
fi

# Tier 2: OpenCPN installed (only if not already Tier 3)
if [ "$current_tier" -lt 2 ]; then
    opencpn_installed=$("$SCRIPT_DIR/detect-opencpn.sh")
    log "OpenCPN installed: $opencpn_installed"
    if [ "$opencpn_installed" = "true" ]; then
        log "OpenCPN detected — Tier 2"
        current_tier=2
    fi
fi

# Tier 1: server-approved (reads tier_service cache; network call is done by tier_service.py)
# Only consulted if not already Tier 2+.
if [ "$current_tier" -lt 1 ]; then
    if [ -f "$APPROVAL_CACHE" ]; then
        server_approved=$(python3 -c "
import json, time
from pathlib import Path
try:
    cache = json.loads(Path('$APPROVAL_CACHE').read_text())
    age_min = (time.time() - cache.get('cached_at', 0)) / 60
    if age_min < 60 and cache.get('approved'):
        print('true')
    else:
        print('false')
except Exception:
    print('false')
" 2>/dev/null || echo "false")
        if [ "$server_approved" = "true" ]; then
            log "Server-approved cache valid — Tier 1"
            current_tier=1
        else
            log "Server-approval cache missing or stale — Tier 0 (tier_service will poll at runtime)"
        fi
    else
        log "No approval cache — Tier 0 (tier_service will poll at runtime)"
    fi
fi

log "Detected tier: $current_tier"

# Write tier to license.json for legacy consumers
jq --argjson t "$current_tier" '.tier = $t' "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"

# Update feature flags based on tier
case $current_tier in
    0)
        log "Tier 0: Disabling paid features"
        jq '.features.voice_assistant = false |
            .features.camera = false |
            .features.unlimited_resets = false |
            .features.cloud_sync = false |
            .max_resets = 10' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
    1)
        log "Tier 1: Server-approved — mobile app integration features enabled"
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
        chmod 644 "$LICENSE_FILE"
        chown d3kos:d3kos "$LICENSE_FILE"
        ;;
esac

log "Tier management complete. Current tier: $current_tier"

# Output tier for systemd services to use
echo "$current_tier"
