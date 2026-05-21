# Entity: Fix My Pi

*Last updated: S86 2026-05-21 | Sources: pi-system.md, MEMORY.md*

---

## Identity

- **Type:** Remote diagnostic and repair service
- **Tier gate:** T1+ (Free tier T0 cannot access)
- **Pi service:** `fix_my_pi.py` at `/opt/d3kos/services/`
- **Companion:** `d3kos-cloud-agent` on Pi (receives remote commands)

---

## What It Does

Allows the owner to remotely diagnose and repair the Pi from the PWA. The Pi watchdog detects service failures, sends an alert to HostPapa, and the PWA can then trigger automated fixes (restart services, run health checks, apply OTA updates).

---

## Pi-Side Components

### REQUIRED_SERVICES (updated S61)

The Fix My Pi service monitor watches exactly three services:
- `d3kos-cloud-agent` — receives remote commands; **do not stop this** when testing FMP
- `d3kos-export-manager` — safe to stop for FMP demo/testing
- `d3kos-tier` — tier enforcement service

### Watchdog

Cron every 5 minutes. On service failure → sends alert to `watchdog-alert.php` on HostPapa. `d3kos-ai-bridge.service` is in CRITICAL_SERVICES (auto_restart=True, added S20).

### cloud-config.json

`amboat_base_url` = `https://atmyboat.com` (updated S61 from `/staging`). All 6 `pi_source` fallback defaults also updated.

---

## cloud_agent.py Events

Handles inbound commands from HostPapa:

| Event | Action |
|-------|--------|
| `pair_confirmed` | Writes device pairing to license.json |
| `tier_change` | Normalises to string "T0"–"T3", writes license.json |
| `fleet_assign` | Writes fleet.json, restarts d3kos-fleet-push.service |
| `fleet_unassign` | Removes fleet.json |

---

## HostPapa Side

- `watchdog-alert.php` — receives failure alerts from Pi watchdog
- Stripe webhook: `STRIPE_WEBHOOK_SECRET` constant in `inc/atmyboat-config.php` (fixed S74 — was pointing to staging)

---

## OTA Flow

Pi → watchdog alert → HostPapa → PWA notification → operator triggers fix → cloud_agent receives command → executes repair → reports result back to PWA.

---

## Related

- [[entities/pwa]] — the phone-side interface for Fix My Pi
- [[entities/pi-system]] — watchdog runs on Pi, cloud_agent.py on Pi
- [[entities/atmyboat-website]] — HostPapa hosts the PHP side
- [[entities/tier-system]] — T1+ required
