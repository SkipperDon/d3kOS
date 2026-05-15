# WiBoat + SafeHelm + Communications
## Functional Requirements Document

**Document:** `WIBOAT_SAFEHELM_FRD_v1.2.md`
**Version:** 1.2
**Date:** 2026-05-15
**Status:** Draft — Approved for Development Planning
**Author:** Skipper Don | AtMyBoat.com
**Project:** d3kOS Marine Safety Extension — WiBoat + SafeHelm
**Classification:** Internal Engineering

---

## Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-05-15 | Skipper Don / Claude Code | Initial FRD — derived from architecture, business case, NFR, and SafeHelm spec |
| 1.1 | 2026-05-15 | Skipper Don / Claude Code | Dual-network config confirmed (on-boat 10.42.0.2 / LAN 192.168.1.x); 4-antenna hardware baselined to Phase 1 with SP4T RF switch; G2 resolved; G3 resolved by design; FR-WB-021/022/024 updated to reflect P2 delivery on 4-antenna bearing |
| 1.2 | 2026-05-15 | Skipper Don / Claude Code | Resolved 12 specification gaps: CSI throughput channel definition (Issue 1); range confidence discard hysteresis (Issue 2); heading freshness timeout and COG fallback hierarchy (Issue 3); IMU-unavailable degraded clutter mode (Issue 4); PIW override path bypassing display thresholds (Issue 5); Kalman stability numeric thresholds (Issue 6); CPA/TCPA mathematical model and polar-to-Cartesian conversion (Issue 7); alarm budget level table (Issue 8); LoRa coordinate encoding format (Issue 9); multistatic batman-adv fusion algorithm (Issue 10); Gemini explanation throttling policy (Issue 11); CBF predictive constraint with vessel dynamics and captain override rules (Issue 12) |

---

## Phase Reference Key

Every functional requirement carries a phase tag indicating when it must be delivered.

| Tag | Phase | Scope |
|---|---|---|
| [P1] | Phase 1 — Foundation | Basic range detection, shadow mode, no alarms, no autopilot |
| [P2] | Phase 2 — Advisory | Bearing + classification, voice advisories, sea trial |
| [P3] | Phase 3 — Multi-vessel | 360° coverage validation, conflict solver, batman-adv mesh (4-antenna hardware installed Phase 1; bearing software Phase 2) |
| [P4] | Phase 4 — Autopilot | Single-box consolidation, pypilot integration |
| [ALL] | All phases | Required from Phase 1 onward |

---

## Table of Contents

1. Executive Summary
2. System Overview and Scope
3. User Roles and Personas
4. Architectural Overview
5. Functional Requirements — WiBoat Subsystem
6. Functional Requirements — SafeHelm Subsystem
7. COLREGs Advisory Specification
8. Functional Requirements — Communications Layer
9. Functional Requirements — AI Quality Layer
10. Functional Requirements — d3kOS Integration
11. Functional Requirements — Signal K Plugin (Standalone Compatibility)
12. Functional Requirements — Data Logging and User Management
13. Functional Requirements — Display and UI
14. Phase Applicability Matrix
15. Out of Scope
16. Dependencies and Constraints
17. Known Gaps and Open Questions
18. Glossary

---

## 1. Executive Summary

WiBoat + SafeHelm is an open-source marine collision avoidance system that fuses WiFi Channel State Information (CSI) radar, forward-facing camera, LoRa mesh radio, and AIS into a single safety layer integrated with the d3kOS marine operating system running on a Raspberry Pi.

The system solves four hazard categories invisible to conventional marine instruments:

- **Deadheads** (submerged or semi-submerged logs) — no radar return at low freeboard; no AIS
- **Persons in water** — near-zero radar cross-section; camera fails at night or in fog
- **Ice floes** — irregular shape, poor radar return; no AIS
- **Small unpowered craft** — kayaks, paddleboards, rowing shells — no electronics

The system is designed around two interlocking principles:

1. **Layered sensing** — no single sensor is sufficient; confidence is a composite score from all available sensors, dynamically re-weighted by conditions
2. **Explainable advice** — every advisory can be attributed to a COLREGs rule, a confidence score, and a sensor source; the captain remains in command at all times

This document specifies all functional requirements for the WiBoat processor, SafeHelm collision avoidance engine, LoRa communications layer, AI quality assessment layer, d3kOS integration, Signal K standalone compatibility, data logging, and display.

---

## 2. System Overview and Scope

### 2.1 System Name

**WiBoat + SafeHelm** — WiFi CSI Marine Object Detection and COLREGs Collision Avoidance System
Companion module to **d3kOS** v0.9.9+

### 2.2 Purpose

Transform d3kOS from a passive navigation monitor into an active, multi-sensor collision avoidance system capable of detecting, classifying, and advising on non-AIS marine hazards in all visibility conditions.

### 2.3 System Boundaries

**In scope:**

- WiFi CSI signal capture, range estimation, bearing estimation, and object classification
- Multi-sensor fusion (WiFi CSI + camera + AIS + GPS + IMU + LoRa)
- COLREGs-aware encounter classification and advisory generation
- Voice advisory delivery via d3kOS Helm voice (ai_bridge)
- Helm AI query interface (natural language queries about contacts)
- LoRa/Meshtastic cooperative hazard sharing (5–15 km)
- 5 GHz batman-adv cooperative multistatic mesh (0–500 m, Phase 3)
- Display integration via AvNav overlay widget and Signal K virtual AIS targets
- AI quality assessment layer (TFLite edge model + Gemini explanation + post-voyage optimization)
- d3kOS boat log integration for contact, advisory, and sensor performance events
- User log management (view, export, delete)
- Signal K plugin for standalone compatibility (OpenPlotter, bare Signal K)
- Autopilot integration via pypilot (Phase 4 only, after sea trial calendar gate)

**Out of scope:**

- Commercial AIS transponder replacement (WiBoat is advisory only, not a certified navigation system)
- Radar replacement for commercial or regulated vessels
- Certified safety system (SOLAS, COLREG-certified); advisory use only
- Type approval or Transport Canada certification (this is a v1.0 goal, not a v0.x goal)
- d3k-lite / OpenPlotter full feature parity — Signal K plugin provides base compatibility; d3kOS-specific features require d3kOS
- WiBoat as a general-purpose WiFi positioning or indoor sensing system

### 2.4 Target Platform

| Component | Hardware | OS / Kernel |
|---|---|---|
| WiBoat processor | Raspberry Pi 4B (4GB) | Raspberry Pi OS Bullseye 32-bit, kernel 5.10 LOCKED |
| SafeHelm / d3kOS | Raspberry Pi 5 (existing d3kOS boat Pi) | Raspberry Pi OS, non-16k kernel |
| Phase 4 consolidation | Raspberry Pi 5 | Non-16k kernel, both subsystems on one box |

### 2.5 Regulatory Context

- 2.4 GHz ISM band operation (no licence required, Canada ISED RSS-210)
- Maximum EIRP: 4W (36 dBm) — target configuration is approximately 2.5W EIRP (within limits)
- WiBoat is an advisory tool. The captain bears all navigational responsibility.
- COLREGs advisories are recommendations, not commands, except when autopilot is actively engaged (Phase 4) and the captain has explicitly activated autopilot response.

---

## 3. User Roles and Personas

### 3.1 Role: Captain (Primary Operator)

The person at the helm. May be solo. Interacts with WiBoat + SafeHelm via:
- Voice (receives advisories; queries Helm AI)
- AvNav display (sees contacts, widget, alerts)
- Physical helm (overrides any autopilot command at all times)

**System obligations to the Captain:**
- Never issue more than 6 actionable warnings per hour (alarm budget)
- Always explain the basis for any advisory (rule number, sensor, confidence)
- Always allow the captain to dismiss or override any advisory without additional confirmation steps
- Maintain full function without internet connectivity

### 3.2 Role: Builder / System Administrator

The person who assembles, installs, and configures the system. Interacts via:
- d3kOS Settings UI
- SSH / systemd (during setup only)
- Configuration files

**System obligations to the Builder:**
- All services start on boot without manual intervention after initial setup
- Health API endpoint available for diagnostics
- All configuration in a single JSON file per subsystem

### 3.3 Role: Fleet Member (Cooperative Mesh)

Any vessel within LoRa range (5–15 km) or 5 GHz mesh range (0–500 m) that is running Meshtastic or a compatible WiBoat node. Receives anonymized hazard alerts from other equipped vessels. No interaction beyond automatic reception.

### 3.4 Role: OpenPlotter / Generic Signal K User (Phase 1+)

A mariner using OpenPlotter or bare Signal K (not d3kOS). Accesses WiBoat contacts and basic COLREGs proximity alerts via the Signal K plugin. Does not receive d3kOS-specific features (Helm voice, Gemini AI explanation, boat log).

---

## 4. Architectural Overview

### 4.1 Layered Architecture

The system is structured in three layers. Data flows from the hardware upward. The d3kOS extension is additive — the Signal K plugin is the complete base system.

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 3 — d3kOS Extension (RPi 5, d3kOS only)          │
│  Helm voice (ai_bridge :3002)                           │
│  Helm AI query interface                                │
│  d3kOS boat log capture                                 │
│  Gemini AI explanation proxy (:8097)                    │
│  d3kOS Settings UI integration                          │
│  AvNav widget (full featured)                           │
├─────────────────────────────────────────────────────────┤
│  LAYER 2 — Signal K Plugin (any Signal K system)        │
│  SafeHelm COLREGs engine                                │
│  WiBoat contact consumer                               │
│  Virtual AIS target injection                           │
│  Signal K notification alerts                           │
│  Basic proximity alarms                                 │
│  LoRa vessel display                                    │
├─────────────────────────────────────────────────────────┤
│  LAYER 1 — WiBoat Processor (RPi 4B, platform-agnostic) │
│  nexmon_csi extraction                                  │
│  Range / bearing signal processing                      │
│  Object classification (TFLite)                         │
│  Kalman contact tracker                                 │
│  WebSocket contact feed (:8766)                         │
│  Health API (:8767)                                     │
│  Meshtastic LoRa bridge (:8768)                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Two-Box Phase (Phases 1–3)

WiBoat runs on a dedicated RPi 4B (kernel 5.10 locked for nexmon_csi compatibility). SafeHelm runs on the existing d3kOS RPi 5. Connected via dedicated boat Ethernet LAN.

**On-boat network (deployment):** `10.0.0.0/24` subnet. WiBoat RPi 4B hardcoded static IP: `10.42.0.2`. D3kOS RPi 5 on-boat IP: operator-assigned on the boat router (placeholder `10.42.0.1`). All service endpoints in `wiboat-config.json` and `safehelm-config.json` reference `10.x.x.x` for deployed operation.

**LAN / development network:** `192.168.1.0/24` subnet for development, testing, and laptop access. D3kOS RPi 5 LAN address: `192.168.1.237` (existing). WiBoat LAN dev address: DHCP during development. The `WIBOAT_HOST` environment variable overrides the config file value for switching between on-boat and LAN/dev without file edits.

### 4.3 Single-Box Phase (Phase 4)

After Migration Gate 3 bench validation passes, all services consolidate onto a single RPi 5. ALFA adapters and Heltec V3 LoRa connect via USB. Non-16k kernel required on RPi 5 for nexmon_csi.

### 4.4 Sensing Range Summary

| Layer | Technology | Range | What It Detects |
|---|---|---|---|
| Active sensing | WiFi CSI 2.4 GHz | 0–250 m | Non-AIS targets, range + bearing, all weather |
| Visual confirmation | Forward camera (d3kOS Forward Watch) | 0–250 m | Visual bearing, object ID in clear conditions |
| Cooperative sensing | 5 GHz batman-adv mesh | 0–500 m | Multi-vessel cooperative contacts (Phase 3) |
| Registered vessels | AIS via Signal K | 0–50 nm | MMSI, course, speed, vessel type |
| Fleet mesh | LoRa / Meshtastic | 5–15 km | Position of Meshtastic-equipped vessels (Phase 2) |

---

## 5. Functional Requirements — WiBoat Subsystem

### 5.1 CSI Extraction

**FR-WB-001 [P1]** The system shall extract Channel State Information (CSI) from the Raspberry Pi 4B internal BCM43455 WiFi chip using nexmon_csi firmware patch, operating in monitor mode on 2.4 GHz channel 6 (configurable).

**FR-WB-002 [P1]** The system shall output raw CSI packets as UDP datagrams on localhost:5500 at a minimum rate of 100 packets per second per logical antenna channel. Definition of "channel": one physical antenna position in the sequential SP4T switching cycle. With 4-antenna UCA and equal dwell time per position, total nexmon_csi output shall be ≥ 400 pps (100 pps × 4 antenna positions). In Phase 1 single-antenna mode (before SP4T activation), total output shall be ≥ 100 pps. The per-channel rate governs MUSIC input quality; the total rate governs watchdog thresholds (see FR-WB-003).

**FR-WB-003 [P1]** If CSI throughput drops below the degraded threshold for more than 3 consecutive seconds, the system shall set sensor mode to DEGRADED_SENSING and notify the SafeHelm sensor hub. Degraded threshold: Phase 1 (single-antenna): < 80 pps total. Phase 2+ (4-antenna SP4T): < 320 pps total (equivalent to < 80 pps on any single antenna channel). The per-channel floor of 80 pps applies regardless of phase.

**FR-WB-004 [P1]** The nexmon_csi service shall be managed by systemd with `Restart=on-failure`. Recovery from a crash shall complete within 5 seconds without OS reboot.

**FR-WB-005 [P1]** The system shall use a dedicated ALFA AWUS036NH WiFi adapter as the high-power frame injector (TX) on 2.4 GHz. The RPi internal BCM43455 performs CSI extraction (RX). These are separate radio functions on separate hardware.

**FR-WB-006 [P1]** WiFi channel, bandwidth (20 MHz Phase 1, 40 MHz Phase 3+), MAC filter, and UDP output port shall be configurable in `wiboat-config.json` without code changes.

### 5.2 Range Estimation

**FR-WB-010 [P1]** The system shall estimate target range using Inverse Fast Fourier Transform (IFFT) applied to the Time-of-Flight (ToF) component of CSI subcarrier phase data.

**FR-WB-011 [P1]** Range estimation shall operate from a minimum of 5 m to a maximum of 250 m, configurable in `wiboat-config.json`.

**FR-WB-012 [P1]** Range accuracy shall be validated against a known 1 m² aluminium reflector at 10 m, 25 m, and 50 m. Acceptance criterion: ±5 m at 50 m range.

**FR-WB-013 [P1]** Range confidence shall be expressed as a float 0.0–1.0, decaying with weak CSI signal strength. A contact shall not be discarded on a single low-confidence measurement. Discard requires range confidence below 0.30 for **3 or more consecutive processing frames**. On discard: the associated Kalman filter state shall be reset and the track closed. The contact may be re-acquired as a new track if signal recovers. Range confidence below 0.30 applies before classification — a contact that fails this threshold does not proceed to the TFLite classifier and does not increment classification confidence scores. The temporal hysteresis prevents transient multipath nulls from generating spurious track loss events.

**FR-WB-014 [P1]** Range noise floor, minimum detectable range, and maximum reliable range shall be documented in the Phase 1 validation report.

### 5.3 Bearing Estimation

**FR-WB-020 [P2]** The system shall estimate target bearing using the MUSIC (Multiple Signal Classification) algorithm applied to phase differences across the 4-antenna array. The 4-antenna Uniform Circular Array (UCA) hardware is installed in Phase 1; the MUSIC bearing software is activated in Phase 2.

**FR-WB-021 [P2]** Phase 2 (4-antenna UCA, hardware installed Phase 1): bearing shall be estimated with ±15° accuracy at 100 m range using Unitary Root MUSIC on 4 sequentially sampled antenna positions (GPIO-controlled SP4T RF switch on BCM43455). Validated against a GPS-tracked tender. The 4-antenna UCA eliminates port/starboard ambiguity from Phase 2 onward — no forward-looking assumption required.

**FR-WB-022 [P2]** The system shall use Unitary Root MUSIC on the 4-channel UCA (antennas sampled sequentially via SP4T RF switch at BCM43455 input). Bearing accuracy shall be validated at ±15° from all four quadrants (forward, aft, port, starboard). At marine target speeds (≤20 kts / 10 m/s), the 40 ms inter-antenna sampling interval introduces ≤0.4 m target displacement — within the ±15° bearing accuracy budget at ranges ≥ 30 m.

**FR-WB-023 [P2]** Bearing requires own vessel heading resolved via the following fallback hierarchy:

1. **Primary:** `vessels.self.navigation.headingTrue` from Signal K. Fresh if data age ≤ 5 seconds.
2. **Fallback:** `vessels.self.navigation.courseOverGroundTrue` (COG) from Signal K — used only when `headingTrue` is stale (> 5 seconds old) AND own vessel SOG ≥ 1.0 kt. COG is an acceptable heading proxy when making way; it is unreliable at low speed or when stopped.
3. **Degraded:** If neither `headingTrue` nor COG qualifies, `bearing_deg_true` shall be set to null and `bearing_confidence` to 0.0.

A heading source is considered stale after **5 seconds** without a fresh Signal K update. Stale heading shall be logged once per 30-second interval to avoid log flooding. When operating on COG fallback, `bearing_source` in the contact JSON shall be set to `"cog_fallback"` to distinguish from compass heading.

Range-only contacts (`bearing_deg_true = null`) **shall not enter CPA/TCPA computation**. They trigger proximity-by-distance alerts only (per FR-SH-043). This prevents false COLREGs advisories from contacts with no angular position information.

**FR-WB-024 [P2]** Phase 2 shall validate 360° bearing coverage by testing bearing accuracy from all four quadrants (forward, aft, port, starboard). Hardware is installed from Phase 1; this validation is part of the Phase 2 sea trial gate.

### 5.4 Clutter Filtering

**FR-WB-030 [P2]** The system shall apply static background subtraction to remove own-vessel reflections (mast, cabin, railings) from the CSI signal.

**FR-WB-031 [P2]** The system shall apply a bandpass wave frequency filter rejecting oscillations in the 0.1–0.5 Hz range (wave-induced CSI fluctuation). Filter bounds shall be configurable.

**FR-WB-032 [P2]** The system shall implement ego-motion compensation using a two-tier approach based on IMU availability:

**Tier A — Full compensation (IMU available):** Pitch and roll data from the IMU (via Signal K) plus own-vessel speed and COG from GPS are used to de-trend CSI phase shifts caused by own-vessel motion. This is the target operating state.

**Tier B — Degraded compensation (IMU unavailable, G5 not resolved):** When IMU data is absent or stale (> 3 seconds), the system shall operate in `DEGRADED_CLUTTER` mode. Own-vessel speed and COG from GPS provide partial velocity de-trending for forward motion only. Pitch and roll compensation is suspended. The wave frequency bandpass filter (FR-WB-031) remains active as the primary clutter suppressor. The system shall log `IMU_UNAVAILABLE` and set `ego_motion_mode: "gps_only"` in the health API response (FR-WB-062). DEGRADED_CLUTTER mode does not suspend sensing — it reduces clutter discrimination accuracy. This is an acceptable Phase 2 operating state until G5 is resolved.

**FR-WB-033 [P2]** The system shall implement sea clutter discrimination using an LSTM-based spatial-temporal stationarity filter. Waves are temporally stationary (rhythmic oscillation); vessels are spatially mobile (linear vector). This distinction shall reduce false alarm rate to below 30% in Beaufort 4 sea state.

### 5.5 Object Classification

**FR-WB-040 [P2]** The system shall classify each confirmed contact into one of five categories using a TFLite CNN-LSTM model running locally on the Raspberry Pi. Categories: `vessel`, `person_in_water`, `deadhead`, `ice_floe`, `unknown`.

**FR-WB-041 [P2]** Classification shall be performed on-device. No raw CSI data or classification data shall leave the local network during the real-time sensing path.

**FR-WB-042 [P2]** Each classification shall produce a confidence score (0.0–1.0). The composite confidence shall be the minimum of range confidence and bearing confidence.

**FR-WB-043 [P2]** Classification confidence thresholds:
- ≥ 0.70: contact enters COLREGs engine; classification label displayed
- 0.40–0.69: contact displayed with UNCERTAIN marker; does not trigger COLREGs rule
- < 0.40: contact logged but not displayed; contributes to post-voyage training data

**FR-WB-043a [P2] — PIW Override Path (Exception to FR-WB-043):** When the TFLite classifier returns `person_in_water` at **any confidence level**, including below 0.40, the PIW override path activates unconditionally:
- The contact **bypasses** the display confidence threshold — it is displayed with the MOB/PIW symbol regardless of composite_confidence
- The contact **bypasses** the COLREGs entry threshold — it enters the CRITICAL alert path directly
- A CRITICAL voice advisory is issued immediately (FR-SH-060, FR-DK-031)
- The alarm budget exemption applies (FR-SH-061)
- The Gemini confidence breakdown shall include the word "LOW CONFIDENCE PIW DETECTION" when composite_confidence < 0.40, so the captain can make an informed judgment

Rationale: the cost of a false alarm is a brief slow-down. The cost of a suppressed PIW detection is a life. These thresholds must never be applied symmetrically to PIW. A PIW at 0.05 confidence is always worth acting on.

**FR-WB-044 [P2]** For contacts within 40 m, classification confidence of ≥ 0.95 shall be the Phase 5 target. Contacts within 40 m below 0.70 confidence shall trigger a proximity alert regardless of classification.

**FR-WB-045 [P2]** Object signatures used for classification:

| Class | Primary Discriminators |
|---|---|
| `vessel` | High-amplitude stable reflection; 2–15 Hz engine vibration in Doppler; large metal RCS; AIS correlation when available |
| `person_in_water` | Small profile; 0.2–0.5 Hz micro-Doppler (breathing/body sway); near-zero propulsion signature; approximately 1 m² cross-section at 2.4 GHz |
| `deadhead` | Near-stationary; no Doppler shift from propulsion; lossy dielectric (waterlogged wood vs. seawater conductivity contrast); dense point reflection |
| `ice_floe` | Slow uniform drift; diffuse distributed reflection (irregular shape); distinct dielectric constant at 2.4 GHz; no propulsion signature |
| `unknown` | Signature does not match trained classes; confidence score below threshold |

**FR-WB-046 [P3]** The classification model shall be updateable from a post-voyage correction dataset without hardware access. Update process: copy new model file via USB or local network to `/opt/wiboat/models/`; service restart loads new weights.

### 5.6 Contact Tracking

**FR-WB-050 [P1]** The system shall maintain a Kalman filter per active contact, tracking position, velocity (range rate), and heading rate over time.

**FR-WB-051 [P1]** A contact shall be marked `kalman_stable: true` when the Kalman filter has received at least 3 consecutive observations within a 500 ms rolling window that satisfy all of the following numeric consistency thresholds:

| Metric | Threshold | Rationale |
|---|---|---|
| Range variance across 3-frame window | ≤ 15 m² (±3.9 m RMS) | Rejects multipath spikes and target jump artifacts |
| Bearing variance across 3-frame window | ≤ 100 °² (±10° RMS) | Consistent with MUSIC accuracy spec at range ≥ 30 m |
| Time window | All 3 observations within 500 ms | Prevents stale frames from satisfying stability |

"Consistent" means all three observations fall within these bounds simultaneously. A single outlier in any metric resets the convergence counter to zero.

Stability state management:
- `kalman_stable` resets to `false` on contact dropout (5 consecutive missing frames per FR-WB-052); re-acquisition starts a fresh convergence count
- Classification confidence does not affect stability — stability is a geometric tracking property only
- Phase 1: bearing variance threshold applies only once MUSIC is active (Phase 2); in Phase 1 (range-only), only range variance and time window apply

**FR-WB-052 [P1]** A contact that does not appear in 5 consecutive processing frames (500 ms) shall be removed from the active contact list and its track closed.

**FR-WB-053 [P1]** The Kalman filter shall produce a `range_rate_ms` field (closing rate in m/s; negative = approaching) for use in CPA/TCPA approximation.

### 5.7 Contact Output

**FR-WB-060 [P1]** The system shall publish the current contact list as a JSON message on WebSocket endpoint `ws://[WIBOAT_IP]:8766/contacts` at 10 Hz (100 ms update interval).

**FR-WB-061 [P1]** The contact JSON schema shall conform exactly to the WiBoat Contact JSON Format v1.0 defined in `WIBOAT_SAFEHELM_INTEGRATED_ARCHITECTURE.md` §5.1. Schema version shall be included in every message. Any schema change shall increment the schema version and maintain backwards compatibility for one version.

**FR-WB-062 [P1]** The system shall provide an HTTP health and status endpoint at `http://[WIBOAT_IP]:8767/health` returning: service uptime, CSI packet rate, active contact count, current antenna mode, Signal K heading source status, and last error if any.

**FR-WB-063 [P1]** All services shall start on boot via systemd without manual intervention. `wiboat-processor.service` and `wiboat-meshtastic-bridge.service` shall be enabled at installation.

### 5.8 Standalone AvNav Injection (Fallback Mode)

**FR-WB-070 [P1]** When SafeHelm is not reachable on the LAN, the system shall automatically fall back to standalone mode and inject WiBoat contacts directly into AvNav via UDP NMEA 0183 on port 9876 (AvNav listener on RPi 5).

**FR-WB-071 [P1]** In standalone mode, contacts shall be injected as synthetic `!AIVDM` AIS sentences using MMSI range 970000001–970000099.

**FR-WB-072 [P1]** Standalone mode shall display a status banner in AvNav: "WiBoat standalone — SafeHelm offline. Range + bearing only. No COLREGs advisories."

**FR-WB-073 [P1]** The system shall attempt to reconnect to SafeHelm every 30 seconds. On reconnect, standalone mode shall be cancelled and integrated mode resumed. A voice announcement shall be made via ai_bridge if d3kOS is available.

---

## 6. Functional Requirements — SafeHelm Subsystem

SafeHelm is organized as a 7-layer stack per `SAFEHELM_SYSTEM_SPEC.md`. This section specifies functional requirements for each layer and the WiBoat integration additions.

### 6.1 Layer 1 — Sensor Fusion and Reliability

**FR-SH-010 [P1]** Every sensor input shall receive a continuous confidence score (0.0–1.0) that decays when data is stale and recovers when fresh data arrives. Decay rates:

| Sensor | Decay Rate (per second) | Stale Threshold |
|---|---|---|
| AIS | 0.05 | < 0.3 |
| Camera (Forward Watch) | 0.20 | < 0.3 |
| GPS | 0.02 | < 0.3 |
| IMU | 0.10 | < 0.3 |
| WiBoat (WiFi CSI) | 0.10 | < 0.3 |

**FR-SH-011 [P1]** The system shall define and enforce 8 operating modes based on sensor availability:

| Mode | Active Sensors | Operator Alert |
|---|---|---|
| FULL | AIS + WiBoat + Camera + GPS + IMU | None |
| FULL_NO_CAMERA | AIS + WiBoat + GPS + IMU | None |
| AIS_WIBOAT | AIS + WiBoat + GPS | None |
| AIS_ONLY | AIS + GPS | Yellow banner — "WiBoat offline. Non-AIS targets not visible." |
| CAMERA_ONLY | Camera + GPS | Yellow banner — "WiBoat offline. Bearing only for non-AIS targets." |
| GPS_ONLY | GPS | Red banner + audio — "No target tracking. Navigation only." |
| DEGRADED | Partial GPS | Red banner + audio — "Limited accuracy. Proceed with caution." |
| BLIND | None reliable | Critical alarm — "Sensor failure. Disengage autopilot. Navigate by sight." |

**FR-SH-012 [P1]** Mode transitions shall be announced via Helm voice (ai_bridge) when the change affects safety capability (any transition to/from AIS_ONLY, CAMERA_ONLY, GPS_ONLY, DEGRADED, or BLIND).

**FR-SH-013 [P2]** WiBoat contacts shall be consumed via a dedicated `WiBoatReader` thread subscribing to `ws://[WIBOAT_IP]:8766/contacts`. On disconnect: set WIFI_RADAR confidence = 0.0, log mode change, retry every 5 seconds. On reconnect: announce via voice if confidence was 0.0.

**FR-SH-014 [P2]** WiBoat contacts with `kalman_stable: false` shall be displayed with an UNSTABLE marker and shall not trigger COLREGs rule processing until stability is confirmed.

### 6.2 Layer 2 — Real-Time Execution Core

**FR-SH-020 [P1]** The SafeHelm core loop shall execute on a deterministic 100 ms (10 Hz) timer. The loop shall process all sensor inputs, update all contact tracks, evaluate all COLREGs encounters, and dispatch any advisories within the 100 ms window.

**FR-SH-021 [P1]** If a loop iteration exceeds 90 ms execution time, the watchdog shall log an overrun event. If three consecutive overruns occur, the system shall log a PERFORMANCE_DEGRADED event and notify the d3kOS diagnostics system (Fix My Pi).

**FR-SH-022 [P1]** Thread isolation shall prevent any single sensor input failure from blocking the core loop. Each sensor input runs in a separate thread with a queue; the core loop reads from queues, never from blocking I/O.

**FR-SH-023 [P1]** The nexmon_csi driver, Meshtastic serial link, classification pipeline, and advisory generator shall each be monitored by the watchdog. On hang detection, the affected service shall restart within 5 seconds without OS reboot.

### 6.3 Layer 3 — Vessel Dynamics Model

**FR-SH-030 [P2]** The system shall maintain a configurable vessel dynamics model for own vessel, including: turn radius at current speed, stopping distance at current speed, drift rate under wind, and prop walk direction.

**FR-SH-031 [P2]** Own vessel dynamics shall be configurable in `safehelm-config.json` with fields for: vessel type, LOA, displacement, propulsion type, turn radius at 5 kts and 8 kts, stopping distance at 5 kts and 8 kts.

**FR-SH-032 [P2]** The dynamics model shall be used to compute the required lead time for any course or speed change recommendation. A vessel with a 150 m stopping distance shall not receive a "stop" recommendation for a contact at 100 m.

### 6.4 Layer 4 — COLREGs Decision Engine

**FR-SH-040 [P2]** The COLREGs decision engine shall classify every contact with composite confidence ≥ 0.70 into one of the following encounter types: head-on, crossing-give-way, crossing-stand-on, overtaking-give-way, overtaking-stand-on, overtaken-stand-on, constrained-vessel, restricted-visibility, non-AIS-hazard.

**FR-SH-041 [P2]** For each encounter, the engine shall compute:
- Closest Point of Approach (CPA) in metres
- Time to CPA (TCPA) in seconds
- Give-way / stand-on status based on relative bearing and vessel type
- Recommended action: course change (degrees, port or starboard), speed reduction, or no action required

**FR-SH-042 [P2]** CPA/TCPA for WiBoat contacts shall use the following mathematical model:

**Coordinate conversion (polar → Cartesian):**
Own vessel is the Cartesian origin (0, 0). Contact polar coordinates (range_m, bearing_deg_true) are converted to Cartesian (x, y) at each frame:
```
x = range_m × sin(bearing_rad)
y = range_m × cos(bearing_rad)
```

**Relative velocity estimation:**
Own vessel velocity vector (Vx_own, Vy_own) is derived from SOG and COG from Signal K. Contact velocity vector (Vx_c, Vy_c) is estimated from the Cartesian position change across the last 3 stable Kalman frames divided by elapsed time. Relative velocity: (Vx_rel, Vy_rel) = (Vx_c − Vx_own, Vy_c − Vy_own).

**CPA and TCPA:**
Using standard linear CPA algebra on the relative position and relative velocity vectors. TCPA = − (P · V) / |V|² where P is relative position vector and V is relative velocity vector. CPA = |P + V × TCPA|. If TCPA < 0, vessels are already diverging — no action required.

**Bearing confidence guard:** When `bearing_confidence < 0.50`, bearing rate-of-change is unreliable. In this case, CPA/TCPA computation is suspended and proximity-by-distance alert (FR-SH-043) is used instead.

**Range-only contacts:** Contacts with `bearing_deg_true = null` do not enter CPA/TCPA computation. Proximity-by-distance alert only.

**Execution gate:** CPA/TCPA computation runs only when `kalman_stable == true` AND `composite_confidence >= 0.50` AND `bearing_deg_true != null` AND `bearing_confidence >= 0.50`.

**FR-SH-043 [P2]** Proximity alert thresholds (applied when CPA/TCPA not computable):
- Contact within 200 m: WARNING level alert
- Contact within 100 m: CRITICAL level alert

**FR-SH-044 [P2]** AIS vessel type field shall be used to determine COLREGs priority hierarchy (Rule 18): Not Under Command > Restricted in Ability to Manoeuvre > Constrained by Draft > Fishing > Sailing > Power-driven.

**FR-SH-045 [P3]** Rule 19 (restricted visibility) mode shall activate when: Forward Watch camera reports low-confidence conditions, OR operator activates manually. In Rule 19 mode, all vessels are treated as potentially not visible; speed reduction advisory is issued at 1 nm range.

**FR-SH-046 [P3]** Rule 12 (sailing vessels on tack) shall be implemented in Phase 3 when wind angle data is available from NMEA. Port-tack vessel gives way to starboard-tack. Windward vessel gives way when on same tack.

### 6.5 Layer 5 — Multi-Vessel Conflict Solver

**FR-SH-050 [P3]** The system shall construct a conflict graph when two or more simultaneous COLREGs encounters are active. The graph shall assign priority to each encounter and compute a single escape heading that satisfies all active encounters.

**FR-SH-051 [P3]** The conflict solver shall detect deadlock conditions (no single heading satisfies all encounters simultaneously) and escalate to DEFENSIVE mode when deadlock is unresolvable.

**FR-SH-052 [P3]** DEFENSIVE mode shall: reduce speed recommendation, issue an alert to the captain, display all active conflicts on the AvNav widget, and await captain input before issuing further course change recommendations.

**FR-SH-053 [P3]** Non-compliant vessel detection: if a vessel designated as stand-on takes an action inconsistent with its designated rule (changes course toward own vessel instead of maintaining), the system shall flag it as NON_COMPLIANT and switch to defensive navigation for that contact.

**FR-SH-054 [P3]** Acceptance test: conflict solver shall produce a consistent escape heading for a scenario with 10 simultaneous AIS targets in a simulated harbour approach.

### 6.6 Layer 6 — Human Interface

**FR-SH-060 [P2]** All advisories shall be delivered via the d3kOS Helm voice system (POST to ai_bridge :3002/webhook/alert). CRITICAL level alerts shall additionally use direct espeak-ng subprocess call to bypass any mute state.

**FR-SH-061 [P2]** The alarm budget shall not exceed 6 actionable warnings per hour during normal operation. After 6 warnings, the system shall enter QUIET mode for 2 minutes before re-enabling non-critical alerts.

The following table defines which advisory levels increment the alarm budget counter:

| Advisory Level | Increments Budget | Notes |
|---|---|---|
| INFO | No | Situational awareness only — no action required |
| ADVISORY | No | Monitoring only — does not constitute an actionable warning |
| WARNING | **Yes** | Requires action; increments counter |
| HIGH | **Yes** | Requires prompt action; increments counter |
| CRITICAL | No — **Exempt** | Always delivered; never suppressed by QUIET mode |
| SYSTEM | No | Sensor/mode status — not an actionable warning |

**Repeated alert rule:** A repeated alert for the same `contact_id` within the 2-minute dismiss window (FR-SH-064) does not increment the budget counter. The counter increments only on first delivery of a WARNING or HIGH alert for a given contact within the dismiss window. If CPA reduces by more than 20% after dismissal, re-delivery is treated as a new event and increments the counter.

**PIW exemption:** PIW alerts are CRITICAL level — exempt from the budget and never suppressed by QUIET mode.

**FR-SH-062 [P2]** Every advisory shall include:
- What was detected (object type, range, bearing)
- Why it matters (COLREGs rule number, or proximity threshold)
- What to do (recommended action)
- Confidence level (expressed as percentage in voice advisory)

**FR-SH-063 [P2]** The AvNav overlay widget shall provide a one-tap EXECUTE button for any recommended course change. Tapping EXECUTE shall confirm the advisory and, in Phase 4, route the course change to pypilot. In Phases 1–3, EXECUTE is acknowledgement only; the captain steers manually.

**FR-SH-064 [P2]** The captain shall be able to dismiss any advisory with a single tap. Dismissal suppresses re-alerting for the same contact for 2 minutes unless the situation materially changes (CPA reduces by more than 20%).

**FR-SH-065 [P2]** Night mode: a Red-Only display mode shall be available and activated either via the AvNav widget or via Helm voice command. Night mode shall maintain luminance appropriate for scotopic vision; no blue or green wavelengths.

### 6.7 Layer 7 — Safety Envelope

**FR-SH-070 [P4]** Control Barrier Functions (CBF) shall enforce hard constraints on autopilot commands. The CBF shall veto any course command that would bring **predicted future CPA** below the configured minimum safe distance (default: 50 m).

**Predictive evaluation:** CBF operates on future CPA, not instantaneous CPA. For each proposed autopilot command (heading change), the CBF simulates the resulting vessel trajectory using the vessel dynamics model (FR-SH-031) and computes the predicted CPA against all active contacts. The prediction horizon is the greater of: 3 × own vessel stopping distance at current speed, or 2 minutes. If the predicted CPA under the proposed command falls below the safety margin, the command is vetoed and an alternative minimum-deviation heading is computed that satisfies the constraint.

**Vessel dynamics integration:** Turn radius and stopping distance at current speed (from `safehelm-config.json`, FR-SH-031) are used to compute the achievable trajectory. A command that physically cannot be completed within the prediction horizon is treated as a straight-line trajectory at current heading for the inertial segment.

**Captain EXECUTE override:** When the captain taps EXECUTE on an advisory, the recommended heading is permitted even if it would reduce CPA below the configured safety margin, provided the heading does not violate the **absolute hard floor: CPA < 10 m**. The 10 m hard floor is not configurable and cannot be overridden by any software command. Only physical helm input (FR-SH-071) bypasses CBF entirely.

**CBF scope:** CBF applies to autopilot commands only (Phase 4). It does not constrain manual helming. The captain retains full authority at the physical helm at all times.

**FR-SH-071 [P4]** Physical helm input (any change in wheel or tiller position) shall disengage SafeHelm autopilot mode immediately and unconditionally. This is a hardware-level override; it shall not be bypassable in software.

**FR-SH-072 [P4]** The autopilot integration shall never issue unintended rudder commands. Acceptance test: 2-hour sea trial at anchor and in open water, zero unintended commands. Captain endorsement required before Phase 4 deployment.

**FR-SH-073 [P4]** SafeHelm shall communicate course corrections to pypilot via TCP port 23322. Only heading hold commands shall be issued; SafeHelm shall never override the speed control or autopilot mode directly.

### 6.8 AIS + WiBoat Fusion Rule

**FR-SH-080 [P2]** When a WiBoat contact and an AIS target fall within bearing tolerance ±15° AND range tolerance ±50 m of the AIS-computed position, the system shall merge them into a single UnifiedTarget with:
- `source = {'ais', 'wifi_radar'}`
- `lat/lon` from AIS (authoritative)
- `range_m` from WiBoat (confirmatory)
- `composite_confidence = max(ais_confidence, wiboat_confidence)`

**FR-SH-081 [P2]** If a WiBoat contact and AIS target do NOT match within tolerance, they shall be maintained as separate tracks. The system shall not assume they are the same vessel.

**FR-SH-082 [P2]** AIS + WiBoat fusion raises contact confidence to approximately 0.98. A fused contact shall display both data sources in the AvNav widget detail view.

---

## 7. COLREGs Advisory Specification

This section defines the advisory text, trigger conditions, priority, and recommended action for each COLREGs encounter type. Advisories are derived from IMO International Regulations for Preventing Collisions at Sea (COLREGs) 1972, as amended.

**Advisory Priority Levels:**

| Level | Description | Delivery |
|---|---|---|
| INFO | Situational awareness only | AvNav widget only |
| ADVISORY | Action may be required soon | AvNav widget + voice (normal volume) |
| WARNING | Action required | AvNav widget + voice (elevated) + alarm budget tracked |
| HIGH | Action required promptly | AvNav widget + voice + tone |
| CRITICAL | Immediate action required | AvNav widget + voice (direct espeak — bypasses mute) + alarm budget exempt |
| SYSTEM | Sensor or system status | AvNav widget + voice (if safety-affecting) |

---

### 7.1 Rule 14 — Head-On Situation (Power-driven vessels)

**Trigger:** Two power-driven vessels approaching on near-reciprocal courses (bearing within ±10° of 000° relative); TCPA ≤ 5 minutes.

| Field | Content |
|---|---|
| Priority | HIGH |
| Voice advisory | "Head-on vessel [BEARING]° at [RANGE] metres, TCPA [TIME] minutes. Rule 14 applies. Both vessels must alter course to starboard. Recommend [X]° starboard. Confidence [N]%." |
| AvNav widget | Red contact triangle, bearing, range, TCPA, Rule 14 label, EXECUTE button |
| Recommended action | Alter course to starboard — sufficient to result in port-to-port passing |
| Escalation to CRITICAL | TCPA ≤ 60 seconds |

---

### 7.2 Rule 15 — Crossing Situation, Give-Way Vessel

**Trigger:** Own vessel is power-driven and the other vessel is on the starboard bow (bearing 000° to 112.5° relative); crossing encounter; TCPA ≤ 5 minutes.

| Field | Content |
|---|---|
| Priority | HIGH |
| Voice advisory | "Crossing vessel on starboard at [BEARING]°, [RANGE] metres, TCPA [TIME] minutes. We are the give-way vessel under Rule 15. Recommend altering [X]° to starboard to pass astern. Confidence [N]%." |
| AvNav widget | Red contact triangle, give-way indicator, Rule 15 label, EXECUTE button |
| Recommended action | Alter course to starboard or reduce speed to pass astern of the stand-on vessel |
| Escalation to CRITICAL | CPA < 100 m |

---

### 7.3 Rule 15 — Crossing Situation, Stand-On Vessel

**Trigger:** Own vessel is power-driven and the other vessel is on the port bow (bearing 247.5° to 000° relative); crossing encounter.

| Field | Content |
|---|---|
| Priority | ADVISORY |
| Voice advisory | "Crossing vessel on port at [BEARING]°, [RANGE] metres, TCPA [TIME] minutes. We are stand-on vessel under Rule 15. Maintain course and speed. Monitor." |
| AvNav widget | Amber contact triangle, stand-on indicator, Rule 15 label |
| Recommended action | Maintain course and speed. If other vessel does not give way and collision risk develops, escalate to Rule 17 action. |
| Escalation | If CPA < 100 m and other vessel has not altered course: escalate to HIGH — "Stand-on vessel may not be giving way. Consider evasive action under Rule 17." |

---

### 7.4 Rule 13 — Overtaking, Give-Way Vessel

**Trigger:** Own vessel is approaching another vessel from astern within 22.5° of her stern (relative bearing 112.5° to 247.5°); own vessel speed greater than target speed.

| Field | Content |
|---|---|
| Priority | ADVISORY |
| Voice advisory | "We are overtaking vessel at [BEARING]°, [RANGE] metres. We are give-way vessel under Rule 13. Keep clear to [port/starboard]. Confidence [N]%." |
| AvNav widget | Amber contact, overtaking indicator, Rule 13 label |
| Recommended action | Maintain safe passing distance; alter course to give maximum clearance |

---

### 7.5 Rule 13 — Being Overtaken, Stand-On Vessel

**Trigger:** Another vessel is approaching own vessel from astern within 22.5° of own stern; target speed greater than own speed.

| Field | Content |
|---|---|
| Priority | INFO |
| Voice advisory | "Vessel overtaking from [BEARING]° at [RANGE] metres. We are stand-on vessel under Rule 13. Maintain course and speed." |
| AvNav widget | Blue contact, being-overtaken indicator |
| Recommended action | Maintain course and speed |

---

### 7.6 Rule 16 — Action by Give-Way Vessel (General)

**Trigger:** Applied to any encounter where own vessel is the give-way vessel and recommended action has not been taken within 2 minutes of initial advisory.

| Field | Content |
|---|---|
| Priority | WARNING (escalates from initial advisory) |
| Voice advisory | "Give-way action not yet taken. [VESSEL TYPE] at [BEARING]°, CPA now [RANGE] metres in [TIME] seconds. Take substantial course or speed change now. Rule 16." |
| Recommended action | Early and substantial action — a course change of less than 10° is not sufficient |

---

### 7.7 Rule 17 — Stand-On Vessel, Collision Cannot Be Avoided

**Trigger:** Own vessel is designated stand-on; give-way vessel has not altered course; CPA < 50 m; TCPA < 3 minutes.

| Field | Content |
|---|---|
| Priority | CRITICAL |
| Voice advisory | "Collision risk — give-way vessel not responding. We are stand-on but must now take action under Rule 17. Recommend [X]° [port/starboard] immediately. Rule 17." |
| AvNav widget | Flashing red, Rule 17 label, EXECUTE button |
| Recommended action | Take independent action to avoid collision — any action is permitted at this stage |

---

### 7.8 Rule 18 — Responsibilities Between Vessels (Power vs Sail)

**Trigger:** AIS vessel type identifies target as sailing vessel, fishing vessel, RAM, or NUC, and own vessel is power-driven.

| Field | Content |
|---|---|
| Priority | HIGH |
| Voice advisory | "[VESSEL TYPE] at [BEARING]°, [RANGE] metres, TCPA [TIME] minutes. We are power-driven give-way vessel under Rule 18. Keep clear. Confidence [N]%." |
| Recommended action | Keep clear; pass at safe distance on the designated side for the encounter type |
| Note | Rule 12 (sailing vessel tack priority) is a Phase 3 extension requiring wind angle data from NMEA. Until Phase 3, all sailing vessel encounters default to Rule 18 give-way. |

---

### 7.9 Rule 19 — Restricted Visibility

**Trigger (automatic):** Forward Watch camera confidence < 0.40 for more than 30 seconds (fog/night/rain conditions detected). OR operator activates manually.

**Trigger (WiBoat):** Contact detected by WiFi CSI only (no camera confirmation), range < 500 m, fog/low-visibility conditions active.

| Field | Content |
|---|---|
| Priority | WARNING |
| Voice advisory | "Restricted visibility mode active. Radar contact at [BEARING]°, [RANGE] metres. Proceeding at safe speed. Rule 19 applies. Maintain careful watch." |
| AvNav widget | Fog indicator on status bar; all contacts shown with restricted-visibility flag |
| Recommended action | Proceed at safe speed adapted to visibility and prevailing circumstances; be ready to stop within safe distance |
| WiBoat advantage | WiFi CSI continues to operate in fog/darkness; advisory quality does not degrade |

---

### 7.10 Non-AIS Hazard — Deadhead

**Trigger:** WiBoat classifies contact as `deadhead` with confidence ≥ 0.70, range ≤ 250 m, CPA < own vessel safe manoeuvring distance.

| Field | Content |
|---|---|
| Priority | HIGH (< 200 m); CRITICAL (< 80 m) |
| Voice advisory | "Deadhead detected [RANGE] metres ahead at [BEARING]°. Submerged log — no AIS. Recommend altering [X]° [port/starboard] to clear. Confidence [N]%." |
| AvNav widget | Log/deadhead symbol, range, bearing, confidence, EXECUTE button |
| Recommended action | Alter course to clear; reduce speed if range < 80 m |
| Note | No COLREGs give-way/stand-on logic applies to non-vessel hazards. Avoidance is always own vessel's obligation. |

---

### 7.11 Non-AIS Hazard — Person in Water

**Trigger:** WiBoat classifies contact as `person_in_water` with any confidence score (even below 0.70), range ≤ 200 m.

| Field | Content |
|---|---|
| Priority | CRITICAL (regardless of confidence level) |
| Voice advisory | "Person in water detected [RANGE] metres at [BEARING]°. Reduce speed immediately. Stand by for man-overboard procedures. Confidence [N]%." |
| AvNav widget | MOB symbol, flashing, immediate alert |
| Recommended action | Reduce speed, begin MOB protocol, assign crew to maintain visual contact |
| Note | PIW detection fires at ANY confidence level. The cost of a false alarm is a slow-down; the cost of a missed detection is a life. The alarm budget exemption applies. |

---

### 7.12 Non-AIS Hazard — Ice Floe

**Trigger:** WiBoat classifies contact as `ice_floe` with confidence ≥ 0.70, range ≤ 250 m.

| Field | Content |
|---|---|
| Priority | HIGH |
| Voice advisory | "Ice floe detected [RANGE] metres at [BEARING]°. Drifting hazard — no AIS. Reduce speed and alter course [X]° [port/starboard]. Confidence [N]%." |
| AvNav widget | Ice floe symbol, range, bearing, confidence |
| Recommended action | Alter course and reduce speed; continue monitoring as ice floes drift |

---

### 7.13 Unknown Contact

**Trigger:** WiBoat detects contact; confidence 0.40–0.69 (UNCERTAIN) or classification = `unknown`.

| Field | Content |
|---|---|
| Priority | ADVISORY |
| Voice advisory | "Unidentified contact [RANGE] metres at [BEARING]°. Classification uncertain. Monitoring. Confidence [N]%." |
| AvNav widget | Contact displayed with question-mark uncertainty marker |
| Recommended action | Monitor; if range decreases to < 150 m, escalate to WARNING regardless of confidence |

---

### 7.14 System Degradation

**Trigger:** Any sensor transition to stale or offline status that affects collision avoidance capability.

| Field | Content |
|---|---|
| Priority | SYSTEM |
| Voice advisory | "Warning: [SENSOR NAME] offline. System now in [MODE] mode. [Specific capability lost, e.g., non-AIS targets may not be visible]." |
| AvNav widget | Status banner with mode indicator (colour coded: grey=full, amber=degraded, red=critical) |

---

## 8. Functional Requirements — Communications Layer

### 8.1 LoRa / Meshtastic Mesh

**FR-CM-010 [P2]** The system shall integrate a Heltec V3 LoRa node (915 MHz, Canada) running Meshtastic firmware, connected to the WiBoat RPi 4B via USB serial.

**FR-CM-011 [P2]** The Meshtastic bridge service shall run on RPi 4B and expose a JSON API at `http://[WIBOAT_IP]:8768/vessels`, returning position, heading, speed, signal quality, and last-seen time for all active mesh nodes.

**FR-CM-012 [P2]** LoRa vessels shall be injected into Signal K via the `signalk-meshtastic` plugin on RPi 5. They shall appear in AvNav and in SafeHelm as vessels at their last known position.

**FR-CM-013 [P2]** LoRa vessels shall be tracked at MONITOR priority only in SafeHelm. Their update rate (~60 s) is too slow for CPA/TCPA computation. They shall appear on the chart but shall not trigger CRITICAL alarms. This is by design — long-range awareness, not collision avoidance.

**FR-CM-014 [P2]** Hazard alerts detected by WiBoat shall be broadcast over the LoRa mesh with: object type, hazard coordinates (encoded as bearing/range per the format below), confidence score, and timestamp. Raw CSI data and vessel identity shall never be transmitted over the mesh.

**Hazard coordinate encoding format:**
```json
{
  "object_type": "deadhead",
  "bearing_deg": 127,
  "range_m": 85,
  "confidence": 0.81,
  "ts_utc": 1747350412
}
```
- `bearing_deg`: integer, 0–359 degrees true (relative to transmitting vessel's heading at time of detection)
- `range_m`: integer, metres
- `ts_utc`: Unix epoch seconds UTC

**Receiving vessel transform:** The receiving vessel converts the hazard to its own reference frame using: absolute hazard position = transmitting vessel position + bearing/range vector, then converts to bearing/range from own position. The receiving vessel must have a valid GPS fix to perform this transform.

**Timestamp drift tolerance:** ±30 seconds between nodes. Meshtastic nodes use GPS-disciplined clock when a GPS fix is available; NTP otherwise. Alerts older than 5 minutes shall be discarded as stale and not displayed.

**Privacy rationale:** Bearing/range encoding avoids transmitting own vessel's absolute GPS position over the mesh.

**FR-CM-015 [P2]** Received hazard alerts from other mesh vessels shall be displayed in AvNav as a shared hazard layer. A received alert shall display: source vessel (node ID only, anonymized), hazard type, coordinates, age of detection. Received alerts shall not trigger voice advisories unless the hazard is within 1 nm of own vessel.

**FR-CM-016 [P2]** If the Meshtastic serial connection is lost, the bridge service watchdog shall call `restartPlugin()` after 3 missed heartbeats (30 seconds). If Signal K plugin restart fails, the watchdog shall notify Fix My Pi diagnostics.

**FR-CM-017 [P2]** LoRa-equipped non-d3kOS vessels (a kayak with a Heltec V3 running Meshtastic) shall appear in AvNav as trackable contacts at their broadcast position, even though they have no radar signature. This is the cooperative picture for equipped vessels.

### 8.2 5 GHz batman-adv Cooperative Mesh (Phase 3)

**FR-CM-020 [P3]** When two or more WiBoat-equipped vessels are within 500 m, their 5 GHz WiFi adapters shall form a batman-adv mesh network automatically.

**FR-CM-021 [P3]** In cooperative mesh mode, the WiBoat contact lists from multiple vessels shall be merged using the following algorithm:

**Contact matching criteria** (two contacts are considered the same physical target when ALL of the following hold):
- Bearing deviation: ≤ 25° between the bearing vectors resolved to a common reference frame
- Range deviation: ≤ 50 m from the AIS-derived or GPS-derived position of each node
- Classification agreement: same class, OR at least one contact is classified `unknown`
- Time difference: observations within ≤ 2 seconds of each other

**Merge result:**
- `range_m`: weighted mean, weight = range_confidence of each node
- `bearing_deg_true`: weighted mean, weight = bearing_confidence of each node
- `classification`: class with higher confidence score; if both have equal confidence, the node with more Kalman-stable frames wins
- `composite_confidence`: `min(1.0, c_node1 + c_node2 × 0.30)` — multistatic bonus of 30% of the second node's confidence, capped at 1.0
- `source_node_ids`: array of all contributing node IDs (e.g., `["node_A", "node_B"]`)

**No-match (separate tracks):** If bearing deviation > 25° or range deviation > 50 m, the contacts are maintained as independent tracks. They are not merged.

**Classification contradiction:** If two contacts match spatially (bearing ≤ 25°, range ≤ 50 m) but have contradictory classifications each with composite_confidence > 0.60 (e.g., node A says `vessel`, node B says `deadhead`), the contacts shall be flagged as `TRACKING_CONFLICT`, both tracks retained, and a SYSTEM advisory issued: "Contact classification conflict between sensors — monitor manually."

**Kalman state fusion:** Each node independently maintains its Kalman filter. The merged contact uses innovation-weighted combination of the two Kalman estimates. `kalman_stable` in the merged contact requires both source nodes to independently report `kalman_stable: true` before the merged track is considered stable.

**FR-CM-022 [P3]** batman-adv mesh topology shall be self-healing. Vessels entering and leaving the mesh shall not require configuration changes.

**FR-CM-023 [P3]** Cooperative multistatic sensing shall be used to resolve blind spots caused by own vessel hull or superstructure blocking WiFi reflections.

---

## 9. Functional Requirements — AI Quality Layer

The AI quality layer comprises three distinct functions with separate latency and infrastructure profiles. These are NOT the same system.

### 9.1 Fast Path — TFLite Edge Inference (On-device, RPi 4B)

**FR-AI-010 [P2]** Object classification (FR-WB-040 through FR-WB-045) shall be performed by a TensorFlow Lite CNN-LSTM model running entirely on the WiBoat RPi 4B. No cloud call is made in the detection path.

**FR-AI-011 [P2]** The TFLite model shall complete inference in ≤ 50 ms per contact to remain within the 100 ms processing loop budget.

**FR-AI-012 [P2]** If SoC temperature exceeds 75°C, the system shall switch to a quantized lightweight model variant that maintains ≤ 200 ms latency. The thermal event shall be logged. This is the thermal management requirement from the NFR.

**FR-AI-013 [P2]** The classification model shall be versioned. The model file shall be stored at `/opt/wiboat/models/classifier_vX.Y.tflite`. On service start, the latest version is loaded. Old versions are retained for 30 days (configurable) for diagnostic rollback.

### 9.2 Explanation Path — Gemini Proxy (d3kOS, real-time explanation)

**FR-AI-020 [P2]** When a new contact is classified with confidence ≥ 0.70, or when an advisory is generated, the system shall submit a structured query to the existing d3kOS Gemini proxy (port 8097) requesting a plain-language explanation of the classification.

**FR-AI-021 [P2]** The Gemini explanation query shall be non-blocking. It shall not delay advisory delivery. Advisory delivery via voice/AvNav occurs immediately from the COLREGs engine. The Gemini explanation appends to the advisory within 1–5 seconds.

**FR-AI-022 [P2]** The Gemini explanation shall include:
- Why the contact was classified as the stated type (which signal features drove the decision)
- The confidence breakdown by sensor (WiFi CSI, camera, AIS, LoRa)
- Whether the COLREGs rule selection is consistent with the contact's known characteristics
- One-sentence plain-language explanation suitable for delivery via Helm voice

**FR-AI-023 [P2]** Example explanation output: "Contact classified as deadhead at 87% confidence. Stationary dense reflection, no Doppler, waterlogged-wood dielectric contrast detected. No AIS. COLREGs: non-vessel hazard — avoidance is own vessel's obligation."

**FR-AI-024 [P2]** If the Gemini proxy is offline or returns an error, the advisory shall still be delivered without the explanation. The system shall not block on AI explanation availability.

**FR-AI-025 [P2]** The Gemini explanation layer shall also respond to Helm voice queries about WiBoat status (see Section 10.4).

**FR-AI-026 [P2] — Gemini Explanation Throttling Policy:** The following rules govern query rate to the Gemini proxy (port 8097):

**Rate limit:** Maximum **4 explanation queries per 60-second rolling window**. This applies across all contacts and advisory events combined.

**Queue behaviour:** When the rate limit is reached, additional qualifying queries are placed in a priority queue. Queue ordering:

| Priority | Advisory Level / Event |
|---|---|
| 1 (highest) | CRITICAL alerts, PIW detections |
| 2 | HIGH advisories |
| 3 | WARNING advisories |
| 4 | New contacts ≥ 0.70 confidence |
| 5 (lowest) | ADVISORY level, confidence 0.70–0.79 |

Maximum queue depth: 8 pending queries. When queue is full, the lowest-priority pending query is dropped and logged as `EXPLANATION_DROPPED`.

**Caching:** If the same `contact_id` generates a new advisory within 10 minutes, and the classification type and confidence tier (≥0.70, 0.40–0.69) are unchanged, the prior explanation is reused without a new Gemini query. Cache key: `contact_id + classification_type + confidence_tier`. Cache TTL: 10 minutes.

**Low-priority deferral:** Priority 5 queries (ADVISORY, confidence 0.70–0.79) are deferred until the queue has been empty for ≥ 5 seconds. If the queue remains busy for > 60 seconds, the low-priority explanation is skipped and logged as `EXPLANATION_SKIPPED`. The advisory itself is still delivered without the explanation.

**Burst scenario:** If 20 qualifying contacts appear within one processing cycle (e.g., entering a busy harbour), the throttle queue accepts the highest-priority 8 and drops the rest. The captain receives advisories for all contacts immediately; explanations are delivered as queue capacity allows.

### 9.3 Post-Voyage Optimization — Gemini Pro (Async, cloud)

**FR-AI-030 [P3]** At end of voyage (when SafeHelm is set to inactive state), the system shall compile a voyage AI report package containing: anonymized contact events, classification decisions, confidence scores, false alarms (WiBoat saw contact but camera did not confirm), and missed detections (camera saw contact but WiBoat did not).

**FR-AI-031 [P3]** The voyage AI report shall be submitted to Gemini Pro (via the existing Gemini API on d3kOS) for post-voyage analysis. Results shall be returned within 24 hours.

**FR-AI-032 [P3]** The post-voyage analysis shall produce:
- A corrected dataset of misclassified contacts with suggested correct labels
- Recommended adjustments to wave filter parameters based on sea state during the voyage
- A confidence calibration report (is the model's stated confidence accurate vs. ground truth?)
- A plain-language voyage safety summary for the captain's boat log

**FR-AI-033 [P3]** The corrected dataset shall be stored locally and used as the training input for the next model update. Model weight updates shall be operator-approved before deployment to the active classifier.

---

## 10. Functional Requirements — d3kOS Integration

### 10.1 LAN Connectivity

**FR-DK-010 [P1]** WiBoat RPi 4B and SafeHelm RPi 5 shall communicate exclusively over Ethernet. On-boat deployment uses `10.0.0.0/24` subnet. LAN/development deployment uses `192.168.1.0/24` subnet. WiFi shall not be used for inter-device communication on either network.

**FR-DK-011 [P1]** WiBoat RPi 4B on-boat static IP shall be `10.42.0.2` (hardcoded in firmware and `wiboat-config.json`). This IP shall be stored as `signalk.host` in `wiboat-config.json` and as `wiboat.host` in `safehelm-config.json`. The `WIBOAT_HOST` environment variable overrides these values for LAN/development deployments. In Phase 4 single-box mode, both values shall be `localhost`.

### 10.2 Signal K Integration

**FR-DK-020 [P1]** WiBoat contacts confirmed by SafeHelm (composite confidence ≥ 0.70) shall be injected into Signal K on RPi 5 as virtual vessel entries in the `vessels.*` path using MMSI range 998000001–998000099.

**FR-DK-021 [P1]** Camera contacts from Forward Watch shall use MMSI range 999000001–999000099 (existing, unchanged). WiBoat-only contacts shall use MMSI range 998000001–998000099. Fused AIS+WiBoat contacts shall use the real MMSI from AIS.

**FR-DK-022 [P1]** SafeHelm shall subscribe to Signal K for own vessel data: `vessels.self.navigation.headingTrue`, `vessels.self.navigation.speedOverGround`, `vessels.self.navigation.position`, `vessels.self.navigation.courseOverGroundTrue`.

### 10.3 d3kOS Voice System (ai_bridge)

**FR-DK-030 [P2]** All COLREGs advisories and sensor status alerts shall be delivered via POST to `http://localhost:3002/webhook/alert` on d3kOS ai_bridge. The alert payload shall include: message text, priority level, and source ("safehelm").

**FR-DK-031 [P2]** CRITICAL level alerts (PIW detection, CPA < 50 m, BLIND mode) shall additionally invoke espeak-ng directly via subprocess, bypassing the ai_bridge queue and mute state.

**FR-DK-032 [P2]** Voice alert text shall conform to the COLREGs Advisory Specification in Section 7. Advisory text shall be concise (under 20 words for WARNING and above) and unambiguous. Numbers shall be spoken as individual digits for bearing and range (e.g., "one-two-seven degrees, two-hundred metres").

**FR-DK-033 [P2]** Voice language shall follow the d3kOS locale setting. The system shall support the 18 languages specified in the NFR (FR-NFR-032), with English as the fallback when a translation is unavailable.

### 10.4 Helm AI Query Interface

**FR-DK-040 [P2]** The d3kOS Helm AI voice assistant shall be extended to respond to WiBoat/SafeHelm queries. The Helm assistant shall route queries matching WiBoat/SafeHelm intent patterns to a SafeHelm query endpoint before responding.

**FR-DK-041 [P2]** Supported Helm AI queries (minimum set):

| Query intent | Example phrase | Response source |
|---|---|---|
| Current contacts | "What's WiBoat seeing?" | SafeHelm /status — contact list |
| Specific contact | "Explain the contact to starboard" | SafeHelm + Gemini explanation path |
| Collision risk | "What's my collision risk right now?" | SafeHelm COLREGs engine summary |
| System status | "Is WiBoat online?" | WiBoat health API |
| Mode status | "What mode is SafeHelm in?" | SafeHelm operating mode |
| Nearest hazard | "What's the nearest hazard?" | SafeHelm closest non-AIS contact |

**FR-DK-042 [P2]** SafeHelm shall expose a query REST endpoint at `http://localhost:8095/safehelm/query` accepting a JSON intent object and returning a structured response suitable for Gemini to compose into a Helm voice reply.

**FR-DK-043 [P2]** The Helm AI query interface shall operate in under 3 seconds end-to-end from voice input to voice response under normal conditions.

### 10.5 d3kOS Settings UI Integration

**FR-DK-050 [P2]** WiBoat + SafeHelm configuration shall be accessible via the d3kOS Settings UI under a new "Safety" section. No SSH access shall be required for routine operator configuration.

**FR-DK-051 [P2]** Configurable settings exposed in the UI (minimum):
- SafeHelm enabled / disabled
- Alarm budget (warnings per hour, 3–12 configurable)
- Minimum safe CPA distance (default 50 m)
- Night mode toggle
- Vessel dynamics profile (LOA, type, propulsion)
- WiBoat host IP (for two-box mode)
- Classification confidence threshold (0.50–0.90 configurable)
- PIW detection sensitivity (always max — not configurable below HIGH)
- Post-voyage AI analysis enabled / disabled

**FR-DK-052 [P3]** Settings UI shall display current operating mode, active sensor count, and last contact detection time.

### 10.6 Fix My Pi Integration

**FR-DK-060 [P1]** WiBoat and SafeHelm services shall register with the d3kOS Fix My Pi diagnostics system as monitored services.

**FR-DK-061 [P1]** Fix My Pi shall be able to: check service health status, restart individual services, and run the WiBoat range validation test (test against known reflector at configured distance).

**FR-DK-062 [P1]** Service health data (uptime, CSI packet rate, contact count, loop overrun events) shall be available to Fix My Pi via the WiBoat health API and the SafeHelm status endpoint.

---

## 11. Functional Requirements — Signal K Plugin (Standalone Compatibility)

The Signal K plugin layer provides a base level of WiBoat + SafeHelm capability to any Signal K system, including OpenPlotter. This section defines what works WITHOUT d3kOS.

### 11.1 Base Plugin Capability

**FR-SK-010 [P1]** A standalone Signal K plugin (`signalk-wiboat`) shall be published as an open-source npm package. It shall connect to the WiBoat WebSocket on port 8766 and inject contacts into Signal K without requiring d3kOS.

**FR-SK-011 [P1]** The plugin shall inject WiBoat contacts as Signal K vessel objects using MMSI range 970000001–970000099 in standalone mode.

**FR-SK-012 [P2]** The plugin shall include a basic COLREGs proximity alert engine producing Signal K notifications (the standard Signal K notification path). These notifications shall be visible in freeboard-sk, Kip, and AvNav without additional plugins.

**FR-SK-013 [P2]** The plugin shall produce standard NMEA 0183 `!AIVDM` sentences via `signalk-to-nmea0183`, allowing WiBoat contacts to appear on any NMEA-connected chart plotter.

**FR-SK-014 [P2]** The plugin shall provide a basic AvNav overlay widget compatible with the standard AvNav plugin API. This widget shall show contact symbols and confidence scores. It shall not include the d3kOS-specific Helm AI, boat log, or Gemini explanation features.

### 11.2 OpenPlotter Compatibility

**FR-SK-020 [P2]** The WiBoat processor (RPi 4B) and the `signalk-wiboat` plugin shall function without d3kOS installed. An OpenPlotter user with a WiBoat RPi 4B and a Signal K server shall be able to see contacts on freeboard-sk.

**FR-SK-021 [P2]** The installation documentation shall include a standalone installation guide for OpenPlotter / bare Signal K, clearly noting which features require d3kOS.

**FR-SK-022 [P2]** Voice alerts for non-d3kOS users shall be delivered via the Signal K notification system (text only). Audio is the responsibility of the Signal K display application used.

---

## 12. Functional Requirements — Data Logging and User Management

### 12.1 Contact Detection Events

**FR-LOG-010 [P1]** Every contact detection event shall be appended to the d3kOS boat log. Event fields: timestamp (ISO 8601), contact ID, object type, range, bearing, composite confidence, sensor source(s), operating mode.

**FR-LOG-011 [P1]** Contact detection events shall be stored in the existing d3kOS boat log database. WiBoat events shall be tagged with `source: "wiboat"` for filtering.

**FR-LOG-012 [P1]** Log entries shall not include: raw CSI data, camera frames, GPS coordinates of other vessels, or any personally identifiable information about other mariners.

### 12.2 Advisory and Alarm Events

**FR-LOG-020 [P2]** Every advisory or alarm generated by SafeHelm shall be logged with: timestamp, COLREGs rule applied, advisory text, priority level, contact ID(s) involved, recommended action, and whether the captain acknowledged or dismissed the advisory.

**FR-LOG-021 [P2]** The post-voyage AI summary (from FR-AI-033) shall be appended to the boat log as a voyage entry with: voyage duration, total contacts, false alarm count, advisory count by priority, and the Gemini-generated captain's summary.

### 12.3 Sensor Performance Logging

**FR-LOG-030 [P1]** Per-voyage sensor performance shall be logged: CSI packet rate (average and minimum), classification confidence distribution, operating mode time breakdown (minutes in each mode), and loop overrun count.

**FR-LOG-031 [P1]** Thermal events (SoC > 75°C, lightweight model engaged) shall be logged with timestamp and duration.

### 12.4 User Log Management

**FR-LOG-040 [P2]** The captain shall be able to view WiBoat/SafeHelm log entries via the d3kOS Settings UI without SSH access.

**FR-LOG-041 [P2]** Log view shall support filtering by: date range, event type (contact / advisory / alarm / system), priority level, object type.

**FR-LOG-042 [P2]** The captain shall be able to export the WiBoat/SafeHelm log to a CSV or JSON file for external analysis. Export shall be accessible from the Settings UI.

**FR-LOG-043 [P2]** The captain shall be able to delete log entries by date range from the Settings UI. The system shall warn before deleting entries less than 30 days old. Deletion is irreversible.

**FR-LOG-044 [P2]** Log retention policy (configurable in Settings UI, default 90 days): entries older than the retention period shall be automatically purged. The purge schedule shall run at 02:00 local time when the system is active.

**FR-LOG-045 [P2]** All persistent logs shall be stored with AES-256 encryption at rest, consistent with the NFR security requirement. The encryption key shall be derived from the d3kOS device identifier. Key management shall be documented in the system installation guide.

---

## 13. Functional Requirements — Display and UI

### 13.1 AvNav Overlay Widget

**FR-UI-010 [P2]** SafeHelm shall provide an AvNav JavaScript widget (`safehelm-widget.js`) that overlays on the AvNav chart. The widget shall be loadable as a standard AvNav user plugin.

**FR-UI-011 [P2]** The widget shall display in a persistent corner panel: current operating mode, active sensor count (with traffic-light colour indicator), active advisory count, and alarm budget remaining.

**FR-UI-012 [P2]** Each WiBoat contact shall appear on the AvNav chart as a typed symbol:

| Object Type | Symbol | Colour |
|---|---|---|
| `vessel` | AIS triangle | Standard AIS colours |
| `person_in_water` | Person/MOB symbol | Red |
| `deadhead` | Log/anchor symbol | Orange |
| `ice_floe` | Diamond/snowflake | Cyan |
| `unknown` (UNCERTAIN) | Circle with ? | Grey |
| LoRa vessel | AIS triangle (dashed outline) | Blue |

**FR-UI-013 [P2]** Tapping a contact symbol on the AvNav chart shall open a contact detail panel showing: object type, confidence breakdown by sensor, range, bearing, CPA, TCPA (if computable), COLREGs rule applied, and the Gemini AI explanation (when available).

**FR-UI-014 [P2]** Active advisories shall display in a scrollable advisory panel within the widget. Each advisory shall show: time, priority indicator, advisory text, and EXECUTE / DISMISS buttons.

**FR-UI-015 [P2]** The EXECUTE button shall confirm the advisory and, in Phase 4, route the recommended course change to pypilot. In Phases 1–3, EXECUTE records captain acknowledgement in the boat log.

**FR-UI-016 [P2]** The DISMISS button suppresses re-alerting for the same contact for 2 minutes, logs the dismissal, and removes the advisory from the panel.

### 13.2 Contact Symbology Standards

**FR-UI-020 [P2]** All contact symbols shall conform to d3kOS iconography and shall align with ECDIS/IMO symbology where a standard symbol exists.

**FR-UI-021 [P2]** Contact symbols shall maintain consistent colour semantics across all views: red = CRITICAL hazard requiring immediate action; orange = WARNING/HIGH requiring prompt action; amber = ADVISORY requiring monitoring; grey = INFO / uncertain; blue = cooperative mesh vessel.

**FR-UI-022 [P2]** Confidence level shall be displayed as a percentage on the contact label (e.g., "87%"). Contacts below 0.70 composite confidence shall display the UNCERTAIN marker (question mark overlay on symbol).

### 13.3 Accessibility (AODA / WCAG 2.1 AA)

**FR-UI-030 [ALL]** Minimum touch target size: 60 × 60 px for all interactive widget elements. UI shall remain operable with wet hands or gloves.

**FR-UI-031 [ALL]** Minimum contrast ratio: 4.5:1 for standard text; 3:1 for large text and icons.

**FR-UI-032 [ALL]** All text in the widget and settings UI shall be a minimum of 18px. No exception.

**FR-UI-033 [ALL]** The widget shall function correctly at both 100% and 150% browser zoom levels.

### 13.4 Night Mode

**FR-UI-040 [P2]** A night mode (Red-Only) shall be available. Night mode shall:
- Apply a red-wavelength only colour filter to the widget and contact symbols
- Suppress all blue and green wavelengths
- Maintain luminance levels appropriate for scotopic (dark-adapted) vision
- Be activatable by voice command ("night mode on/off") and by widget toggle

**FR-UI-041 [P2]** Night mode state shall persist across AvNav page navigation and browser refresh.

---

## 14. Phase Applicability Matrix

This matrix maps every functional requirement group to its required delivery phase. A requirement marked [P2] must be met before Phase 2 sea trial gate G2.3 can be declared passed.

| Requirement Group | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| CSI extraction (FR-WB-001–006) | ✓ | | | |
| Range estimation (FR-WB-010–014) | ✓ | | | |
| Standalone AvNav fallback (FR-WB-070–073) | ✓ | | | |
| Contact output WebSocket (FR-WB-060–063) | ✓ | | | |
| Kalman tracker (FR-WB-050–053) | ✓ | | | |
| Sensor fusion Layer 1 (FR-SH-010–014) | ✓ | | | |
| Real-time execution core (FR-SH-020–023) | ✓ | | | |
| SafeHelm shadow mode | ✓ | | | |
| d3kOS LAN connectivity (FR-DK-010–011) | ✓ | | | |
| Signal K integration (FR-DK-020–022) | ✓ | | | |
| Fix My Pi integration (FR-DK-060–062) | ✓ | | | |
| Signal K plugin base (FR-SK-010–011) | ✓ | | | |
| Contact detection logging (FR-LOG-010–012) | ✓ | | | |
| Sensor performance logging (FR-LOG-030–031) | ✓ | | | |
| Bearing estimation (FR-WB-020–024) | | ✓ | | |
| Clutter filtering (FR-WB-030–033) | | ✓ | | |
| Object classification TFLite (FR-WB-040–046) | | ✓ | | |
| TFLite fast path AI (FR-AI-010–013) | | ✓ | | |
| Gemini explanation path AI (FR-AI-020–025) | | ✓ | | |
| COLREGs decision engine (FR-SH-040–046) | | ✓ | | |
| Vessel dynamics model (FR-SH-030–032) | | ✓ | | |
| Voice advisory delivery (FR-DK-030–033) | | ✓ | | |
| Helm AI query interface (FR-DK-040–043) | | ✓ | | |
| AvNav overlay widget full (FR-UI-010–016) | | ✓ | | |
| Night mode (FR-UI-040–041) | | ✓ | | |
| LoRa / Meshtastic mesh (FR-CM-010–017) | | ✓ | | |
| Advisory logging (FR-LOG-020–021) | | ✓ | | |
| User log management (FR-LOG-040–045) | | ✓ | | |
| Signal K plugin full (FR-SK-012–022) | | ✓ | | |
| Settings UI (FR-DK-050–052) | | ✓ | | |
| Human interface / alarm budget (FR-SH-060–065) | | ✓ | | |
| AIS + WiBoat fusion (FR-SH-080–082) | | ✓ | | |
| 4-antenna 360° bearing — MUSIC software (FR-WB-022, FR-WB-024) | | ✓ | | |
| Multi-vessel conflict solver (FR-SH-050–054) | | | ✓ | |
| Rule 12 sailing vessel tack (FR-SH-046) | | | ✓ | |
| Rule 19 restricted visibility (FR-SH-045) | | | ✓ | |
| 5 GHz batman-adv mesh (FR-CM-020–023) | | | ✓ | |
| Post-voyage AI optimization (FR-AI-030–033) | | | ✓ | |
| COLREGs Rule 19 mode | | | ✓ | |
| Control Barrier Functions (FR-SH-070–073) | | | | ✓ |
| pypilot autopilot integration | | | | ✓ |
| Single-box consolidation | | | | ✓ |

---

## 15. Out of Scope

The following are explicitly excluded from this FRD and shall not be built or implied by any requirement above:

1. **Commercial or regulatory certification** — WiBoat + SafeHelm is not a certified safety system. SOLAS compliance, Transport Canada type approval, and CE marking are out of scope for v0.x. They may become goals in a future FRD version.

2. **TURN server infrastructure** — WiBoat cooperative communication uses LoRa (no internet required) and Ethernet LAN. No cloud TURN server, broker, or relay is needed or built.

3. **Vessel tracking beyond 50 nm** — AIS covers registered vessels to 50 nm. WiBoat WiFi CSI operates to 250 m. LoRa mesh covers 5–15 km. No system component attempts tracking beyond these natural limits.

4. **Radar replacement for commercial vessels** — WiBoat is advisory for recreational and small commercial vessels. It is not a substitute for Class A radar or ARPA on vessels where these are required by regulation.

5. **d3k-lite / OpenPlotter feature parity** — The Signal K plugin provides base compatibility. d3kOS-specific features (Gemini AI explanation, Helm voice, boat log) require d3kOS.

6. **Offline AI model (Gemma4 on Pi)** — Gemma4 (9.6 GB) exceeds available RPi 5 RAM. Real-time AI explanation uses the existing Gemini proxy on d3kOS. If a future lighter model (under 3 GB quantized) becomes available that fits on the Pi 5 with full d3kOS running, it may be scoped in a future FRD revision.

7. **Tailscale VPN** — Removed from the architecture per project decision S79. Not used.

8. **App Store distribution** — PWA only for any mobile companion integration.

---

## 16. Dependencies and Constraints

| Dependency | Details | Blocks |
|---|---|---|
| Raspberry Pi 4B with BCM43455 WiFi | Required for nexmon_csi. BCM43455 is the CSI extraction chip. | All WiBoat sensing |
| Kernel 5.10 locked (Bullseye 32-bit) | nexmon_csi requires this kernel. Cannot apt upgrade. | WiBoat RPi 4B OS |
| Signal K running on RPi 5 | Required for AIS data, own vessel heading, AvNav injection | SafeHelm Layers 1, 4, 6 |
| d3kOS ai_bridge running on RPi 5 | Required for Helm voice advisories | Voice delivery |
| d3kOS Gemini proxy running on RPi 5 | Required for AI explanation path | FR-AI-020–025 |
| Static IP assigned to WiBoat RPi 4B | Operator action — must be done before Phase 1 code | All LAN integration |
| AvNav running on RPi 5 | Required for overlay widget display | FR-UI-010–022 |
| Heltec V3 flashed with Meshtastic firmware | Required for LoRa mesh | FR-CM-010–017 |
| Non-16k kernel on RPi 5 | Required for Phase 4 single-box nexmon_csi | Migration Gate 3 |
| ALFA AWUS036NH (×2 from Phase 1) | TX injectors for probe frame injection. Both units deployed from Phase 1 for full azimuthal TX coverage. | Range and bearing |
| 12 dBi outdoor omni antennas (×4 from Phase 1) | Mast or radar arch mount. LMR-400 coax. All 4 installed Phase 1. | Range / bearing performance |
| SP4T RF switch (×1, GPIO-controlled) | Single-pole 4-throw RF switch connects 4 antennas to BCM43455 RX input. GPIO cycling enables 4-channel time-multiplexed CSI from single BCM43455. | 4-channel bearing (Phase 2 software) |
| IMU connected to RPi via Signal K | Required for ego-motion compensation (FR-WB-032) | Phase 2 clutter filtering |
| Forward Watch camera operational | Required for sensor fusion classification confirmation | Phase 2 confidence targets |

**EIRP Constraint:** The configured transmit power (ALFA 2W + 12 dBi antenna + 800 mW amplifier, Phase 2) must not exceed 4W (36 dBm) EIRP under ISED RSS-210 (Canada). Target is approximately 2.5W EIRP = 34 dBm. EIRP calculation must be documented before the amplifier is deployed on the boat.

---

## 17. Known Gaps and Open Questions

These are unresolved at FRD v1.0. Each must be resolved before the phase indicated.

| # | Gap | Phase Required | Resolution Path |
|---|---|---|---|
| G1 | nexmon_csi exact kernel version for RPi 5 unconfirmed | Before P4 | Migration Gate 3 bench test resolves this |
| G2 | ~~WiBoat static IP not yet assigned~~ **RESOLVED 2026-05-15** | Resolved | On-boat IP confirmed: `10.42.0.2` (hardcoded). LAN/dev network: `192.168.1.x`. See Section 4.2 and FR-DK-011. |
| G3 | ~~Port/starboard bearing ambiguity in 2-antenna (Phase 1–2)~~ **RESOLVED BY DESIGN** | Phase 1 hardware | 4-antenna UCA with SP4T RF switch installed from Phase 1. Bearing ambiguity eliminated by Phase 2 MUSIC activation. No forward-looking assumption required. See FR-WB-021, FR-WB-022. |
| G4 | Waterlogged wood dielectric contrast vs. seawater at 2.4 GHz | Before P2 classification | Marine environment test data required |
| G5 | IMU signal path to WiBoat processor not implemented | Before P2 | Signal K IMU → WiBoat heading compensation. **v1.2:** FR-WB-032 Tier B degraded mode documented — GPS-only de-trending operational pending IMU path resolution |
| G6 | WiBoat CPU budget on RPi 5 (Phase 4) unvalidated | Before P4 | Migration Gate 3 resolves |
| G7 | 5 GHz adapter for batman-adv mesh not in Phase 1–2 BOM | Before P3 | Budget and procure for Phase 3 |
| G8 | Rain/spray WiFi range degradation unquantified | Phase 2 report | Marine environment test characterizes |
| G9 | LoRa vessel update rate (~60 s) too slow for CPA/TCPA | Documented design decision | By design: LoRa = MONITOR only |
| G10 | Rule 12 (sailing vessel tack) requires wind angle from NMEA | Phase 3 | NMEA wind data path must be confirmed |
| G11 | Post-voyage AI training data volume management | Phase 3 | Retention policy for voyage snippets |
| G12 | Model weight update approval workflow | Phase 3 | Operator-approval gate in Settings UI |

---

## 18. Glossary

| Term | Definition |
|---|---|
| AIS | Automatic Identification System — standard vessel transponder for position and identity |
| AvNav | AvNav Navigator — open-source chart plotter running on d3kOS |
| batman-adv | Better Approach To Mobile Adhoc Networking (advanced) — Layer 2 WiFi mesh protocol |
| BCM43455 | Broadcom WiFi chip in Raspberry Pi 4B/5. nexmon_csi patches this chip for CSI extraction |
| CPA | Closest Point of Approach — minimum predicted distance between two vessels |
| CSI | Channel State Information — per-subcarrier amplitude and phase data extracted from WiFi frames |
| Deadhead | Semi-submerged or fully submerged log. Major hazard in Pacific Northwest and tidal waterways |
| EIRP | Effective Isotropic Radiated Power — total transmitted power including antenna gain |
| IFFT | Inverse Fast Fourier Transform — mathematical transform used to extract time-of-flight from CSI |
| IMO | International Maritime Organization |
| IMU | Inertial Measurement Unit — accelerometer + gyroscope. Provides pitch, roll, yaw data |
| ISED | Innovation, Science and Economic Development Canada — regulator for radio spectrum |
| Kalman filter | Recursive state estimation algorithm used to track contacts across successive observations |
| LoRa | Long Range — low-power radio technology. Used with Meshtastic firmware for mesh networking |
| Meshtastic | Open-source LoRa mesh network firmware |
| MMSI | Maritime Mobile Service Identity — 9-digit vessel identifier used in AIS |
| MUSIC | Multiple Signal Classification — algorithm for Angle of Arrival estimation from multi-antenna phase data |
| nexmon_csi | Open-source firmware patch for Broadcom WiFi chips enabling raw CSI output |
| NMEA 0183 | Serial data standard for marine instruments |
| NPU | Neural Processing Unit — dedicated AI inference accelerator (e.g., Raspberry Pi AI HAT+) |
| PIW | Person In Water — the highest-priority non-AIS hazard detection class |
| RCS | Radar Cross-Section — measure of how detectable an object is to radar/WiFi |
| SafeHelm | COLREGs collision avoidance engine. Runs on RPi 5 as part of d3kOS |
| Signal K | Open-source marine data interchange standard and server. Used by d3kOS, OpenPlotter, others |
| TCPA | Time to Closest Point of Approach — predicted time until minimum separation between two vessels |
| TFLite | TensorFlow Lite — compressed neural network inference runtime for edge devices |
| ToF | Time of Flight — the time delay of a reflected signal, used to estimate range |
| WCAG | Web Content Accessibility Guidelines |
| WiBoat | WiFi CSI proximity sensing subsystem. Runs on RPi 4B (kernel 5.10 locked) |

---

*WiBoat + SafeHelm Functional Requirements Document v1.2*
*2026-05-15 | Skipper Don | AtMyBoat.com*
*Source documents: WIBOAT_SAFEHELM_INTEGRATED_ARCHITECTURE.md v1.0 · SAFEHELM_SYSTEM_SPEC.md v1.0 · nfr wiboat.odt · WiBoat_SafeHelm_Business_Case.docx · wifi_marine_radar_RD_framework.md v0.1 · wiboat review of integration.odt · WiFi can identify object types.odt*
*Temporary location: C:\Users\donmo\Downloads\wiboat\ — to be relocated to Helm-OS project directory in a future session*
