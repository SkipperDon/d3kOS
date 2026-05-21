# Entity: Pi System

*Last updated: S85 2026-05-20 | Sources: MEMORY.md, pi-system.md — S85: PiCAN-M added, N2K hardware section added*

---

## Hardware

- **Model:** Raspberry Pi 5
- **IP:** 192.168.1.237
- **User:** d3kos
- **SSH key:** `~/.ssh/id_d3kos`
- **OS:** Raspberry Pi OS (labwc Wayland compositor)
- **RAM:** 8GB
- **CAN bus HAT:** PiCAN-M — provides `can0`, the Pi's physical connection to the NMEA 2000 backbone

## NMEA 2000

See [[entities/nmea2000-layer]] for full detail. Short version:
- **PiCAN-M** = the Pi's N2K interface (GPIO HAT → can0)
- **CX5106** = separate engine ADC device ON the N2K bus (not the Pi's interface)
- Signal K reads all N2K traffic via canboat-js on can0

## Systemd Services

| Service | Description | Notes |
|---------|-------------|-------|
| d3kos-ai-bridge | AI bridge TTS/SSE | Enabled on boot S20; mute state persisted to tts-mute.json |
| d3kos-voice-assistant | Voice assistant hybrid | |
| d3kos-agents | AA1–AA6 autonomous agents | |
| d3kos-failure-reporter | Failure intelligence FI1 | Port 8109 NOT 8106 |
| d3kos-gemini-proxy | Gemini proxy | Port 3001 |
| d3kos-fleet-push | Fleet push service | Restarted by cloud_agent on fleet commands |

## Watchdog

- `d3kos_watchdog.py` — cron every 5 min, 10 services, auto-restart
- Sends cloud alert to `watchdog-alert.php` on HostPapa on failure
- `d3kos-ai-bridge.service` in CRITICAL_SERVICES with auto_restart=True (added S20)
- Fix My Pi REQUIRED_SERVICES list updated S61

## Key Fixes (BUG log)

| Bug | Status | Fix |
|-----|--------|-----|
| BUG-01 | RESOLVED S44 | ALSA hardware mute `amixer -c S330 cset numid=2 off/on` + tts-mute.json |
| BUG-02 | RESOLVED S44 | `pdf_processor` import moved inside `__init__` — voice queries 9.6s → 0.6s |
| BUG-03 | RESOLVED S44 | `_prewarm_recognizer()` pre-creates KaldiRecognizer at startup — eliminates ~2s silence |
| BUG-04 | RESOLVED S61 | Tier stored as "T0"–"T3" strings, not integers |

## Audio

- S330 USB speaker — raw device `hw:1,0` rejects 22050Hz; must use PulseAudio default or `plughw:S330,0` via aplay
- Piper TTS confirmed working (Amy female voice). `communicate(timeout=20)` removed — Pi load caused espeak fallback
- BUG-01: ALSA mute combined with tts-mute.json. Mute survives restarts (ai_bridge reads on startup)

## RAG / Ollama

- Ollama disabled at boot — started on-demand only
- Model: `gemma3:1b` (815MB) — phi3.5 OOM under full stack
- `nomic-embed-text` for query embedding
- ChromaDB path: `/opt/d3kos/data/vector-db/` (NOT /home/d3kos/.cache/chroma/)
- Corpus: 2146 docs — D3KOS_USER_MANUAL_v0992.md (78 chunks + 137 re-ingested S55), Ontario Regulation 2026.pdf, global_marine_emergency_contacts.pdf, MNR.pdf

## Sudoers

- `/etc/sudoers.d/d3kos-chpasswd` — NOPASSWD chpasswd (password change flow)
- `/etc/sudoers.d/d3kos` — NOPASSWD systemctl restart/stop d3kos-fleet-push.service

## Cloud Agent

- `cloud_agent.py` handles: pair_confirmed, tier_change, fleet_assign, fleet_unassign
- `handle_tier_change` — normalises to string "T0"–"T3" before writing license.json (fixed S27c)
- Fleet assign: writes `/opt/d3kos/config/fleet.json`, restarts d3kos-fleet-push.service
- Cloud config URL updated S61

## Signal K

- v2.23.0 on port 8099
- PGN 127488: revolutions + boostPressure on can0.64
- PGN 127489: oil pressure + coolant temp (only when engine running)
- Fuel/battery: NOT wired to NMEA 2000

## Related

- [[entities/d3kos-platform]] — services, ports, directory layout
- [[entities/pwa]] — mobile companion app
- [[entities/tier-system]] — license.json tier storage
