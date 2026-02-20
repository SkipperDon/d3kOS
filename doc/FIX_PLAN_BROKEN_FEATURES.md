# Fix Plan for Broken Features

**Date:** February 20, 2026
**Status:** AUTO-ACCEPTANCE MODE
**Issues:** 4 critical fixes needed

---

## EXECUTIVE SUMMARY

Fixing all broken features identified in comprehensive system status review:

1. ✅ Fish Detection Phase 2.1 Error (investigating)
2. ⏳ Voice Assistant Wake Word Detection (2-3 hours)
3. ⏳ Boatlog CSV Export Button (1-2 hours)
4. ⏳ Export Queue/Retry System (10-12 hours)

**Total Time:** 14-18 hours
**Approach:** Systematic investigation → Fix → Verify → Document → Commit

---

## ISSUE 1: FISH DETECTION PHASE 2.1 ERROR

### Investigation Plan

**Step 1: Check Service Status**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
systemctl status d3kos-fish-detector.service
journalctl -u d3kos-fish-detector.service -n 50 --no-pager
```

**Step 2: Check API Endpoint**
```bash
curl http://localhost:8086/detect/status
```

**Step 3: Check Model File**
```bash
ls -lh /opt/d3kos/models/marine-vision/yolov8n.onnx
# Should be 13MB
```

**Step 4: Check Dependencies**
```bash
python3 -c "import onnxruntime; print(onnxruntime.__version__)"
python3 -c "import numpy; print(numpy.__version__)"
python3 -c "from PIL import Image; print('PIL OK')"
```

**Step 5: Check Database**
```bash
ls -lh /opt/d3kos/data/marine-vision/captures.db
sqlite3 /opt/d3kos/data/marine-vision/captures.db "SELECT count(*) FROM captures;"
```

### Common Issues & Fixes

**Issue 1A: Service Failed to Start**
- **Cause:** Missing dependencies, syntax error, port conflict
- **Fix:**
  ```bash
  # Check what failed
  journalctl -u d3kos-fish-detector.service -n 100

  # Reinstall dependencies if needed
  pip3 install onnxruntime numpy pillow

  # Check port not in use
  sudo lsof -i :8086

  # Restart service
  sudo systemctl restart d3kos-fish-detector.service
  ```

**Issue 1B: Model File Missing**
- **Cause:** Download failed, file deleted, wrong path
- **Fix:**
  ```bash
  # Re-download model
  cd /opt/d3kos/models/marine-vision
  wget https://storage.googleapis.com/ailia-models/yolov8/yolov8n.onnx

  # Verify size
  ls -lh yolov8n.onnx  # Should be ~13MB

  # Restart service
  sudo systemctl restart d3kos-fish-detector.service
  ```

**Issue 1C: ONNX Runtime Error**
- **Cause:** ARM incompatibility, version mismatch
- **Fix:**
  ```bash
  # Check ONNX Runtime version
  python3 -c "import onnxruntime; print(onnxruntime.__version__)"

  # Should be 1.24.1 or newer
  # If not, reinstall
  pip3 install --upgrade onnxruntime

  # Test model loading
  python3 <<EOF
import onnxruntime as ort
session = ort.InferenceSession('/opt/d3kos/models/marine-vision/yolov8n.onnx')
print("Model loaded successfully")
EOF
  ```

**Issue 1D: Camera Connection Error**
- **Cause:** Camera offline, network issue, RTSP error
- **Fix:**
  ```bash
  # Check camera reachable
  ping -c 3 10.42.0.100

  # Check camera stream
  systemctl status d3kos-camera-stream.service

  # Verify RTSP URL
  ffmpeg -i rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_sub -frames:v 1 /tmp/test.jpg

  # Restart camera service if needed
  sudo systemctl restart d3kos-camera-stream.service
  ```

**Issue 1E: Database Locked/Corrupted**
- **Cause:** Concurrent access, disk full, power loss
- **Fix:**
  ```bash
  # Check database integrity
  sqlite3 /opt/d3kos/data/marine-vision/captures.db "PRAGMA integrity_check;"

  # If corrupted, backup and recreate
  cp captures.db captures.db.bak
  sqlite3 captures.db.bak ".dump" | sqlite3 captures_new.db
  mv captures_new.db captures.db

  # Restart service
  sudo systemctl restart d3kos-fish-detector.service
  ```

### Fix Script

Create automated fix script:

**File:** `/opt/d3kos/scripts/fix-fish-detector.sh`
```bash
#!/bin/bash
# Fish Detector Service Fix Script

set -e

echo "=== Fish Detector Diagnostic & Fix ==="

# Check dependencies
echo "Checking dependencies..."
python3 -c "import onnxruntime" 2>/dev/null || {
    echo "Installing onnxruntime..."
    pip3 install onnxruntime
}

python3 -c "import numpy" 2>/dev/null || {
    echo "Installing numpy..."
    pip3 install numpy
}

python3 -c "from PIL import Image" 2>/dev/null || {
    echo "Installing pillow..."
    pip3 install pillow
}

# Check model file
if [ ! -f /opt/d3kos/models/marine-vision/yolov8n.onnx ]; then
    echo "Model file missing, downloading..."
    mkdir -p /opt/d3kos/models/marine-vision
    cd /opt/d3kos/models/marine-vision
    wget -q https://storage.googleapis.com/ailia-models/yolov8/yolov8n.onnx
    echo "Model downloaded"
fi

# Check model size
SIZE=$(stat -c%s /opt/d3kos/models/marine-vision/yolov8n.onnx)
if [ $SIZE -lt 10000000 ]; then
    echo "Model file too small, re-downloading..."
    cd /opt/d3kos/models/marine-vision
    rm -f yolov8n.onnx
    wget -q https://storage.googleapis.com/ailia-models/yolov8/yolov8n.onnx
fi

# Test model loading
echo "Testing model loading..."
python3 <<EOF
import onnxruntime as ort
session = ort.InferenceSession('/opt/d3kos/models/marine-vision/yolov8n.onnx')
print("✓ Model loads successfully")
EOF

# Check database
echo "Checking database..."
mkdir -p /opt/d3kos/data/marine-vision
if [ ! -f /opt/d3kos/data/marine-vision/captures.db ]; then
    echo "Database missing, will be created on first run"
fi

# Restart service
echo "Restarting fish detector service..."
sudo systemctl restart d3kos-fish-detector.service

# Wait for service to start
sleep 2

# Check status
if systemctl is-active --quiet d3kos-fish-detector.service; then
    echo "✓ Service running"

    # Test API
    if curl -s http://localhost:8086/detect/status | grep -q "running"; then
        echo "✓ API responding"
        echo "=== Fish Detector Fixed Successfully ==="
        exit 0
    else
        echo "✗ API not responding"
        exit 1
    fi
else
    echo "✗ Service failed to start"
    echo "Check logs: journalctl -u d3kos-fish-detector.service -n 50"
    exit 1
fi
```

**Permissions:**
```bash
chmod +x /opt/d3kos/scripts/fix-fish-detector.sh
```

### Testing Plan

**Test 1: Service Status**
```bash
systemctl status d3kos-fish-detector.service
# Expected: active (running)
```

**Test 2: API Response**
```bash
curl http://localhost:8086/detect/status
# Expected: {"status": "running", ...}
```

**Test 3: Detection Test**
```bash
curl -X POST http://localhost:8086/detect/frame
# Expected: Detection results with bounding boxes
```

**Test 4: Web UI**
```
Navigate to: http://192.168.1.237/marine-vision.html
Click: "Run Detection Now"
# Expected: Detection results displayed
```

---

## ISSUE 2: VOICE ASSISTANT WAKE WORD DETECTION

### Problem Statement

- **Service:** d3kos-voice.service
- **Status:** Running but not detecting wake words
- **Wake Words:** "helm", "advisor", "counsel"
- **User Report:** "it once worked well now for some reason it not working"

### Root Cause Analysis

**Investigation from Session 2026-02-17:**

1. **PipeWire Interference:**
   - PipeWire reduces microphone signal by 17x
   - Direct hardware: 3.1% signal
   - Via PipeWire: 0.18% signal

2. **PocketSphinx Subprocess:**
   - Service says "Listening for wake words..."
   - PocketSphinx process runs
   - But no wake words detected
   - Python subprocess stdout not readable

3. **Audio Routing:**
   - Microphone: Anker S330 at plughw:3,0
   - Previous attempt to use direct hardware failed
   - Reverted to Feb 13 version, still broken

### Investigation Plan

**Step 1: Check Service & Process**
```bash
systemctl status d3kos-voice.service
ps aux | grep pocketsphinx
```

**Step 2: Test Microphone Directly**
```bash
# Test recording
arecord -D plughw:3,0 -d 2 -f S16_LE -r 16000 /tmp/test.wav

# Check signal strength
sox /tmp/test.wav -n stat 2>&1 | grep "Maximum amplitude"
# Should be > 0.5 (50%)
```

**Step 3: Test PocketSphinx Directly**
```bash
pocketsphinx_continuous \
  -adcdev plughw:3,0 \
  -kws /opt/d3kos/config/sphinx/wake-words.kws \
  -dict /opt/d3kos/models/vosk/vosk-model-small-en-us-0.15/dict \
  -hmm /opt/d3kos/models/vosk/vosk-model-small-en-us-0.15/model

# Speak "helm" into microphone
# Should see: KEYPHRASE helm /1e-03/ detected
```

**Step 4: Check Audio Configuration**
```bash
# List audio devices
arecord -l

# Check PipeWire status
systemctl --user status pipewire
systemctl --user status wireplumber

# Check ALSA config
cat ~/.asoundrc
# Should NOT exist (causes conflicts)
```

### Fix Approach

**Option A: Fix PocketSphinx Integration (2 hours)**

Update `/opt/d3kos/services/voice/voice-assistant-hybrid.py`:

```python
def start_wake_word_detection(self):
    """Start PocketSphinx wake word detection"""

    # Use direct hardware access, unbuffered output
    cmd = [
        "stdbuf", "-oL", "-eL",  # Unbuffered stdout/stderr
        "pocketsphinx_continuous",
        "-adcdev", "plughw:3,0",  # Direct hardware
        "-kws", "/opt/d3kos/config/sphinx/wake-words.kws",
        "-dict", "/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15/dict",
        "-hmm", "/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15/model",
        "-logfn", "/tmp/pocketsphinx.log",  # Log to file, not /dev/null
        "-inmic", "yes"
    ]

    # Start process with proper pipes
    self.sphinx_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1  # Line buffered
    )

    # Monitor stdout in separate thread
    def monitor_output():
        for line in iter(self.sphinx_process.stdout.readline, ''):
            if "KEYPHRASE" in line:
                # Extract wake word
                if "helm" in line.lower():
                    self.handle_wake_word("auto")
                elif "advisor" in line.lower():
                    self.handle_wake_word("onboard")
                elif "counsel" in line.lower():
                    self.handle_wake_word("openrouter")

    threading.Thread(target=monitor_output, daemon=True).start()
```

**Option B: Replace with Vosk Wake Word (3 hours)**

Replace PocketSphinx with Vosk's built-in wake word detection:

```python
from vosk import Model, KaldiRecognizer

# Load wake word model
model = Model("/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)

# Add grammar for wake words
grammar = '''
{
  "name": "wake_words",
  "rule": [
    "helm",
    "advisor",
    "counsel"
  ]
}
'''
recognizer.SetGrammar(grammar)

# Process audio stream
import pyaudio
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    input_device_index=3,  # Anker S330
    frames_per_buffer=4000
)

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "").lower()
        if "helm" in text:
            handle_wake_word("auto")
        elif "advisor" in text:
            handle_wake_word("onboard")
        elif "counsel" in text:
            handle_wake_word("openrouter")
```

**Recommended:** Option A first (faster), then Option B if A fails.

### Testing Plan

**Test 1: Manual PocketSphinx**
```bash
pocketsphinx_continuous -adcdev plughw:3,0 -kws wake-words.kws
# Speak "helm" - should see detection
```

**Test 2: Service Test**
```bash
sudo systemctl restart d3kos-voice.service
# Wait 5 seconds
# Speak "helm" loudly and clearly
# Check response: "Aye Aye Captain"
```

**Test 3: All Wake Words**
```
Say "helm" → Should respond
Say "advisor" → Should respond
Say "counsel" → Should respond
```

**Test 4: End-to-End**
```
Say "helm what is the RPM"
# Expected: Full voice query response
```

---

## ISSUE 3: BOATLOG CSV EXPORT BUTTON

### Problem Statement

- **Page:** http://192.168.1.237/boatlog.html
- **Button:** "Export to CSV" button
- **Issue:** Crashes/errors when clicked
- **Expected:** Download CSV file with boatlog entries

### Investigation Plan

**Step 1: Check Export Endpoint**
```bash
# Test API directly
curl -X POST http://localhost/api/boatlog/export
# or
curl -X GET http://localhost/api/boatlog/export.csv
```

**Step 2: Check Boatlog Database**
```bash
sqlite3 /opt/d3kos/data/boatlog/boatlog.db <<EOF
SELECT count(*) FROM boatlog_entries;
SELECT * FROM boatlog_entries LIMIT 5;
EOF
```

**Step 3: Check boatlog.html Code**
```bash
grep -A10 "Export" /var/www/html/boatlog.html
# Find export button click handler
```

### Root Cause Analysis

**Likely Issues:**
1. Export endpoint doesn't exist or wrong URL
2. CSV generation logic broken
3. Database query error
4. Missing Python CSV library
5. Nginx proxy not configured for export endpoint

### Fix Implementation

**File:** `/var/www/html/boatlog.html`

Find export button (around line 200-300):
```html
<button onclick="exportBoatlog()">Export to CSV</button>
```

Update JavaScript function:
```javascript
async function exportBoatlog() {
    try {
        // Show loading
        showMessage('Generating CSV export...', 'info');

        // Call export endpoint
        const response = await fetch('/api/boatlog/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Export failed: ${response.statusText}`);
        }

        // Get CSV content
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `boatlog_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showMessage('✓ Export complete', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showMessage(`✗ Export failed: ${error.message}`, 'error');
    }
}
```

**Create Export API Endpoint:**

**File:** `/opt/d3kos/services/boatlog/boatlog-api.py` (or create if doesn't exist)

```python
#!/usr/bin/env python3
"""
Boatlog Export API
Provides CSV export functionality for boatlog entries
"""

from flask import Flask, jsonify, Response
import sqlite3
import csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)

BOATLOG_DB = '/opt/d3kos/data/boatlog/boatlog.db'

@app.route('/api/boatlog/export', methods=['POST', 'GET'])
def export_boatlog():
    """Export all boatlog entries as CSV"""
    try:
        # Connect to database
        conn = sqlite3.connect(BOATLOG_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query all entries
        cursor.execute("""
            SELECT
                entry_id,
                timestamp,
                entry_type,
                content,
                latitude,
                longitude,
                weather_conditions
            FROM boatlog_entries
            ORDER BY timestamp DESC
        """)

        rows = cursor.fetchall()

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Entry ID',
            'Timestamp',
            'Type',
            'Content',
            'Latitude',
            'Longitude',
            'Weather'
        ])

        # Write data
        for row in rows:
            writer.writerow([
                row['entry_id'],
                row['timestamp'],
                row['entry_type'],
                row['content'],
                row['latitude'] or '',
                row['longitude'] or '',
                row['weather_conditions'] or ''
            ])

        conn.close()

        # Return CSV
        csv_data = output.getvalue()
        filename = f"boatlog_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8095)
```

**Systemd Service:**

**File:** `/etc/systemd/system/d3kos-boatlog-api.service`
```ini
[Unit]
Description=d3kOS Boatlog Export API
After=network.target

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/boatlog
ExecStart=/usr/bin/python3 /opt/d3kos/services/boatlog/boatlog-api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Nginx Configuration:**

Add to `/etc/nginx/sites-enabled/default`:
```nginx
location /api/boatlog/ {
    proxy_pass http://localhost:8095/api/boatlog/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

**Enable Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-boatlog-api.service
sudo systemctl start d3kos-boatlog-api.service
sudo nginx -t && sudo systemctl reload nginx
```

### Testing Plan

**Test 1: API Direct**
```bash
curl -X POST http://localhost:8095/api/boatlog/export > test.csv
cat test.csv
# Should show CSV with header and data
```

**Test 2: Via Nginx**
```bash
curl -X POST http://localhost/api/boatlog/export > test2.csv
# Should work same as Test 1
```

**Test 3: Web UI**
```
1. Navigate to http://192.168.1.237/boatlog.html
2. Click "Export to CSV" button
3. Should download CSV file
4. Open CSV - verify data present
```

---

## ISSUE 4: EXPORT QUEUE/RETRY SYSTEM

### Problem Statement

- **Service:** d3kos-export-manager.service (port 8094)
- **Status:** Running, manual export works
- **Missing:** Queue, retry logic, boot-time upload, scheduled export, history tracking

### Implementation Plan

This is the largest fix (10-12 hours). Full implementation per MASTER_SYSTEM_SPEC Section 8.3.4.

**Phase 1: Queue System (3-4 hours)**
- Export queue file structure
- Queue management class
- Add to queue on manual export
- Queue status API

**Phase 2: Retry Logic (2-3 hours)**
- Background worker thread
- 3-attempt retry (immediate, 5min, 15min)
- Failed export tracking
- Network connectivity check

**Phase 3: Boot-time Upload (1-2 hours)**
- First-boot service
- Check queue on boot
- Upload pending exports
- Log results

**Phase 4: Scheduled Export (2-3 hours)**
- Systemd timer for 3:00 AM daily
- Tier 2+ check
- Incremental export (only new data)
- Auto-add to queue

**Phase 5: All 9 Categories (2-3 hours)**
- Engine benchmark data
- Boatlog entries
- Marine vision captures (metadata)
- Marine vision snapshots (metadata)
- QR code data
- Settings configuration
- System alerts
- Onboarding configuration
- Telemetry & analytics

### Detailed Implementation

**(This section would be very long - ~500 lines of code)**

Due to length constraints, I'll create this as a separate implementation guide.

### Testing Plan

**Test 1: Queue File**
```bash
cat /opt/d3kos/data/exports/export_queue.json
# Should show pending exports
```

**Test 2: Retry Logic**
```bash
# Trigger export with no internet
# Check queue shows retry attempts
# Reconnect internet
# Verify auto-upload
```

**Test 3: Boot Upload**
```bash
# Create export
# Reboot system
# Check logs for boot-time upload
```

**Test 4: Scheduled Export**
```bash
# Wait for 3:00 AM or trigger manually
systemctl start d3kos-export-daily.timer
# Check export created and queued
```

---

## DEPLOYMENT PLAN

### Prerequisites

1. Pi must be powered on and connected to network
2. SSH access functional
3. Backup created before changes

### Deployment Order

**Step 1: Fish Detection Fix (30 min)**
1. Run fix script
2. Verify service
3. Test detection

**Step 2: Boatlog Export Fix (1 hour)**
1. Deploy API service
2. Update HTML
3. Configure nginx
4. Test export

**Step 3: Voice Assistant Fix (2-3 hours)**
1. Update service code
2. Test microphone
3. Test wake words
4. Verify end-to-end

**Step 4: Export Queue (10-12 hours)**
1. Phase 1: Queue system
2. Phase 2: Retry logic
3. Phase 3: Boot upload
4. Phase 4: Scheduled
5. Phase 5: All categories

### Rollback Plan

Each fix has backups:
```bash
# Fish detection
sudo systemctl stop d3kos-fish-detector
sudo cp fish_detector.py.bak fish_detector.py
sudo systemctl start d3kos-fish-detector

# Boatlog
sudo systemctl stop d3kos-boatlog-api
sudo rm boatlog-api.py
sudo systemctl reload nginx

# Voice
sudo systemctl stop d3kos-voice
sudo cp voice-assistant-hybrid.py.bak voice-assistant-hybrid.py
sudo systemctl start d3kos-voice

# Export
sudo systemctl stop d3kos-export-manager
sudo cp export-manager.py.bak export-manager.py
sudo systemctl start d3kos-export-manager
```

---

## DOCUMENTATION

Each fix will be documented in:
- `FIX_1_FISH_DETECTION.md`
- `FIX_2_VOICE_ASSISTANT.md`
- `FIX_3_BOATLOG_EXPORT.md`
- `FIX_4_EXPORT_QUEUE.md`

Final summary in:
- `ALL_FIXES_COMPLETE.md`

---

## COMMIT PLAN

**Commit 1:** Fish detection fix
**Commit 2:** Boatlog export fix
**Commit 3:** Voice assistant fix
**Commit 4:** Export queue system

**Final Commit:** "fix: Complete all broken features - voice, boatlog export, fish detection, export queue"

---

**Status:** Ready to proceed with auto-acceptance
**Next:** Begin Issue 1 - Fish Detection investigation
