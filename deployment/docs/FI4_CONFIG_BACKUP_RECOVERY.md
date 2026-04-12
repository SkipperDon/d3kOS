# FI4 — Config Backup and Recovery
**Version:** 1.0.0
**Status:** Design complete — implementation pending
**Tier gate:** T1, T2, T3 only. T0 has no account and no cloud connection — not applicable.
**Document date:** 2026-04-12

---

## 1. Purpose

FI4 solves a specific problem: when a Pi's SD card dies or is wiped, the user loses all their
configuration — vessel name, preferences, camera slots, tier assignment, cloud connection
credentials, and device identity. Without recovery, they must start from scratch, re-enter
everything, and re-pair their device as if it were a new installation.

FI4 backs up the Pi's config to HostPapa automatically on a daily schedule. If the Pi needs
to be reflashed, the user selects "Recover Existing Pi" in the setup wizard, enters their
Recovery Key, and the full config is restored within 60 seconds.

---

## 2. Scope

**Included in backup:**

| File | Purpose |
|---|---|
| `cloud-config.json` | HostPapa URL, amboat_api_key, TURN credentials |
| `device-token.json` | Device UUID — identity on HostPapa |
| `license.json` | Tier, features, installation_id |
| `user-preferences.json` | Vessel name, units, language, timezone, alert types |
| `ai-config.json` | AI provider and model settings |
| `slots.json` | Camera position assignments |
| `hardware.json` | Discovered hardware config |
| `fleet.json` | Fleet assignment (T3) |
| `community-prefs.json` | Community preferences |
| `onboarding.json` | Onboarding completion state |
| `timezone.txt` | Timezone string |
| `tts-mute.json` | TTS mute state |

**Total backup size per Pi:** approximately 4–5 KB.

**Excluded from backup:**

| What | Why |
|---|---|
| `api-keys.json` | Contains user's personal Gemini API key — not stored server-side. User re-enters after recovery (one-time, ~30 seconds). |
| `engine_history.db` | Too large. Voyage data is kept in HostPapa exports, not on the Pi. |
| ChromaDB / RAG data | Re-ingested from manual PDF after recovery. |
| Log files | Not needed for recovery. |

---

## 3. Recovery Key

The Recovery Key is the Pi's `device_token` UUID — a 36-character identifier generated at
first pairing and stored in `device-token.json`.

Example: `701e5754-e2ce-4fa3-97a6-f2c7c7e020c6`

**Where to find it:**
- **d3kOS Settings page** → System section → "Recovery Key" with Copy button
- **d3kOS mobile app** → Settings → Device Info → Recovery Key
- **Email** — sent to the user's registered email address at first pairing
- **Physical label** — user is recommended to write it on a label stuck to the Pi case

T0 users do not have a Recovery Key. FI4 does not apply to T0.

---

## 4. Architecture

```
Pi (running)
  cloud_agent.py
    push_config_snapshot()
        │
        │  POST /mobile/config-backup.php
        │  X-Device-Token: {device_token}
        │  X-Api-Key: {amboat_api_key}
        │  Body: {config_json: "{...all config files...}"}
        ↓
HostPapa MySQL
  amboat_config_packages
  (device_token, config_json, created_at, updated_at)
        │
        │  GET /mobile/config-restore.php?token={device_token}
        │  (no auth required beyond knowing the token)
        ↓
Pi (fresh / reflash)
  setup.html — Recovery mode
    write all config files to /opt/d3kos/config/
    restart services
    redirect to dashboard
```

---

## 5. Backup Triggers

Config snapshot is pushed to HostPapa automatically on:

1. **Daily cloud sync** — `cloud_agent.py` calls `push_config_snapshot()` on every sync
   cycle (default every 30 seconds, but snapshot is only pushed if config has changed since
   last push — checked via hash comparison).
2. **Post-pair** — immediately after `pair_confirmed` handler completes.
3. **Fix My Pi trigger** — when a Fix My Pi command is received, snapshot is pushed before
   diagnostics run (ensures HostPapa has the latest state before any repair actions).
4. **Manual** — future: "Backup Now" button in app Settings.

---

## 6. Recovery Paths

### Path 1 — App available, internet available (most common)

1. User flashes fresh d3kOS SD card → Pi boots → setup wizard loads
2. User opens d3kOS app → taps **Restore Existing Pi**
3. App shows list of previously paired Pis (stored in PWA local storage)
4. User selects their Pi
5. App sends `device_token` to setup wizard (QR code scan or local LAN POST)
6. Setup wizard calls `config-restore.php` → receives full config package
7. Pi writes all config files → restarts services → dashboard loads
8. **Time to restore: under 2 minutes**
9. One manual step: re-enter Gemini API key in Settings

### Path 2 — No app, internet available

1. Fresh Pi → setup wizard → user taps **Recover Existing Pi**
2. Wizard prompts: "Enter your Recovery Key"
3. User types the 36-character device token UUID
4. Wizard calls `config-restore.php` with that token
5. Config restored → same result as Path 1
6. **Time to restore: under 3 minutes**

### Path 3 — No internet, app available (marina with no connectivity)

1. Fresh Pi → wizard loads → user opens app
2. App has a **cached copy** of the last config snapshot in PWA local storage
   (updated every time the app successfully syncs)
3. App pushes config directly to Pi over local WiFi
   (Pi setup wizard exposes a local recovery endpoint during wizard mode)
4. Config restored without HostPapa
5. **Time to restore: under 2 minutes, no internet required**

### Failure case

No internet + no app + no recovery key written down anywhere. In this scenario:
- Option A (this feature) cannot restore
- Option B (SD partition) also cannot restore if the original card is physically destroyed
- Both approaches fail identically when all three are unavailable simultaneously

Mitigation: the app being the recovery key holder means this only fails if both the
phone AND internet are simultaneously unavailable AND the user has no written key.

---

## 7. Security Model

**Backup endpoint (`config-backup.php`):**
- Requires both `X-Device-Token` and `X-Api-Key` (amboat_api_key)
- Only the Pi can push its own backup — it has both credentials
- Pi identity is validated against `wpax_usermeta` (device token must exist in DB)
- Config stored as TEXT in `amboat_config_packages` — not encrypted at rest
- Acceptable because HostPapa already holds the amboat_api_key and device_token; the
  backup contains no information not already known to HostPapa

**Restore endpoint (`config-restore.php`):**
- Requires only the `device_token` (passed as query parameter)
- No additional auth — the token is long (36 chars, UUID) and not guessable
- Rate-limited to 5 restore attempts per token per hour (prevent enumeration)
- Returns 404 if no backup exists for the token (does not confirm token existence)

**What is NOT stored:**
- `api-keys.json` — contains user's personal Gemini API key
- Any passwords
- SSH keys or certificates

---

## 8. Database Schema

```sql
CREATE TABLE IF NOT EXISTS amboat_config_packages (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    device_token    VARCHAR(64)  NOT NULL,
    config_json     MEDIUMTEXT   NOT NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_device_token (device_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

One row per Pi. UPSERT on save (INSERT ... ON DUPLICATE KEY UPDATE).
Table auto-created by `config-backup.php` on first call.

---

## 9. File Index

### HostPapa PHP (deploy to `mobile/`)

| File | Purpose |
|---|---|
| `mobile/config-backup.php` | POST — receive and store config snapshot from Pi |
| `mobile/config-restore.php` | GET — return config snapshot by device_token |

### Pi source files

| File | Change |
|---|---|
| `cloud_agent.py` | Add `push_config_snapshot()`, `restore_config_snapshot()`, call from daily sync and `pair_confirmed` handler |
| `fix_my_pi.py` | Add config snapshot push as first step of Fix My Pi run |

### Dashboard templates

| File | Change |
|---|---|
| `templates/setup.html` | Add "Recover Existing Pi" mode — recovery key input + restore call |
| `templates/settings.html` | Add Recovery Key display with Copy button (System section) |

### PWA (atmyboat.com/staging/app/)

| File | Change |
|---|---|
| `app.js` or new `recovery.js` | Store config snapshot in PWA local storage on sync; "Restore Pi" button; Path 3 local push |

---

## 10. Component Interfaces

### `config-backup.php` — request

```
POST /mobile/config-backup.php
X-Device-Token: {device_token}
X-Api-Key: {amboat_api_key}
Content-Type: application/json

{
  "config_json": "{escaped JSON string of all config files}",
  "version": "0.9.9.3",
  "checksum": "{sha256 of config_json}"
}
```

Response: `{"success": true, "updated_at": "2026-04-12T09:43:00Z"}`

### `config-restore.php` — request

```
GET /mobile/config-restore.php?token={device_token}
```

Response (success):
```json
{
  "success": true,
  "device_token": "701e5754-...",
  "config_json": "{...all config files...}",
  "version": "0.9.9.3",
  "updated_at": "2026-04-12T09:43:00Z"
}
```

Response (not found): `{"success": false, "error": "No backup found"}`

### `cloud_agent.py` — `push_config_snapshot()`

```python
CONFIG_BACKUP_FILES = [
    'cloud-config.json', 'device-token.json', 'license.json',
    'user-preferences.json', 'ai-config.json', 'slots.json',
    'hardware.json', 'fleet.json', 'community-prefs.json',
    'onboarding.json', 'timezone.txt', 'tts-mute.json',
]
```

Reads each file into a dict keyed by filename. Serialises to JSON string.
Computes SHA-256 hash. Compares to last pushed hash (stored in
`/opt/d3kos/config/config-snapshot-hash.txt`). Only POSTs if changed.

---

## 11. Known Limitations

- **T0 only:** FI4 does not apply to T0 (no account, no cloud, no pairing).
- **Gemini API key not backed up:** User must re-enter once after recovery.
- **Backup lag:** Config is backed up on sync — up to 24h behind latest state if the Pi
  crashes between syncs. In practice the Pi syncs every 30 seconds when online, so lag
  is minimal.
- **HostPapa required for Path 1/2:** If HostPapa staging/production is down, recovery
  falls back to Path 3 (app cache). If all three paths are unavailable simultaneously,
  recovery is not possible.

---

*FI4 Config Backup and Recovery — v1.0.0 — 2026-04-12*
*AtMyBoat.com — d3kOS feature documentation*
