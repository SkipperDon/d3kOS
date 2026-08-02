# `/var/lib/avnav/avnav_server.xml` — version-controlled reference

**Added to the canonical tree S117 2026-08-02.** Until then this file existed only on Pi SD cards
and was the third known Pi-only config — a rebuild from the repo would have silently reverted every
fix in it.

**Source of this copy:** the lab Pi `192.168.1.237`, pulled 2026-08-02.
`md5 44230c86550839f7e08e113e6c720037`, byte-identical to the Pi at the time of capture.

---

## ⚠ THIS IS A REFERENCE BASELINE, NOT A DEPLOYABLE ARTEFACT

**Do not copy this file onto another Pi wholesale.** It contains per-machine values that are wrong
on any other machine. Treat it as the record of *which settings must exist*, and apply the portable
ones deliberately.

### Portable — must exist on every d3kOS Pi

| Setting | Line | Why |
|---|---|---|
| `fetchAis="true"` on `<AVNSignalKHandler>` | 65 | **The entire BUG-19 + BUG-20 fix.** AvNav's `fetchAis` defaults to **False** (`signalkhandler.py:663`). Without this attribute `aisFetchPeriod=0` and `fetchAisData()` is never called — AvNav shows `ais INACTIVE disabled` while its Signal K connection looks perfectly healthy. Both AIS targets and camera hazard detections reach the map through this one path. |
| `aisQueryPeriod="5"` on `<AVNSignalKHandler>` | 65 | Companion to the above. Chosen S115 as a reasonable value, **not a measured optimum.** |
| `decodeData="true"`, `port="8099"` | 65 | AvNav takes GPS from Signal K rather than a serial device. |

### Machine-specific — DO NOT copy between Pis

| Setting | Why it must not be copied |
|---|---|
| `uuid="…"` on `<AVNSignalKHandler>` | Per-installation identity. Duplicating identities across Pis is the BUG-39 defect class. |
| Any `<UsbDevice usbid="…">` rule | **`usbid` is a physical USB port path, not a device identity.** Verified S117: `1-1.4:1.0` is the **u-blox GPS on the boat** and the **GEMBIRD SD card reader on the lab Pi**. The same string means different hardware on different machines. Copying a usbid rule between Pis targets whatever happens to be plugged into that port. |

---

## Known divergence between the boat and the lab — UNRESOLVED

| Setting | Lab Pi | Boat Pi |
|---|---|---|
| `fetchAis="true" aisQueryPeriod="5"` | **present** (added S115) | **absent** — never deployed |
| `<UsbDevice usbid="1-1.4:1.0" type="ignore"/>` | **absent** | **applied S96 — but not seen since** |

**The boat's copy of this file has never been read.** S109 recorded this explicitly: *"The boat's
`avnav_server.xml` has never been inspected — its u-blox rule state is inference, not fact."* The
boat Pi is not reachable from the lab network (boat hotspot only, `172.20.10.8`), so the two cannot
be reconciled from here.

**The S96 u-blox rule was verified applied and surviving reboot on 2026-07-11**
(`STATUS[1-1.4:1.0] INACTIVE, /dev/ttyACM0 configured to be ignored`). Whether it is still there is
unknown — **a clone of the lab card onto the boat would erase it**, which is why
`deployment/docs/runbooks/HAIKU_ONBOAT_VALIDATION.md` Phase 2 checks for it and re-applies if
missing.

**What that rule fixed (S96):** `AVNUsbSerialReader` repeatedly reopening `/dev/ttyACM0` at every
baud rate while gpsd held the port exclusively for Signal K — a perpetual error loop that flooded
the logs and made AvNav *appear* broken. AvNav was never actually down. Do not re-diagnose this.

---

## Reconciling the two Pis — requires a boat visit

1. Read the boat's file: `ssh d3kos@172.20.10.8 'cat /var/lib/avnav/avnav_server.xml'`
2. Diff it against this baseline; record any boat-only settings **here**, in this README.
3. Apply the **portable** settings the boat is missing — currently `fetchAis` / `aisQueryPeriod`.
4. Confirm the boat's u-blox rule still matches the port its GPS is actually plugged into —
   re-derive the usbid on the boat, do not assume `1-1.4:1.0`.
5. Re-capture the boat's file into this directory as `avnav_server.xml.boat` so both machines are
   on record.
