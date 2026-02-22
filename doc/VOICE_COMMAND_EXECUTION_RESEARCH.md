# Voice Command Execution Research - Emergency Reboot Implementation

**Date**: February 22, 2026
**Purpose**: Research proper methods for executing system commands (reboot) from voice assistant
**Status**: RESEARCH ONLY - NO IMPLEMENTATION

---

## Executive Summary

This document analyzes the current d3kOS implementation for voice-triggered system reboot and compares it against industry best practices, professional voice assistant implementations, and Linux system architecture standards.

---

## 1. Current d3kOS Implementation

### Architecture Overview (from CLAUDE.md & MASTER_SYSTEM_SPEC.md)

**Voice Pipeline**:
```
User → PocketSphinx (wake word "Helm")
     → Vosk (speech-to-text)
     → query_handler.py (pattern matching)
     → Piper (text-to-speech response)
     → System action (if applicable)
```

**Current Reboot Implementation** (`query_handler.py` line ~215):
```python
elif category == 'reboot':
    # Emergency reboot command (for when touchscreen is broken)
    import os
    os.system('sudo systemctl start d3kos-emergency-reboot.service')
    return "Rebooting system now. Please wait 60 seconds."
```

**Systemd Service** (`/etc/systemd/system/d3kos-emergency-reboot.service`):
```ini
[Unit]
Description=d3kOS Emergency Reboot Service
DefaultDependencies=no
Before=shutdown.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/reboot
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

**Permissions**:
- User: `d3kos`
- Sudoers: `/etc/sudoers.d/*` contains `d3kos ALL=(ALL) NOPASSWD: ALL`
- Full sudo access without password

---

## 2. What We've Tried (Session Timeline)

| Attempt | Method | Result | Issue |
|---------|--------|--------|-------|
| 1 | `subprocess.Popen(['sudo', 'reboot'])` | ❌ Failed | Command not in PATH when run from service |
| 2 | `subprocess.Popen(['/usr/bin/sudo', '/usr/sbin/reboot'])` | ❌ Failed | Process hung on pipes |
| 3 | `subprocess.Popen([...], stdout=PIPE, stderr=PIPE)` | ❌ Failed | Process blocked on pipe I/O |
| 4 | `subprocess.Popen([...], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, start_new_session=True)` | ❌ Failed | Process detached but didn't execute |
| 5 | `os.system('sudo reboot &')` | ❌ Failed | Background operator ineffective |
| 6 | `os.system('sudo systemctl start d3kos-emergency-reboot.service &')` | ❌ Failed | Service didn't start |
| 7 | `os.system('sudo systemctl start d3kos-emergency-reboot.service')` (no &) | ✅ Command line works | ❌ Voice execution fails |

**Key Observation**: Command-line Python test DOES trigger reboot, but voice-triggered execution does NOT.

---

## 3. Industry Best Practices (Python Subprocess)

### Recommended Approaches (2026 Standards)

Sources:
- [Python Subprocess Documentation](https://docs.python.org/3/library/subprocess.html)
- [DigitalOcean Tutorial](https://www.digitalocean.com/community/tutorials/python-system-command-os-subprocess-call)
- [Real Python Guide](https://realpython.com/python-subprocess/)

**Modern Python (3.5+) Recommendation**: Use `subprocess.run()`

```python
import subprocess

# Recommended approach
result = subprocess.run(
    ['sudo', 'systemctl', 'start', 'd3kos-emergency-reboot.service'],
    check=True,  # Raises CalledProcessError on failure
    capture_output=True,  # Capture stdout/stderr
    text=True  # Return strings not bytes
)
```

**Why NOT `os.system()`**:
- Security risk with shell=True
- No error handling
- No output capture
- Deprecated in favor of subprocess module
- Documentation states: "The subprocess module provides more powerful facilities for spawning new processes"

**Why NOT `subprocess.Popen()` for Simple Commands**:
- Popen() is for advanced use cases (streaming, real-time I/O)
- subprocess.run() is simpler and recommended for one-off commands
- Popen() requires explicit process management

**Key Security Principle**:
- Pass command as LIST, not string: `['sudo', 'reboot']` not `'sudo reboot'`
- Avoids shell injection vulnerabilities
- More secure and reliable

---

## 4. Professional Voice Assistant Implementations

### Mycroft Open-Source Voice Assistant

Sources:
- [Mycroft Linux Documentation](https://mycroft-ai.gitbook.io/docs/using-mycroft-ai/get-mycroft/linux)
- [Mycroft Systemd Integration](https://github.com/j1nx/mycroft-systemd)

**Mycroft Architecture**:
- Runs as systemd services (one per component)
- Uses D-Bus for inter-process communication
- Relies on systemd for service control
- Skills (plugins) can trigger systemd actions

**Systemd Integration Pattern**:
```bash
# Start Mycroft service
sudo systemctl start mycroft.service

# Skills trigger systemd actions via D-Bus
dbus-send --system --dest=org.freedesktop.systemd1 \
          /org/freedesktop/systemd1 \
          org.freedesktop.systemd1.Manager.StartUnit \
          string:"target-service.service" string:"replace"
```

**Key Lesson**: Professional voice assistants DON'T execute commands directly from Python. They use system-level interfaces (D-Bus, systemd) designed for service management.

---

## 5. Linux System Architecture Standards

### Proper Non-Root Command Execution

Sources:
- [Baeldung: Poweroff and Reboot as Normal User](https://www.baeldung.com/linux/poweroff-reboot-normal-user)
- [ArchWiki: Polkit](https://wiki.archlinux.org/title/Polkit)
- [Video/Linux Facts: D-Bus Reboot](https://fhackts.wordpress.com/2019/08/08/shutting-down-or-rebooting-over-dbus-programmatically-from-a-non-root-user/)

### Method 1: D-Bus (Modern, Recommended)

**What is D-Bus?**
- Inter-process communication (IPC) system
- Standard way for applications to communicate with systemd
- Built into modern Linux distributions
- Designed for privilege elevation

**D-Bus Reboot Command**:
```bash
dbus-send --system --print-reply \
          --dest=org.freedesktop.login1 \
          /org/freedesktop/login1 \
          "org.freedesktop.login1.Manager.Reboot" \
          boolean:true
```

**Python D-Bus Example**:
```python
import dbus

# Connect to system bus
bus = dbus.SystemBus()

# Get systemd-logind manager
manager = bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')

# Call Reboot method
reboot = manager.get_dbus_method('Reboot', 'org.freedesktop.login1.Manager')
reboot(True)  # True = interactive (ask user), False = immediate
```

**Advantages**:
- No sudo required (polkit handles authorization)
- Proper privilege separation
- Error handling built-in
- Standard Linux approach
- Works with systemd-based systems

### Method 2: Polkit Rules (Authorization Framework)

**What is Polkit?**
- Framework for defining and handling authorizations
- Manages privileges without requiring root
- Integrates with D-Bus for systemd actions
- Can grant specific permissions to specific users

**Custom Polkit Rule** (`/etc/polkit-1/rules.d/50-d3kos-reboot.rules`):
```javascript
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.login1.reboot" &&
        subject.user == "d3kos") {
        return polkit.Result.YES;  // Allow without password
    }
});
```

**Advantages**:
- Fine-grained control (only reboot, not all sudo)
- No NOPASSWD: ALL needed (security improvement)
- Standard Linux authorization mechanism
- Auditable (polkit logs actions)

### Method 3: Systemd User Services (Session-based)

**Systemd --user Mode**:
- Services run in user's systemd instance
- No root privileges required
- Can control system services via socket activation

**Example**:
```ini
# ~/.config/systemd/user/emergency-reboot.service
[Unit]
Description=Emergency Reboot Trigger

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl reboot
```

**Limitations**: Still requires polkit or sudo for actual reboot.

---

## 6. Why Current Implementation Fails

### Analysis of Voice vs Command-Line Difference

**Command-Line Test (WORKS)**:
```bash
cd /opt/d3kos/services/ai
python3 -c "from query_handler import AIQueryHandler; \
            h = AIQueryHandler(); \
            print(h.query('reboot system', force_provider='onboard'))"
```
Result: System reboots successfully ✅

**Voice Test (FAILS)**:
```
User: "HELM" → "reboot system"
System: "Rebooting system now. Please wait 60 seconds."
Result: No reboot occurs ❌
```

### Root Cause Hypothesis

**Theory 1: Process Hierarchy**
- Voice service runs as systemd service (d3kos-voice.service)
- Service has different environment than interactive shell
- `os.system()` shell might not have proper TTY/session context
- Systemd service isolation may block certain operations

**Theory 2: Systemd Service Dependencies**
- `d3kos-emergency-reboot.service` may not start properly when called from d3kos-voice.service
- Possible dependency cycle or ordering issue
- DefaultDependencies=no might interact poorly with service calls

**Theory 3: Shell Environment**
- `os.system()` spawns a shell (/bin/sh)
- Shell environment differs between interactive and service contexts
- PATH, user session, or systemd scope may be incorrect

**Theory 4: Execution Context**
- Command may execute but get queued/delayed by systemd
- Process may be killed by systemd before completing
- Service Type=oneshot may conflict with calling from another service

---

## 7. Recommended Solutions (Ranked)

### Solution 1: D-Bus Direct Call (BEST PRACTICE)

**Approach**: Use Python D-Bus bindings to call systemd-logind directly

**Implementation**:
```python
elif category == 'reboot':
    try:
        import dbus
        bus = dbus.SystemBus()
        manager = bus.get_object('org.freedesktop.login1',
                                '/org/freedesktop/login1')
        reboot = manager.get_dbus_method('Reboot',
                                        'org.freedesktop.login1.Manager')
        reboot(False)  # False = no confirmation dialog
        return "Rebooting system now. Please wait 60 seconds."
    except Exception as e:
        return f"Reboot failed: {e}"
```

**Advantages**:
- ✅ Industry standard approach
- ✅ No sudo required (polkit handles it)
- ✅ Proper privilege separation
- ✅ Better error handling
- ✅ Works reliably from systemd services

**Disadvantages**:
- ⚠️ Requires python3-dbus package
- ⚠️ May need polkit rule for passwordless operation

**Polkit Rule Required** (`/etc/polkit-1/rules.d/50-d3kos-reboot.rules`):
```javascript
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.login1.reboot" &&
        subject.user == "d3kos") {
        return polkit.Result.YES;
    }
});
```

---

### Solution 2: subprocess.run() Instead of os.system()

**Approach**: Replace os.system() with modern subprocess.run()

**Implementation**:
```python
elif category == 'reboot':
    import subprocess
    try:
        result = subprocess.run(
            ['sudo', 'systemctl', 'reboot'],
            check=True,
            timeout=5,
            capture_output=True,
            text=True
        )
        return "Rebooting system now. Please wait 60 seconds."
    except subprocess.CalledProcessError as e:
        return f"Reboot command failed: {e.stderr}"
    except subprocess.TimeoutExpired:
        # Reboot initiated, service will be killed
        return "Rebooting system now. Please wait 60 seconds."
```

**Advantages**:
- ✅ Modern Python best practice
- ✅ Better error handling
- ✅ Timeout prevents hangs
- ✅ More secure than os.system()

**Disadvantages**:
- ⚠️ Still uses sudo (security concern)
- ⚠️ May still fail from service context
- ⚠️ Doesn't address root cause

---

### Solution 3: Systemd Socket Activation

**Approach**: Create a socket that triggers the reboot service

**Implementation**:

**Socket Unit** (`/etc/systemd/system/d3kos-emergency-reboot.socket`):
```ini
[Unit]
Description=d3kOS Emergency Reboot Socket

[Socket]
ListenStream=/run/d3kos/emergency-reboot.sock
SocketMode=0660
SocketUser=d3kos
SocketGroup=d3kos

[Install]
WantedBy=sockets.target
```

**Service Unit** (`/etc/systemd/system/d3kos-emergency-reboot@.service`):
```ini
[Unit]
Description=d3kOS Emergency Reboot Handler
After=d3kos-emergency-reboot.socket
Requires=d3kos-emergency-reboot.socket

[Service]
Type=oneshot
ExecStart=/usr/sbin/reboot
StandardInput=socket
```

**Python Code**:
```python
elif category == 'reboot':
    import socket
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect('/run/d3kos/emergency-reboot.sock')
        sock.send(b'REBOOT\n')
        sock.close()
        return "Rebooting system now. Please wait 60 seconds."
    except Exception as e:
        return f"Reboot trigger failed: {e}"
```

**Advantages**:
- ✅ Systemd native approach
- ✅ Proper service isolation
- ✅ No sudo required
- ✅ Reliable from service context

**Disadvantages**:
- ⚠️ More complex setup
- ⚠️ Requires systemd 230+ (we have 255, so OK)

---

### Solution 4: Direct /usr/sbin/reboot with Capabilities

**Approach**: Grant CAP_SYS_BOOT capability to Python script

**Implementation**:
```bash
# Grant capability to Python interpreter
sudo setcap cap_sys_boot+ep /usr/bin/python3
```

**Python Code**:
```python
elif category == 'reboot':
    import subprocess
    subprocess.Popen(['/usr/sbin/reboot'])
    return "Rebooting system now. Please wait 60 seconds."
```

**Advantages**:
- ✅ No sudo required
- ✅ Direct execution

**Disadvantages**:
- ❌ SECURITY RISK: Gives ALL Python scripts reboot capability
- ❌ Not recommended for production
- ❌ Breaks on Python updates (capability lost)

---

### Solution 5: Systemd Drop-in Override (Current Approach Fix)

**Approach**: Fix current systemd service approach with proper isolation

**Drop-in Unit** (`/etc/systemd/system/d3kos-voice.service.d/allow-reboot.conf`):
```ini
[Service]
# Allow voice service to trigger reboot service
AmbientCapabilities=CAP_SYS_BOOT
```

**Keep Current Code**:
```python
elif category == 'reboot':
    import os
    os.system('sudo systemctl start d3kos-emergency-reboot.service')
    return "Rebooting system now. Please wait 60 seconds."
```

**Advantages**:
- ✅ Minimal code change
- ✅ Leverages existing systemd service

**Disadvantages**:
- ⚠️ Still uses os.system() (deprecated)
- ⚠️ May not address root cause
- ⚠️ Capability may be insufficient

---

## 8. Testing Matrix

| Solution | Security | Reliability | Complexity | Recommendation |
|----------|----------|-------------|------------|----------------|
| **D-Bus + Polkit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **BEST CHOICE** |
| subprocess.run() | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Good fallback |
| Socket Activation | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | Complex but robust |
| Capabilities | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Not recommended |
| Current (os.system) | ⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | Currently failing |

---

## 9. Recommendation

### Primary Solution: D-Bus + Polkit

**Rationale**:
1. Industry standard for systemd-based systems
2. Used by professional voice assistants (Mycroft, etc.)
3. Proper privilege separation (no NOPASSWD: ALL needed)
4. Reliable from systemd service context
5. Better security (fine-grained permissions)
6. Auditable via polkit logs

**Implementation Steps**:
1. Install python3-dbus: `sudo apt install python3-dbus`
2. Create polkit rule in `/etc/polkit-1/rules.d/50-d3kos-reboot.rules`
3. Update query_handler.py to use D-Bus call
4. Test from command line
5. Test from voice command
6. Verify in logs

**Estimated Time**: 30-45 minutes

---

## 10. Documentation References

### Python Subprocess Best Practices:
- [Python Subprocess Documentation](https://docs.python.org/3/library/subprocess.html)
- [DigitalOcean: Python System Command](https://www.digitalocean.com/community/tutorials/python-system-command-os-subprocess-call)
- [Real Python: Python Subprocess](https://realpython.com/python-subprocess/)
- [Medium: subprocess Module Guide](https://medium.com/@AlexanderObregon/how-to-use-pythons-subprocess-module-to-run-system-commands-ffdeabcb9721)

### Professional Voice Assistant Implementation:
- [Mycroft Linux Documentation](https://mycroft-ai.gitbook.io/docs/using-mycroft-ai/get-mycroft/linux)
- [Mycroft Systemd Integration](https://github.com/j1nx/mycroft-systemd)

### Linux System Architecture:
- [Baeldung: Poweroff and Reboot as Normal User](https://www.baeldung.com/linux/poweroff-reboot-normal-user)
- [ArchWiki: Polkit](https://wiki.archlinux.org/title/Polkit)
- [Video/Linux Facts: D-Bus Reboot](https://fhackts.wordpress.com/2019/08/08/shutting-down-or-rebooting-over-dbus-programmatically-from-a-non-root-user/)
- [Baeldung: Restart Systemd Service with Specific User](https://www.baeldung.com/linux/systemd-service-restart-specific-user)

---

## 11. Next Steps

**DO NOT IMPLEMENT** until user reviews and approves approach.

**For Discussion**:
1. Does D-Bus + Polkit approach align with d3kOS architecture?
2. Is python3-dbus package acceptable dependency?
3. Should we keep current NOPASSWD: ALL or switch to polkit fine-grained permissions?
4. Fallback plan if D-Bus fails?

---

**END OF RESEARCH DOCUMENT**
