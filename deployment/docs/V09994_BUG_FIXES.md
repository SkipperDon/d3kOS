# v0.9.9.4 Bug Fixes — Investigation & Status
**Version:** 1.4.0 | **Created:** 2026-04-21 S65 | **Updated:** 2026-07-10 S95 | **Status:** IN PROGRESS

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
