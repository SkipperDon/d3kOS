# Entity: signalk-forward-watch

*Last updated: S86 2026-05-21 | Sources: MEMORY.md, signalk-forward-watch repo*

---

## Identity

- **Type:** Signal K plugin (npm package)
- **Version:** v0.2.3 (current, published)
- **npm:** `signalk-forward-watch`
- **Local repo:** `/home/boatiq/signalk-forward-watch/`
- **Pi path:** `~/.signalk/node_modules/signalk-forward-watch/`
- **Status:** Live and deployed on Pi

---

## What It Does

ML-based marine target detection plugin for Signal K. Detects vessels using ONNX inference (YOLOv8n + EfficientNet-483) from camera feeds. Distinct from SafeHelm — this is the *existing* deployed detection layer. SafeHelm consumes its output as one data source.

---

## Architecture

### Worker Thread (critical — do not change)

onnxruntime loads ~470MB into Node.js memory at `require()` time. Without the worker thread, this would be loaded into Signal K's main heap on every start, even when the plugin is disabled.

**Fix (v0.2.0):** ONNX inference runs in a Node.js Worker thread (`detector-worker.js`). SK heap is unaffected regardless of plugin enable/disable state.

### ONNX Pipeline

| Step | Model |
|------|-------|
| Detection | YOLOv8n |
| Classification | EfficientNet-483 |
| Species ID (on-demand) | Gemini Vision |

---

## Key Fixes — v0.2.3

**geodesy ESM/CJS fix:**

geodesy v2 uses `"type":"module"`. On Node 22+, `require()` returns a namespace object (silent failure — all detections dropped). On Node <22, `require()` throws `ERR_REQUIRE_ESM`.

**Fix:** Inline Vincenty spherical haversine in `gps-calculator.js`. geodesy dependency removed entirely.

---

## Deploy Pattern

Direct scp to Pi works without npm publish:
```bash
scp -i ~/.ssh/id_d3kos <file> d3kos@192.168.1.237:~/.signalk/node_modules/signalk-forward-watch/
```

For full publish cycle, use npm:
- **Always run `npm pack --dry-run` before `npm publish`** — bad v0.2.2 publish included internal .txt docs
- `.npmignore` covers `*.txt`, `ROADMAP.md`, `.aao-backups/`
- Once a version is unpublished, that version number cannot be republished — must bump

**npm token:** stored in `~/.npmrc` on this machine. Rotate via npmjs.com → Access Tokens after every session that publishes.

---

## Related

- [[entities/safehelm]] — SafeHelm consumes forward-watch detections as camera data source
- [[entities/pi-system]] — host platform
- [[entities/d3kos-platform]] — Signal K runs on port 8099
