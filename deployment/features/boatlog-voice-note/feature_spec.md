# Boatlog Voice Note — Feature Spec

## Overview
Replace the placeholder `recordVoiceNote()` function in boatlog.html with a working
MediaRecorder implementation. The backend API already exists at `POST /api/boatlog/voice-note`.

The current function just shows a Tier 2 alert(). Replace it with real recording logic.

---

## PHASE 1: REPLACE recordVoiceNote PLACEHOLDER — voice-note-js

Replace the entire `recordVoiceNote()` function with a working implementation.

### API (already deployed — do not change)
- `POST /api/boatlog/voice-note` — accepts `multipart/form-data` with field `audio` (WAV/WebM blob)
- Returns `{ "success": true, "transcript": "...", "entry_id": "..." }`

### Existing UI elements (already in HTML — do not recreate)
- Button: `<button id="btn-voice-note" onclick="recordVoiceNote()">` — already exists
- Button text is "🎤 Voice Note" already

### What to write — the replacement function only:

```javascript
    function recordVoiceNote() {
      var btn = document.getElementById('btn-voice-note');
      if (btn.dataset.recording === 'true') {
        // Stop recording
        if (window._voiceRecorder) { window._voiceRecorder.stop(); }
        return;
      }
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Microphone not available on this device.');
        return;
      }
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
          var chunks = [];
          var recorder = new MediaRecorder(stream);
          window._voiceRecorder = recorder;
          btn.dataset.recording = 'true';
          btn.textContent = '⏹ Stop Recording';
          btn.style.background = '#CC0000';
          recorder.ondataavailable = function(e) { if (e.data.size > 0) chunks.push(e.data); };
          recorder.onstop = function() {
            btn.dataset.recording = 'false';
            btn.textContent = '🎤 Voice Note';
            btn.style.background = '';
            stream.getTracks().forEach(function(t) { t.stop(); });
            var blob = new Blob(chunks, { type: 'audio/webm' });
            var fd = new FormData();
            fd.append('audio', blob, 'voice-note.webm');
            btn.textContent = '⏳ Saving...';
            btn.disabled = true;
            fetch('/api/boatlog/voice-note', { method: 'POST', body: fd })
              .then(function(r) { return r.json(); })
              .then(function(d) {
                btn.disabled = false;
                btn.textContent = '🎤 Voice Note';
                if (d.success) {
                  alert('Voice note saved' + (d.transcript ? ': ' + d.transcript : '.'));
                  if (typeof loadLogEntries === 'function') loadLogEntries();
                } else {
                  alert('Failed to save voice note.');
                }
              })
              .catch(function() {
                btn.disabled = false;
                btn.textContent = '🎤 Voice Note';
                alert('Upload failed — check connection.');
              });
          };
          recorder.start();
        })
        .catch(function() {
          alert('Microphone access denied.');
        });
    }
```

### Rules
- Write ONLY the replacement function — exactly as shown in the spec above
- Do NOT add any other code outside the function
- Do NOT recreate the button HTML — it already exists
- The function must handle: start → stop → upload → show result
