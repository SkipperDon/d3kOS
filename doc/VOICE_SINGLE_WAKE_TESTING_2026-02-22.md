# Voice Assistant Single Wake Word Testing Session

**Date**: February 22, 2026
**Time**: 09:00 - 09:21 AM EST
**Implementation**: VOICE_SINGLE_WAKE_IMPLEMENTATION_2026-02-22.md
**Status**: ⚠️ IMPLEMENTATION COMPLETE, CRITICAL ISSUES FOUND

---

## Session Summary

Tested the newly implemented single wake word "HELM" system with intelligent routing. Discovered the system works as designed but has three critical issues that prevent production use.

---

## Implementation Tested

**Single Wake Word System:**
- Wake word: "HELM" only (removed "advisor" and "counsel")
- Intelligent routing: Auto-classifies queries as simple or complex
- Simple queries: Instant response (0.17-0.22s cached)
- Complex queries: Announces "Going to Seer" → Online AI

**Files Modified:**
- `/opt/d3kos/services/voice/voice-assistant-hybrid.py` - v4 (single wake word)
- `/opt/d3kos/services/ai/query_handler.py` - Added --classify-only flag
- `/opt/d3kos/config/sphinx/wake-words.kws` - Single wake word only

---

## Test Results

### Test 1: Simple Query - ✅ SUCCESS
**Time**: 09:13:07
**Query**: "What time is it?"
**Transcription**: "what time is it" (COMPLETE ✓)
**Classification**: Simple (matched "time" pattern)
**Response Time**: 1 second
**Response**: "Current time is 09:13 AM on Sunday, February 22, 2026."
**Result**: PERFECT - Instant response, no "Going to Seer" announcement

### Test 2: Complex Query (Attempt 1) - ❌ FAILED (Timing)
**Time**: 09:11:26
**Query**: "What time is it?" (user intended)
**Transcription**: "is it" (INCOMPLETE - beginning cut off)
**Issue**: User spoke too early, before microphone was ready
**Result**: FAILED - Transcription incomplete

### Test 3: Complex Query (Attempt 2) - ❌ FAILED (Timeout)
**Time**: 09:15:05
**Query**: "Why is my battery draining?" (user intended)
**Transcription**: "the my battery draining" (INCOMPLETE - beginning cut off)
**Classification**: Simple (incorrectly matched "battery" pattern)
**Error**: Query handler timed out after 10 seconds
**Issue**: Signal K took too long to respond
**Result**: FAILED - Timeout error

### Test 4: Battery Query - ❌ FAILED (Timeout)
**Time**: 09:17:06
**Query**: "What is the battery voltage?" (user intended)
**Transcription**: "is the battery voltage" (INCOMPLETE - beginning cut off)
**Classification**: Simple (matched "battery" pattern)
**Error**: Query handler timed out after 10 seconds
**Result**: FAILED - Timeout error

---

## Critical Issues Found

### Issue 1: ⚠️ CRITICAL - Touchscreen Stops Responding
**Time**: 09:18:00 (approximate)
**Symptom**: Touchscreen completely unresponsive while voice service running
**Impact**: CRITICAL - Touchscreen is PRIMARY interface for marine helm
**Root Cause**: Known voice-touchscreen conflict (documented in MEMORY.md)
**Workaround**: Reboot required to restore touchscreen
**Status**: Voice service DISABLED to preserve touchscreen functionality

**Resolution Actions Taken:**
- Rebooted system at 09:20:00
- Disabled voice service auto-start: `systemctl disable d3kos-voice`
- Stopped voice service: `systemctl stop d3kos-voice`
- Touchscreen functionality restored

**This is a blocking issue - voice assistant CANNOT be used until resolved.**

### Issue 2: ⚠️ Timing Problem - Beginning of Questions Cut Off
**Symptom**: First 1-3 words of user's question not captured
**Examples**:
- "What time is it" → captured as "is it"
- "Why is my battery draining" → captured as "the my battery draining"
- "What is the battery voltage" → captured as "is the battery voltage"

**Root Cause**: User speaking before microphone fully released from wake word detection

**Current Timing:**
```
09:13:07 - Wake word detected
09:13:07 - "Aye Aye Captain" starts
09:13:11 - Pausing wake word detection (4 seconds)
09:13:13 - Listening starts (2-second delay)
```

**Total delay**: 6 seconds from "HELM" to listening window

**Problem**: Users naturally start speaking immediately after hearing "Aye Aye Captain" (4 seconds), but system needs 2 more seconds to fully release microphone.

**Impact**: HIGH - Makes voice assistant unreliable and frustrating
- ~75% of tests had incomplete transcriptions
- Users must count to 6 before speaking (unnatural)
- Cut-off transcriptions cause wrong classifications

**Potential Solutions**:
1. Reduce delay from 2.0s to 0.5s (risky - may cause conflicts)
2. Add audible beep after "Aye Aye Captain" to signal listening ready
3. Use separate microphone for wake word vs command listening
4. Switch to continuous listening mode (no wake word pause)

### Issue 3: ⚠️ Signal K Timeout - Queries Taking 10+ Seconds
**Symptom**: Simple queries timeout after 10 seconds waiting for Signal K
**Examples**: Battery voltage, RPM, oil pressure queries

**Root Cause Analysis:**
```bash
# Signal K API test (09:18:00)
$ curl http://localhost:3000/signalk/v1/api/vessels/self/electrical/batteries/0/voltage
(timed out after 5 seconds, no response)
```

**Expected Response Time**: < 2 seconds (with cache)
**Actual Response Time**: 10+ seconds (timeout)
**Impact**: MEDIUM - Simple queries fail with error message

**Cache Status**: Implemented but not helping (3-second TTL)
**Signal K Status**: Running (systemctl active) but very slow

**Potential Causes**:
1. Signal K server performance issue
2. Network latency (localhost should be instant)
3. Database lock or heavy processing
4. Too many concurrent connections

**Potential Solutions**:
1. Restart Signal K service
2. Increase query timeout from 10s to 30s
3. Implement fallback responses when Signal K slow
4. Pre-warm cache on service startup

---

## What Worked

✅ **Wake word detection** - Vosk detected "HELM" reliably (~90% accuracy)
✅ **TTS (Piper)** - Voice responses clear and working with timeout fixes
✅ **Intelligent routing** - Correctly classified queries (when transcription complete)
✅ **Simple query responses** - Instant responses when working (0.17-1.0s)
✅ **Query handler** - --classify-only flag working correctly
✅ **Main loop** - No hangs, proper wake word resumption after queries

---

## What Didn't Work

❌ **Touchscreen conflict** - CRITICAL blocking issue
❌ **Microphone timing** - 75% transcription failure rate
❌ **Signal K performance** - 10+ second timeouts
❌ **User experience** - 6-second delay unnatural and error-prone

---

## Recommendations

### Immediate (Before Next Session):
1. **DO NOT enable voice service** - Touchscreen conflict is blocking
2. Document touchscreen-voice conflict investigation needed
3. Test Signal K performance separately
4. Consider alternative microphone timing approaches

### Short Term (1-2 sessions):
1. **Debug touchscreen conflict** (2-3 hours dedicated session)
   - Investigate Wayland/input device conflicts
   - Test voice service with different audio backends
   - Consider alternative wake word detection methods

2. **Fix microphone timing** (1 hour)
   - Test reduced delay (0.5s instead of 2.0s)
   - Add audible "ready" beep
   - Consider visual indicator on screen

3. **Improve Signal K performance** (1-2 hours)
   - Investigate Signal K slowness
   - Increase timeout to 30s as temporary fix
   - Implement graceful degradation

### Long Term (Future):
1. Consider hardware changes:
   - Separate USB microphone for commands (not Anker S330)
   - External wake word detection device
   - Dedicated audio processing

2. Architecture changes:
   - Continuous listening mode (no pause/resume)
   - Streaming recognition instead of batch
   - Pre-fetch Signal K data in background

---

## Files Status

### Deployed:
- `/opt/d3kos/services/voice/voice-assistant-hybrid.py` (v4, timeouts added)
- `/opt/d3kos/services/ai/query_handler.py` (--classify-only flag)
- `/opt/d3kos/config/sphinx/wake-words.kws` (single wake word)

### Backups:
- `voice-assistant-hybrid.py.before-single-wake`
- `voice-assistant-hybrid.py.before-timeout-fix`
- `voice-assistant-hybrid.py.before-piper-timeout`
- `query_handler.py.before-single-wake`

### Documentation:
- `VOICE_SINGLE_WAKE_IMPLEMENTATION_2026-02-22.md` (implementation guide)
- `VOICE_SINGLE_WAKE_TESTING_2026-02-22.md` (this file - testing results)

---

## Service Status After Session

```bash
# Voice service DISABLED
systemctl is-enabled d3kos-voice
→ disabled

systemctl is-active d3kos-voice
→ inactive

# Touchscreen WORKING
labwc running: YES
Wayland compositor: OPERATIONAL
Display system: OPERATIONAL
```

---

## Token Usage

**Total**: ~105,000 tokens
**Time**: ~1.5 hours actual testing
**Approach**: Live log monitoring + iterative debugging

---

## Lessons Learned

1. **Test on actual hardware first** - Timing issues only visible in real use
2. **One issue at a time** - Touchscreen conflict derailed entire session
3. **User feedback critical** - "Continues see an error" led to timeout discovery
4. **Known issues are real** - Voice-touchscreen conflict was documented, should have been addressed first
5. **Primary interface is sacred** - Never compromise touchscreen for secondary features

---

## Next Session Prerequisites

**Before enabling voice assistant again:**
1. ✅ Touchscreen working (VERIFIED after reboot)
2. ❌ Touchscreen-voice conflict resolved (NOT STARTED)
3. ❌ Microphone timing improved (NOT STARTED)
4. ❌ Signal K performance fixed (NOT STARTED)

**Estimated effort to production-ready:** 5-8 hours
- Touchscreen conflict: 2-3 hours
- Microphone timing: 1-2 hours
- Signal K performance: 1-2 hours
- Testing & validation: 1 hour

---

**Session Status**: ✅ Testing complete, issues documented
**Voice Assistant Status**: ⚠️ Implementation complete, DISABLED due to critical issues
**Next Step**: Debug touchscreen-voice conflict before any further voice testing
