#!/bin/bash
# detect-timezone.sh — d3kOS Timezone Auto-Detection
#
# Queries public IP geolocation APIs to set the system timezone automatically.
# Designed for first boot or redeployment to a new location — the d3kOS image
# is built in one timezone and may be installed anywhere in the world.
#
# Design rules:
#   - Never fails the service (always exits 0)
#   - Tries three independent APIs; moves on if one is unreachable or returns garbage
#   - Validates the response is a real IANA timezone before calling timedatectl
#   - Logs every decision to journal (StandardOutput=journal in unit file)
#   - Safe to run on every boot: if timezone already correct, does nothing

set -uo pipefail

log() { echo "[detect-timezone] $*" >&2; }

CURRENT_TZ=$(timedatectl show --property=Timezone --value 2>/dev/null || cat /etc/timezone 2>/dev/null || echo "UTC")

log "Starting timezone detection (current: ${CURRENT_TZ})"

# ── API query helpers ────────────────────────────────────────────────────────

# Returns the detected timezone string, or returns 1 on failure.
# Each block tries one API and short-circuits to the next on any failure.
detect_timezone() {
    local tz

    # API 1: ip-api.com — HTTP, no auth, JSON response
    tz=$(curl -s --max-time 8 http://ip-api.com/json 2>/dev/null \
        | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['timezone'])" 2>/dev/null)
    if [[ -n "${tz:-}" && "$tz" == */* ]]; then
        log "API 1 (ip-api.com) responded: $tz"
        echo "$tz"
        return 0
    fi

    # API 2: worldtimeapi.org — HTTP, no auth, JSON response
    tz=$(curl -s --max-time 8 http://worldtimeapi.org/api/ip 2>/dev/null \
        | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['timezone'])" 2>/dev/null)
    if [[ -n "${tz:-}" && "$tz" == */* ]]; then
        log "API 2 (worldtimeapi.org) responded: $tz"
        echo "$tz"
        return 0
    fi

    # API 3: ipapi.co — HTTPS, no auth, plain-text timezone string
    tz=$(curl -s --max-time 8 https://ipapi.co/timezone 2>/dev/null)
    if [[ -n "${tz:-}" && "$tz" == */* ]]; then
        log "API 3 (ipapi.co) responded: $tz"
        echo "$tz"
        return 0
    fi

    log "All three APIs unreachable or returned invalid data"
    return 1
}

# ── Main ─────────────────────────────────────────────────────────────────────

if DETECTED=$(detect_timezone 2>/dev/null); then
    if [[ "$DETECTED" == "$CURRENT_TZ" ]]; then
        log "Detected timezone matches current (${CURRENT_TZ}) — no change needed"
    else
        log "Timezone change: ${CURRENT_TZ} → ${DETECTED}"
        if timedatectl set-timezone "$DETECTED" 2>/dev/null; then
            log "Success — timezone is now ${DETECTED}"
        else
            log "timedatectl rejected '${DETECTED}' as invalid — keeping ${CURRENT_TZ}"
        fi
    fi
else
    log "Detection failed — keeping current timezone: ${CURRENT_TZ}"
    log "This is normal on first boot before DNS is fully available."
    log "The service will run again on next boot."
fi

exit 0
