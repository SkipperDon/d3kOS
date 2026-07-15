# v0.9.9.5 — Research & Discussion Backlog
**Version:** 1.1 | **Created:** 2026-06-23 S92 | **Updated:** 2026-07-15 S99 — D13 added | **Status:** DISCUSSION / PRE-APPROVAL
**Owner:** Donald Moskaluk — AtMyBoat.com / d3kOS

> **Purpose:** Captures every idea, research topic, and architectural discussion that has been
> explored across sessions but is NOT yet approved for build. These items have been discussed,
> researched, and in some cases fully designed — but no code has been written without an explicit
> go-ahead from the operator.
>
> This document is the "holding tank" between idea and PROJECT_CHECKLIST.md build task.
> When an item is approved for build, move it to PROJECT_CHECKLIST.md with a task breakdown.

---

## How to Read This Document

| Status Tag | Meaning |
|---|---|
| `[RESEARCH]` | Topic explored, no formal design yet |
| `[DESIGN COMPLETE]` | Full spec or architecture exists — ready to build when approved |
| `[PARTIAL DESIGN]` | Design started, gaps remain before build can begin |
| `[AWAITING COMMUNITY]` | Needs forum/user validation before operator commits to build |
| `[AWAITING OPERATOR]` | Needs a hardware, config, or external action from Don before progressing |
| `[DEFERRED]` | Explicitly deferred to a future version — do not action now |

---

## 1. WiBoat — WiFi CSI Marine Radar

**Status:** `[DESIGN COMPLETE]` — full engineering design, hardware BOM, and architecture ready. No code written.

**What was discussed and researched (S79–S82):**
- WiFi CSI (Channel State Information) as a zero-cost radar substitute using RPi 4B + nexmon_csi patch
- Time-of-flight range estimation via IFFT of CSI frequency response
- Angle of arrival (AoA) bearing estimation via MUSIC algorithm with 4-antenna UCA
- SP4T GPIO-controlled RF switch for time-multiplexed 4-channel CSI on a single BCM43455 radio
- 2× ALFA AWUS036NH TX injectors for continuous probe frame injection
- Heltec V3 LoRa module + batman-adv mesh for multi-boat cooperative sensing
- Integration with SafeHelm collision avoidance (WiBoat as the sensor layer)
- WebSocket server on port 8766, WiBoat Contact JSON schema, MMSI registry

**Research conclusions:**
- 4-antenna UCA resolves port/starboard ambiguity — no 2nd RPi needed
- EIRP constraint: ALFA at full power + 12dBi exceeds ISED 4W — must set TX to 21 dBm
- BCM43455 kernel must stay at 5.10 — do NOT run apt upgrade after flash
- Two-box Phase 1 (RPi 4B + RPi 5) → Phase 4 single-box consolidation

**Design documents:**
- `deployment/docs/wiboat/WIBOAT_SAFEHELM_FRD_v1.1.md` — 150+ functional requirements
- `deployment/docs/wiboat/WiBoat_BOM_v2.md` — full hardware BOM, $565–$868 CAD
- `deployment/docs/wiboat/WIBOAT_SAFEHELM_INTEGRATED_ARCHITECTURE.md` — port registry, MMSI, API
- 3× SVG architecture diagrams

**Open discussion questions before Phase 1 build:**
- Confirm RPi 5 on-boat static IP (10.42.0.1 is placeholder in FRD)
- Real-world range: literature says 10–20m indoor; open water with 12dBi omni TBD
- Does the SP4T RF switch switching speed introduce CSI phase discontinuities that break MUSIC?
- Will the 5.10 kernel + nexmon_csi combination still install on current Bullseye image?

**What would trigger moving to PROJECT_CHECKLIST.md:**
- Hardware procured (WB-02)
- On-boat IPs confirmed (WB-01)
- Don approves Phase 1 build start

---

## 2. SafeHelm — Maritime Collision Avoidance System

**Status:** `[DESIGN COMPLETE]` — full 7-layer architecture designed, COLREGs framework documented. No code written.

**What was discussed and researched (S76–S77):**
- 7-layer architecture: AIS ingestion → camera detection → contact fusion → CPA/TCPA engine → COLREGs classifier → conflict resolver → output (voice + AvNav widget + autopilot)
- COLREGs Rules 8, 12–19 compliance framework — stand-on/give-way roles, vessel type hierarchy
- Python service on port 8095 (standalone, NOT a Signal K plugin — needs threading, not Node.js event loop)
- AvNav integration via NMEA TCP injection — synthetic AIS vessels appear as native triangles on chart
- Voice alerts via existing ai_bridge (port 3002, Jabra S330 speaker), CRITICAL alerts bypass mute via espeak-ng subprocess
- pypilot integration (port 23322) deferred to Phase 4 — only after Phase 2 sea trial
- 4-phase build plan: Shadow (log only) → Advisory (voice + widget) → Conflict Solver → Autopilot

**Research conclusions:**
- Standalone Python is correct architecture; Signal K plugin would block on inference
- Camera-only mode is bearing-only (no range) — blocks CPA/TCPA for non-AIS targets
- WiBoat integration resolves the camera range limitation (fuse via ±15° bearing + ±50m range)
- AIS isolation is a hard Phase 1 gate — synthetic targets must NEVER reach the VHF transponder
- 4-layer AIS isolation spec written: `wiki/concepts/ais-isolation.md`

**Design documents:**
- `deployment/docs/SAFEHELM_DESIGN.md` — 1,312-line production-ready design
- `deployment/docs/safehelm/SAFEHELM_SYSTEM_SPEC.md` — file structure, systemd, COLREGs internals

**Forum article:** Ready for posting (Navigation & Charts category). Awaiting Don's post.

**10 known design gaps (PART 18 SH-01 to SH-15):**
- SH-02: Rule 12 (sailing vessels) — needs wind angle from NMEA
- SH-03: Rule 19 (restricted visibility / fog) — fog signal output, speed advisory
- SH-04: Night / low-light camera fallback
- SH-06: AIS-camera fusion algorithm spec — association threshold, bearing proximity
- SH-07: Virtual MMSI expiry logic — ghost vessel cleanup
- SH-08: Startup health check spec
- SH-09: Depth sounder → Safety Envelope pipeline
- SH-10: Incident logging spec (file, format, review UI)
- SH-15: AIS transmitPGNs explicit whitelist in Signal K (HARD GATE before any synthetic injection)

**Open discussion questions before Phase 1 build:**
- Don confirms: is radar connected to Signal K? (If yes, resolves camera range gap for CPA)
- Community interest in the forum article — needed to validate effort before building
- SH-15 AIS isolation whitelist must be verified on Pi before any code is written

**What would trigger moving to PROJECT_CHECKLIST.md:**
- Forum article posted and community response confirms interest
- Don approves Shadow Mode Phase 1 build

---

## 3. Sail-O-Vision — External Collaboration Opportunity

**Status:** `[RESEARCH]` — assessed for integration opportunity. No action taken.

**What was discussed and researched (S87 — 2026-05-21):**
- adamgoldberg's GitHub repo: Jetson-based YOLOv8l marine vessel detection
- `nmea_client.py` in sail-o-vision repo parses radar TTM sentences + AIS — directly reusable in SafeHelm Phase 1
- PTZ ONVIF camera control: adamgoldberg has not built it yet (same stage as d3kOS)
- AIS700 (Raymarine) confirmed transmit-only on N2K — does NOT relay received vessel PGNs back to bus
- Injecting synthetic NMEA2000 PGN 129038/129039 is safe with AIS700 (no VHF re-broadcast risk)
- Masthead geometry range formula confirmed: range = h / tan(θ), with roll compensation from PGN 127257
- Dragon's Lair simulator concept: mock ONVIF device returning video clips based on commanded position — validates SafeHelm state machine without live hardware

**Research conclusions:**
- `nmea_client.py` is a ready-made component — do not reinvent
- Dragon's Lair simulator is worth building before SafeHelm Phase 1 hardware test
- PTZ ONVIF integration is a natural collaboration point with adamgoldberg
- 4-layer AIS isolation is conservative for this hardware; explicit whitelist (SH-15) is still required

**Open discussion questions:**
- Has Don reached out to adamgoldberg about collaboration?
- Which component to integrate first: nmea_client.py (easiest) or PTZ ONVIF?
- Is Dragon's Lair simulator worth building before SafeHelm Phase 1? (Low cost, high validation value)

**What would trigger action:**
- Don decides to reach out to adamgoldberg OR
- SafeHelm Phase 1 approved (then integrate nmea_client.py as component)

---

## 4. D3K-Lite — Free OpenPlotter Addon

**Status:** `[AWAITING COMMUNITY]` — feasibility study complete (1,261 lines), forum article drafted. No code written.

**What was discussed and researched (S78 — 2026-05-11):**
- Free .deb addon that wraps OpenPlotter (Signal K, AvNav) with d3kOS dashboard, Gemini AI, Windy weather, Fix My Pi diagnostics
- 70% code reuse from d3kOS with path/port/env-var changes
- Flask on port 8085 (not 8080 to avoid AvNav, not 3000 to avoid Signal K)
- Python 3.11 venv on Bookworm, systemd services, no changes to OpenPlotter core
- Estimated build: 25 hours across 4–5 sessions
- Mobile companion: QR pairing, same PWA as d3kOS
- Upgrade path: d3k-lite users → d3kOS (same AtMyBoat.com account)

**Research conclusions:**
- Technically feasible — no major architectural blockers
- Key risk: OpenPlotter's service names and config paths differ from d3kOS — mapping exercise needed
- Target audience: OpenPlotter users who want dashboard + AI + mobile without building full d3kOS

**Forum article:** Ready for posting (Navigation & Charts, Interest Gauge frame). Awaiting Don's post.

**Open discussion questions:**
- Is this a free product or freemium? (Removed pricing from article per Don's instruction — decision still open)
- Does d3k-lite share the AtMyBoat.com Fix My Pi subscription model?
- What is the priority relative to WiBoat and SafeHelm?

**What would trigger moving to PROJECT_CHECKLIST.md:**
- Forum article posted and community interest confirmed (DL-3)
- Don approves Phase 1 build

---

## 5. signalk-forward-watch — Open Items Post-v0.2.3

**Status:** `[PARTIAL DESIGN]` — v0.2.3 live on npm and Pi. Three small improvements discussed.

**What was discussed:**
- Download-on-first-run: instead of requiring manual model download, plugin downloads YOLOv8n ONNX on first enable
- OpenPlotter compatibility test: run the plugin on a real OpenPlotter instance (Signal K on different base OS)
- README update: Step 2 (model download) is now unnecessary — README still references it

**Research conclusions:**
- Download-on-first-run is a standard npm plugin UX pattern — low complexity
- OpenPlotter test is a prerequisite for d3k-lite (plugin must work on OpenPlotter before d3k-lite wraps it)

**Open discussion questions:**
- What model hosting URL for download-on-first-run? (GitHub releases, Hugging Face, or npm asset)
- Does OpenPlotter use the same Node.js Signal K server version as d3kOS?

**What would trigger moving to PROJECT_CHECKLIST.md:**
- Don approves one or more of these small improvements for a v0.2.4

---

## 6. AAO Data Collection System

**Status:** `[AWAITING OPERATOR]` — architecture designed (v1.1), deploy plan ready. Blocked on UpdraftPlus backup prerequisite.

**What was discussed and researched (S70–S81):**
- Public data collection endpoint at `atmyboat.com/research/` for AAO methodology research
- MySQL tables: `aao_contributors` + `aao_sessions`
- PHP endpoints: `aao-register.php`, `aao-submit.php` (validation + IP hash), `aao-data.php` (public JSON API)
- `aao-collector.py` — Python stdlib script for contributors to submit their session data
- Privacy policy page, landing page with dataset download link
- Architecture doc: `aao-methodology-repo/data-collection/ARCHITECTURE.md` v1.1

**Research conclusions:**
- No new infrastructure needed — HostPapa MySQL already paid
- IP hashing ensures contributor anonymity
- System supports the research paper (Governing the AI Productivity Promise v3.3)

**Blocked on:**
- DC-02: UpdraftPlus backup before DB changes (Don's action)
- DC-03: Confirm `admin@atmyboat.com` deliverability on HostPapa (Don's action)

**What would trigger moving to PROJECT_CHECKLIST.md:**
- Don completes DC-02 and DC-03 and gives go-ahead

---

## 7. Mobile App PWA — Remaining Build Work

**Status:** `[PARTIAL DESIGN]` — strategy and architecture decided (S14, strategy brief v2.0.0). Core PWA exists on staging. Command queue, fleet screen, OTA not yet built.

**What was discussed:**
- Fix My Pi remote diagnostics from phone (T1+ tier feature)
- Find My Boat: Pi syncs position → PWA chart shows boat marker
- OTA firmware update triggered from phone
- Fleet Management map screen (Leaflet, PWA)
- Command queue round-trip: phone → HostPapa PHP broker → Pi executes → result returned

**Research conclusions:**
- Architecture decided: PWA + HostPapa PHP message broker (no third-party relay)
- WebRTC/STUN P2P confirmed for live Pi ↔ phone connection
- Tailscale must be removed before v0.9.4 build begins
- All payments via Stripe on atmyboat.com only — never in-app

**Open discussion questions:**
- Is live Pi ↔ phone connection (WebRTC STUN) needed before OTA/command features?
- Which PWA feature is highest priority: Fix My Pi, Find My Boat, or command queue?

**What would trigger moving to PROJECT_CHECKLIST.md:**
- Don approves a specific PWA feature for build
- v0.9.9.4 on-boat validation complete first (prerequisite)

---

## 8. pypilot Integration — SafeHelm Phase 4

**Status:** `[DEFERRED]` — explicitly deferred until SafeHelm Phase 2 sea trial is validated.

**What was discussed:**
- pypilot on port 23322, direct TCP, for automated helm correction based on COLREGs advisory
- Integration only after Phase 2 (advisory mode + voice alerts) survives one full sailing season
- High risk — wrong autopilot commands at sea = collision, not avoidance

**Why deferred:** Cannot rush autopilot integration. Calendar gate WB-14 (one full sailing season in advisory mode) is a hard prerequisite. No further design work on pypilot until that gate passes.

---

## 9. Research Paper — Governing the AI Productivity Promise

**Status:** `[AWAITING OPERATOR]` — paper v3.3 complete. Submission is Don's action.

**What was discussed and researched (S70):**
- Target journal: Research Policy
- Dataset v2: 36 sessions, `session_sqs_dataset_v2.csv`
- Exclusion log: 23 of 33 excluded sessions documented, 10 remain
- `ai_model_version` column still shows placeholder "claude-sonnet-4" — needs verification before submission

**Operator actions required:**
- PAPER-4: Verify ai_model_version in dataset (all 36 rows)
- PAPER-5: Document remaining 10 excluded sessions
- PAPER-7: SSRN upload first, then journal submission

---

## 10. AAO Methodology — Open Evolution Items

**Status:** `[RESEARCH]` — AAO v2.0 published. Ongoing framework evolution.

**What was discussed:**
- Section 24 (Question Queue Protocol) is v2.0 — not yet exercised in a real build session; threshold of 3 open questions may need tuning
- "Queue-Governed Build" compliance label (§24.9.2) is new — no reference implementation
- LinkedIn article "I Wrote 140 Lines to Teach My AI to Say 'I Don't Know'" — approved by Don (S90 addendum)
- AAO About the Author section on LinkedIn still says v1.9 — should be updated to v2.0

**Open discussion questions:**
- Should Section 24 threshold be 3 questions or adjusted after first real-world use?
- Is a reference implementation of Queue-Governed Build needed before it can be cited?

---

## 11. 360° Marine Vision — NCS2 Cameras + Satellite Overlay + Cellular (New Animation & Satellite)

**Status:** `[PARTIAL DESIGN]` — full case study written with working prototype Python code. No d3kOS-specific design doc exists yet. Not yet built.

**What was discussed (S92 2026-06-23):**

A 360° situational awareness system using four Reolink PoE cameras accelerated by an Intel Neural Compute Stick 2 (NCS2), with a dual-layer helm display combining live AI detection overlays and satellite base map imagery, connected via eSIM/4G cellular.

### Hardware Stack
- RPi 4B (8GB) — stream ingest + orchestration only
- Intel NCS2 (USB 3.0) — 100% of YOLOv8n inference offloaded here
- 4× Reolink PoE cameras: 2× RLC-810A (bow + stern), 2× RLC-820A (port + starboard)
- Marine DC PoE switch (12V/24V input → 48V PoE output)
- eSIM/4G HAT — cellular connectivity for satellite tile download offshore

### Core Efficiency Design
The problem: 4× 4K streams on RPi 4B = instant crash. Three strategies resolve this:

1. **Sub-stream harvesting** — pull Reolink RTSP sub-stream at 640×360 instead of 4K main stream. 95%+ data reduction. Matches YOLOv8n's native 640×640 input with minimal CPU resize cost.
2. **Frame skipping** — process 1 frame in 6. At 30 FPS source = ~5 inferences/second/camera. Marine hazards move slowly; this is sufficient for collision avoidance alerting.
3. **OpenVINO NCS2 offload** — YOLOv8n exported to OpenVINO IR format (.xml/.bin). RPi CPU handles only RTSP decode; NCS2 handles all matrix math. Target latency <150ms end-to-end.

### Marine Object Classes (model target)
`buoy` | `vessel` | `kayak` | `debris` | `person_in_water`

Note: Standard YOLOv8n (COCO) does not include these classes. A marine-specific fine-tuned or custom-trained model is required. Open question: source of training data.

### d3kOS Integration (Decoupled — standalone module)
The vision system does NOT integrate into d3kOS core files. It communicates via MQTT only:
- MQTT broker: `localhost:1883`
- Topic: `vessel/safety/vision_alerts`
- Payload: lightweight JSON — `{timestamp, source_camera, hazard_detected, confidence_score, inference_latency_ms}`
- Node-RED receives payload → Switch node routes by hazard type → Signal K delta (chart marker) + TTS voice alert ("Warning: Kayak detected on Port Midship")

This is consistent with d3kOS's existing standalone service pattern (SafeHelm port 8095, signalk-forward-watch plugin architecture).

### Satellite Imagery Layer (Dual-Layer Rendering)
Two completely decoupled display planes:
- **Front canvas (animation overlay):** HTML5 Canvas via Node-RED UI / d3kOS dashboard. Renders bounding boxes, hazard vectors, collision alarms. Updates 5–10 FPS from MQTT feed. Transparent background.
- **Base layer (satellite map):** MapLibre GL self-hosted on Pi. Requests static PNG/WebP tiles from satellite APIs. Only re-renders when boat moves into new coordinate tile.

**Satellite sources discussed:**

| Source | Revisit Rate | Resolution | Cost | Auth Required |
|--------|-------------|------------|------|---------------|
| NASA GIBS | Daily (3–5hr after capture) | 250m/pixel | Free | None |
| Copernicus Sentinel-2 (CDSE) | Every 5 days | 10m/pixel | Free tier (10k cloud credits/month) | Free account |

**Recommended hybrid stack:**
1. Primary base: self-hosted offline vector charts (MapLibre GL + OpenSeaMap data on Pi SD card) — works with zero internet
2. Satellite overlay: Copernicus Sentinel-2 true color when internet available (toggleable panel)
3. Active canvas: YOLOv8 detections drawn over charts locally — no internet needed

### Standalone vs. Integrated — Design Conclusion
The case study explicitly recommends standalone module, not integration into d3kOS core. Rationale:
- A camera/AI crash must never take down chartplotter
- AI pipeline can be resource-capped (Linux cgroups or Docker) without affecting Signal K
- AI stack (YOLOv8, OpenVINO, PyTorch) updates frequently — standalone prevents library conflicts with d3kOS

### Power Budget
Full system (RPi 4B + NCS2 inference + 4 camera streams): target <12W DC draw.

### Prototype code status
Working Python framework provided in case study:
- Multi-threaded (one thread per camera)
- OpenVINO NCS2 inference loop with frame skipping
- MQTT publish on detection
- RTSP reconnect on camera dropout
- **Note:** YOLO output parsing in prototype is simplified placeholder — real NCS2 OpenVINO output tensor format requires model-specific parsing implementation

---

**Research conclusions:**
- Architecture is sound and consistent with d3kOS patterns (MQTT, standalone services, Node-RED)
- NCS2 is discontinued hardware (Intel stopped production) — availability limited to used market; OpenVINO still supports MYRIAD plugin but support window is finite. Alternative: Hailo-8L (actively supported, similar form factor) or Google Coral USB.
- Marine class model is the critical missing piece — no off-the-shelf YOLOv8n model covers these classes
- NASA GIBS and Copernicus tile URLs in case study are template placeholders, not production-ready endpoints — real WMTS endpoint configuration work required
- eSIM/4G HAT model not specified — compatibility with RPi 4B and d3kOS network config to be confirmed

---

**Relationship to existing d3kOS items:**
- **signalk-forward-watch:** Existing Pi plugin also uses YOLOv8n ONNX but runs in CPU mode on Node.js Worker thread. NCS2 approach would be a separate Python service — they could coexist or NCS2 approach could supersede it for Pi.
- **SafeHelm:** NCS2 camera detections could feed SafeHelm's sensor fusion layer (Layer 1) as the camera detection source — this is a natural integration point. Reduces camera range limitation for non-AIS targets.
- **Camera Overhaul (existing):** Current d3kOS camera system uses slots.json/hardware.json, fish detector, and frame buffer. NCS2 system would be a parallel standalone service using the same physical cameras via RTSP. No conflict, but camera IP coordination needed.
- **WiBoat:** WiBoat provides range via WiFi CSI; NCS2 cameras provide classification. Combined: range + class = complete non-AIS contact picture. Strong synergy.

---

**Open questions before any design work begins:**
1. Is the Intel NCS2 the target hardware, or is Don open to Hailo-8L / Google Coral as actively-supported alternatives?
2. Where does the marine-class YOLOv8 model come from? Options: (a) fine-tune on marine dataset, (b) use sail-o-vision's Jetson YOLOv8l model converted to OpenVINO, (c) find existing marine detection model
3. Does Don want this as a pure SafeHelm sensor layer or as a standalone dashboard feature with its own display panel?
4. eSIM/4G HAT: which model? Needs to confirm RPi 4B compatibility and whether cellular replaces or supplements the existing boat network
5. Is MapLibre GL the right chart engine, or should this integrate with AvNav (already running on Pi port 8080)?
6. Offline vector chart tiles: OpenSeaMap tiles or official NOAA/CHS ENC tiles?

**What would trigger moving to PROJECT_CHECKLIST.md:**
- Don confirms target hardware (NCS2 vs. Hailo vs. Coral)
- Marine class model source identified
- Don decides: standalone vision system vs. SafeHelm sensor layer vs. both

---

## 13. VHF Communication Suite — Audio Replay + STT Transcription + Translation + Signal K Alerts

**Status:** `[PARTIAL DESIGN]` — base project identified and assessed (S99 2026-07-15). Four-phase architecture defined. No d3kOS code written yet. Blocking unknown: VHF radio audio tap accessibility.

**What was discussed and researched (S99 2026-07-15):**

Based on open-source project `github.com/hwater/vhf-clear-audio-replay` (MIT, created 2026-07-02). Don intends to adapt and extend this project for d3kOS as a four-phase communications feature. Community engagement with project author underway.

### Phase 1 — VHF Audio Replay (Base Project)

Taps the VHF radio's speaker/line-out jack via a USB audio adapter. Records every transmission as a denoised MP3 using sox VOX detection and ffmpeg spectral denoising (EBU R128 normalization). Classifies recordings as speech vs. carrier noise via a lightweight Python modulation index classifier (numpy only — no ML model). Serves a browser-based replay list with waveform thumbnails on port 8088.

**Signal path:**
```
VHF radio speaker out → USB audio adapter (C-Media 0d8c:0014)
  → ALSA dsnoop (vhf device) → sox VOX threshold (3% amplitude)
  → sox bandpass filter (250–3400 Hz) → ffmpeg FFT denoise + loudness normalize
  → MP3 file → vhf-classify.py (modulation index) → speech or noise
  → vhf-web.py (port 8088) → browser replay list
```

**New hardware required:** USB C-Media audio adapter (e.g. Unitek Y-247A, ~$10–15 CAD). No SDR hardware. RTL2838 dongle / rtl_ais stack completely unaffected.

**d3kOS integration pattern:** Two systemd services (`vhf-recorder.service`, `vhf-web.service`) behind one nginx `location /vhf/` reverse-proxy block. Port 8088 is unoccupied in d3kOS port registry. Signal K vessel name integration pre-built in base project (reads `vessels.self.name`). Storage path redirected from `/srv/music/` (OwnTone-centric) to `/opt/d3kos/data/vhf/`. OwnTone dependency removed from service file (one-line edit).

**Pre-install checks required:**
- VHF radio model: confirm accessible audio output jack (speaker terminals or 3.5mm)
- `/etc/asound.conf` on Pi: check for existing content — must merge if present
- ALSA card index: base project pins adapter to `hw:3` — confirm no collision with existing Pi audio devices

### Phase 2 — Signal K Keyword Alerts

Post-transcription keyword scan pushes notifications to Signal K alert tree. Triggers a visual flash and optional TTS voice alert via the existing Helm AI voice path.

**Keywords to detect:** `MAYDAY`, `PAN-PAN`, `SÉCURITÉ` / `SECURITE`, vessel MMSI (from Signal K `vessels.self.mmsi`), vessel name (from Signal K `vessels.self.name`).

**Signal K notification PUT:**
```
PUT http://localhost:3000/signalk/v1/api/vessels/self/notifications/vhf/<alert-id>
{ "value": { "message": "MAYDAY detected on CH16", "state": "alarm", "method": ["sound","visual"] } }
```

**Complexity:** ~20 lines of Python. Highest-value, lowest-cost enhancement. Can ship with Phase 1.

### Phase 3 — Faster-Whisper STT Transcription

Runs Faster-Whisper (CTranslate2-based) locally on the Pi CPU after each classified-speech MP3 is written. Not real-time — async post-processing only.

| Model | RAM | Time per 10s clip on Pi 5 | Recommendation |
|---|---|---|---|
| `tiny` | ~150MB | ~3–5s | Minimum viable |
| `base` | ~300MB | ~8–12s | Recommended — better maritime vocab |
| `small` | ~500MB | ~25–40s | Too slow for realtime replay |

**Transcript displayed in replay list** beside the audio waveform. Enables full-text search of radio log.

**Dependency:** `pip install faster-whisper`. CUDA not required (CPU-only Pi). Model downloads from HuggingFace on first run — needs internet once; can be pre-downloaded during install.

**Pi memory gate:** Confirm `free -m` on Pi shows >500MB available after d3kOS services load before committing to `base` model. If headroom is tight, use `tiny`.

### Phase 4 — Argos Translate (Local Offline Translation)

Pipes transcription text through Argos Translate (fully offline, CPU neural MT) for real-time English translation of non-English transmissions. Designed for international waters — French coast guard (St. Lawrence, Québec) is the primary Canadian use case.

**Language detection:** `langdetect` Python library (~1MB, no model — pure statistical). Detects language before deciding whether to invoke translation model.

**Model loading strategy:** Lazy-load on first detection of a specific language; cache model in memory for session. Pre-load French-English pair (~150MB) as default; expose language selector in Settings for user configuration. Do NOT pre-load all 30+ Argos language pairs.

**Both original text and English translation displayed** in the replay list.

---

**Research conclusions:**
- Base project (Phase 1) is a near-perfect d3kOS fit: Trixie-compatible, systemd-native, Signal K-aware, zero pip dependencies, MIT licensed. Fork and own it if needed.
- Keyword alerts (Phase 2) is the highest value/effort ratio of the four phases — should ship with Phase 1.
- Faster-Whisper (Phase 3) is feasible on Pi 5 with `base` model if memory headroom is confirmed. No GPU needed.
- Argos Translate (Phase 4) requires language selection decision: which pairs to support (French-English at minimum for Canada). Lazy-load pattern prevents RAM overcommit.
- Total new apt packages for Phase 1: `sox`, `ffmpeg`, `alsa-utils`, `python3-numpy`.
- Total estimated build effort: Phase 1+2: ~4 hours. Phase 3: ~3 hours (model integration + UI). Phase 4: ~3 hours (language detection + translation pipeline + Settings UI). All four phases: ~10 hours.

**Community context:** Project was discovered in July 2026. Don has engaged with the hwater/vhf-clear-audio-replay GitHub community. d3kOS implementation would be a fork/adaptation, not a direct inclusion.

---

**Open questions before Phase 1 build:**
1. **Radio audio tap (BLOCKING):** What is the VHF radio model? Does it have a 3.5mm speaker jack or accessible speaker terminals for the USB audio adapter tap?
2. **`/etc/asound.conf` check:** Does the Pi currently have an `/etc/asound.conf`? (Run `cat /etc/asound.conf` on Pi to verify before install.)
3. **ALSA card index:** What audio devices are currently on the Pi? Run `aplay -l` on Pi to confirm card 3 is unoccupied (or adjust udev rule accordingly).
4. **Pi memory headroom:** Run `free -m` on Pi after d3kOS services load — is there >500MB available for Faster-Whisper `base` model, or should `tiny` be used?
5. **Translation languages:** French-English as the default pre-loaded pair — is that correct? Any other language pairs needed for anticipated cruising areas?

**What would trigger moving to PROJECT_CHECKLIST.md:**
- VHF radio audio tap confirmed accessible (blocking question 1 resolved)
- Don approves Phase 1 + Phase 2 build start

---

## 12. On-Boat Validation — Prerequisite for Everything Above

**Status:** `[AWAITING OPERATOR]` — all build work above is blocked until d3kOS is validated at the helm.

**Why this matters:** WiBoat, SafeHelm, D3K-Lite, and the PWA all build on top of d3kOS. If d3kOS has issues on the boat (GPS, cameras, NMEA2000, touchscreen keyboard BUG-08), those issues will compound during Phase 1 builds of the above systems.

**Critical on-boat items to clear first:**
- OB-2: GPS live fix confirmation (outdoor, dock, clear sky)
- OB-5: BUG-08 keyboard fix confirmation on Pi touchscreen
- OB-I04: NMEA2000 backbone connected to Pi
- OB-3: Signal K live data (SOG, COG, DEPTH, AIS) confirmed

---

## Prioritization Discussion (not decided — for Don's review)

| # | Item | Complexity | Dependency | Value |
|---|------|------------|------------|-------|
| 1 | On-boat validation (prerequisite) | Low — already built | None | Required |
| 2 | BUG-08 keyboard v2.2 fix | Low (1 file) | On-boat test | Blocks multilingual |
| 3 | signalk-forward-watch v0.2.4 | Low (3 small items) | None | Community visibility |
| 4 | SafeHelm forum article post | Zero (article ready) | Don's action | Community validation |
| 5 | D3K-Lite forum article post | Zero (article ready) | Don's action | Community validation |
| 6 | SafeHelm Phase 1 Shadow Mode | High | Forum validation + SH-15 gate | Safety capability |
| 7 | WiBoat Phase 1 | High | Hardware procurement | Sensor capability |
| 8 | D3K-Lite build | High | Community validation | New user segment |
| 9 | AAO data collection system | Medium | Don backup action | Research infrastructure |
| 10 | PWA feature build | Medium | On-boat validation | User experience |
| 11 | Research paper submission | Zero (paper ready) | Don verifies dataset | Academic record |
| 11b | 360° Vision: NCS2 cameras + satellite + cellular | High | Hardware selection + model source | Safety + awareness |
| 12 | VHF Communication Suite (D13) — Phase 1+2 | Low (~4h) | Radio audio tap confirmed | Safety + situational awareness |
| 12b | VHF Communication Suite (D13) — Phase 3+4 (STT + Translation) | Medium (~6h) | Pi memory confirmed + Phase 1 live | Safety + international ops |
| 13 | pypilot integration | Very High | SafeHelm Phase 2 sea trial | Automation |

---

*This document is maintained by Claude Code. When an item is approved for build, create a task breakdown in PROJECT_CHECKLIST.md and mark that item as promoted here.*
*Do not delete entries — update status or mark PROMOTED.*
