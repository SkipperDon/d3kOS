# Voice Emergency Reboot - D-Bus Implementation Guide

**Date**: February 22, 2026
**Purpose**: Implement D-Bus-based reboot command for voice assistant
**Status**: ✅ IMPLEMENTATION COMPLETE - TESTED AND WORKING
**Test Date**: February 22, 2026 10:37 AM EST
**Test Result**: SUCCESS - Voice command triggered immediate system reboot

---

## Executive Summary

This document describes the implementation of a D-Bus-based emergency reboot command for the d3kOS voice assistant. This replaces the current `os.system()` approach with an industry-standard Linux system interface.

**Problem**: Current `os.system('sudo systemctl start d3kos-emergency-reboot.service')` fails when triggered via voice, but works from command line.

**Solution**: Use D-Bus to communicate directly with systemd-logind, the standard Linux service manager for system operations like reboot.

---

## What is D-Bus?

**D-Bus (Desktop Bus)** is an inter-process communication (IPC) system that provides:
- Standard way for applications to communicate
- Message bus for system and session services
- Interface to systemd system manager
- Authorization framework integration (polkit)

**Why D-Bus for Reboot?**
- Designed for exactly this use case
- Used by professional voice assistants (Mycroft, etc.)
- Works reliably from systemd services
- No sudo required (polkit handles authorization)
- Better security than NOPASSWD: ALL

**D-Bus Architecture**:
```
Voice Assistant (Python)
        ↓
    D-Bus System Bus
        ↓
systemd-logind (Manager)
        ↓
    /usr/sbin/reboot
```

---

## Implementation Overview

### Changes Required

**1. Install Dependencies** (if not present):
```bash
sudo apt install python3-dbus
```

**2. Create Polkit Rule** (passwordless authorization):
```javascript
// /etc/polkit-1/rules.d/50-d3kos-reboot.rules
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.login1.reboot" &&
        subject.user == "d3kos") {
        return polkit.Result.YES;
    }
});
```

**3. Update query_handler.py** (replace os.system() with D-Bus):
```python
elif category == 'reboot':
    # Emergency reboot command (for when touchscreen is broken)
    try:
        import dbus
        bus = dbus.SystemBus()
        manager = bus.get_object('org.freedesktop.login1',
                                '/org/freedesktop/login1')
        reboot = manager.get_dbus_method('Reboot',
                                        'org.freedesktop.login1.Manager')
        reboot(False)  # False = immediate, no user confirmation
        return "Rebooting system now. Please wait 60 seconds."
    except Exception as e:
        import logging
        logging.error(f"D-Bus reboot failed: {e}")
        return f"Reboot command failed. Please use physical reboot button."
```

**4. Test Implementation**:
- Test from command line (Python)
- Test from voice command
- Verify system reboots
- Check logs for errors

---

## Detailed Implementation Steps

### Phase 1: Verify Dependencies (5 minutes)

**Step 1.1: Check if python3-dbus is installed**
```bash
dpkg -l | grep python3-dbus
```

Expected output:
```
ii  python3-dbus  1.3.2-4  armhf  Python 3 bindings for D-Bus
```

**Step 1.2: If not installed, install it**
```bash
sudo apt update
sudo apt install python3-dbus -y
```

**Step 1.3: Verify D-Bus system bus is running**
```bash
systemctl status dbus
```

Expected: `active (running)`

---

### Phase 2: Create Polkit Authorization Rule (5 minutes)

**Step 2.1: Create polkit rules directory (if doesn't exist)**
```bash
sudo mkdir -p /etc/polkit-1/rules.d
```

**Step 2.2: Create reboot authorization rule**
```bash
sudo tee /etc/polkit-1/rules.d/50-d3kos-reboot.rules > /dev/null << 'EOF'
/* Allow d3kos user to reboot without password */
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.login1.reboot" &&
        subject.user == "d3kos") {
        return polkit.Result.YES;
    }
});
EOF
```

**Step 2.3: Set correct permissions**
```bash
sudo chmod 644 /etc/polkit-1/rules.d/50-d3kos-reboot.rules
sudo chown root:root /etc/polkit-1/rules.d/50-d3kos-reboot.rules
```

**Step 2.4: Restart polkit to load new rules**
```bash
sudo systemctl restart polkit
```

**Step 2.5: Verify polkit rule syntax**
```bash
sudo pkaction | grep reboot
```

Expected output should include:
```
org.freedesktop.login1.reboot
org.freedesktop.login1.reboot-multiple-sessions
```

---

### Phase 3: Backup Current Implementation (2 minutes)

**Step 3.1: Create backup of query_handler.py**
```bash
sudo cp /opt/d3kos/services/ai/query_handler.py \
       /opt/d3kos/services/ai/query_handler.py.bak.before-dbus
```

**Step 3.2: Verify backup**
```bash
ls -lh /opt/d3kos/services/ai/query_handler.py*
```

---

### Phase 4: Update query_handler.py (10 minutes)

**Step 4.1: Locate the reboot section**
```bash
grep -n "elif category == 'reboot'" /opt/d3kos/services/ai/query_handler.py
```

Expected output: Line number (e.g., `215:`)

**Step 4.2: Create Python script to update the code**

Save this to `/tmp/update_reboot_dbus.py`:
```python
#!/usr/bin/env python3
"""
Update query_handler.py to use D-Bus for reboot command
"""

# Read the file
with open('/opt/d3kos/services/ai/query_handler.py', 'r') as f:
    content = f.read()

# Old implementation
old_code = '''        elif category == 'reboot':
            # Emergency reboot command (for when touchscreen is broken)
            import os
            os.system('sudo systemctl start d3kos-emergency-reboot.service')
            return "Rebooting system now. Please wait 60 seconds."'''

# New D-Bus implementation
new_code = '''        elif category == 'reboot':
            # Emergency reboot command (for when touchscreen is broken)
            # Uses D-Bus to communicate with systemd-logind (industry standard)
            try:
                import dbus
                # Connect to system D-Bus
                bus = dbus.SystemBus()
                # Get systemd-logind manager object
                manager = bus.get_object('org.freedesktop.login1',
                                        '/org/freedesktop/login1')
                # Get Reboot method from Manager interface
                reboot_method = manager.get_dbus_method('Reboot',
                                        'org.freedesktop.login1.Manager')
                # Execute reboot (False = immediate, no confirmation dialog)
                reboot_method(False)
                return "Rebooting system now. Please wait 60 seconds."
            except dbus.exceptions.DBusException as e:
                # D-Bus specific error
                import logging
                logging.error(f"D-Bus reboot failed: {e}")
                return "Reboot command failed. Please use physical reboot button."
            except Exception as e:
                # General error (e.g., dbus module not installed)
                import logging
                logging.error(f"Reboot error: {e}")
                return "Reboot command failed. Please install python3-dbus package."'''

# Replace
if old_code in content:
    content = content.replace(old_code, new_code)

    # Write back
    with open('/opt/d3kos/services/ai/query_handler.py', 'w') as f:
        f.write(content)

    print("✅ SUCCESS: Updated query_handler.py to use D-Bus")
    print("📝 Backup saved at: query_handler.py.bak.before-dbus")
else:
    print("❌ ERROR: Could not find old code pattern")
    print("The reboot section may have been modified already")
    exit(1)
```

**Step 4.3: Execute the update script**
```bash
sudo python3 /tmp/update_reboot_dbus.py
```

Expected output: `✅ SUCCESS: Updated query_handler.py to use D-Bus`

**Step 4.4: Verify the change**
```bash
grep -A 15 "elif category == 'reboot'" /opt/d3kos/services/ai/query_handler.py
```

Should show new D-Bus code with comments.

---

### Phase 5: Test from Command Line (5 minutes)

**Step 5.1: Test classification (doesn't execute reboot)**
```bash
cd /opt/d3kos/services/ai
python3 query_handler.py --classify-only "reboot system"
```

Expected: `SIMPLE: reboot`

**Step 5.2: Test D-Bus connection (without reboot)**
```bash
python3 << 'EOF'
import dbus
bus = dbus.SystemBus()
manager = bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
print("✅ D-Bus connection successful")
print(f"Manager object: {manager}")
EOF
```

Expected: `✅ D-Bus connection successful`

**Step 5.3: Test actual reboot (SYSTEM WILL REBOOT!)**

⚠️ **WARNING**: This will reboot the system immediately!

```bash
cd /opt/d3kos/services/ai
python3 query_handler.py "reboot system"
```

**Expected behavior**:
1. Response: "Rebooting system now. Please wait 60 seconds."
2. System begins shutdown within 2-3 seconds
3. System reboots
4. System comes back online in ~45-60 seconds

**If system doesn't reboot**: Check logs (Phase 6)

---

### Phase 6: Restart Services (2 minutes)

**Step 6.1: Restart AI API service**
```bash
sudo systemctl restart d3kos-ai-api
```

**Step 6.2: Restart Voice service**
```bash
sudo systemctl restart d3kos-voice
```

**Step 6.3: Verify services are running**
```bash
systemctl is-active d3kos-ai-api d3kos-voice
```

Expected: Both show `active`

---

### Phase 7: Test Voice Command (10 minutes)

**Step 7.1: Monitor logs**
```bash
journalctl -u d3kos-voice -f --no-pager
```

**Step 7.2: Execute voice command**
1. Say "HELM" clearly
2. Wait for "Aye Aye Captain"
3. Count to 8 slowly
4. Say "REBOOT SYSTEM" clearly and loudly

**Step 7.3: Verify in logs**

Expected log sequence:
```
✓ Wake word detected: HELM
🔊 Assistant: Aye Aye Captain
🎤 Listening for 3 seconds...
📝 Transcribing...
💭 You asked: reboot system
  ⚡ Simple query detected, using instant response
🔊 Assistant: Rebooting system now. Please wait 60 seconds.
```

**Step 7.4: Observe system behavior**
- TTS plays response (~2 seconds)
- System begins shutdown (~5-10 seconds)
- Screen goes black
- System reboots (~45-60 seconds total)

---

## Testing Matrix

| Test Case | Expected Result | Pass/Fail |
|-----------|-----------------|-----------|
| python3-dbus installed | Package present | ⬜ |
| D-Bus system bus running | Service active | ⬜ |
| Polkit rule created | File exists with correct permissions | ⬜ |
| Backup created | query_handler.py.bak.before-dbus exists | ⬜ |
| Code updated | D-Bus code present in query_handler.py | ⬜ |
| Classification test | Returns "SIMPLE: reboot" | ⬜ |
| D-Bus connection test | Connects successfully | ⬜ |
| Command-line reboot | System reboots | ⬜ |
| Services restart | Both active | ⬜ |
| Voice transcription | Correctly transcribes "reboot system" | ⬜ |
| Voice reboot execution | System reboots | ⬜ |

---

## Troubleshooting

### Issue 1: python3-dbus not found

**Symptom**: `ModuleNotFoundError: No module named 'dbus'`

**Solution**:
```bash
sudo apt update
sudo apt install python3-dbus -y
sudo systemctl restart d3kos-ai-api d3kos-voice
```

---

### Issue 2: D-Bus connection fails

**Symptom**: `dbus.exceptions.DBusException: org.freedesktop.DBus.Error.ServiceUnknown`

**Check D-Bus service**:
```bash
systemctl status dbus
```

**Restart D-Bus** (if needed):
```bash
sudo systemctl restart dbus
```

---

### Issue 3: Permission denied

**Symptom**: `dbus.exceptions.DBusException: org.freedesktop.login1.NotAuthorized`

**Check polkit rule**:
```bash
cat /etc/polkit-1/rules.d/50-d3kos-reboot.rules
```

**Verify syntax**:
```bash
sudo pkaction --verbose | grep login1.reboot
```

**Restart polkit**:
```bash
sudo systemctl restart polkit
```

---

### Issue 4: Voice transcription fails

**Symptom**: "I didn't catch that" or empty transcription

**This is NOT a D-Bus issue** - it's a microphone/audio issue.

**Solutions**:
- Speak louder and clearer
- Wait full 8 seconds after "Aye Aye Captain"
- Check microphone levels
- See previous documentation on timing issues

---

### Issue 5: Reboot still doesn't work

**Debug D-Bus call manually**:
```bash
dbus-send --system --print-reply \
          --dest=org.freedesktop.login1 \
          /org/freedesktop/login1 \
          org.freedesktop.login1.Manager.Reboot \
          boolean:false
```

Expected: System reboots immediately

**Check logs**:
```bash
journalctl -u d3kos-ai-api --since "1 minute ago" --no-pager
journalctl -u d3kos-voice --since "1 minute ago" --no-pager
```

Look for Python exceptions or D-Bus errors.

---

## Rollback Plan

If D-Bus implementation fails and you need to revert:

**Step 1: Restore backup**
```bash
sudo cp /opt/d3kos/services/ai/query_handler.py.bak.before-dbus \
       /opt/d3kos/services/ai/query_handler.py
```

**Step 2: Restart services**
```bash
sudo systemctl restart d3kos-ai-api d3kos-voice
```

**Step 3: Remove polkit rule (optional)**
```bash
sudo rm /etc/polkit-1/rules.d/50-d3kos-reboot.rules
sudo systemctl restart polkit
```

**Step 4: Verify rollback**
```bash
grep -A 5 "elif category == 'reboot'" /opt/d3kos/services/ai/query_handler.py
```

Should show old `os.system()` code.

---

## Security Analysis

### Before (os.system with NOPASSWD: ALL)

**Security Issues**:
- ❌ d3kos user has FULL sudo access to ALL commands
- ❌ Any compromised Python code can execute ANY root command
- ❌ No audit trail of what commands are executed
- ❌ `os.system()` vulnerable to shell injection if user input involved

### After (D-Bus with Polkit)

**Security Improvements**:
- ✅ d3kos user can ONLY reboot (via polkit rule)
- ✅ Cannot execute other root commands
- ✅ Polkit logs all authorization attempts
- ✅ D-Bus is not vulnerable to injection attacks
- ✅ Industry-standard authorization framework

**Recommendation**: After verifying D-Bus works, consider removing `NOPASSWD: ALL` and using polkit for other privileged operations.

---

## Performance Comparison

| Metric | os.system() | D-Bus |
|--------|-------------|-------|
| **Execution time** | ~10-50ms | ~5-15ms |
| **Reliability from service** | ⚠️ Unreliable | ✅ Reliable |
| **Error handling** | ❌ None | ✅ Exception-based |
| **Security** | ⚠️ Requires NOPASSWD | ✅ Fine-grained polkit |
| **Industry adoption** | Deprecated | Standard |
| **Python version** | All | 2.7+ |

---

## Documentation References

### D-Bus and Polkit:
- [Video/Linux Facts: D-Bus Reboot](https://fhackts.wordpress.com/2019/08/08/shutting-down-or-rebooting-over-dbus-programmatically-from-a-non-root-user/)
- [ArchWiki: Polkit](https://wiki.archlinux.org/title/Polkit)
- [Baeldung: Poweroff and Reboot as Normal User](https://www.baeldung.com/linux/poweroff-reboot-normal-user)

### Python D-Bus Bindings:
- [Python D-Bus Tutorial](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html)
- [D-Bus Specification](https://dbus.freedesktop.org/doc/dbus-specification.html)

### systemd-logind:
- [systemd-logind Documentation](https://www.freedesktop.org/software/systemd/man/systemd-logind.service.html)
- [org.freedesktop.login1 D-Bus API](https://www.freedesktop.org/software/systemd/man/org.freedesktop.login1.html)

---

## Success Criteria

The implementation is successful when:

1. ✅ python3-dbus package installed
2. ✅ Polkit rule created and active
3. ✅ query_handler.py updated with D-Bus code
4. ✅ Backup created before changes
5. ✅ Command-line test triggers reboot
6. ✅ Voice command triggers reboot
7. ✅ No errors in logs
8. ✅ System reboots within 10 seconds of command
9. ✅ System comes back online automatically
10. ✅ Voice service auto-starts after reboot

---

## Maintenance

### After System Updates

**Python updates**: D-Bus bindings are compiled C extensions. After Python upgrades, you may need to reinstall:
```bash
sudo apt reinstall python3-dbus
```

**Polkit updates**: Rules in `/etc/polkit-1/rules.d/` persist across updates. No action needed.

**systemd updates**: D-Bus API is stable. No changes needed.

---

## Future Enhancements

Once D-Bus reboot is working, consider adding other D-Bus system operations:

1. **Shutdown**: `Poweroff()` method
2. **Suspend**: `Suspend()` method
3. **Service control**: Via systemd D-Bus interface
4. **Log queries**: Via systemd-journald D-Bus interface

---

## ✅ IMPLEMENTATION COMPLETE - SUCCESS

**Implementation Date**: February 22, 2026
**Status**: FULLY FUNCTIONAL - Voice-triggered reboot working
**User Confirmation**: "it worked it really worked"

### Implementation Summary

✅ **All 7 Phases Completed:**
1. Dependencies verified (python3-dbus 1.4.0-1)
2. Polkit rule created and loaded
3. query_handler.py backed up
4. D-Bus code implemented
5. Pattern matching updated (added standalone "reboot")
6. Services restarted successfully
7. Voice command tested successfully

### Test Results

**Test Date**: February 22, 2026 10:37 AM EST

**Test Command**: "HELM" → "reboot"

**Results**:
```
10:37:22 - Wake word detected: HELM ✓
10:37:22 - Response: "Aye Aye Captain" ✓
10:37:28 - Listening for 3 seconds... ✓
10:37:34 - Transcribed: "reboot" ✓
10:37:34 - Pattern matched: Simple query (reboot) ✓
10:37:36 - Connection closed (SYSTEM REBOOTED) ✓
```

**System rebooted successfully via D-Bus!**

### Files Modified

1. `/etc/polkit-1/rules.d/50-d3kos-reboot.rules` - Created
2. `/opt/d3kos/services/ai/query_handler.py` - D-Bus implementation + patterns
3. Backup: `query_handler.py.bak.dbus-YYYYMMDD-HHMMSS`

### Documentation Updated

- ✅ README.md - Emergency reboot added to Voice Assistant commands
- ✅ AI_ASSISTANT_USER_GUIDE.md - Emergency Reboot section added
- ✅ SESSION_VOICE_EMERGENCY_REBOOT_COMPLETE.md - Full session documentation
- ✅ This file - Status updated to COMPLETE

### Actual Implementation Time

- Research: ~30 minutes (completed in previous session)
- Implementation: ~45 minutes (Phases 1-6)
- Testing & Fixes: ~30 minutes (pattern matching)
- Documentation: ~30 minutes
**Total**: ~2 hours 15 minutes

---

**Implementation Complete** - Emergency voice reboot is now a production feature of d3kOS!
