# d3kOS Export Boot Race Condition Fix

**Service:** `d3kos-export-boot.service`
**Script:** `/opt/d3kos/scripts/export-on-boot.sh`
**Fixed:** 2026-03-11 (Session Part 22)
**Status before fix:** FAILED since 2026-03-04

---

## Symptom

`d3kos-export-boot.service` showed `failed (Result: exit-code)` with `status=7/NOTRUNNING` after every boot. Journal stopped at "✓ Network available" — no further log output.

## Root Cause

Two bugs combined to kill the script on every boot:

### 1. Boot race condition

`d3kos-export-boot.service` and `d3kos-export-manager.service` both start at the same systemd target. The export-boot script checked `systemctl is-active d3kos-export-manager.service` — this returns active (exit 0) as soon as the Python process starts. However, the Flask server inside export-manager takes ~2 seconds to bind to port 8094. The script ran `curl http://localhost:8094/...` before the port was open.

Timeline on 2026-03-04 boot:
```
15:16:26  export-manager process starts (systemd: active)
15:16:26  export-boot starts
15:16:27  export-boot: network available — immediately curls port 8094
15:16:27  curl: connection refused (port not yet bound) → exit code 7
15:16:29  export-manager: Flask bound to port 8094 ← 2 seconds too late
```

### 2. `set -e` with unguarded curl

The script opened with `set -e`. curl exit code 7 (`CURLE_COULDNT_CONNECT`) propagated directly to systemd as the script exit code. Systemd decoded this as `status=7/NOTRUNNING` and marked the service failed.

---

## Fix — `/opt/d3kos/scripts/export-on-boot.sh`

| Change | Before | After |
|--------|--------|-------|
| `set -e` | Present — any failure kills script | Removed |
| Port check | `systemctl is-active` (process exists, not port-ready) | `nc -z localhost 8094` retry loop — 10 × 3s = 30s max |
| Port not ready | Script dies on curl | Log warning + `exit 0` (clean) |
| `curl` failure | Kills script | `curl --max-time 5 ... \|\| echo '{}'` |
| `jq` failure | Kills script | `jq ... \|\| echo '0'` |

### Port-ready loop (key addition)

```bash
PORT_READY=0
for i in {1..10}; do
    if nc -z localhost 8094 2>/dev/null; then
        log "✓ Export manager port ready"
        PORT_READY=1
        break
    fi
    sleep 3
done

if [ "$PORT_READY" -eq 0 ]; then
    log "✗ Export manager port 8094 not ready after 30s — skipping queue check"
    exit 0
fi
```

---

## Verification

After deploying the fix:
```
sudo systemctl reset-failed d3kos-export-boot.service
sudo systemctl start d3kos-export-boot.service
```

Result:
```
Active: active (exited) — status=0/SUCCESS
[09:39:44] ✓ Network available
[09:39:44] Waiting for export manager port 8094...
[09:39:44] ✓ Export manager port ready
[09:39:44] Queue status: 0 pending exports
[09:39:44] No pending exports
[09:39:44] === Boot-time upload complete ===
```

---

## Note on Previous Fix Attempt

An earlier session (Part 12, 2026-03-05) added a retry loop and marked the item done in `PROJECT_CHECKLIST.md`. That fix did not resolve the issue because it targeted `export-daily.sh`, not the actual race in `export-on-boot.sh`, and did not address the `set -e` + curl interaction. The service remained FAILED until the 2026-03-11 fix.
