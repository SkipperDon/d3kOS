# Voice Recording Mic Lock — Solution Spec
**Date:** 2026-03-07
**Status:** Ready to implement
**Affected services:** voice-assistant-hybrid.py · network-api.py · boatlog.html

---

## Problem Statement

When the user taps the mic button in Boatlog to record a voice note, the browser calls
`getUserMedia()` to capture audio. The voice assistant service (`d3kos-voice.service`) is
already holding the ALSA microphone device open via a persistent `arecord` subprocess
(PID visible in `systemctl status d3kos-voice`). ALSA does not share the device — one
process wins, the other gets silence or an error. The voice service wins because it started
first, so the browser recording gets nothing, and the voice service interprets the noise as
a command and responds "Aye Aye Captain".

**Root cause:** Two processes competing for an exclusive ALSA device.
**Fix:** The voice service must release the mic before the browser can take it, then
reclaim it when the browser is done.

---

## Solution: Signal-Based Mic Lock

The voice service already has a `wake_word_detector.stop()` method (in `wake_word_vosk.py`
line 73) that terminates the `arecord` subprocess and releases the ALSA device. The fix
wires this to an external signal so Boatlog can tell the voice service to step aside.

```
Boatlog taps mic
        │
        ▼
POST /api/voice/pause           ←── network-api.py (port 8101)
        │
        ▼
os.kill(voice_pid, SIGUSR1)     ←── sends signal to voice service process
        │
        ▼
voice service SIGUSR1 handler
 → wake_word_detector.stop()    ←── terminates arecord subprocess
 → _mic_locked = True           ←── blocks run loop from restarting
        │
        ▼
mic is free — getUserMedia() succeeds
        │
     [user records note]
        │
        ▼
POST /api/voice/resume          ←── network-api.py
        │
        ▼
os.kill(voice_pid, SIGUSR2)
        │
        ▼
voice service SIGUSR2 handler
 → _mic_locked = False
 → wake_word_detector.listen()  ←── arecord restarts, mic held again
        │
        ▼
voice commands resume (~0.5 seconds — model already loaded, just restarts arecord)
```

No service restart. No model reload. The lock/unlock cycle takes under one second.

---

## Component 1: voice-assistant-hybrid.py

**File:** `/opt/d3kos/services/voice/voice-assistant-hybrid.py`

### Add to `__init__`:
```python
import signal
self._mic_locked = False
```

### Add signal handlers (call from `__init__` after existing setup):
```python
signal.signal(signal.SIGUSR1, self._handle_mic_lock)
signal.signal(signal.SIGUSR2, self._handle_mic_unlock)
```

### Add handler methods to `HybridVoiceAssistant` class:
```python
def _handle_mic_lock(self, signum, frame):
    """External mic lock request — release ALSA device for browser recording."""
    self._mic_locked = True
    try:
        self.wake_word_detector.stop()
        print("🔒 Mic locked for external recording")
    except Exception as e:
        print(f"⚠️  Mic lock error: {e}")

def _handle_mic_unlock(self, signum, frame):
    """External mic unlock — reclaim ALSA device and resume wake word detection."""
    self._mic_locked = False
    print("🔓 Mic unlocked — resuming wake word detection")
    # run_service loop will detect _mic_locked == False and restart listen()
```

### Modify `run_service()` loop:

The existing loop (around line 258) starts `wake_word_listener` in a thread. The thread
calls `wake_word_detector.listen()` which blocks until `stop()` is called. After `stop()`,
the loop needs to check `_mic_locked` before restarting.

**Existing loop structure (simplified):**
```python
while self.running:
    listener_thread = Thread(target=wake_word_listener, daemon=True)
    listener_thread.start()
    listener_thread.join()
    # ... immediately restarts
```

**Change to:**
```python
while self.running:
    if self._mic_locked:
        time.sleep(0.5)   # idle — mic is held by browser
        continue

    listener_thread = Thread(target=wake_word_listener, daemon=True)
    listener_thread.start()
    listener_thread.join()
    # loop continues — next iteration checks _mic_locked before restarting
```

That `time.sleep(0.5)` loop runs silently while the browser has the mic. When SIGUSR2
arrives, `_mic_locked` becomes False, the next iteration skips the sleep and restarts
the listener thread.

---

## Component 2: network-api.py

**File:** `/opt/d3kos/services/network/network-api.py`
**Port:** 8101 (already proxied by nginx for `/api/`)

Add two endpoints and a safety timer:

```python
import signal
import os
import threading

# Auto-resume timer handle — cancels itself on resume
_voice_auto_resume_timer = None

def _get_voice_pid():
    """Get the MainPID of d3kos-voice.service. Returns None if not running."""
    try:
        result = subprocess.run(
            ['systemctl', 'show', 'd3kos-voice', '--property=MainPID'],
            capture_output=True, text=True, timeout=3
        )
        pid_str = result.stdout.strip().replace('MainPID=', '')
        pid = int(pid_str)
        return pid if pid > 0 else None
    except Exception:
        return None

@app.route('/api/voice/pause', methods=['POST'])
def voice_pause():
    global _voice_auto_resume_timer
    pid = _get_voice_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGUSR1)
        except ProcessLookupError:
            pass  # Service stopped between check and kill — fine

    # Safety: auto-resume after 90 seconds if browser crashes without calling resume
    if _voice_auto_resume_timer:
        _voice_auto_resume_timer.cancel()
    def auto_resume():
        _do_voice_resume()
    _voice_auto_resume_timer = threading.Timer(90.0, auto_resume)
    _voice_auto_resume_timer.start()

    return jsonify({'status': 'paused'})

@app.route('/api/voice/resume', methods=['POST'])
def voice_resume():
    _do_voice_resume()
    return jsonify({'status': 'resumed'})

def _do_voice_resume():
    global _voice_auto_resume_timer
    if _voice_auto_resume_timer:
        _voice_auto_resume_timer.cancel()
        _voice_auto_resume_timer = None
    pid = _get_voice_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGUSR2)
        except ProcessLookupError:
            pass
```

No nginx changes needed — `/api/voice/pause` and `/api/voice/resume` will route through
the existing `/api/` proxy block to port 8101.

---

## Component 3: boatlog.html

**File:** `/var/www/html/boatlog.html`

Three changes:

### A. Before calling getUserMedia — pause voice service
The existing mic button calls a function like `startVoiceRecording()`. Wrap it:

```javascript
async function startVoiceRecording() {
    // Pause helm voice commands so mic is free
    try {
        await fetch('http://localhost:8101/api/voice/pause', { method: 'POST' });
    } catch (e) {
        // Non-blocking — if network-api is down, still try to record
    }

    // Show indicator
    const indicator = document.getElementById('voice-pause-indicator');
    if (indicator) indicator.style.display = 'block';

    // Existing getUserMedia call follows here unchanged...
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // ... existing recording logic
    } catch (err) {
        // getUserMedia failed — release mic lock immediately
        await resumeVoice();
        // ... existing error handling
    }
}
```

### B. After save or cancel — resume voice service
```javascript
async function resumeVoice() {
    try {
        await fetch('http://localhost:8101/api/voice/resume', { method: 'POST' });
    } catch (e) {
        // Silent — auto-resume timer in network-api covers this
    }
    const indicator = document.getElementById('voice-pause-indicator');
    if (indicator) indicator.style.display = 'none';
}
```

Call `resumeVoice()` at every exit point:
- After note is saved successfully
- After user cancels the recording
- After any recording error

### C. Safety — resume if user leaves the page
```javascript
window.addEventListener('beforeunload', function() {
    navigator.sendBeacon(
        'http://localhost:8101/api/voice/resume',
        JSON.stringify({})
    );
});
```
`sendBeacon` fires even when the page is closing, unlike `fetch`.

### D. Visual indicator (add to boatlog.html body)

Three states shown in sequence:

```html
<!-- Add near the mic recording UI -->
<div id="voice-rec-indicator" style="display:none; border-radius:6px; padding:10px 18px;
     font-size:20px; text-align:center; margin-bottom:12px; transition:all 0.2s;">
</div>
```

JavaScript sets the state:

```javascript
function setRecIndicator(state) {
    const el = document.getElementById('voice-rec-indicator');
    if (!el) return;
    const states = {
        preparing: {
            text: 'Releasing helm mic...',
            bg: '#1a1a00', border: '#888800', color: '#cccc00'
        },
        ready: {
            text: 'Go ahead Captain, record your log',
            bg: '#001a00', border: '#00CC00', color: '#00FF00'
        },
        recording: {
            text: 'Recording... tap Stop when done',
            bg: '#1a0000', border: '#CC0000', color: '#FF4444'
        },
        saving: {
            text: 'Saving note...',
            bg: '#111111', border: '#444444', color: '#888888'
        }
    };
    const s = states[state];
    if (!s) { el.style.display = 'none'; return; }
    el.style.display  = 'block';
    el.style.background   = s.bg;
    el.style.border   = '1px solid ' + s.border;
    el.style.color    = s.color;
    el.textContent    = s.text;
}
```

**Sequence:**
1. Tap mic → `setRecIndicator('preparing')` — amber "Releasing helm mic..."
2. pause resolves + getUserMedia() succeeds → `setRecIndicator('ready')` — green "Go ahead Captain, record your log"
3. User taps Record/Start → `setRecIndicator('recording')` — red "Recording... tap Stop when done"
4. User taps Stop → `setRecIndicator('saving')` — grey "Saving note..."
5. Saved → `setRecIndicator(null)` — indicator hidden, voice resumed

---

## What the User Experiences

1. Opens Boatlog, taps the mic button
2. Amber bar appears: "Voice commands paused during recording"
3. Recording proceeds normally — no conflict with helm voice
4. Taps Stop → saves note → amber bar disappears
5. Helm voice commands resume automatically (~0.5 seconds)
6. If the user navigates away mid-recording, `sendBeacon` resumes automatically
7. If the browser crashes, the 90-second timer in network-api resumes automatically

Helm voice is never permanently locked out.

---

## Safety Summary

| Scenario | Protection |
|----------|-----------|
| User saves note normally | `resumeVoice()` called in save handler |
| User cancels recording | `resumeVoice()` called in cancel handler |
| getUserMedia fails | `resumeVoice()` called in catch block |
| User navigates away | `beforeunload` → `sendBeacon` |
| Browser crashes | 90-second auto-resume timer in network-api |
| Voice service not running | `_get_voice_pid()` returns None → no-op, no error |
| network-api down | `try/catch` in JS → still tries getUserMedia, recording still works |

---

## Files Changed

| File | Change |
|------|--------|
| `voice-assistant-hybrid.py` | +signal import, +`_mic_locked` flag, +SIGUSR1/SIGUSR2 handlers, +sleep check in run loop |
| `network-api.py` | +`/api/voice/pause`, +`/api/voice/resume`, +`_get_voice_pid()`, +auto-resume timer |
| `boatlog.html` | +`resumeVoice()`, +pause before getUserMedia, +resume at all exit points, +beforeunload beacon, +amber indicator |

No new services. No new ports. No nginx changes. No service restarts to implement.

---

## Estimated Ollama Phases

This is straightforward enough to implement directly (no generation needed):

| Change | Method |
|--------|--------|
| voice-assistant-hybrid.py | Direct edit (~20 lines) |
| network-api.py | Direct edit (~35 lines) |
| boatlog.html | Direct edit (~30 lines) |

Total: ~85 lines across 3 files. All logic is defined above — copy-paste + integration.

---

*Solution by Claude Code — March 2026*
*Companion to: SESSION_LOG.md, MASTER_SYSTEM_SPEC.md*
