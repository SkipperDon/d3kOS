# Entity: SafeHelm

*Last updated: S85 2026-05-20 | Sources: SAFEHELM_DESIGN.md, SAFEHELM_SYSTEM_SPEC.md, PROJECT_CHECKLIST.md PART 18*

---

## Status

**DESIGN ONLY — no code written.** Architecture complete. Community interest gauge article drafted, not yet posted (SH-1 pending).

---

## What It Is

Maritime collision avoidance module for d3kOS. Watches for vessels on a collision course and warns the captain. Fuses three data sources: AIS (via Signal K), radar contacts (via Signal K), and camera detections (eWaSR ML model on Reolink cameras).

---

## Architecture

- **Language:** Python
- **Port:** 8095
- **Service:** `d3kos-safehelm.service` (not yet created)
- **Path:** `/opt/d3kos/services/safehelm/` (not yet deployed)
- **Design doc:** `deployment/docs/SAFEHELM_DESIGN.md` (1,312 lines, v1.0 S77)
- **System spec:** `deployment/docs/safehelm/SAFEHELM_SYSTEM_SPEC.md`

## Data Sources

| Source | How | PGNs / Path |
|--------|-----|-------------|
| AIS | Signal K vessel store | via can0 / TCP 10110 |
| Radar contacts | Signal K | requires radar on N2K |
| Camera detections | eWaSR on Reolink cameras | ports 8084/8086 |
| WiBoat contacts | WebSocket :8766 | when WiBoat hardware present |

## Synthetic AIS Injection

SafeHelm creates virtual vessels in Signal K for non-AIS contacts:
- **999xxxxxx** — camera-only detections
- **998xxxxxx** — WiBoat/radar contacts

Injection via TCP port 10110 (NMEA 0183 delta). **AIS isolation is mandatory** — see [[concepts/ais-isolation]].

## Build Phases

| Phase | Mode | Description |
|-------|------|-------------|
| 1 | Shadow | Log only, no alarms. Validates CPA/TCPA math. |
| 2 | Advisory | Voice alerts via ai_bridge + AvNav widget. Sea trial required. |
| 3 | Conflict Solver | Multi-vessel graph, non-compliant vessel detection. |
| 4 | Autopilot | pypilot integration. Hard gate: full sailing season in Phase 2 first. |

## COLREGs Coverage

Rules 8, 12–19. Rule 12 (sailing vessel port/starboard tack) requires wind angle input. Rule 19 (restricted visibility) requires fog/night detection.

## Alert Delivery

- Voice: `POST http://localhost:3002/webhook/alert` → ai_bridge (Jabra S330)
- Chart: AvNav JS widget at `~/avnav/user/plugins/`
- MFD: PGN 126983 via PiCAN-M → Axiom MFD (LH4.8.164+, bidirectional acknowledgment via PGN 126984)

## Open Gaps (PART 18)

14 tasks open. Key gates before Phase 1:
- SH-15 (new): explicit transmitPGNs whitelist audit — AIS isolation verified, not just implicit
- SH-11: Phase 1 Shadow Mode build
- Community interest confirmation (SH-1 → SH-3)

## Related

- [[entities/wiboat]] — WiBoat is the sensor layer that feeds SafeHelm contact queue
- [[entities/nmea2000-layer]] — PiCAN-M provides N2K output path for PGN 126983 alerts
- [[concepts/ais-isolation]] — mandatory before any synthetic AIS injection ships
- [[entities/pi-system]] — host platform
