# Voice Assistant Fix Procedure
**Issue:** Wake word detection not working (CRITICAL - since Feb 14, 2026)
**Root Cause:** PipeWire reducing microphone signal by 17×
**Fix:** Direct hardware access bypassing PipeWire
**Tested:** Feb 17, 2026 - ✅ WORKING
**Session:** Session-Voice-4 (Timeline & Root Cause Analysis)

---

## Quick Fix (5 minutes)

**For immediate restoration of voice functionality:**

```bash
# SSH to Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Apply fix
sudo sed -i.bak 's/"-inmic", "yes"/"-adcdev", "plughw:3,0"/' \
    /opt/d3kos/services/voice/voice-assistant-hybrid.py

# Restart service
sudo systemctl restart d3kos-voice

# Test (say "HELM" out loud)
# Expected: "Aye Aye Captain" response
```

**If voice works:** ✅ Proceed to "Permanent Fix" section below to commit changes

**If voice doesn't work:** ⚠️ See "Troubleshooting" section

---

## Complete Fix Procedure (30 minutes)

### Prerequisites

**Required:**
- SSH access to Pi: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`
- Sudo privileges (password: d3kos2026)
- Git access to SkipperDon/d3kOS repository

**Optional (Recommended):**
- Working microphone for voice testing
- Second terminal window for monitoring logs

---

### Step 1: Verify Current State (5 minutes)

**1.1 SSH to Raspberry Pi:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
```

**1.2 Check voice service status:**
```bash
systemctl status d3kos-voice
```

**Expected output:**
```
● d3kos-voice.service - d3kOS Voice Assistant
   Loaded: loaded (/etc/systemd/system/d3kos-voice.service; enabled)
   Active: active (running) since...
```

**If not running:**
```bash
sudo systemctl start d3kos-voice
```

**1.3 Check current PocketSphinx configuration:**
```bash
ps aux | grep pocketsphinx_continuous | grep -v grep
```

**Look for one of these:**
- `/-inmic yes` - ❌ BROKEN (using ALSA default via PipeWire)
- `/-adcdev plughw:3,0` - ✅ WORKING (direct hardware access)

**If shows `-adcdev` but voice still not working:** Service may need restart, continue to Step 2

**If shows `-inmic`:** Fix needed, continue to Step 2

**1.4 Check file content:**
```bash
grep -n -E "inmic|adcdev" /opt/d3kos/services/voice/voice-assistant-hybrid.py
```

**Expected broken state (line ~107):**
```python
107:    "-inmic", "yes",
```

**Expected working state (line ~107):**
```python
107:    "-adcdev", "plughw:3,0",
```

---

### Step 2: Test Microphone Signal (5 minutes)

**2.1 Test direct hardware access:**
```bash
arecord -D plughw:3,0 -d 2 -f S16_LE -r 16000 /tmp/test_direct.wav
```

**Expected:** Recording completes successfully

**2.2 Check signal strength:**
```bash
sox /tmp/test_direct.wav -n stat 2>&1 | grep "Maximum amplitude"
```

**Expected:** ~0.03 to 0.05 (3-5% of maximum)

**If much lower (<0.01):** Hardware microphone issue - check Anker S330 mute button/volume

**2.3 Test via PipeWire (for comparison):**
```bash
arecord -d 2 -f S16_LE -r 16000 /tmp/test_pipewire.wav
sox /tmp/test_pipewire.wav -n stat 2>&1 | grep "Maximum amplitude"
```

**Expected:** ~0.002 (0.2% of maximum) - **17× lower than direct hardware**

**2.4 Clean up test files:**
```bash
rm -f /tmp/test_direct.wav /tmp/test_pipewire.wav
```

---

### Step 3: Apply Fix to Voice Service (5 minutes)

**3.1 Create backup:**
```bash
sudo cp /opt/d3kos/services/voice/voice-assistant-hybrid.py \
        /opt/d3kos/services/voice/voice-assistant-hybrid.py.bak.$(date +%Y%m%d-%H%M%S)
```

**3.2 Verify backup created:**
```bash
ls -lh /opt/d3kos/services/voice/voice-assistant-hybrid.py.bak.*
```

**Expected:** New file with timestamp

**3.3 Apply fix (automated):**
```bash
sudo sed -i 's/"-inmic", "yes"/"-adcdev", "plughw:3,0"/' \
    /opt/d3kos/services/voice/voice-assistant-hybrid.py
```

**3.4 Verify fix applied:**
```bash
grep -n -E "inmic|adcdev" /opt/d3kos/services/voice/voice-assistant-hybrid.py
```

**Expected output (line ~107):**
```
107:    "-adcdev", "plughw:3,0",
```

**If still shows `-inmic yes`:** Sed command failed, apply manual fix:
```bash
sudo nano /opt/d3kos/services/voice/voice-assistant-hybrid.py
# Find line ~107 with "-inmic", "yes"
# Change to: "-adcdev", "plughw:3,0",
# Save: Ctrl+O, Enter
# Exit: Ctrl+X
```

---

### Step 4: Restart Voice Service (2 minutes)

**4.1 Restart service:**
```bash
sudo systemctl restart d3kos-voice
```

**4.2 Check service status:**
```bash
systemctl status d3kos-voice
```

**Expected:**
```
● d3kos-voice.service - d3kOS Voice Assistant
   Active: active (running) since [just now]
```

**If failed:** Check logs for errors:
```bash
journalctl -u d3kos-voice -n 50 --no-pager
```

**4.3 Verify PocketSphinx subprocess:**
```bash
ps aux | grep pocketsphinx_continuous | grep -v grep
```

**CRITICAL:** Must show `-adcdev plughw:3,0` in output

**Example working output:**
```
d3kos    1234  ... /usr/bin/pocketsphinx_continuous -adcdev plughw:3,0 -kws ...
```

**If shows `-inmic yes`:** Service didn't load new code, check systemd cache:
```bash
sudo systemctl daemon-reload
sudo systemctl restart d3kos-voice
```

---

### Step 5: Test Wake Word Detection (3 minutes)

**5.1 Open log monitor (Terminal 1):**
```bash
journalctl -u d3kos-voice -f
```

**5.2 Test wake words (speak clearly):**
- Say: **"HELM"**
- Wait 2 seconds
- Say: **"ADVISOR"**
- Wait 2 seconds
- Say: **"COUNSEL"**

**5.3 Expected log output:**
```
Detected wake word: HELM
🎤 Listening for 3 seconds...
```

**5.4 Expected TTS response:**
- Play audio: "Aye Aye Captain"

**5.5 Test full query:**
- Say: **"HELM"**
- Wait for "Aye Aye Captain"
- Say: **"What is the RPM?"**
- Wait for AI response

**Expected response:**
- "The current engine RPM is [value]"

**If wake word detected:** ✅ SUCCESS - Voice assistant working!

**If no detection:** ⚠️ See "Troubleshooting" section

---

### Step 6: Commit Fix to Git (10 minutes)

**6.1 Exit Pi SSH session:**
```bash
exit
```

**6.2 Copy voice service to development machine (WSL/Ubuntu):**
```bash
# On WSL/Ubuntu
cd /home/boatiq/Helm-OS

# Create directory structure if needed
mkdir -p opt/d3kos/services/voice
mkdir -p opt/d3kos/config/sphinx

# Copy voice service from Pi
scp -i ~/.ssh/d3kos_key d3kos@192.168.1.237:/opt/d3kos/services/voice/voice-assistant-hybrid.py \
    opt/d3kos/services/voice/

# Copy wake word config
scp -i ~/.ssh/d3kos_key d3kos@192.168.1.237:/opt/d3kos/config/sphinx/wake-words.kws \
    opt/d3kos/config/sphinx/
```

**6.3 Verify files copied:**
```bash
ls -lh opt/d3kos/services/voice/voice-assistant-hybrid.py
grep -n adcdev opt/d3kos/services/voice/voice-assistant-hybrid.py
```

**Expected:** File exists, contains `-adcdev plughw:3,0`

**6.4 Add to git:**
```bash
git add opt/d3kos/services/voice/voice-assistant-hybrid.py
git add opt/d3kos/config/sphinx/wake-words.kws
git add doc/VOICE_TIMELINE_ANALYSIS.md
git add doc/VOICE_ASSISTANT_ROOT_CAUSE_REPORT.md
git add doc/VOICE_ASSISTANT_FIX_PROCEDURE.md
```

**6.5 Commit with detailed message:**
```bash
git commit -m "Fix voice assistant: Bypass PipeWire with direct hardware access

CRITICAL FIX: Voice assistant wake word detection broken since Feb 14, 2026

Root Cause:
- PipeWire audio server intercepts ALSA default device
- Applies lossy sample rate conversion (48kHz → 16kHz)
- Applies stereo-to-mono mixing and volume processing
- Reduces microphone signal by 17× (from 3.1% to 0.18%)
- PocketSphinx requires ~2-5% signal for wake word detection
- Result: Wake word detection fails completely

Solution:
- Changed PocketSphinx from -inmic yes to -adcdev plughw:3,0
- Direct hardware access bypasses PipeWire
- Maintains full 3.1% signal strength
- Wake word detection working perfectly

Testing:
- Tested Feb 17, 2026 - Working
- Re-tested Feb 18, 2026 - Working
- All 3 wake words (HELM, ADVISOR, COUNSEL) responding
- Full query processing operational

Files Modified:
- opt/d3kos/services/voice/voice-assistant-hybrid.py (line ~107)
- Changed: ['-inmic', 'yes'] to ['-adcdev', 'plughw:3,0']

Documentation:
- doc/VOICE_TIMELINE_ANALYSIS.md (timeline investigation)
- doc/VOICE_ASSISTANT_ROOT_CAUSE_REPORT.md (technical analysis)
- doc/VOICE_ASSISTANT_FIX_PROCEDURE.md (this procedure)

Session: Session-Voice-4 (Timeline & Root Cause Analysis)
Related Sessions: Session-Voice-1, 2, 3 (parallel debugging)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**6.6 Push to remote:**
```bash
git push origin main
```

**6.7 Verify commit:**
```bash
git log --oneline -1
```

**Expected:** New commit showing voice fix

---

### Step 7: Update Documentation (5 minutes)

**7.1 Update MEMORY.md:**
```bash
nano /home/boatiq/.claude/projects/-home-boatiq/memory/MEMORY.md
```

**Add to Voice Assistant section:**
```markdown
## Voice Assistant - FIXED ✅ (2026-02-18)

**Issue:** Wake word detection broken since Feb 14, 2026
**Root Cause:** PipeWire audio server reducing microphone signal by 17×
**Fix Applied:** Changed PocketSphinx from `-inmic yes` to `-adcdev plughw:3,0`
**Status:** ✅ WORKING as of Feb 18, 2026
**Committed:** Git commit [hash from Step 6.7]

**Technical Details:**
- PipeWire interference: Sample rate conversion (48kHz→16kHz), stereo-to-mono mixing
- Signal loss: 3.1% → 0.18% (17.2× reduction)
- Solution: Direct hardware access bypasses PipeWire
- File: `/opt/d3kos/services/voice/voice-assistant-hybrid.py` line ~107

**Permanent Fix:**
```bash
# If voice breaks again:
sudo sed -i 's/"-inmic", "yes"/"-adcdev", "plughw:3,0"/' \
    /opt/d3kos/services/voice/voice-assistant-hybrid.py
sudo systemctl restart d3kos-voice
```

**Prevention:**
- Voice service files now tracked in git
- Automated deployment script available
- Test script verifies correct configuration

**Related Documents:**
- doc/VOICE_TIMELINE_ANALYSIS.md
- doc/VOICE_ASSISTANT_ROOT_CAUSE_REPORT.md
- doc/VOICE_ASSISTANT_FIX_PROCEDURE.md
```

Save and exit: Ctrl+O, Enter, Ctrl+X

**7.2 Update .session-status.md:**
```bash
cd /home/boatiq/Helm-OS
nano .session-status.md
```

**Change Session-Voice-4 status to COMPLETE:**
```markdown
| **Session-Voice-4** | Timeline & Root Cause Analysis | ✅ COMPLETE | 2026-02-18 13:00-15:00 | Claude Session-Voice-4 | 5/5 tasks |
```

**Add to Completed Sessions:**
```markdown
### Session-Voice-4: Timeline & Root Cause Analysis
- **Completed:** 2026-02-18
- **Agent ID:** Session-Voice-4
- **Domain:** Voice Assistant Debugging (Domain 3)
- **Result:** ✅ SUCCESS - Root cause identified, fix applied and committed
- **Time:** ~2 hours
- **Deliverables:**
  - VOICE_TIMELINE_ANALYSIS.md (timeline investigation)
  - VOICE_ASSISTANT_ROOT_CAUSE_REPORT.md (technical analysis)
  - VOICE_ASSISTANT_FIX_PROCEDURE.md (fix procedure)
  - voice-assistant-hybrid.py (fixed and committed to git)
- **Status:** Voice assistant working, issue RESOLVED
```

Save and exit, then commit:
```bash
git add .session-status.md
git add /home/boatiq/.claude/projects/-home-boatiq/memory/MEMORY.md
git commit -m "Session-Voice-4 COMPLETE: Voice assistant fixed and documented"
git push
```

---

## Troubleshooting

### Issue: Wake word not detected after fix

**Symptoms:**
- Service running
- PocketSphinx shows `-adcdev plughw:3,0`
- No response when saying wake words

**Checks:**

**1. Verify microphone signal:**
```bash
arecord -D plughw:3,0 -d 2 -f S16_LE -r 16000 /tmp/test.wav
sox /tmp/test.wav -n stat 2>&1 | grep "Maximum amplitude"
```

**Expected:** >0.02 (2%)

**If <0.01:** Hardware issue:
- Check Anker S330 mute button (LED should be ON)
- Check Anker S330 volume knob (turn clockwise to increase)
- Check USB connection
- Try different USB port

**2. Check PocketSphinx subprocess:**
```bash
ps aux | grep pocketsphinx_continuous
```

**Expected:** Process running with `-adcdev plughw:3,0`

**If not running:**
```bash
journalctl -u d3kos-voice -n 100 --no-pager | grep -i error
```

**Common errors:**
- "Failed to open audio device": Check if card 3 exists (`arecord -l`)
- "Permission denied": Check if d3kos user in audio group (`groups d3kos`)

**3. Check wake word threshold:**
```bash
cat /opt/d3kos/config/sphinx/wake-words.kws
```

**Expected content:**
```
HELM /1e-3/
ADVISOR /1e-3/
COUNSEL /1e-3/
```

**If threshold too strict (e.g., 1e-10):** Increase to 1e-3 or 1e-2:
```bash
sudo nano /opt/d3kos/config/sphinx/wake-words.kws
# Change all thresholds to /1e-3/
sudo systemctl restart d3kos-voice
```

**4. Manual PocketSphinx test:**
```bash
/usr/bin/pocketsphinx_continuous \
    -adcdev plughw:3,0 \
    -kws /opt/d3kos/config/sphinx/wake-words.kws \
    -dict /usr/share/pocketsphinx/model/en-us/cmudict-en-us.dict \
    -hmm /usr/share/pocketsphinx/model/en-us/en-us
```

**Say "HELM" - should see output:**
```
HELM
```

**If working manually but not via service:** Service configuration issue, check systemd unit file

---

### Issue: Service fails to start

**Symptoms:**
```bash
systemctl status d3kos-voice
# Shows: failed (code=exited, status=1/FAILURE)
```

**Solution:**

**1. Check service logs:**
```bash
journalctl -u d3kos-voice -n 100 --no-pager
```

**2. Common errors:**

**Error: "Python module not found"**
```
ModuleNotFoundError: No module named 'vosk'
```

**Fix:**
```bash
sudo pip3 install vosk piper-tts pocketsphinx
```

**Error: "Permission denied"**
```
PermissionError: [Errno 13] Permission denied: '/opt/d3kos/...'
```

**Fix:**
```bash
sudo chown -R d3kos:d3kos /opt/d3kos/services/voice/
sudo chown -R d3kos:d3kos /opt/d3kos/config/sphinx/
sudo chmod +x /opt/d3kos/services/voice/voice-assistant-hybrid.py
```

**Error: "Audio device not found"**
```
Failed to open audio device plughw:3,0
```

**Fix - Check available audio devices:**
```bash
arecord -l
```

**Find Anker S330 microphone, note card number:**
```
card 3: S330 [Anker S330], device 0: USB Audio [USB Audio]
```

**If different card number (e.g., card 4):**
```bash
sudo sed -i 's/plughw:3,0/plughw:4,0/' \
    /opt/d3kos/services/voice/voice-assistant-hybrid.py
sudo systemctl restart d3kos-voice
```

---

### Issue: Wake word detected but no TTS response

**Symptoms:**
- Wake word detected (seen in logs)
- No "Aye Aye Captain" audio playback

**Checks:**

**1. Test Piper TTS:**
```bash
echo "Test" | piper --model /opt/d3kos/models/piper/en_US-amy-medium.onnx --output_file /tmp/test.wav
aplay /tmp/test.wav
```

**Expected:** Hear "Test" spoken

**If no sound:**
- Check speaker volume (Anker S330)
- Check ALSA output device:
```bash
arecord -l  # Note speaker card number
# Modify voice-assistant-hybrid.py to use correct output device
```

**2. Check audio routing:**
```bash
pactl list sinks short  # If using PulseAudio
wpctl status            # If using PipeWire
```

---

### Issue: Fix reverts after system reboot

**Symptoms:**
- Voice works after manual fix
- After reboot, voice broken again
- File shows `-inmic yes` again

**Root Cause:** File overwritten by deployment or configuration management

**Solution:**

**1. Verify fix is committed to git:**
```bash
git log --oneline | grep -i voice
```

**Expected:** Recent commit with voice fix

**If not committed:** Re-do Step 6 (Commit to Git)

**2. Check for automated deployment:**
```bash
crontab -l  # Check for cron jobs
systemctl list-timers  # Check for systemd timers
```

**If deployment script exists:** Update it to pull from git:
```bash
cd /home/boatiq/Helm-OS && git pull
sudo cp opt/d3kos/services/voice/voice-assistant-hybrid.py /opt/d3kos/services/voice/
sudo systemctl restart d3kos-voice
```

**3. Create automated fix script:**

**/opt/d3kos/scripts/ensure-voice-fix.sh:**
```bash
#!/bin/bash
# Ensure voice assistant uses direct hardware access

if grep -q '"-inmic", "yes"' /opt/d3kos/services/voice/voice-assistant-hybrid.py; then
    echo "Voice fix not applied, applying now..."
    sudo sed -i.bak 's/"-inmic", "yes"/"-adcdev", "plughw:3,0"/' \
        /opt/d3kos/services/voice/voice-assistant-hybrid.py
    sudo systemctl restart d3kos-voice
    echo "Voice fix applied, service restarted"
else
    echo "Voice fix already in place"
fi
```

**Make executable:**
```bash
sudo chmod +x /opt/d3kos/scripts/ensure-voice-fix.sh
```

**Add to boot:**
```bash
sudo nano /etc/systemd/system/d3kos-voice.service
```

**Add before ExecStart:**
```
ExecStartPre=/opt/d3kos/scripts/ensure-voice-fix.sh
```

---

## Rollback Procedure

**If fix causes issues, revert to backup:**

```bash
# Find backup file
ls -lt /opt/d3kos/services/voice/voice-assistant-hybrid.py.bak.*

# Restore most recent backup
sudo cp /opt/d3kos/services/voice/voice-assistant-hybrid.py.bak.[timestamp] \
        /opt/d3kos/services/voice/voice-assistant-hybrid.py

# Restart service
sudo systemctl restart d3kos-voice

# Verify
ps aux | grep pocketsphinx_continuous
```

---

## Automated Fix Script

**Create automated script for future use:**

**/opt/d3kos/scripts/fix-voice-assistant.sh:**
```bash
#!/bin/bash
# Automated Voice Assistant Fix Script
# Fixes PipeWire interference issue
# Session-Voice-4, 2026-02-18

set -e

echo "=== d3kOS Voice Assistant Fix ==="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Do not run as root"
    exit 1
fi

# Backup current file
BACKUP="/opt/d3kos/services/voice/voice-assistant-hybrid.py.bak.$(date +%Y%m%d-%H%M%S)"
echo "1. Creating backup: $BACKUP"
sudo cp /opt/d3kos/services/voice/voice-assistant-hybrid.py "$BACKUP"

# Apply fix
echo "2. Applying fix..."
sudo sed -i 's/"-inmic", "yes"/"-adcdev", "plughw:3,0"/' \
    /opt/d3kos/services/voice/voice-assistant-hybrid.py

# Verify fix
if grep -q '"-adcdev", "plughw:3,0"' /opt/d3kos/services/voice/voice-assistant-hybrid.py; then
    echo "   ✅ Fix applied successfully"
else
    echo "   ❌ Fix failed to apply"
    sudo cp "$BACKUP" /opt/d3kos/services/voice/voice-assistant-hybrid.py
    exit 1
fi

# Restart service
echo "3. Restarting voice service..."
sudo systemctl restart d3kos-voice
sleep 2

# Verify service
if systemctl is-active --quiet d3kos-voice; then
    echo "   ✅ Service running"
else
    echo "   ❌ Service failed to start"
    sudo cp "$BACKUP" /opt/d3kos/services/voice/voice-assistant-hybrid.py
    sudo systemctl restart d3kos-voice
    exit 1
fi

# Verify PocketSphinx
if ps aux | grep pocketsphinx_continuous | grep -q "adcdev plughw:3,0"; then
    echo "   ✅ PocketSphinx using direct hardware access"
else
    echo "   ⚠️  PocketSphinx not using expected device"
fi

echo
echo "=== Fix Complete ==="
echo "Test by saying: HELM"
echo "Expected response: Aye Aye Captain"
```

**Install script:**
```bash
sudo mkdir -p /opt/d3kos/scripts
sudo nano /opt/d3kos/scripts/fix-voice-assistant.sh
# Paste above content
sudo chmod +x /opt/d3kos/scripts/fix-voice-assistant.sh
```

**Usage:**
```bash
/opt/d3kos/scripts/fix-voice-assistant.sh
```

---

## Verification Checklist

After completing fix procedure, verify:

- [ ] File contains `-adcdev plughw:3,0` (not `-inmic yes`)
- [ ] Service running: `systemctl status d3kos-voice`
- [ ] PocketSphinx subprocess running with correct args
- [ ] Microphone signal strength >2% (direct hardware test)
- [ ] Wake word "HELM" detected and logged
- [ ] TTS response "Aye Aye Captain" plays
- [ ] Full query processing works (e.g., "What is the RPM?")
- [ ] Fix committed to git repository
- [ ] MEMORY.md updated with fix information
- [ ] .session-status.md marked Session-Voice-4 as COMPLETE

---

## Success Criteria

✅ **Voice assistant is considered FIXED when:**
1. Wake word detection working for all 3 wake words (HELM, ADVISOR, COUNSEL)
2. TTS response playing correctly ("Aye Aye Captain")
3. Full query processing operational (AI responses)
4. Fix persists across service restarts
5. Fix committed to git repository
6. Documentation updated

---

**Document Version:** 1.0
**Last Updated:** 2026-02-18
**Author:** Claude Session-Voice-4
**Related Documents:**
- `VOICE_TIMELINE_ANALYSIS.md` - Timeline investigation
- `VOICE_ASSISTANT_ROOT_CAUSE_REPORT.md` - Technical analysis
- `.session-status.md` - Session coordination
