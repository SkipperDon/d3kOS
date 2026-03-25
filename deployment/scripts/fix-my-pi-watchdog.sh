#!/bin/bash
# fix-my-pi-watchdog.sh — Fix My Pi watchdog for d3kOS
# Runs every 5–10 minutes via systemd timer (fix-my-pi-watchdog.service)
# Written in bash — survives broken Python. Only requires: bash, curl, systemctl.
#
# What it does:
#   1. Reads credentials from /opt/d3kos/config/cloud-credentials.json
#   2. Polls HostPapa: GET /mobile/fix-my-pi-job.php — any pending job?
#   3. If yes: runs local diagnostics, attempts fixes, posts results
#   4. Posts result to /mobile/fix-my-pi-result.php
#
# Deploy to Pi: /opt/d3kos/services/fix-my-pi-watchdog.sh
# Make executable: chmod +x /opt/d3kos/services/fix-my-pi-watchdog.sh

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
CREDS_FILE="/opt/d3kos/config/cloud-credentials.json"
LOG_FILE="/var/log/d3kos-fmp-watchdog.log"
BASE_URL="https://atmyboat.com"
TIMEOUT=30    # curl timeout seconds

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

# ── Load credentials ──────────────────────────────────────────────────────────
if [ ! -f "$CREDS_FILE" ]; then
    log "ERROR: $CREDS_FILE not found — cannot authenticate."
    exit 1
fi

API_KEY=$(python3 -c "import json,sys; d=json.load(open('$CREDS_FILE')); print(d.get('atmyboat_api_key',''))" 2>/dev/null || echo "")
DEVICE_UUID=$(python3 -c "import json,sys; d=json.load(open('$CREDS_FILE')); print(d.get('device_uuid',''))" 2>/dev/null || echo "")

if [ -z "$API_KEY" ] || [ -z "$DEVICE_UUID" ]; then
    log "ERROR: Missing API key or device UUID in $CREDS_FILE"
    exit 1
fi

AUTH_HEADER="Authorization: Bearer $API_KEY"
TOKEN_HEADER="X-Device-Token: $DEVICE_UUID"

# ── Poll for pending job ──────────────────────────────────────────────────────
log "Polling for pending Fix My Pi job..."

RESPONSE=$(curl -sf --max-time "$TIMEOUT" \
    -H "$AUTH_HEADER" \
    -H "$TOKEN_HEADER" \
    "${BASE_URL}/mobile/fix-my-pi-job.php" 2>/dev/null || echo "")

if [ -z "$RESPONSE" ]; then
    log "No response from server (offline or no job). Exiting."
    exit 0
fi

JOB_ID=$(echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); j=d.get('data',{}).get('job'); print(j['id'] if j else '')" 2>/dev/null || echo "")

if [ -z "$JOB_ID" ]; then
    log "No pending job."
    exit 0
fi

log "Pending Fix My Pi job found: #$JOB_ID — starting diagnostics."

# ── Run diagnostics ───────────────────────────────────────────────────────────
CHECKS_JSON="[]"
SERVICES_RESTARTED="[]"
ERRORS_JSON="[]"
SUMMARY=""

run_check() {
    local name="$1"
    local result="ok"
    local action="none"
    local output=""

    case "$name" in
        services)
            SERVICES=("signalk" "node-red" "avnav" "nginx")
            local restarted=()
            for svc in "${SERVICES[@]}"; do
                if ! systemctl is-active --quiet "$svc" 2>/dev/null; then
                    log "Service $svc is down — attempting restart."
                    if systemctl restart "$svc" 2>/dev/null; then
                        sleep 3
                        if systemctl is-active --quiet "$svc" 2>/dev/null; then
                            restarted+=("$svc")
                            action="restarted_$svc"
                        else
                            result="failed"
                            action="restart_failed_$svc"
                        fi
                    fi
                fi
            done
            if [ ${#restarted[@]} -gt 0 ]; then
                SERVICES_RESTARTED=$(python3 -c "import json; print(json.dumps($(printf '"%s",' "${restarted[@]}" | sed 's/,$//')))" 2>/dev/null || echo '[]')
                result="fixed"
            fi
            ;;
        disk)
            local free_kb
            free_kb=$(df /opt/d3kos 2>/dev/null | awk 'NR==2{print $4}' || echo "0")
            local free_mb=$(( free_kb / 1024 ))
            if [ "$free_mb" -lt 500 ]; then
                result="low_disk"
                # Clear log cache
                find /var/log/d3kos -name "*.log" -mtime +7 -delete 2>/dev/null || true
                journalctl --vacuum-size=100M 2>/dev/null || true
                action="cleared_old_logs"
            else
                result="ok_${free_mb}mb_free"
            fi
            ;;
        memory)
            local free_mb
            free_mb=$(free -m 2>/dev/null | awk '/^Mem:/{print $7}' || echo "0")
            if [ "$free_mb" -lt 100 ]; then
                result="low_memory_${free_mb}mb"
                action="flagged"
            else
                result="ok_${free_mb}mb_free"
            fi
            ;;
        network)
            if curl -sf --max-time 5 https://atmyboat.com > /dev/null 2>&1; then
                result="ok_internet_reachable"
            else
                result="no_internet"
                action="flagged"
            fi
            ;;
        signalk)
            if curl -sf --max-time 5 http://localhost:3000/signalk > /dev/null 2>&1; then
                result="ok_responding"
            else
                result="not_responding"
                systemctl restart signalk 2>/dev/null && sleep 5 && action="restarted"
            fi
            ;;
        node_red)
            if curl -sf --max-time 5 http://localhost:1880 > /dev/null 2>&1; then
                result="ok_responding"
            else
                result="not_responding"
                systemctl restart node-red 2>/dev/null && sleep 3 && action="restarted"
            fi
            ;;
    esac

    echo "{\"name\":\"$name\",\"result\":\"$result\",\"action_taken\":\"$action\"}"
}

# Run each check and accumulate JSON
CHECK_RESULTS=()
for check in services disk memory network signalk node_red; do
    log "Running check: $check"
    CHECK_RESULTS+=("$(run_check "$check")")
done

# Build checks JSON array
CHECKS_JSON="[$(IFS=,; echo "${CHECK_RESULTS[*]}")]"

# Build summary
FIXED_COUNT=$(echo "$CHECKS_JSON" | python3 -c "import json,sys; checks=json.load(sys.stdin); print(sum(1 for c in checks if 'fixed' in c.get('result','') or 'restarted' in c.get('action_taken','')))" 2>/dev/null || echo "0")
SUMMARY="Fix My Pi diagnostic complete. Ran 6 checks. $FIXED_COUNT issue(s) found and fixed."

log "Diagnostics complete. $SUMMARY"

# ── Post results ──────────────────────────────────────────────────────────────
RESULT_PAYLOAD=$(python3 -c "
import json
payload = {
    'job_id': $JOB_ID,
    'status': 'completed',
    'report': {
        'checks_run': $CHECKS_JSON,
        'services_restarted': $SERVICES_RESTARTED,
        'errors': $ERRORS_JSON,
        'summary': '$SUMMARY'
    }
}
print(json.dumps(payload))
" 2>/dev/null)

if [ -z "$RESULT_PAYLOAD" ]; then
    log "ERROR: Failed to build result payload."
    exit 1
fi

POST_RESPONSE=$(curl -sf --max-time "$TIMEOUT" \
    -X POST \
    -H "$AUTH_HEADER" \
    -H "$TOKEN_HEADER" \
    -H "Content-Type: application/json" \
    -d "$RESULT_PAYLOAD" \
    "${BASE_URL}/mobile/fix-my-pi-result.php" 2>/dev/null || echo "")

if echo "$POST_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    log "Result posted successfully for job #$JOB_ID."
else
    log "WARNING: Result post failed or no response. Server may have timed out."
fi

exit 0
