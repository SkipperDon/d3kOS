# AD1 — Architecture: Service Map
**Version:** v1.0.0
**Date:** 2026-04-02
**Project:** AtMyBoat.com / d3kOS

---

## Summary

This document maps every running service across all three platforms: the Raspberry Pi (d3kOS), the HostPapa shared hosting backend (PHP endpoints), and the PWA frontend (GitHub Pages). It serves as a quick-reference inventory for diagnosing connectivity issues, planning deployments, and confirming service responsibilities. Services are grouped by platform. Ports are included where applicable.

---

## Platform 1 — Raspberry Pi (d3kOS)

```
+-----------------------------------------------------------------------+
|                        Raspberry Pi — d3kOS                           |
+-----------------------------------------------------------------------+
|                                                                       |
|  NAVIGATION & CHARTS                                                  |
|  +-----------------------+    +----------------------------+          |
|  | Signal K              |    | AvNav                      |          |
|  | :8099                 |    | :8080                      |          |
|  | NMEA/AIS data hub     |    | Chart plotter UI           |          |
|  +-----------------------+    +----------------------------+          |
|                                                                       |
|  WEB UI & AUTOMATION                                                  |
|  +-----------------------+    +----------------------------+          |
|  | Flask Dashboard       |    | Node-RED                   |          |
|  | :3000                 |    | :1880                      |          |
|  | d3kOS main UI         |    | Flow automation (disabled) |          |
|  +-----------------------+    +----------------------------+          |
|                                                                       |
|  AI & VOICE                                                           |
|  +-----------------------+    +----------------------------+          |
|  | Gemini Proxy          |    | Voice Assistant            |          |
|  | :8097                 |    | (no dedicated port)        |          |
|  | Helm AI assistant     |    | TTS/STT frontend           |          |
|  +-----------------------+    +----------------------------+          |
|                                                                       |
|  CAMERA & DETECTION                                                   |
|  +-----------------------+    +----------------------------+          |
|  | Camera Service        |    | Fish Detector              |          |
|  | :8084                 |    | :8086                      |          |
|  | MJPEG stream          |    | CV inference engine        |          |
|  +-----------------------+    +----------------------------+          |
|                                                                       |
|  INPUT / CONTROL                                                      |
|  +-----------------------+                                            |
|  | Keyboard API          |                                            |
|  | :8087                 |                                            |
|  | Bluetooth KB bridge   |                                            |
|  +-----------------------+                                            |
|                                                                       |
|  BACKGROUND WORKERS (no ports — system services)                     |
|  +--------------------+  +------------------+  +------------------+  |
|  | alert_watcher      |  | export_worker    |  | cloud_agent      |  |
|  | Monitors alerts,   |  | Runs every 30min |  | Polls HostPapa   |  |
|  | triggers immediate |  | POSTs telemetry  |  | every 30s for    |  |
|  | export on event    |  | to HostPapa      |  | commands         |  |
|  +--------------------+  +------------------+  +------------------+  |
|                                                                       |
|  LIVE SESSION / WEBRTC                                                |
|  +-----------------------+    +----------------------------+          |
|  | live_session          |    | tier_service               |          |
|  | :8090                 |    | (no port)                  |          |
|  | WebRTC signaling,     |    | License/tier enforcement   |          |
|  | P2P data channel      |    | reads license.json         |          |
|  +-----------------------+    +----------------------------+          |
|                                                                       |
+-----------------------------------------------------------------------+
```

### Pi Service Summary Table

| Service | Port | Type | Notes |
|---|---|---|---|
| Flask Dashboard | 3000 | HTTP | Main d3kOS UI |
| Gemini Proxy | 8097 | HTTP | AI query endpoint for voice/Helm |
| Camera Service | 8084 | HTTP | MJPEG stream |
| Fish Detector | 8086 | HTTP | CV inference |
| Keyboard API | 8087 | HTTP | Bluetooth keyboard bridge |
| Signal K | 8099 | HTTP/WS | NMEA 2000 / AIS data hub |
| AvNav | 8080 | HTTP | Chart plotter |
| Node-RED | 1880 | HTTP | Flow automation (disabled until Phase 4) |
| live_session | 8090 | WS | WebRTC signaling channel |
| alert_watcher | — | Worker | Monitors alerts, fires immediate export |
| export_worker | — | Worker | Runs every 30min, POSTs to data-ingress.php |
| cloud_agent | — | Worker | Polls command-queue.php every 30s |
| tier_service | — | Worker | License/tier enforcement, reads license.json |
| Voice Assistant | — | Worker | TTS/STT, calls Gemini Proxy |

---

## Platform 2 — HostPapa (PHP Endpoints)

All endpoints live under `atmyboat.com/wp-content/themes/twentytwenty-child/mobile/`

```
+-----------------------------------------------------------------------+
|              HostPapa — PHP API Endpoints (shared hosting)            |
+-----------------------------------------------------------------------+
|                                                                       |
|  DEVICE REGISTRATION & PAIRING                                        |
|  +------------------------+   +-------------------------+             |
|  | register-device.php    |   | pair-device.php         |             |
|  | Creates device record, |   | Links app_token to      |             |
|  | issues device_token    |   | device_token, returns   |             |
|  |                        |   | tier level              |             |
|  +------------------------+   +-------------------------+             |
|                                                                       |
|  DATA INGESTION & SYNC                                                |
|  +------------------------+   +-------------------------+             |
|  | data-ingress.php       |   | dashboard-data.php      |             |
|  | Receives Pi telemetry  |   | Returns synced engine   |             |
|  | writes snapshots,      |   | snapshot, alerts, log,  |             |
|  | alerts, boatlog        |   | position for PWA        |             |
|  +------------------------+   +-------------------------+             |
|                                                                       |
|  COMMAND QUEUE                                                        |
|  +------------------------+   +-------------------------+             |
|  | command-queue.php      |   | app-command.php         |             |
|  | Pi polls this (30s)    |   | PWA submits commands,   |             |
|  | for pending commands   |   | polls for ACK/result    |             |
|  +------------------------+   +-------------------------+             |
|                                                                       |
|  FILE & REPORT MANAGEMENT                                             |
|  +------------------------+   +-------------------------+             |
|  | file-manifest.php      |   | pdf-store.php           |             |
|  | OTA file manifest for  |   | Stores PDF reports from |             |
|  | Pi updates             |   | PWA (jsPDF generated)   |             |
|  +------------------------+   +-------------------------+             |
|  +------------------------+   +-------------------------+             |
|  | pdf-analyze.php        |   | list-reports.php        |             |
|  | Gemini AI analysis     |   | Returns list of stored  |             |
|  | of uploaded report     |   | PDF reports for PWA     |             |
|  +------------------------+   +-------------------------+             |
|                                                                       |
|  FIX MY PI (FMP)                                                      |
|  +------------------------+   +-------------------------+             |
|  | fix-my-pi-app.php      |   | fix-my-pi-billing.php   |             |
|  | App-facing FMP entry   |   | Stripe webhook for FMP  |             |
|  | point, initiates charge|   | charges, queues command |             |
|  +------------------------+   +-------------------------+             |
|                                                                       |
|  COMMUNITY (Node-RED flows — disabled until Phase 4)                 |
|  +------------------------+   +-------------------------+             |
|  | community/markers.php  |   | community/position.php  |             |
|  | Community map markers  |   | Position broadcast      |             |
|  +------------------------+   +-------------------------+             |
|  +------------------------+                                           |
|  | community/benchmark.ph |                                           |
|  | Performance benchmarks |                                           |
|  +------------------------+                                           |
|                                                                       |
|  TELEMETRY (Node-RED flows — disabled until Phase 4)                 |
|  +------------------------+                                           |
|  | telemetry/push.php     |                                           |
|  | High-freq telemetry    |                                           |
|  | ingest (future use)    |                                           |
|  +------------------------+                                           |
|                                                                       |
|  WEBRTC SUPPORT                                                       |
|  +------------------------+   +-------------------------+             |
|  | turn-credentials.php   |   | rtc-signal.php          |             |
|  | Returns Metered.ca     |   | Polling-based WebRTC    |             |
|  | TURN credentials       |   | signaling channel       |             |
|  +------------------------+   +-------------------------+             |
|                                                                       |
|  MONITORING                                                           |
|  +------------------------+                                           |
|  | watchdog-alert.php     |                                           |
|  | Receives Pi watchdog   |                                           |
|  | alerts (cron */5 min)  |                                           |
|  +------------------------+                                           |
|                                                                       |
|  WORDPRESS HOOKS (admin-ajax.php)                                    |
|  +-----------------------------------------------+                   |
|  | action=atmyboat_stripe_webhook                 |                   |
|  | Stripe subscription webhook handler            |                   |
|  | Routes to inc/stripe-webhook.php               |                   |
|  +-----------------------------------------------+                   |
|                                                                       |
+-----------------------------------------------------------------------+
```

### HostPapa Endpoint Summary Table

| Endpoint | Auth | Caller | Purpose |
|---|---|---|---|
| register-device.php | WordPress login cookie | PWA | Create device record, issue device_token |
| pair-device.php | app_token | PWA | Link app_token to device_token |
| data-ingress.php | AMBOAT_API_KEY + device_token | Pi | Receive telemetry snapshots |
| dashboard-data.php | app_token | PWA | Return synced Pi data |
| command-queue.php | AMBOAT_API_KEY + device_token | Pi | Serve pending commands to Pi |
| app-command.php | app_token | PWA | Submit commands, poll for results |
| file-manifest.php | AMBOAT_API_KEY | Pi | OTA file manifest |
| pdf-store.php | app_token | PWA | Store generated PDF reports |
| pdf-analyze.php | app_token | PWA | AI analysis of PDF |
| list-reports.php | app_token | PWA | List stored reports |
| fix-my-pi-app.php | app_token | PWA | Initiate Fix My Pi charge |
| fix-my-pi-billing.php | Stripe webhook secret | Stripe | Handle FMP payment webhook |
| community/markers.php | app_token | Node-RED / Pi | Community map markers |
| community/position.php | app_token | Node-RED / Pi | Position broadcast |
| community/benchmark.php | app_token | Node-RED / Pi | Performance benchmarks |
| telemetry/push.php | AMBOAT_API_KEY | Node-RED / Pi | High-freq telemetry (Phase 4) |
| turn-credentials.php | app_token | PWA | Generate TURN credentials |
| rtc-signal.php | app_token | PWA + Pi | WebRTC signaling |
| watchdog-alert.php | internal secret | Pi cron | Pi health alerts |
| admin-ajax.php (stripe webhook) | Stripe webhook secret | Stripe | Subscription billing events |

---

## Platform 3 — PWA (GitHub Pages)

```
+-----------------------------------------------------------------------+
|               PWA — GitHub Pages (Progressive Web App)               |
|               URL: skipper-don.github.io/atmyboat-app                |
+-----------------------------------------------------------------------+
|                                                                       |
|  CORE APPLICATION                                                     |
|  +------------------------+   +-------------------------+             |
|  | app.js                 |   | sw.js (v7)              |             |
|  | Main application logic |   | Service worker          |             |
|  | handles all UI + API   |   | Offline cache, push     |             |
|  | calls to HostPapa      |   | notification handler    |             |
|  +------------------------+   +-------------------------+             |
|                                                                       |
|  MANIFEST                                                             |
|  +------------------------+                                           |
|  | manifest.json          |                                           |
|  | PWA install config,    |                                           |
|  | icons, theme, display  |                                           |
|  +------------------------+                                           |
|                                                                       |
|  IDENTITY                                                             |
|  app_token → localStorage                                             |
|  (issued by WordPress on login, consumed by all API calls)           |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## Platform 4 — External Services

```
+-----------------------------------------------------------------------+
|                        External Services                              |
+-----------------------------------------------------------------------+
|                                                                       |
|  PAYMENTS                        AI                                   |
|  +--------------------+          +------------------------------+     |
|  | Stripe API         |          | Gemini API (Google)          |     |
|  | Subscription mgmt  |          | Pi key: ...iGIA              |     |
|  | FMP charges        |          | Website key: ...MhR0         |     |
|  | Webhooks to        |          | Shared project quota:        |     |
|  | HostPapa           |          | 1500 req/day                 |     |
|  +--------------------+          +------------------------------+     |
|                                                                       |
|  WEBRTC                                                               |
|  +--------------------+          +------------------------------+     |
|  | STUN Servers       |          | Metered.ca TURN              |     |
|  | Google:            |          | a.relay.metered.ca           |     |
|  | stun.l.google.com  |          | Fallback when STUN fails     |     |
|  | :19302             |          | (CGNAT / symmetric NAT)      |     |
|  | Cloudflare STUN    |          | Credentials per-session      |     |
|  +--------------------+          +------------------------------+     |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## Notes

- Node-RED flows are installed but disabled. The community and telemetry HostPapa endpoints exist but receive no traffic until Phase 4 is activated.
- The Pi watchdog cron runs every 5 minutes (*/5) and monitors 10 services. It calls watchdog-alert.php on HostPapa if a service fails to auto-restart.
- Both Gemini API keys share the same Google Cloud project quota (1500 req/day). Exhausting either key can affect the other service. Do not create new Google Cloud projects for Gemini without billing configured — new projects default to limit: 0.
- Ollama was removed from the workstation on 2026-04-01 and is disabled on the Pi. claude-haiku-4-5-20251001 is the current fallback AI for lightweight tasks.
- Service worker cache is pinned to v7. Any breaking PWA change requires a version bump in sw.js to force cache invalidation on client devices.
