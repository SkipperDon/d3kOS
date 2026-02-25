# Voice Assistant Watchdog System

**Date**: February 25, 2026
**Purpose**: Automatic monitoring and self-healing for d3kOS voice assistant
**Status**: Ready for deployment

---

## Problem Solved

The voice assistant service runs but the Vosk background thread fails to start, causing:
- Main thread runs (checking for wake words)
- Background Vosk listener thread missing
- No `arecord` subprocess (no audio capture)
- Callback never fires
- Wake word detection doesn't work

**Root Cause**: Background daemon thread either never starts or crashes immediately after service start.

---

## Solution: Watchdog System

Automated monitoring system that:
1. **Checks every 2 minutes** if voice service is healthy
2. **Verifies both threads** are running (main + Vosk listener)
3. **Checks for arecord** subprocess (audio capture)
4. **Monitors microphone signal** strength
5. **Auto-restarts service** if any check fails
6. **Logs all actions** to `/var/log/d3kos-voice-watchdog.log`

---

## Health Checks Performed

### 1. Service Running Check
- Verifies `d3kos-voice.service` is active
- If not: Starts service

### 2. Thread Count Check ⭐ **KEY CHECK**
- Counts threads in voice process
- Expected: 2+ threads (main + Vosk background)
- If < 2: **Restarts service immediately**

### 3. Audio Capture Check
- Looks for `arecord` subprocess (child of voice service)
- `arecord` is spawned by Vosk to capture microphone audio
- If missing: Warns and checks if Vosk recently started

### 4. Callback Activity Check
- Monitors logs for `DEBUG-LOOP` vs `DEBUG-CALLBACK` messages
- High loop count with no callbacks = possible stuck state
- Combined with missing arecord = restart triggered

### 5. Microphone Signal Check
- Tests microphone with 1-second recording
- Measures signal amplitude with `sox`
- Warns if signal < 1% (too weak for detection)

---

## Files Created

### 1. Watchdog Script
**Location**: `/opt/d3kos/scripts/voice-watchdog.sh`
**Purpose**: Main health check logic
**Runs as**: root (needs systemctl permissions)

**What it does:**
- Runs all 5 health checks
- Logs results to `/var/log/d3kos-voice-watchdog.log`
- Auto-restarts service if issues found
- Verifies restart succeeded

### 2. Systemd Service
**Location**: `/etc/systemd/system/d3kos-voice-watchdog.service`
**Type**: Oneshot (runs once per timer trigger)
**Purpose**: Wrapper to run watchdog script

### 3. Systemd Timer
**Location**: `/etc/systemd/system/d3kos-voice-watchdog.timer`
**Schedule**: Every 2 minutes
**Purpose**: Triggers watchdog service on schedule

---

## Deployment

### Quick Deploy (Automated)
```bash
cd /home/boatiq
./deploy-voice-watchdog.sh
```

This will:
1. Copy files to Pi via SSH
2. Install to correct locations
3. Enable and start timer
4. Show status

### Manual Deploy

**On your development machine:**
```bash
cd /home/boatiq

# Copy files to Pi
scp -i ~/.ssh/d3kos_key voice-watchdog.sh d3kos@192.168.1.237:/tmp/
scp -i ~/.ssh/d3kos_key d3kos-voice-watchdog.service d3kos@192.168.1.237:/tmp/
scp -i ~/.ssh/d3kos_key d3kos-voice-watchdog.timer d3kos@192.168.1.237:/tmp/
```

**On the Pi (via SSH):**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Install watchdog script
sudo mkdir -p /opt/d3kos/scripts
sudo mv /tmp/voice-watchdog.sh /opt/d3kos/scripts/
sudo chmod +x /opt/d3kos/scripts/voice-watchdog.sh
sudo chown root:root /opt/d3kos/scripts/voice-watchdog.sh

# Install systemd files
sudo mv /tmp/d3kos-voice-watchdog.service /etc/systemd/system/
sudo mv /tmp/d3kos-voice-watchdog.timer /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/d3kos-voice-watchdog.*

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable d3kos-voice-watchdog.timer
sudo systemctl start d3kos-voice-watchdog.timer

# Check status
systemctl status d3kos-voice-watchdog.timer
```

---

## Usage

### Check Watchdog Status
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'systemctl status d3kos-voice-watchdog.timer'
```

### View Watchdog Logs
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'cat /var/log/d3kos-voice-watchdog.log'
```

### Run Watchdog Manually (Force Check Now)
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'sudo systemctl start d3kos-voice-watchdog.service'
```

### View Next Scheduled Run
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'systemctl list-timers d3kos-voice-watchdog.timer'
```

### Disable Watchdog
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'sudo systemctl stop d3kos-voice-watchdog.timer'
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'sudo systemctl disable d3kos-voice-watchdog.timer'
```

### Re-enable Watchdog
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'sudo systemctl enable d3kos-voice-watchdog.timer'
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'sudo systemctl start d3kos-voice-watchdog.timer'
```

---

## Log Format

**Log Location**: `/var/log/d3kos-voice-watchdog.log`

**Example Healthy Log:**
```
[2026-02-25 15:45:00] OK: Service healthy. Threads: 2, arecord: 1
[2026-02-25 15:47:00] OK: Service healthy. Threads: 2, arecord: 1
```

**Example Restart Log:**
```
[2026-02-25 15:49:00] ERROR: Only 1 thread(s) running (expected 2+). Restarting service...
[2026-02-25 15:49:05] SUCCESS: Restart successful. Now 2 threads running.
```

**Example Warning Log:**
```
[2026-02-25 15:51:00] WARNING: No arecord process found. Vosk may not be capturing audio.
[2026-02-25 15:51:00] WARNING: Weak microphone signal (0.006). Check volume/mute button.
```

**Log Rotation:**
- Automatically rotates when log exceeds 1MB
- Old log moved to `/var/log/d3kos-voice-watchdog.log.old`

---

## What This Fixes

### Before Watchdog:
1. Voice service starts
2. Background Vosk thread fails to start
3. Only 1 thread running (main loop)
4. No arecord subprocess (no audio)
5. Callback never fires
6. Service appears "running" but doesn't work
7. **Manual intervention required** to diagnose and restart

### After Watchdog:
1. Voice service starts
2. Background Vosk thread fails to start
3. **Watchdog detects** only 1 thread (within 2 minutes)
4. **Watchdog restarts** service automatically
5. Restart creates 2 threads + arecord subprocess
6. Vosk starts capturing audio
7. Wake word detection works
8. **No manual intervention needed**

---

## Monitoring Frequency

**Why 2 minutes?**
- Fast enough to catch failures quickly
- Slow enough to not overload system
- Voice is Tier 2 feature (not critical like engine monitoring)
- Allows ~30 seconds for service startup + 90 seconds margin

**Can be adjusted** in `/etc/systemd/system/d3kos-voice-watchdog.timer`:
```ini
[Timer]
OnUnitActiveSec=2min  # Change this value (e.g., 1min, 5min, 10min)
```

After changing:
```bash
sudo systemctl daemon-reload
sudo systemctl restart d3kos-voice-watchdog.timer
```

---

## Performance Impact

**CPU**: ~0.1% during check (2-second burst every 2 minutes)
**Memory**: ~5MB for script execution
**Disk I/O**: Minimal (append to log file)
**Network**: None

**Total Impact**: Negligible on Raspberry Pi 4B

---

## Integration with Self-Healing System

This watchdog is **complementary** to the existing d3kos-self-healing system:

| System | Scope | Frequency | Action |
|--------|-------|-----------|--------|
| **Self-Healing** | All d3kos services | 5 minutes | Restart any failed service |
| **Voice Watchdog** | Voice assistant only | 2 minutes | Restart if threads missing |

**Why both?**
- Self-healing checks if service is running (basic)
- Voice watchdog checks if service is *working correctly* (advanced)
- Voice watchdog has voice-specific checks (threads, arecord, microphone)

---

## Troubleshooting

### Watchdog Timer Not Running
```bash
# Check timer status
systemctl status d3kos-voice-watchdog.timer

# Check timer list
systemctl list-timers | grep voice

# Start timer
sudo systemctl start d3kos-voice-watchdog.timer
```

### Watchdog Restarting Service Too Often
Check logs to see why:
```bash
cat /var/log/d3kos-voice-watchdog.log | grep ERROR

# Common causes:
# - "Only 1 thread(s) running" = Vosk thread not starting (voice service bug)
# - "No arecord process" = Vosk not capturing audio
# - "Weak microphone signal" = Hardware issue (volume, mute button)
```

### Watchdog Not Detecting Issues
```bash
# Run manually to see what it checks
sudo /opt/d3kos/scripts/voice-watchdog.sh

# Check if timer is actually running
systemctl list-timers d3kos-voice-watchdog.timer
```

---

## Uninstall

```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 << 'EOF'
sudo systemctl stop d3kos-voice-watchdog.timer
sudo systemctl disable d3kos-voice-watchdog.timer
sudo rm /etc/systemd/system/d3kos-voice-watchdog.service
sudo rm /etc/systemd/system/d3kos-voice-watchdog.timer
sudo rm /opt/d3kos/scripts/voice-watchdog.sh
sudo rm /var/log/d3kos-voice-watchdog.log*
sudo systemctl daemon-reload
EOF
```

---

## Future Enhancements

1. **Microphone auto-gain** - Boost signal if consistently weak
2. **Thread count trending** - Alert if threads fluctuating
3. **Wake word test** - Periodically test detection with synthetic audio
4. **Callback timeout** - Restart if no callbacks for 5+ minutes (even with arecord running)
5. **Integration dashboard** - Show watchdog status in web UI

---

## Summary

**What**: Automated monitoring and self-healing for voice assistant threads
**Why**: Vosk background thread fails to start, breaking wake word detection
**How**: Check every 2 minutes, restart if threads missing
**Impact**: Voice assistant becomes self-healing, no manual restarts needed

**Ready to deploy**: Run `./deploy-voice-watchdog.sh` from `/home/boatiq/`
