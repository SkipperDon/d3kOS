#!/bin/bash
# Export Queue Boot-time Upload
# Checks queue and uploads pending exports on system boot

set -e

LOG_FILE="/var/log/d3kos-export-boot.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== d3kOS Export Boot-time Upload ==="

# Wait for network (max 60 seconds)
log "Waiting for network..."
for i in {1..12}; do
    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        log "✓ Network available"
        break
    fi
    sleep 5
done

# Check if export manager is running
if ! systemctl is-active --quiet d3kos-export-manager.service; then
    log "⚠ Export manager not running, starting..."
    systemctl start d3kos-export-manager.service
    sleep 3
fi

# Check queue status
QUEUE_STATUS=$(curl -s http://localhost:8094/export/queue/status)
PENDING_COUNT=$(echo "$QUEUE_STATUS" | jq -r '.pending_count // 0')

log "Queue status: $PENDING_COUNT pending exports"

if [ "$PENDING_COUNT" -gt 0 ]; then
    log "Processing pending exports..."

    # Worker will automatically process queue
    # Just wait and monitor

    # Monitor for 5 minutes max
    for i in {1..10}; do
        sleep 30
        QUEUE_STATUS=$(curl -s http://localhost:8094/export/queue/status)
        PENDING_COUNT=$(echo "$QUEUE_STATUS" | jq -r '.pending_count // 0')
        log "Queue status: $PENDING_COUNT pending"

        if [ "$PENDING_COUNT" -eq 0 ]; then
            log "✓ All exports uploaded"
            break
        fi
    done
else
    log "No pending exports"
fi

log "=== Boot-time upload complete ==="
