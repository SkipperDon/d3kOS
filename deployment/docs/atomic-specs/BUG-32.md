# Atomic Spec — BUG-32 (AIS Never Reaches Signal K: Port Conflict)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-29 (S110) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-32 · `PROJECT_CHECKLIST.md` PART 17
**Severity:** HIGH — safety (no AIS targets visible on dashboard)
**Depends on:** nothing. Both files already in canonical tree (pulled from lab Pi this session).
**On-boat validation required:** yes — confirming AIVDM sentences arrive requires real AIS VHF traffic.

---

## Tier-1 finding

### Root cause (confirmed from live Pi evidence, S107 + S110)

Two faults in the SK AIS pipeline topology:

1. **Port conflict.** Signal K holds TCP 10110 as its NMEA0183 **output** server
   (a socket that sends SK's own GPS/navigation sentences to external clients).
   `rtl_ais` is configured with `-h 127.0.0.1 -P 10110`, which means it connects
   **to** 10110 as a client and writes AIS sentences into SK's outgoing output socket —
   where they are discarded.

2. **Wrong provider direction.** The SK `ais` pipedProvider is configured as a TCP
   **client** (`host: "127.0.0.1"`, `port: "10110"`) — meaning SK tries to connect to
   10110 and read from it. But 10110 is SK's own outgoing server, so SK would read its
   own GPS output back (a complete loop, not AIS data).

### Fix

**Port 10108** is free on the lab Pi (confirmed via `ss -tlnp`, S110).

Correct topology:
- SK `ais` pipedProvider → **TCP server** listening on 10108 (remove `host` → server mode)
- `rtl_ais` → TCP client pushing to 127.0.0.1:10108 (change `-P 10110` → `-P 10108`)
- Boot order: `rtl-ais.service` already declares `After=signalk.service` → SK listener is up before rtl_ais connects. No race condition.

`[ASSUMED]` Removing the `host` field from SK's TCP subOptions puts the provider into server/listen mode. If after deploy SK does NOT appear in `ss -tlnp | grep 10108`, escalate — add `"server": true` to subOptions explicitly.

---

## CURRENT STATE (derive from these exact lines — do not guess)

**File 1 — `deployment/v0.9.9.4/etc/systemd/system/rtl-ais.service`**
```ini
[Unit]
Description=RTL-SDR AIS Receiver
After=network.target signalk.service
Wants=signalk.service

[Service]
Type=simple
User=d3kos
ExecStart=/usr/bin/rtl_ais -h 127.0.0.1 -P 10110 -n
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**File 2 — `deployment/v0.9.9.4/home/d3kos/.signalk/settings.json`**
The `ais` pipedProvider block (inside `pipedProviders` array):
```json
{
  "id": "ais",
  "pipeElements": [
    {
      "type": "providers/simple",
      "options": {
        "logging": false,
        "type": "NMEA0183",
        "subOptions": {
          "validateChecksum": true,
          "type": "tcp",
          "host": "127.0.0.1",
          "port": "10110",
          "sentenceEvent": "nmea0183"
        }
      }
    }
  ],
  "enabled": false
}
```

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-32   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-32 — AIS never reaches Signal K; rtl_ais and SK ais provider
            both connected to port 10110 (SK's own NMEA0183 output — a loop)

FILES TO EDIT (exactly two)
  deployment/v0.9.9.4/etc/systemd/system/rtl-ais.service
  deployment/v0.9.9.4/home/d3kos/.signalk/settings.json

CHANGE A — rtl-ais.service: change the push port from 10110 to 10108

  CURRENT (ExecStart line only):
    ExecStart=/usr/bin/rtl_ais -h 127.0.0.1 -P 10110 -n

  REPLACEMENT:
    ExecStart=/usr/bin/rtl_ais -h 127.0.0.1 -P 10108 -n

  No other lines in the service file change.

CHANGE B — settings.json: re-wire the ais pipedProvider

  Find the pipedProvider object with "id": "ais".
  Replace its entire contents with the following:

  CURRENT (the complete ais provider object):
    {
      "id": "ais",
      "pipeElements": [
        {
          "type": "providers/simple",
          "options": {
            "logging": false,
            "type": "NMEA0183",
            "subOptions": {
              "validateChecksum": true,
              "type": "tcp",
              "host": "127.0.0.1",
              "port": "10110",
              "sentenceEvent": "nmea0183"
            }
          }
        }
      ],
      "enabled": false
    }

  REPLACEMENT:
    {
      "id": "ais",
      "pipeElements": [
        {
          "type": "providers/simple",
          "options": {
            "logging": false,
            "type": "NMEA0183",
            "subOptions": {
              "validateChecksum": true,
              "type": "tcp",
              "port": 10108,
              "sentenceEvent": "nmea0183"
            }
          }
        }
      ],
      "enabled": true
    }

  Three changes from CURRENT to REPLACEMENT:
    1. `host` field REMOVED from subOptions — puts SK in server/listen mode
    2. `port` value changed from string "10110" to number 10108
    3. `enabled` changed from false to true

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT modify any other pipedProvider (can0, gps) — touch only the ais block.
  • Do NOT change the port number anywhere other than these two files.
  • Do NOT modify the rtl-ais.service [Unit], [Install], or any line other than ExecStart.
  • Do NOT modify settings.json outside the ais pipedProvider block.
  • Do NOT add or remove any JSON key other than removing "host" and changing port/enabled.
  • Do NOT deploy to the Pi (Tier 1 deploys after §25.8 verify).

INTERFACE CONTRACT
  After Change A:
    → rtl_ais will connect to 127.0.0.1:10108 instead of 10110
    → SK port 10110 (NMEA0183 output) is untouched and still serves other clients

  After Change B:
    → SK ais pipedProvider is enabled and in server/listen mode on port 10108
    → rtl_ais (TCP client) connects to SK's listener on 10108
    → SK parses incoming AIVDM sentences and populates vessels.* with AIS targets

FAILING TESTS FIRST (TDD — write, RUN, watch fail, THEN fix)
  File: tests/bug32-ais-port.test.cjs
  Run : node tests/bug32-ais-port.test.cjs

  These are pure file-content assertions — no mock DOM, no async.
  Read the two files and assert their content.

  Required test cases (5):

  1. rtl-ais.service ExecStart contains "-P 10108"
     Read rtl-ais.service. Assert the ExecStart line contains "-P 10108".

  2. rtl-ais.service ExecStart does NOT contain "10110"
     Same file. Assert the ExecStart line does NOT contain "10110".

  3. settings.json ais provider is enabled
     Parse settings.json. Find pipedProviders entry with id "ais".
     Assert entry.enabled === true.

  4. settings.json ais provider port is 10108 (number, not string)
     Same parse. Assert subOptions.port === 10108 (strict equality — number type).

  5. settings.json ais provider has no "host" key in subOptions
     Same parse. Assert !("host" in subOptions).

  EXPECTED BEFORE THE FIX:
    test 1 — FAIL: ExecStart has "10110", not "10108"
    test 2 — FAIL: ExecStart contains "10110"
    test 3 — FAIL: enabled is false
    test 4 — FAIL: port is "10110" (string, wrong value, wrong type)
    test 5 — FAIL: "host" key is present in subOptions

  All 5 must flip FAIL → PASS.
  Report the BEFORE run output.

DONE WHEN
  • All 5 tests FAIL before edit and PASS after.
  • git diff touches only rtl-ais.service, settings.json, and the new test file.
  • settings.json remains valid JSON (parse without error after edit).
  • No other pipedProviders were modified.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • settings.json does not have a pipedProviders array, or the ais entry cannot
    be found by id "ais"
                                   → ADVICE (show the actual providers list)
  • settings.json is not valid JSON after your edit
                                   → CRITICAL (do not write the file; show your diff)
  • The "can0" or "gps" pipedProvider blocks were accidentally modified
                                   → CRITICAL (revert those blocks immediately)
  • The rtl-ais.service file contains multiple ExecStart lines
                                   → ADVICE (show all ExecStart lines; change only the one
                                     with rtl_ais, not any ExecStartPre/Post)

PRE-FLIGHT SELF-CHECK
  1. How many files do I edit?              → exactly 2 (rtl-ais.service + settings.json)
  2. Is settings.json still valid JSON?     → YES — verify with JSON.parse before saving
  3. Are other pipedProviders untouched?    → YES — only ais block changed
  4. What proves done?                      → all 5 tests flip fail → pass

RETURN TO TIER 1
  • The diff for both files
  • node output showing BEFORE run (fail) then AFTER run (pass) for all 5 tests
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. Port 10108 confirmed free on lab Pi via `ss -tlnp` (S110) — not in the 8000-range or 10110.
2. Removing `host` from SK TCP subOptions → server/listen mode. ESCALATE-IF covers the case where this assumption is wrong.
3. `port` changed from string `"10110"` to number `10108` — SK's JSON schema expects a number for port.
4. `enabled: true` is required — without it SK never connects the provider to the pipeline.
5. `rtl-ais.service` has `After=signalk.service` — SK's listener on 10108 will be up before rtl_ais connects. No boot-race.
6. SK port 10110 (NMEA0183 output server) is untouched — no regression to other NMEA0183 consumers.
7. Tests use strict `===` for port number type — catches the `"10110"` string-vs-number regression.
8. Test 5 (no `host` key) is the critical topology test — ensures client mode is not accidentally preserved.

## Post-deploy validation (Tier 1 runs after accepting Haiku return)

Lab (immediate):
- `ss -tlnp | grep 10108` on Pi → SK node process listening on 10108
- `journalctl -u rtl-ais -n 20` → "AIS data will be sent to 127.0.0.1 port 10108"

On-boat (required for full verification):
- SK vessels API returns > 1 vessel entry while underway in an area with AIS traffic
- Dashboard AIS overlay shows targets (dependent on BUG-19/BUG-20 overlay fix, out of scope here)
