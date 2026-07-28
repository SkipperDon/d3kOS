# v0.9.9.4 Bug Fixes — Investigation & Status
**Version:** 1.14.0 | **Created:** 2026-04-21 S65 | **Updated:** 2026-07-28 S109 | **Status:** IN PROGRESS

> **S107 ON-BOAT PHASE A EVIDENCE (2026-07-27) — READ FIRST.** Live SSH investigation on the boat
> Pi (`172.20.10.8`) with the engine running and the Garmin connected to the NMEA 2000 bus.
> Seven new defects logged as **BUG-28 … BUG-34**. Three findings override earlier records:
> - **The boat Pi runs d3kOS v0.9.2.2 (build 2026-03-23).** The S96 and S105 fixes are NOT on it.
>   **BUG-15, BUG-26 and BUG-27 are therefore NOT fixed on the boat** despite being marked
>   `[x] FIXED`/`COMPLETE` — those deploys went to the lab Pi (`192.168.1.237`). See BUG-28.
> - **E1 CONFIRMED and BUG-18 root cause replaced.** Garmin depth IS on the bus and IS in Signal K
>   (`environment.depth.belowTransducer` = 0.99 m, `$source: can0.0`, PGN 128267 @ ~1 Hz). The
>   dashboard subscribes to `environment.depth.belowKeel`, which Signal K never populates. See BUG-30.
> - **BUG-25 and BUG-22 are NOT bugs.** Gemini answered a live query on the boat; internet egress
>   works. The wizard gate behaves as designed. See those entries.

> **S106 corrections & plan (2026-07-24):** On-boat analysis plan authored at
> `V09994_ONBOAT_ANALYSIS_PLAN.md` (per-bug expected behavior + investigation steps; fix in lab
> after on-boat evidence). Operator-confirmed expectations correct the records below:
> - **E1 (BUG-18):** depth source = **Garmin unit via NMEA 2000**. The candidate "no depth
>   sounder present" is WRONG and removed — the sounder exists on the bus; the problem is the
>   Garmin depth not reaching the gauge.
> - **E2 (BUG-16):** tapping any gauge must show that gauge's live value + its normal range from
>   the boat's documentation + advice on the actual reading; identical generic text = broken.
> - **Confound (BUG-19/BUG-20):** o-charts license expired 2026-04-01 → AvNav chart is blank;
>   renew (OB-O05) and confirm the chart base renders BEFORE judging AIS/hazard overlays.

## STANDING RULE — Read This First

This document is the holistic bug tracker for all platforms. Every bug on every platform (Pi, HostPapa website, Admin CRM VM, PWA) is logged here before any fix is attempted. Bugs are reviewed and prioritized as a group — not fixed one-off.

**At session start:** read this document AND PROJECT_CHECKLIST.md PART 17 before accepting any new work.

**When a bug is reported:** log it here with BUG-XX number, symptom, and known details → THEN investigate → THEN fix. Never fix without logging first.

**No fix is deployed without a corresponding entry in both this document and PART 17.**

---

---

## BUG-07 — Gemini model `gemini-2.5-flash` returning HTTP 503 on all environments

**Status:** `[x]` COMPLETE — 2026-04-21 S65

### Symptoms
- AI assistant on staging and production website returns "AI service unavailable"
- Pi AI Navigation shows "Gemini unavailable / check api key"
- Gemini API key was valid and correctly deployed — key was NOT the problem

### Root Cause
`gemini-2.5-flash` is under persistent high demand on Google's infrastructure. Every call
to the model returns HTTP 503 regardless of which API key is used or which environment.
This is a Google-side capacity issue, not a configuration problem.

`gemini-2.0-flash` and older models return 404 (discontinued).

### Fix Applied
Changed model from `gemini-2.5-flash` → `gemini-2.5-flash-lite` in all four locations:

| Location | File | Method | Status |
|----------|------|--------|--------|
| HostPapa staging | `inc/atmyboat-config.php` | FTP upload | `[x]` Done |
| HostPapa production | `inc/atmyboat-config.php` | FTP upload | `[x]` Done |
| Pi gemini-proxy (port 8097) | `/opt/d3kos/config/api-keys.json` | SSH sed | `[x]` Done |
| Pi gemini-nav (port 3001) | `/opt/d3kos/services/gemini-nav/config/gemini.env` | SSH sed | `[x]` Done |

### Pi Service Architecture Note (critical — two separate Gemini services on Pi)
The Pi has two completely separate Gemini services. They read different config files.
Changing one does NOT affect the other.

| Service | Port | Config File | Used By |
|---------|------|-------------|---------|
| `d3kos-gemini-proxy.service` | 8097 | `/opt/d3kos/config/api-keys.json` | General Gemini proxy (`gemini-proxy.py`) |
| `d3kos-gemini.service` | 3001 | `/opt/d3kos/services/gemini-nav/config/gemini.env` | AI Navigation (`gemini_proxy.py`) |

### Verification
- HostPapa staging: end-to-end PHP probe → HTTP 200 + model response confirmed
- HostPapa production: same probe → confirmed
- Pi port 8097: `/gemini/test` endpoint → `{"success": true, "model": "gemini-2.5-flash-lite"}`
- Pi port 3001: `/status` endpoint → `{"model": "gemini-2.5-flash-lite", "online": true}`

---

## BUG-08 — Helm Assistant on-screen keyboard shows but immediately hides; typing does not work

**Status:** `[~]` IN PROGRESS — investigation complete, fix attempt in progress

### Symptoms (reported by Don 2026-04-21)
1. Tapping the textarea in Helm Assistant (helm.html) — keyboard does not appear (or flashes briefly)
2. Manually opening squeekboard — keyboard shows but typing does not work

### What Was Confirmed Working
- AI Assistant page (ai-assistant.html) — keyboard works correctly
- `keyboard-fix.js` v2.1 is deployed (`/var/www/html/js/keyboard-fix.js`)
- D-Bus call via `/keyboard/show` returns `{"ok": true}` — squeekboard IS being invoked
- `d3kos-keyboard-api.service` running, `User=d3kos` (correct session user)
- labwc `mouseEmulation="no"` — unchanged, `pointerType` is 'touch'
- Keyboard API log confirmed show→hide at 14:35:08 (same second) — keyboard flashes

### Root Cause Analysis

#### Symptom 2 (typing doesn't work): Wayland text input protocol not active
When manually opened, squeekboard has no active `zwp_text_input_v3` text input client to send
keystrokes to. This protocol is activated when an input element receives Chromium's DOM focus
AND the Chromium window has Wayland compositor keyboard focus. If the helm.html textarea lost
zwp_text_input_v3 registration (e.g., from a programmatic `blur()` call or focus loss), typing
to a manually opened keyboard has nowhere to go.

#### Symptom 1 (keyboard flashes): `el.blur()` fires hideKeyboard before `_recentlyShown` is set
keyboard-fix.js v2.1 calls `el.blur()` before `el.focus()` to force zwp_text_input_v3
re-registration. The problem: `el.blur()` fires the blur event synchronously. If there is a
`{ once: true }` `hideKeyboard` listener still attached from the PREVIOUS tap (which wasn't
consumed by a natural blur), it fires immediately — BEFORE `showKeyboard()` is called. At that
moment `_recentlyShown` is still false, so `hideKeyboard()` runs and calls `/keyboard/hide`.
Then `showKeyboard()` fires and sets `_recentlyShown = true`. Result: hide then show, or show
then hide depending on fetch delivery order — but in practice the user sees keyboard flash.

**Evidence:** Keyboard API log at 14:35:08 shows `/keyboard/show` then `/keyboard/hide` in the
same second — both fired from the same synchronous event handler. This matches the above
timing sequence.

#### Why ai-assistant.html works but helm.html doesn't — investigation incomplete
Both pages have:
- Auto-focus on page load (`inputBox.focus()` in ai-assistant.html load event; `setTimeout(..., 500)` in helm.html)
- Element-level `pointerup` handler that shrinks layout for keyboard coverage
- `blur` event listener that restores layout when keyboard dismissed
- `keyboard-fix.js` loaded last

Key difference identified: ai-assistant.html calls `inputBox.focus()` in the `finally` block
after EVERY AI response. helm.html does NOT re-focus after send. Effect on zwp_text_input_v3
registration is not yet confirmed.

**Investigation was interrupted before confirming:** whether the show+hide pattern also occurs
on ai-assistant.html; the exact textarea HTML attribute differences; whether the `el.blur()`
timing is the definitive cause or a contributing factor only.

### Fix Attempted (v2.1 — insufficient)
keyboard-fix.js v2.1 added:
- `el.blur()` before `el.focus()` — intended to force zwp_text_input_v3 re-registration
- `_recentlyShown` 800ms guard — intended to suppress blur-triggered hide after keyboard shows

Result: fix is insufficient. The `_recentlyShown` guard does not cover the case where a
previous tap's `{ once: true }` hideKeyboard listener fires during `el.blur()` before
`showKeyboard()` is called.

### Next Diagnosis Steps (not yet done)
1. Check keyboard API logs for ai-assistant.html to see if show+hide pattern also occurs there
2. Confirm whether the `{ once: true }` listener from a previous tap is the definitive cause:
   - Test: first tap on page (no previous listener) — does keyboard stay up?
   - Test: second tap — does keyboard flash?
3. Read full textarea attribute list on ai-assistant.html for structural differences
4. Consider fix: remove `el.blur()` and instead use a different mechanism to re-register
   zwp_text_input_v3 (e.g., `requestAnimationFrame` around `el.focus()`)

### Fix Needed (proposed — not yet approved or tested)
The `hideKeyboard` blur listener from a previous tap fires during `el.blur()` before
`_recentlyShown` is set. Solution: remove the `{ once: true }` pattern entirely and instead
cancel the hide using the `_recentlyShown` guard PLUS move the guard check so it also covers
the programmatic blur from `el.blur()`.

Alternative: instead of `el.blur()` + `el.focus()`, use `el.dispatchEvent(new FocusEvent('blur'))`
+ `el.focus()` so zwp_text_input_v3 is re-registered without firing existing event listeners.

**Awaiting Don's next session to continue investigation and approve fix.**

---

---

## BUG-10 — Stripe Webhook Endpoints Pointing to /staging/ After Phase 4 Live Push

**Status:** `[x]` RESOLVED S74 2026-05-04
**Platform:** HostPapa (website + Stripe account)
**Reported:** 2026-05-04 via Stripe failure email (6 failed deliveries since 2026-05-01)

### Symptom
Stripe emailed to report webhook endpoint `https://atmyboat.com/staging/wp-admin/admin-ajax.php?action=atmyboat_stripe_webhook` had been failing since May 1, 2026. Investigation revealed BOTH live mode webhook endpoints still pointed to `/staging/` paths — meaning all real production Stripe events (subscription payments, cancellations, Fix My Pi charges) since Phase 4 launch (2026-04-12) were being delivered to the staging subdirectory rather than the live site.

### Root Cause
Phase 4 live push (2026-04-12) deployed the WordPress site to production but the Stripe Dashboard webhook endpoint URLs were never updated from staging paths to live paths. The webhook signing secrets in `inc/atmyboat-config.php` on the live server were the old staging secrets, not matching any live endpoint.

### Affected Files / Systems
- Stripe Dashboard — both live mode webhook endpoints (misconfigured URLs)
- `inc/atmyboat-config.php` on HostPapa live server — stale signing secrets
- `CREDENTIAL_VAULT.md` — live webhook secret entries were `[DON TO PROVIDE]` placeholders

### Fix Applied (S74 2026-05-04)
1. Don updated both Stripe Dashboard webhook endpoints to production URLs:
   - `https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/fix-my-pi-billing.php?action=webhook`
   - `https://atmyboat.com/wp-admin/admin-ajax.php?action=atmyboat_stripe_webhook`
2. New signing secrets obtained from Stripe Dashboard
3. Live `inc/atmyboat-config.php` updated via FTPS: `STRIPE_WEBHOOK_SECRET` + `STRIPE_WEBHOOK_SECRET_SUB`
4. `CREDENTIAL_VAULT.md` updated with live secrets; staging entries marked deleted

### Verification
Both endpoints confirmed Active, 0 failures in Stripe Dashboard post-fix.

---

## Files Modified This Version

| File | Location | Change | Status |
|------|----------|--------|--------|
| `inc/atmyboat-config.php` | HostPapa staging | GEMINI_MODEL → gemini-2.5-flash-lite | `[x]` |
| `inc/atmyboat-config.php` | HostPapa production | GEMINI_MODEL → gemini-2.5-flash-lite | `[x]` |
| `/opt/d3kos/config/api-keys.json` | Pi | gemini_model → gemini-2.5-flash-lite | `[x]` |
| `/opt/d3kos/services/gemini-nav/config/gemini.env` | Pi | GEMINI_MODEL → gemini-2.5-flash-lite | `[x]` |
| `/var/www/html/js/keyboard-fix.js` | Pi | v2.0 → v2.1 (blur guard + recentlyShown) | `[~]` Insufficient |

---

## Known Gaps / Uncertainties

- `keyboard-fix.js` v2.1 is deployed but the keyboard still flashes. The exact condition
  that bypasses `_recentlyShown` is identified (previous tap's blur listener fires during
  el.blur()) but a corrected fix has not been written or tested.
- It is NOT confirmed why ai-assistant.html works while helm.html doesn't. The investigation
  was interrupted. The re-focus-after-send difference is noted but causality not proven.
- `CREDENTIAL_VAULT.md` model entries updated S65 — gemini-2.5-flash-lite, both Pi config paths corrected.

---

## BUG-09 — AvNav data corruption after power loss; self-healing audit for all critical services

**Status:** `[ ]` OPEN — research required. Logged 2026-07-10 S94. No fix attempted yet.
**Platform:** Pi (primary); all d3kOS services (secondary audit scope)

### Symptom
AvNav chart navigation software becomes corrupted after unexpected power loss on the boat.
Root cause confirmed by operator: loss of boat electrical power (not a software crash) causes
an unclean shutdown of the Pi, leaving AvNav in a corrupted state on next boot.

### Known Root Cause
Unexpected power loss = no graceful systemd shutdown = services killed mid-write. AvNav
stores chart tile caches, route data, and config files on the Pi filesystem. Any write in
progress at power-off can leave files partially written or in an inconsistent state.
Same risk applies to any service that writes to disk without journaling or atomic commits.

### Research Required — Part 1: AvNav-Specific Recovery

Questions to answer before designing a fix:

| # | Question | Approach |
|---|----------|----------|
| R1 | What data does AvNav write that is corruption-prone? (tile cache, routes, config, track log) | Read AvNav docs + inspect `/home/d3kos/.avnav/` on Pi |
| R2 | Does AvNav have a built-in integrity check or recovery mode? | Review AvNav source / docs |
| R3 | Can corrupted AvNav state be detected on boot (e.g. failed service start, specific error in journal)? | Test: simulate power cut, observe systemd journal |
| R4 | What is the minimal recovery action? (delete cache only? restore from backup? reinstall?) | Determine from R1 + R3 |
| R5 | Can the recovery be automated in a systemd `ExecStartPre=` script? | Design after R4 |

### Research Required — Part 2: System-Wide Self-Healing Audit

Scope: every service that writes persistent state on the Pi.

| Service | Writes To | Corruption Risk | Self-Healing Strategy (TBD) |
|---------|-----------|-----------------|------------------------------|
| AvNav | `/home/d3kos/.avnav/` (tile cache, routes, config) | HIGH — confirmed | TBD — see Part 1 |
| Signal K | `~/.signalk/` (settings.json, security.json, plugin data) | MEDIUM — JSON config | Validate JSON on boot; restore from `.bak` if parse fails |
| Flask services (dashboard, camera, boatlog, etc.) | `/opt/d3kos/config/*.json` | MEDIUM — config JSON | Validate JSON on boot; restore factory defaults if corrupt |
| SQLite DBs (boatlog, fix-my-pi, engine snapshots) | `/opt/d3kos/data/*.db` | MEDIUM — SQLite has WAL mode | Enable WAL mode if not set; run `PRAGMA integrity_check` on boot |
| ChromaDB (RAG vector store) | `/home/boatiq/rag-stack/chroma_db/` | HIGH — binary index files | Detect corruption; trigger re-ingest from source documents |
| AvNav tile downloads | `/home/d3kos/.avnav/data/` | LOW — re-downloadable | Delete partial tiles; re-download on demand |

### Proposed Architecture: Unified Boot Self-Healing Service

Concept: a single `d3kos-selfheal.service` that runs `ExecStartPre` before all other services:

```
1. Check AvNav state → repair if corrupt
2. Validate all JSON config files → restore from .bak if invalid
3. Run SQLite integrity check on all DBs → log failures, alert via Fix My Pi
4. Check ChromaDB index → flag for re-ingest if corrupt
5. Log self-heal result to /opt/d3kos/logs/selfheal.log
6. Optionally: POST result to Fix My Pi watchdog endpoint
```

**This is design only — no code written. Research questions (R1–R5) must be answered before implementation begins.**

### Fix Status
| Step | Status |
|------|--------|
| Logged to PART 17 + V09994_BUG_FIXES.md | `[x]` Done S94 |
| AvNav research (R1–R5) | `[ ]` Not started |
| System-wide service audit (confirm risk levels) | `[ ]` Not started |
| Self-healing service design (atomic spec) | `[ ]` Blocked on research |
| Implementation | `[ ]` Blocked on design |
| Pi deployment + test | `[ ]` Blocked on implementation |

### Operator Actions Required Before Research Can Begin
- Confirm: is the Pi accessible via SSH right now for log inspection?
- Confirm: which AvNav data was lost/corrupted (routes? tile cache? settings?)
- Confirm: is there a specific AvNav error message on boot, or does it just silently fail?

---

## BUG-11 — No universal method to verify any brand of AIS, GPS, microphone, or speaker is working when connected to d3kOS

**Status:** `[ ]` OPEN — research required. Logged 2026-07-10 S95. Updated S95.
**Platform:** Pi (all hardware integration points)

### Symptom
When any boater connects an AIS receiver, GPS source, microphone, or speaker to d3kOS —
regardless of brand or model — there is no built-in mechanism to confirm the device is
functional and being used by the system. The d3kOS dashboard provides no device health
indicators for these peripheral categories.

A device that is incompatible, misconfigured, or silently failing produces the same user
experience as a working device: no data, no error, no feedback.

### Governing Constraint
**The solution cannot be brand-specific.** d3kOS is used worldwide. The make and model
of connected hardware is unknown in advance and varies by user. The fix must define
a generic detection framework that works for any compliant device in each category —
not a whitelist of supported brands, not a lookup table of known hardware.

The correct question is not "what devices does Don use?" — it is "how does d3kOS
reliably detect, verify, and monitor any device of this type?"

### Two Failure Classes to Solve For

**Class A — Compatibility failure (at connect time)**
The device uses a protocol variant, baud rate, physical interface, or data format
that d3kOS does not currently handle. Result: device plugged in, system sees nothing,
user sees nothing. No error surfaced.

**Class B — Silent operational failure (at runtime)**
The device is compatible and recognized on boot, but subsequently stops producing
valid data (cable fault, power brownout, RF signal loss, USB disconnect/reconnect).
d3kOS has no runtime watchdog for this condition. The user receives no warning.

Both failure classes must be addressable by the generic framework.

### Research Plan

#### Part 1 — Understand d3kOS Current Integration Points (read existing code/config on Pi)

For each device category, determine how d3kOS currently consumes the device — this is
what the detection framework must hook into.

| Device Category | Expected d3kOS Integration | What to Confirm on Pi |
|----------------|---------------------------|----------------------|
| AIS receiver | Signal K NMEA 0183 serial provider OR NMEA 2000 via PiCAN-M | Which Signal K providers are configured; are they bound to a specific `/dev/tty*` path? |
| GPS source | Signal K NMEA 0183 or NMEA 2000 | Same as AIS — how is position data ingested? Is it the same provider or separate? |
| Microphone | ALSA capture device (Linux audio subsystem) | Is a specific card/device hardcoded? Does `arecord -l` show the device? |
| Speaker / audio output | ALSA playback device | Is a specific card/device hardcoded in Piper TTS config or `ai_bridge.py`? |

#### Part 2 — Generic Detection Strategy Per Category

The goal: determine what evidence d3kOS can observe — without knowing the device brand —
to answer "is this device present and producing valid data?"

| Device Category | Class A Detection (is it connected and recognized?) | Class B Detection (is it producing valid data?) |
|----------------|---------------------------------------------------|------------------------------------------------|
| AIS | Does Signal K have an active provider for this path? Is any AIS NMEA sentence (e.g. `!AIVDM`) arriving at the configured port? | Monitor `vessels.*.navigation.position` or AIS paths in Signal K — did last-seen timestamp go stale? |
| GPS | Is a valid `$GPRMC` / `$GPGGA` sentence arriving at the configured serial path OR is Signal K path `navigation.position` populating? | Monitor Signal K position path — age of last fix > N seconds = silent failure |
| Microphone | Does `arecord -l` enumerate a capture device? Does a short test capture produce non-silent audio (RMS > threshold)? | Periodic short capture test: flat/zero RMS = device silent or dead |
| Speaker | Does `aplay -l` enumerate a playback device? Does a test tone play without ALSA error? | Periodic test tone: ALSA error or no-output = device gone |

**Key principle:** all four detection strategies rely only on standard Linux subsystem
interfaces (Signal K data paths, ALSA enumeration, NMEA sentence presence) — not on
any brand-specific driver, SDK, or device identifier. Any compliant device will produce
the expected signals if working correctly.

#### Part 3 — Detection Timing Model

Determine when each check should run:

| Check Type | Timing | Rationale |
|-----------|--------|-----------|
| Boot presence check | On `d3kos-selfheal.service` startup (before other services) | Catch Class A failures before the user ever reaches the dashboard |
| Runtime data-freshness check | Polling loop, every N seconds (N TBD) | Catch Class B failures during a voyage |
| On-demand check | User-triggered from Settings or Fix My Pi | Allow user to re-run check after cable swap or reboot |

#### Part 4 — Notification Design

When a check fails, determine the correct notification path:

| Failure Scenario | Notification Channel | Priority |
|-----------------|---------------------|----------|
| Device absent at boot (not enumerated) | Dashboard persistent banner + Fix My Pi diagnostic | HIGH |
| Device present but no valid data at boot | Dashboard persistent banner + voice TTS warning | HIGH |
| Device was working, now silent > N seconds | Dashboard warning + optional voice TTS | MEDIUM |
| Device absent at boot but not configured (user has no such device) | No notification — absence is expected | N/A |

**Open design question:** how does d3kOS know whether a device category is expected?
(e.g. a boat with no AIS should not receive an "AIS missing" alert.)
Resolution options: (a) a device configuration page in Settings where user declares what is installed,
(b) auto-detect at first boot and cache the inventory, (c) only alert when a device was previously seen.
This question must be answered before implementation can begin.

#### Part 5 — Compatibility Gap Handling

Some devices will fail Class A detection because d3kOS does not yet support their protocol
variant (e.g. non-standard baud rate, NMEA 2000 PGN d3kOS does not subscribe to, etc.).

For these cases the resolution is not "add support for brand X" but:
- Identify the protocol gap (what standard are we missing?)
- Extend d3kOS to support the standard, not the brand
- Examples: auto-negotiate NMEA 0183 baud rates; support common GPS sentence variants
  (`$GNRMC` as well as `$GPRMC`); handle ALSA device re-enumeration on USB disconnect/reconnect

### Fix Status
| Step | Status |
|------|--------|
| Logged to PART 17 + V09994_BUG_FIXES.md | `[x]` Done S95 |
| Reframed as generic/model-agnostic framework | `[x]` Done S95 |
| Part 1: read current d3kOS integration points on Pi (requires SSH) | `[ ]` Not started |
| Part 2: generic detection strategy per category | `[ ]` Blocked on Part 1 |
| Part 3: detection timing model | `[ ]` Blocked on Part 2 |
| Part 4: notification design + "expected device" question answered | `[ ]` Blocked on Part 2 |
| Part 5: compatibility gap audit | `[ ]` Blocked on Part 1 |
| Implementation — device health monitor service | `[ ]` Blocked on design |
| Pi deployment + test | `[ ]` Blocked on implementation |

### Pre-Research Prerequisite
SSH access to the Pi is required to read current Signal K provider config and ALSA
device configuration. No specific device brand information is needed before research begins.
Research starts from what d3kOS currently does — and builds the generic framework outward from there.

---

## BUG-12 — AIS targets not showing in dashboard; Signal K AIS provider disabled

**Status:** `[ ]` **REOPENED S109 2026-07-28 — the `[x] FIXED` claim was FALSE.** Superseded by **BUG-32**. The fix recorded below is present on no Pi in service, and the approach itself was never valid.

> **CORRECTION — S109 2026-07-28.** This entry carried `[x] FIXED — 2026-07-11 S96` for 17 days. Two independent faults:
>
> 1. **Not present anywhere.** The S96 change was written to whichever card was in the boat on 2026-07-11; that card is out of service. S107 read the boat Pi's `~/.signalk/settings.json` at mtime **2026-03-12** with `ais` `enabled: false`, and S109 read the lab Pi (master) live as `enabled: false`. See **BUG-28**.
> 2. **The fix itself was invalid.** Signal K holds TCP 10110 as its own NMEA0183 **output** server — `ss -lntp` → `LISTEN *:10110 users:(("node",…))`, confirmed on the lab Pi 2026-07-28. The `ais` pipedProvider is a TCP **client** to that same port, so enabling it makes Signal K read its own GPS output back in a loop. It can never carry AIS. `rtl_ais` pushing to the same port is discarded for the same reason.
>
> **Do NOT re-apply the fix recorded below.** It is retained as a historical record. The real fix is **BUG-32** — give `rtl_ais` a dedicated port and point the provider at that — which is unbuilt.
>
> Verification method note: the false status arose from treating a *deploy record* as evidence of *current state*. Any claim about what is on a Pi must cite a live read or the most recent on-boat evidence.

**Logged:** 2026-07-11 S96 (on-boat, Don at Port Colborne area, Pi IP 172.20.10.8)
**Platform:** Pi (d3kOS dashboard)

### Symptom
AIS targets not appearing in dashboard or AvNav. Don reported "AIS may not be working" during on-boat session S96.

### Root Cause
Signal K `ais` pipedProvider was set to `"enabled": false` in `~/.signalk/settings.json`.
`rtl_ais` was running correctly (process `/usr/bin/rtl_ais -h 127.0.0.1 -P 10110 -n`)
and outputting NMEA0183 AIS sentences to TCP port 10110 — exactly what the provider
is configured to read. The provider being disabled meant SK was not consuming any of it.

When/how it was disabled is unknown. No AIS PGNs were observed on the NMEA2000 bus (can0)
during testing, confirming RTL-SDR is the intended (and only) AIS path.

Stale test vessel MMSIs (800000001, 800000003) visible in SK prior to fix — leftover
from the simulator removed March 2026. These cleared on SK service restart.

### Investigation Method (S96 — Pi Diagnosis Protocol)
Three parallel agents:
1. Services/logs: confirmed all services active; AIS vessel count showed only test MMSIs
2. Config/git: found `"enabled": false` in pipedProviders for 'ais'; rtl_ais running on 10110
3. Filesystem: disk 23% used, memory 4.7GB free, no filesystem issues

### Fix Applied
```bash
# On Pi via SSH:
python3 -c "
import json
with open('/home/d3kos/.signalk/settings.json', 'r') as f:
    d = json.load(f)
for p in d['pipedProviders']:
    if p['id'] == 'ais':
        p['enabled'] = True
with open('/home/d3kos/.signalk/settings.json', 'w') as f:
    json.dump(d, f, indent=2)
"
sudo systemctl restart signalk
```

### Verification
- Signal K vessel count after restart: 1 (own vessel only — correct clean state)
- Test MMSIs cleared on restart — confirmed
- rtl_ais still running on port 10110 — confirmed
- Whether live AIS targets appear depends on VHF range of nearby vessels at time of test

### Side Investigation — AvNav Serial Port Conflict (same session)
During the BUG-12 investigation, a separate AvNav issue was also found and fixed:
AvNav's `AVNUsbSerialReader` was repeatedly failing to open `/dev/ttyACM0` (the u-blox 7 GPS)
because gpsd/Signal K already had exclusive access. This caused a continuous error loop in the
AvNav log (`ERROR, unable to open port`). AvNav was still navigating via its `AVNSignalKHandler`
(data from SK at port 8099), but the serial reader conflict caused log spam and resource waste.

**Fix applied:** Added `<UsbDevice usbid="1-1.4:1.0" type="ignore"/>` inside the
`AVNUsbSerialReader` block in `/var/lib/avnav/avnav_server.xml`. Backup at
`/var/lib/avnav/avnav_server.xml.bak.20260711`. AvNav restarted. Error loop confirmed gone.

Note: This is a separate issue from BUG-09 (power-loss file corruption). The serial conflict
may be pre-existing and unrelated to the power loss event. BUG-09 investigation (R1-R5) remains open.

### Relation to BUG-11
BUG-11 (generic device detection framework) was opened because AIS "may not be working"
and there was no way to tell. BUG-12 is the specific failure BUG-11 would have caught —
the AIS provider being silently disabled with no alert or health indicator in the dashboard.
BUG-11 research should consider this failure mode as a test case.

---

## BUG-13 — Speed gauge flickers between steady-state and current speed during throttle transitions; long-press opens options panel that obscures readout

**Status:** `[ ]` OPEN — investigation required
**Logged:** 2026-07-11 S97 (reported on-boat by Don)
**Platform:** Pi (d3kOS dashboard — speed gauge tile)

### Symptom

**Issue 1 — Gauge flickering during speed transitions:**
At steady cruising speed the gauge is stable and correct. When engine throttle is changed (speed increases or decreases), the display behaves as follows:
1. Momentarily shows the new current speed
2. Snaps back to the prior steady-state speed reading
3. Oscillates back and forth between the old reading and the new reading continuously throughout the speed transition
4. Does not settle cleanly on the new speed until the boat reaches a new steady state

The gauge does not track the speed smoothly during acceleration or deceleration — it shows both the old and new values alternately rather than a continuous update.

**Issue 2 — Long-press options panel obscures speed readout:**
When Don pressed and held the gauge tile on the touchscreen (attempting to monitor the speed more closely), an options panel appeared. The panel appearance is noted as expected/functional, but the panel covered the gauge face, making it impossible to read the current speed during the interaction. There is no way to simultaneously view options and the live speed reading.

### Known Context
- Reported while under way — throttle changes during navigation
- Signal K is the data source for speed (SOG — Speed Over Ground, path `navigation.speedOverGround`)
- The dashboard gauge likely reads from a Signal K WebSocket or REST poll
- Uncertainty flag: the exact gauge component file and rendering mechanism are unknown — investigation required

### Hypothesized Root Causes (unconfirmed — investigation required)

**Issue 1 candidates:**
- A smoothing/moving-average algorithm on the gauge is showing both the smoothed average and the raw value alternately — the display is toggling between a lagging average and the live reading
- The gauge is reading from two data sources (e.g. both a Signal K WebSocket push and a polling endpoint) and the two sources disagree during transitions, causing alternation
- A debounce or throttle interval in the UI update loop is causing the gauge to render a stale cached value between live updates
- Signal K itself may be emitting burst updates after a period of silence, arriving out-of-order or causing double-render on the consumer side

**Issue 2 candidates:**
- The options panel is rendered as an overlay that covers the full tile, including the gauge face
- No picture-in-picture or compact-mode for the gauge while options are open
- Touch event interpretation: a long-press that is meant for monitoring is being captured as a context-menu trigger

### Investigation Required

Before any fix is proposed:

**R1 — Identify the gauge component:**
- Which HTML/JS file renders the speed gauge tile on the dashboard?
- What is the Signal K data path being consumed (`navigation.speedOverGround` or other)?
- Is the update mechanism WebSocket (push) or polling (setInterval)?

**R2 — Identify the smoothing/averaging logic:**
- Is there a rolling average, exponential moving average (EMA), or debounce applied to the incoming speed value before it is rendered?
- If yes: what is the window or time constant?
- Is there a secondary data path (e.g. REST /api/v1/vessels/self alongside the WS stream) that could cause dual updates?

**R3 — Identify the options panel mechanism:**
- What event triggers the options panel on the speed tile (long-press, right-click, hold)?
- What does the options panel display — tile configuration, raw value, units?
- Does it cover the gauge or render alongside it?

**R4 — On-boat reproduction:**
- Reproduce the flicker by accelerating from idle to cruising speed while watching the dashboard
- Capture approximate flicker rate (is it every ~1s, every 200ms, continuous?)
- Confirm whether the flicker stops once the new speed is held steady

### Fix Approach (pending investigation)

Two separate fixes expected:

**Fix 1 — Gauge stability:** Likely one of:
- Remove or tune the smoothing algorithm so it does not create a visible split between raw and averaged values during transitions
- Unify the data source so the gauge reads from exactly one source (WebSocket preferred)
- Apply a single low-pass filter with an appropriate time constant (e.g. 1–2 seconds) that smooths rapid noise without introducing the oscillation

**Fix 2 — Options panel UX:** Likely one of:
- Render the options panel as a sidebar or bottom sheet instead of a full overlay, keeping the gauge face visible
- Add a live speed readout inside the options panel so the value is still accessible
- Shorten the long-press duration threshold or change the gesture to avoid accidental trigger while monitoring

### Files Likely Affected (unconfirmed)
- Pi: `/var/www/html/` — dashboard HTML/JS (specific file unknown — investigation required)
- Possibly: `/opt/d3kos/services/` — any service feeding speed data to the dashboard

### Checklist
| Step | Status |
|------|--------|
| Logged to PART 17 + V09994_BUG_FIXES.md | `[x]` Done S97 |
| R1 — Identify gauge component and data path | `[ ]` |
| R2 — Identify smoothing/averaging logic | `[ ]` |
| R3 — Identify options panel mechanism | `[ ]` |
| R4 — On-boat reproduction and flicker rate | `[ ]` |
| Fix 1 — Gauge stability | `[ ]` |
| Fix 2 — Options panel UX | `[ ]` |
| Verified stable at new steady-state speed on Pi touchscreen | `[ ]` |

---

## BUG-14 — CX5106 NMEA 2000 Engine Gateway Not Transmitting Data — Device Not Visible on NMEA 2000 Bus

**Status:** `[~]` IN PROGRESS — replacement unit on bus, tachometer signal connection pending
**Logged:** 2026-07-13 S98 (on-boat, Monterey 265 SEL, Pi IP 172.20.10.8)
**Updated:** 2026-07-20 S101 — new unit confirmed on NMEA 2000 bus
**Platform:** Pi (NMEA 2000 network, CX5106 integration)

### S101 Update — 2026-07-20 (On-boat, engine running)

Old CX5106 unit replaced with new unit. New unit confirmed on NMEA 2000 bus.

**NMEA 2000 network devices confirmed on bus:**
| Source | Device | PGNs |
|--------|--------|------|
| src=0 | Garmin ECHOMAP Ultra 106sv | GPS, depth, heading, temp |
| src=64 | Pangoo | PGN 127488 (Engine RPM) |
| src=106 | CX5106 (new unit) | PGN 126993 (Heartbeat only, every 60s) |

**Progress made:**
- CX5106 on NMEA 2000 bus at src=106 — confirmed stable (heartbeat every 60 seconds)
- Fuel sender (fuel gauge line) connected to CX5106
- ONE fuel packet (PGN 127505, value=0%) received by Signal K at 19:32:36 — data path confirmed
- CX5106 not broadcasting continuously — investigation ongoing

**Tachometer signal wire — confirmed S101:**
- **Blue wire, Pole 3 of RPM gauge** = tachometer signal (Monterey non-standard color; ABYC standard = gray)
- Pole 1: Purple (12V ignition) + Red fused (illumination power) + White (illumination return)
- Pole 2: Black (ground)
- Pole 3: Blue = tachometer signal from engine coil/HEI → this is what CX5106 RPM input needs
- NOTE: Clip to blue wire in PARALLEL — gauge continues to show RPM normally after clip

**DIP switches on new unit:**
- SW1: ON, SW2: OFF, SW3: ON, SW6: ON

**Open question — NOT confirmed by source:**
Whether CX5106 requires the RPM/tachometer signal to enable data output was inferred from observed behavior (one packet sent when RPM clip made contact) but has NOT been confirmed from CX5106 documentation. Treat as working hypothesis only.

**Next step:**
Connect CX5106 RPM input wire to blue wire at Pole 3 of RPM gauge (parallel clip). Verify with `candump can0` on Pi — should see PGN 127505 appearing at regular intervals.

### Symptom
CX5106 engine data gateway installed on the boat. Device has power (green LED on). However, it does not transmit any NMEA 2000 messages. Signal K shows zero messages from CX5106 on the CAN0 NMEA 2000 bus. Only "Pangoo" device (ID 64) appears in the NMEA 2000 sources list.

### Equipment & Configuration
- **Device:** CX5106 NMEA 2000 analog-to-digital converter
- **Boat:** Monterey 265 SEL (North American 8-cylinder gasoline engine)
- **Signal source:** Purple sender wire (fuel tank level) — measured 40-70 Ohms (correct sender resistance range)
- **DIP switch configuration:** SW3=ON (ignition coil RPM source), SW6=ON (8 cylinders)
- **NMEA 2000 connection:** Drop cable connected to T-connector on PiCAN-M

### Investigation Conducted (S98)
1. **Power:** Green LED on CX5106 confirmed — device is powered
2. **Sender signal:** Purple wire tested with multimeter (Ohms setting) — showed 40-70Ω resistance (correct for fuel sender)
3. **DIP switches:** Verified set to correct positions for 8-cyl gasoline (SW3=ON, SW6=ON)
4. **NMEA 2000 connection:** 
   - Drop cable physically connected to T-connector
   - Reseated connection 4 times
   - No visible corrosion or damage
5. **Signal K NMEA 2000 sources:** Only device visible is "Pangoo" (ID 64)
   - CX5106 does NOT appear in `curl http://localhost:8099/signalk/v1/api/sources` output
   - No CX5106 device ID enumerated on the bus

### Known Details
- Purple sender wire IS connected to CX5106 (only connection point for fuel sensor on this device)
- Analog gauges on the dashboard still work correctly (they receive the purple sender signal directly, not via CX5106)
- CAN0 interface on Pi is UP and receiving NMEA 2000 messages from Pangoo device (proves the backbone is functional)
- All DIP switch positions verified against CX5106_CONFIGURATION_GUIDE.md for 8-cylinder gasoline engine

### Root Cause Candidates
1. **Most likely:** CX5106 device is defective (has power, receiving sender signal, but hardware/firmware failure prevents NMEA 2000 transmission)
2. **Less likely but not ruled out:** CX5106 NMEA 2000 PHY or network stack failure (device isolated from the bus despite cable connection)
3. **Very unlikely:** NMEA 2000 backbone has a termination issue affecting only this device (Pangoo device works fine on same bus)

### Evidence Against Configuration Issues
- DIP switches set to manufacturer spec
- Sender wire connected and confirmed to have the signal (40-70Ω matches fuel sender resistance curve)
- Cable physically connected and reseated multiple times
- NMEA 2000 bus is active and receiving messages from other device

### Next Steps (blocked pending resolution)
If the device is defective:
1. Obtain a replacement CX5106 unit
2. Test the replacement with the same configuration
3. If replacement works → original unit is confirmed defective; document as hardware failure
4. If replacement also fails → issue is not the unit (revisit NMEA 2000 backbone or configuration)

If a replacement is not available:
1. Option: remove CX5106 and rely on analog gauges (they work correctly without it)
2. Alternative: implement software-based signal conditioning on Pi to read the sender resistance directly via an ADC and convert to NMEA 2000 PGNs (complex, requires new hardware)

### Relation to BUG-11
BUG-11 (generic device health detection) would have caught this failure automatically. d3kOS should alert the user: "CX5106 device not found on NMEA 2000 bus" on boot. This bug demonstrates why BUG-11 is critical.

---

## BUG-15 — Course Heading Flashes Different Directions on d3kOS Dashboard While Boat Is Stationary

**Status:** `[ ]` OPEN — investigation required
**Logged:** 2026-07-13 S98 (on-boat, reported by Don)
**Platform:** Pi (d3kOS dashboard — COG display)

### Symptom
While the boat is anchored or stationary (Speed Over Ground = 0), the course heading (COG — Course Over Ground) on the d3kOS dashboard display rapidly flashes between different directions. The display should remain stable or locked to a single direction when not moving.

### Context
- Reported during on-boat session while anchored / not under way
- Speed gauge shows 0 or near-zero
- Heading display is oscillating rapidly (flashing multiple directions)

### Hypothesized Root Causes (unconfirmed — investigation required)

**Candidate 1: GPS/GNSS receiver noise**
- When SOG is zero or very low, GPS receivers often show erratic heading (since direction is meaningless with no movement)
- Noise in the GPS signal can cause rapid COG swings when the vessel is stationary
- Fix would be: filter out COG updates when SOG is below a threshold (e.g., ignore COG when SOG < 0.5 knots)

**Candidate 2: Multiple heading sources with conflicting values**
- d3kOS may be receiving COG from multiple sources (GPS NMEA0183 GGA/RMC sentence, compass heading, NMEA2000 PGN)
- During stationary periods, these sources may disagree or one may return stale values
- Dashboard rendering alternates between the sources

**Candidate 3: Dashboard display caching / update bug**
- Dashboard may be rendering cached COG values alongside fresh values
- A rendering glitch could cause the old heading to display, then the new heading, then back to old — appearing as a flash

**Candidate 4: Signal K WebSocket push bursts**
- Signal K may emit multiple rapid COG updates when the heading is noisy, causing the dashboard to re-render multiple times per second
- No debounce or rendering throttle on the consumer side

### Investigation Required

**R1 — Identify COG data source and rendering:**
- What HTML/JS file renders the heading/COG display on d3kOS dashboard?
- Is COG data sourced from Signal K WebSocket (push) or REST polling?
- What is the update frequency?

**R2 — Check Signal K COG path activity when stationary:**
- On Pi SSH: `curl -s http://localhost:8099/signalk/v1/api/vessels/self/navigation/courseOverGroundTrue`
- Observe: does the COG value change rapidly when SOG is near zero?
- Capture: screenshot/log of the raw Signal K values during the flashing period

**R3 — Check if COG is the issue or if other headings are also flashing:**
- Does compass heading (if available in Signal K) also flash?
- Does courseOverGroundMagnetic (COG magnetic variant) flash?
- Or is it only COG that's affected?

**R4 — On-boat reproduction and frequency measurement:**
- Reproduce the flashing while stationary and anchored (low SOG)
- Estimate the flashing rate (is it 1 Hz, 10 Hz, continuous?)
- Note: does it stop as soon as the boat is underway (SOG > threshold)?

### Proposed Fix (pending investigation)

**Fix candidate:** Implement a COG validation filter in the dashboard consumer:
```
If SOG < 0.5 knots:
  - Do NOT update the displayed COG
  - Hold the previous stable value
  - Or display "Heading uncertain — moving slowly" message
Else:
  - Display the live COG value
```

Alternative: implement a low-pass filter on COG that attenuates rapid changes when SOG is low.

### Files Likely Affected (unconfirmed)
- Pi: `/var/www/html/` — dashboard HTML/JS (heading/COG display — specific file unknown — investigation required)
- Possibly: Signal K data consumers or WebSocket subscriptions

### Checklist
| Step | Status |
|------|--------|
| Logged to PART 17 + V09994_BUG_FIXES.md | `[x]` Done S98 |
| R1 — Identify COG rendering component and data source | `[ ]` |
| R2 — Observe raw Signal K COG values when stationary | `[ ]` |
| R3 — Determine if issue is COG-specific or broader | `[ ]` |
| R4 — On-boat reproduction and flashing frequency | `[ ]` |
| Proposed fix — COG filter (SOG threshold validation) | `[ ]` |
| Test fix on Pi dashboard | `[ ]` |
| Verified: COG remains stable when stationary | `[ ]` |

---

## BUG-16 — Engine Gauge Tap Dialog Shows Hardcoded/Simulated Data; Does Not Read Live Signal K Values or Compare Against Actual Tolerances

**Status:** `[ ]` OPEN — logged only. No investigation or fix attempted.
**Platform:** Pi (d3kOS dashboard — engine gauges)
**Reported:** 2026-07-15 S100 — on-boat testing

### Symptom

When the operator taps/presses any engine gauge on the d3kOS dashboard (oil pressure, coolant
temperature, RPM, battery voltage, fuel), a dialog appears. The dialog shows hardcoded or
simulated data — for example, it indicates "oil pressure is too low" with a fixed value — rather
than reading the actual live engine value from Signal K and evaluating whether that value is
within the normal tolerance range for the boat.

**Expected behaviour (as designed/intended):**
1. Operator taps any gauge
2. Dialog reads the actual live current value for that gauge from Signal K
3. Compares the reading against the normal operating tolerance (advisory / alert / critical thresholds)
4. If within tolerance → shows green "Normal" status with the actual reading
5. If outside tolerance → shows specific advisory for that gauge stating:
   - The actual reading vs. the expected normal range
   - What the operator should do immediately
   - Source: boat maintenance manual (if uploaded) OR AI-researched normal operating ranges for this engine

**Observed behaviour:**
- Dialog opens and shows data, but the data is simulated/hardcoded, not live Signal K readings
- Reported example: oil pressure alarm shown even when oil pressure gauge on screen reads normally

### Root Cause (preliminary — code inspection only; not yet confirmed on boat)

Three issues identified in `deployment/v0.9.4/pi_source/overlays.js`:

**Issue 1 — `showCrit()` is hardcoded (not live)**
```js
// Line 123 — overlays.js
ticker.textContent = '⛔ CRITICAL — OIL PRESSURE 8 PSI — TAKE ACTION NOW';
```
This function displays a fixed string. The `8 PSI` value is a demo constant, not a live reading.
If any code path triggers `showCrit()` on gauge tap, the operator sees simulated data.

**Issue 2 — `showAlert()` is also hardcoded**
```js
// Line 20 — overlays.js
ticker.textContent = '⚠ AIS ALERT — VESSEL CPA 0.18NM IN 4 MINUTES — HOLD COURSE';
```
Also a demo constant — unrelated to engine gauges but indicates the alert system was built
with simulation data throughout.

**Issue 3 — `openDiag()` silent fallback when Signal K cache is empty**
`openDiag()` reads `window._d3kEngData` (live cache populated by Signal K WebSocket).
If Signal K is offline or the cache has not been populated yet, `_diagReadingsSummary()`
returns `'no live readings available (Signal K offline)'` and all gauge cards show `—` with
`✓ Normal`. This creates a false "everything is normal" result when in fact no data was read.

**Design gap — no maintenance manual integration:**
The current `openDiag()` sends a generic Gemini prompt with the readings. It does not:
- Reference the boat's uploaded maintenance manual for engine-specific tolerances
- Use boat model / engine model to look up normal operating ranges
- Source the advisory from boat-specific data

### Affected Files

| File | Location | Role |
|------|----------|------|
| `deployment/v0.9.4/pi_source/overlays.js` | Repo | `showCrit()`, `showAlert()`, `openDiag()` — all diagnostic dialog logic |
| Pi: `/var/www/html/js/overlays.js` | Pi (deployed) | Live version |
| `deployment/v0.9.4/pi_source/instruments.js` | Repo | `window._d3kEngData` cache write — needs verification |
| Pi: `/var/www/html/js/instruments.js` | Pi (deployed) | Live version |

### Investigation Required (deferred — holistic group review)

- **R1:** Confirm which function is actually triggered when a gauge is tapped on Pi (is it `openDiag()` or `showCrit()` or something else?)
- **R2:** Confirm whether `window._d3kEngData` is being populated on the Pi when engine is running
- **R3:** Confirm the operator's tier level — `openDiag()` shows an "upgrade" screen for T0/T1 users instead of live data
- **R4:** Determine if the fix scope is: (a) fix the data binding only, or (b) also add maintenance manual sourcing

### Checklist
| Step | Status |
|------|--------|
| Logged to PART 17 + V09994_BUG_FIXES.md | `[x]` Done S100 |
| R1 — Confirm which function fires on gauge tap | `[ ]` |
| R2 — Confirm `_d3kEngData` populated on Pi | `[ ]` |
| R3 — Confirm operator tier level | `[ ]` |
| R4 — Determine fix scope | `[ ]` |
| Write fix | `[ ]` |
| Deploy and verify on Pi | `[ ]` |

---

## BUG-17 — Battery Voltage Not Displaying on d3kOS Dashboard

**Status:** `[ ]` OPEN — logged S101 2026-07-20
**Logged:** 2026-07-20 S101 (on-boat, Monterey 265 SEL)
**Platform:** Pi (d3kOS dashboard — battery/electrical display)

### Symptom
Battery voltage tile on d3kOS dashboard shows no data. Signal K path `/vessels/self/electrical/` returns empty. No battery voltage, no alternator voltage, no electrical data of any kind.

### Confirmed S101
```
curl -s http://localhost:8099/signalk/v1/api/vessels/self/electrical/
→ Empty response (no JSON data)
```

### Root Cause
No battery voltage source present on the NMEA 2000 bus. The CX5106 is the intended source for battery/alternator voltage via PGN 127489 (Engine Parameters Dynamic). CX5106 is on the bus (heartbeat confirmed) but not yet broadcasting data PGNs — see BUG-14.

### Two-part dependency
1. **BUG-14 must be resolved first** — CX5106 must be continuously broadcasting before any PGN 127489 data appears
2. **Battery input wire** — CX5106 may require a separate battery voltage input wire connected to its BAT+ terminal in addition to the sender wires. This has not been verified on Don's installation.

### Signal K Path
```
/vessels/self/electrical/batteries/0/voltage
```

### Investigation Required
- [ ] Confirm CX5106 has a battery voltage input terminal (check CX5106 wiring diagram)
- [ ] Confirm which wire on Don's boat connects to CX5106 BAT+ terminal (if it exists)
- [ ] After BUG-14 resolved: verify PGN 127489 appears in candump with battery voltage field populated
- [ ] Verify d3kOS dashboard battery tile reads from correct Signal K path

### Relation to BUG-14
Cannot be fixed independently — resolving BUG-14 (CX5106 continuous data) is a prerequisite.

---

## BUG-18 — Depth Gauge Not Registering on d3kOS Dashboard

**Status:** `[ ]` OPEN — logged S103 2026-07-20
**Logged:** 2026-07-20 S103
**Platform:** Pi (d3kOS dashboard — depth display)

### Symptom
Depth gauge on d3kOS dashboard shows no data. Depth is expected to come from a depth sounder on the NMEA 2000 bus, read by Signal K, displayed by d3kOS.

### Expected Data Path
```
Depth sounder → NMEA 2000 bus (PGN 128267 — Water Depth)
  → Signal K → /vessels/self/environment/depth/belowKeel (or belowTransducer)
  → d3kOS dashboard depth tile
```

### Root Cause
Unknown — investigation required. Candidates in order of likelihood:

1. **No depth sounder on NMEA 2000 bus** — depth sounder may be a standalone unit (not N2K connected) or may not be installed
2. **Depth sounder present but not broadcasting PGN 128267** — device on bus but not transmitting depth PGNs
3. **Signal K receiving PGN 128267 but d3kOS reading wrong path** — path mismatch between what Signal K publishes and what d3kOS subscribes to
4. **d3kOS depth gauge display bug** — frontend not rendering the value even when Signal K has it

### Investigation Steps (in order — do not skip)
- [ ] On-boat: run `candump` or check Signal K data browser — is PGN 128267 appearing on the bus?
- [ ] Check Signal K: `curl http://localhost:8099/signalk/v1/api/vessels/self/environment/depth/` — does it return any data?
- [ ] If Signal K has data: check d3kOS dashboard source code for the depth tile — what Signal K path is it subscribing to?
- [ ] If no Signal K data and no PGN 128267: determine whether a depth sounder is present and how it is connected

### Signal K Paths to Check
```
/vessels/self/environment/depth/belowKeel
/vessels/self/environment/depth/belowTransducer
/vessels/self/environment/depth/belowSurface
```

### Fix Steps
- [ ] Identify root cause from investigation above
- [ ] Write fix (path correction, Signal K config, or d3kOS dashboard code — TBD)
- [ ] Deploy and verify on Pi

---

## BUG-19 — AIS Targets Not Visible on AvNav Map

**Status:** `[ ]` OPEN — logged S104 2026-07-21
**Logged:** 2026-07-21 S104
**Platform:** Pi (AvNav chart display)
**Checklist:** A-06 (pass with caveat — "have not seen anything broadcasting")

### Symptom
AIS is confirmed working in Signal K (rtl_ais running, AIS pipedProvider enabled per BUG-12 fix S96). When AIS-transmitting vessels are nearby, no symbols or target markers appear on the AvNav chart pane on the d3kOS dashboard. Operator reported: "AIS looks to be working but I do not see the location on the avnav map. There are no symbols showing."

### Root Cause Candidates
1. **AvNav not receiving AIS from Signal K** — AVNSignalKHandler may not be forwarding AIS target data to AvNav
2. **AvNav AIS overlay disabled** — AIS target display layer may be turned off in AvNav config or UI
3. **No AIS-transmitting vessels within range during testing** — A-06 noted "pass but have not seen anything broadcasting"; if no vessels were broadcasting, the test cannot confirm display works
4. **AvNav AIS format mismatch** — Signal K AIS data format may not match what AvNav expects for symbol rendering

### Investigation Steps (in order — do not skip)
- [ ] SSH to Pi: check Signal K data browser for any `vessels.*` entries other than `self` — are AIS vessel objects present?
- [ ] `curl http://localhost:8099/signalk/v1/api/vessels/ | python3 -m json.tool` — how many vessel entries?
- [ ] Check AvNav config (`/var/lib/avnav/avnav_server.xml`) — is `AVNSignalKHandler` configured and enabled?
- [ ] In AvNav web UI (port 8080): check if AIS target display is toggled on in the chart view controls
- [ ] Test with a known AIS source (MMSI simulator or wait for a vessel): confirm whether symbols appear when verified AIS data is present in Signal K

### Fix Steps
- [ ] Identify root cause from investigation
- [ ] Fix AVNSignalKHandler config, AvNav overlay setting, or data path as indicated
- [ ] Deploy and verify on Pi with confirmed AIS traffic present

---

## BUG-20 — Camera Hazard Detections Not Appearing on AvNav Map

**Status:** `[ ]` OPEN — logged S104 2026-07-21
**Logged:** 2026-07-21 S104
**Platform:** Pi (camera detection → AvNav integration)
**Checklist:** G-10 (failed — no bounding boxes); operator report

### Symptom
Four cameras functioning and connected. Multiple real-world waterway hazards observed at close range on-boat: kayakers, deadhead log, ducks, geese, people swimming. None of these appeared as markers, overlays, or symbols on the AvNav chart. G-10 (fish detection bounding boxes) also failed — no bounding boxes visible on camera view.

### Root Cause Candidates
1. **Integration pipeline not built** — signalk-forward-watch can detect marine objects and publish to Signal K, but the pipeline to display those detections as AvNav chart overlays is likely not implemented
2. **Fish detector not trained for above-water objects** — the fish detector (d3kos-fish-detector.service, port 8086, YOLOv8n + EfficientNet) is designed for fish detection. Kayakers, logs, ducks, geese, and swimmers are above-water targets it was not trained for
3. **signalk-forward-watch not running or not detecting** — the forward-watch plugin may not be active or not detecting targets at the camera resolution/angle used
4. **No AvNav overlay renderer built** — even if detections fire and reach Signal K, there is no AvNav overlay plugin or renderer to display them on the chart

### Investigation Steps
- [ ] SSH to Pi: `systemctl is-active signalk-forward-watch` (or check via SK plugin list) — is it running?
- [ ] Check Signal K data browser: are any forward-watch detection events appearing as SK paths?
- [ ] Confirm fish detector: does it produce any output when camera is aimed at surface objects? (`journalctl -u d3kos-fish-detector -n 50`)
- [ ] Assess whether an AvNav overlay renderer for camera detections was ever built

### Fix Steps
- [ ] Determine scope: is this a "pipeline exists but broken" bug or a "feature not yet built" gap
- [ ] If gap: design and build detection → Signal K → AvNav overlay pipeline as a new feature
- [ ] If broken: diagnose and fix the broken component
- [ ] Deploy and verify with real on-water targets

---

## BUG-21 — No Verbal or Visual Warning for Waterway Hazards

**Status:** `[ ]` OPEN — logged S104 2026-07-21
**Logged:** 2026-07-21 S104
**Platform:** Pi (hazard warning system)
**Operator report:** Blocking — cannot use d3kOS as a situational awareness tool without this

### Symptom
Cameras functioning. Kayakers, deadhead log, ducks, geese, and swimmers were observed at close range. No audio warning was played and no visual alert appeared on the d3kOS dashboard at any point.

### Root Cause Candidates
1. **Warning pipeline not built end-to-end** — the path from camera detection → hazard classification → alert threshold → audio/visual notification likely does not exist as a complete implementation
2. **SafeHelm not implemented** — SafeHelm (the collision avoidance / COLREGs warning system) is design-only; no code has been written. This is the intended home for hazard warning logic
3. **signalk-forward-watch alert integration missing** — even if forward-watch detects objects, no code wires those detections to the d3kOS notification or audio system
4. **Audio output not configured for alerts** — Pi audio device may not be set up for notification playback even if alert logic existed

### Investigation Steps
- [ ] Confirm what warning/alert features are actually implemented in the current codebase (search d3kOS dashboard + services for alert/notification code)
- [ ] Confirm SafeHelm build status: design-only confirmed — no code exists
- [ ] Check if signalk-forward-watch has any alert output path implemented

### Fix Steps
- [ ] Scope decision required: is hazard warning a v0.9.9.4 fix or a new feature requiring full design?
- [ ] If new feature: create feature spec and add to roadmap (likely v0.9.9.5 or SafeHelm Phase 1)
- [ ] If partial implementation exists: diagnose and complete the warning pipeline
- [ ] Test end-to-end with real hazard targets on water

---

## BUG-22 — Setup Wizard Bypassed on Fresh Load

**Status:** `[ ]` OPEN — logged S104 2026-07-21
**Logged:** 2026-07-21 S104
**Platform:** Pi (d3kOS dashboard — entry point routing)
**Checklist:** B-01 (failed), B-02 (failed)

### Symptom
On fresh browser load (or cleared cookies/localStorage), the system should redirect to the Setup Wizard Step 1 of 6. Instead, it loads directly to the main dashboard. B-01 and B-02 both failed.

### Root Cause Candidates
1. **Wizard-completed flag incorrectly persisted** — a `setup_complete` or similar flag in localStorage/cookie is set from a prior session and not cleared on fresh load
2. **Redirect logic checking wrong condition** — the entry point in `index.html` or `dashboard.js` may check a condition that always evaluates to "wizard done"
3. **Flag set prematurely during development** — the wizard may have been completed during development and the flag was never reset for production testing

### Investigation Steps
- [ ] Check `index.html` or main dashboard entry file: what condition triggers wizard redirect?
- [ ] In browser dev tools on Pi: check localStorage and cookies for wizard-related flags
- [ ] Clear all localStorage/cookies and reload — does wizard appear?
- [ ] Trace the redirect logic path in source

### Fix Steps
- [ ] Identify the flag or condition causing bypass
- [ ] Fix condition to correctly detect first-run state
- [ ] Deploy and verify on Pi

---

## BUG-23 — Boat Log Voice Note Transcription Failing

**Status:** `[~]` DIAGNOSED 2026-07-23 — partial. `boatlog-api` + `voice` services up, but `d3kos-voice-watchdog` **FAILED** (voice assistant running 1 thread, expected 2+); no local STT/whisper service found; mic capture absent at home (on-boat only). Transcription path unconfirmed — possible feature gap (Faster-Whisper STT is v0.9.9.5 D13, not built). Do NOT blind-restart the watchdog — find the 1-thread cause first. Diagnosis: `runbooks/GROUP-A-services.md`. (Was: `[ ]` OPEN logged S104 2026-07-21)
**Logged:** 2026-07-21 S104
**Platform:** Pi (Boat Log — voice note feature)
**Checklist:** H-03 (failed)

### Symptom
Tapping the voice record button, speaking a sentence, then tapping stop does not produce a VOICE entry in the Boat Log list. H-03 failed on-boat.

### Root Cause Candidates
1. **STT service not running** — speech-to-text transcription service (Whisper or similar) may not be active on Pi
2. **POST to `/api/boatlog/voice-note` failing** — the endpoint receiving the audio and triggering transcription may be returning an error
3. **Transcription timeout** — STT taking longer than the UI waits, causing silent failure
4. **Entry written to DB but not rendering** — transcription succeeds but the Boat Log list query does not fetch the new entry

### Investigation Steps
- [ ] SSH to Pi: `systemctl is-active d3kos-boatlog` (or whichever service handles voice notes)
- [ ] Check `journalctl -u d3kos-boatlog -n 50` for errors during record+stop
- [ ] In browser dev tools on Pi: check network tab when tapping stop — what does the POST response say?
- [ ] Check SQLite DB: `sqlite3 /opt/d3kos/data/boatlog.db "SELECT * FROM entries ORDER BY id DESC LIMIT 5;"`

### Fix Steps
- [ ] Identify root cause from investigation
- [ ] Fix service, endpoint, or rendering issue
- [ ] Deploy and verify on Pi

---

## BUG-24 — Boat Log Engine Auto-Capture Not Working

**Status:** `[ ]` OPEN — logged S104 2026-07-21
**Logged:** 2026-07-21 S104
**Platform:** Pi (Boat Log — engine auto-capture)
**Checklist:** H-04 (failed)
**Dependency:** May be blocked by BUG-14 (CX5106 not broadcasting RPM data)

### Symptom
After running the engine for 30+ minutes, no ENGINE badge entry appeared automatically in the Boat Log. H-04 failed on-boat.

### Root Cause Candidates
1. **Blocked by BUG-14** — engine auto-capture may require live RPM data from CX5106 to trigger. If CX5106 is not broadcasting (BUG-14 not resolved), RPM = 0 and auto-capture threshold is never met
2. **Auto-capture service not running** — the background service monitoring engine state may not be active
3. **RPM threshold logic broken** — even with RPM data present, the threshold check or time-based trigger may have a code bug
4. **Boat Log write path broken** — auto-capture fires but cannot write the ENGINE entry (related to BUG-23 path)

### Investigation Steps
- [ ] First: confirm whether BUG-14 is resolved. If CX5106 not broadcasting, this bug cannot be tested independently
- [ ] If CX5106 broadcasting: check Signal K for live RPM path (`/vessels/self/propulsion/*/revolutions`)
- [ ] Check which service or script implements engine auto-capture and confirm it is running
- [ ] Review the RPM threshold and time condition in source

### Fix Steps
- [ ] Resolve BUG-14 first (or confirm auto-capture works with simulated RPM)
- [ ] Fix auto-capture trigger logic or service
- [ ] Deploy and verify

---

## BUG-25 — AI Navigation (Gemini) Cannot Connect On Boat

**Status:** `[~]` DIAGNOSED 2026-07-23 — likely NOT a d3kOS bug. Both Gemini services up + enabled; live model = `gemini-2.5-flash-lite`; key present; `:3001/status` = online. Bad model (`gemini-2.5-flash`) exists only in `.bak`/`.ota-backup`, not live config. Root cause points to **internet egress** (Pi `curl google → 000`). Pending on-boat internet confirmation. Full diagnosis: `runbooks/GROUP-A-services.md`. (Was: `[ ]` OPEN logged S104 2026-07-21)
**Logged:** 2026-07-21 S104
**Platform:** Pi (AI Navigation — Gemini integration)
**Checklist:** J-01 (failed), J-02 (failed), J-03 (failed)

### Symptom
AI Navigation page shows "could not connect." No response to queries. GEMINI badge never appears. J-01, J-02, J-03 all failed on-boat.

### Root Cause Candidates
1. **gemini-proxy service not running** (port 8097, reads `api-keys.json`) — most likely cause
2. **gemini-nav service not running** (port 3001, reads `gemini.env`) — second Gemini service; both must be active
3. **API key missing or expired** — key in `api-keys.json` or `gemini.env` may be invalid
4. **Wrong model ID** — memory confirms `gemini-2.5-flash-lite` required on all environments; if model changed or was set to `gemini-2.5-flash` (returns 503 persistently), connection will fail
5. **Network isolation on boat** — boat hotspot may not have internet access for Gemini API calls

### Investigation Steps
- [ ] SSH to Pi: `systemctl is-active d3kos-gemini` and `systemctl is-active d3kos-gemini-proxy` — both must show `active`
- [ ] Check logs: `journalctl -u d3kos-gemini -n 30` and `journalctl -u d3kos-gemini-proxy -n 30`
- [ ] Verify model in `api-keys.json` and `gemini.env` — must be `gemini-2.5-flash-lite`
- [ ] Confirm boat hotspot has live internet: `curl -s https://www.google.com` from Pi
- [ ] Test proxy directly: `curl http://localhost:8097/` and `curl http://localhost:3001/`

### Fix Steps
- [ ] Start failed service(s) and set to auto-start if not enabled
- [ ] Correct model ID if wrong
- [ ] Verify API key validity
- [ ] Deploy and verify on Pi

---

## BUG-26 — Anchor Watch Set Anchor Failing; No Alarm Sound

**Status:** `[x]` FIXED + DEPLOYED TO PI S105 2026-07-23 — pending operator Set Anchor test at helm. Fix: 5 anchor fetches routed to `AI_BRIDGE` (`:3002`) in `anchor-watch.html`; deployed + dashboard restarted (backup `.bak.20260723`). ROOT CAUSE was: anchor endpoints live on ai-bridge (`:3002`, verified: `/anchor/set`=405 POST-only, `/anchor/state`=200); dashboard (`:3000`) serves none (all 404). `anchor-watch.html` fetches bare `/anchor/*` → `:3000` → 404 → Set Anchor never arms (K-02). Fix = point the 5 anchor fetches at `AI_BRIDGE` (`:3002`), matching the file's existing SSE call. Atomic spec: `atomic-specs/BUG-26.md`. Diagnosis: `runbooks/GROUP-A-services.md`. (Was: `[ ]` OPEN logged S104 2026-07-21)
**Logged:** 2026-07-21 S104
**Platform:** Pi (Anchor Watch feature)
**Checklist:** K-02 (failed), K-03 (unknown — no sound observed)

### Symptom
Anchor Watch page loads and shows GPS position (K-01 passed). Tapping "Set Anchor" does not arm monitoring — status does not change to armed/monitoring (K-02 failed). Whether the alarm triggers when the radius is exceeded is unknown; no alarm sound was observed (K-03 unknown).

### Root Cause Candidates
1. **Anchor watch service not running** — backend service that stores the anchor point and monitors drift may not be active
2. **GPS position not being written to anchor reference** — the "Set Anchor" action may fail to persist the current position
3. **API endpoint failure** — the frontend POST to set the anchor point may be returning an error silently
4. **Audio notification system not configured** — even if monitoring works, Pi audio device may not be set for alarm playback

### Investigation Steps
- [ ] SSH to Pi: confirm anchor watch service exists and is running
- [ ] In browser dev tools on Pi: check network tab when tapping "Set Anchor" — what is the API response?
- [ ] Check what API endpoint Set Anchor calls and whether that endpoint exists and returns 200
- [ ] Test audio: can the Pi play any sound? `aplay /usr/share/sounds/alsa/Front_Center.wav`

### Fix Steps
- [ ] Identify failing component (service, endpoint, or audio)
- [ ] Fix and deploy
- [ ] Verify on Pi with GPS fix active

---

## BUG-27 — Status Bar Text Not Readable at 1 Metre — AODA Violation

**Status:** `[x]` COMPLETE — deployed to Pi + operator-confirmed 1 m legibility 2026-07-23
**Logged:** 2026-07-21 S104
**Platform:** Pi (d3kOS dashboard — status bar CSS)
**Checklist:** D-09 (failed)
**Rule:** AODA minimum 18px ALL text — zero exceptions

### Symptom
Standing at the helm (~1 metre from the 10.1" touchscreen), the status bar showing vessel name and clock is not legible without leaning in or moving closer. D-09 failed.

### Root Cause (CORRECTED 2026-07-23)
Original hypothesis ("font size below 18px") was WRONG — code inspection found nothing
in the helm status bar (`#sb`) below the 18px AODA floor. Actual state: `.sb-vessel`
(vessel name) = 18px (exactly at the floor), `#clk` (clock) = 22px (already above it).
The real defect: 18px is the AODA *floor*, not a readable-at-1-metre size on a 10.1"
screen. Fix = raise the two operator-named helm elements to helm-distance sizes.
`#status-bar` (settings-page bar) and `.sb-ticker` were NOT the target.

### Investigation Steps
- [x] Read the status bar CSS — confirmed `#sb` helm bar: `.sb-vessel` 18px, `#clk` 22px (d3kos.css); `#status-bar` is the separate settings-page bar
- [x] Confirmed NOT below 18px — see corrected root cause

### Fix Steps
- [x] Raised `.sb-vessel` 18→28px and `#clk` 22→26px (helm-distance readability)
- [x] Deployed to Pi 2026-07-23 (`/opt/d3kos/services/dashboard/static/css/d3kos.css`; backup `.bak.20260723`)
- [x] Operator confirmed legibility at 1 metre on the 10.1" screen — 2026-07-23

### Fix Applied (2026-07-23)
- **Files:** `deployment/d3kOS/dashboard/static/css/d3kos.css` (repo) → `/opt/d3kos/services/dashboard/static/css/d3kos.css` (Pi)
- **Change:** `.sb-vessel` font-size 18→28px; `#clk` font-size 22→26px (font-size only; no other properties)
- **Process:** AAO §23/§25 atomic spec (`deployment/docs/atomic-specs/BUG-27.md`) — Tier 3 (Haiku) implemented failing-test-first; Tier 1 (Opus) verified diff scope + CSS override probe (PASS); operator authorized Pi deploy.
- **Backup/rollback:** `/opt/d3kos/services/dashboard/static/css/d3kos.css.bak.20260723`
- **No service restart** (Flask serves static from disk per request).
- **⚠ S107 CORRECTION:** this fix is **NOT present on the boat Pi** — `.sb-vessel` is still `18px`
  there and no `.bak.20260723` exists. The 1 m legibility confirmation cannot have been made on the
  boat screen. Status downgraded from COMPLETE to **DEPLOYED TO LAB PI ONLY**. See BUG-28.

---

## BUG-28 — Boat Pi Running v0.9.2.2; Two Deploy Sources Diverged (S96/S105 Fixes Absent)

**Status:** `[ ]` OPEN — logged S107 2026-07-27 (on-boat evidence)
**Severity:** HIGH — invalidates on-boat validation of any bug marked fixed after 2026-04-12
**Reported:** S107 on-boat, during Phase A investigation

### Symptom
Bugs marked `[x] FIXED` in PART 17 still reproduce on the boat. The operator's expectation was that
the boat Pi is a copy of the lab Pi and therefore carries the latest code. It does not.

### Evidence (boat Pi `172.20.10.8`, 2026-07-27)
```
/opt/d3kos/config/version.txt → d3kOS Version 0.9.2.2, Release Date March 23, 2026
```
| S105 fix | Expected | Actual on boat Pi | File mtime |
|---|---|---|---|
| BUG-27 `.sb-vessel` | 28px | **18px** | Apr 12 |
| BUG-15 `_lastSogKts` | present | **0 occurrences** | Apr 8 21:21 |
| BUG-26 `AI_BRIDGE` | present | **0 occurrences** | Apr 12 |
| S105 `.bak.20260723` backups | 3 files | **none exist** | — |

`~/.signalk/settings.json` mtime is **2026-03-12**, so the S96 BUG-12 AIS fix (2026-07-11) is also
absent — which is why `ais` is `enabled: false` again (see BUG-32). The Pi itself is healthy and
running: data files were written at 15:01 on 2026-07-27; exports exist from 2026-04-15 and 2026-04-22.
Only the **deployed code** is frozen at April vintage.

### Root cause — two-source divergence
`concepts/two-source-sync-rule` (d3kOS/dashboard/ + v0.9.4/pi_source/ must stay in sync) is **violated**:
```
deployment/d3kOS/dashboard/static/js/instruments.js
  → 4420050  2026-07-23  BUG-15: gate COG updates when SOG < 0.5 kn    ✓ has fix
deployment/v0.9.4/pi_source/instruments.js
  → 9800728  2026-04-08  S40: M14 verified — fix JS syntax error…       ✗ frozen
```
`diff` between the two trees → **DIVERGED**. The boat Pi's `instruments.js` (Apr 8 21:21, zero
`_lastSogKts`) matches the frozen `pi_source` tree, not the updated `d3kOS/dashboard` tree.

`Uncertainty flag:` two explanations remain consistent with the evidence and are not yet
distinguished — (a) the boat image was built from the stale `pi_source` tree, or (b) the boat was
imaged from the lab Pi before 2026-07-23. Either way the divergence above is real and is a defect.

### Affected files
- `deployment/v0.9.4/pi_source/` (entire tree — last touched 2026-04-08)
- `deployment/d3kOS/dashboard/` (current)
- Boat Pi `/opt/d3kos/` (v0.9.2.2)

### Fix steps
- [ ] **Confirm the version on the lab Pi (`192.168.1.237`) — operator-requested, deferred to lab session.** Lab Pi is unreachable from the boat hotspot (100% packet loss, SSH timeout).
- [ ] Decide the single canonical deploy source; reconcile the two trees
- [ ] Re-verify BUG-15, BUG-26, BUG-27 on the boat after a real release reaches it
- [ ] Add a version/commit stamp check to the release process so a stale copy is detectable

### ⚠ Critical note
Re-copying the latest version to the boat will **NOT** fix the engine gauges, depth gauge, BUG-16 or
BUG-24 — those defects (BUG-29, BUG-30) exist in the latest source too.

---

## BUG-29 — Dashboard Subscribes to `propulsion.0.*`; Signal K Publishes `propulsion.port.*`

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont** — logged S107 2026-07-27 | Tier 3 + Tier-1 §25.8 ACCEPT 13/13 | **NOT on the boat Pi** — unproven against live Signal K data
**Severity:** HIGH — breaks every engine gauge; root cause of BUG-24 and a root cause of BUG-16
**Present in:** latest repo source AND the boat Pi (not a stale-copy artifact)

### Evidence
```
curl .../vessels/self/propulsion  →  keys: ['port']
propulsion.port.revolutions = 0   $source: can0.64   pgn 127488   (live)

instruments.js subscribes:            Signal K actually publishes:
  propulsion.0.revolutions        →     propulsion.port.revolutions          ✗
  propulsion.0.coolantTemperature →     (nothing under .0.)                  ✗
  propulsion.0.oilPressure        →     (nothing under .0.)                  ✗
  propulsion.0.trimTabPosition    →     propulsion.port.drive.trimState      ✗ (leaf differs too)
  tanks.fuel.0.currentLevel       →     tanks.fuel.0.currentLevel            ✓ MATCHES
  electrical.batteries.0.voltage  →     (electrical tree empty — no source)
```
Repo counts (both trees): `propulsion.0.` ×8, `propulsion.port.` ×**0**.

### Root cause
The Signal K N2K mapper converts engine instance 0 to the name **`port`**, not the numeric `0`. The
dashboard was written against the numeric form and has never matched real NMEA 2000 hardware output.
Fuel is the single gauge that works precisely because that one path happens to coincide.

`Assumption:` the instance→name mapping (`0` → `port`) is Signal K N2K mapper behaviour, verified
empirically here against SK 2.23.0 with live Garmin + gateway traffic. Whether it is configurable
was NOT determined — check before choosing between editing 6 files vs. a mapper setting.

### Cascade
`window._d3kEngData` is populated **only** by those handlers, so it is permanently
`{coolant:null, oil:null, rpm:null, bat:null, fuel:0}`. This causes:
- **BUG-16** — every gauge tap renders `—` cards and sends Gemini the prompt
  *"Current readings: fuel 0%"* regardless of which gauge was tapped → identical generic text (E2 violation)
- **BUG-24** — `boatlog-engine.js` gates on `rpmHz > RPM_THRESHOLD_HZ (3)`; `rpm_hz` never leaves 0,
  so the engine is never "running" and no ENGINE entry can ever be written

### Affected files (blast radius — 6 live files)
- `deployment/d3kOS/dashboard/static/js/instruments.js`
- `deployment/d3kOS/dashboard/static/js/boatlog-engine.js`
- `deployment/d3kOS/dashboard/templates/engine-monitor.html`
- `deployment/d3kOS/dashboard/templates/helm-assistant.html`
- `deployment/v0.9.4/pi_source/instruments.js`
- `deployment/v0.9.4/pi_source/engine-monitor.html`

### Fix steps
- [ ] Confirm whether the SK instance→name mapping is configurable (cheaper than 6 file edits)
- [ ] Failing test first: assert the handler fires for the real SK path
- [ ] Prefer a tolerant subscription (accept both `propulsion.0.*` and `propulsion.port.*`) so a
      future single/twin-engine change does not break it again
- [ ] Re-verify BUG-16 and BUG-24 after the fix

---

## BUG-30 — Depth Gauge Reads `belowKeel`; Signal K Publishes `belowTransducer` (Replaces BUG-18 Root Cause)

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont** — logged S107 2026-07-27 | ACCEPT 16/16 | **NOT on the boat Pi** — and the PRIMARY fix (a negative keel offset on the Garmin) is still NOT set | **Supersedes the BUG-18 root-cause candidates**
**Severity:** HIGH — safety-relevant instrument

### Evidence — E1 confirmed, depth IS present
With the Garmin connected (operator action, S107 on-boat):
```
environment.depth.belowTransducer = 0.99 m   $source: can0.0   pgn 128267   LIVE
Garmin src 0 on bus: 128267 ×20 /20s, plus 129025/129026/129029 ×420, 130310/130312 ×50
```
Dashboard subscribes to `environment.depth.belowKeel` (repo: `belowKeel` ×2, `belowTransducer` ×0).
No keel/transducer offset is configured in Signal K, so `belowKeel` is never derived.

### Root cause
Same class as BUG-29 — path mismatch. The sounder exists, the data arrives, the gauge is bound to a
path nothing publishes. **The S106 candidate "no depth sounder present" is definitively wrong; E1 is correct.**

### Fix steps
- [ ] Either configure the transducer→keel offset in Signal K so `belowKeel` is derived, **or**
      subscribe to `belowTransducer` — operator decision, since `belowKeel` is the safer displayed value
- [ ] If reading `belowTransducer` directly, label the gauge accordingly (depth below transducer ≠ below keel)
- [ ] Failing test first; re-verify BUG-18 on-boat

---

## BUG-31 — Unidentified NMEA 2000 Device at src 64 Broadcasting Frozen Engine + False Fuel Data

**Status:** `[ ]` OPEN — logged S107 2026-07-27 | **Severity:** HIGH — false instrument data
**Requires physical identification on the boat**

### Evidence
```
candump can0 (20 s):  canid 09F20040  PGN 127488  src 64   ×201  (10 Hz)
raw payload, identical in every frame:   00 00 00 96 05 00 FF FF
  engine instance 00 | speed 0000 = 0 RPM | boost 0596 ×100Pa = 143,000 Pa | trim 00 | rsvd FFFF
                      canid 19F21140  PGN 127505  src 64   ×8    (~0.4 Hz)
tanks.fuel.0.currentLevel = 0 (ratio)   capacity = 1.16 m³ ≈ 306 US gal
```
Device identity from PGN 126996: `modelId "Pangoo"`, mfr 1998, product 1002, serial
`N20210700100`, cert Level B, LEN 2, class *Internetwork device*, function 132 (A/D converter).

### Analysis
- The payload is **byte-identical across all captured frames** — a real analog sender would show jitter
- `boostPressure` is a real encoded value (not the 0xFFFF "not available" marker) on an engine with
  **no turbo or supercharger** (MerCruiser 454 Mag MPI)
- **Operator confirmed the fuel tank is FULL; src 64 reports 0%.** Because `tanks.fuel.0.currentLevel`
  is the one path that matches (BUG-29), the gauge faithfully displays this false 0%
- Signal K binds the engine gauges to src 64's zeros, **not** to the CX5106 (src 106)
- `Uncertainty flag:` the removed lab simulator script documents the same source address 64 (`0x40`).
  **This was checked and ruled out** — no simulator files, units, or processes exist on the boat Pi.
  The address match is a coincidence (64 is a common default). src 64 is a real device.
- `[UNVERIFIED INFERENCE — not confirmed by documentation]` src 64 may be the original CX5106 that
  S98 declared defective. A WebSearch did **not** confirm Pangoo as the CX5106's manufacturer.

### Fix steps
- [ ] **Operator: physically locate and identify the src 64 device on the boat** (second gateway box?)
- [ ] Determine whether it is wired to the fuel/engine senders, and disconnect or reconfigure it
- [ ] Re-verify fuel % and engine PGNs with only one gateway on the bus
- [ ] If it is the original CX5106, correct the S98 record — two replacement units may have been unnecessary

### Related
Blocks trustworthy validation of BUG-14, BUG-16, BUG-17, BUG-24.

---

## BUG-32 — AIS Never Reaches Signal K: rtl_ais Sends to TCP 10110, Which Signal K Itself Occupies

**Status:** `[ ]` OPEN — logged S107 2026-07-27 | **Severity:** HIGH — safety (no AIS targets)
**Replaces the BUG-19 root-cause candidates**

### Evidence
```
ss -tlnp        → LISTEN *:10110  users:(("node",pid=2152,fd=18))     ← Signal K itself
rtl_ais journal → "AIS data will be sent to 127.0.0.1 port 10110"    ← rtl_ais is a CLIENT
nc localhost 10110 (20 s) → 0 AIVDM/AIVDO sentences; only $GPGGA/$GPRMC/$GPZDA/$GPGSV
SK vessels API  → 1 entry (self only) — ZERO AIS targets
settings.json   → pipedProvider "ais": enabled = false
```
Hardware is fine: RTL2838 present on USB, `rtl_ais` running, tuned to 162.000 MHz, internal AIS
decoder enabled, dongle serial `myAIS`.

### Root cause
Two distinct faults:
1. **Port conflict / wrong topology.** Signal K holds TCP 10110 as its **NMEA0183 output** server.
   `rtl_ais` is configured to *push* AIS to that same port as a client, so AIS is written into an
   output socket and discarded. The `ais` provider is likewise configured as a *client* to 10110 —
   if enabled it would read Signal K's own GPS output back (a loop), not AIS.
2. **Regression.** `ais` is `enabled: false`; `settings.json` mtime is 2026-03-12, so the S96 BUG-12
   fix (2026-07-11) was never applied to this Pi (see BUG-28).

### Fix steps
- [ ] Give `rtl_ais` a dedicated port (not 10110) **or** run it as a listener and point the SK provider at it
- [ ] Re-enable the `ais` pipedProvider and confirm it persists across restart
- [ ] Confirm AIVDM sentences arrive and `vessels.*` targets appear before judging BUG-19/BUG-20 overlays
- [ ] Guard against boot-order races between Signal K and rtl_ais

---

## BUG-33 — Hazard Alerting Disabled and Far Too Slow in forward-watch Config

**Status:** `[ ]` OPEN — logged S107 2026-07-27 | **Severity:** HIGH — safety
**Refines BUG-21 (not "never built" — partly a config defect)**

### Evidence
`~/.signalk/plugin-config-data/signalk-forward-watch.json`:
```json
{ "camera_ip": "10.42.0.100", "detection_interval": 300, "alert_cooldown": 30,
  "audio_alarm": false, "confidence_threshold": 0.4, "enabled": true }
```
- **`audio_alarm: false`** — the audible warning path is switched off in config
- **`detection_interval: 300`** — 300 s = **5 minutes** between detection passes; useless for a
  kayaker, swimmer or deadhead at close range
- Signal K `notifications` tree is **absent entirely** (top-level keys: environment, navigation,
  propulsion, tanks, uuid) — no hazard notifications are being published
- Cameras ARE reachable: `ping 10.42.0.100` 0% loss; startup scan found 4 RTSP hosts
  (`10.42.0.63/.100/.133/.181`). Pi is the subnet gateway (`eth0 10.42.0.1/24`)
- **Zero** forward-watch/detection lines in the last 200 Signal K journal entries

### Fix steps
- [ ] Set `audio_alarm: true`; verify the audio path end-to-end (ALSA device, per VOICE_AUDIO_FIX.md)
- [ ] Reduce `detection_interval` to a value appropriate for collision avoidance; document the CPU trade-off
- [ ] Confirm detections are published to `notifications.*` and that a consumer renders them at the helm
- [ ] Re-verify BUG-20 and BUG-21 afterwards
- [ ] **Security:** `camera_pass` is stored in plaintext and embedded in the RTSP URL — move to a secret store

---

## BUG-34 — Gauge Tap Dialog: Hardcoded Alarm String and Generic Thresholds Not Sourced From Boat Documentation

**Status:** `[ ]` OPEN — logged S107 2026-07-27 | **Severity:** MEDIUM-HIGH (E2 violation + safety gap)
**Refines BUG-16 — these are code defects independent of the BUG-29 path mismatch**

### Evidence — `overlays.js` (boat Pi)
1. **`showCrit()` is entirely hardcoded** (fabricated reading):
```js
ticker.textContent = '⛔ CRITICAL — OIL PRESSURE 8 PSI — TAKE ACTION NOW';
```
2. **Thresholds are generic JS literals, not from this boat's documentation:**
```js
{ coolant:{adv:88,alrt:98,crit:105}, oil:{adv:30,alrt:25,crit:20}, bat:{adv:12.4,alrt:12.0,crit:11.5} }
```
Compare the S106-sourced MerCruiser 454 Mag MPI values
(`MERCRUISER_454_MAG_MPI_SM_AI.md`): oil **≥30 psi @2000 rpm / ≥4 psi at idle**; thermostat
**160 °F (71 °C)**; alternator **13.9–14.7 V**. Consequences:
   - A normal **idle** oil pressure (manual floor 4 psi) is flagged **"Critical"** by `crit:20` → false alarms
   - Battery has **no upper bound** — a 15.5 V overcharging alternator renders as **"✓ Normal"** (safety gap)
3. **`_diagBuildCards()` builds only Coolant / Oil / RPM / Battery** — no fuel or depth card, although
   `_diagCellLabel()` maps `cellFuel` and `cellDepth`. Tapping those gauges yields a dialog with no matching card.
4. **Tier gate is NOT the cause** — `license.json` shows `tier: T3`; the `tier < 2` branch is not taken.
   The S106 root-cause candidate "tier gate shows upgrade screen" is **ruled out**.
5. `openDiag()` posts to a hardcoded `http://localhost:8097/gemini/chat` — works only from a browser
   running on the Pi; would fail from the PWA/phone.

### Fix steps
- [ ] Replace `showCrit()`'s hardcoded string with the live value + gauge identity
- [ ] Source thresholds from the boat/engine documentation (per E2), not JS literals; add battery upper bound
- [ ] Add fuel and depth cards, or stop offering those gauges a diagnostic dialog
- [ ] Replace the hardcoded localhost Gemini URL with a relative/configurable endpoint
- [ ] Acceptance test: each gauge tap must show **that** gauge's live value + documented range + advice on the actual reading

---

## BUG-35 — OTA Upgrade Destroys Three of the Four Fields in `version.txt`

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont** — logged S108 2026-07-27 | ACCEPT 12/12 | **NOT on the boat Pi** — latent; no OTA has ever run so the fix is unexercised | **Severity:** LOW-MEDIUM (silent metadata loss; no outage)
**Discovered** while correcting the lab Pi's stale version label in S108. **Latent — has never fired.**

### Symptom
After any successful OTA upgrade, `/opt/d3kos/config/version.txt` is reduced from four lines to
one. `Release Date`, `Status` and `Build` are permanently destroyed. No error is raised and no
service fails, so the loss is silent.

### Root cause
`ota_upgrade.py` step 7 rewrites the entire file with a single formatted line:
```python
# 7. Update version.txt
try:
    VERSION_FILE.write_text(f'd3kOS Version {latest_ver}\n')
except Exception as e:
    errors.append(f'Could not update version.txt: {e}')
```
`Path.write_text()` truncates the file. The other three fields are never re-emitted.

### The file contract it violates (4 lines — current state of the lab Pi after S108)
```
d3kOS Version 0.9.9.2
Release Date: April 12, 2026
Status: Release
Build: v0.9.9.2
```

### Affected files — 3 live copies, all with the defect at line 277
| Copy | Path | Notes |
|------|------|-------|
| Pi — service path (**live**) | `/opt/d3kos/services/cloud-agent/ota_upgrade.py` | `d3kos-cloud-agent` unit has `WorkingDirectory=/opt/d3kos/services/cloud-agent` |
| Pi — second copy | `/opt/d3kos/services/ota_upgrade.py` | **Diverged** — different md5 from the cloud-agent copy |
| Repo | `deployment/v0.9.4/pi_source/ota_upgrade.py` | Only repo copy; lives in the frozen `pi_source` tree (see BUG-28) |

md5 on the lab Pi: `7043f1d7…` (`services/`) vs `6105de65…` (`services/cloud-agent/`) — the two Pi
copies are **not** identical, so any fix must be applied to each and their divergence resolved.
There is **no** copy in `deployment/d3kOS/`, so the usual two-source-sync pairing does not apply here.

### Impact
- `export_categories.collect_version()` parses `Release Date:` and `Status:` by prefix — after an
  OTA those keys simply vanish from the export payload. No error, just missing data.
- `ota_upgrade.get_current_version()` and `cloud_agent.get_version()` keep working: both need only
  line 1. **This is why the defect is silent.**
- The S108 label correction (0.9.2.2 → 0.9.9.2, April 12 2026, Release) will be wiped by the first OTA.

### NOT the cause of the S108 stale label
`version.txt` still had all four fields with mtime **2026-03-23 20:32**, so no OTA has ever rewritten
it. The April 12 v0.9.9.2 release simply never touched `version.txt` at all — a separate gap in the
release process, recorded against BUG-28. Do not conflate the two.

### Fix steps
- [ ] Emit all four fields in step 7 (version, release date, status, build)
- [ ] Source release date / status / build from the OTA manifest rather than hardcoding them
- [ ] Apply to all three copies; resolve the `services/` vs `services/cloud-agent/` divergence first
- [ ] TDD (failing test first): invoke the version-write step, then assert
      `export_categories.collect_version()` still returns `version`, `release_date` and `status`
- [ ] Regression: `ota_upgrade.get_current_version()` and `cloud_agent.get_version()` still return the bare version

---

> ## ⚠ S108 LINEAGE CORRECTION (2026-07-27) — READ BEFORE BUG-28, BUG-29, BUG-30 OR DEP20
>
> **The two repo trees are the opposite of how S107 read them.** Verified by md5, not inference:
>
> | Evidence | Result |
> |---|---|
> | Lab Pi `instruments.js.bak.20260723` (pre-S105) | `496d9800…` = **`deployment/v0.9.4/pi_source/instruments.js`** |
> | Lab Pi `instruments.js` (current, post-S105) | `d957fb8b…` = **`deployment/d3kOS/dashboard/…/instruments.js`** |
> | Lab Pi `app.py` | `34211e37…` = **`deployment/d3kOS/dashboard/app.py`** |
>
> | Feature | `v0.9.4/pi_source` | `d3kOS/dashboard` |
> |---|---|---|
> | `_d3kEngData` (M14 cache) | **6** | 0 |
> | `/config/tier` · `/anchor/set` · `/helm/mute` | **present** | absent |
>
> **`deployment/v0.9.4/pi_source/` IS the v0.9.9.2 release tree.** It appears "frozen at Apr 8"
> because it stopped changing *at release* — not because it is stale. **`deployment/d3kOS/dashboard/`
> is a separate lineage that never contained the v0.9.9.2 features.** S107 concluded the reverse from
> commit dates alone, and BUG-28 / BUG-29 / BUG-30 / DEP20 all inherit that error.
>
> **Operator decision S108:** the lab Pi is the **master**, relabelled **v0.9.9.4 (In Development)**.
> The published v0.9.9.2 archive.org image is left as-is. A new canonical tree will be seeded
> **from the Pi**, and both old trees archived. See BUG-36 … BUG-39.

---

## BUG-36 — S105 Deploy Regressed `instruments.js`: the M14 Engine-Data Cache Was Silently Removed

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont** — logged S108 2026-07-27 | ACCEPT 13/13 | **NOT on the boat Pi** — served `instruments.js` verified `_d3kEngData` ×6 post-deploy | **Severity:** HIGH (feature loss, shipped by a "fix")
**Caused by:** the S105 BUG-15 deploy on 2026-07-23 10:12

### Evidence
| File | `_d3kEngData` | Size | md5 |
|---|---|---|---|
| `instruments.js.bak.20260723` (pre-S105) | **6** | 19,201 | `496d9800…` = `pi_source` |
| `instruments.js` (current) | **0** | 18,794 | `d957fb8b…` = `d3kOS/dashboard` |

The S105 deploy sourced the file from `deployment/d3kOS/dashboard/`, which never had the cache.
The three-line COG fix was correct; the file it was applied to was from the wrong lineage.

### Consequence
`overlays.js` line 61 reads:
```js
const eng = window._d3kEngData || {};
```
Nothing populates it now. `[UNVERIFIED INFERENCE — read from the code path, page not loaded]`
the M14 AI Engine Diagnostic renders empty cards for every gauge.

### Fix steps
- [ ] Restore `_d3kEngData` into the master's `instruments.js`, **keeping** the S105 `_lastSogKts` COG gate
- [ ] TDD: assert each SK handler writes its key into `window._d3kEngData`
- [ ] Regression: confirm the S105 COG gate still suppresses updates below 0.5 kn

---

## BUG-37 — Dashboard `app.py` Is Missing All Seven v0.9.9.2 Routes

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont** — logged S108 2026-07-27 | ACCEPT 9/9 | **NOT on the boat Pi** — health-checked: `/config/tier` 200 `{"tier":3}` (404 before), `/anchor/state` + `/anchor/advice` 200 | **Severity:** HIGH

### Evidence
Lab Pi `app.py` md5 `34211e37…` = `deployment/d3kOS/dashboard/app.py`. The v0.9.9.2 tree
(`deployment/v0.9.4/pi_source/app.py`, md5 `d06b15da…`) defines seven routes the deployed file lacks:
```
/config/tier      /anchor/set     /anchor/state    /anchor/clear
/anchor/dismiss   /anchor/advice  /helm/mute
```

### Consequence
- **This is the true root cause of BUG-26.** The S105 fix (pointing `anchor-watch.html` at
  `AI_BRIDGE` :3002) is a workaround for proxy routes that v0.9.9.2 already provides on :3000.
- `/config/tier` missing → the M14 tier gate cannot query the licence tier.
- `/helm/mute` missing → the S44 CORS fix has no server side.

### Fix steps
- [ ] Port the seven routes into the master's `app.py`
- [ ] Re-evaluate whether the BUG-26 `AI_BRIDGE` workaround should stay or revert to the proxy
- [ ] TDD: assert each route returns non-404

---

## BUG-38 — `overlays.js` Writes to Three DOM IDs That `index.html` Never Defines

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont** — logged S108 2026-07-27 | ACCEPT 15/15 | **NOT on the boat Pi** — health-checked: diagTitle/diagGrid/diagAiTxt present in the rendered page | **Severity:** MEDIUM-HIGH
**Present in the v0.9.9.2 release itself — not a deployment gap**

### Evidence
`overlays.js` (md5-identical to the v0.9.9.2 source) calls:
```js
getElementById('diagGrid')   getElementById('diagTitle')   getElementById('diagAiTxt')
```
The deployed `index.html` **matches v0.9.9.2 exactly** and defines only `id="diagBack"`.
Both repo trees' `index.html` are md5-identical (`295f287c…`) and define none of the three.
DEPLOYMENT_INDEX records these IDs as added in S39 — **that change was never committed to either tree.**

### Consequence
`getElementById` returns `null` for all three. Combined with BUG-36 the diagnostic panel has
neither data nor a container. Together these are a second, independent root cause of BUG-16.

### Fix steps
- [ ] Add `diagTitle`, `diagGrid`, `diagAiTxt` to the diag panel markup in `index.html`
- [ ] TDD: assert each ID resolves before `openDiag()` writes to it
- [ ] Add a null-guard in `overlays.js` so a missing container degrades instead of throwing

---

## BUG-39 — Cloning the Master Duplicates Six Identity Values Across Two Pis

**Status:** `[~]` **DEPLOYED TO LAB PI 2026-07-27 S108-cont — unit installed DISABLED, master GUARDED** | ACCEPT 23/23 | **NOT on the boat Pi** — Phase B (clone-procedure wiring) NOT started | **Severity:** HIGH (blocks the boat clone)
**Must be resolved before the master card is cloned to the boat**

### The duplicated identities (read from the lab Pi)
| Item | Value | Consequence if duplicated |
|---|---|---|
| `device_token` | `701e5754-e2ce-4fa3-97a6-f2c7c7e020c6` | **Most serious** — one cloud identity for two Pis; telemetry, Fix My Pi, fleet and PWA pairing all collide in `amboat_devices` |
| `installation_id` | `3861513b314c5ee7` (tier T3) | duplicate licence identity |
| Signal K vessel UUID | `urn:mrn:signalk:uuid:e1592142-…` | duplicate identity on the marine data layer |
| `machine-id` | `c654e389c17e42ceb33b756141ad0772` | duplicate host identity |
| SSH host keys | 3 private keys | host-key collisions / MITM warnings |
| Filesystem UUIDs | `d6944274…` (ext4), `F587-071F` (vfat) | a third copy joins the existing SD↔USB duplicate pair. PARTUUIDs differ so boot is safe, but UUID-based mounts are ambiguous |

### Fix steps
- [ ] First-boot regeneration script: new `device_token`, `machine-id`, SSH host keys, SK vessel UUID
- [ ] Decide whether `installation_id` / tier is per-device or per-owner before regenerating it
- [ ] Regenerate filesystem UUIDs on the clone (`tune2fs -U random`, `fatlabel`/`mlabel`) or accept and document
- [ ] Verify the boat wifi profile and the `10.42.0.1/24` camera AP exist on the card
- [ ] Acceptance: both Pis online simultaneously, each appearing as a distinct device in the CRM


---

## BUG-40 — Signal K Runs With a Different Vessel UUID Than `settings.json` Declares

**Status:** `[ ]` OPEN — logged S108 2026-07-27 | **Severity:** LOW-MEDIUM (identity/config integrity)
**Found while resolving Q39.3 for BUG-39. It removes the SK UUID from BUG-39's scope.**

### Evidence (lab Pi, Signal K v2.23.0)
| Check | Result |
|---|---|
| Live API `/signalk/v1/api/vessels/self/uuid` | `urn:mrn:signalk:uuid:e1592142-4955-4b4d-a085-40fa674e0e13` |
| `~/.signalk/settings.json` → `vessel.uuid` | `urn:mrn:signalk:uuid:af7d4be0-fb1d-4164-976d-de373c1c0331` |
| `grep -rl e1592142` over `/home/d3kos`, `/opt/d3kos`, `/etc` | **no match** |
| `~/.signalk/serverState/` | empty |
| `~/.signalk/defaults.json` | does not exist |

The configured vessel identity is **ignored**, and the identity actually in use is **not persisted
anywhere on disk**.

### Consequences
- The vessel's declared identity is not the one published on `vessels.self` to any consumer.
- **Positive side effect:** because it is not persisted, a cloned card does not duplicate it —
  which is why the SK UUID was struck from BUG-39.

### Not yet diagnosed
Whether Signal K v2 moved vessel identity to `defaults.json` (absent here) and silently ignores the
legacy `settings.json` `vessel` block, or whether the value is derived from something stable such as
`machine-id`. `Uncertainty flag: distinguishing these requires restarting Signal K and comparing the
UUID before and after — barred by the no-Pi-changes hold in force at S108.`

### Fix steps
- [ ] Restart Signal K on a non-production Pi and check whether the UUID changes → runtime-random vs derived
- [ ] Establish where SK v2.23 expects vessel identity (`defaults.json` vs `settings.json`)
- [ ] Set the vessel identity in the location SK actually reads, and confirm the API reports it
- [ ] Decide whether the boat and lab should carry distinct vessel UUIDs (relates to BUG-39)
