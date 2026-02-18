# Voice Assistant Timeline Analysis
**Session:** Session-Voice-4 (Timeline & Root Cause Analysis)
**Date:** 2026-02-18
**Investigator:** Claude Session-Voice-4
**Status:** Task 1 Complete - Timeline Established

---

## Executive Summary

**Finding:** Voice assistant wake word detection broke on Feb 14, 2026. A fix was identified and successfully applied on Feb 17, 2026, but was **NOT persisted** (not committed to git, possibly not restarted properly). As of Feb 18, 2026, voice is broken again.

**Root Cause (Identified Feb 17):** PipeWire audio server reducing microphone signal by **17× (from 3.1% to 0.18%)** when using ALSA default device.

**Fix (Applied Feb 17, Tested Successfully):** Changed PocketSphinx from `-inmic yes` (ALSA default via PipeWire) to `-adcdev plughw:3,0` (direct hardware access).

**Critical Issue:** Fix was never committed to git repository, making it non-persistent across deployments or service restarts.

---

## Timeline of Events

### BEFORE Feb 14, 2026: Working State ✅

**Evidence:**
- MEMORY.md: "System Was Working Before 2026-02-14"
- .session-status.md (line 14): "CRITICAL ISSUE since Feb 14"
- SESSION_2026-02-17_UI_TESTING_FIXES.md: User quote "it once worked well now for some reason it not working"

**System State:**
- Voice assistant detecting wake words: "helm", "advisor", "counsel"
- PocketSphinx running and outputting wake word detections
- Response time: Normal (wake word → "Aye Aye Captain" → answer)

---

### Feb 14, 2026: Voice Assistant Breaks ❌

**What Broke:**
- Wake word detection stopped working
- PocketSphinx service runs but doesn't detect spoken wake words
- User can say "HELM" repeatedly with no response

**What Was NOT Broken:**
- PocketSphinx process runs correctly
- Microphone captures audio (arecord works)
- Text-based AI assistant continues working
- All other system services operational

**Potential Causes (Investigated Feb 17):**
1. System update (apt upgrade)
2. PipeWire configuration change
3. Audio routing change
4. PocketSphinx package update
5. Manual configuration change

**Git History:**
- ✅ **VERIFIED:** No git commits on Feb 14-15, 2026
- Breakage NOT caused by code deployment from git

---

### Feb 16, 2026: AI Optimization Work (Unrelated)

**Git Commit:** a57542c - "Add Voice/AI optimization and multi-session coordination system"

**What Changed:**
- Signal K caching added (3s TTL)
- AI query patterns expanded (8→13 types)
- Phi-2 LLM removed (freed 1.7GB storage)
- Multi-session coordination files added

**Files Modified:**
- `/opt/d3kos/services/ai/signalk_client.py` (on Pi, not in git)
- `/opt/d3kos/services/ai/ai_api.py` (on Pi, not in git)
- `/opt/d3kos/services/ai/query_handler.py` (on Pi, not in git)
- `.session-status.md`, `.domain-ownership.md`, `CLAUDE.md`, `MASTER_SYSTEM_SPEC.md` (in git)

**Voice Impact:** ❌ NONE - This was AI text query optimization, not voice/wake word detection

---

### Feb 17, 2026: Root Cause Found & Fix Applied ✅

**Session:** UI Testing & Fixes (documented in SESSION_2026-02-17_UI_TESTING_FIXES.md)

**Root Cause Discovery:**

**Problem:** PipeWire audio server reducing microphone signal by 17×

**Evidence:**
```bash
# Direct hardware access (bypassing PipeWire)
arecord -D plughw:3,0 -d 2 -f S16_LE -r 16000 /tmp/test.wav
sox /tmp/test.wav -n stat 2>&1 | grep "Maximum amplitude"
# Result: 3.1% signal strength

# Via PipeWire (ALSA default device)
arecord -d 2 -f S16_LE -r 16000 /tmp/test.wav
sox /tmp/test.wav -n stat 2>&1 | grep "Maximum amplitude"
# Result: 0.18% signal strength

# Signal Loss: 3.1% / 0.18% = 17.2× reduction!
```

**Why PipeWire Reduces Signal:**
- Sample rate conversion (48kHz → 16kHz)
- Stereo to mono mixing
- Volume processing pipeline
- Buffering and latency compensation

**Fix Applied:**

**File Modified:** `/opt/d3kos/services/voice/voice-assistant-hybrid.py`

**Change:**
```python
# BEFORE (broken - uses ALSA default via PipeWire)
sphinx_cmd = [
    "/usr/bin/pocketsphinx_continuous",
    "-inmic", "yes",  # ← Uses ALSA default (goes through PipeWire)
    "-kws", kws_file,
    "-dict", "/usr/share/pocketsphinx/model/en-us/cmudict-en-us.dict",
    "-hmm", "/usr/share/pocketsphinx/model/en-us/en-us",
    "-logfn", "/dev/null"
]

# AFTER (working - direct hardware access)
sphinx_cmd = [
    "/usr/bin/pocketsphinx_continuous",
    "-adcdev", "plughw:3,0",  # ← Direct hardware access (bypasses PipeWire)
    "-kws", kws_file,
    "-dict", "/usr/share/pocketsphinx/model/en-us/cmudict-en-us.dict",
    "-hmm", "/usr/share/pocketsphinx/model/en-us/en-us",
    "-logfn", "/dev/null"
]
```

**Testing (Feb 17):**
```
User said: "HELM"
Result: ✅ Voice assistant detected wake word
Response: "Aye Aye Captain"
Status: WORKING
```

**Backups Created:**
- `/opt/d3kos/services/voice/voice-assistant-hybrid.py.bak.pipewire`
- `/opt/d3kos/config/sphinx/wake-words.kws.bak.1e10`

**Git Commit:**
- ❌ **NOT COMMITTED** - Fix was applied directly on Pi but never pushed to git
- ❌ **NOT DOCUMENTED** - No mention of git commit in SESSION_2026-02-17_UI_TESTING_FIXES.md

---

### Feb 17, 2026: Git Commits (No Voice Changes)

**Commits on Feb 17:**
1. `c786ca2` - "Session B: Marine Vision Notifications (Phase 2.6) - Complete"
2. `238a7fe` - "Session B Post-Deployment: Fix vcan0 simulator error"
3. `3e11544` - "Session B Post-Deployment: Fix GPS configuration"

**Files Modified:**
- Marine Vision notification system
- Signal K settings (vcan0, gpsd)
- GPS configuration
- ❌ **NO voice-related files**

---

### Feb 18, 2026: Voice Broken Again - Parallel Debug Sessions Initiated ❌

**.session-status.md Updated:** "CRITICAL ISSUE since Feb 14"

**4 Parallel Debug Sessions Launched:**
1. **Session-Voice-1:** Audio Hardware & Signal Path (0/6 tasks)
2. **Session-Voice-2:** PocketSphinx Config & Testing (0/5 tasks)
3. **Session-Voice-3:** Alternative Wake Word Engines (🟢 ACTIVE, 0/4 tasks)
4. **Session-Voice-4:** Timeline & Root Cause Analysis (this session, 0/5 tasks)

**Git Commits on Feb 18 (AM):**
1. `92cebc4` (08:53) - "Distribution Prep Session 1: Installation scripts"
2. `ab9b192` (08:53) - "Distribution Prep Session 2: Configuration & service scripts"
3. `bda42b6` (08:56) - "Update .session-status.md: Mark Session-Dist-2 as COMPLETE"
4. `240cfe3` (08:57) - "Distribution Prep Session 3: Testing & validation suite"
5. `5527901` (09:11) - "Distribution Prep Session 4: Documentation & packaging"

**Files Modified:**
- Distribution preparation scripts and documentation
- Test suites (including test-known-issues.sh for voice)
- Installation guides, troubleshooting guides
- ❌ **NO voice-related service files**

**Implication:** Voice fix from Feb 17 was lost or never persisted properly.

---

## Root Cause Analysis

### Why Voice Broke on Feb 14

**Most Likely Cause:** System update or PipeWire configuration change

**Supporting Evidence:**
1. No git commits on Feb 14-15 (not code deployment)
2. User statement: "it once worked well" (implies external change)
3. PipeWire interference discovered (17× signal reduction)
4. Similar timing to other system changes

**Requires Investigation (Next Tasks):**
- Check `/var/log/apt/history.log` for Feb 14 system updates
- Check for PipeWire, ALSA, PocketSphinx, kernel updates
- Check for audio configuration changes

### Why Voice Fix Didn't Persist (Feb 17 → Feb 18)

**Critical Failure:** Fix was applied but not made persistent

**Possible Reasons:**

1. **Service Not Restarted Properly**
   - Fix applied to file: ✅
   - Service restarted: ❓ (not documented)
   - If service not restarted, old code still running in memory

2. **Fix Not Committed to Git**
   - File modified on Pi: ✅
   - Committed to git: ❌ **VERIFIED - NOT COMMITTED**
   - Pushed to remote: ❌
   - Any deployment from git would overwrite fix

3. **System Reboot Lost Changes**
   - If file was modified but service not set to auto-load modified version
   - Systemd may have cached old service configuration

4. **PipeWire Configuration Changed Again**
   - If PipeWire updated or reconfigured after Feb 17
   - Could re-break even with fix in place

5. **Manual Reversion During Troubleshooting**
   - Feb 17 session involved multiple attempts
   - Possible fix was applied, tested, then reverted by mistake
   - Backup files exist but may not reflect final state

---

## Git Repository Analysis

### Voice-Related Files in Git

**Search Command:**
```bash
git log --all --name-only --oneline | grep -i "voice\|sphinx\|pocketsphinx"
```

**Result:** ❌ **NO voice-related service files tracked in git repository**

**Implication:** Voice assistant code lives ONLY on the Pi at:
- `/opt/d3kos/services/voice/voice-assistant-hybrid.py`
- `/opt/d3kos/config/sphinx/wake-words.kws`

**Risk:** Any changes made directly on Pi are NOT backed up to git and can be lost.

### Commits Since Voice Broke (Feb 14-18)

| Date | Commit | Description | Voice Impact |
|------|--------|-------------|--------------|
| Feb 16 | a57542c | AI optimization, multi-session | ❌ None |
| Feb 17 | c786ca2 | Marine Vision notifications | ❌ None |
| Feb 17 | 238a7fe | Fix vcan0 simulator error | ❌ None |
| Feb 17 | 3e11544 | Fix GPS configuration | ❌ None |
| Feb 18 | 92cebc4 | Distribution Prep Session 1 | ❌ None |
| Feb 18 | ab9b192 | Distribution Prep Session 2 | ❌ None |
| Feb 18 | bda42b6 | Update session status | ❌ None |
| Feb 18 | 240cfe3 | Distribution Prep Session 3 | ❌ None |
| Feb 18 | 5527901 | Distribution Prep Session 4 | ❌ None |

**Finding:** No git commits modified voice-related code between Feb 14-18.

---

## Critical Gaps in Documentation

### 1. Voice Fix Not Committed (Feb 17)

**What Should Have Happened:**
```bash
# After applying fix on Pi
cd /home/boatiq/Helm-OS
git add <voice-assistant-hybrid.py if tracked>
git commit -m "Fix voice assistant: Direct hardware access to bypass PipeWire interference"
git push
```

**What Actually Happened:**
- Fix applied directly on Pi: ✅
- Tested successfully: ✅
- Service restarted: ❓ Not documented
- Committed to git: ❌ **NOT DONE**
- Documented in session notes: ⚠️ Partial (mentioned in SESSION_2026-02-17_UI_TESTING_FIXES.md but no commit info)

### 2. Service Restart Not Documented

**SESSION_2026-02-17_UI_TESTING_FIXES.md** does not mention:
- `sudo systemctl restart d3kos-voice` after fix
- Verification that service loaded new code
- Check that PocketSphinx subprocess restarted with new `-adcdev` parameter

### 3. Voice Service Files Not in Git

**Current State:**
- Voice service code lives only on Pi
- No version control for voice assistant
- Changes can be lost with no backup

**Recommendation:**
- Add `/opt/d3kos/services/voice/` to git repository
- Track all service files, not just documentation

---

## Next Investigation Steps

### Task 2: System Changes Investigation

**Required:**
1. Check `/var/log/apt/history.log` for Feb 14 updates
2. Check for PipeWire, ALSA, PocketSphinx package updates
3. Check for kernel updates
4. Compare package versions before/after Feb 14

### Task 3: Configuration Drift Analysis

**Required:**
1. Check current state of `/opt/d3kos/services/voice/voice-assistant-hybrid.py`
2. Verify if Feb 17 fix (`-adcdev plughw:3,0`) is still in place
3. Check for PipeWire configuration changes
4. Check for audio device changes (USB renumbering)

### Task 4: Service State Analysis

**Required:**
1. Verify d3kos-voice service is running
2. Check PocketSphinx subprocess is running
3. Test microphone signal strength (direct vs PipeWire)
4. Check service logs for errors

### Task 5: Root Cause Determination

**Required:**
1. Synthesize findings from Sessions 1, 2, 3, 4
2. Determine exact cause of Feb 14 breakage
3. Determine why Feb 17 fix didn't persist
4. Create permanent fix procedure

---

## Preliminary Recommendations

### Immediate Actions (Before Final Fix)

1. **Verify Current State**
   - SSH to Pi: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`
   - Check voice service: `systemctl status d3kos-voice`
   - Check file: `cat /opt/d3kos/services/voice/voice-assistant-hybrid.py | grep -E "inmic|adcdev"`
   - Determine if fix is in place or reverted

2. **Test Signal Strength**
   ```bash
   # Direct hardware
   arecord -D plughw:3,0 -d 2 -f S16_LE -r 16000 /tmp/test1.wav
   sox /tmp/test1.wav -n stat 2>&1 | grep "Maximum amplitude"

   # Via PipeWire
   arecord -d 2 -f S16_LE -r 16000 /tmp/test2.wav
   sox /tmp/test2.wav -n stat 2>&1 | grep "Maximum amplitude"
   ```

3. **Check System Updates**
   ```bash
   grep "2026-02-14" /var/log/apt/history.log
   ```

### Permanent Fix Strategy

1. **Apply Fix to Voice Service**
   - Change `-inmic yes` to `-adcdev plughw:3,0`
   - Create backup before modifying

2. **Restart Service Properly**
   ```bash
   sudo systemctl restart d3kos-voice
   sudo systemctl status d3kos-voice
   ps aux | grep pocketsphinx  # Verify subprocess running with new args
   ```

3. **Test Wake Word Detection**
   - Say "HELM" and verify response
   - Test all 3 wake words: helm, advisor, counsel

4. **Commit to Git**
   - Add voice service files to repository
   - Commit with clear message
   - Push to remote

5. **Document in MEMORY.md**
   - Update voice assistant section
   - Mark issue as RESOLVED
   - Add permanent fix instructions

---

## Files Referenced in This Analysis

**Read:**
- `/home/boatiq/.claude/projects/-home-boatiq/memory/MEMORY.md`
- `/home/boatiq/Helm-OS/.session-status.md`
- `/home/boatiq/Helm-OS/doc/SESSION_2026-02-17_UI_TESTING_FIXES.md`

**Created:**
- `/home/boatiq/Helm-OS/doc/VOICE_TIMELINE_ANALYSIS.md` (this file)

**To Be Created:**
- `/home/boatiq/Helm-OS/doc/VOICE_ASSISTANT_ROOT_CAUSE_REPORT.md` (after Task 5)
- `/home/boatiq/Helm-OS/doc/VOICE_ASSISTANT_FIX_PROCEDURE.md` (after Task 5)
- `/opt/d3kos/scripts/fix-voice-assistant.sh` (automated fix script)

---

## Task 1 Status: ✅ COMPLETE

**Timeline Established:**
- Voice working: BEFORE Feb 14, 2026
- Voice broke: Feb 14, 2026 (no git commits)
- Root cause found: Feb 17, 2026 (PipeWire 17× signal reduction)
- Fix applied & tested: Feb 17, 2026 (successful)
- Fix NOT committed: Feb 17, 2026 (critical failure)
- Voice broken again: Feb 18, 2026 (fix lost or not persistent)

**Next Task:** Task 2 - System Changes Investigation (check apt logs, package updates)

---

**Document Version:** 1.0
**Last Updated:** 2026-02-18
**Author:** Claude Session-Voice-4
**Session:** Voice Assistant Timeline & Root Cause Analysis
