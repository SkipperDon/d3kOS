# AD2 — Architecture: Data Flow
**Version:** v1.0.0
**Date:** 2026-04-02
**Project:** AtMyBoat.com / d3kOS

---

## Summary

This document describes the data pipeline between the Raspberry Pi (d3kOS), the HostPapa PHP backend, and the PWA frontend. It covers the scheduled 30-minute export cycle, alert-triggered immediate exports, the PWA read path, and the Node-RED telemetry/community flows that are built but disabled pending Phase 4 activation.

---

## Primary Export Pipeline — Pi → HostPapa → PWA

```
  RASPBERRY PI                    HOSTPAPA                      PWA
  ============                    ========                      ===

  [Signal K :8099]
  [Flask sensors]
  [Camera :8084]
        |
        | (reads sensor state)
        v
  [export_worker.py]
  (runs every 30min via         POST /mobile/data-ingress.php
   systemd timer)  ─────────────────────────────────────>  [data-ingress.php]
                                 Headers:                        |
                                 AMBOAT_API_KEY                  | writes to DB:
                                 device_token (UUID)             |   amboat_engine_snapshots
                                                                 |   amboat_alerts
                                                                 |   amboat_boatlog
                                                                 |
                                                                 | updates wp_usermeta:
                                                                 |   last_sync  (timestamp)
                                                                 |   position   (lat/lon)
                                                                 |
                                 <── HTTP 200 + JSON ────────────+
                                     includes: tier, commands    |
                                                                 |
  [export_worker reads                                           |
   tier from response]                                           |
  [license.json updated                                          |
   if tier changed]                                              |
                                                                 |
                                                           [PWA / app.js]
                                 GET /mobile/dashboard-data.php
                                 Header: app_token         <─────────────────
                                                                 |
                                 <── JSON response ─────────────>
                                     synced_at
                                     position (lat/lon)
                                     engine_snapshot (latest)
                                     alerts (recent, unread)
                                     boatlog (recent entries)
```

---

## Alert-Triggered Immediate Export

Alerts do not wait for the 30-minute timer. The alert_watcher service detects alert events and immediately calls export_worker logic to push the alert upstream.

```
  RASPBERRY PI                    HOSTPAPA
  ============                    ========

  [Any source: Signal K,
   camera, Fish Detector,
   Flask sensor threshold]
        |
        | (event detected)
        v
  [alert_watcher.py]
        |
        | immediately triggers
        | (does not wait for
        |  30-min timer)
        v
  [export_worker — alert
   export path]  ──────────────> POST /mobile/data-ingress.php
                                  payload: alert record only
                                  (not full telemetry snapshot)
                                       |
                                       | writes to: amboat_alerts
                                       | sets: alert_sent = 1
                                       |
                                 <── HTTP 200 ───────────────────
```

---

## Command Delivery Pipeline — HostPapa → Pi

Commands flow from PWA → HostPapa queue → Pi polling.

```
  PWA                         HOSTPAPA                    RASPBERRY PI
  ===                         ========                    ============

  [app.js submits
   command (e.g. FMP,
   reboot, config)]
        |
        v
  POST /mobile/app-command.php
  Header: app_token ─────────> [app-command.php]
                                    |
                                    | writes to:
                                    | amboat_command_queue
                                    | status = 'pending'
                                    |
                               <── command_id ──────────

  (PWA begins polling
   app-command.php with
   command_id for result)

                               [command-queue.php]
                                    ^
                                    | GET every 30 seconds
                                    | Header: AMBOAT_API_KEY
                                    | + device_token
  [cloud_agent.py]  ───────────────+
        |
        | (receives pending commands)
        v
  [Executes command:
   fix_my_pi.py,
   restart service,
   config update, etc.]
        |
        | POST ACK + result
        v
  POST /mobile/app-command.php
  action=ack  ───────────────> [app-command.php]
                                    |
                                    | updates command record:
                                    | status = 'complete'
                                    | result = payload
                                    |
                               [PWA polls receive result]
```

---

## Database Tables Written by data-ingress.php

| Table | Written By | Key Fields | Retention |
|---|---|---|---|
| amboat_engine_snapshots | export_worker (30min) | device_token, rpm, temp, voltage, snapshot_at | Rolling window (configurable) |
| amboat_alerts | alert_watcher (immediate) + export_worker | device_token, alert_type, severity, alert_at, sent | Until acknowledged |
| amboat_boatlog | export_worker (30min) | device_token, log_entry, logged_at | Persistent |
| amboat_command_queue | app-command.php | device_token, command, status, created_at, ack_at | Until ACKed + cleanup |
| wp_usermeta: last_sync | data-ingress.php | meta_key=atmyboat_last_sync | Overwritten each sync |
| wp_usermeta: position | data-ingress.php | meta_key=atmyboat_position | Overwritten each sync |
| wp_usermeta: atmyboat_tier | stripe-webhook.php | meta_key=atmyboat_tier | Overwritten on tier change |

---

## Tier Sync Path (Pi License Update)

```
  STRIPE               HOSTPAPA                  RASPBERRY PI
  ======               ========                  ============

  [Payment event:
   subscription start,
   upgrade, cancel]
        |
        v
  POST webhook ──────> [stripe-webhook.php]
                            |
                            | updates wp_usermeta:
                            | atmyboat_tier = T2/T3/T0
                            |

                                              (next 30min export cycle)
                       [data-ingress.php]  <── POST export_worker
                            |
                            | response includes:
                            | { "tier": "T2" }
                            |
                       ──────────────────> [export_worker reads response]
                                                  |
                                                  v
                                           [license.json updated]
                                           [tier_service re-reads]
```

---

## Node-RED Flows — Disabled Until Phase 4

These flows are present in Node-RED (:1880) but all output nodes are disabled.

```
  NODE-RED (Pi :1880)             HOSTPAPA ENDPOINTS
  ===================             ==================

  [telemetry/push flow]   ──X──>  telemetry/push.php      (DISABLED)
  [community/position]    ──X──>  community/position.php  (DISABLED)
  [community/benchmark]   ──X──>  community/benchmark.php (DISABLED)
  [community/markers]     ──X──>  community/markers.php   (DISABLED)

  X = output node disabled in Node-RED editor
```

Activation procedure for Phase 4: enable output nodes in Node-RED editor, verify HostPapa endpoints are accepting, test end-to-end before enabling community map in PWA.

---

## Notes

- `export_worker.py` is the only service that writes to data-ingress.php for regular telemetry. It is distinct from cloud_agent (which only reads command-queue.php) and alert_watcher (which triggers alert-only exports).
- Pi identity in all HostPapa calls is the `device_token` UUID from `/opt/d3kos/config/device-token.json`. The `installation_id` hex from `license.json` is NOT used for HostPapa calls. Mixing these up is a confirmed critical bug pattern (see MEMORY.md).
- The `data-ingress.php` response is the authoritative source for tier updates to the Pi. The Pi does not call a separate tier endpoint.
- Alert exports use the same data-ingress.php endpoint but with a reduced payload (alert record only, not full engine snapshot).
- Position data in wp_usermeta is a simple lat/lon — it is not stored historically. Only the last known position is kept.
