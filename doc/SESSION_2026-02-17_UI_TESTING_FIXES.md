# Session 2026-02-17 - UI Testing & Voice Fix

**Date:** February 17, 2026
**Session Type:** Bug fixes and testing after Sessions A, B, C
**Status:** ✅ COMPLETE - All 3 issues resolved

---

## Session Context

After completing three implementation sessions:
- **Session A:** Installation ID System (4-6 hours)
- **Session B:** License/Tier System (4 hours)
- **Session C:** Data Export System (1 hour)

User tested the UI changes and reported 3 failing issues.

---

## Issues Reported

### Issue 1: Export Manager JSON Error ❌
**Problem:** Settings → Data Management page crashed with "Failed to execute 'json' on 'Response': Unexpected end of JSON input"

**Root Cause:** Nginx proxy misconfiguration
- Export manager running on port **8094**
- Nginx proxying to port **8090** (wrong service)

**Fix:**
```bash
# /etc/nginx/sites-enabled/default
location /export/ {
    proxy_pass http://localhost:8094/export/;  # Changed from 8090
}
```

**Also Added Missing Endpoint:**
```python
# /opt/d3kos/services/export/export-manager.py
@app.route('/export/status', methods=['GET'])
def api_export_status():
    return jsonify({
        'success': True,
        'tier': tier,
        'can_export': can_export,
        'export_count': export_count
    })
```

**Result:** ✅ Export page loads correctly

---

### Issue 2: QR Code Not Readable on Mobile ❌
**Problem:** QR code displayed in onboarding wizard Step 19 but mobile phones couldn't scan it

**Original QR Data (170+ characters):**
```json
{
  "installation_uuid": "3861513b-314c-5ee7-0000-000000000000",
  "pairing_token": "PAIR-ABC123XYZ",
  "api_endpoint": "https://d3kos-cloud/api/v1",
  "current_tier": 0
}
```

**Issues:**
1. Complex JSON data (170+ chars) = dense QR code
2. Non-standard colors (green on black)
3. High error correction level (Level H)

**Fixes Applied:**

1. **Simplified Data** (170 chars → 16 chars):
```javascript
// Old:
const qrData = JSON.stringify({...complex object...});

// New:
const qrData = id;  // Just "3861513b314c5ee7"
```

2. **Standard Colors:**
```javascript
colorDark: "#000000",   // Black (was green)
colorLight: "#FFFFFF",  // White (was black)
```

3. **Larger Size:**
```javascript
width: 400,   // Was 300
height: 400,  // Was 300
```

4. **Better Error Correction:**
```javascript
correctLevel: QRCode.CorrectLevel.M  // Medium (was H)
```

**Result:** ✅ QR code scans easily on mobile phones

---

### Issue 3: Voice Assistant Not Responding ❌
**Problem:** Voice service running but not detecting wake words ("helm", "advisor", "counsel")

**User Quote:** "it once worked well now for some reason it not working"

**Investigation Process:**

1. **Manual PocketSphinx Test:**
```bash
pocketsphinx_continuous -inmic yes -kws /opt/d3kos/config/sphinx/wake-words.kws
```
**Result:** ✅ Detected "helm" successfully → PocketSphinx works!

2. **Microphone Level Test:**
```bash
arecord -D plughw:3,0 -d 2 -f S16_LE -r 16000 /tmp/test.wav
sox /tmp/test.wav -n stat 2>&1 | grep "Maximum amplitude"
```
**Result:** 0.007416 (0.7%) - EXTREMELY LOW SIGNAL

3. **Volume Check:**
```bash
amixer -c 3 contents | grep "Capture Volume"
```
**Result:** Volume already at MAX (127/127) - Not a volume issue

4. **PipeWire Investigation:**
```bash
# Direct hardware access
arecord -D plughw:3,0 → Maximum amplitude: 0.031189 (3.1%)

# ALSA default (via PipeWire)
arecord → Maximum amplitude: 0.001801 (0.18%)
```
**FOUND IT:** PipeWire reducing signal by **17x!**

**Root Cause:**
- PipeWire audio server intercepting microphone
- Applying sample rate conversion (48kHz → 16kHz)
- Mixing stereo to mono with signal loss
- PocketSphinx using ALSA default (via PipeWire) instead of direct hardware

**Fix:**
```python
# /opt/d3kos/services/voice/voice-assistant-hybrid.py
# Old:
["-inmic", "yes",...]

# New:
["-adcdev", "plughw:3,0",...]
```

**Why This Works:**
- `-inmic yes` uses ALSA default device (controlled by PipeWire)
- `-adcdev plughw:3,0` bypasses PipeWire and accesses hardware directly
- Direct access = 17x louder signal = wake word detection works!

**Result:** ✅ Voice assistant responds to wake words

---

## Files Modified

### 1. `/etc/nginx/sites-enabled/default`
**Change:** Fixed export proxy port
```nginx
location /export/ {
    proxy_pass http://localhost:8094/export/;  # Was 8090
}
```

### 2. `/opt/d3kos/services/export/export-manager.py`
**Change:** Added `/export/status` endpoint
```python
@app.route('/export/status', methods=['GET'])
def api_export_status():
    # Returns tier, can_export, export_count
```

### 3. `/var/www/html/onboarding.html`
**Change:** Simplified QR code generation
```javascript
// Before: 170-char JSON
const qrData = JSON.stringify({installation_uuid: ...});

// After: 16-char plain text
const qrData = id;  // "3861513b314c5ee7"
```
**Also changed:** Colors (black on white), size (400x400), error correction (M)

### 4. `/opt/d3kos/services/voice/voice-assistant-hybrid.py`
**Change:** Direct hardware microphone access
```python
# Before:
["-inmic", "yes",...]

# After:
["-adcdev", "plughw:3,0",...]
```

### 5. Wake Word Config (reverted changes)
**File:** `/opt/d3kos/config/sphinx/wake-words.kws`
**Restored to original:**
```
helm /1e-3/
advisor /1e-3/
counsel /1e-3/
```

### 6. ALSA Config (removed)
**File:** `~/.asoundrc` (deleted)
**Why:** PipeWire conflict - not needed with direct hardware access

---

## Backups Created

All modified files backed up before changes:

```
/opt/d3kos/services/export/export-manager.py.bak.status
/var/www/html/onboarding.html.bak.qrfix
/var/www/html/onboarding.html.bak.qrsimple
/opt/d3kos/services/voice/voice-assistant-hybrid.py.bak.pipewire
/opt/d3kos/config/sphinx/wake-words.kws.bak.1e10
```

---

## Testing Results

### Export Manager
```bash
curl http://192.168.1.237/export/status | jq .
```
**Output:**
```json
{
  "can_export": true,
  "export_count": 2,
  "installation_id": "3861513b314c5ee7",
  "service_status": "running",
  "success": true,
  "tier": 2
}
```
✅ **PASS**

### QR Code
- Scanned with mobile phone camera
- Displays: `3861513b314c5ee7`
- ✅ **PASS**

### Voice Assistant
```bash
# Say "HELM" into Anker S330 microphone
# Expected: "Aye Aye Captain" TTS response
```
✅ **PASS** (after PipeWire fix)

---

## Technical Deep Dive: PipeWire Issue

### Problem
PipeWire audio server sits between applications and hardware:
```
PocketSphinx → ALSA → PipeWire → Hardware (plughw:3,0)
```

### Signal Loss Analysis
| Path | Signal Level | Notes |
|------|--------------|-------|
| Direct Hardware | 3.1% | Clean signal |
| Via PipeWire | 0.18% | **17x reduction!** |

### PipeWire Processing Pipeline
1. **Sample Rate Conversion:** 48kHz (hardware) → 16kHz (PocketSphinx)
2. **Channel Mixing:** Stereo (2ch) → Mono (1ch)
3. **Volume Processing:** Applies system volume settings
4. **Buffering:** Adds latency and potential signal degradation

### Why Direct Access Works
```python
"-adcdev", "plughw:3,0"  # Bypasses PipeWire entirely
```
- No sample rate conversion
- No channel mixing
- No volume processing
- No buffering latency
- **Result:** 17x stronger signal!

### PipeWire Configuration (for reference)
```bash
pactl list sources | grep "alsa_input.usb-ANKER"
```
Shows PipeWire is controlling the S330:
- Driver: PipeWire
- Sample Spec: s16le 2ch 48000Hz
- Volume: 100% (but still applies processing)

---

## System Status After Fixes

### Services Running
```bash
systemctl status d3kos-export-manager  # Port 8094, active
systemctl status d3kos-voice           # Active, using plughw:3,0
systemctl status d3kos-tier-manager    # Active
systemctl status d3kos-tier-api        # Port 8093, active
systemctl status d3kos-license-api     # Port 8091, active
```

### Tier Status
```json
{
  "tier": 2,
  "installation_id": "3861513b314c5ee7",
  "features": {
    "voice_assistant": true,
    "camera": true,
    "unlimited_resets": true,
    "cloud_sync": false
  },
  "upgrade_method": "opencpn_detect"
}
```

### Nginx Proxies
```
/license/  → localhost:8091  # License API
/tier/     → localhost:8093  # Tier API
/export/   → localhost:8094  # Export Manager (FIXED)
/ai/       → localhost:8080  # AI Assistant
/camera/   → localhost:8084  # Camera Stream
/detect/   → localhost:8086  # Fish Detection
```

---

## Lessons Learned

### 1. Always Check Audio Path
- Don't assume `-inmic yes` uses hardware directly
- Audio servers (PipeWire/PulseAudio) can interfere
- Test with direct hardware access when troubleshooting

### 2. QR Code Best Practices
- Keep data minimal (plain text > JSON)
- Use standard colors (black on white)
- Larger size = easier scanning
- Medium error correction usually sufficient

### 3. Nginx Proxy Debugging
- Always verify service ports with `lsof -i :PORT`
- Test endpoints directly (localhost) before nginx
- Check nginx logs when proxies fail

### 4. Port Management
- Port 8090: Old export service (leftover)
- Port 8091: License API
- Port 8093: Tier API
- Port 8094: Export Manager (correct)

---

## Session Statistics

**Time Spent:** ~3 hours
**Token Usage:** ~97,000 tokens
**Issues Fixed:** 3/3 (100%)
**Files Modified:** 6
**Backups Created:** 5
**System Reboots:** 0 (all hot fixes)

---

## Next Phase Preparation

### Tasks Completed (Sessions A, B, C + Testing)
- ✅ Installation ID System
- ✅ License/Tier System
- ✅ Data Export System (simplified)
- ✅ UI Testing & Bug Fixes

### Ready for Next Phase
System is now fully functional with:
- Proper installation ID (persistent, file-based)
- Tier detection and feature restrictions
- Data export capability (Tier 1+)
- Working voice assistant
- Scannable QR code
- All APIs operational

### Potential Next Steps
1. **Marine Vision Phase 2.2+** - Custom fish detection model
2. **Full Data Export Implementation** - Queue system, boot-time upload
3. **E-commerce Integration** - Stripe billing (40-60 hour project)
4. **Charts Page** - Install o-charts addon
5. **Boatlog Export Fix** - Fix export button crash
6. **Documentation** - User guides for new features

---

## Commands Reference

### Test Export API
```bash
curl http://192.168.1.237/export/status | jq .
curl -X POST http://192.168.1.237/export/generate | jq .
```

### Test Voice Assistant
```bash
# Manual PocketSphinx test
pocketsphinx_continuous -adcdev plughw:3,0 -kws /opt/d3kos/config/sphinx/wake-words.kws

# Check microphone levels
arecord -D plughw:3,0 -d 2 -f S16_LE -r 16000 /tmp/test.wav
sox /tmp/test.wav -n stat 2>&1 | grep "Maximum amplitude"
```

### Check Tier Status
```bash
curl http://192.168.1.237/tier/status | jq .
```

### Service Management
```bash
sudo systemctl status d3kos-voice
sudo systemctl restart d3kos-export-manager
journalctl -u d3kos-voice -n 50 --no-pager
```

---

**Session Complete:** All 3 issues resolved, system fully operational.
