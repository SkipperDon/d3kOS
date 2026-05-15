# SafeHelm: Master System Specification
## d3kOS Collision Avoidance Module

**Document:** `SAFEHELM_SYSTEM_SPEC.md`  
**Version:** 1.0  
**Date:** 2026-05-11  
**Status:** Approved for Development  
**Repository:** `github.com/SkipperDon/d3kOS`  
**Module Path:** `d3kOS/services/safehelm/`  
**Target Platform:** Raspberry Pi 5 · d3kOS v0.9.9+  
**Integration Stack:** Signal K → AvNav → pypilot · Helm Voice (ai_bridge)

---

## 1. Purpose and Scope

SafeHelm is a COLREGs-aware collision avoidance and decision support module for the d3kOS open-source marine operating system. It transforms d3kOS from a passive monitor into an active maritime safety layer — taking sensor data from AIS, Forward Watch (camera), GPS, and IMU and turning it into real-time situational awareness, voice advisories, and — in later phases — autopilot guidance via pypilot.

**What SafeHelm is:** a modular, explainable, safety-first collision avoidance system designed for solo sailors and coastal cruisers running on a Raspberry Pi 5.

**What SafeHelm is not:** a certified navigation system. It is an advisory and decision-support tool. The captain remains responsible for all navigational decisions.

### 1.1 Why It Matters

Research from EMSA (2025) indicates 78.8% of EU marine casualties involved the human element. Collision is the leading cause of ship-related fatalities. Commercial systems providing this capability (Raymarine, Furuno ARPA) cost thousands of dollars. No production-ready, COLREGs-compliant collision avoidance module exists as open source today.

SafeHelm fills that gap on a $150 hardware budget.

### 1.2 Why It Fits d3kOS

d3kOS already has:
- **Forward Watch** — computer vision vessel detection (camera layer)
- **Signal K integration** — AIS, GPS, NMEA normalisation (data layer)
- **Helm voice assistant** — audio output via ai_bridge (voice layer)
- **AvNav** — chart display and navigation UI (display layer)
- **pypilot** — autopilot control (actuation layer)

SafeHelm is the **reasoning layer** that connects these existing components into a cohesive safety loop.

---

## 2. Research Foundation and Gaps Addressed

The academic research on maritime collision avoidance (EMSA 2025, Wróbel et al. 2022, JMSE 2022/2024, arXiv 2025) is sound in theory but fails in six critical ways when applied to real deployment. SafeHelm explicitly addresses each gap.

| Research Gap | SafeHelm Solution |
|---|---|
| Assumes sensors always work | Sensor Reliability Layer with confidence decay and 6 degraded operating modes |
| No real-time guarantees | Deterministic 100ms execution loop with watchdog timers |
| Treats boats as point masses | Vessel Dynamics Model: turn radius, stopping distance, prop walk, drift |
| Ignores human factors | Alarm Budget System (max 6 warnings/hour), 2-minute silence window, one-tap confirm |
| Single-vessel focus only | Conflict Graph with priority assignment and deadlock resolution |
| Non-compliant vessels assumed away | Compliance Tracker with Defensive Navigation Mode |
| No safety envelope | Control Barrier Functions separating planner from hard constraints |
| Deployment path undefined | Pi 5 + Signal K + AvNav + pypilot, systemd service, AvNav JS widget |

### 2.1 Technology Readiness Context

| Capability | TRL (2026) | SafeHelm Target |
|---|---|---|
| Heading-hold autopilot | TRL 9 | Already in d3kOS via pypilot |
| Waypoint following | TRL 8 | Already in d3kOS via AvNav |
| Obstacle detection (AIS) | TRL 7 | Phase 1 output |
| Single-vessel COLREGs CA | TRL 5 | Phase 2 output |
| Multi-vessel COLREGs CA | TRL 3 | Phase 3 output |
| Certified / deployable CA | TRL 1 | Phase 5 aspiration |

---

## 3. System Architecture: 7-Layer Stack

SafeHelm is a layered system. Data flows upward through the layers (raw sensor → decision). Commands flow downward (decision → actuator). Each layer has exactly one job and communicates with its neighbours only through defined interfaces.

```
┌──────────────────────────────────────────────────────────┐
│  LAYER 7: SAFETY ENVELOPE                                 │
│  Control Barrier Functions · hard constraints · veto      │
├──────────────────────────────────────────────────────────┤
│  LAYER 6: HUMAN INTERFACE                                 │
│  AvNav widget · voice alerts · one-tap · alarm budget     │
├──────────────────────────────────────────────────────────┤
│  LAYER 5: MULTI-VESSEL CONFLICT SOLVER                    │
│  Priority graph · deadlock resolver · defensive mode      │
├──────────────────────────────────────────────────────────┤
│  LAYER 4: COLREGs DECISION ENGINE                         │
│  Situation classifier · give-way/stand-on · escape hdg    │
├──────────────────────────────────────────────────────────┤
│  LAYER 3: VESSEL DYNAMICS MODEL                           │
│  Turn radius · stopping dist · drift · prop walk          │
├──────────────────────────────────────────────────────────┤
│  LAYER 2: REAL-TIME EXECUTION CORE                        │
│  100ms deterministic loop · thread isolation · watchdog   │
├──────────────────────────────────────────────────────────┤
│  LAYER 1: SENSOR FUSION & RELIABILITY                     │
│  AIS + Camera + GPS + IMU · confidence scoring · modes    │
└──────────────────────────────────────────────────────────┘
        ↑                                    ↓
  Signal K (AIS, GPS)          pypilot port 23322
  Forward Watch (camera)       AvNav TCP NMEA / JS widget
  GPS/IMU                      Helm voice (ai_bridge :3002)
```

### 3.1 Data Flow End-to-End

```
Forward Watch (camera, :8084)
        │ direct queue — no network hop
        ▼
SafeHelm Core (Python daemon, :8095)
        │ reads AIS + own nav        │ writes virtual vessels + alerts
        ▼                            ▼
Signal K (:3000)              Signal K (:3000)
        │                            │
   AIS from NMEA              virtual AIS targets
        │                            ▼
        └──────────────────► AvNav renders AIS triangles
                                     │
                            AvNav JS widget polls
                            /safehelm/status → overlay
                                     │
                            Captain taps [EXECUTE]
                                     ▼
                            POST /safehelm/execute
                                     ▼
                            SafeHelm → pypilot :23322
                                     ▼
                               Rudder moves

Voice path:
SafeHelm → POST ai_bridge :3002 /webhook/alert
        → Helm TTS engine → speaker
```

---

## 4. File Structure

```
d3kOS/services/safehelm/
├── safehelm.py                 Main entry point, Flask app + daemon init
├── core/
│   ├── loop.py                 SafeHelmCore: 100ms deterministic thread
│   ├── sensor_hub.py           SensorConfidenceTracker, input queues
│   ├── dynamics.py             VesselDynamics: turn/stop physics
│   └── envelope.py             SafetyEnvelope, barrier function
├── engine/
│   ├── cpa.py                  CPA / TCPA calculations
│   ├── colregs.py              COLREGs encounter classifier
│   ├── conflict.py             ConflictGraph, multi-vessel solver
│   └── compliance.py           Non-compliant vessel detection
├── interface/
│   ├── signalk_reader.py       Signal K WebSocket subscriber
│   ├── virtual_ais.py          Inject camera targets into Signal K
│   ├── pypilot_client.py       pypilot TCP command interface
│   └── voice.py                Alert generation → ai_bridge
├── ui/
│   └── safehelm-widget.js      AvNav overlay widget
├── tests/
│   ├── test_cpa.py
│   ├── test_colregs.py
│   ├── test_conflict.py
│   └── replay_tool.py          AIS capture file replay tester
├── safehelm-config.json        Vessel dynamics, thresholds, preferences
├── safehelm.service            systemd unit for Pi autostart
└── README.md
```

### 4.1 systemd Service

```ini
[Unit]
Description=d3kOS SafeHelm Collision Avoidance Service
After=network.target d3kos-signalk.service
Requires=d3kos-signalk.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/safehelm
ExecStart=/opt/d3kos/venv/bin/python safehelm.py
Restart=on-failure
RestartSec=5
KillMode=process

[Install]
WantedBy=multi-user.target
```

---

## 5. Layer Specifications

### 5.1 Layer 1 — Sensor Fusion and Reliability

Every data input receives a continuous confidence score (0.0–1.0) that decays when data is stale and recovers when fresh data arrives.

**Decay rates (per second):**

| Sensor | Decay Rate | Rationale |
|---|---|---|
| AIS | 0.05 | Updates every ~10s at close range |
| Camera | 0.20 | Must be near-real-time |
| GPS | 0.02 | Generally reliable |
| IMU | 0.10 | Drift is slow but real |

**Stale threshold:** confidence < 0.3 = sensor considered unreliable.

**Operating Modes:**

| Mode | Active Sensors | Capability | Operator Alert |
|---|---|---|---|
| FULL | AIS + Camera + GPS + IMU | All targets visible | None |
| AIS_ONLY | AIS + GPS | AIS targets only, dark vessels invisible | Yellow banner |
| CAMERA_ONLY | Camera + GPS | Visual targets, estimated range | Yellow banner |
| GPS_ONLY | GPS | Own position only, no target tracking | Red banner + audio |
| DEGRADED | Partial GPS | Limited accuracy, advisory only | Red banner + audio |
| BLIND | None reliable | Emergency: disengage autopilot | Critical alarm |

Mode is determined automatically each cycle. Mode changes are logged and announced via voice.

**Camera-to-World Transform** requires: camera field of view, mounting angle, own position, own heading, target pixel coordinates, and estimated range. The range estimation problem (single monocular camera on a moving hull) is the hardest unsolved technical problem in this system. Until radar or stereo range is available, camera targets produce bearing only and cannot feed CPA/TCPA math — they trigger directional alerts only.

**AIS-Camera Target Association:** targets within 15° bearing and estimated at similar range are fused into a single track. Ambiguous associations remain as separate tracks. All tracks expire after 60 seconds without update.

**Virtual MMSI Management:** camera targets use MMSI range 999000001–999000099. Targets are expired from Signal K after 90 seconds without update to prevent ghost vessels on the chart.

### 5.2 Layer 2 — Real-Time Execution Core

SafeHelm runs a fixed-frequency update loop at 10 Hz (100ms period). The watchdog logs any cycle that exceeds 90ms. The loop never blocks on I/O — all network calls are non-blocking with short timeouts.

**100ms cycle budget:**

| Time | Action |
|---|---|
| T+0ms | Read all sensor queues (non-blocking, latest value) |
| T+5ms | Update confidence scores |
| T+10ms | Fuse AIS + Camera targets into unified target list |
| T+15ms | Run CPA/TCPA for all active targets |
| T+30ms | Run COLREGs classifier for risk targets |
| T+45ms | Run Conflict Graph solver if >1 risk target |
| T+60ms | Evaluate Safety Envelope constraints |
| T+70ms | Determine action (None / Advisory / Autopilot) |
| T+80ms | Push to output queues |
| T+100ms | Cycle complete |

**Four isolated threads, communicating only through thread-safe queues:**

| Thread | Job | Period |
|---|---|---|
| `SafeHelmCore` | Main decision loop | 100ms |
| `AISReader` | Signal K WebSocket, pushes to queue | Event-driven |
| `CameraFeeder` | Forward Watch output, pushes to queue | 200ms |
| `OutputBus` | Reads action queue, dispatches to AvNav/pypilot/voice | Event-driven |

### 5.3 Layer 3 — Vessel Dynamics Model

Configured once per vessel in `safehelm-config.json`. Defaults for a 35–40ft sailing vessel with single inboard diesel.

**Key parameters:**

| Parameter | Default | Description |
|---|---|---|
| `loa_meters` | 11.0 | Length Overall |
| `min_turn_radius_nm` | 0.05 | At full rudder, full speed |
| `stopping_dist_nm` | 0.08 | Crash stop distance |
| `max_turn_rate_deg_s` | 3.0 | Degrees per second |
| `prop_walk_dir` | -1 (port) | Single-screw prop walk direction |
| `windage_factor` | 0.15 | Leeway as fraction of wind speed |

All recommended headings are validated against dynamics before presentation. A heading that cannot physically be reached before TCPA is never recommended.

### 5.4 Layer 4 — COLREGs Decision Engine

**CPA/TCPA** is the core risk metric. Distance alone is meaningless — a vessel 5 miles away on a collision course is more dangerous than one 500 feet away passing astern.

**Encounter Classification (Rules 13–17):**

| Relative Bearing | Target Relative Heading | Encounter | Own Role |
|---|---|---|---|
| 112.5°–247.5° | Any | Overtaking (Rule 13) | Give-way |
| ≤15° or ≥345° | 165°–195° | Head-on (Rule 14) | Both turn starboard |
| 5°–112.5° | Any | Crossing, target starboard (Rule 15) | Give-way |
| 247.5°–355° | Any | Crossing, target port (Rule 15) | Stand-on |

**Known limitations of the classifier (Phase 1–2 scope):**
- Rule 12 (two sailing vessels, tack/leeward logic) requires wind angle — not implemented in Phase 1
- Rule 18 (vessel type hierarchy: RAM, NUC, fishing) requires AIS vessel-type parsing — Phase 2
- Rule 19 (restricted visibility) requires fog/night detection — Phase 2

**Risk Levels:**

| Level | Condition |
|---|---|
| CLEAR | TCPA < 0 (past) or CPA > domain |
| MONITOR | CPA < domain, TCPA > 10 min |
| WARNING | CPA < domain, TCPA 5–10 min |
| CRITICAL | CPA < domain, TCPA < 5 min |

**Escape Heading Algorithm:** sweep candidate headings in 5° steps (starboard preference) to find the nearest COLREGs-compliant course that clears all threats and is achievable given vessel dynamics. Returns `None` if no heading solves all conflicts (triggers emergency advisory).

### 5.5 Layer 5 — Multi-Vessel Conflict Solver

When more than one threat is active, a Conflict Graph finds a single heading that clears all of them. Priority assignment rules:

1. CRITICAL before WARNING
2. Give-way obligation before stand-on
3. Closest TCPA breaks ties
4. Starboard-side vessels get higher attention priority

**Deadlock Resolution:** when no heading simultaneously clears all conflicts, the system recommends a speed reduction. Slowing from 6 to 2 knots often resolves crossing geometry. If neither heading change nor speed reduction resolves within safety margin, CRITICAL alarm fires and autopilot is disengaged.

**Non-Compliant Vessel Detection:** a give-way vessel that has not altered course by >10° within 60 seconds when TCPA < 5 minutes is flagged as non-compliant. Response:

1. Defensive Mode activated — stand-on duty suspended, own evasive action planned (Rule 17(a)(ii))
2. Ship domain expanded 2× for that target
3. CRITICAL threshold tightened: fires at TCPA < 8 min instead of 5
4. Audit log entry with full sensor snapshot

### 5.6 Layer 6 — Human Interface

**Alarm Budget** prevents fatigue:

| Alarm Level | Max Per Hour | Notes |
|---|---|---|
| CRITICAL | Unlimited | Never suppressed |
| WARNING | 6 | Throttled after limit |
| ADVISORY | 20 | Throttled after limit |

**Voice Alert Format:**  
`[Direction] vessel, bearing [NNN]. [Role phrase]. [Action phrase].`

Examples:
- *"Starboard vessel, bearing zero four five. We are give-way. Recommend turn to two seven zero."*
- *"Head-on. Both vessels must turn starboard. Recommend zero nine zero."*
- *"CRITICAL. Collision course. No clear heading found. Manual override required."*

CRITICAL alerts bypass the Helm mute state and call `espeak-ng` directly — a muted Helm should not silence collision alarms.

**AvNav Widget States:**

- **CLEAR** — small green dot, no text
- **WARNING** — yellow banner: `⚠ Vessel SW 225° — Give-way — Suggest 090°  [ACK] [EXECUTE]`
- **CRITICAL** — full-width pulsing red: `🚨 COLLISION RISK — Bearing 045° — TCPA 4min — [EXECUTE NOW] [TAKE HELM]`

`[TAKE HELM]` disengages SafeHelm autopilot control and silences alarms for 2 minutes. After 2 minutes, if the threat is still active, the alarm re-fires. The 2-minute window is the maximum.

### 5.7 Layer 7 — Safety Envelope

The Safety Envelope is mathematically separate from the planning layers. It vetoes unsafe actions regardless of what the planner recommends.

**Hard Constraints (never violated):**

| Constraint | Default Value |
|---|---|
| Minimum depth before manoeuvre | 3.0 m |
| Maximum rudder rate | 50%/s |
| Sailing no-go zone | 40° apparent wind |
| Maximum heel | 30° |

**Control Barrier Function:** verifies that enough time remains to execute a full 180° turn with margin before TCPA. If `barrier_function()` returns negative (insufficient turn time remaining), Emergency Mode engages:

1. Immediate full starboard rudder command to pypilot (COLREGs preference)
2. Critical voice alert
3. Full sensor snapshot logged for post-incident review
4. Autonomous control locked out until captain acknowledges

---

## 6. External Integrations

### 6.1 Signal K (Data In)

WebSocket subscription to `vessels.*` for: `navigation.position`, `speedOverGround`, `courseOverGroundTrue`, `headingTrue`, `sensors.ais.class`. All data normalised before entering sensor queues.

### 6.2 Virtual AIS Injection (AvNav Display)

Camera-detected targets are injected as Signal K vessels via PUT to `vessels/urn:mrn:d3k:visual:{id}`. AvNav renders them as standard AIS triangles. AvNav's own CPA alarm also fires on these targets — providing a second independent safety layer over the same risk.

### 6.3 pypilot (Autopilot Commands Out)

Direct TCP to pypilot port 23322. Commands are JSON: `{"ap.heading_command": [radians]}`. pypilot must be in compass mode before heading commands are sent. All commands are conditional on Safety Envelope validation passing. Timeout: 80ms — never blocks the safety loop.

### 6.4 Helm Voice (ai_bridge)

All voice alerts route through `POST http://localhost:3002/webhook/alert` with `severity` field. CRITICAL severity bypasses ai_bridge and calls `espeak-ng` directly to be immune to Helm mute state.

---

## 7. Configuration Reference

`safehelm-config.json` — configured once per vessel installation.

```json
{
  "vessel": {
    "loa_meters": 11.0,
    "beam_meters": 3.7,
    "max_speed_kts": 8.0,
    "cruise_speed_kts": 6.0,
    "min_turn_radius_nm": 0.05,
    "stopping_dist_nm": 0.08,
    "max_turn_rate_deg_s": 3.0,
    "prop_walk_dir": -1,
    "windage_factor": 0.15,
    "vessel_type": "sailing"
  },
  "safety": {
    "ship_domain_nm": 0.25,
    "critical_tcpa_sec": 300,
    "warning_tcpa_sec": 600,
    "min_depth_m": 3.0,
    "no_go_zone_deg": 40.0,
    "max_heel_deg": 30.0
  },
  "alarm_budget": {
    "max_warnings_per_hour": 6,
    "max_advisories_per_hour": 20
  },
  "camera": {
    "hfov_deg": 84.0,
    "pan_offset_deg": 0.0,
    "tilt_offset_deg": -5.0
  },
  "ports": {
    "signalk_ws": "ws://localhost:3000/signalk/v1/stream",
    "signalk_api": "http://localhost:3000/signalk/v1/api",
    "pypilot_host": "localhost",
    "pypilot_port": 23322,
    "ai_bridge_url": "http://localhost:3002",
    "safehelm_api_port": 8095,
    "avnav_nmea_port": 10110
  }
}
```

---

## 8. Known Limitations and Open Problems

These are design-level limitations acknowledged in the spec. They do not block Phase 1 or 2 but must be addressed before Phase 4 (autopilot integration).

| # | Limitation | Phase Affected | Notes |
|---|---|---|---|
| L1 | **Monocular range estimation unsolved** | All | Camera gives bearing only. CPA/TCPA requires distance. Camera targets trigger directional alerts only until radar or stereo is available. |
| L2 | **Rule 12 not implemented** | Phase 1–2 | Two sailing vessels — requires wind angle data. Add in Phase 2. |
| L3 | **Rule 18 vessel type hierarchy** | Phase 1 | AIS vessel type parsing needed. RAM/NUC/fishing priority not applied in Phase 1. |
| L4 | **Rule 19 restricted visibility** | Phase 1–2 | Night/fog detection not implemented. System continues applying Rules 13–17 in conditions where they do not apply. |
| L5 | **Night / low-light camera** | All | Camera produces nothing useful at night without IR illumination. Automatic fallback to AIS_ONLY after sunset not yet implemented. |
| L6 | **Depth sounder integration** | Phase 3 | Safety Envelope uses `min_depth_m` but no live depth feed yet connected. |
| L7 | **Startup health check** | Phase 1 | System must validate Signal K connectivity, GPS fix, and AIS reception before reporting operational. |
| L8 | **Incident log format undefined** | Phase 2 | Format, fields, rotation, and review UI needed before sea trials. |
| L9 | **AIS-camera fusion algorithm** | Phase 2 | Association logic for same vessel appearing from both sources needs hardening. |

---

## 9. Testing Strategy

### 9.1 Unit Tests (No Hardware)

Pure Python, synthetic data. Each module independently testable. Target: >80% coverage before Phase 1 completion.

Key test cases:
- Head-on CPA approaches zero correctly
- Crossing give-way produces starboard escape heading
- Non-compliant vessel triggers defensive mode
- Alarm budget throttles warnings correctly
- Barrier function returns negative for insufficient turn time

### 9.2 Scenario Replay Tests

`replay_tool.py` feeds recorded AIS/GPS captures through the full stack and verifies:
- No false positives in open water
- Correct COLREGs classification for standard scenarios
- Escape heading always achievable given vessel dynamics
- Alarm budget respected across a 4-hour voyage replay

### 9.3 Hardware-in-the-Loop (Pi)

On live Pi with pypilot in simulate mode. Acceptance criteria:
- 100ms loop completes within 90ms under full thread load
- Virtual AIS targets appear in AvNav within 500ms of camera detection
- Voice alerts fire within 200ms of risk threshold crossing
- pypilot command round-trip < 150ms
- System correctly enters AIS_ONLY mode when camera confidence drops

### 9.4 Sea Trials (Phase 2 gate before Phase 3)

One full 4-hour passage in Phase 2 advisory-only mode before any autopilot integration is permitted. Acceptance criteria:
- All AIS encounters correctly classified by COLREGs rule
- Zero false CRITICAL alarms
- Voice advisories accurate and non-fatiguing
- Virtual AIS targets for detected visual vessels appear correctly in AvNav

---

## 10. Phased Development Roadmap

SafeHelm is developed in five phases. Each phase must pass its acceptance criteria before the next begins. Phases 1–2 are the validated safety baseline. Phase 4 (autopilot integration) must not proceed without at least one full season of Phase 2 sea time.

---

### Phase 1 — Shadow Mode (Watchstander)
**Duration:** 4 weeks  
**Risk:** Zero — no alarms, no output to helm  
**Objective:** Verify the core math is correct before anyone depends on it.

| Task | Description | Deliverable |
|---|---|---|
| 1.1 | Implement Layers 1–4 (Sensor, Loop, Dynamics, COLREGs) | Python modules in `core/` and `engine/` |
| 1.2 | Signal K WebSocket reader | `signalk_reader.py` |
| 1.3 | CPA/TCPA engine with unit tests | `cpa.py`, `test_cpa.py` |
| 1.4 | COLREGs classifier with unit tests | `colregs.py`, `test_colregs.py` |
| 1.5 | Log-only mode — classifications written to file, no alarms | `safehelm.log` output |
| 1.6 | AIS replay tool | `replay_tool.py` |
| 1.7 | Startup health check | Validates SK/GPS/AIS before reporting operational |
| 1.8 | Unit test coverage >80% | CI passing |

**Phase 1 gate:** Replay of 10 known AIS encounters produces correct COLREGs classification in all 10 cases.

---

### Phase 2 — Advisory Mode (Messenger)
**Duration:** 4 weeks  
**Risk:** Low — informational only, captain decides all actions  
**Objective:** Deliver the full advisory experience. Earns the captain's trust.

| Task | Description | Deliverable |
|---|---|---|
| 2.1 | Layer 6: Alarm Budget System | `alarm_budget.py` |
| 2.2 | Voice alert generation and ai_bridge integration | `voice.py` |
| 2.3 | CRITICAL bypass: direct espeak-ng for mute-immune alerts | `voice.py` |
| 2.4 | Virtual AIS injection for camera-detected targets | `virtual_ais.py` |
| 2.5 | AvNav JS widget: status, EXECUTE, TAKE HELM buttons | `safehelm-widget.js` |
| 2.6 | Flask API: `/status`, `/execute`, `/silence` endpoints | `safehelm.py` |
| 2.7 | Incident log: structured JSON per event | `logs/incidents/` |
| 2.8 | Rule 12 (sailing vessels) and Rule 18 (vessel types) | `colregs.py` update |
| 2.9 | Night mode detection → auto AIS_ONLY after sunset | `sensor_hub.py` |
| 2.10 | 4-hour sea trial in advisory-only mode | Trial report |

**Phase 2 gate:** Sea trial produces zero false CRITICAL alarms. Voice advisories are accurate. AvNav widget functions correctly. Captain endorses advisory quality.

---

### Phase 3 — Multi-Vessel and Conflict Resolution (Navigator)
**Duration:** 3 weeks  
**Risk:** Low — still advisory only  
**Objective:** Handle harbours, shipping lanes, and non-cooperative vessels.

| Task | Description | Deliverable |
|---|---|---|
| 3.1 | Layer 5: Conflict Graph and priority assignment | `conflict.py` |
| 3.2 | Deadlock detection and speed-reduction recommendation | `conflict.py` |
| 3.3 | Non-compliant vessel compliance tracker | `compliance.py` |
| 3.4 | Defensive Navigation Mode (Rule 17(a)(ii)) | `compliance.py`, `colregs.py` |
| 3.5 | Rule 19 restricted visibility mode | `colregs.py` |
| 3.6 | Depth sounder integration via Signal K | `sensor_hub.py` |
| 3.7 | Harbour simulation test: 10+ simultaneous AIS targets | Simulation test report |

**Phase 3 gate:** Simulation with 10 simultaneous AIS targets produces a single consistent escape heading recommendation. Non-compliant vessel test produces defensive mode activation.

---

### Phase 4 — Autopilot Integration (Pilot)
**Duration:** 4 weeks  
**Risk:** High — system physically moves the rudder  
**Prerequisite:** Phase 2 sea trial completed and endorsed. At least one full sailing season in advisory-only mode recommended before Phase 4.

| Task | Description | Deliverable |
|---|---|---|
| 4.1 | Layer 7: Safety Envelope with hard constraints | `envelope.py` |
| 4.2 | Control Barrier Function implementation | `envelope.py` |
| 4.3 | pypilot TCP client: compass mode, heading command, disengage | `pypilot_client.py` |
| 4.4 | Emergency Mode: barrier breach → full starboard rudder + lock | `loop.py` |
| 4.5 | Deadman switch: physical helm input immediately disengages | Hardware + `pypilot_client.py` |
| 4.6 | Human override always wins: verify helm input detection | Integration test |
| 4.7 | AvNav widget: [EXECUTE NOW] activates pypilot command | `safehelm-widget.js` update |
| 4.8 | Controlled open-water autopilot nudge sea trial | Trial report |

**Phase 4 gate:** Controlled sea trial. Autopilot nudge executes correctly in 5 pre-planned scenarios. Human override immediately disengages in all test cases. Zero unintended rudder commands during 2-hour trial.

---

### Phase 5 — Open Source Release and Community Adoption
**Duration:** Ongoing  
**Risk:** None — documentation and packaging only  
**Objective:** Make SafeHelm accessible to the wider OpenPlotter and maritime OSS community.

| Task | Description | Deliverable |
|---|---|---|
| 5.1 | README with step-by-step install instructions | `README.md` |
| 5.2 | Example configs for common vessel types | `config-examples/` |
| 5.3 | Signal K plugin manifest for App Store listing | `package.json` |
| 5.4 | OpenPlotter compatibility verification | Compatibility matrix |
| 5.5 | Community documentation site | docs page on d3kOS site |

---

## 11. Summary Comparison: Research vs SafeHelm

| Dimension | Research Papers (2026) | SafeHelm Design |
|---|---|---|
| Sensor failure | Ignored | 6 explicit degraded modes, confidence decay |
| Real-time budget | Never addressed | 100ms deterministic loop with watchdog |
| Vessel physics | Point masses | Turn radius, stopping distance, prop walk, drift |
| Human factors | Absent | Alarm budget, one-tap confirm, 2-min silence |
| Multi-vessel | Mostly single-target | Conflict graph with deadlock resolution |
| Non-compliant vessels | Assumed cooperative | Compliance tracker, defensive mode |
| Safety layer | None | CBF barrier function, hard constraints |
| Deployment target | Server/simulation | Pi 5, Signal K, AvNav, pypilot |
| Explainability | Black box | Named COLREGs rule cited per decision |
| Cost | Not discussed | ~$150 (Pi 5 + HDR camera) |

**The research describes what to build. This document describes how to build it, what happens when sensors fail, when vessels misbehave, and when the real world fails to cooperate.**

---

## 12. Honest Assessment

**Phase 1 and 2 are worth building now.** The advisory layer — CPA/TCPA on AIS targets, voice alerts, virtual AIS injection for camera-detected vessels, the AvNav widget — is 6–8 weeks of focused work at zero additional hardware cost. No open-source tool does this on a Pi today. The gap is real.

**Phase 4 requires caution.** A recommendation the captain can ignore is safe by definition. A command that physically turns the boat is only safe if every failure mode has been tested in the real world. The Control Barrier Function, the compliance tracker, the deadlock resolver — these are architecturally correct but untested at sea. Do not proceed to Phase 4 without a full season of Phase 2 sea time.

The best collision avoidance system for a solo sailor is not one that turns the boat. It is one that wakes the captain up with the right information at the right time so they can turn the boat themselves. **That system is Phase 2. That system is achievable. That system does not exist as open source today.**

---

*SafeHelm Master System Specification v1.0 — 2026-05-11*  
*d3kOS — github.com/SkipperDon/d3kOS*  
*AtMyBoat.com*
