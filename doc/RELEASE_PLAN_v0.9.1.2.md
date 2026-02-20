# d3kOS v0.9.1.2 Release Plan

**Version**: 0.9.1.2 (Tier 0 Installation Complete)
**Date**: February 20, 2026
**Status**: READY FOR IMPLEMENTATION
**Tier Setting**: 3 (for testing purposes)

---

## EXECUTIVE SUMMARY

This plan outlines the remaining work to complete d3kOS v0.9.1.2, which represents a **complete Tier 0 installation** with all core features implemented, tested, documented, and committed. Work is divided into **4 parallel sessions** with clear dependencies identified.

**Exclusions** (per user requirements):
- ❌ Web database / central server
- ❌ Hosted website (atmyboat.com)
- ❌ E-commerce / Stripe billing
- ❌ Mobile apps (iOS/Android)

**Requirements**:
- ✅ All work verified, tested, documented, committed
- ✅ Version set to 0.9.1.2
- ✅ Tier set to 3 for testing
- ✅ Image build process documented
- ✅ Documents pushed to GitHub

---

## CURRENT STATUS ASSESSMENT

### ✅ IMPLEMENTED & WORKING

| Feature | Status | Notes |
|---------|--------|-------|
| Installation ID system | ✅ Complete | File-based, persistent |
| License/Tier system | ✅ Complete | Tier detection, feature restrictions |
| Onboarding wizard (Initial Setup) | ✅ Complete | 20 steps, QR code, DIP switches |
| Main menu (index.html) | ✅ Complete | 9 buttons, responsive |
| Dashboard (dashboard.html) | ✅ Complete | Engine metrics, tank levels, system status |
| Navigation page | ✅ Complete | GPS data, WebSocket integration |
| Weather page | ✅ Complete | Windy.com radar, touch controls |
| Boatlog page | ✅ Complete | Voice/text/auto entries (export broken) |
| Settings page | ✅ Complete | System configuration |
| AI Assistant (text) | ✅ Complete | Web UI, 13 instant patterns, caching |
| Camera streaming | ✅ Complete | Reolink integration, RTSP, port 8084 |
| Fish detection (basic) | ✅ Partial | YOLOv8n ONNX, person detection only |
| Telegram notifications | ✅ Complete | Fish capture alerts |
| Manual management | ✅ Complete | Auto-search, upload, API |
| Health monitoring | ✅ Complete | Pi system metrics |
| History API | ✅ Complete | Port 8092 |
| Upload API | ✅ Complete | Port 8097 |
| Export Manager | ✅ Partial | Service running, queue logic missing |

### ❌ NOT IMPLEMENTED

| Feature | Priority | Effort | Session |
|---------|----------|--------|---------|
| **Timezone Auto-Detection** | HIGH | 3-4h | Session A |
| **Self-Healing System** | MEDIUM | 6-8h | Session B |
| **Data Export Queue/Retry** | MEDIUM | 4-5h | Session C |
| **Backup & Restore** | LOW | 3-4h | Session D |
| **Voice Assistant Fix** | HIGH | 2-3h | Session A |
| **Boatlog Export Fix** | HIGH | 1-2h | Session C |
| **OpenCPN Auto-Install** | MEDIUM | 2-3h | Session D |
| **Version Update (0.9.1.2)** | HIGH | 1h | Session A |
| **Tier Set to 3** | HIGH | 30min | Session A |
| **Image Build Documentation** | HIGH | 2-3h | Session D |
| **Testing Suite** | HIGH | 4-6h | All Sessions |
| **Documentation Updates** | HIGH | 3-4h | All Sessions |

### ⚠️ NEEDS IMPROVEMENT

| Feature | Issue | Effort | Session |
|---------|-------|--------|---------|
| Fish Detection | Only detects person, needs fish model | 6-8h | Future (excluded) |
| Charts Page | Needs o-charts addon | 2-3h | Future (excluded) |

---

## PARALLEL SESSION PLAN

### Session Dependencies Matrix

```
Session A (Foundation)
    ↓
Session B (Intelligence)  Session C (Data)  Session D (Deployment)
    ↓                         ↓                   ↓
    └─────────────────────────┴───────────────────┘
                         ↓
              Final Integration & Testing
                         ↓
                   GitHub Push
```

**Dependency Rules**:
- **Session A MUST complete first** (version, tier, timezone)
- Sessions B, C, D can run in parallel after A completes
- All sessions must complete before final integration testing
- GitHub push happens after all commits are made

---

## SESSION A: FOUNDATION & CRITICAL FIXES

**Owner**: Primary session (run first, blocks others)
**Domain**: System Configuration, Voice, Version Management
**Duration**: 6-8 hours
**Dependencies**: None (runs first)

### Objectives
1. ✅ Update system version to 0.9.1.2
2. ✅ Set tier to 3 for testing
3. ✅ Implement timezone auto-detection
4. ✅ Fix voice assistant wake word detection
5. ✅ Test and verify all changes
6. ✅ Document updates
7. ✅ Commit to git

---

### Task A1: Version & Tier Update (1 hour)

#### Step A1.1: Update Version Number
```bash
# SSH to Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Update license.json
sudo nano /opt/d3kos/config/license.json
# Change: "version": "1.0.3" → "version": "0.9.1.2"

# Create version file
cat > /opt/d3kos/config/version.txt << 'EOF'
d3kOS Version 0.9.1.2
Release Date: February 20, 2026
Status: Tier 0 Installation Complete
Build: opensource-testing
EOF

# Update version in main menu
sudo nano /var/www/html/index.html
# Find footer section, update version display
```

#### Step A1.2: Set Tier to 3
```bash
# Update license.json
sudo nano /opt/d3kos/config/license.json
# Change: "tier": 2 → "tier": 3
# Change: "max_resets": 9999 → "max_resets": 9999 (already unlimited)
# Add: "testing_mode": true

# Restart tier services
sudo systemctl restart d3kos-tier-api
sudo systemctl restart d3kos-license-api

# Verify
curl http://localhost:8093/tier/status | jq .
# Should show: "tier": 3
```

#### Step A1.3: Update Settings Page
```bash
# Add version display to settings.html
sudo nano /var/www/html/settings.html
# Add section showing:
# - d3kOS Version: 0.9.1.2
# - Build Date: February 20, 2026
# - Tier: 3 (Testing Mode)
# - Installation ID: [from API]
```

**Verification**:
- [ ] `cat /opt/d3kos/config/license.json` shows version 0.9.1.2, tier 3
- [ ] Settings page displays correct version
- [ ] Tier API returns tier 3
- [ ] All Tier 3 features enabled (check feature flags)

**Testing**:
```bash
# Test tier detection
curl http://localhost:8093/tier/status

# Test license API
curl http://localhost:8091/license/info

# Check settings page
curl http://localhost/settings.html | grep -i version
```

---

### Task A2: Timezone Auto-Detection (3-4 hours)

#### Step A2.1: Create Detection Script
```bash
# Create /opt/d3kos/scripts/detect-timezone.sh
sudo mkdir -p /opt/d3kos/scripts
sudo nano /opt/d3kos/scripts/detect-timezone.sh
```

**Script Content**:
```bash
#!/bin/bash
# d3kOS Timezone Auto-Detection Script
# Version: 1.0
# Uses 3-tier fallback: GPS → Internet → UTC

set -e

TIMEZONE_FILE="/opt/d3kos/config/timezone.txt"
LOG_FILE="/opt/d3kos/logs/timezone-detection.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Tier 1: GPS Coordinate Detection
detect_gps_timezone() {
    log "Tier 1: Attempting GPS-based timezone detection..."

    # Wait up to 30 seconds for GPS fix
    for i in {1..30}; do
        GPS_DATA=$(curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/position 2>/dev/null || echo "")

        if echo "$GPS_DATA" | jq -e '.value.latitude' >/dev/null 2>&1; then
            LAT=$(echo "$GPS_DATA" | jq -r '.value.latitude')
            LON=$(echo "$GPS_DATA" | jq -r '.value.longitude')

            log "GPS fix acquired: $LAT, $LON"

            # Use timezonefinder library (install: pip3 install timezonefinder)
            TIMEZONE=$(python3 -c "from timezonefinder import TimezoneFinder; print(TimezoneFinder().timezone_at(lat=$LAT, lng=$LON))" 2>/dev/null || echo "")

            if [ -n "$TIMEZONE" ] && [ "$TIMEZONE" != "None" ]; then
                log "Timezone detected via GPS: $TIMEZONE"
                echo "$TIMEZONE"
                return 0
            fi
        fi

        sleep 1
    done

    log "GPS detection failed (no fix or invalid coordinates)"
    return 1
}

# Tier 2: Internet Geolocation
detect_internet_timezone() {
    log "Tier 2: Attempting internet-based timezone detection..."

    # Try worldtimeapi.org
    TIMEZONE=$(curl -s "http://worldtimeapi.org/api/ip" 2>/dev/null | jq -r '.timezone' 2>/dev/null || echo "")

    if [ -n "$TIMEZONE" ] && [ "$TIMEZONE" != "null" ]; then
        log "Timezone detected via internet (worldtimeapi): $TIMEZONE"
        echo "$TIMEZONE"
        return 0
    fi

    # Fallback: ip-api.com
    TIMEZONE=$(curl -s "http://ip-api.com/json/?fields=timezone" 2>/dev/null | jq -r '.timezone' 2>/dev/null || echo "")

    if [ -n "$TIMEZONE" ] && [ "$TIMEZONE" != "null" ]; then
        log "Timezone detected via internet (ip-api): $TIMEZONE"
        echo "$TIMEZONE"
        return 0
    fi

    log "Internet detection failed (no connection or invalid response)"
    return 1
}

# Tier 3: Default to UTC
detect_utc_fallback() {
    log "Tier 3: Using UTC fallback"
    echo "UTC"
    return 0
}

# Main detection flow
main() {
    log "=== d3kOS Timezone Auto-Detection Started ==="

    # Check if already configured
    if [ -f "$TIMEZONE_FILE" ]; then
        EXISTING=$(cat "$TIMEZONE_FILE")
        log "Timezone already configured: $EXISTING"
        log "Skipping auto-detection (remove $TIMEZONE_FILE to re-detect)"
        exit 0
    fi

    # Try GPS first
    if DETECTED_TZ=$(detect_gps_timezone); then
        TIMEZONE="$DETECTED_TZ"
    # Try internet second
    elif DETECTED_TZ=$(detect_internet_timezone); then
        TIMEZONE="$DETECTED_TZ"
    # Default to UTC
    else
        DETECTED_TZ=$(detect_utc_fallback)
        TIMEZONE="$DETECTED_TZ"
    fi

    # Apply timezone
    log "Setting system timezone to: $TIMEZONE"
    timedatectl set-timezone "$TIMEZONE" 2>&1 | tee -a "$LOG_FILE"

    # Save to config file
    echo "$TIMEZONE" > "$TIMEZONE_FILE"
    log "Timezone saved to $TIMEZONE_FILE"

    # Display current time
    CURRENT_TIME=$(date)
    log "Current time: $CURRENT_TIME"

    log "=== Timezone Auto-Detection Complete ==="
}

main "$@"
```

```bash
# Make executable
sudo chmod +x /opt/d3kos/scripts/detect-timezone.sh

# Install dependencies
sudo pip3 install timezonefinder
```

#### Step A2.2: Create Systemd Service
```bash
sudo nano /etc/systemd/system/d3kos-timezone-setup.service
```

**Service Content**:
```ini
[Unit]
Description=d3kOS Timezone Auto-Detection
After=network-online.target signalk.service
Wants=network-online.target
Before=d3kos-first-boot.service

[Service]
Type=oneshot
User=root
ExecStart=/opt/d3kos/scripts/detect-timezone.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Enable service
sudo systemctl daemon-reload
sudo systemctl enable d3kos-timezone-setup.service

# Test manually (remove existing config first)
sudo rm -f /opt/d3kos/config/timezone.txt
sudo /opt/d3kos/scripts/detect-timezone.sh

# Verify
cat /opt/d3kos/config/timezone.txt
timedatectl
```

#### Step A2.3: Add Manual Override to Settings
```bash
# Update settings.html
sudo nano /var/www/html/settings.html
```

**Add Timezone Section**:
```html
<!-- Add to Settings page -->
<div class="section">
    <h2>🌍 Timezone Configuration</h2>

    <div class="setting-row">
        <label>Current Timezone:</label>
        <span id="current-timezone">Loading...</span>
    </div>

    <div class="setting-row">
        <label>Detection Method:</label>
        <span id="timezone-method">Loading...</span>
    </div>

    <div class="setting-row">
        <label>Manual Override:</label>
        <select id="timezone-select">
            <option value="">Auto-Detect</option>
            <option value="America/Toronto">America/Toronto (EST/EDT)</option>
            <option value="America/New_York">America/New_York (EST/EDT)</option>
            <option value="America/Los_Angeles">America/Los_Angeles (PST/PDT)</option>
            <option value="Europe/London">Europe/London (GMT/BST)</option>
            <option value="UTC">UTC</option>
            <!-- Add more common timezones -->
        </select>
        <button onclick="setTimezone()">Set Timezone</button>
    </div>

    <div class="setting-row">
        <button onclick="redetectTimezone()">🔄 Re-Detect Timezone</button>
    </div>
</div>

<script>
// Load current timezone
async function loadTimezone() {
    try {
        const response = await fetch('/api/timezone');
        const data = await response.json();
        document.getElementById('current-timezone').textContent = data.timezone;
        document.getElementById('timezone-method').textContent = data.method;
    } catch (err) {
        document.getElementById('current-timezone').textContent = 'Error loading';
    }
}

// Manual override
async function setTimezone() {
    const timezone = document.getElementById('timezone-select').value;
    if (!timezone) {
        alert('Please select a timezone');
        return;
    }

    try {
        const response = await fetch('/api/timezone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ timezone })
        });

        if (response.ok) {
            alert('Timezone updated to ' + timezone);
            loadTimezone();
        }
    } catch (err) {
        alert('Error setting timezone: ' + err.message);
    }
}

// Re-detect
async function redetectTimezone() {
    if (!confirm('This will reset your timezone and re-detect automatically. Continue?')) {
        return;
    }

    try {
        const response = await fetch('/api/timezone/redetect', { method: 'POST' });
        if (response.ok) {
            alert('Timezone re-detection started. Page will reload in 5 seconds.');
            setTimeout(() => location.reload(), 5000);
        }
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

loadTimezone();
</script>
```

#### Step A2.4: Create Timezone API
```bash
# Create timezone API service
sudo nano /opt/d3kos/services/system/timezone-api.py
```

**API Content**:
```python
#!/usr/bin/env python3
"""
d3kOS Timezone API
Port: 8098
Endpoints: GET/POST /api/timezone, POST /api/timezone/redetect
"""

import json
import os
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TIMEZONE_FILE = '/opt/d3kos/config/timezone.txt'
DETECTION_SCRIPT = '/opt/d3kos/scripts/detect-timezone.sh'

@app.route('/api/timezone', methods=['GET'])
def get_timezone():
    """Get current timezone configuration"""
    try:
        # Read configured timezone
        if os.path.exists(TIMEZONE_FILE):
            with open(TIMEZONE_FILE, 'r') as f:
                timezone = f.read().strip()
        else:
            timezone = 'Not configured'

        # Get system timezone
        result = subprocess.run(['timedatectl', 'show', '--property=Timezone'],
                                capture_output=True, text=True)
        system_tz = result.stdout.strip().split('=')[1] if '=' in result.stdout else 'Unknown'

        # Determine detection method
        if timezone == 'UTC':
            method = 'Fallback (UTC)'
        elif timezone == system_tz:
            method = 'Auto-detected'
        else:
            method = 'Manual override'

        return jsonify({
            'success': True,
            'timezone': timezone,
            'system_timezone': system_tz,
            'method': method
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timezone', methods=['POST'])
def set_timezone():
    """Manually set timezone"""
    try:
        data = request.get_json()
        timezone = data.get('timezone', '').strip()

        if not timezone:
            return jsonify({'success': False, 'error': 'Timezone required'}), 400

        # Set system timezone
        result = subprocess.run(['timedatectl', 'set-timezone', timezone],
                                capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr}), 500

        # Save to config
        with open(TIMEZONE_FILE, 'w') as f:
            f.write(timezone)

        return jsonify({'success': True, 'timezone': timezone})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timezone/redetect', methods=['POST'])
def redetect_timezone():
    """Re-run auto-detection"""
    try:
        # Remove config file to trigger re-detection
        if os.path.exists(TIMEZONE_FILE):
            os.remove(TIMEZONE_FILE)

        # Run detection script
        result = subprocess.run([DETECTION_SCRIPT],
                                capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr}), 500

        return jsonify({'success': True, 'message': 'Timezone re-detected'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8098, debug=False)
```

```bash
# Make executable
sudo chmod +x /opt/d3kos/services/system/timezone-api.py

# Create systemd service
sudo nano /etc/systemd/system/d3kos-timezone-api.service
```

**Service**:
```ini
[Unit]
Description=d3kOS Timezone API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/d3kos/services/system
ExecStart=/usr/bin/python3 /opt/d3kos/services/system/timezone-api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable d3kos-timezone-api.service
sudo systemctl start d3kos-timezone-api.service

# Add nginx proxy
sudo nano /etc/nginx/sites-enabled/default
```

**Nginx Config** (add to existing server block):
```nginx
location /api/timezone {
    proxy_pass http://localhost:8098/api/timezone;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
}
```

```bash
# Reload nginx
sudo systemctl reload nginx

# Test API
curl http://localhost/api/timezone
```

**Verification**:
- [ ] Detection script runs without errors
- [ ] Timezone detected correctly (GPS, internet, or UTC)
- [ ] System timezone set correctly (`timedatectl`)
- [ ] Config file created at `/opt/d3kos/config/timezone.txt`
- [ ] Settings page displays timezone correctly
- [ ] Manual override works
- [ ] Re-detection works

**Testing**:
```bash
# Test GPS detection (if GPS available)
sudo rm /opt/d3kos/config/timezone.txt
sudo /opt/d3kos/scripts/detect-timezone.sh
cat /opt/d3kos/logs/timezone-detection.log

# Test internet detection (disable GPS)
# Simulate no GPS by stopping Signal K
sudo systemctl stop signalk
sudo rm /opt/d3kos/config/timezone.txt
sudo /opt/d3kos/scripts/detect-timezone.sh
sudo systemctl start signalk

# Test UTC fallback (no GPS, no internet)
# Disconnect internet, stop Signal K
sudo rm /opt/d3kos/config/timezone.txt
sudo /opt/d3kos/scripts/detect-timezone.sh

# Test manual override
curl -X POST http://localhost/api/timezone \
  -H "Content-Type: application/json" \
  -d '{"timezone":"America/Toronto"}'
```

---

### Task A3: Voice Assistant Fix (2-3 hours)

**Problem**: Wake word detection broken (PocketSphinx not detecting "HELM")
**Root Cause**: PipeWire reducing microphone signal by 17×
**Solution**: Systematic debugging + potential alternative wake word engine

#### Step A3.1: Investigate Current State
```bash
# Test microphone levels
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Direct hardware test
arecord -D plughw:3,0 -d 2 -f S16_LE -r 16000 /tmp/mic-test.wav
sox /tmp/mic-test.wav -n stat 2>&1 | grep "Maximum amplitude"

# Via PipeWire test
arecord -d 2 -f S16_LE -r 16000 /tmp/mic-pipewire.wav
sox /tmp/mic-pipewire.wav -n stat 2>&1 | grep "Maximum amplitude"

# Check PocketSphinx process
ps aux | grep pocketsphinx

# Check voice service logs
sudo journalctl -u d3kos-voice -n 100
```

#### Step A3.2: Try Vosk Wake Word (Alternative)
```bash
# Install Vosk
pip3 install vosk

# Download lightweight model
mkdir -p /opt/d3kos/models/vosk-wakeword
cd /opt/d3kos/models/vosk-wakeword
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model

# Create test script
nano /opt/d3kos/scripts/test-vosk-wakeword.py
```

**Test Script**:
```python
#!/usr/bin/env python3
import os
import sys
import pyaudio
import json
from vosk import Model, KaldiRecognizer

# Load model
model = Model("/opt/d3kos/models/vosk-wakeword/model")
rec = KaldiRecognizer(model, 16000)
rec.SetWords(True)

# Audio stream
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    input_device_index=None,  # Use default
    frames_per_buffer=4000
)

print("Listening for 'helm'...")

try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get('text', '').lower()

            if 'helm' in text:
                print(f"✓ Wake word detected: {text}")
        else:
            partial = json.loads(rec.PartialResult())
            partial_text = partial.get('partial', '').lower()

            if 'helm' in partial_text:
                print(f"⚠ Partial match: {partial_text}")

except KeyboardInterrupt:
    print("\nStopped")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
```

```bash
# Test Vosk wake word
python3 /opt/d3kos/scripts/test-vosk-wakeword.py
# Say "HELM" several times, check detection rate
```

#### Step A3.3: Implement Solution (Based on Test Results)

**Option 1: Fix PocketSphinx with Direct Hardware**
```bash
# If direct hardware access works, update voice service
sudo nano /opt/d3kos/services/voice/voice-assistant-hybrid.py

# Change:
# ["-inmic", "yes",...]
# To:
# ["-adcdev", "plughw:3,0",...]

# Restart service
sudo systemctl restart d3kos-voice
```

**Option 2: Switch to Vosk Wake Word** (if PocketSphinx unfixable)
```bash
# Update voice assistant to use Vosk
sudo cp /opt/d3kos/services/voice/voice-assistant-hybrid.py \
       /opt/d3kos/services/voice/voice-assistant-hybrid.py.bak.pocketsphinx

# Replace wake word detection code with Vosk implementation
# (Full code update needed - 200+ lines)

# Restart service
sudo systemctl restart d3kos-voice
```

**Verification**:
- [ ] Wake word detection rate > 95% (say "HELM" 20 times, should detect 19+)
- [ ] False positive rate < 5% (30 seconds silence, max 1-2 false detections)
- [ ] Response time < 2 seconds (wake word → "Aye Aye Captain")
- [ ] Service starts automatically on boot
- [ ] No PipeWire interference

**Testing**:
```bash
# Detection rate test
# Say "HELM" 20 times, count detections
sudo journalctl -u d3kos-voice -f

# False positive test
# Remain silent for 60 seconds, count false detections

# Response time test
# Measure time from "HELM" to response start

# Integration test
# Test full voice query: "Helm, what's the RPM?"
```

---

### Task A4: Documentation & Commit (1 hour)

#### Step A4.1: Create Session A Summary Document
```bash
# On local machine (Ubuntu)
cd /home/boatiq/Helm-OS/doc
nano SESSION_A_FOUNDATION_COMPLETE.md
```

**Document Content**:
```markdown
# Session A: Foundation & Critical Fixes - COMPLETE

**Date**: [Fill in]
**Duration**: [Fill in]
**Status**: ✅ COMPLETE

## Summary

Completed foundational updates for d3kOS v0.9.1.2:
- Version updated to 0.9.1.2
- Tier set to 3 for testing
- Timezone auto-detection implemented
- Voice assistant wake word detection fixed

## Changes Made

### 1. Version & Tier Update
- Updated `/opt/d3kos/config/license.json`: version 0.9.1.2, tier 3
- Created `/opt/d3kos/config/version.txt`
- Updated settings.html with version display
- Verified all Tier 3 features enabled

### 2. Timezone Auto-Detection
- Created `/opt/d3kos/scripts/detect-timezone.sh` (3-tier: GPS → Internet → UTC)
- Created `d3kos-timezone-setup.service` (first-boot)
- Created timezone API service (port 8098)
- Added manual override to settings page
- Installed timezonefinder library

### 3. Voice Assistant Fix
- [Describe solution implemented]
- [Detection rate achieved: X%]
- [False positive rate: X%]
- [Response time: X seconds]

## Files Modified

**On Raspberry Pi:**
- `/opt/d3kos/config/license.json`
- `/opt/d3kos/config/version.txt` (new)
- `/opt/d3kos/scripts/detect-timezone.sh` (new)
- `/etc/systemd/system/d3kos-timezone-setup.service` (new)
- `/opt/d3kos/services/system/timezone-api.py` (new)
- `/etc/systemd/system/d3kos-timezone-api.service` (new)
- `/var/www/html/settings.html`
- `/etc/nginx/sites-enabled/default`
- `/opt/d3kos/services/voice/voice-assistant-hybrid.py`

**On Local Machine:**
- `/home/boatiq/Helm-OS/doc/SESSION_A_FOUNDATION_COMPLETE.md` (this file)

## Testing Results

### Version & Tier
- [X] License API returns version 0.9.1.2
- [X] Tier API returns tier 3
- [X] Settings page displays correct version
- [X] All Tier 3 features enabled

### Timezone Auto-Detection
- [X] GPS detection works (if GPS available)
- [X] Internet detection works (if online)
- [X] UTC fallback works (if offline)
- [X] Manual override works
- [X] Settings page displays timezone

### Voice Assistant
- [X] Wake word detection rate > 95%
- [X] False positive rate < 5%
- [X] Response time < 2 seconds
- [X] Auto-start on boot

## Next Steps

Session A complete. Ready to proceed with:
- Session B: Self-Healing System
- Session C: Data Export Queue
- Session D: Backup & Image Build

All sessions can now run in parallel.
```

#### Step A4.2: Update MASTER_SYSTEM_SPEC.md
```bash
# Update spec with implementation status
nano /home/boatiq/Helm-OS/MASTER_SYSTEM_SPEC.md
```

**Changes**:
```markdown
# Update version history table at top:
| 3.6 | 2026-02-20 | d3kOS Team | Implemented Timezone Auto-Detection (Section 4.1.4), fixed voice assistant wake word detection, updated version to 0.9.1.2, set tier to 3 for testing |

# Update Section 4.1.4 - Add implementation note:
**Implementation Status**: ✅ COMPLETE (February 20, 2026)
- Script: `/opt/d3kos/scripts/detect-timezone.sh`
- Service: `d3kos-timezone-setup.service`
- API: Port 8098
- Settings UI: Manual override available

# Update Section 6.3.1 - License version:
"version": "0.9.1.2",  # Was 1.0.3
"tier": 3,  # Was 2
"testing_mode": true  # New field
```

#### Step A4.3: Commit to Git
```bash
cd /home/boatiq/Helm-OS

# Check git status
git status

# Add modified files
git add MASTER_SYSTEM_SPEC.md
git add doc/SESSION_A_FOUNDATION_COMPLETE.md

# Commit
git commit -m "Session A: Version 0.9.1.2, Tier 3, Timezone Auto-Detection, Voice Fix

- Updated system version to 0.9.1.2
- Set tier to 3 for testing mode
- Implemented timezone auto-detection (GPS → Internet → UTC fallback)
- Created timezone API service (port 8098)
- Added manual timezone override to settings
- Fixed voice assistant wake word detection
- All changes verified and tested

Closes: Foundation updates for v0.9.1.2 release
See: doc/SESSION_A_FOUNDATION_COMPLETE.md"

# Push to local repo (don't push to GitHub yet - wait for all sessions)
git push origin main
```

**Verification**:
- [ ] All modified files committed
- [ ] Commit message follows convention
- [ ] Documentation updated
- [ ] Session summary created
- [ ] Changes pushed to local repo

---

## SESSION B: SELF-HEALING SYSTEM

**Owner**: Parallel session (after Session A)
**Domain**: System Intelligence, Health Monitoring
**Duration**: 6-8 hours
**Dependencies**: Session A complete (requires tier 3 enabled)

### Objectives
1. ✅ Implement AI-powered self-healing (Section 6.4)
2. ✅ Create detection layer (engine anomalies, Pi health)
3. ✅ Create correlation engine
4. ✅ Integrate AI diagnosis
5. ✅ Implement safe auto-remediation
6. ✅ Create user notifications
7. ✅ Test and verify
8. ✅ Document updates
9. ✅ Commit to git

---

### Task B1: Self-Healing Detection Layer (2-3 hours)

#### Step B1.1: Create Issue Detection Service
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Create detection service
sudo mkdir -p /opt/d3kos/services/self-healing
sudo nano /opt/d3kos/services/self-healing/issue_detector.py
```

**Detection Service** (`issue_detector.py`):
```python
#!/usr/bin/env python3
"""
d3kOS Issue Detection Service
Monitors engine and Pi health, detects anomalies
"""

import time
import json
import sqlite3
import requests
import subprocess
from datetime import datetime, timedelta

# Database for issue tracking
DB_PATH = '/opt/d3kos/data/self-healing/issues.db'
SIGNALK_API = 'http://localhost:3000/signalk/v1/api'

class IssueDetector:
    def __init__(self):
        self.init_database()

    def init_database(self):
        """Create issues database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                raw_data TEXT,
                status TEXT DEFAULT 'detected',
                correlation_id TEXT,
                ai_diagnosis TEXT,
                remediation_action TEXT,
                resolved_at TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_history (
                timestamp TEXT PRIMARY KEY,
                cpu_temp REAL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                rpm INTEGER,
                oil_pressure REAL,
                coolant_temp REAL
            )
        ''')

        conn.commit()
        conn.close()

    def detect_engine_anomalies(self):
        """Check for engine health issues"""
        issues = []

        try:
            # Get current engine data
            response = requests.get(f'{SIGNALK_API}/vessels/self/propulsion/port', timeout=2)
            engine_data = response.json()

            rpm = engine_data.get('revolutions', {}).get('value', 0)
            if rpm:
                rpm = int(rpm * 60)  # Convert to RPM

            oil_pressure = engine_data.get('oilPressure', {}).get('value')
            coolant_temp = engine_data.get('coolantTemperature', {}).get('value')
            boost = engine_data.get('boostPressure', {}).get('value')

            # Rule-based anomaly detection

            # Low oil pressure (engine running)
            if rpm > 500 and oil_pressure and oil_pressure < 20:
                issues.append({
                    'category': 'engine',
                    'severity': 'critical',
                    'description': f'Low oil pressure: {oil_pressure:.1f} PSI at {rpm} RPM',
                    'raw_data': json.dumps(engine_data)
                })

            # High coolant temperature
            if coolant_temp and coolant_temp > 105:  # >105°C
                issues.append({
                    'category': 'engine',
                    'severity': 'critical' if coolant_temp > 110 else 'warning',
                    'description': f'High coolant temperature: {coolant_temp:.1f}°C',
                    'raw_data': json.dumps(engine_data)
                })

            # High boost pressure (turbo overboost)
            if boost and boost > 200000:  # >2 bar
                issues.append({
                    'category': 'engine',
                    'severity': 'warning',
                    'description': f'High boost pressure: {boost/1000:.1f} kPa',
                    'raw_data': json.dumps(engine_data)
                })

            # Statistical anomaly detection
            issues.extend(self.detect_statistical_anomalies('rpm', rpm))
            issues.extend(self.detect_statistical_anomalies('oil_pressure', oil_pressure))

        except Exception as e:
            print(f"Error detecting engine anomalies: {e}")

        return issues

    def detect_pi_health_issues(self):
        """Check for Raspberry Pi health issues"""
        issues = []

        try:
            # CPU temperature
            temp_result = subprocess.run(['vcgencmd', 'measure_temp'],
                                          capture_output=True, text=True)
            cpu_temp = float(temp_result.stdout.strip().split('=')[1].replace("'C", ""))

            if cpu_temp > 80:
                issues.append({
                    'category': 'pi_health',
                    'severity': 'critical' if cpu_temp > 85 else 'warning',
                    'description': f'High CPU temperature: {cpu_temp:.1f}°C',
                    'raw_data': json.dumps({'cpu_temp': cpu_temp})
                })

            # Memory usage
            mem_result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            mem_lines = mem_result.stdout.strip().split('\n')[1].split()
            mem_used = int(mem_lines[2])
            mem_total = int(mem_lines[1])
            mem_percent = (mem_used / mem_total) * 100

            if mem_percent > 90:
                issues.append({
                    'category': 'pi_health',
                    'severity': 'warning',
                    'description': f'High memory usage: {mem_percent:.1f}%',
                    'raw_data': json.dumps({'mem_percent': mem_percent})
                })

            # Disk usage
            disk_result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            disk_percent = int(disk_result.stdout.strip().split('\n')[1].split()[4].replace('%', ''))

            if disk_percent > 90:
                issues.append({
                    'category': 'pi_health',
                    'severity': 'critical' if disk_percent > 95 else 'warning',
                    'description': f'High disk usage: {disk_percent}%',
                    'raw_data': json.dumps({'disk_percent': disk_percent})
                })

            # Service status
            critical_services = [
                'd3kos-license-api',
                'd3kos-tier-api',
                'd3kos-health',
                'signalk',
                'nodered',
                'nginx'
            ]

            for service in critical_services:
                result = subprocess.run(['systemctl', 'is-active', service],
                                        capture_output=True, text=True)
                status = result.stdout.strip()

                if status != 'active':
                    issues.append({
                        'category': 'service_failure',
                        'severity': 'critical',
                        'description': f'Service {service} is {status}',
                        'raw_data': json.dumps({'service': service, 'status': status})
                    })

            # Save health metrics to history
            self.save_health_history({
                'cpu_temp': cpu_temp,
                'memory_usage': mem_percent,
                'disk_usage': disk_percent
            })

        except Exception as e:
            print(f"Error detecting Pi health issues: {e}")

        return issues

    def detect_statistical_anomalies(self, metric, current_value):
        """Detect anomalies using statistical process control"""
        issues = []

        if current_value is None:
            return issues

        try:
            # Get historical data (last 100 readings)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute(f'''
                SELECT {metric} FROM health_history
                WHERE {metric} IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 100
            ''')

            history = [row[0] for row in cursor.fetchall()]
            conn.close()

            if len(history) < 30:
                return issues  # Not enough data

            # Calculate mean and standard deviation
            mean = sum(history) / len(history)
            variance = sum((x - mean) ** 2 for x in history) / len(history)
            std_dev = variance ** 0.5

            # 3-sigma rule
            deviation = abs(current_value - mean)
            if deviation > 3 * std_dev:
                issues.append({
                    'category': 'statistical_anomaly',
                    'severity': 'warning',
                    'description': f'{metric} anomaly: {current_value:.1f} (mean: {mean:.1f}, σ: {std_dev:.1f})',
                    'raw_data': json.dumps({
                        'metric': metric,
                        'current': current_value,
                        'mean': mean,
                        'std_dev': std_dev,
                        'deviation': deviation
                    })
                })

        except Exception as e:
            print(f"Error in statistical anomaly detection: {e}")

        return issues

    def save_health_history(self, metrics):
        """Save current health metrics to history"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO health_history (timestamp, cpu_temp, cpu_usage, memory_usage, disk_usage)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                metrics.get('cpu_temp'),
                metrics.get('cpu_usage'),
                metrics.get('memory_usage'),
                metrics.get('disk_usage')
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving health history: {e}")

    def save_issue(self, issue):
        """Save detected issue to database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO issues (timestamp, category, severity, description, raw_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                issue['category'],
                issue['severity'],
                issue['description'],
                issue['raw_data']
            ))

            issue_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return issue_id
        except Exception as e:
            print(f"Error saving issue: {e}")
            return None

    def run(self):
        """Main detection loop"""
        print("🔍 d3kOS Issue Detector started")

        while True:
            try:
                # Detect engine issues
                engine_issues = self.detect_engine_anomalies()
                for issue in engine_issues:
                    issue_id = self.save_issue(issue)
                    print(f"⚠ Issue detected #{issue_id}: {issue['description']}")

                # Detect Pi health issues
                pi_issues = self.detect_pi_health_issues()
                for issue in pi_issues:
                    issue_id = self.save_issue(issue)
                    print(f"⚠ Issue detected #{issue_id}: {issue['description']}")

                # Sleep 10 seconds between checks
                time.sleep(10)

            except KeyboardInterrupt:
                print("\n🛑 Issue detector stopped")
                break
            except Exception as e:
                print(f"Error in detection loop: {e}")
                time.sleep(10)

if __name__ == '__main__':
    detector = IssueDetector()
    detector.run()
```

```bash
# Make executable
sudo chmod +x /opt/d3kos/services/self-healing/issue_detector.py

# Create data directory
sudo mkdir -p /opt/d3kos/data/self-healing

# Create systemd service
sudo nano /etc/systemd/system/d3kos-issue-detector.service
```

**Service**:
```ini
[Unit]
Description=d3kOS Issue Detection Service
After=network.target signalk.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/self-healing
ExecStart=/usr/bin/python3 /opt/d3kos/services/self-healing/issue_detector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable d3kos-issue-detector.service
sudo systemctl start d3kos-issue-detector.service

# Check status
sudo systemctl status d3kos-issue-detector
sudo journalctl -u d3kos-issue-detector -f
```

**Verification**:
- [ ] Service starts without errors
- [ ] Database created at `/opt/d3kos/data/self-healing/issues.db`
- [ ] Engine anomalies detected (simulate low oil pressure)
- [ ] Pi health issues detected (simulate high disk usage)
- [ ] Statistical anomalies detected after baseline established

---

### Task B2: Self-Healing Remediation Layer (2-3 hours)

#### Step B2.1: Create Remediation Service
```bash
sudo nano /opt/d3kos/services/self-healing/remediation_engine.py
```

**Remediation Service**:
```python
#!/usr/bin/env python3
"""
d3kOS Remediation Engine
Automatically fixes detected issues with safe actions
"""

import time
import json
import sqlite3
import subprocess
import requests
from datetime import datetime

DB_PATH = '/opt/d3kos/data/self-healing/issues.db'
AI_API = 'http://localhost:8080/ai/query'

class RemediationEngine:
    def __init__(self):
        self.safe_actions = {
            'service_failure': self.restart_service,
            'high_disk_usage': self.cleanup_disk,
            'stuck_process': self.kill_stuck_process,
            'high_memory_usage': self.clear_caches,
            'high_cpu_temp': self.throttle_services
        }

    def get_pending_issues(self):
        """Get issues that need remediation"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT issue_id, category, severity, description, raw_data
            FROM issues
            WHERE status = 'detected'
            AND remediation_action IS NULL
            ORDER BY
                CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'warning' THEN 2
                    ELSE 3
                END,
                timestamp ASC
        ''')

        issues = []
        for row in cursor.fetchall():
            issues.append({
                'issue_id': row[0],
                'category': row[1],
                'severity': row[2],
                'description': row[3],
                'raw_data': json.loads(row[4]) if row[4] else {}
            })

        conn.close()
        return issues

    def diagnose_with_ai(self, issue):
        """Use AI to diagnose root cause"""
        try:
            prompt = f"""Analyze this system issue and provide a diagnosis:

Category: {issue['category']}
Severity: {issue['severity']}
Description: {issue['description']}
Raw Data: {json.dumps(issue['raw_data'], indent=2)}

Provide:
1. Root cause analysis
2. Recommended remediation action
3. Risk level (low/medium/high)

Keep response concise (2-3 sentences).
"""

            response = requests.post(AI_API,
                                     json={'question': prompt, 'provider': 'openrouter'},
                                     timeout=15)

            if response.status_code == 200:
                data = response.json()
                return data.get('answer', 'AI diagnosis unavailable')
            else:
                return 'AI diagnosis failed'
        except Exception as e:
            print(f"AI diagnosis error: {e}")
            return f'AI diagnosis error: {str(e)}'

    def restart_service(self, issue):
        """Safely restart a failed service"""
        try:
            service_name = issue['raw_data'].get('service')
            if not service_name:
                return {'success': False, 'message': 'No service name provided'}

            # Don't restart critical system services automatically
            protected_services = ['systemd', 'dbus', 'sshd']
            if service_name in protected_services:
                return {
                    'success': False,
                    'message': f'Protected service {service_name} - manual intervention required'
                }

            # Restart service
            result = subprocess.run(['systemctl', 'restart', service_name],
                                    capture_output=True, text=True)

            if result.returncode == 0:
                # Wait 5 seconds and verify
                time.sleep(5)
                verify = subprocess.run(['systemctl', 'is-active', service_name],
                                        capture_output=True, text=True)

                if verify.stdout.strip() == 'active':
                    return {
                        'success': True,
                        'message': f'Service {service_name} restarted successfully'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Service {service_name} failed to start after restart'
                    }
            else:
                return {
                    'success': False,
                    'message': f'Failed to restart {service_name}: {result.stderr}'
                }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def cleanup_disk(self, issue):
        """Free up disk space safely"""
        try:
            actions_taken = []

            # Clear APT cache
            result = subprocess.run(['apt-get', 'clean'], capture_output=True, text=True)
            if result.returncode == 0:
                actions_taken.append('Cleared APT cache')

            # Clear journal logs older than 7 days
            result = subprocess.run(['journalctl', '--vacuum-time=7d'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                actions_taken.append('Cleaned old journal logs')

            # Delete old camera recordings (keep last 7 days)
            recordings_dir = '/home/d3kos/camera-recordings'
            result = subprocess.run([
                'find', recordings_dir, '-name', '*.mp4', '-mtime', '+7', '-delete'
            ], capture_output=True, text=True)
            if result.returncode == 0:
                actions_taken.append('Deleted old camera recordings')

            # Clear temp files
            result = subprocess.run(['rm', '-rf', '/tmp/*'],
                                    capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                actions_taken.append('Cleared /tmp/')

            return {
                'success': True,
                'message': f'Disk cleanup complete: {", ".join(actions_taken)}'
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def kill_stuck_process(self, issue):
        """Kill stuck/zombie processes"""
        try:
            process_name = issue['raw_data'].get('process')
            if not process_name:
                return {'success': False, 'message': 'No process name provided'}

            # Find process ID
            result = subprocess.run(['pgrep', process_name],
                                    capture_output=True, text=True)

            if result.returncode != 0 or not result.stdout.strip():
                return {
                    'success': False,
                    'message': f'Process {process_name} not found'
                }

            pid = result.stdout.strip().split('\n')[0]

            # Try SIGTERM first (graceful)
            subprocess.run(['kill', '-15', pid], capture_output=True, text=True)
            time.sleep(2)

            # Check if still running
            verify = subprocess.run(['pgrep', process_name],
                                    capture_output=True, text=True)

            if verify.returncode != 0:
                return {
                    'success': True,
                    'message': f'Process {process_name} (PID {pid}) terminated gracefully'
                }

            # Force kill with SIGKILL
            subprocess.run(['kill', '-9', pid], capture_output=True, text=True)

            return {
                'success': True,
                'message': f'Process {process_name} (PID {pid}) force killed'
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def clear_caches(self, issue):
        """Clear system caches to free memory"""
        try:
            # Drop page cache
            with open('/proc/sys/vm/drop_caches', 'w') as f:
                f.write('1\n')

            return {
                'success': True,
                'message': 'System caches cleared'
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def throttle_services(self, issue):
        """Reduce CPU load to cool down"""
        try:
            actions_taken = []

            # Stop non-critical services temporarily
            non_critical = ['d3kos-fish-detector']

            for service in non_critical:
                result = subprocess.run(['systemctl', 'stop', service],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    actions_taken.append(f'Stopped {service}')

            return {
                'success': True,
                'message': f'CPU throttling applied: {", ".join(actions_taken)}'
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def apply_remediation(self, issue):
        """Apply remediation action for an issue"""
        category = issue['category']

        # Get AI diagnosis first (Tier 3 only)
        ai_diagnosis = self.diagnose_with_ai(issue)

        # Update issue with diagnosis
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE issues SET ai_diagnosis = ? WHERE issue_id = ?',
                       (ai_diagnosis, issue['issue_id']))
        conn.commit()
        conn.close()

        # Check if we have a safe action for this category
        if category not in self.safe_actions:
            print(f"⚠ No safe remediation for {category}, manual intervention required")
            return {
                'success': False,
                'message': f'No automated remediation available for {category}'
            }

        # Apply remediation
        print(f"🔧 Applying remediation for issue #{issue['issue_id']}: {issue['description']}")
        action_func = self.safe_actions[category]
        result = action_func(issue)

        # Update issue status
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if result['success']:
            cursor.execute('''
                UPDATE issues
                SET status = 'resolved',
                    remediation_action = ?,
                    resolved_at = ?
                WHERE issue_id = ?
            ''', (result['message'], datetime.now().isoformat(), issue['issue_id']))
            print(f"✅ Remediation successful: {result['message']}")
        else:
            cursor.execute('''
                UPDATE issues
                SET status = 'remediation_failed',
                    remediation_action = ?
                WHERE issue_id = ?
            ''', (result['message'], issue['issue_id']))
            print(f"❌ Remediation failed: {result['message']}")

        conn.commit()
        conn.close()

        return result

    def run(self):
        """Main remediation loop"""
        print("🔧 d3kOS Remediation Engine started")

        while True:
            try:
                # Get pending issues
                issues = self.get_pending_issues()

                if issues:
                    print(f"\n📋 Found {len(issues)} pending issue(s)")

                    for issue in issues:
                        self.apply_remediation(issue)

                # Sleep 30 seconds between checks
                time.sleep(30)

            except KeyboardInterrupt:
                print("\n🛑 Remediation engine stopped")
                break
            except Exception as e:
                print(f"Error in remediation loop: {e}")
                time.sleep(30)

if __name__ == '__main__':
    engine = RemediationEngine()
    engine.run()
```

```bash
# Make executable
sudo chmod +x /opt/d3kos/services/self-healing/remediation_engine.py

# Create systemd service
sudo nano /etc/systemd/system/d3kos-remediation.service
```

**Service**:
```ini
[Unit]
Description=d3kOS Remediation Engine
After=network.target d3kos-issue-detector.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/d3kos/services/self-healing
ExecStart=/usr/bin/python3 /opt/d3kos/services/self-healing/remediation_engine.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable d3kos-remediation.service
sudo systemctl start d3kos-remediation.service

# Check status
sudo systemctl status d3kos-remediation
sudo journalctl -u d3kos-remediation -f
```

**Verification**:
- [ ] Service starts without errors
- [ ] Pending issues are processed
- [ ] Safe actions execute correctly
- [ ] AI diagnosis integrated (Tier 3)
- [ ] Issue status updated to 'resolved' or 'remediation_failed'

---

### Task B3: Self-Healing API & UI (1-2 hours)

#### Step B3.1: Create Self-Healing API
```bash
sudo nano /opt/d3kos/services/self-healing/self_healing_api.py
```

**API**:
```python
#!/usr/bin/env python3
"""
d3kOS Self-Healing API
Port: 8099
Endpoints: /healing/issues, /healing/history, /healing/stats
"""

import json
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DB_PATH = '/opt/d3kos/data/self-healing/issues.db'

@app.route('/healing/issues', methods=['GET'])
def get_issues():
    """Get current unresolved issues"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT issue_id, timestamp, category, severity, description,
                   status, ai_diagnosis, remediation_action
            FROM issues
            WHERE status IN ('detected', 'remediation_failed')
            ORDER BY
                CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'warning' THEN 2
                    ELSE 3
                END,
                timestamp DESC
        ''')

        issues = []
        for row in cursor.fetchall():
            issues.append({
                'issue_id': row[0],
                'timestamp': row[1],
                'category': row[2],
                'severity': row[3],
                'description': row[4],
                'status': row[5],
                'ai_diagnosis': row[6],
                'remediation_action': row[7]
            })

        conn.close()

        return jsonify({'success': True, 'issues': issues, 'count': len(issues)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/healing/history', methods=['GET'])
def get_history():
    """Get resolved issues history"""
    try:
        days = int(request.args.get('days', 7))

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        since = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute('''
            SELECT issue_id, timestamp, category, severity, description,
                   remediation_action, resolved_at
            FROM issues
            WHERE status = 'resolved'
            AND timestamp >= ?
            ORDER BY resolved_at DESC
        ''', (since,))

        history = []
        for row in cursor.fetchall():
            history.append({
                'issue_id': row[0],
                'timestamp': row[1],
                'category': row[2],
                'severity': row[3],
                'description': row[4],
                'remediation_action': row[5],
                'resolved_at': row[6]
            })

        conn.close()

        return jsonify({'success': True, 'history': history, 'count': len(history)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/healing/stats', methods=['GET'])
def get_stats():
    """Get self-healing statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Total issues detected
        cursor.execute('SELECT COUNT(*) FROM issues')
        total_issues = cursor.fetchone()[0]

        # Resolved issues
        cursor.execute("SELECT COUNT(*) FROM issues WHERE status = 'resolved'")
        resolved_issues = cursor.fetchone()[0]

        # Failed remediations
        cursor.execute("SELECT COUNT(*) FROM issues WHERE status = 'remediation_failed'")
        failed_remediations = cursor.fetchone()[0]

        # Pending issues
        cursor.execute("SELECT COUNT(*) FROM issues WHERE status = 'detected'")
        pending_issues = cursor.fetchone()[0]

        # Issues by category
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM issues
            GROUP BY category
            ORDER BY count DESC
        ''')
        by_category = {row[0]: row[1] for row in cursor.fetchall()}

        # Issues by severity
        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM issues
            GROUP BY severity
        ''')
        by_severity = {row[0]: row[1] for row in cursor.fetchall()}

        # Success rate
        success_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0

        conn.close()

        return jsonify({
            'success': True,
            'stats': {
                'total_issues': total_issues,
                'resolved': resolved_issues,
                'failed': failed_remediations,
                'pending': pending_issues,
                'success_rate': round(success_rate, 1),
                'by_category': by_category,
                'by_severity': by_severity
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099, debug=False)
```

```bash
# Make executable
sudo chmod +x /opt/d3kos/services/self-healing/self_healing_api.py

# Create systemd service
sudo nano /etc/systemd/system/d3kos-healing-api.service
```

**Service**:
```ini
[Unit]
Description=d3kOS Self-Healing API
After=network.target

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/self-healing
ExecStart=/usr/bin/python3 /opt/d3kos/services/self-healing/self_healing_api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable d3kos-healing-api.service
sudo systemctl start d3kos-healing-api.service

# Add nginx proxy
sudo nano /etc/nginx/sites-enabled/default
```

**Nginx Config**:
```nginx
location /healing/ {
    proxy_pass http://localhost:8099/healing/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
}
```

```bash
sudo systemctl reload nginx

# Test API
curl http://localhost/healing/issues
curl http://localhost/healing/stats
```

#### Step B3.2: Add Self-Healing UI to Settings
```bash
sudo nano /var/www/html/settings-healing.html
```

**UI Page** (abbreviated - 200+ lines total):
```html
<!DOCTYPE html>
<html>
<head>
    <title>Self-Healing Status - d3kOS</title>
    <style>
        body {
            background: #000;
            color: #fff;
            font-family: Arial;
            font-size: 22px;
        }
        .header {
            background: #00CC00;
            color: #000;
            padding: 20px;
            font-size: 32px;
            font-weight: bold;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px;
        }
        .stat-card {
            background: #1a1a1a;
            padding: 20px;
            border: 2px solid #00CC00;
            border-radius: 10px;
        }
        .stat-value {
            font-size: 48px;
            font-weight: bold;
            color: #00CC00;
        }
        .issue {
            background: #1a1a1a;
            margin: 10px 20px;
            padding: 20px;
            border-left: 5px solid #ff0000;
        }
        .issue.warning {
            border-left-color: #ffaa00;
        }
        .issue.resolved {
            border-left-color: #00CC00;
        }
    </style>
</head>
<body>
    <div class="header">🛡️ Self-Healing System</div>

    <div class="stats" id="stats">
        <!-- Populated by JS -->
    </div>

    <h2 style="margin: 20px;">Current Issues</h2>
    <div id="current-issues">
        <!-- Populated by JS -->
    </div>

    <h2 style="margin: 20px;">Recent History (Last 7 Days)</h2>
    <div id="history">
        <!-- Populated by JS -->
    </div>

    <script>
        async function loadStats() {
            const response = await fetch('/healing/stats');
            const data = await response.json();

            if (data.success) {
                const stats = data.stats;
                document.getElementById('stats').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_issues}</div>
                        <div>Total Issues</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.resolved}</div>
                        <div>Resolved</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.pending}</div>
                        <div>Pending</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.success_rate}%</div>
                        <div>Success Rate</div>
                    </div>
                `;
            }
        }

        async function loadIssues() {
            const response = await fetch('/healing/issues');
            const data = await response.json();

            if (data.success) {
                const container = document.getElementById('current-issues');
                if (data.issues.length === 0) {
                    container.innerHTML = '<p style="margin: 20px;">✅ No current issues</p>';
                } else {
                    container.innerHTML = data.issues.map(issue => `
                        <div class="issue ${issue.severity}">
                            <strong>${issue.description}</strong><br>
                            <small>Category: ${issue.category} | Severity: ${issue.severity}</small><br>
                            <small>Detected: ${new Date(issue.timestamp).toLocaleString()}</small><br>
                            ${issue.ai_diagnosis ? `<p>AI Diagnosis: ${issue.ai_diagnosis}</p>` : ''}
                            ${issue.remediation_action ? `<p>Action: ${issue.remediation_action}</p>` : ''}
                        </div>
                    `).join('');
                }
            }
        }

        async function loadHistory() {
            const response = await fetch('/healing/history?days=7');
            const data = await response.json();

            if (data.success) {
                const container = document.getElementById('history');
                container.innerHTML = data.history.slice(0, 10).map(issue => `
                    <div class="issue resolved">
                        <strong>${issue.description}</strong><br>
                        <small>Remediation: ${issue.remediation_action}</small><br>
                        <small>Resolved: ${new Date(issue.resolved_at).toLocaleString()}</small>
                    </div>
                `).join('');
            }
        }

        loadStats();
        loadIssues();
        loadHistory();

        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadStats();
            loadIssues();
            loadHistory();
        }, 30000);
    </script>
</body>
</html>
```

```bash
# Add link to main settings page
sudo nano /var/www/html/settings.html
# Add button: "🛡️ Self-Healing Status" → /settings-healing.html
```

**Verification**:
- [ ] API returns issues, history, and stats
- [ ] Settings page displays self-healing status
- [ ] Stats update in real-time
- [ ] Issue cards show correct severity colors
- [ ] History shows resolved issues

---

### Task B4: Documentation & Commit (1 hour)

```bash
# Create session summary
cd /home/boatiq/Helm-OS/doc
nano SESSION_B_SELF_HEALING_COMPLETE.md
```

**Summary Document** (abbreviated):
```markdown
# Session B: Self-Healing System - COMPLETE

**Date**: [Fill in]
**Duration**: [Fill in]
**Status**: ✅ COMPLETE

## Summary

Implemented AI-powered self-healing system per spec Section 6.4:
- Issue detection layer (engine + Pi health)
- AI diagnosis integration
- Safe auto-remediation actions
- User notification system
- History tracking and statistics

## Changes Made

### Services Created
1. Issue Detector (`d3kos-issue-detector.service`, port N/A)
2. Remediation Engine (`d3kos-remediation.service`, port N/A)
3. Self-Healing API (`d3kos-healing-api.service`, port 8099)

### Detection Capabilities
- Engine anomalies (low oil, high temp, overboost)
- Statistical anomalies (3-sigma rule)
- Pi health issues (CPU temp, memory, disk, services)
- Service failures

### Remediation Actions
- Restart failed services
- Cleanup disk space
- Kill stuck processes
- Clear caches
- Throttle CPU load

### AI Integration
- Root cause analysis (Tier 3 only)
- Recommended remediation
- Risk assessment

## Files Created

**On Raspberry Pi:**
- `/opt/d3kos/services/self-healing/issue_detector.py`
- `/opt/d3kos/services/self-healing/remediation_engine.py`
- `/opt/d3kos/services/self-healing/self_healing_api.py`
- `/etc/systemd/system/d3kos-issue-detector.service`
- `/etc/systemd/system/d3kos-remediation.service`
- `/etc/systemd/system/d3kos-healing-api.service`
- `/opt/d3kos/data/self-healing/issues.db`
- `/var/www/html/settings-healing.html`

## Testing Results

### Detection
- [X] Engine anomalies detected (simulated low oil pressure)
- [X] Pi health issues detected (simulated high disk)
- [X] Statistical anomalies detected after baseline
- [X] Service failures detected

### Remediation
- [X] Service restart works
- [X] Disk cleanup frees space
- [X] Stuck processes killed
- [X] Caches cleared
- [X] CPU throttling applied

### AI Diagnosis (Tier 3)
- [X] Root cause analysis generated
- [X] Remediation recommendations accurate
- [X] Risk assessment provided

## Next Steps

Session B complete. Ready to proceed with final integration.
```

```bash
# Update MASTER_SYSTEM_SPEC.md
nano /home/boatiq/Helm-OS/MASTER_SYSTEM_SPEC.md
```

**Spec Updates**:
```markdown
# Add to version history:
| 3.7 | 2026-02-20 | d3kOS Team | Implemented Self-Healing System (Section 6.4) - issue detection, AI diagnosis, auto-remediation, user notifications |

# Update Section 6.4:
**Implementation Status**: ✅ COMPLETE (February 20, 2026)
- Detection: `d3kos-issue-detector.service`
- Remediation: `d3kos-remediation.service`
- API: Port 8099
- UI: `/settings-healing.html`
```

```bash
# Commit to git
cd /home/boatiq/Helm-OS
git add MASTER_SYSTEM_SPEC.md doc/SESSION_B_SELF_HEALING_COMPLETE.md
git commit -m "Session B: Self-Healing System Implementation

- Implemented AI-powered self-healing per spec Section 6.4
- Created issue detection service (engine + Pi health)
- Created remediation engine with safe actions
- Integrated AI diagnosis for root cause analysis
- Added self-healing API (port 8099)
- Created settings UI for monitoring
- All changes verified and tested

Closes: Self-healing system for v0.9.1.2
See: doc/SESSION_B_SELF_HEALING_COMPLETE.md"

git push origin main
```

---

## SESSION C: DATA EXPORT & BACKUP

**Owner**: Parallel session (after Session A)
**Domain**: Data Management, Backup Systems
**Duration**: 6-8 hours
**Dependencies**: Session A complete (requires tier system)

### Objectives
1. ✅ Complete data export queue/retry system (Section 8.3.4)
2. ✅ Fix boatlog export button
3. ✅ Implement backup & restore (Section 8.2)
4. ✅ Test and verify
5. ✅ Document updates
6. ✅ Commit to git

---

### Task C1: Data Export Queue System (3-4 hours)

#### Step C1.1: Complete Export Manager
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Update export manager with queue logic
sudo nano /opt/d3kos/services/export/export-manager.py
```

**Add Queue System** (add to existing file):
```python
# Add to imports
import time
from threading import Thread

# Add queue file constant
QUEUE_FILE = '/opt/d3kos/data/exports/export_queue.json'
HISTORY_FILE = '/opt/d3kos/data/exports/export_history.json'

# Add queue management class
class ExportQueue:
    def __init__(self):
        self.queue = self.load_queue()
        self.history = self.load_history()

        # Start background worker
        self.worker_thread = Thread(target=self.process_queue, daemon=True)
        self.worker_thread.start()

    def load_queue(self):
        """Load pending exports from queue file"""
        try:
            if os.path.exists(QUEUE_FILE):
                with open(QUEUE_FILE, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []

    def save_queue(self):
        """Save queue to disk"""
        os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
        with open(QUEUE_FILE, 'w') as f:
            json.dump(self.queue, f, indent=2)

    def load_history(self):
        """Load export history"""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []

    def save_history(self):
        """Save history to disk"""
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

        # Keep last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]

        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)

    def add_export(self, export_data):
        """Add export to queue"""
        export_item = {
            'id': str(int(time.time() * 1000)),
            'timestamp': datetime.now().isoformat(),
            'data': export_data,
            'attempts': 0,
            'max_attempts': 3,
            'status': 'pending',
            'last_error': None
        }

        self.queue.append(export_item)
        self.save_queue()

        return export_item['id']

    def upload_to_central_database(self, export_data):
        """Upload export data to central database API"""
        try:
            # Central database endpoint (placeholder - replace with actual URL)
            # For v0.9.1.2, this will fail (no central database)
            # But queue will retry and store for future sync

            API_ENDPOINT = 'https://d3kos-cloud.example.com/api/v1/data/import'

            response = requests.post(
                API_ENDPOINT,
                json=export_data,
                headers={
                    'Authorization': f"Bearer {export_data['installation_id']}",
                    'Content-Type': 'application/json'
                },
                timeout=30
            )

            if response.status_code == 200:
                return {'success': True, 'response': response.json()}
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'No internet connection or central database unavailable'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def process_queue(self):
        """Background worker to process export queue"""
        print("📤 Export queue worker started")

        while True:
            try:
                # Process pending exports
                for export_item in self.queue[:]:  # Copy to avoid modification during iteration
                    if export_item['status'] != 'pending':
                        continue

                    if export_item['attempts'] >= export_item['max_attempts']:
                        # Max attempts reached, mark as failed
                        export_item['status'] = 'failed'
                        self.history.append(export_item)
                        self.queue.remove(export_item)
                        self.save_queue()
                        self.save_history()
                        print(f"❌ Export {export_item['id']} failed after {export_item['max_attempts']} attempts")
                        continue

                    # Attempt upload
                    export_item['attempts'] += 1
                    print(f"📤 Uploading export {export_item['id']} (attempt {export_item['attempts']}/{export_item['max_attempts']})")

                    result = self.upload_to_central_database(export_item['data'])

                    if result['success']:
                        # Success - remove from queue
                        export_item['status'] = 'completed'
                        export_item['completed_at'] = datetime.now().isoformat()
                        self.history.append(export_item)
                        self.queue.remove(export_item)
                        self.save_queue()
                        self.save_history()
                        print(f"✅ Export {export_item['id']} uploaded successfully")
                    else:
                        # Failed - update error and retry later
                        export_item['last_error'] = result['error']
                        self.save_queue()
                        print(f"⚠ Export {export_item['id']} failed: {result['error']}")

                        # Wait before retry (5 seconds for attempt 1, 5 minutes for attempt 2, 15 minutes for attempt 3)
                        retry_delays = [5, 300, 900]
                        delay = retry_delays[export_item['attempts'] - 1] if export_item['attempts'] <= 3 else 900
                        time.sleep(delay)

                # Sleep 30 seconds between queue checks
                time.sleep(30)

            except Exception as e:
                print(f"Error in export queue worker: {e}")
                time.sleep(60)

# Initialize queue at module level
export_queue = ExportQueue()

# Update generate_export() function to use queue
@app.route('/export/generate', methods=['POST'])
def api_generate_export():
    """Generate and queue export data"""
    try:
        # Check tier (Tier 1+ required)
        tier_response = requests.get('http://localhost:8093/tier/status', timeout=2)
        tier_data = tier_response.json()
        tier = tier_data.get('tier', 0)

        if tier < 1:
            return jsonify({
                'success': False,
                'error': 'Data export requires Tier 1 or higher'
            }), 403

        # Generate export data (existing logic)
        export_data = {
            'installation_id': get_installation_id(),
            'tier': tier,
            'timestamp': datetime.now().isoformat(),
            'format_version': '1.0',
            'categories': {}
        }

        # Category 1: Engine benchmark
        # Category 2: Boatlog entries
        # Category 3-9: Other categories (existing code)
        # ... (keep existing export generation code)

        # Add to queue instead of immediate upload
        queue_id = export_queue.add_export(export_data)

        return jsonify({
            'success': True,
            'message': 'Export queued for upload',
            'queue_id': queue_id,
            'export_size': len(json.dumps(export_data))
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export/queue', methods=['GET'])
def api_export_queue():
    """Get current export queue status"""
    return jsonify({
        'success': True,
        'pending': len([e for e in export_queue.queue if e['status'] == 'pending']),
        'queue': export_queue.queue
    })

@app.route('/export/history', methods=['GET'])
def api_export_history():
    """Get export history"""
    return jsonify({
        'success': True,
        'history': export_queue.history[-20:]  # Last 20
    })
```

```bash
# Restart service
sudo systemctl restart d3kos-export-manager

# Test queue
curl -X POST http://localhost/export/generate
curl http://localhost/export/queue
curl http://localhost/export/history
```

**Verification**:
- [ ] Export queued successfully
- [ ] Background worker running
- [ ] Retry logic works (check after 5 sec, 5 min, 15 min)
- [ ] Failed exports marked after 3 attempts
- [ ] History saved correctly

---

### Task C2: Fix Boatlog Export Button (1-2 hours)

#### Step C2.1: Debug Current Export Issue
```bash
# Check boatlog page for export button
sudo nano /var/www/html/boatlog.html
# Find export button click handler
```

#### Step C2.2: Implement CSV Export
```python
# Add to export-manager.py

@app.route('/export/boatlog/csv', methods=['GET'])
def api_export_boatlog_csv():
    """Export boatlog to CSV file"""
    try:
        # Read boatlog database
        conn = sqlite3.connect('/opt/d3kos/data/boatlog/boatlog.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, timestamp, type, entry, location, weather, crew_notes
            FROM boatlog_entries
            ORDER BY timestamp DESC
        ''')

        entries = cursor.fetchall()
        conn.close()

        # Generate CSV
        csv_lines = ['ID,Timestamp,Type,Entry,Location,Weather,Crew Notes']

        for entry in entries:
            # Escape commas and quotes
            csv_line = ','.join([
                str(entry[0]),
                entry[1],
                entry[2],
                f'"{entry[3].replace('"', '""')}"',
                f'"{entry[4].replace('"', '""') if entry[4] else ""}"',
                f'"{entry[5].replace('"', '""') if entry[5] else ""}"',
                f'"{entry[6].replace('"', '""') if entry[6] else ""}"'
            ])
            csv_lines.append(csv_line)

        csv_content = '\n'.join(csv_lines)

        # Return as downloadable file
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=boatlog_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

```bash
# Update boatlog.html export button
sudo nano /var/www/html/boatlog.html
```

**Fix Export Button**:
```javascript
// Change from:
function exportBoatlog() {
    // Old broken code
}

// To:
function exportBoatlog() {
    window.location.href = '/export/boatlog/csv';
}
```

**Verification**:
- [ ] Export button doesn't crash
- [ ] CSV file downloads correctly
- [ ] All boatlog entries included
- [ ] CSV format valid (opens in Excel/LibreOffice)

---

### Task C3: Backup & Restore System (2-3 hours)

#### Step C3.1: Create Backup Script
```bash
sudo nano /opt/d3kos/scripts/create-backup.sh
```

**Backup Script**:
```bash
#!/bin/bash
# d3kOS Backup Script
# Creates full system backup to USB drive

set -e

BACKUP_DIR="/media/d3kos/6233-3338/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="d3kos_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "🔄 Creating d3kOS backup: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Backup databases
echo "📦 Backing up databases..."
mkdir -p "$BACKUP_PATH/databases"
cp -r /opt/d3kos/data/*.db "$BACKUP_PATH/databases/" 2>/dev/null || true
cp -r /opt/d3kos/data/*/