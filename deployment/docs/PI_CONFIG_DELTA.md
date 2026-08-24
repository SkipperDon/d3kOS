# Per-Pi Configuration Delta Record

**Last updated:** 2026-08-24 (S133)
**Purpose:** Documents configuration that legitimately differs between the lab Pi
(192.168.1.237) and the boat Pi (172.20.10.8). These files are NOT byte-compared by
`tools/release-state.sh` — invariants are asserted instead of hashes.

---

## 1. `/var/lib/avnav/avnav_server.xml`

**Template:** `deployment/v0.9.9.4/var/lib/avnav/avnav_server.xml.template`
**Invariant asserted by release-state.sh:** `fetchAis="true"` AND `aisQueryPeriod="5"` must be present on every Pi (BUG-19/20 fix).

### Lab Pi (192.168.1.237) — baseline

No u-blox USB GPS ignore rule. The lab has no u-blox hardware, so AvNav's
auto-detect is harmless.

### Boat Pi (172.20.10.8) — additional rule required

Inside `<AVNUsbSerialReader>` the boat Pi has:

```xml
<UsbDevice usbid="1-1.4:1.0" type="ignore"/>
```

**Why:** SignalK owns the u-blox GPS (usbid `1-1.4:1.0`). Without this ignore rule,
AvNav also claims the device, causing serial contention and GPS data loss. This is the
boat-specific regression logged in MEMORY.md ("u-blox ignore rule absent on lab card").

**How to verify on boat Pi:**

```bash
grep -o 'usbid="[^"]*" type="ignore"' /var/lib/avnav/avnav_server.xml
```

Expected: `usbid="1-1.4:1.0" type="ignore"` (plus any other ignored devices).

---

## 2. `/opt/d3kos/services/fleet/config/fleet-push.env`

**Template:** `deployment/v0.9.9.4/opt/d3kos/services/fleet/config/fleet-push.env.template`
**Excluded from verifier:** `release-state.sh` excludes `/config/.*\.env$` from EXTRA_ON_PI
(per-Pi secret, never committed).

### Both Pis — same values except AMBOAT_API_KEY

| Variable | Value | Notes |
|---|---|---|
| `FLEET_INGEST_URL` | `https://atmyboat.com/...fleet-ingest.php` | Same on all Pis |
| `AMBOAT_API_KEY` | **set per-Pi** | Production key — never committed; rotate on compromise |
| `SIGNALK_URL` | `http://localhost:8099` | Same on all Pis |
| `PREDICTIVE_STATUS_URL` | `http://localhost:8106/predictive/status` | Same on all Pis |
| `PUSH_INTERVAL_S` | `60` | Same on all Pis |
| `FLEET_PUSH_PORT` | `8108` | Same on all Pis |

**To set up on a new Pi:**

```bash
cp /opt/d3kos/services/fleet/config/fleet-push.env.template \
   /opt/d3kos/services/fleet/config/fleet-push.env
# Edit and set AMBOAT_API_KEY to the real production key
nano /opt/d3kos/services/fleet/config/fleet-push.env
```

---

## Invariant Verification

Run `tools/release-state.sh` — it will:
1. Byte-compare all canonical-tree files EXCEPT `.template` files
2. Assert `fetchAis="true"` and `aisQueryPeriod="5"` are present in the Pi's live
   `avnav_server.xml` regardless of other differences in that file
