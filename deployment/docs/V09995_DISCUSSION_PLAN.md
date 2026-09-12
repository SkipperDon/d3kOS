# v0.9.9.5 — Research & Discussion Backlog
**Version:** 1.5 | **Created:** 2026-06-23 S92 | **Updated:** 2026-09-12 S161 — **§17 D21 Extended AIS (internet overlay) NOT APPROVED — operator ruling. §18 D22 AIS receive-chain upgrade APPROVED as research (release TBD): Q1 rtl_ais channel config, Q2 on-boat antenna height, Q3 receiver value, Q4 transceiver — and Q4 makes SH-15 a blocking prerequisite, since a transmitting unit could broadcast synthetic SafeHelm/WiBoat targets to other vessels.** | Prior: 1.4 — S161 §17 logged, four premises corrected, hard constraint against feeding D02 recorded | Prior: 1.3 — 2026-09-10 S156 v0.9.9.5 scope reduced; v0.9.9.6 defined | **Status:** DISCUSSION / PRE-APPROVAL
**Owner:** Donald Moskaluk — AtMyBoat.com / d3kOS

> **Purpose:** Captures every idea, research topic, and architectural discussion that has been
> explored across sessions but is NOT yet approved for build. These items have been discussed,
> researched, and in some cases fully designed — but no code has been written without an explicit
> go-ahead from the operator.
>
> This document is the "holding tank" between idea and PROJECT_CHECKLIST.md build task.
> When an item is approved for build, move it to PROJECT_CHECKLIST.md with a task breakdown.

---

## Build Classification (updated S156 2026-09-10)

### ✅ SCOPE DECISION — S156 2026-09-10 (operator)
- **v0.9.9.5 scope reduced** to three items: D02, D05, D16 only. No new hardware required.
- **D11, D13, D15 deferred to v0.9.9.6.**
- **D01 WiBoat (Microware Spatial Awareness) moved to v0.9.9.6.**
- **v0.9.9.6 will target RPi 5** as the platform — with a PiCAN-M alternative HAT for NMEA2000 so RPi 5 users have full engine data functionality. PiCAN-M HAT compatibility with RPi 5 is uncertain; research and hardware selection is part of v0.9.9.6 scope.

---

### d3kOS Build — v0.9.9.5 (REDUCED SCOPE — decided S156)
Runs on the existing d3kOS Pi (RPi 4B). No new hardware required.

| Item | Description |
|------|-------------|
| D02 SafeHelm | Python collision avoidance service :8095, COLREGs engine, voice + AvNav integration |
| D05 signalk-forward-watch v0.2.4 | Three small improvements to existing Signal K plugin |
| D16 3D Surround Situational Awareness | Tesla-style 3D helm view in Chromium; existing 4 cameras; no new hardware |
| Bug corrections | All open v0.9.9.4 bugs carried forward |

**Hardware to procure for v0.9.9.5:** None — all three items run on existing hardware.

---

### d3kOS Build — v0.9.9.6 (defined S156)
Targets RPi 5 as the primary platform. Includes all items deferred from v0.9.9.5 plus WiBoat.
**Key architectural decision for v0.9.9.6:** replace PiCAN-M with a RPi 5-compatible NMEA2000 HAT or adapter — so users with RPi 5 hardware have full engine data functionality. HAT selection is part of v0.9.9.6 research scope.

| Item | Description |
|------|-------------|
| D11 360° Marine Vision AI | USB AI accelerator + MQTT service reading existing 4 cameras |
| D13 VHF Communication Suite | USB audio adapter, audio replay, Signal K alerts, STT, translation |
| D15 Universal Device Health | Real device health indicators in Settings (builds on BUG-50 fix) |
| D01 WiBoat | WiFi CSI marine radar — RPi 5 + ALFA adapters + SP4T switch + UCA antennas + LoRa mesh |
| RPi 5 platform | PiCAN-M alternative HAT/adapter for NMEA2000 on RPi 5 — research + selection TBD |

**Hardware to procure for v0.9.9.6 (preliminary):**
- RPi 5 board — ~$110 CAD
- RPi 5-compatible NMEA2000 HAT/adapter — TBD (research required)
- USB C-Media audio adapter (D13) — ~$15 CAD
- USB AI accelerator — NCS2 / Hailo-8L / Google Coral (D11) — decision pending
- 2× ALFA AWUS036NH USB adapters — ~$100 CAD
- SP4T RF switch (GPIO-controlled) — ~$45 CAD
- 4× 12dBi omni antennas (UCA array) — ~$180 CAD
- Heltec V3 LoRa module — ~$30 CAD

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

**Status:** `[APPROVED]` — v0.2.3 live on npm and Pi. All three improvements approved S156 2026-09-10 for v0.9.9.5. Tracked as SK-FW-1/2/3 in PROJECT_CHECKLIST.md.

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

> **⚠ Phase 3 has a SECOND consumer — BUG-23b (moved here S117 2026-08-02).**
> Boat Log **voice notes cannot be transcribed** for exactly the same reason the VHF audio cannot:
> **there is no speech-to-text engine installed on the Pi at all.** Recording works; nothing turns
> speech into text. This is an absence, not a defect — which is why BUG-23b was moved out of the
> v0.9.9.4 bug tracker. Installing Faster-Whisper for Phase 3 below **also unblocks Boat Log voice
> notes**, so scope Phase 3 with both consumers in mind rather than as VHF-only.
> (BUG-23**a** — the voice service respawn hot loop, 39% CPU — was a real defect and was **fixed in
> S116**. It is unrelated to this.)

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

## 14. Unclean-Shutdown Hardening — System-Wide Self-Healing Audit

**Status:** `[RESEARCH]` — moved here from BUG-09 Part 2 by operator decision, S117 2026-08-02.

**Origin — read this before doing any work on it.** This was the second half of BUG-09, which was
**closed as NOT A BUG** in S117. BUG-09's first half claimed power loss corrupts AvNav data. That
claim was never verified — it was recorded in S94 from an operator observation of a *symptom* and
carried forward as fact for a month. **No AvNav corruption has ever been observed, captured or
reproduced.** Every actual investigation found a different, real cause:
- **S96 (on the boat):** `AVNUsbSerialReader` reopening `/dev/ttyACM0` at every baud rate while
  gpsd held the port exclusively for Signal K — a log-flooding error loop that made AvNav *look*
  broken. AvNav was never down. **Fixed S96.**
- **S96 (on the boat):** blank charts caused by the **o-charts licence expiring 2026-04-01**, with
  the 1.3 GB of chart files intact on disk. A renewal (OB-O05), not a defect.

This item is therefore **hardening against a risk that is real in principle but has never been
demonstrated here.** It is not a defect and must not be re-entered in the bug tracker.

**⛔ Operator instruction S117 — do NOT build a watchdog for this.** A watchdog restarts a dead or
hung service; unclean-shutdown damage is to data at rest, so it would fail repeatedly. **BUG-23a
(fixed S116) is the worked example** — a watchdog hot-looping on a fault it could not repair, at
**39% CPU** and **~2,536 log lines/minute**.

**What was established S117 by live reads of the lab Pi (do not re-derive):**
- Root filesystem is **ext4 on the SD card** (`/dev/mmcblk0p2`, `defaults,noatime`, 117 GB, 22%
  used). ext4's default journalling protects filesystem *metadata*, not file *contents* — a file
  mid-write at power-off can be left torn while the filesystem itself checks out clean. SD cards
  add independent exposure: the flash translation layer can lose an entire block on power loss.
- **AvNav already self-heals its own config.** `/usr/lib/avnav/server/avnav_manager.py:249` —
  `getFallbackName()` returns `<cfg>.ok` (or `.initial`) and `getInvalidName()` quarantines a bad
  file as `.invalid-<UTC timestamp>`. **Do not build config repair for AvNav.**
- **AvNav's live write surface is tiny** — 14 files in 24 h (logs, GPS tracks, the `.ok` copy).
  `ochartsng` is 1.4 GB of the 1.4 GB total and is effectively static; only its logs change.
- `/dev/watchdog` and `/dev/watchdog0` exist but `RuntimeWatchdogSec` is **not** configured. That
  addresses the Pi **hanging** — a different failure from data damage.
- **No UPS, supercapacitor, or power-fail shutdown service exists.** Hold-up power is the only
  measure that actually prevents an unclean shutdown. Hardware; no product researched, and none
  should be named without research per the Hardware Claim Protocol.

**Scope if pursued — every service that writes persistent state:**
AvNav, Signal K (`~/.signalk/`), the Flask APIs, the SQLite databases, and the ChromaDB RAG store.

**Open discussion questions:**
- Is this worth doing at all, given no corruption has ever been demonstrated on this system?
- Should the 1.4 GB of static charts simply be made read-only, so the largest asset cannot be
  damaged regardless? (Highest value, lowest risk, independent of everything else here.)
- Is hold-up power the honest answer, making all software mitigation secondary?
- Should the unconfigured hardware watchdog be enabled on its own merits — for **hangs**, clearly
  labelled as unrelated to this item?

**What would trigger moving to PROJECT_CHECKLIST.md:**
- An actual instance of corruption being observed and captured on either Pi, **or**
- Don deciding the read-only-charts change is worth doing on its own merits.

---

## 15. Universal Device Health Framework — Is Any Connected Device Actually Working?

**Status:** `[RESEARCH]` — moved here from **BUG-11** by operator decision, S117 2026-08-02.
Logged originally 2026-07-10 S95. No root cause, no design, never started.

**The problem in one line:** connect an AIS receiver, GPS, microphone or speaker of any make, and
d3kOS cannot tell the owner whether it is working. A broken device and a working device produce the
same experience — silence, no error, no feedback.

**Governing constraint — this is what makes it hard.** The solution **cannot be brand-specific**.
d3kOS ships worldwide; the make and model of connected hardware is unknown in advance. The correct
question is not *"what devices does Don use?"* but *"how does d3kOS reliably detect, verify and
monitor any device of this type?"* No whitelist, no lookup table of known hardware.

**Two failure classes, both must be covered:**
- **Class A — compatibility failure at connect time.** The device uses a protocol variant, baud
  rate, physical interface or data format d3kOS does not handle. Plugged in, system sees nothing,
  user sees nothing, no error surfaced.
- **Class B — silent operational failure at runtime.** The device was recognised at boot and later
  stopped producing valid data — cable fault, power brownout, RF signal loss, USB
  disconnect/reconnect. No runtime detection of this exists today.

### ⚠ Scope boundary against BUG-50 — read before starting

**BUG-50 stays in v0.9.9.4 and must NOT be folded into this item.** Logged S117, it is the
concrete, proven, bounded defect: the Settings page shows **GPS, AIS, OpenPlotter and AvNav as
green when they are dead**, because those rows are wired to the Signal K *server's* liveness rather
than to any actual data. Verified live — GPS shows green while `navigation/position` returns 404,
AIS shows green while Signal K holds zero targets.

| | BUG-50 (stays in v0.9.9.4) | D15 (this item) |
|---|---|---|
| Scope | GPS, AIS, OpenPlotter, AvNav indicators | The generic framework, **plus microphone and speaker** |
| State | Root cause proven, fix bounded | No root cause, no design |
| Blocking? | No — fix it now | No — research |

Fixing BUG-50 produces the **working reference implementation** that this framework can then
generalise. Do this item *after* BUG-50, not instead of it.

**Historical proof the problem is real:** throughout BUG-32 — when AIS was being discarded entirely
because `rtl_ais` was pushing into a port Signal K owns as its own output — the Settings page
displayed AIS as healthy. The owner had no way to know.

**Open discussion questions:**
- Is "data arrived recently" a sufficient universal health signal, or does each category need its
  own definition of alive?
- How is "no AIS targets because nothing is in range" distinguished from "receiver is dead"? These
  are genuinely different and a two-state indicator cannot express both — the honest answer may be
  three states including **UNKNOWN**.
- Microphone and speaker have no data stream to watch. Do they need active probing (a test tone, a
  capture sample), and is that acceptable to run automatically at the helm?
- Should this surface as a Settings page section, a dashboard indicator, or a notification?

**What would trigger moving to PROJECT_CHECKLIST.md:**
- BUG-50 fixed first, then Don approving a generic framework built on that pattern.

---

## 16. 3D Surround Situational Awareness — Tesla-Style Helm View

**Status:** `[APPROVED]` — spec written S156 2026-09-10. See `deployment/docs/D16_3D_SURROUND_VIEW_SPEC.md`. One open decision before build: go2rtc vs. camera_stream_manager.py (§5 of spec). No code written.
**Build group:** d3kOS Build — v0.9.9.5 (runs in Chromium on existing Pi, no new hardware)

**What was discussed (S147 2026-09-05):**

A surround situational awareness display rendered in Chromium. Uses the existing 4 cameras (bow, helm/stern, port, starboard — all RLC-810A/820A, confirmed installed S112). Accessible from the d3kOS dashboard via a single switch that toggles between AvNav (:8080) and this view (:3000/3d-view).

**Display mode decided:** Bird's eye view with prominent forward panel. Forward emphasis minimum 50 metres.

### Display Layout (decided S147 2026-09-05)

Three-zone layout integrated into the existing Marine Vision page. The toggle (AvNav ↔ Marine Vision) switches the iframe `src` — Marine Vision now contains all three zones.

Display is 1920×1200 landscape (confirmed from d3kOS Chromium flags).

```
┌─────────────────────────────┬──────────────────────┐
│  FORWARD PANEL              │  BIRD'S EYE STITCH   │
│  Bow cam — perspective view │  All 4 cameras        │
│  50m+ range rings (SVG)     │  Homography stitch    │
│  D11 detection boxes        │  Forward-emphasized   │
│  WiBoat range → rings Ph.3  │  D11 bearing markers  │
│  (~65% of top section)      │  (~35% of top section)│
├─────────────────────────────┴──────────────────────┤
│  MARINE VISION — existing screens (unchanged)      │
│  Camera grids · fish detection · controls          │
└────────────────────────────────────────────────────┘
```

**Why forward panel + bird's eye side-by-side (not pure bird's eye for 50m):**
Camera-only bird's eye transformation loses useful resolution past ~15–20m — a camera at 1–2m above the waterline sees 50m objects at a very shallow angle, and top-down projection compresses them to near-zero pixels. The forward perspective panel solves this: natural perspective projection shows 50m+ clearly with SVG range rings calibrated to the bow camera's FOV and mount height. The bird's eye stitch handles close-quarters spatial awareness around the hull. Same approach used by Garmin Surround View (commercial marine reference, confirmed S147).

**Precedent / prior art (researched S147 2026-09-05):**
- **Frigate NVR + go2rtc "Birdseye"** — closest open-source example. Uses go2rtc for streaming + tiled composite view. Not a true homography stitch — a grid of feeds. Confirmed go2rtc is the right streaming layer.
- **RPI_BEV (hichristensen)** — OpenCV perspective transformation for navigational assistance on RPi. Confirms the stitch approach works on Pi hardware. No browser output or RTSP.
- **4-camera surround on RPi 3 (hanifizzudinrahman)** — OpenCV surround view on Pi with fisheye cameras. Confirms Pi compute is sufficient.
- **Garmin Surround View** — only production marine bird's eye surround system. Six through-hull cameras, 360° view for docking. Commercially closed, thousands of dollars. Validates the marine use case.
- **Gap:** No open-source marine multi-camera bird's eye view served to a browser on a Raspberry Pi exists. d3kOS D16 would be the first.

### Architecture

**Phase 1 — Base view (no AI required)**
- Python Flask serves `/3d-view` page
- OpenCV homography stitches 4 camera RTSP sub-streams into bird's eye image (JPEG, served via existing camera service port 8084)
- Bow camera RTSP sub-stream displayed as perspective forward panel (HTML `<video>` element or MJPEG)
- SVG range rings at 10m / 25m / 50m overlaid on forward panel (calibrated to bow camera mount height + field of view)
- **Toggle switch — AvNav ↔ 3D view (HARD CONSTRAINT: must not touch engine or nav ribbon)**
  - AvNav already runs as `#avnav-frame` iframe inside the d3kOS dashboard. Engine row (`#rowEngine`) and nav row (`#rowNav`) are fully independent and stay full width at all times — this is existing behaviour ("ribbons stay full width").
  - The toggle switches only the iframe `src` — AvNav URL ↔ `:3000/3d-view`. One JS call. No page navigation.
  - The row-pill controls (BOTH / ENGINE / NAV / WX) that govern the ribbons are completely unaffected. Toggle must not be placed in the row-pill zone and must not interact with `showRow()`.
  - Toggle button sits outside both ribbon rows — exact placement confirmed against live layout during build.

**Phase 2 — D11 AI overlays**
- Page subscribes to MQTT `vessel/safety/vision_alerts` via WebSocket bridge
- Detection events appear as coloured bounding boxes on the forward panel
- Bearing-only markers appear as directional wedges on the bird's eye stitch
- No additional hardware — requires D11 (USB AI accelerator) to be operational

**Phase 3 — WiBoat range integration**
- WiBoat range measurements (WebSocket :8766) lock range rings to real measured distances
- Bird's eye markers become positionally accurate (bearing + range = true grid position)
- Forward panel range rings update dynamically from WiBoat data

### Open-source stack (researched S147 2026-09-05 — verified projects only)

**No Three.js or Babylon.js needed.** The browser does layout only. All video processing stays in Python/go2rtc. Plain HTML/CSS in an existing Flask template — fits the d3kOS pattern exactly.

**go2rtc** — `github.com/AlexxIT/go2rtc` — MIT licence ✅
- RTSP → WebRTC / MJPEG / HLS served to any browser
- Pre-built ARM64 binary, runs on Pi natively — no compilation
- All 4 Reolink RTSP sub-streams configured in one YAML file
- Forward panel: bow camera WebRTC stream in HTML `<video>` element
- 2,100+ commits, actively maintained

**Bird's eye homography stitch — implement directly in d3kOS using OpenCV** (Apache 2.0 ✅)
- Reference implementation: `github.com/dyfcalid/CameraCalibration` (Python + OpenCV, supports standard cameras, matches RLC-810A/820A) — but it is **GPL-3.0 ⚠️**
- d3kOS distributes as an SD card image (binary distribution). Including GPL-3.0 code requires a GPL-3.0 licence notice on d3kOS. **Decision: implement the stitch natively using `cv2.getPerspectiveTransform` + `cv2.warpPerspective` — ~50 lines of Python, Apache 2.0, no dependency on the GPL project. dyfcalid is the reference, not the dependency.**
- Output: OpenCV MJPEG stream → served by existing Flask camera service at port 8084 → HTML `<img>` element in the 3D view page

**SVG range rings** — plain SVG overlay on the `<video>` element, calibrated to bow camera FOV and mount height. No library needed.

**Open decision — go2rtc vs. `camera_stream_manager.py` at port 8084:**
go2rtc may overlap with the existing camera service. Boundary must be drawn before build: does go2rtc replace `camera_stream_manager.py`, run alongside it, or serve D16 only? This is a build-start decision.

### Hardware required
- **None** — uses existing 4 cameras, existing Pi, existing Chromium stack
- D11 USB AI accelerator required for Phase 2 overlays only

### Relationship to existing items
- **D11:** D11 is the detection backend; D16 Phase 2 consumes its MQTT output. D16 Phase 1 builds and ships independently.
- **WiBoat (Microware Spatial Awareness):** Provides range data for Phase 3 accurate positioning.
- **AvNav:** Not replaced — single-switch toggle keeps both available at the helm.

**Camera mount confirmed S147 2026-09-05 (photo provided by operator):**
- Position: starboard bow rail top, bullet-style Reolink mount, forward-facing
- Estimated height above waterline: ~1.2–1.5m (Monterey 265 bow rail height — freeboard not published in any spec sheet per research S147; must be measured on boat)
- Line of sight confirmed: 300m+ on open water at that elevation (operator confirmed from photo)
- 50m range trivially achievable. Ring distribution at ~1.5m height:
  - 10m ring: low in frame (near bow deck visible)
  - 25m ring: mid-frame
  - 50m ring: upper third (near horizon)

**Open questions before build begins:**
1. Precise bow camera height above waterline — tape measure, bow rail top to waterline, on next boat visit. Required for exact ring pixel positions.
2. Bow camera tilt angle — level or angled slightly downward? Affects ring vertical distribution.
3. Confirm horizontal FOV in installed position (RLC-810A spec: 87° — verify no obstruction from rail hardware).

**Installation standard — minimum camera height (applies to all d3kOS users, not just this boat):**

Different boats have different bow rail heights. D16 must work across all installations. The physics determines the minimum:

| Standard | Height | Reason |
|----------|--------|--------|
| Absolute minimum | 0.9m / 3 ft above waterline | Deck level on a small boat — wave interference becomes frequent below this |
| Recommended minimum | 1.2m / 4 ft above waterline | Typical bow rail height on recreational boats — range rings spread adequately across the frame |
| Ideal | 1.5m+ / 5 ft+ above waterline | Top of bow rail on mid-size+ boats — rings distribute cleanly across full frame height |

**Additional mounting requirements:**
- Forward-facing — no more than 15° downward tilt
- Clear sight line ahead — not obscured by windshield, bimini frame, or anchor hardware
- Camera must support RTSP sub-stream at 640×360 or lower (all Reolink models do)

**Calibration — user inputs their camera height, software calculates ring positions:**
The range ring pixel positions are calculated from camera height + camera FOV. D16 includes a settings input (camera height in metres/feet). User enters their measurement once; rings calculate automatically. No hardcoded values — works for any boat installation.

Formula: for a ring at distance d, with camera height h and vertical FOV θ_v:
`ring_y = frame_height × (0.5 - arctan(h/d) / θ_v)`

**What would trigger moving to PROJECT_CHECKLIST.md:**
- Don approves Phase 1 build start
- Can proceed without D11 — Phase 1 is camera-only

---

## 17. Extended AIS (Internet-Sourced) Overlay — "God's Eye View"

**Status:** ⛔ `[NOT APPROVED]` — **operator ruling S161 2026-09-12: "gods eye view is not approved."** Proposed, reviewed and declined in the same session. **No release assigned. No code written. Do not re-enter as an open build task.**
**Build group:** none. Retained as a research record only — the findings below are *why* it was declined, and should not be re-litigated without new information (e.g. AISStream materially changing its coverage, or a use case that is genuinely harbour-bound).
**Superseded in intent by:** **§18 / D22** — the receive-chain upgrade, which is the sensor improvement the operator was actually reaching for.
**Source document:** `d3kos-extended-ais-requirements-architecture.md` (operator-supplied, prepared against `bilawalsidhu/gods-eye-view`)

**What was proposed (S161 2026-09-12):**

The operator currently receives AIS on a USB device and asked about adding "something larger." The draft specifies a supplementary layer that pulls **terrestrial AIS from AISStream.io** over a websocket held server-side, exposes it to the frontend on a same-origin REST endpoint, and renders it as a visually distinct overlay alongside onboard-receiver contacts. Ten functional and eight non-functional requirements, a four-phase rollout, and an API contract are drafted.

### The core finding — this is not a receiver upgrade

The operator's framing ("AIS as a USB device … thinking of something larger") suggests a **sensor** improvement. Extended AIS is not one. It is a *different data source with different failure modes*, and the gain is much smaller than the draft implies:

| | Onboard RTL-SDR receiver | AISStream.io |
|---|---|---|
| Range | 15–25 nm, VHF line-of-sight | **~40 nm from shore stations** |
| Offshore | Works everywhere | **Nothing** — no satellite coverage |
| Latency | Real-time | 15–30 s+, and messages are **dropped** to slow consumers |
| Internet | None required | Hard dependency |
| Trustworthy for collision avoidance | Yes | **No** |

The draft's §2.2 cites "roughly 200 km near well-instrumented coastlines." AISStream's own documentation states vessels more than **~40 nm offshore disappear from the feed**. So the real marginal gain is a thin coastal band — roughly 15–25 nm out to ~40 nm — and **zero gain in exactly the water where a skipper is most exposed.**

A genuinely "larger" AIS capability is a **hardware** question: a dedicated dual-channel AIS receiver in place of the SDR dongle, and above all **antenna height**, which is what actually sets VHF line-of-sight. That is a separate item and has not been researched. *Uncertainty flag: no specific receiver or antenna has been evaluated — nothing is asserted about products or cost.*

### Premises in the draft that are wrong for d3kOS

Verified against the canonical tree `deployment/v0.9.9.4/` this session. **Do not build from the draft as written.**

1. **§2.1 — "AIS targets arrive via NMEA 2000/0183 hardware (CX5106 gateway or PiCAN-M HAT)." Wrong.** AIS comes from an **RTL-SDR USB dongle**: `etc/systemd/system/rtl-ais.service` runs `rtl_ais -T -P 10108`, feeding Signal K on **10108** — a dedicated port chosen precisely because Signal K itself owns 10110 as its NMEA0183 *output* (BUG-32; BUG-12 is closed with a standing "never re-enable the `ais` client provider on 10110"). The CX5106 is the **engine** gateway (resistance senders → N2K) and appears nowhere in the AIS path.
2. **§7.2 / §8 — markers cannot be drawn on "the existing chart layer" from a new `extendedAisLayer.js`.** AvNav is served on :8080 inside a **cross-origin iframe** (`#avnav-frame`, `opt/d3kos/services/dashboard/templates/index.html:194`). d3kOS cannot reach into its map. The only route proven in this project is the **BUG-19/BUG-20 pattern**: publish contacts into Signal K and let AvNav render them via `AVNSignalKHandler`. **That route trips the SH-15 hard gate** — PART 18 requires an explicit `transmitPGNs` whitelist on the Signal K canboat-js provider *before any synthetic AIS injection ships*, so nothing outbound can reach the boat's real N2K bus or a transmitting AIS unit.
3. **§7.2 file paths are not this repo.** `server/services/`, `server/routes/`, `.env.example` do not exist here. The canonical tree mirrors Pi paths (`opt/d3kos/services/...`), and the key-storage convention is `api-keys.json` / `config/*.env` — both gitignored, both covered by the pre-commit secret hook.
4. **The websocket must not live in the dashboard Flask process.** That process drives the helm kiosk; a blocking or crashing websocket there is BUG-105-class severity. Project pattern is a **separate systemd unit on its own port** (gemini-proxy :8097, ai-bridge :3002, camera :8084). NFR2's "no crash of the Flask process" is only achievable by not putting it there.

### Hard constraint — must never feed SafeHelm

⛔ **Extended-AIS contacts must be excluded from the D02 CPA/TCPA engine and the COLREGs classifier entirely — not merely styled differently or captioned with a disclaimer.**

This follows from the **§13.5 ruling (S160): alert authority must be proportional to sensor coverage.** A 15–30 s-delayed, droppable, internet-dependent position is not a basis for a give-way or stand-on call, and D20 records that the answer to "make SafeHelm more assertive" is "what sensor was added?" — an internet feed is not one.

The draft's **FR5** walks straight into this: it routes a tap into Helm Assistant so the user can ask *"how close will this vessel pass me"* — a CPA question answered from delayed data. FR5 needs an **explicit refusal path** ("this contact is internet-sourced; I can't compute a passing distance from it"), not a banner. The draft's NG1 states the feature "must not be marketed as" collision-avoidance-grade but contains **no requirement forbidding the data from entering the collision logic.** That gap is the single most important correction.

### Other gaps found

- **FR9 (Boat Log state transitions) is not currently implementable.** **BUG-24** is open: there is no server-side Boat Log capture service; `boatlog-engine.js` loads on `boat-log.html` only. FR9 needs the service that BUG-24 identified as an unmade design decision.
- **§10 Q4 overstates i18n.** Multi-language is **v1.1 deferred** — Layers 1, 2, 4 and 5 are all "not started" and four pages already lack translations. There is no live "18-language i18n system" to route through.
- **NG3 references a "Nine Tools grid."** *Uncertainty flag: I could not confirm that this is d3kOS terminology — it may have been carried in from another product. Verify before quoting it in any spec.*
- **AISStream terms for a commercial helm product are unresolved** (NFR8, §10.1). This is an operator/legal call, not an AI one. Note one term already confirmed and in the draft's favour: **direct browser connections are prohibited**, so the server-side proxy is mandatory rather than merely good practice.

### What the draft gets right

Server-side proxy and key isolation (G2/NFR1); bbox subscription centred on GPS rather than a global feed (FR1); off by default with explicit opt-in (FR7); dedup with the **onboard receiver taking rendering precedence** (FR10) — exactly the right precedence; a Pi-appropriate render cap of 500 against the reference project's 12,000 (NFR3); silence watchdog and reconnect (NFR4); low-bandwidth mode for metered links (NFR5); and the refusal to import the reference project's CCTV/FLIR cosmetic skins (NG3). The phased rollout is sensibly ordered.

### Fit with D17

Good fit. The feature needs internet and no accelerator, so it runs on the existing Pi 4 and would register in `capabilities-manifest.json` gated on connectivity — exercising D17's feature gate for a non-hardware capability, which nothing else in scope currently does.

### Scope concern

v0.9.9.5 currently holds **D02, D05, D16, D17 — 11 build tasks, none started**, and D02 alone carries 160 guard tests plus a COLREGs gap of 13 unimplemented rules out of 16. Adding a networked, credentialed, ToS-encumbered fourth data source to that release competes with the safety work already queued and is the kind of addition that turns a release into a rolling scope. **Recommendation was: v0.9.9.6, after D02 ships and after the ToS question is answered.** **Operator decision S161 2026-09-12: neither — leave as RESEARCH with no release assigned.** v0.9.9.5 keeps its four items; nothing is scheduled for D21.

**What would trigger moving to PROJECT_CHECKLIST.md:**
- AISStream ToS reviewed and confirmed acceptable for a commercial marine product (operator action)
- A value decision made with the real coverage numbers above, not the draft's ~200 km figure
- The hard constraint (no path into D02) written into the spec as a testable requirement with a guard test, per §12.1
- Operator assigns a release

---

## 18. AIS Receive Chain — Real Sensor Upgrade (Receiver + Antenna Height)

**Status:** `[APPROVED — RESEARCH, release TBD]` — approved S161 2026-09-12 by operator decision, applying the S161 suggestion after D21 was declined.
**Build group:** none yet — needs a release assignment once Q1/Q2 are answered.
**Scope:** research and measurement. **NOT procurement.** No code.

**Why this item exists:**

The operator's original ask (S161) was *"I have ais as usb device connected to d3kos but was thinking of something larger."* That is a **sensor** question. D21 answered it with an internet data source, which gave a thin coastal improvement and **zero additional coverage offshore** — so it was declined. This item is the sensor question, properly separated: what would actually extend what d3kOS sees, with no internet dependency.

> ⚠ **Nothing in this section is a hardware recommendation.** No receiver, antenna, cable, price or range figure has been researched. Per the Hardware Claim Protocol, every specific below is an **open question requiring a sourced answer** before anything is recommended, and no physical action should be taken on the basis of this section as written.

### Q1 — What is the existing receive chain actually doing?

Established from the canonical tree: `etc/systemd/system/rtl-ais.service` runs `rtl_ais -T -P 10108`, feeding Signal K on port 10108 (dedicated, because Signal K owns 10110 — BUG-32).

Open: does this configuration receive **both** AIS channels (161.975 and 162.025 MHz) or only one, and what does `-T` do?

`[UNVERIFIED INFERENCE — source not confirmed]` I do not know what the `-T` flag means and will not guess. This must be read from the rtl_ais documentation or its source before any conclusion is drawn about single- vs dual-channel reception. **This is the cheapest question here and it may turn out to be the whole answer** — a receiver that is only watching one of two channels is missing roughly half the traffic for free, and no hardware purchase would be needed to fix it.

### Q2 — What antenna is on it, and how high?

Antenna height above the waterline is the dominant term in VHF line-of-sight. A receiver upgrade cannot beat an antenna that is mounted too low.

Open, and **requires an on-boat measurement** (add to OPERATOR / ON-BOAT TASKS at the next visit — pairs with the D16 bow-camera height measurement already pending):
- Height of the AIS antenna above the waterline
- Antenna type, and whether it is AIS-specific or a general VHF antenna
- Dedicated, or shared with the VHF radio through a splitter
- Cable type and run length

### Q3 — Would a dedicated dual-channel AIS receiver measurably beat the SDR *in this installation*?

**Unanswerable until Q1 and Q2 are known.** If the limiting factor is antenna height, cable loss, or a single-channel configuration, a new receiver buys nothing — which is exactly the mistake D21 made in a different direction: reaching for new equipment before measuring the existing chain. Answer Q1 and Q2 first.

### Q4 — Receive-only, or a Class B transceiver?

Being **seen** by other vessels is plausibly a larger safety gain than seeing further, and it speaks to the gap recorded in D20 — COLREGs Rule 7(c) treats AIS-only traffic data as "scanty information," and the reference vessel is currently invisible to other AIS-equipped traffic.

⛔ **If a transmitting transceiver is ever fitted, the SH-15 hard gate stops being a pending task and becomes critical.**

SH-15 requires an explicit `transmitPGNs` whitelist on the Signal K canboat-js provider. Today that gate protects against synthetic AIS reaching the boat's own N2K bus. With a transceiver fitted, it is the **only** thing standing between synthetic targets — SafeHelm classifications, WiBoat's 998xxxxxx virtual MMSIs (PART 19 WB-10), D11 camera detections — and being **broadcast to other vessels as real AIS traffic.**

**Transmitting a phantom target to other vessels is a materially worse defect than displaying one on our own screen.** It would put false contacts on someone else's chartplotter. **SH-15 must be closed before any transceiver is connected**, and that ordering is not negotiable on schedule grounds.

### Q5 — Regulatory

MMSI registration and any licensing required for a transmitting unit in Canadian waters. **Operator/legal question — not an AI one.** Nothing asserted.

### Relationship to §13.5 and D20

Unlike D21, this is a genuine sensor addition, so under the S160 §13.5 principle — *alert authority must be proportional to sensor coverage* — it is the kind of change that could justify stronger alerting. Two caveats:

1. A better AIS receiver still cannot see vessels that transmit nothing: most small craft, tenders, kayaks, swimmers, debris. **Radar (D20) remains the larger gap.**
2. Any future request to make SafeHelm more assertive must still be answered with "what sensor was added?" — D22 is a legitimate answer to that question in a way D21 was not, but it is a partial one.

**What would trigger moving to PROJECT_CHECKLIST.md as a build task:**
- Q1 answered from documentation (desk research, no boat needed)
- Q2 measured on the boat
- Q3 answerable, and the answer is "yes, measurably"
- If Q4 goes toward a transceiver: **SH-15 closed first**

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
| 12c | Unclean-shutdown hardening (D14) — read-only charts only | Low (1 mount change) | None | Protects 1.4 GB of charts |
| 13 | pypilot integration | Very High | SafeHelm Phase 2 sea trial | Automation |
| 14 | Unclean-shutdown hardening (D14) — full self-healing audit | High | An actual corruption event being captured | Unproven — no corruption ever observed |
| 15 | Universal device health framework (D15, ex BUG-11) | High | **BUG-50 fixed first** — it is the reference implementation | Owner can tell if their AIS/GPS/mic/speaker works |
| 16 | **3D Surround Situational Awareness (D16)** | Medium (~6–10h) | Don chooses display mode (bird's eye vs. 3D perspective) | Tesla-style helm view; pairs with D11 + WiBoat |
| ~~17~~ | ~~Extended AIS internet overlay (D21)~~ | — | — | ⛔ **NOT APPROVED S161** — declined by operator. Zero coverage gain offshore |
| 17 | **AIS receive chain — receiver + antenna height (D22)** | Q1 desk research: Low. Q3 onward: unknown | Q1 (rtl_ais channel config) → Q2 (on-boat antenna measurement) → Q3. **Q4 transceiver requires SH-15 closed first** | The real sensor upgrade — extends coverage with no internet. Q1 may be free |

---

*This document is maintained by Claude Code. When an item is approved for build, create a task breakdown in PROJECT_CHECKLIST.md and mark that item as promoted here.*
*Do not delete entries — update status or mark PROMOTED.*
