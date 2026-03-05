#!/bin/bash
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

# Daily Scheduled Export (Tier 2+ only)
# Runs daily at 3:00 AM via systemd timer

set -e

LOG_FILE="/var/log/d3kos-export-daily.log"
touch "$LOG_FILE" 2>/dev/null || LOG_FILE="/tmp/d3kos-export-daily.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== d3kOS Daily Scheduled Export ==="

# Wait for tier API
wait_for_api() {
  local url="$1" max=10 i=0
  while [ $i -lt $max ]; do
    if curl -sf "$url" > /dev/null 2>&1; then return 0; fi
    i=$((i+1)); sleep 3
  done
  return 1
}

if ! wait_for_api "http://localhost:8093/tier/status"; then
  log "⚠ Tier API not available after 30s — skipping export"
  exit 0
fi
TIER_STATUS=$(curl -s http://localhost:8093/tier/status)
TIER=$(echo "$TIER_STATUS" | jq -r '.tier // 0')

log "Current tier: $TIER"

if [ "$TIER" -lt 2 ]; then
    log "⚠ Scheduled export requires Tier 2+ (current: Tier $TIER)"
    log "Skipping export"
    exit 0
fi

log "Triggering export..."

# Trigger export
RESULT=$(curl -s -X POST http://localhost:8094/export/generate)
SUCCESS=$(echo "$RESULT" | jq -r '.success // false')

if [ "$SUCCESS" = "true" ]; then
    QUEUE_ID=$(echo "$RESULT" | jq -r '.queue_id')
    CATEGORY_COUNT=$(echo "$RESULT" | jq -r '.category_count')
    log "✓ Export generated and queued: $QUEUE_ID ($CATEGORY_COUNT categories)"
else
    ERROR=$(echo "$RESULT" | jq -r '.error // "Unknown error"')
    log "✗ Export failed: $ERROR"
    exit 1
fi

log "=== Daily export complete ==="