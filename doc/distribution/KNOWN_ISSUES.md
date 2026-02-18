# d3kOS Known Issues

**Document Version:** 1.0
**Date:** 2026-02-18
**Distribution Version:** 1.0.3

This document lists all known issues with the d3kOS system that have not yet been resolved. Each issue includes:
- Description of the problem
- Root cause analysis
- Current status
- Workarounds (if available)
- Planned resolution (if applicable)

---

## Issue #1: Voice Assistant Wake Word Detection Not Working ⚠️

**Severity:** Medium
**Status:** KNOWN - Not Fixed
**First Reported:** 2026-02-17
**Affects:** Tier 2+ users with voice assistant enabled

### Description
Voice assistant service (`d3kos-voice`) runs correctly and PocketSphinx wake word detection process is active, but wake words ("helm", "advisor", "counsel") are not detected when spoken into the microphone.

### Symptoms
- Service status shows "running"
- PocketSphinx process visible in `ps aux`
- Service logs show "🎤 Listening for wake words..."
- Speaking wake words into microphone produces no response
- No "Wake word detected" entries in service logs

### Root Cause
Investigation revealed multiple contributing factors:

1. **PipeWire Signal Loss (CONFIRMED)**
   - PipeWire audio server reduces microphone signal by ~17x
   - Direct hardware access: 3.1-4.5% signal strength
   - Via PipeWire: 0.18% signal strength
   - Currently mitigated by using `-adcdev plughw:3,0` for direct hardware access

2. **PocketSphinx Subprocess Integration (SUSPECTED)**
   - Python subprocess handling may not be correctly reading wake word output from PocketSphinx stdout
   - `-logfn /dev/null` suppresses internal PocketSphinx logging but may also suppress wake word detection output
   - Issue persists even with Feb 13 "known working" configuration

3. **System Updates (POSSIBLE)**
   - User reported "it once worked well" but broke at some earlier point
   - Possible PocketSphinx, ALSA, PipeWire, or kernel update changed behavior
   - Timeline analysis needed to identify what changed

### Current Workaround
**Use text-based AI Assistant instead:**
- URL: http://192.168.1.237/ai-assistant.html
- Provides same functionality as voice assistant
- Works perfectly with touchscreen or physical keyboard
- Same AI models (online + onboard rule-based)

### Attempted Fixes (All Failed)
1. ❌ Switched from PipeWire to direct hardware access (`-adcdev plughw:3,0`)
   - Result: Improved signal strength, but detection still failed
2. ❌ Removed `-logfn /dev/null` to enable stdout output
   - Result: PocketSphinx subprocess wouldn't stay running
3. ❌ Reverted to Feb 13 "working" configuration
   - Result: Still doesn't detect wake words (implies issue is system-level, not code)

### Planned Resolution
**Requires dedicated 2-3 hour debugging session:**
1. Timeline analysis (system update logs since last known working date)
2. Manual PocketSphinx testing (outside of Python, direct command-line)
3. Audio stack investigation (test PulseAudio vs PipeWire vs ALSA direct)
4. Python subprocess debugging (extensive logging, stdout monitoring)
5. Consider alternative wake word engines (Vosk, Porcupine, Snowboy)

**Alternative:** May consider rebuilding voice assistant from scratch with different architecture

---

## Issue #2: GPS Drift When Stationary (Indoors)

**Severity:** Low
**Status:** EXPECTED BEHAVIOR - Not a Bug
**Affects:** All systems when used indoors

### Description
GPS shows movement (0.5-2 knots speed, changing course) when boat is stationary with engine off, particularly when system is indoors.

### Symptoms
- Speed over ground: 0.5-2 knots (should be 0 when stationary)
- Course over ground: Changing randomly (e.g., 100°, 150°, 45°)
- Position "wanders" within 10-30 meter radius
- Satellite count: 3-6 (low)
- HDOP: 3.0-5.0 (poor accuracy)

### Root Cause
**This is normal GPS behavior with weak satellite signals:**
- Indoor/urban environments block GPS signals
- Low satellite count (3-6 satellites vs optimal 8-12)
- High HDOP (Horizontal Dilution of Precision) indicates large error circle
- GPS position estimate "wanders" within the error circle
- GPS firmware interprets position changes as movement

### Expected Behavior Outdoors
- 8-12 satellites visible
- HDOP < 2.0 (good accuracy)
- Position accuracy: ±3-5 meters
- Speed: 0.0 knots when stationary
- No false movement

### Workaround
**Not needed - this is expected indoors.**

Signal K correctly reports GPS data; the issue is with GPS signal quality, not software.

### Verification
To verify GPS is working correctly:
1. Check satellite count: `curl http://192.168.1.237/signalk/v1/api/vessels/self/navigation/gnss/satellitesInView`
2. If satellites < 4, GPS has weak fix (expected indoors)
3. If satellites ≥ 8 outdoors and still drifting, check antenna connection

---

## Issue #3: NMEA2000 Simulator Should Be Disabled (Production)

**Severity:** Low
**Status:** DOCUMENTED - Distribution Image Should Not Include
**Affects:** Distribution image only

### Description
NMEA2000 simulator (`d3kos-simulator.service`) is useful for development/testing but should be disabled or removed before distribution.

### Symptoms
- Service `d3kos-simulator.service` exists and may auto-start
- Signal K provider `vcan0-simulator` may be enabled
- Virtual CAN interface `vcan0` created on boot
- Conflicts with real CAN0 data (engine, chartplotter)

### Resolution
**Before creating distribution image:**
1. Stop simulator: `sudo systemctl stop d3kos-simulator`
2. Disable auto-start: `sudo systemctl disable d3kos-simulator`
3. Edit Signal K settings: `~/.signalk/settings.json`
   - Find `"id": "vcan0-simulator"`
   - Set `"enabled": false`
4. Optionally remove service file: `sudo rm /etc/systemd/system/d3kos-simulator.service`

### Verification
Run pre-distribution checklist:
```bash
/opt/d3kos/tests/pre-distribution-checklist.sh
```

---

## Issue #4: Boatlog Export Button (Untested)

**Severity:** Low
**Status:** NEEDS TESTING
**Reported:** 2026-02-17
**Affects:** Boatlog page export functionality

### Description
User reported boatlog export button may crash or not work correctly. Not yet verified in current distribution testing.

### Symptoms
- Clicking "Export" button on boatlog page may not download file
- Possible JavaScript console errors
- Export manager service is running correctly

### Investigation Needed
This issue requires manual browser testing:
1. Navigate to http://192.168.1.237/boatlog.html
2. Add test entries to boatlog
3. Click "Export" button
4. Verify CSV file downloads correctly
5. Check browser console for errors

### Prerequisites Verified
- ✅ Export manager service is running (port 8094)
- ✅ Nginx proxy configured correctly (`/export/` → `localhost:8094`)
- ✅ Export API endpoints responding

### Workaround
If export button fails, use API directly:
```bash
curl -X POST http://192.168.1.237/export/generate | jq .
```

---

## Issue #5: Onboarding Wizard Reset Limit (Tier 0)

**Severity:** Low
**Status:** BY DESIGN - Feature, Not Bug
**Affects:** Tier 0 users only

### Description
Tier 0 (free) users have a limit of 10 onboarding wizard resets. After 10 resets, the wizard cannot be reset again without upgrading to Tier 2+.

### Design Rationale
- Prevents abuse of free tier
- Encourages upgrade to paid tiers
- Unlimited resets available with Tier 2+ (OpenCPN installed or paid subscription)

### Current Status
Check reset counter:
```bash
jq '.reset_count, .max_resets' /opt/d3kos/config/license.json
```

### Workaround
**Upgrade to Tier 2+:**
- **Option 1:** Install OpenCPN (auto-detected, free upgrade)
- **Option 2:** Purchase Tier 2 subscription ($9.99/month)
- **Option 3:** Purchase Tier 3 subscription ($99.99/year)

After upgrade, reset count becomes unlimited (`max_resets: -1`).

---

## Issue #6: PipeWire Audio Signal Reduction

**Severity:** Low
**Status:** MITIGATED
**Affects:** Voice assistant and any audio recording

### Description
PipeWire audio server sits between applications and hardware, causing ~17x reduction in microphone signal strength during sample rate conversion and stereo-to-mono mixing.

### Technical Details
- **Direct hardware (plughw:3,0):** 3.1-4.5% signal strength
- **Via PipeWire:** 0.18% signal strength
- **Loss factor:** ~17x reduction
- **Cause:** Sample rate conversion (48kHz → 16kHz), stereo → mono, volume processing

### Current Mitigation
Voice assistant service configured to bypass PipeWire:
```python
# /opt/d3kos/services/voice/voice-assistant-hybrid.py
["-adcdev", "plughw:3,0", ...]  # Direct hardware access
```

This restores signal strength to 3.1-4.5% (normal levels).

### Impact
- ✅ Voice assistant uses direct hardware access (PipeWire bypassed)
- ✅ Other audio applications (VLC, arecord) work normally
- ⚠️ Any new audio recording applications should use `plughw:X,Y` format

### No Action Required
System is already configured correctly.

---

## Issue #7: Telegram Notifications Not Configured (Default State)

**Severity:** None
**Status:** EXPECTED - Fresh Installation
**Affects:** Fresh installations

### Description
Telegram notification system is installed but not configured by default. Users must set up their own Telegram bot and chat ID.

### Setup Required
1. Create Telegram bot via @BotFather
2. Get bot token (format: `110201543:AAHdqTcvCH1...`)
3. Get chat ID (send message to bot, then query updates)
4. Configure d3kOS:
   ```bash
   curl -X POST http://192.168.1.237/notify/config \
     -H "Content-Type: application/json" \
     -d '{"enabled":true,"bot_token":"YOUR_TOKEN","chat_id":"YOUR_CHAT_ID"}'
   ```
5. Test:
   ```bash
   curl -X POST http://192.168.1.237/notify/test
   ```

### Documentation
Full setup guide: `/home/boatiq/Helm-OS/doc/MARINE_VISION_NOTIFICATION_INTEGRATION.md`

### Expected Status
On fresh installation:
- Service running: ✅
- Telegram configured: ❌ (expected)
- Notifications enabled: ❌ (expected)

---

## Testing Known Issues

All known issues are tested by the test suite:
- **test-known-issues.sh** - Tests and documents all known issues
- Expected to report some "KNOWN ISSUE" results (not failures)

To run known issues test:
```bash
/opt/d3kos/tests/test-known-issues.sh
```

---

## Reporting New Issues

If you discover a new issue not listed here:

1. Check if issue is in test suite output
2. Review `/opt/d3kos/tests/reports/test-report-latest.html`
3. Document:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System logs (if applicable)
4. Report via GitHub issues: https://github.com/[d3kos-repo]/issues

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-18 | Initial version for distribution 1.0.3 |

---

**End of Known Issues Document**
