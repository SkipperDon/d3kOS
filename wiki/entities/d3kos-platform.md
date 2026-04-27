# Entity: d3kOS Platform

*Last updated: S62 2026-04-17 | Sources: MEMORY.md, pi-system.md*

---

## Identity

- **Product:** d3kOS — marine navigation dashboard for recreational boaters
- **Pi IP:** 192.168.1.237
- **Pi user:** d3kos
- **SSH key:** `~/.ssh/id_d3kos`
- **Current version:** v0.9.9 (pre-launch; v1.0 gated on v0.9.9 security audit)

## Directory Layout (Pi)

| Path | Purpose |
|------|---------|
| `/opt/d3kos/services/` | All Python services |
| `/opt/d3kos/config/` | Runtime config (json files) |
| `/opt/d3kos/data/` | User data — preserved through rollbacks |
| `/var/www/html/` | Static pages (served by nginx) |

## Two Source Directories (CRITICAL)

`deployment/d3kOS/dashboard/` and `deployment/v0.9.4/pi_source/` are BOTH authoritative sources for the Pi. Any new file added to one MUST be added to the other and deployed to Pi. Violation discovered S52 (Anchor Watch + Manual pages missing from d3kOS/dashboard/ since S39b/S41).

See [[concepts/two-source-sync-rule]].

## Key Services and Ports

| Service | Port | Notes |
|---------|------|-------|
| Flask dashboard | :3000 | nginx proxies all / to this |
| Gemini proxy | :3001 | |
| AI bridge | :3002 | TTS, SSE alerts, mute state |
| Preferences API | :8107 | units metric/imperial |
| Remote API | :8111 | |
| Camera stream | :8084 | |
| Fish detector | :8086 | |
| Failure reporter | :8109 | NOT :8106 (taken by predictive_maintenance) |
| Signal K | :8099 | v2.23.0 |
| AvNav | :8080 | |
| Voice assistant | systemd | d3kos-voice-assistant.service |

## nginx

Static CSS/assets require explicit nginx location block — without it they fall through to Flask and 404. Block was added S27c; must be re-added if nginx config is ever rebuilt.

## Chromium Launcher

`launch-d3kos.sh` is the real launcher (waits for Flask :3000, then opens `http://localhost/`). `d3kos-browser.desktop` was disabled (Hidden=true) in S55b — two instances were running. Single instance confirmed.

## Decisions

- **Title bar color:** labwc renders title bar via `~/.config/labwc/themerc-override`. `<meta name="theme-color">` does NOT affect it. Fix via `window.active.label.text.color` — not yet applied.
- **Ollama:** disabled on Pi; started on-demand only for RAG. gemma3:1b (815MB) chosen over phi3.5 (OOM under full stack).

## Related

- [[entities/pi-system]] — hardware and service details
- [[entities/pwa]] — mobile companion app
- [[concepts/two-source-sync-rule]]
