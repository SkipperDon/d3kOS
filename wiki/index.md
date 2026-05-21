# Helm-OS / d3kOS Wiki Index

*AI-maintained knowledge base. Initialized S62 2026-04-17. Updated by Claude Code each session.*
*Standing scope: all files under wiki/ are permanently authorized for AI write. raw/ is human-only.*

---

## Entities
- [[entities/d3kos-platform]] · d3kOS Pi platform — architecture, services, ports, paths · seeds: MEMORY.md — updated S86
- [[entities/atmyboat-website]] · AtMyBoat.com — WordPress, HostPapa, deploy rules, Stripe webhooks · seeds: MEMORY.md — updated S86
- [[entities/tier-system]] · T0–T3 tier definitions, storage, enforcement · seeds: MEMORY.md S61
- [[entities/pi-system]] · Pi hardware (RPi 5), services map, PiCAN-M, SSH, watchdog · seeds: pi-system.md — updated S85
- [[entities/pwa]] · Progressive Web App — hosting, identity, cache, STUN · seeds: MEMORY.md — updated S86
- [[entities/safehelm]] · Collision avoidance — design only, 7-layer, port 8095, COLREGs, synthetic AIS · seeds: SAFEHELM_DESIGN.md S85
- [[entities/wiboat]] · WiFi CSI marine radar — RPi 4B, nexmon_csi, 4-antenna UCA, WS:8766 · seeds: FRD v1.2 S85
- [[entities/nmea2000-layer]] · PiCAN-M (Pi HAT) vs CX5106 (engine ADC) — critical distinction, AIS isolation · seeds: pi-system.md S85
- [[entities/d3k-lite]] · Free OpenPlotter addon concept — design only, Flask:8085, 70% d3kOS reuse · seeds: feasibility.md S85
- [[entities/signalk-forward-watch]] · npm plugin v0.2.3 — ML marine detection on Pi (YOLOv8n + ONNX worker thread) · seeds: MEMORY.md S86
- [[entities/admin-console-vm]] · CRM VM at 192.168.236.5 — Flask CRM, crm-proxy.php, pscp.exe deploy pattern · seeds: MEMORY.md S86
- [[entities/avnav]] · Chart navigation software on Pi port 8080 — SafeHelm virtual vessel display, d3k-lite integration · seeds: MEMORY.md S86
- [[entities/fix-my-pi]] · Remote diagnostic/repair service — T1+ tier, cloud_agent.py, watchdog alerts · seeds: pi-system.md S86
- [[entities/truenas-verify-agent]] · TrueNAS 192.168.1.102 — FreeBSD NAS + Verify Agent code reviewer · seeds: MEMORY.md S86
- [[entities/sail-o-vision]] · External collaboration — Jetson marine detection, nmea_client.py reusable in SafeHelm Phase 1 · seeds: project_sail_o_vision.md S86

## Concepts
- [[concepts/php-proxy-pattern]] · Flask CRM → PHP → MySQL pattern — permanent architecture · seeds: MEMORY.md
- [[concepts/two-source-sync-rule]] · d3kOS/dashboard/ + v0.9.4/pi_source/ must always stay in sync · seeds: MEMORY.md S52
- [[concepts/ais-isolation]] · 4-layer isolation preventing synthetic AIS targets reaching N2K bus/transponder · seeds: SafeHelm design S85
- [[concepts/orphan-branch-rule]] · Never push main to GitHub — orphan public-release branch only, 12 public files · seeds: MEMORY.md S86

## Sources
*(empty — add raw/ documents as ingested)*

## Syntheses
*(empty — filed as sessions produce cross-source analyses)*

## Questions
- [[questions/bug-06-pwa-tier-display]] · BUG-06: PWA tier shows T1 after BUG-04 fix — blocked pending operator confirmation
- [[questions/session-log-gap-s56-s61]] · Sessions S56–S61 have no SESSION_LOG.md entries
