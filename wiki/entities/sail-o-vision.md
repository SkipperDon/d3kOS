# Entity: sail-o-vision (External Collaboration)

*Last updated: S86 2026-05-21 | Sources: project_sail_o_vision.md, S84 assessment*

---

## Identity

- **Repo:** https://github.com/adam-gol/sail-o-vision (MIT licence)
- **Author:** adamgoldberg (1 contributor)
- **Forum:** Cruiser forum — "Request: Video captured 'at sea' for non-cloud AI recognition system"
- **Type:** External project — not part of d3kOS, potential collaboration

---

## What It Does

Marine vision detection system running on Jetson Orin Nano Super (~$150 hardware). Detects vessels using YOLOv8l + TensorRT at 21 FPS. Includes AIS + radar TTM NMEA parsing and a 4-tier contact priority system.

---

## Production-Ready Components

| Component | Status |
|-----------|--------|
| YOLOv8l + TensorRT, 21 FPS on Jetson | Production-ready |
| NMEA 0183 multi-threaded parser: AIS (pyais) + radar TTM (pynmea2) | Production-ready |
| Own-vessel state, 120s contact expiry, thread-safe | Production-ready |
| MVTD maritime dataset: 98.5% detection, 0 false positives | Validated |
| 4-tier contact priority system | Complete |

## Not Yet Connected to Hardware (same stage as d3kOS)

- ONVIF PTZ control — state machine in `simulate_operations.py` is complete simulation, no real M300C yet
- NMEA 2000 alert PGN injection
- Chartplotter integration

---

## Key Asset for SafeHelm Phase 1

**`nmea_client.py` (443 lines)** — radar TTM parser that SafeHelm currently lacks. Thread-safe, handles multi-sentence AIS, 120s contact expiry. **Directly reusable when SafeHelm Phase 1 begins** — review before writing a new NMEA parser.

---

## Proposed Integration Architecture

- sail-o-vision runs standalone on Jetson (GPU inference + PTZ — adam's hardware)
- Outputs contacts via NMEA UDP or synthetic AIS
- SafeHelm ingests those contacts same as AIS targets
- No merged codebases, no shared release cycle

---

## GitHub Discussion (S84/S85)

Don opened GitHub Discussion #3 (May 19). adam-gol replied May 20 with ONVIF PTZ architecture. Don posted a reply (drafted S85) covering AIS isolation layers, PGN 126983 Axiom behaviour, and ONVIF PTZ feedback. Reply written in natural human voice; adam-gol's reply appeared AI-written.

---

## 8 Questions Prepared (S84)

Hardware & timeline, what's running today, architecture intent, collaboration fit. Key unknowns: M300C in hand or planned? `nmea_client.py` tested live? Alert routing mechanism? Who is the WhatsApp implementer?

---

## Related

- [[entities/safehelm]] — SafeHelm Phase 1: review nmea_client.py before writing NMEA parser; discuss PTZ handoff before designing it
- [[entities/wiboat]] — complementary detection layer; different physics (WiFi CSI vs optical)
