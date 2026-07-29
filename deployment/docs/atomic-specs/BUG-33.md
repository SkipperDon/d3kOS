# Atomic Spec — BUG-33 (Hazard Alerting Disabled; 5-Minute Detection Interval)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · documentation only
**Created:** 2026-07-29 (S110) by Tier 1 (Opus 5)
**⚠ RETROACTIVE SPEC** — fix was applied directly on the Pi in S110 without following §25 workflow.
This spec documents the fix as applied. No Haiku handoff occurred. This is a known deviation from
the §25 process (acknowledged by operator S110). Logged as UAC event in session quality metrics.
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-33 · `PROJECT_CHECKLIST.md` PART 17
**Severity:** HIGH — safety (5-minute detection interval = zero detections during any normal hazard encounter)
**Refines:** BUG-21 (pipeline IS built end-to-end; config was the only defect)
**Credential constraint:** the target file contains `camera_pass` and RTSP URL with embedded
password. This file MUST NEVER be committed to the canonical tree or any repo. No test file
was created (tests in `tests/` read from the canonical tree; target file is excluded).
**On-boat validation required:** yes — RTSP camera is on boat subnet only; lab Pi cannot reach it.

---

## Tier-1 finding

### Root cause (confirmed from live Pi evidence, S107 + S110)

Two config defects in `signalk-forward-watch.json`:

1. **`audio_alarm: false`** — the audible warning path is switched off entirely. The plugin
   source (`signalk-output.js`) calls `playBeep()` via `paplay`/`aplay` only when
   `audio_alarm === true`. With this false, no audio alert fires regardless of detection result.

2. **`detection_interval: 300`** — 300 seconds = 5 minutes between detection passes.
   A kayaker at close range during a 30-second crossing window will never be detected.
   The plugin's ONNX detection loop in `index.js` runs once every `detection_interval`
   seconds and early-returns (`if (!framePath) return`) if the RTSP grab fails. A 10-second
   interval is appropriate for collision avoidance.

### Pipeline status (confirmed S110 — no code changes needed)

`signalk-forward-watch` is built end-to-end:
- `index.js`: loads ONNX model at startup; detection loop runs every `detection_interval` s;
  calls `sendDetections()` which publishes to `environment.forwardWatch.detections` in SK
- `signalk-output.js`: fires SK `notifications.forwardWatch.*` when GPS + distance fields
  available; calls `playBeep()` when `audio_alarm: true`
- ONNX model present on Pi: `~/.signalk/node_modules/signalk-forward-watch/models/forward-watch.onnx` (12 MB)
- GPU warning at startup is expected on Pi 4 (no discrete GPU); ONNX Runtime uses CPU inference

### Fix

Two value changes to the plugin config on the Pi:
- `detection_interval`: 300 → **10** (10-second cycle; CPU cost ~50–150 ms/frame on Pi 4 at 10 s = safe)
- `audio_alarm`: false → **true** (enables audio alarm via `paplay`/`aplay`)

---

## CURRENT STATE (values on Pi before fix, S107 evidence)

**File — `/home/d3kos/.signalk/plugin-config-data/signalk-forward-watch.json`**
(⚠ contains credentials — NEVER commit)
```json
{
  "camera_ip": "10.42.0.100",
  "camera_user": "[REDACTED]",
  "camera_pass": "[REDACTED]",
  "rtsp_url": "rtsp://[REDACTED]@10.42.0.100:554/stream1",
  "detection_interval": 300,
  "alert_cooldown": 30,
  "audio_alarm": false,
  "confidence_threshold": 0.4,
  "enabled": true
}
```

---

## CHANGE (applied S110)

Two value changes — all other fields preserved:

| Field | Before | After |
|-------|--------|-------|
| `detection_interval` | `300` | `10` |
| `audio_alarm` | `false` | `true` |

Applied via:
```python
import json, pathlib
p = pathlib.Path('/home/d3kos/.signalk/plugin-config-data/signalk-forward-watch.json')
cfg = json.loads(p.read_text())
cfg['detection_interval'] = 10
cfg['audio_alarm'] = True
p.write_text(json.dumps(cfg, indent=2))
```

Signal K restarted after change: `sudo systemctl restart signalk`

---

## CONSTRAINT BOUNDARIES

- Do NOT change `confidence_threshold`, `alert_cooldown`, `camera_ip`, or any other field
- Do NOT commit this file to the repo at any path — credentials are present
- Do NOT pull this file into `deployment/v0.9.9.4/` canonical tree — ever
- Do NOT set `detection_interval` below 5 (CPU overload risk on Pi 4)

---

## INTERFACE CONTRACT

After fix:
- SK forward-watch plugin runs a detection pass every 10 seconds
- When RTSP grab succeeds and ONNX detects a target above `confidence_threshold: 0.4`:
  - `environment.forwardWatch.detections` is published to SK data store
  - `notifications.forwardWatch.*` is published when GPS + distance fields available
  - `paplay`/`aplay` is called for audio alarm

In the lab (camera unreachable):
- RTSP grab fails → `if (!framePath) return` → no detections published (expected)
- `environment.forwardWatch` key remains absent from SK data store (expected)

---

## TDD / VERIFICATION

**No test file created.** The target config file contains credentials and cannot go in
the canonical tree. Standard `tests/*.cjs` / `tests/*.py` read from repo paths — inapplicable.

**Manual verification commands (run on Pi after fix):**

```bash
# 1. Confirm values on disk
python3 -c "
import json, pathlib
cfg = json.loads(pathlib.Path(
  '/home/d3kos/.signalk/plugin-config-data/signalk-forward-watch.json'
).read_text())
assert cfg['detection_interval'] == 10, f'FAIL: interval={cfg[\"detection_interval\"]}'
assert cfg['audio_alarm'] == True,      f'FAIL: audio_alarm={cfg[\"audio_alarm\"]}'
print('PASS: detection_interval=10, audio_alarm=True')
"

# 2. Confirm ONNX model present
ls -lh ~/.signalk/node_modules/signalk-forward-watch/models/forward-watch.onnx

# 3. Confirm SK is running with plugin enabled
systemctl is-active signalk
```

**On-boat validation (required — cannot test in lab):**
```bash
# Wait 15 seconds, then check for detections key in SK data
curl -s http://localhost:8099/signalk/v1/api/vessels/self/environment/forwardWatch | python3 -m json.tool
# Expected: JSON with "detections" key (when camera reachable and ONNX runs)

# Confirm notifications path (when GPS active + detection occurs)
curl -s http://localhost:8099/signalk/v1/api/vessels/self/notifications | python3 -m json.tool
# Expected: "forwardWatch" key present
```

---

## Tier-1 verification notes (§25.8 — retroactive)

1. `detection_interval: 10` is appropriate — ONNX CPU inference on Pi 4 ≈ 50–150 ms/frame;
   10 s cycle leaves >98% idle time. Lower bound is 5 s per constraint.
2. `audio_alarm: True` in Python JSON serializes as `true` in JSON — correct for the plugin's
   JS `if (config.audio_alarm)` check.
3. All other config fields preserved — Python json.load/dump round-trip confirmed.
4. SK restart was required — plugin config is read at startup, not hot-reloaded.
5. `environment.forwardWatch` absent from SK data store in lab is confirmed expected behavior,
   not a regression. Root cause: `if (!framePath) return` at top of detection loop in `index.js`.
6. On-boat validation is the only way to confirm end-to-end — lab cannot substitute.

## Post-deploy verification (completed S110 — lab scope only)

- [x] Config values on disk confirmed: `detection_interval: 10`, `audio_alarm: True`
- [x] ONNX model confirmed present (12 MB)
- [x] SK running with plugin enabled after restart
- [x] GPU warning at startup confirmed expected (CPU fallback active)
- [ ] `environment.forwardWatch.detections` populated — **pending on-boat validation**
- [ ] `notifications.forwardWatch.*` published — **pending on-boat validation**
- [ ] Audio alarm fires — **pending on-boat validation**
