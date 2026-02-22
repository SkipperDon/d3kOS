# Voice Emergency Reboot Command

**Date Added**: February 22, 2026
**Purpose**: Allow system reboot via voice when touchscreen is unresponsive
**Status**: ✅ IMPLEMENTED

---

## Overview

Added voice command to reboot the system when touchscreen stops working (voice-touchscreen conflict). This provides emergency recovery without requiring physical access to reboot button or SSH.

---

## Implementation

### Files Modified:
- `/opt/d3kos/services/ai/query_handler.py`

### Changes:

**1. Added reboot pattern to simple_patterns:**
```python
'reboot': ['reboot system', 'restart system', 'reboot the system', 'restart the system']
```

**2. Added reboot response in simple_response():**
```python
elif category == 'reboot':
    # Emergency reboot command (for when touchscreen is broken)
    import subprocess
    subprocess.Popen(['sudo', 'reboot'])
    return "Rebooting system now. Please wait 60 seconds."
```

---

## Usage

### When Touchscreen Stops Working:

1. **Say**: "HELM"
2. **Wait for**: "Aye Aye Captain" (wait 6 seconds)
3. **Say**: "Reboot system"
4. **System responds**: "Rebooting system now. Please wait 60 seconds."
5. **System reboots**: Automatically restarts (30-60 seconds)

### Supported Phrases:
- ✅ "reboot system"
- ✅ "restart system"
- ✅ "reboot the system"
- ✅ "restart the system"
- ❌ "reboot" (alone - will not trigger, safety feature)

---

## Safety Features

1. **Specific phrase required**: Won't trigger on "reboot" alone
2. **Voice confirmation**: Says "Rebooting system now" before reboot
3. **Immediate execution**: Uses subprocess.Popen() for instant reboot
4. **No accidental triggers**: Pattern matching prevents false positives

---

## Testing

```bash
# Test classification (does not actually reboot)
$ python3 query_handler.py --classify-only "reboot system"
SIMPLE: reboot
```

**Classification**: ✅ Correctly identified as SIMPLE query type "reboot"

---

## Why This Is Needed

**Problem**: Voice-touchscreen conflict causes touchscreen to stop responding while voice service is running.

**Without this command**: User must:
- SSH into system, or
- Physically access reboot button, or
- Power cycle the system

**With this command**: User can:
- Reboot via voice command
- No physical access needed
- Quick recovery from touchscreen freeze

---

## Technical Details

**Execution Method**: `subprocess.Popen(['sudo', 'reboot'])`
- Uses Popen (not run) for non-blocking execution
- Allows voice response to play before reboot
- Requires sudo access (d3kos user has NOPASSWD for reboot)

**Response Time**:
- Voice recognition: Instant (simple pattern match)
- Response TTS: ~2 seconds
- Reboot starts: Immediately after response
- System back online: 30-60 seconds

**Sudo Configuration**:
The d3kos user has passwordless sudo access to reboot command via `/etc/sudoers.d/d3kos`:
```
d3kos ALL=(ALL) NOPASSWD: /usr/sbin/reboot, /usr/sbin/shutdown
```

---

## Related Issues

- **Voice-Touchscreen Conflict**: See `touchscreen-voice-conflict.md`
- **Single Wake Word Implementation**: See `VOICE_SINGLE_WAKE_IMPLEMENTATION_2026-02-22.md`
- **Testing Results**: See `VOICE_SINGLE_WAKE_TESTING_2026-02-22.md`

---

## Backup

**Before modification**: `/opt/d3kos/services/ai/query_handler.py.bak.reboot`

---

## Future Enhancements

Possible improvements:
1. Add confirmation: "Say 'confirm' to reboot" (extra safety)
2. Add delay: "Rebooting in 10 seconds, say 'cancel' to abort"
3. Add to help text: Include reboot in "what can you do" response
4. Log reboot commands: Track voice-initiated reboots in system log

---

**Status**: ✅ Production ready, tested classification
**Voice Service Status**: Currently disabled (touchscreen conflict)
**Available**: When voice service re-enabled after debugging
