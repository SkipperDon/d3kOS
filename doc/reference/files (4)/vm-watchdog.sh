#!/usr/bin/env bash
# =============================================================================
# TrueNAS Host-Level VM Watchdog
# Supports: TrueNAS CORE 13 (bhyve) and TrueNAS SCALE (KVM/libvirt)
# Purpose : Ping-based liveness check, VM restart, log analysis, alerting
# =============================================================================
# INSTALL:
#   1. Save to /root/vm-watchdog.sh
#   2. chmod +x /root/vm-watchdog.sh
#   3. Add to TrueNAS cron (every 2 min):  */2 * * * * /root/vm-watchdog.sh
#   4. Edit CONFIG section below
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIG — edit these values
# =============================================================================
VM_NAME="ubuntu-ollama"          # VM name in TrueNAS UI (SCALE: virsh name / CORE: bhyve name)
VM_IP="192.168.1.100"            # Static IP assigned to your Ubuntu VM
PING_COUNT=3                      # Number of ping attempts before declaring down
PING_TIMEOUT=5                    # Seconds to wait per ping
PING_FAILURES_BEFORE_RESTART=2   # Consecutive failed checks before restart
SSH_CHECK=true                    # Also verify SSH port is open (more reliable than ping)
SSH_PORT=22
SSH_TIMEOUT=5

# Ollama agent health endpoint (running inside the VM on port 11435)
AGENT_CHECK=true                  # Query the ollama-agent /health endpoint
AGENT_PORT=11435                  # Must match AGENT_PORT in ollama-agent.py
AGENT_TIMEOUT=10                  # Seconds to wait for agent response

# TrueNAS platform: "CORE" (FreeBSD/bhyve) or "SCALE" (Linux/KVM)
PLATFORM="SCALE"

# Notification settings
NOTIFY_EMAIL="you@example.com"          # Set to "" to disable email
NOTIFY_WEBHOOK=""                        # Slack/Discord/ntfy webhook URL, or ""
NTFY_TOPIC=""                            # ntfy.sh topic (e.g. "truenas-alerts"), or ""

# Cooldown: minimum seconds between restarts (avoid restart loops)
RESTART_COOLDOWN=300   # 5 minutes

# Log and state files
LOG_FILE="/var/log/vm-watchdog.log"
STATE_FILE="/tmp/vm-watchdog-state"
LOCK_FILE="/tmp/vm-watchdog.lock"

# Log analysis thresholds
LOG_ANALYSIS=true
MAX_RESTARTS_PER_HOUR=5      # Alert if VM restarts more than this per hour
# =============================================================================

# --- Lock to prevent overlapping runs ---
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] Watchdog already running, exiting." >> "$LOG_FILE"
    exit 0
fi

# --- Logging helper ---
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$1] $2" | tee -a "$LOG_FILE"
}

# --- Notification helper ---
notify() {
    local subject="$1"
    local body="$2"
    log "NOTIFY" "$subject"

    # Email via TrueNAS sendmail (if configured in TrueNAS UI → Alerts → Email)
    if [[ -n "$NOTIFY_EMAIL" ]]; then
        echo -e "Subject: [VM-Watchdog] $subject\n\n$body\n\nHost: $(hostname)\nTime: $(date)" \
            | sendmail "$NOTIFY_EMAIL" 2>/dev/null || true
    fi

    # Slack/Discord webhook
    if [[ -n "$NOTIFY_WEBHOOK" ]]; then
        curl -s -X POST "$NOTIFY_WEBHOOK" \
            -H 'Content-type: application/json' \
            --data "{\"text\":\"[VM-Watchdog] $subject\n$body\"}" &>/dev/null || true
    fi

    # ntfy.sh push notification (great for mobile alerts)
    if [[ -n "$NTFY_TOPIC" ]]; then
        curl -s -d "$subject: $body" "https://ntfy.sh/$NTFY_TOPIC" &>/dev/null || true
    fi
}

# --- State helpers (track consecutive failures and restart count) ---
get_state() { [[ -f "$STATE_FILE" ]] && cat "$STATE_FILE" || echo "0 0 0"; }
set_state() { echo "$1 $2 $3" > "$STATE_FILE"; }

read -r FAIL_COUNT LAST_RESTART RESTART_COUNT_HOUR <<< "$(get_state)"

# Reset hourly restart counter every 3600 seconds
NOW=$(date +%s)
if (( NOW - LAST_RESTART > 3600 )); then
    RESTART_COUNT_HOUR=0
fi

# =============================================================================
# PLATFORM-SPECIFIC VM MANAGEMENT
# =============================================================================

vm_status() {
    if [[ "$PLATFORM" == "SCALE" ]]; then
        # TrueNAS SCALE uses libvirt/virsh
        virsh domstate "$VM_NAME" 2>/dev/null | grep -q "running" && echo "running" || echo "stopped"
    else
        # TrueNAS CORE uses bhyve; check via middleware or ps
        midclt call virt.instance.query "[[\`name\`,\`=\`,\`$VM_NAME\`]]" 2>/dev/null \
            | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['status'] if d else 'unknown')" \
            2>/dev/null || echo "unknown"
    fi
}

vm_restart() {
    log "ACTION" "Attempting VM restart: $VM_NAME"
    if [[ "$PLATFORM" == "SCALE" ]]; then
        # Graceful shutdown first, then start
        virsh shutdown "$VM_NAME" &>/dev/null || true
        sleep 10
        # Force off if still running
        virsh destroy "$VM_NAME" &>/dev/null || true
        sleep 3
        virsh start "$VM_NAME"
    else
        # TrueNAS CORE via middleware API (works from shell)
        midclt call virt.instance.stop  '{"id":"'"$VM_NAME"'","force":true}' &>/dev/null || true
        sleep 5
        midclt call virt.instance.start '{"id":"'"$VM_NAME"'"}' || true
    fi
    log "ACTION" "VM restart command issued for: $VM_NAME"
}

vm_bridge_reset() {
    # Reset the bridge/tap interface if virtio drops
    log "ACTION" "Attempting bridge reset"
    if [[ "$PLATFORM" == "SCALE" ]]; then
        # Find the bridge used by this VM and bounce it
        BRIDGE=$(virsh domiflist "$VM_NAME" 2>/dev/null | awk '/bridge/{print $3}' | head -1)
        # TrueNAS uses "bridge0", "bridge1" etc — not "br0"
        [[ -z "$BRIDGE" ]] && BRIDGE="bridge0"
        if [[ -n "$BRIDGE" ]]; then
            ip link set "$BRIDGE" down && sleep 1 && ip link set "$BRIDGE" up
            log "INFO" "Bridge $BRIDGE bounced"
        fi
    else
        # CORE: epair/tap interfaces
        VM_ID=$(midclt call virt.instance.query "[[\`name\`,\`=\`,\`$VM_NAME\`]]" 2>/dev/null \
            | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if d else '')" 2>/dev/null || echo "")
        [[ -n "$VM_ID" ]] && ifconfig "tap${VM_ID}" destroy 2>/dev/null || true
    fi
}

# =============================================================================
# LIVENESS CHECKS
# =============================================================================

check_ping() {
    ping -c "$PING_COUNT" -W "$PING_TIMEOUT" "$VM_IP" &>/dev/null
}

check_ssh_port() {
    timeout "$SSH_TIMEOUT" bash -c "echo >/dev/tcp/$VM_IP/$SSH_PORT" &>/dev/null
}

check_ollama_agent() {
    # Query the ollama-agent /health endpoint inside the VM
    local response
    response=$(curl -sf --max-time "$AGENT_TIMEOUT" \
        "http://${VM_IP}:${AGENT_PORT}/health" 2>/dev/null) || return 1
    # Check the "healthy" field in the JSON response
    echo "$response" | grep -q '"healthy": true'
}

vm_is_alive() {
    if check_ping; then
        if $SSH_CHECK && ! check_ssh_port; then
            return 1
        fi
        # If agent check is enabled, query Ollama health too
        if $AGENT_CHECK; then
            if check_ollama_agent; then
                log "INFO" "Ollama agent: healthy ✓"
            else
                log "WARN" "Ollama agent: degraded or unreachable (VM stays up, agent may self-recover)"
                # Don't restart the VM for agent issues — agent handles Ollama restarts internally
                # Only log and notify
                notify "Ollama degraded on $VM_NAME" \
                    "VM is reachable but Ollama agent reports unhealthy status. Check /var/log/ollama-agent.log inside VM."
            fi
        fi
        return 0
    else
        return 1
    fi
}

# =============================================================================
# LOG ANALYSIS
# =============================================================================

analyze_logs() {
    [[ "$LOG_ANALYSIS" != "true" ]] && return

    # Check restart rate
    if (( RESTART_COUNT_HOUR >= MAX_RESTARTS_PER_HOUR )); then
        notify "CRITICAL: VM restart loop detected" \
            "VM '$VM_NAME' has restarted $RESTART_COUNT_HOUR times in the last hour. Manual intervention required."
        log "ALERT" "Restart loop detected: $RESTART_COUNT_HOUR restarts/hour"
    fi

    # Check TrueNAS system log for bridge errors (SCALE)
    if [[ "$PLATFORM" == "SCALE" ]]; then
        local bridge_errors
        # TrueNAS bridge interfaces are named bridge0, bridge1, etc.
        bridge_errors=$(journalctl -n 200 --no-pager 2>/dev/null \
            | grep -iE "(bridge[0-9]+|virtio|tap|vnet|network).*error" | wc -l || echo 0)
        if (( bridge_errors > 10 )); then
            notify "WARNING: High bridge error rate" \
                "$bridge_errors bridge/virtio errors in recent logs. Bridge may be unstable."
        fi

        # Check for kernel panics or OOM in VM
        local oom_events
        oom_events=$(journalctl -n 500 --no-pager 2>/dev/null \
            | grep -c "Out of memory" || echo 0)
        (( oom_events > 0 )) && notify "WARNING: OOM events detected" \
            "$oom_events OOM events found in system journal."
    fi
}

# =============================================================================
# MAIN WATCHDOG LOGIC
# =============================================================================

log "INFO" "--- Watchdog check: VM=$VM_NAME IP=$VM_IP ---"

# Check if VM process is running at all
STATUS=$(vm_status)
log "INFO" "VM hypervisor status: $STATUS"

if [[ "$STATUS" != "running" ]]; then
    log "WARN" "VM is not running (status: $STATUS). Starting it."
    vm_restart
    notify "VM was stopped — restarted" "VM '$VM_NAME' was found stopped. Watchdog has started it."
    set_state 0 "$NOW" "$((RESTART_COUNT_HOUR + 1))"
    exit 0
fi

# VM process is up — now test network liveness
if vm_is_alive; then
    log "INFO" "VM is reachable ✓"
    set_state 0 "$LAST_RESTART" "$RESTART_COUNT_HOUR"
else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    log "WARN" "VM unreachable (failure #$FAIL_COUNT of $PING_FAILURES_BEFORE_RESTART)"

    if (( FAIL_COUNT >= PING_FAILURES_BEFORE_RESTART )); then
        # Enforce cooldown between restarts
        SECONDS_SINCE_RESTART=$((NOW - LAST_RESTART))
        if (( LAST_RESTART > 0 && SECONDS_SINCE_RESTART < RESTART_COOLDOWN )); then
            log "WARN" "Cooldown active — $((RESTART_COOLDOWN - SECONDS_SINCE_RESTART))s remaining. Skipping restart."
        else
            log "ERROR" "VM unreachable after $FAIL_COUNT checks. Initiating recovery."
            notify "VM unreachable — restarting" \
                "VM '$VM_NAME' at $VM_IP failed $FAIL_COUNT consecutive liveness checks. Restarting now."

            # First try a bridge reset (less disruptive)
            vm_bridge_reset
            sleep 15

            if vm_is_alive; then
                log "INFO" "VM recovered after bridge reset ✓"
                notify "VM recovered via bridge reset" "VM '$VM_NAME' is back after bridge bounce."
                set_state 0 "$NOW" "$((RESTART_COUNT_HOUR + 1))"
            else
                # Full VM restart
                vm_restart
                set_state 0 "$NOW" "$((RESTART_COUNT_HOUR + 1))"
                notify "VM hard restarted" "Full restart of '$VM_NAME' was performed."
            fi
        fi
    else
        set_state "$FAIL_COUNT" "$LAST_RESTART" "$RESTART_COUNT_HOUR"
    fi
fi

# Run log analysis on every check
analyze_logs

# Rotate log file if over 5MB
LOG_SIZE=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
if (( LOG_SIZE > 5242880 )); then
    mv "$LOG_FILE" "${LOG_FILE}.1"
    log "INFO" "Log rotated"
fi

log "INFO" "--- Check complete ---"
