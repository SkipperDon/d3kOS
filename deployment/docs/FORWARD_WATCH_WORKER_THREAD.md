# signalk-forward-watch v0.2.0 — Worker Thread Fix

**Plugin:** `signalk-forward-watch`
**Repo:** `github.com/SkipperDon/signalk-forward-watch`
**npm:** `signalk-forward-watch@0.2.0`
**Fixed:** 2026-03-11 (Session Part 22)

---

## Symptom

Signal K became unstable when `signalk-forward-watch` was installed. SK heap grew by ~470MB at startup, even when the plugin was set to `enabled: false` in the admin UI. In Part 21 (2026-03-08), the plugin was physically deleted from `~/.signalk/node_modules/` to restore SK stability.

## Root Cause

`plugin/detector.js` opened with:

```js
const ort = require('onnxruntime-node');
```

This is a **top-level `require()`**. Node.js evaluates all top-level requires when a module is first loaded — not when a function inside it is called. Signal K loads all registered plugin modules at startup regardless of their enabled state. This meant onnxruntime's full binary runtime (~470MB) was loaded into SK's main process heap on every boot, even if the plugin was never started.

---

## Fix — v0.2.0

Moved all onnxruntime logic into a Node.js Worker thread (`plugin/detector-worker.js`). Worker threads have their own isolated V8 heap. The main SK process never loads onnxruntime.

### Architecture

```
Before (v0.1.x):
  SK process
  └── detector.js → require('onnxruntime-node')  ← loads into SK heap always

After (v0.2.0):
  SK process
  └── detector.js → require('worker_threads')    ← zero overhead
      └── [on plugin start()] → spawns Worker
          └── detector-worker.js → require('onnxruntime-node')  ← isolated heap
```

### Files changed

| File | Change |
|------|--------|
| `plugin/detector-worker.js` | NEW — onnxruntime, sharp, inference, NMS all run here |
| `plugin/detector.js` | Rewritten — thin wrapper. No onnxruntime import. Spawns worker on `init()`, relays messages, terminates on `terminate()` |
| `index.js` | Added `this.detector.terminate()` to `stop()` — ensures worker heap is freed when plugin is disabled |
| `package.json` | Version bumped to 0.2.0 |

### Worker communication protocol

```
Parent (detector.js) → Worker (detector-worker.js)
  { type: 'init', modelPath }       → worker loads ONNX session
  { type: 'detect', imagePath, confidenceThreshold }  → worker runs inference

Worker → Parent
  { type: 'ready' }                 → model loaded
  { type: 'detections', detections } → inference result
  { type: 'error', message }        → any failure (parent handles gracefully)
```

---

## Memory Impact

| State | v0.1.x | v0.2.0 |
|-------|--------|--------|
| Plugin registered, disabled | +470MB SK heap | 0MB added |
| Plugin enabled, running | +470MB SK heap | Worker heap isolated from SK |
| Plugin stopped | +470MB stays | Worker terminated, heap freed |

### Observed on Pi (2026-03-11)

- SK RSS at plugin start: 258MB
- SK RSS after 1 hour: 289MB (stable, expected growth from AIS data)
- Zero crashes, zero journal errors over 1-hour monitoring period
- Previous behaviour: SK OOM/crash before 1 hour

---

## Deployment

Files copied to Pi via scp, `npm install --omit=dev` run in plugin directory, plugin re-registered in `~/.signalk/package.json`, SK restarted.

ONNX runtime load confirmed by journal entry:
```
[W:onnxruntime:...] GPU device discovery failed: ReadFileContents Failed to open
file: "/sys/class/drm/card1/device/vendor"
```
This warning is expected on Pi (no GPU) — onnxruntime falls back to CPU automatically.

---

## Publishing

- **npm:** `npm publish` with granular access token (OTP alone insufficient when npm account has publish 2FA policy — requires token with `Read and Write` scope on the package)
- **GitHub:** `git push origin main && git push origin v0.2.0`
