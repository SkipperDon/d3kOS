# Voice Audio Fix — Wrong Sound Card

**Date:** 2026-03-09
**Status:** RESOLVED — voice input and output working on correct device
**Problem:** Voice assistant had no audio input/output. Commands not heard, no spoken response.

---

## Root Cause

All 5 voice-related Python files were configured to use the HDMI audio device (card 0). The boat uses a Roland S-330 USB audio interface (`plughw:S330,0`) for microphone input and speaker output.

When the Pi boots with HDMI connected, ALSA assigns the HDMI output as card 0. The Roland S-330 USB device gets a different card index. Hardcoding `hw:0,0` or `default` pointed to the wrong device.

---

## Fix

Changed all 5 voice files to use `plughw:S330,0`:

| File | Location on Pi |
|------|---------------|
| `voice-assistant-hybrid.py` | `/opt/d3kos/services/ai/` |
| `boatlog-export-api.py` | `/opt/d3kos/services/boatlog/` |
| `voice-wake.py` | `/opt/d3kos/services/ai/` |
| `tts-engine.py` | `/opt/d3kos/services/ai/` |
| `audio-test.py` | `/opt/d3kos/services/ai/` |

`plughw:S330,0` uses ALSA's plug layer to match device name (`S330`) rather than card index. This is stable across reboots regardless of which card number ALSA assigns.

---

## Verify

```bash
aplay -l | grep -i s330
arecord -l | grep -i s330
```

Should show the Roland S-330 with its assigned card number. The `plughw:S330,0` syntax resolves this name automatically.
