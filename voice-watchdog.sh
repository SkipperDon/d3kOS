#!/bin/bash
# d3kOS Voice Assistant Watchdog
# Monitors voice service health and auto-restarts if threads fail

SERVICE_NAME="d3kos-voice.service"
LOG_FILE="/var/log/d3kos-voice-watchdog.log"
MAX_LOG_SIZE=1048576  # 1MB

# Rotate log if too large
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE") -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "$LOG_FILE.old"
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if service is running
if ! systemctl is-active --quiet $SERVICE_NAME; then
    log "ERROR: Service not running. Starting..."
    systemctl start $SERVICE_NAME
    sleep 5
    exit 0
fi

# Get PID
PID=$(systemctl show -p MainPID --value $SERVICE_NAME)
if [ -z "$PID" ] || [ "$PID" = "0" ]; then
    log "ERROR: Cannot get service PID. Restarting..."
    systemctl restart $SERVICE_NAME
    exit 1
fi

# Check thread count (should be at least 2: main + Vosk listener)
THREAD_COUNT=$(ps -T -p $PID 2>/dev/null | tail -n +2 | wc -l)
if [ "$THREAD_COUNT" -lt 2 ]; then
    log "ERROR: Only $THREAD_COUNT thread(s) running (expected 2+). Restarting service..."
    systemctl restart $SERVICE_NAME
    sleep 5

    # Verify restart worked
    NEW_PID=$(systemctl show -p MainPID --value $SERVICE_NAME)
    NEW_THREAD_COUNT=$(ps -T -p $NEW_PID 2>/dev/null | tail -n +2 | wc -l)
    if [ "$NEW_THREAD_COUNT" -lt 2 ]; then
        log "CRITICAL: Restart failed - still only $NEW_THREAD_COUNT thread(s). Check logs."
        exit 1
    else
        log "SUCCESS: Restart successful. Now $NEW_THREAD_COUNT threads running."
    fi
    exit 0
fi

# Check if arecord subprocess is running (Vosk audio capture)
ARECORD_COUNT=$(pgrep -P $PID arecord | wc -l)
if [ "$ARECORD_COUNT" -eq 0 ]; then
    log "WARNING: No arecord process found. Vosk may not be capturing audio."

    # Check recent logs for Vosk startup
    if ! journalctl -u $SERVICE_NAME --since "2 minutes ago" | grep -q "Listening for wake words"; then
        log "ERROR: Vosk not listening. Restarting service..."
        systemctl restart $SERVICE_NAME
        exit 1
    fi
fi

# Check for callback activity (should see DEBUG-CALLBACK if detecting)
# If we only see DEBUG-LOOP for extended period, callback might be stuck
DEBUG_LOOP_COUNT=$(journalctl -u $SERVICE_NAME --since "1 minute ago" -n 100 | grep -c "DEBUG-LOOP")
DEBUG_CALLBACK_COUNT=$(journalctl -u $SERVICE_NAME --since "1 minute ago" -n 100 | grep -c "DEBUG-CALLBACK")

if [ "$DEBUG_LOOP_COUNT" -gt 50 ] && [ "$DEBUG_CALLBACK_COUNT" -eq 0 ]; then
    # Main loop running but no callbacks for 1 minute
    # This could be normal (no wake words spoken) or a problem
    # Only restart if we also have other issues (like missing arecord)
    if [ "$ARECORD_COUNT" -eq 0 ]; then
        log "WARNING: High DEBUG-LOOP count ($DEBUG_LOOP_COUNT) with no arecord. Possible stuck state."
    fi
fi

# Check microphone signal strength (if arecord exists)
if command -v arecord &> /dev/null && command -v sox &> /dev/null; then
    # Quick 1-second test
    MIC_DEVICE="plughw:3,0"
    TEST_FILE="/tmp/voice_watchdog_test_$$.wav"

    if timeout 2 arecord -D $MIC_DEVICE -d 1 -f S16_LE -r 16000 $TEST_FILE 2>/dev/null; then
        SIGNAL=$(sox $TEST_FILE -n stat 2>&1 | grep "Maximum amplitude" | awk '{print $3}')
        rm -f $TEST_FILE

        # Check if signal too weak (< 0.01 = 1%)
        if [ -n "$SIGNAL" ]; then
            SIGNAL_INT=$(echo "$SIGNAL * 1000" | bc 2>/dev/null | cut -d. -f1)
            if [ "$SIGNAL_INT" -lt 10 ]; then
                log "WARNING: Weak microphone signal ($SIGNAL). Check volume/mute button."
            fi
        fi
    fi
fi

# All checks passed
log "OK: Service healthy. Threads: $THREAD_COUNT, arecord: $ARECORD_COUNT"
exit 0
