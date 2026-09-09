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

**Status:** `[x]` **FIXED + DEPLOYED TO LAB PI S117 2026-08-02 — OPERATOR-CONFIRMED WORKING on the touchscreen ("it works"). NOT on the boat Pi.**

---

## ✅ ACTUAL ROOT CAUSE AND FIX — S117 2026-08-02

**`keyboard-fix.js` was itself the defect.** The page that loads it cannot type. The page that
does not load it types fine. Removing it fixed the bug.

**The fix, in full:** deleted line 709 of
`opt/d3kos/services/dashboard/templates/helm-assistant.html` —
`<script src="/js/keyboard-fix.js"></script>`. 711 → 710 lines. One deletion, nothing added,
no other file touched. Repo and Pi md5 `069cf629…` → `1f83498e…`, identical on both.

### How it was found — the controlled comparison nobody ran

The operator observed that the **AI** menu button opens a page where the keyboard appears **and
types**. Both pages are Flask templates on the same server, same origin, same nginx, same
Chromium, same compositor. Diffing their input paths leaves exactly one material difference:

| | `/ai-navigation` — **works** | `/helm-assistant` — **was broken** |
|---|---|---|
| `keyboard-fix.js` | **not loaded — one inline `<script>` only** | **loaded** (line 709) |
| `blur()` then `focus()` on tap | never | `keyboard-fix.js:67–68` |
| D-Bus `/keyboard/show` force-show | never called | every tap |
| Auto-focus on page load | **yes** (line 287) | no |
| Element | `<input type="text">` | `<textarea>` |

`ai-navigation.html` does nothing special. It puts an input on the page and lets Chromium work.
Tap → Chromium activates `zwp_text_input_v3` normally → squeekboard rises **through the protocol**
→ it is therefore connected to the field → typing works.

### ⚠ TWO PREMISES DISPROVED — do not rebuild on either

1. **`keyboard-api.py` docstring lines 5–6:** *"Bypasses zwp_text_input_v3 which Chromium does not
   trigger on real touch events when labwc mouseEmulation='no'."* — **FALSE.** `/ai-navigation`
   triggers it on that exact Pi, that exact compositor, every time it is used. This sentence was
   written once, never tested, and then read as documentation by every later session. Five fixes
   were built on top of it.
2. **v2.1's premise** — that page-load auto-focus is what breaks typing — is **backwards.** The
   working page auto-focuses; the broken one did not.

Bypassing `zwp_text_input_v3` while force-showing squeekboard over D-Bus produces the exact
reported symptom: **the keyboard appears and typing does nothing.** It is drawn on screen with
nothing connected to the back of it. Every fix from v2.0 through the S116 Wayland IME flags tried
to persuade Chromium to enable text-input-v3 while the show path deliberately bypassed it.

### ⚠ THE ANSWER WAS IN THIS FILE THE WHOLE TIME

Line 197 below, under **"What Was Confirmed Working"**, dated 2026-04-21:
*"AI Assistant page (ai-assistant.html) — keyboard works correctly."*
The working counter-example was recorded in the original bug report. It was filed as a supporting
observation rather than treated as the diagnostic key, and no session diffed the two pages.

**Process lesson:** when something is broken, find the nearest thing that works and diff them
before theorising. Cost of doing so here: four greps and a diff.

### Verification S117
| Check | Result |
|---|---|
| `diff` vs backup | `709d708` — one deletion only |
| Pi md5 vs repo md5 | `1f83498e…` — identical |
| `keyboard-fix` refs in Pi template | 0 |
| `/helm-assistant` via Flask **:3000** | 200 · keyboard-fix 0 · `msg-input` present |
| `/helm-assistant` via nginx **:80** (kiosk origin) | 200 · keyboard-fix 0 · `msg-input` present |
| `/ai-navigation` control | 200 — unaffected |
| `tests/bug48-no-hardcoded-localhost.spec.ts` | 19/19 pass |
| `tests/bug29-engine-path-aliases.test.js` | ALL ASSERTIONS PASSED |
| **Operator touch test on the Pi screen** | **PASS — "it works"** |

Both origins were measured deliberately; testing only `:3000` is what produced the wrong S116
diagnosis recorded below.

### Deliberately NOT done (no BUG-XX entry exists — operator instruction S117)
- `helm.html`, `ai-assistant.html`, `settings.html`, `marine-vision.html` still load
  `keyboard-fix.js`. **Not reported as broken, so not touched.** If one is found broken it gets
  logged first like anything else.
- `keyboard-fix.js` left on disk; `keyboard-api.py` and `d3kos-keyboard-api.service` left running
  — the service also provides `/window/*` for the fullscreen toggle and is not keyboard-only.
- squeekboard left running. No compositor change, no launch-flag change, no reboot.

### Rollback
- Pi: `cp /opt/d3kos/services/dashboard/templates/helm-assistant.html.pre-bug08-20260802_095322.bak <target>` then `sudo systemctl restart d3kos-dashboard`
- Repo: `.aao-backups/20260802_095322_S117/deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/helm-assistant.html.bak`

---

### ⚠ ROOT CAUSE CORRECTED S116 — the earlier analysis was against the wrong page
*(retained for history — superseded by the S117 section above)*

Everything below under "Root Cause Analysis" was investigated against
`/var/www/html/helm.html`, served by **nginx on :80**. **That is not the page the kiosk runs.**
The kiosk target is `http://localhost:3000/` — the **Flask dashboard** — whose
`templates/helm-assistant.html` loaded the script as:

```html
<script src="/js/keyboard-fix.js"></script>   <!-- absolute nginx path -->
```

Flask serves static from `/static/`, so on `:3000` that returned **404**.
**`keyboard-fix.js` had never loaded on the live page at all.** Measured S116:

| URL | Flask :3000 (kiosk) | nginx :80 (old page) |
|---|---|---|
| `/js/keyboard-fix.js` | **404** | 200 |
| `/static/js/keyboard-fix.js` | **404** (file absent) | n/a |
| `POST /keyboard/show` | **404 — no route** | 200, proxied to `127.0.0.1:8087` |

A **second blocker** sat behind the first: `keyboard-fix.js` POSTs to origin-relative
`/keyboard/show`. nginx proxies `/keyboard/` to the keyboard API on **127.0.0.1:8087**, but Flask
had no such route — so even a loaded script could not have reached the API.

The v2.1 blur/`_recentlyShown` timing work was therefore never exercised on the live page. It may
or may not be sufficient; that is now **testable for the first time**.

### FIX APPLIED S116 (4 files)
1. **`static/js/keyboard-fix.js`** (new, v2.2) — the script now exists in the Flask static tree.
2. **`templates/helm-assistant.html`** — `src` switched to
   `{{ url_for('static', filename='js/keyboard-fix.js') }}`.
3. **`app.py`** — added a `/keyboard/<action>` proxy route (`show`/`hide` only) forwarding to
   `127.0.0.1:8087`. Kept origin-relative on the client so the hardcoded-localhost defect class
   from BUG-46/48 is not reintroduced.
4. **v2.2 same-machine guard** — since BUG-46 the dashboard is reachable from a phone or laptop.
   squeekboard exists only on the Pi's own display, so without a guard a remote tap would raise a
   keyboard **at the helm**. The script now no-ops unless the page host is localhost/127.0.0.1.

### Verified S116 — 5/5 `tests/bug08-keyboard-fix-wiring.spec.ts`
- `/static/js/keyboard-fix.js` → **200** (was 404)
- `helm-assistant` emits `src="/static/js/keyboard-fix.js"`; the old `/js/` path must not return
- `POST /keyboard/show` and `/keyboard/hide` → **200 `{"ok":true}`** (was 404) — squeekboard invoked
- `POST /keyboard/bogus` → 404
- **A touch on the textarea from a REMOTE host sends no `/keyboard/*` call** — guard holds

### ⚠ WHAT IS NOT PROVEN — operator action required
These tests cover the **plumbing**, which is what was broken. They **cannot** prove that
squeekboard visually appears and accepts keystrokes — that is real touch-input behaviour on the
Pi's own display, involving `zwp_text_input_v3` registration that a headless browser cannot
reproduce. **Operator must tap the Helm Assistant textarea on the Pi touchscreen and confirm the
keyboard appears AND types.** If it appears but cannot type, the v2.1 blur/timing analysis below
becomes live again — and is now actually reachable.

### ⚠ CORRECTION TO MY OWN S116 DIAGNOSIS — the script WAS loading

The "never loaded" claim above is **WRONG** and is recorded as a recovery event.

nginx `location /` **proxy_passes to 127.0.0.1:3000**. The kiosk launches
`chromium --app=http://localhost/` — port **80** — so the operator sees the Flask dashboard
*through nginx*. On :80, `/js/keyboard-fix.js` is served by nginx from `/var/www/html/js/` and
returns **200**. I measured port 3000 directly instead of the kiosk's real origin, and stated
"the script never loaded" as fact.

What the S116 change actually achieved (still net-positive, but not a load fix):
- direct `:3000` access now works (it genuinely was 404 there)
- Flask has its own `/keyboard/*` routes (nginx already proxied these on :80, so redundant for the
  kiosk but correct for direct access)
- **v2.2 same-machine guard is genuinely new and valuable** — post-BUG-46 a remote tap would
  otherwise raise the keyboard at the helm

### SYMPTOM 2 ROOT CAUSE — CONFIRMED S116, operator-verified on the touchscreen

Operator confirms: **the keyboard appears, but typing produces nothing in the input.** The D-Bus
show path works; the keystrokes have nowhere to go.

**Chromium is launched without Wayland IME support.** Live read of the running process
(Chromium 144.0.7559.109, Debian trixie) shows `--ozone-platform=wayland` present but **neither**
`--enable-wayland-ime` **nor** `--wayland-text-input-version=3`. Without those, Chromium never
registers a `zwp_text_input_v3` client, so squeekboard has no text-input target — it renders and
swallows every key.

Source (researched S116, not inferred):
- <https://issues.chromium.org/issues/40113488> — Ozone-wayland text_input_v3 support
- <https://github.com/swaywm/sway/issues/8276> — the flags are
  `--enable-wayland-ime --wayland-text-input-version=3`; **labwc is reported working**, unlike sway
- <https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland> — same flag set for Wayland IME

This also explains why the v2.1 `el.blur()`/`el.focus()` trick could never work: it tries to force
re-registration of a protocol **Chromium was never told to speak**.

### Proposed fix — NOT applied, needs operator approval (HIGH risk)
Add to `/home/d3kos/.config/autostart/d3kos-browser.desktop`:
```
--enable-wayland-ime --wayland-text-input-version=3
```
⚠ **This changes the kiosk browser launch line.** If it is wrong the helm display may not come up,
and it only takes effect after a session restart or reboot. Needs a tested rollback and should be
done while the operator can see the screen.

Possible bonus: with text-input-v3 active, Chromium may raise the keyboard itself on focus, making
the `/keyboard/show` D-Bus hack redundant. Do not remove it until that is proven.

### Original analysis (retained — but note it targets the nginx page, not the live one)

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

**Status:** `[x]` **NOT A BUG — CLOSED S117 2026-08-02 by operator decision on the evidence below.**
No AvNav corruption has ever been observed, captured or reproduced. Every investigation of the
symptom found a different, real, non-corruption cause — both of them already identified and one
already fixed (S96). The record's "confirmed root cause" was an unverified inference from a
symptom report and should never have been written as fact.

**What the symptom actually was (S96, on the boat):** (1) a serial port conflict flooding the logs
— **fixed**; (2) a blank chart screen caused by an **expired o-charts licence**, with the chart
files intact on disk — a renewal (OB-O05), not a defect.

**Part 2 of this bug — the system-wide self-healing audit — was not a defect either.** It was a
hardening idea bundled into a bug record. **MOVED to the v0.9.9.5 backlog by operator decision
S117 2026-08-02** → `V09995_DISCUSSION_PLAN.md` **§14 — Unclean-Shutdown Hardening**, and
`PROJECT_CHECKLIST.md` PART 20 row **D14**. All the S117 live-read findings below (filesystem,
AvNav's own config self-healing, the write surface, the unconfigured hardware watchdog, the absence
of hold-up power) were carried across so they do not have to be re-derived. **Do not re-enter this
in the bug tracker** — it returns only if an actual corruption event is observed and captured.

**Platform:** Pi (primary); all d3kOS services (secondary audit scope)

---

## ⛔ OPERATOR INSTRUCTION — S117 2026-08-02: DO NOT BUILD A WATCHDOG FOR THIS

**A watchdog is not the solution to BUG-09 and must not be proposed or built for it.**

A watchdog restarts a service that is dead or hung. Power-cut damage is to data at rest.
Restarting AvNav against damaged files fails again — and this project already has a worked
example of that going wrong: **BUG-23a**, fixed S116, where a watchdog hot-looped on a fault it
could not repair, burning **39% CPU** and writing **~2,536 log lines per minute**. Do not
recreate that on the navigation system.

---

## ⚠ THE "CONFIRMED ROOT CAUSE" BELOW IS NOT CONFIRMED — READ BEFORE DESIGNING ANYTHING (S117 2026-08-02)

The Symptom and Known Root Cause sections below state as established fact that power loss
corrupts AvNav data. **That was never verified.** It was recorded in S94 from an operator
observation of the symptom, and has been carried forward unchallenged ever since.

**Every time this symptom has actually been investigated, the cause turned out NOT to be
corruption.**

### S96 (2026-07-11) — investigated ON THE BOAT, found two real non-corruption causes

The session goal was literally *"AvNav file looks corrupt"*. It was not corrupt. Two separate
faults were found, both of which make AvNav **look** broken:

1. **Serial port conflict — FIXED S96.** `AVNUsbSerialReader` was repeatedly opening
   `/dev/ttyACM0` (the u-blox GPS) at every baud rate in turn, while gpsd already held that port
   exclusively for Signal K. A perpetual error loop that flooded the logs and wasted resources.
   AvNav was never actually down — `AVNSignalKHandler` was supplying GPS from Signal K on :8099
   the whole time, and the router log showed live navigation (tracking waypoint "Marker" at
   lat 42.895). **Fix applied to the boat's `/var/lib/avnav/avnav_server.xml`:**
   ```xml
   <UsbDevice usbid="1-1.4:1.0" type="ignore"/>
   ```
   Verified: `STATUS[1-1.4:1.0] INACTIVE, /dev/ttyACM0 configured to be ignored`. Survived reboot.
   ⚠ **This rule is on the BOAT ONLY.** Verified S117: on the lab Pi every `UsbDevice` line in
   `AVNUsbSerialReader` is commented out and `allowUnknown="true"` — the fix is absent. Same
   version-control exposure as the BUG-19/20 fix: `avnav_server.xml` is not in the repo.

2. **Blank chart screen — NOT a software fault at all.** o-charts Canada licences (CAac + CAgl)
   expired **2026-04-01**. Chart files were **intact on disk** (1.3 GB); ochartsng simply refuses
   to decrypt them without a valid licence — `"active": false`, `"errors": 741/741`,
   `"numValidCharts": 0`. Requires a subscription renewal, tracked as **OB-O05 (still blocking)**.
   Nothing to repair, nothing to code.

**S96's own session log recorded that this bug's scope needed revising** — *"BUG-09 scope update
needed… the AvNav-specific issue was not file corruption but license expiry."* **That update was
never made.** The unrevised premise then very nearly caused a corruption-repair system to be
designed in S117 for a problem that may not exist. Same failure as BUG-08: a premise written once,
never re-tested, then built upon.

### Further corrections established S117 by live read of the lab Pi

- **R1 — the data path in this record is WRONG.** It says `/home/d3kos/.avnav/`. **That directory
  does not exist.** AvNav runs as `ExecStart=/usr/bin/avnav -q -b /var/lib/avnav`, and
  `/var/lib/avnav` holds 1.4 GB. Anything designed against the recorded path would have protected
  an empty directory.
- **R2 — ANSWERED: yes, AvNav already self-heals its own config.** Verified in AvNav's source,
  `/usr/lib/avnav/server/avnav_manager.py:249`: `getFallbackName()` returns `<cfg>.ok` (or
  `.initial`), and `getInvalidName()` renames a bad config to `.invalid-<UTC timestamp>`. On the Pi
  now: `avnav_server.xml.ok`, rewritten after each successful start. **Config corruption is already
  handled by AvNav. Do not build a config repair step.**
- **The live write surface is tiny.** In 24 h only **14 files** changed — log files, GPS tracks,
  and the `.ok` config copy. Of the 1.4 GB, `ochartsng` is 1.4 GB and effectively static; only its
  logs changed. `tracks` 3.4 MB, `log` 576 KB; routes/user/settings under 60 KB combined.
- **Filesystem exposure:** single ext4 root on the SD card (`/dev/mmcblk0p2`, `defaults,noatime`,
  117 G, 22% used). ext4's default journalling protects filesystem *metadata*, not file *contents* —
  a file mid-write at power-off can be left torn while the filesystem itself checks out clean. SD
  cards add independent risk (the flash translation layer can lose a whole block on power loss).
- **Hardware watchdog exists and is unconfigured** — `/dev/watchdog` and `/dev/watchdog0` are
  present; `RuntimeWatchdogSec` is not set in `/etc/systemd/system.conf`. This addresses the Pi
  **hanging**, which is a different failure from corruption. Noted for completeness; per the
  operator instruction above it is not a BUG-09 fix.
- **No UPS, supercapacitor, or power-fail shutdown service exists.** The only measure that actually
  prevents an unclean shutdown is giving the Pi enough hold-up power to shut down properly. That is
  hardware and is not specified here — no product has been researched.
- **The lab Pi cannot currently reproduce either S96 condition:** it has no u-blox on USB and its
  ochartsng also returns `{"data": []}` — zero charts.

### What is genuinely still unknown
R3, R4 and R5 remain unanswered, and **no instance of actual AvNav file corruption has ever been
observed, captured, or reproduced.** Before any repair mechanism is specified, someone must
establish that files are in fact being damaged, and which ones. Until then the honest status of
this bug is: **symptom reported; every investigation to date found a different cause.**

---

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

**Status:** `[–]` **MOVED TO v0.9.9.5 — S117 2026-08-02 (operator decision).**
Not a defect — an unbuilt capability with no root cause and no design, logged S95 and never started.
→ `V09995_DISCUSSION_PLAN.md` **§15 — Universal Device Health Framework**, and
`PROJECT_CHECKLIST.md` PART 20 row **D15**.

⚠ **BUG-50 STAYS in v0.9.9.4 and must NOT be folded into D15.** BUG-50 is the proven, bounded piece
of this problem: the Settings page reports **GPS, AIS, OpenPlotter and AvNav as green while they are
dead** — verified live S117 (GPS green while `navigation/position` returns 404; AIS green while
Signal K holds zero targets). Fixing BUG-50 produces the working reference implementation that D15
generalises. **D15 additionally covers microphone and speaker**, which have no data stream to watch
and may need active probing. **Do not re-enter this in the bug tracker.**

The original research material below is retained — it was carried into D15 rather than discarded.
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

**Status:** `[x]` **SUPERSEDED BY BUG-32 — CLOSED S111 2026-07-29.** The S96 fix recorded below was invalid — SK TCP 10110 is SK's own NMEA0183 output; the ais pipedProvider as a client to that port looped SK's GPS back. Real fix: BUG-32 — rtl_ais as TCP server on 10108, SK ais provider as client (fixed S110-cont, lab Pi; on-boat validation pending). Historical record below retained — do not apply.

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

**Status:** `[~]` FIXED (lab) — Issue 1 requires on-boat validation (throttle change needed to confirm debounce resolves flicker); Issue 2 resolved (context menu title shows live value)
**Logged:** 2026-07-11 S97 (reported on-boat by Don) | **Fixed:** 2026-07-29 S110
**Platform:** Pi (d3kOS dashboard — speed gauge tile)

### Fix Applied (S110 — 2026-07-29)

Root cause confirmed from source code investigation:

**Issue 1 — Flicker:** `navigation.speedOverGround` handler called `_setVal('cellSpeed', kts)` on
every WebSocket message. Signal K publishes SOG from all bus sources — Garmin (src 0, live GPS)
and Pangoo (src 64, lagged/cached). During throttle changes the two sources interleave, causing
the display to alternate between them every ~100–200 ms.

**Fix:** Added 250 ms display coalesce timer (`_sogPending` + `_sogDisplayTimer` state vars).
`_lastSogKts` is still set immediately (COG suppression at line 152 unaffected). Multiple
updates within one 250 ms window collapse to a single render of the last received value.
`[ASSUMED]` root cause is multi-source interleaving; if on-boat flicker persists, escalate
to SK subscription-level source filtering.

**Issue 2 — Context menu:** `openCtx(e, name)` set `ctxTtl.textContent = name` only — no live
value visible when menu covered the tile.

**Fix:** Added `e.target.closest('.ic')` traversal + `.ic-v` read before setting the title.
Title now shows `"Speed SOG — 8.2"` when the cell is populated, `"Speed SOG"` when `'---'`.
Applies to all tiles universally (not speed-only).

**File changed:** `static/js/instruments.js` — Changes A (2 new state vars) + B (SOG handler debounce) + C (openCtx live value)
**Tests:** `tests/bug13-speed-gauge.test.cjs` — 5 tests; 2 + 4 failed before fix, all 5 pass after.
**Atomic spec:** `deployment/docs/atomic-specs/BUG-13.md`
**Deployed to lab Pi:** pending (deploy batch with Group B/C)

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

**Status:** `[x]` **CLOSED S118 2026-08-03 — operator confirms the tach wire is now PERMANENTLY
CLIPPED.** This supersedes the S112 finding that CX5106 src 106 was absent from the bus because the
blue Pole 3 RPM-gauge wire had never been permanently connected.
⚠ **Not yet re-verified on the N2K bus.** Confirm src 106 appears in Signal K on the next boat
visit — closing the wiring task is not the same as observing the data.
⚠ **S119 2026-08-04 ON-BOAT VERIFICATION FAILED.** With ignition on and engine RUNNING (operator
confirmed, tach wire permanently clipped): src 106 present on bus, but sending **heartbeat PGN
126993 only (1 frame / 60 s) — zero data PGNs** (no 127488/127489/127505) over 60 s of candump.
Device power, CAN transmitter, cable, and bus all proven good by the heartbeat. Same signature on
both units — the S98 "defective unit" diagnosis was almost certainly wrong. Remaining unknowns are
on the sensor-input/DIP side. No published CX5106 manual exists (Matsutec/iMarinex/Premier Cable
checked S119); the paper leaflet in the box is the only DIP-switch authority. Garmin (src 0) also
absent from the bus during the capture — plotter state unconfirmed. **Operator to decide whether to
reopen.** Reopen decision pending; checkbox left as closed S118.
**Logged:** 2026-07-13 S98 (on-boat, Monterey 265 SEL, Pi IP 172.20.10.8)
**Updated:** 2026-07-20 S101 — new unit confirmed on NMEA 2000 bus; 2026-08-04 S119 — closure
verification failed (heartbeat only, engine running)
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

**Status:** `[~]` **FIXED IN LAB — S107; this entry CORRECTED S114 2026-07-31.** It previously read `[ ]` OPEN, which contradicted `PROJECT_CHECKLIST.md` and was **wrong**. Verified S114 against the served file on the lab Pi: `instruments.js:169` holds the guard `if (_lastSogKts !== null && _lastSogKts < 0.5) return;` — COG is not updated below 0.5 kt. **NOT on the boat Pi**; on-boat validation still required. **Note:** likely the same underlying defect as BUG-13 (no smoothing/deadband on a noisy low-speed signal) — validate the two together.
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

**Status:** `[x]` **CLOSED S116 2026-08-01 — RESOLVED BY BUG-34/BUG-36, verified with LAB-SIM.**
`openDiag()` in `overlays.js` now builds its cards from `window._d3kEngData` — the **live** Signal K
cache restored by BUG-36 — and sends the live readings to Gemini. Nothing is hardcoded.
**Verified S116** by injecting distinctive healthy values that a hardcoded dialog could not reproduce:
oil 47 PSI, RPM 2350, coolant 77 °C, battery 13.7 V. The live cache held exactly those, and the
rendered `#diagGrid` contained `47` and `2350`. The specific on-boat symptom — an oil alarm shown
while the gauge read normally — was also disproved: at 47 PSI (above adv 30 / alrt 25 / crit 4)
`#cellOil` carries no alarm class. Test: `tests/bug16-18-24-labsim-verification.spec.ts`.
⚠ Note: the preliminary root cause below cited `deployment/v0.9.4/pi_source/overlays.js`, which is a
SUPERSEDED read-only tree. The live file is `deployment/v0.9.9.4/.../static/js/overlays.js`.
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

**Status:** `[x]` **CLOSED S118 2026-08-03 — NOT IN SCOPE.** Operator decision: battery
monitoring is no longer part of this build. The dashboard cell was already removed S113 and no
sensing hardware will be fitted for v0.9.9.4. If battery monitoring returns it is a NEW feature
request, not this defect.
**Logged:** 2026-07-20 S101 (on-boat, Monterey 265 SEL)
**Platform:** Pi (d3kOS dashboard — battery/electrical display)

### Symptom
Battery voltage tile on d3kOS dashboard shows no data. Signal K path `/vessels/self/electrical/` returns empty. No battery voltage, no alternator voltage, no electrical data of any kind.

### Confirmed S101
```
curl -s http://localhost:8099/signalk/v1/api/vessels/self/electrical/
→ Empty response (no JSON data)
```

### Root Cause — FULLY INVESTIGATED S113 2026-07-31

Three sources investigated and eliminated:

**1. CX5106 — CONFIRMED CANNOT provide battery voltage**
The CX5106 reads resistance-based analog senders only (0–190 Ω / 240–33 Ω ranges).
Battery voltage is a direct DC voltage measurement — the device has no voltage input terminal.
The prior hypothesis about a "BAT+ terminal" was incorrect.
Source: iMarinex CX5106 product specification (confirmed S113 via WebSearch).

**2. signalk-rpi-monitor — CONFIRMED does not publish electrical data**
Plugin is running and publishing: CPU/GPU temperature, CPU utilisation, memory usage, SD card usage.
No power supply or battery voltage data. Pi 5 hardware (hwmon1/rpi_volt) exposes only an
under-voltage alarm flag (0/1) — not an actual voltage measurement.
Confirmed S113 via live SK API query: `environment.rpi.*` tree contains no electrical data.

**3. Garmin chartplotter — NOT an acceptable solution**
Garmin can publish PGN 127508 (Battery Status) but requires the chartplotter to be powered on.
Independent battery monitoring when Garmin is off is a hard requirement.

### Hardware Required
Dedicated battery monitor needed. Two viable options:
- **Victron SmartShunt 500A** + VE.Direct USB cable → SK plugin `signalk-victron-ble` (~$130 CAD)
- **INA219 I2C module** → wired to Pi GPIO + SK plugin `signalk-raspberry-pi-ina219` (~$8 CAD)
Both provide voltage + current at all times (engine on or off).

### Interim Action — S113 2026-07-31
Battery cell (`cellBat`) removed from dashboard `index.html`. The cell was showing `—`
permanently with no data source. All JS handlers preserved — cell will be restored once
hardware is in place.

### Signal K Path (when hardware is installed)
```
electrical.batteries.0.voltage   ← existing handler in instruments.js, correct
```

### Relation to BUG-14
Independent of BUG-14 — even when CX5106 is fully operational, it cannot provide battery voltage.

---

## BUG-18 — Depth Gauge Not Registering on d3kOS Dashboard

**Status:** `[x]` **CLOSED S116 2026-08-01 — RESOLVED BY BUG-30, verified with LAB-SIM.**
Root cause was candidate 3 ("Signal K receiving but d3kOS reading wrong path"): the dashboard read
`environment.depth.belowKeel` while Signal K publishes `belowTransducer`. Fixed under BUG-30.
**Verified S116** by injecting depth into Signal K and asserting the rendered DOM:
`#cellDepth .ic-v` shows `3.8`, and tracks a change 0.9 → 3.8. Test:
`tests/bug16-18-24-labsim-verification.spec.ts`. No further work — this entry is superseded by BUG-30.
**Logged:** 2026-07-20 S103
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

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S115 2026-08-01** — root cause found and fix proven end-to-end | **NOT on the boat Pi**
**Fix:** added `fetchAis="true" aisQueryPeriod="5"` to `<AVNSignalKHandler>` in `/var/lib/avnav/avnav_server.xml`; restarted avnav.
**Before:** AvNav status `ais INACTIVE disabled`. **After:** `ais NMEA read 2 targets`.
**End-to-end proof (S115):** injected two vessels into Signal K — one shaped exactly like a
`signalk-forward-watch` detection (`mmsi:800000002`, `FW-BOAT (87%)`) and one ordinary
AIS-style target (`mmsi:316001234`). AvNav's AIS API returned BOTH with correct position,
name and course. Test vessels cleared afterwards via a Signal K restart.
⚠ `avnav_server.xml` is a **Pi-only config** at `/var/lib/avnav/` — it is NOT in the canonical
repo tree, so it is not version-controlled. It travels with the SD-card clone. Backup on the
lab Pi: `avnav_server.xml.pre-bug19-20260731_223321.bak`.
**Logged:** 2026-07-21 S104
**Platform:** Pi (AvNav chart display)

### Root Cause — FOUND S115 2026-08-01 (live read, AvNav source + status API)

**AvNav has never asked Signal K for AIS.** It is a single missing attribute.

`/usr/lib/avnav/server/handler/signalkhandler.py:663`
```python
P_AIS = WorkerParameter('fetchAis', type=T_BOOLEAN, default=False,
                        description='fetch AIS data from signalK')
```

The boat/lab config is:
```xml
<AVNSignalKHandler uuid="..." migrated="True" port="8099" decodeData="true"/>
```
**No `fetchAis` attribute** → defaults to `False` → line 284 sets
`aisFetchPeriod = 0` → line 1013 marks AIS `disabled` → line 1209
(`if aisFetchPeriod > 0`) never calls `fetchAisData()`.

**Confirmed live** on the lab Pi via AvNav's own status API:
```
handler: SignalKHandler
   main       NMEA       connected at http://localhost:8099/signalk/v1/api/
   ais        INACTIVE   disabled          <-- here
   websocket  NMEA       connected at ws://localhost:8099/signalk/v1/stream
```
The Signal K connection is healthy. Only the AIS fetch is switched off.

### Proposed fix (NOT applied — needs operator approval)
Add `fetchAis="true"` (and optionally `aisQueryPeriod`, default 10 s) to the
`AVNSignalKHandler` element in `avnav_server.xml`, then restart AvNav.
This is a config change to the master card — it clones to the boat.

### ⚠ BUG-19 and BUG-20 ARE THE SAME DEFECT
`signalk-forward-watch` does NOT emit AIS, NMEA 0183 or NMEA 2000. Its
`plugin/opencpn-output.js` writes each detection into Signal K as a **fake vessel**
under `vessels.urn:mrn:imo:mmsi:80000000X` with `navigation.position`, `name`
(e.g. `FW-BOAT (87%)`), COG and SOG=0.

Those fake vessels live in the **same Signal K vessel tree** as real AIS targets,
so they arrive through the **same `fetchAisData()` path**. Enabling `fetchAis`
should therefore fix BUG-19 **and** BUG-20 together. Validate both in one test.
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

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S115 2026-08-01** — root cause found and fix proven end-to-end | **NOT on the boat Pi**
**Fix:** added `fetchAis="true" aisQueryPeriod="5"` to `<AVNSignalKHandler>` in `/var/lib/avnav/avnav_server.xml`; restarted avnav.
**Before:** AvNav status `ais INACTIVE disabled`. **After:** `ais NMEA read 2 targets`.
**End-to-end proof (S115):** injected two vessels into Signal K — one shaped exactly like a
`signalk-forward-watch` detection (`mmsi:800000002`, `FW-BOAT (87%)`) and one ordinary
AIS-style target (`mmsi:316001234`). AvNav's AIS API returned BOTH with correct position,
name and course. Test vessels cleared afterwards via a Signal K restart.
⚠ `avnav_server.xml` is a **Pi-only config** at `/var/lib/avnav/` — it is NOT in the canonical
repo tree, so it is not version-controlled. It travels with the SD-card clone. Backup on the
lab Pi: `avnav_server.xml.pre-bug19-20260731_223321.bak`.
**Logged:** 2026-07-21 S104
**Platform:** Pi (camera detection → AvNav integration)

### Root Cause — FOUND S115 2026-08-01 (live read, AvNav source + status API)

**AvNav has never asked Signal K for AIS.** It is a single missing attribute.

`/usr/lib/avnav/server/handler/signalkhandler.py:663`
```python
P_AIS = WorkerParameter('fetchAis', type=T_BOOLEAN, default=False,
                        description='fetch AIS data from signalK')
```

The boat/lab config is:
```xml
<AVNSignalKHandler uuid="..." migrated="True" port="8099" decodeData="true"/>
```
**No `fetchAis` attribute** → defaults to `False` → line 284 sets
`aisFetchPeriod = 0` → line 1013 marks AIS `disabled` → line 1209
(`if aisFetchPeriod > 0`) never calls `fetchAisData()`.

**Confirmed live** on the lab Pi via AvNav's own status API:
```
handler: SignalKHandler
   main       NMEA       connected at http://localhost:8099/signalk/v1/api/
   ais        INACTIVE   disabled          <-- here
   websocket  NMEA       connected at ws://localhost:8099/signalk/v1/stream
```
The Signal K connection is healthy. Only the AIS fetch is switched off.

### Proposed fix (NOT applied — needs operator approval)
Add `fetchAis="true"` (and optionally `aisQueryPeriod`, default 10 s) to the
`AVNSignalKHandler` element in `avnav_server.xml`, then restart AvNav.
This is a config change to the master card — it clones to the boat.

### ⚠ BUG-19 and BUG-20 ARE THE SAME DEFECT
`signalk-forward-watch` does NOT emit AIS, NMEA 0183 or NMEA 2000. Its
`plugin/opencpn-output.js` writes each detection into Signal K as a **fake vessel**
under `vessels.urn:mrn:imo:mmsi:80000000X` with `navigation.position`, `name`
(e.g. `FW-BOAT (87%)`), COG and SOG=0.

Those fake vessels live in the **same Signal K vessel tree** as real AIS targets,
so they arrive through the **same `fetchAisData()` path**. Enabling `fetchAis`
should therefore fix BUG-19 **and** BUG-20 together. Validate both in one test.
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

**Status:** `[~]` RESOLVED by BUG-33 config fix — pipeline confirmed built end-to-end — S110 2026-07-29. On-boat validation required.
**Logged:** 2026-07-21 S104 | **Resolved:** S110 2026-07-29
**Platform:** Pi (hazard warning system)
**Operator report:** Blocking — cannot use d3kOS as a situational awareness tool without this

### S110 Resolution Note (2026-07-29)
BUG-21 was originally logged as "pipeline likely not built." S110 investigation confirmed the pipeline IS built end-to-end in `signalk-forward-watch`:
- `index.js`: ONNX model loaded; detection loop runs every `detection_interval` seconds; `sendDetections()` publishes to `environment.forwardWatch.detections`; early exit `if (!framePath) return` when RTSP grab fails (camera unreachable in lab = expected)
- `signalk-output.js`: notifications fire for detections with GPS + distance; `playBeep()` calls `paplay`/`aplay` when `audio_alarm: true`
- The only issues were the BUG-33 config values: `detection_interval: 300` (5-minute gap) + `audio_alarm: false`
- **BUG-33 config fix resolves BUG-21.** No code changes needed. On-boat validation required to confirm detections flow and audio fires when camera is reachable.

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

**Status:** `[x]` NOT A BUG — CLOSED S111 2026-07-29. S107 confirmed on-boat: `vessel.env` exists at `/opt/d3kos/services/dashboard/config/vessel.env`; wizard gate behaves as designed. B-01/B-02 test failures occurred on a configured system (vessel.env populated from a prior session) — not a routing defect.
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

**Status:** `[~]` PARTIAL — **BUG-23a code defects (spin loop + stderr hidden) FIXED + DEPLOYED LAB PI S116 2026-08-01** (see subsection below). Full voice note transcription (STT / Faster-Whisper) is a v0.9.9.5 D13 feature — not a bug fix. Remaining open item: boat Pi not yet validated (no mic connected to lab Pi — fix was verified by CPU/log metrics). (Was: `[~]` DIAGNOSED 2026-07-23)
**Logged:** 2026-07-21 S104
**Platform:** Pi (Boat Log — voice note feature)
**Checklist:** H-03 (failed)

### BUG-23a ROOT CAUSE — FOUND S116 2026-08-01 (live read on the lab Pi)

**The watchdog is not the bug. It is correctly reporting a real, ongoing fault.**

`d3kos-voice.service` is **active and running**, but with **1 thread and no `arecord` child**.
The Vosk listener thread dies the instant it starts, and the main loop respawns it immediately —
forever.

`/opt/d3kos/services/voice/voice-assistant-hybrid.py:355-366`
```python
while True:
    if self._mic_locked:
        time.sleep(0.5); continue
    if not listener_thread.is_alive():
        print("▶  Resuming wake word detection...", flush=True)
        listener_thread = threading.Thread(target=wake_word_listener, daemon=True)
        listener_thread.start()
        print("🎤 Listening for wake words...", flush=True)
```
**There is no sleep, no backoff and no failure limit on the restart path.**

`/opt/d3kos/services/voice/wake_word_vosk.py:117-123`
```python
self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)   # <-- error discarded
```
The `arecord` failure reason is **thrown away**, which is why this was never diagnosable from logs.

#### Measured impact on the lab Pi (S116)
| | |
|---|---|
| Voice service CPU, continuous, doing nothing useful | **6.3%** |
| Log lines written in 60 s | **1,812** (~30/s) |
| Total journal lines accumulated for this unit | **449,642** |
| Threads (expected 2+) | **1** |
| `arecord` children | **0** |

#### Why the thread dies HERE — environmental, lab only
`arecord -l` on the lab Pi returns an **empty capture list** — there is no microphone. The device
is also **hardcoded**: `wake_word_vosk.py:82` falls back to `plughw:0,0`, and card 0 on this Pi is
`vc4hdmi0` (HDMI **playback**, no capture). `wake_word_porcupine.py:41` hardcodes
`plughw:S330,0` separately.

#### THREE distinct defects — the first two are REAL CODE BUGS on every platform
1. **No backoff in the respawn loop** — spins ~30×/s indefinitely. Burns CPU and floods the journal.
   On a boat this is continuous **SD-card write wear**. Possibly a contributor to the 79–87% CPU
   recorded during the S112 cruise.
2. **`stderr=subprocess.DEVNULL` hides the cause** — the ALSA error never reaches the log.
3. **No microphone on the lab Pi** (environmental) plus a **hardcoded capture device** — this is
   what triggers 1 and 2 here. **On the boat a mic exists, so BUG-23a may not reproduce there —
   but defects 1 and 2 will fire the moment the mic drops out (USB dropout, brownout).**

#### FIX APPLIED + DEPLOYED TO LAB PI — S116 2026-08-01 (operator-approved)

| Metric (steady state, 60 s) | Before | After |
|---|---|---|
| Voice service CPU | **39%** | **0.03%** |
| Log lines written | **~2,536** | **4** |
| Watchdog result | `failed` every tick | clean exit |

**1. Respawn backoff** — `voice-assistant-hybrid.py`. Ladder 1→2→5→15→30 s with a
consecutive-failure counter. A listener that lives <2 s counts as a failure; a longer-lived one
resets the counter. Backoff is honoured via a deadline (not a blocking sleep) so the `_mic_locked`
check stays responsive. Per-attempt logging stops after 5 failures, with a DEGRADED message stating
the real cause, then a heartbeat every ~20 attempts so a persistent fault stays visible.

**2. `arecord` stderr captured** — `wake_word_vosk.py`. Was `subprocess.DEVNULL`. Now `PIPE`, with a
0.3 s liveness check: if the process already exited, the real message is stored on
`detector.last_error` and logged once. The log finally shows the actual cause:
`arecord: main:850: audio open error: No such file or directory`.

**3. Watchdog no-capture-hardware guard** — `/opt/d3kos/scripts/voice-watchdog.sh`. If
`arecord -l` lists no card, it logs once and exits 0. Previously it restarted the voice service on
every timer tick, which **reset the new backoff and caused a fresh log burst each time** — the
watchdog was fighting the fix. A missing microphone cannot be restarted into existence.

**4. Honest startup message** — the final device fallback said "Using default mic: plughw:0,0" when
no capture device existed at all. It now states plainly that voice INPUT is unavailable and that TTS
is unaffected.

⚠ **Deliberately NOT changed:** the fallback still returns a device rather than `None`. Returning
`None` sets `all_ok = False` in `check_dependencies()`, which aborts startup — and **this same
service provides the TTS for critical engine alerts (BUG-44)**. A missing microphone must never
silence the alarms. Degraded-but-running is the correct posture; the backoff makes it cheap.

**Device auto-detection already existed** (`detect_microphone()`, line 57) and its generic fallback
parses any card from `arecord -l`, so **an ordinary USB mic will be picked up** — it does not need
to be the Anker S330. Operator is fitting a USB mic to the lab Pi, after which voice becomes
desk-testable like everything else.

**Version-control gap closed:** `voice-watchdog.sh` was Pi-only, outside the canonical tree. It is
now mirrored at `deployment/v0.9.9.4/opt/d3kos/scripts/voice-watchdog.sh` (verified in sync).

#### Original proposed fix (superseded by the above)
- Exponential backoff on respawn (1 s → 2 s → 5 s → 30 s cap) with a consecutive-failure counter.
- Capture `arecord` stderr; log the real reason **once**, not per attempt.
- Probe for a capture device at startup; if none, log once and enter a **degraded/idle** state
  instead of looping — do not pretend to listen.
- Stop hardcoding the device; select it from `arecord -l` and fail loudly if absent.
- Watchdog: treat "no capture hardware" as a distinct state, not a restart trigger.

⚠ **Unrelated to BUG-23b.** Transcription still cannot work regardless — there is no local STT
engine installed at all.

**BUG-23b — MOVE COMPLETED S117 2026-08-02 (operator decision).** It is an **absence, not a
defect**: recording works, nothing converts speech to text. → `V09995_DISCUSSION_PLAN.md` **§13
(D13) Phase 3**, where Faster-Whisper is already planned.

⚠ **Correction to the earlier note here:** it claimed BUG-23b "was moved to the v0.9.9.5 backlog in
S114." **That move was declared but never actually executed** — no reference to BUG-23b existed
anywhere in `V09995_DISCUSSION_PLAN.md`, and the checklist row still read as open. The *capability*
(Faster-Whisper) was in the plan, but framed as VHF-radio transcription only, so nobody connected it
to Boat Log voice notes. S117 added the cross-reference to D13 Phase 3 naming Boat Log as the second
consumer. **No duplicate backlog item was created.**

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

**Status:** `[x]` **FIXED S136 2026-08-28 — Option A implemented. `boatlog_capture.py` server-side service; `d3kos-boatlog-capture.service` enabled on lab Pi. `app.py` GET `/api/boatlog/entries` read-only. `boat-log.html` fetches+merges server entries on load. boatlog-engine.js <script> removed; file kept RETIRED. T4 PASS: engine row written without page open. T8 PASS: journald within 7s.**

**The logic works.** Verified S116 with LAB-SIM: with the Boat Log page open, injecting RPM 0 →
2200 wrote an `event:"start"` engine entry to `localStorage('d3kos-boatlog-entries')` exactly as
designed. So candidates 1 (blocked by BUG-14 / no RPM), 3 (threshold logic) and 4 (write path) are
all **disproved** — it captures correctly when it is running.

**The real root cause is architectural.** `boatlog-engine.js` is loaded by **`boat-log.html` ONLY**
— zero references in `index.html` (verified S116, and asserted by a regression test). It is a
client-side script, so engine auto-capture only runs **while the Boat Log page is open in a
browser**. At the helm the dashboard is on screen, so engine start/stop is never observed and
nothing is ever recorded. That is why H-04 failed on-boat after 30+ minutes of running.

**Fix options (needs an operator decision — this is a design change, not a patch):**
- **(a) Quick:** also load `boatlog-engine.js` from `index.html`. ⚠ `localStorage` is shared per
  origin, so with both pages open two instances would double-record. Needs a single-instance guard.
- **(b) Correct:** move engine capture to a **server-side service** that subscribes to Signal K and
  writes to the Boat Log independently of any browser. Engine logging should not depend on which
  page happens to be displayed. This is the option that actually matches the feature's intent.

**Recommendation: (b).** Also note `boatlog-engine.js` subscribes to `propulsion.port.temperature`
but **not** `propulsion.port.coolantTemperature` — the same alias gap fixed in the dashboard under
BUG-47. Worth correcting in the same change.
**Logged:** 2026-07-21 S104
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

**Status:** `[x]` **CLOSED NOT A BUG — S107 verified LIVE on the boat.** `:3001/status` → `{"gemini_key":true,"model":"gemini-2.5-flash-lite","online":true}`; real query `POST /ask` returned `{"response":"...","tokens":290}`. Internet egress hypothesis disproven — egress and AI both work. PART 17 was ahead of this file; closing to match. (Was: `[~]` DIAGNOSED 2026-07-23 — likely not a d3kOS bug, pending on-boat confirmation. Was: `[ ]` OPEN logged S104 2026-07-21.)
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

**Status:** `[~]` **FIXED IN LAB PI — BOAT STATE UNKNOWN.** Lab Pi tree byte-identical to canonical (S131, 216 files, 0 drift); fix confirmed present in lab. Boat Pi: S107 confirmed `AI_BRIDGE` 0 occurrences — fix NOT on boat. **Verify on next trip:** `grep -c 'AI_BRIDGE' /opt/d3kos/services/dashboard/static/js/anchor-watch.html` → must be ≥5. (Was: `[x]` FIXED + DEPLOYED TO PI S105 2026-07-23 — premature; "TO PI" meant the lab Pi only; boat state was never confirmed.) ROOT CAUSE was: anchor endpoints live on ai-bridge (`:3002`, verified: `/anchor/set`=405 POST-only, `/anchor/state`=200); dashboard (`:3000`) serves none (all 404). `anchor-watch.html` fetches bare `/anchor/*` → `:3000` → 404 → Set Anchor never arms (K-02). Fix = point the 5 anchor fetches at `AI_BRIDGE` (`:3002`), matching the file's existing SSE call. Atomic spec: `atomic-specs/BUG-26.md`. Diagnosis: `runbooks/GROUP-A-services.md`. (Was: `[ ]` OPEN logged S104 2026-07-21)
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

**Status:** `[~]` **DEPLOYED TO LAB PI ONLY — BOAT STATE UNKNOWN.** Lab Pi tree byte-identical to canonical (S131); CSS change confirmed present. Boat Pi: S107 confirmed `.sb-vessel` still 18px — fix NOT on boat. **Verify on next trip:** `grep 'sb-vessel' /opt/d3kos/services/dashboard/static/css/d3kos.css` → must show 28px. (Was: `[x]` COMPLETE — premature; operator confirmation was on lab Pi screen, not the boat.)
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

### ⚠ Critical note — CORRECTED S118 2026-08-03 (the original was true when written, and is now false)

**Superseded text (S107 2026-07-27):** *"Re-copying the latest version to the boat will NOT fix the
engine gauges, depth gauge, BUG-16 or BUG-24 — those defects (BUG-29, BUG-30) exist in the latest
source too."*

That was accurate on 2026-07-27. **BUG-29 and BUG-30 were both fixed later the same day** in
S108-cont, so three of the four items it names no longer hold. Current position:

| Item named in the old note | Status now | Will a boat deploy fix it? |
|---|---|---|
| Engine gauges (**BUG-29**) | `[~]` FIXED lab S108-cont, §25.8 ACCEPT 13/13 | **YES** — the fix is in the canonical tree |
| Depth gauge (**BUG-30**) | `[~]` FIXED lab S108-cont, §25.8 ACCEPT 16/16 | **PARTLY** — code ships, but the primary fix is **configuration**: a keel offset must be set on the Garmin on the boat. Deploy alone is not sufficient. |
| **BUG-16** (gauge tap dialog) | `[x]` CLOSED S116 — resolved by BUG-34/36 | **YES** |
| **BUG-24** (Boat Log engine auto-capture) | `[~]` still unfixed — architectural | **NO** — `boatlog-engine.js` loads on `boat-log.html` only; needs a server-side service, which is an undecided design item |

**The one claim that survives:** a boat deploy does not fix everything, and **BUG-24 specifically will
still reproduce.** Depth also needs the on-boat Garmin keel-offset step.

⚠ Lesson recorded: this note sat wrong for seven sessions and would have set false expectations for
the next boat trip. **A "critical note" that names other bugs by number goes stale the moment those
bugs move.** Prefer pointers to the bug's own status line over restating it.

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

**Status:** `[–]` **REMOVED S118 2026-08-03 — operator decision, not being pursued.**
Was: an unidentified N2K device at src 64 broadcasting frozen engine data and a false 0% fuel level
on a confirmed-full tank. Later identified as the **Pangoo** unit (PGN 126996, S112). Closed without
remediation. ⚠ If the false 0% fuel reading resurfaces during boat testing, raise a **NEW** bug
rather than reopening this one.
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

**Status:** `[~]` FIXED (lab) — on-boat validation required (RTL-SDR dongle absent on lab Pi; confirmed topology correct from SK logs) | **Fixed:** 2026-07-29 S110 | **Severity:** HIGH — safety (no AIS targets)
**Replaces the BUG-19 root-cause candidates**

### Fix Applied (S110 — 2026-07-29)

Root cause confirmed: SK's `TcpProvider` is CLIENT-ONLY — no server/listen mode exists regardless of config (`"server": true`, removing `host` both confirmed ineffective). Correct topology requires `rtl_ais` as TCP server.

**Fix:**
- `rtl-ais.service`: `-h 127.0.0.1 -P 10110` → `-T -P 10108` (`-T` = rtl_ais TCP server mode, listens on 10108; `-h` ignored)
- `settings.json` ais provider: `host: "127.0.0.1"`, `port: 10108` (number), `enabled: true` — SK connects to rtl_ais's listener
- Boot order: `rtl-ais.service` has `After=signalk.service`; SK starts first and retries connection until rtl_ais is up

**Lab verification:** SK logs show `TcpProvider:connect ECONNREFUSED 127.0.0.1:10108` (correct — connecting to 10108 not 10110; rtl_ais absent because no dongle on lab Pi). UUID stable at `af7d4be0`.

**On-boat validation required:** rtl_ais must start successfully (dongle present), SK must connect to 127.0.0.1:10108, AIVDM sentences must arrive, `vessels.*` API must return AIS targets.

**Files changed:** `etc/systemd/system/rtl-ais.service`, `home/d3kos/.signalk/settings.json`. Commits: `13716ac` (initial fix), `89e8ea0` (topology correction).
**Atomic spec:** `deployment/docs/atomic-specs/BUG-32.md` (Note: spec was written before -T flag was discovered; deployed fix differs from spec — spec updated to reflect actual fix).

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

**Status:** `[~]` CONFIG FIXED on lab Pi — on-boat validation required — S110 2026-07-29 | **Severity:** HIGH — safety
**Atomic spec:** `deployment/docs/atomic-specs/BUG-33.md` (retroactive — §25 workflow was not followed; documented as UAC in S110 metrics)
**Refines BUG-21 (not "never built" — a config defect confirmed in S110)**

### S110 Fix Summary (2026-07-29)
Config changed directly on Pi (file contains real credentials — NEVER pull into canonical tree):
`/home/d3kos/.signalk/plugin-config-data/signalk-forward-watch.json`
- `detection_interval`: 300 → **10** (10-second detection cycle; appropriate for collision avoidance)
- `audio_alarm`: false → **true** (enables `paplay`/`aplay` beep on detection)

Applied via Python `json.load` / `json.dump` to preserve all other fields. SK restarted; config confirmed on disk. ONNX model present (`forward-watch.onnx` 12 MB). GPU warning on startup is expected (Pi has no discrete GPU; CPU inference runs). `environment.forwardWatch` absent from SK data store in lab — expected: RTSP camera at `10.42.0.100` is on boat-subnet only; detection loop exits early via `if (!framePath) return` when RTSP grab fails.

**Security constraint:** `camera_pass: d3kos2026` is in the config — never commit this file to the canonical tree or any repo.

**On-boat validation required:**
- Detections published to `environment.forwardWatch.detections` when camera reachable
- `notifications.forwardWatch.*` published when GPS position + distance fields available
- Audio alarm fires via `paplay`/`aplay`

### Evidence (original)
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
- [x] Set `audio_alarm: true` — done S110 (config on Pi); audio path verify requires on-boat test
- [x] Reduce `detection_interval` — done S110; set to 10 s (confirmed reasonable for collision avoidance; CPU impact: ONNX CPU inference is ~50-150 ms/frame on Pi 4, 10 s cycle is safe)
- [ ] Confirm detections are published to `notifications.*` — **pending on-boat validation** (camera unreachable in lab; detection loop exits early at `if (!framePath) return` without RTSP)
- [x] Re-verify BUG-21 — resolved by this fix (see BUG-21 S110 resolution note)
- [ ] **Security:** `camera_pass` in plaintext — deferred; move to secret store or environment variable

---

## BUG-34 — Gauge Tap Dialog: Hardcoded Alarm String and Generic Thresholds Not Sourced From Boat Documentation

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S110 2026-07-29** — logged S107 2026-07-27 | §25.8 ACCEPT 9/9 | **NOT on the boat Pi** | **Severity:** MEDIUM-HIGH (E2 violation + safety gap)
**Refines BUG-16 — these are code defects independent of the BUG-29 path mismatch**

### S110 Fix Summary (2026-07-29)
- `instruments.js`: `THR.oil.crit` 20→4 (MerCruiser 454 idle minimum ≥4 psi per S106 manual); `THR.bat_hi` added `{adv:14.8, alrt:15.2, crit:15.6}` for overcharge; `window._d3kEngData.depth_m` added and written in `_renderDepth`.
- `overlays.js`: `showCrit()` ticker de-fabricated (no longer hardcodes "8 PSI"); `openDiag()` URL `'http://localhost:8097/...'` → `'http://' + window.location.hostname + ':8097/...'`; fallback THR updated to include bat_hi/oil.crit:4/depth/fuel; battery card checks overcharge via `_stateAbove(eng.bat_v, thr.bat_hi)` with guard; Fuel + Depth cards added to `_diagBuildCards`.
- Atomic spec: `deployment/docs/atomic-specs/BUG-34.md`. Tests: `tests/bug34-diag-panel.test.cjs` (9/9 pass). Commit: `b6870d9`.
- Verified post-deploy: all 5 changes confirmed present in served files on lab Pi.

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

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont** — logged S108 2026-07-27 | ACCEPT 13/13 | **NOT on the boat Pi** — served `instruments.js` verified `_d3kEngData` ×6 post-deploy | **§25.8 RE-VERIFIED S133 2026-08-24** — stale test expectation corrected (BUG-34 added `depth_m`, test never updated); all assertions now pass; `_lastSogKts` ×3 confirmed, `fuel_pct=v` (fraction) confirmed, `window.SK_HANDLERS` seam confirmed | **Severity:** HIGH (feature loss, shipped by a "fix")
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

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont** — logged S108 2026-07-27 | ACCEPT 15/15 | **NOT on the boat Pi** — health-checked: diagTitle/diagGrid/diagAiTxt present in the rendered page | **§25.8 RE-VERIFIED S133 2026-08-24** — 3 IDs confirmed on correct elements, classes intact, `#diagGrid` empty, `#diagAiTxt` neutral placeholder, fabricated numbers absent, 3 buttons unchanged | **Severity:** MEDIUM-HIGH
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

**Status:** `[~]` **DEPLOYED TO LAB PI 2026-07-27 S108-cont — unit installed DISABLED, master GUARDED** | ACCEPT 23/23 | **NOT on the boat Pi** — Phase B (clone-procedure wiring) NOT started | **§25.8 RE-VERIFIED S133 2026-08-24** — 16/16 pytest pass; `license.json` confirmed read-only (no write path anywhere in script); `device-token.json` backed up before write, written via python3 only; no `.signalk`, no `tune2fs`/`fatlabel`/`mlabel`; sentinel line 16 (first) / line 168 (last); `bash -n` clean; `chmod +x` set | **Severity:** HIGH (blocks the boat clone)
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

**Status:** `[x]` FIXED + DEPLOYED to lab Pi — 2026-07-29 S110 | **Severity:** LOW-MEDIUM (identity/config integrity)
**Found while resolving Q39.3 for BUG-39. It removes the SK UUID from BUG-39's scope.**

### Fix Applied (S110 — 2026-07-29)

Diagnostic confirmed: SK UUID is **runtime-random** — changed from `e1592142` to `2569c03f` after restart (confirmed live on lab Pi). SK v2.23 ignores `vessel.uuid` in `settings.json`; it expects vessel identity in `defaults.json` (which was absent).

**Fix:** Created `~/.signalk/defaults.json`:
```json
{"vessels": {"self": {"uuid": "urn:mrn:signalk:uuid:af7d4be0-fb1d-4164-976d-de373c1c0331", "name": "d3kOS Vessel"}}}
```
UUID `af7d4be0` taken from `settings.json` vessel block (the configured intent). Verified stable across two restarts on lab Pi. Commit `13716ac`.

**Boat Pi note:** boat Pi may have a different `settings.json` vessel.uuid — verify during next on-boat session before deploying `defaults.json` there.

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

---

## BUG-41 — `/settings` Returns HTTP 500: `tier_num` and `device_token` Never Passed to Template

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S110 2026-07-29** — logged S108-cont 2026-07-27 | §25.8 ACCEPT | **NOT on the boat Pi** | **Severity:** MEDIUM (blocks Settings page entirely; crash on load)
**Another casualty of the lineage split — same root cause as BUG-36/BUG-37**

### Evidence
`settings.html` (d3kOS-lineage) uses `{% if tier_num >= 1 and device_token %}` (line 509) and `{{ device_token }}` (line 521). The deployed `app.py` (d3kOS-lineage) passed only five variables: `avnav_port`, `gemini_port`, `signalk_port`, `vessel_name`, `home_port`. Both `tier_num` and `device_token` were absent → Jinja2 raised `UndefinedError: 'tier_num' is undefined` on every GET `/settings` → HTTP 500. Pre-existing since 2026-04-13 (settings.html mtime). The S108-cont deploy left both files byte-identical — it did not cause this bug.

### S110 Fix Summary (2026-07-29)
- `app.py` `settings()`: added two try/except blocks before `render_template`. Pattern copied verbatim from `config_tier()` (line 613) and `api_recovery_key()` (line 364) in the same file.
- `tier_num`: reads `license.json` → `lic.get('tier', 'T0')` → `int(str(t).replace('T',''))`. Default on exception: `0`.
- `device_token`: reads `device-token.json` → `.get('device_token', '')`. Default on exception: `''`.
- No other variables added or removed. `settings.html` untouched.

---

## BUG-42 — Oil Pressure Alert Cannot Be Dismissed After Engine Shutdown

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S113 2026-07-31** — §25.8 Tier 1 PASS | **Reported:** On-boat, during docked testing | **NOT on the boat Pi**
**Severity:** MEDIUM (alert fires correctly but blocks UI; operator cannot continue using dashboard)

### Symptom
1. Engine running — no alert
2. Operator shuts off engine
3. Oil pressure drops → dashboard alert triggers ✅ **This is correct behavior**
4. Alert displays on screen **BUT operator cannot dismiss it**
5. Alert persists — operator unable to interact with dashboard

### When It Happens
- Occurs during normal operation when engine shuts down
- Alarm notification appears (visual/audio or both)
- Operator seeks to acknowledge/dismiss the alert but no UI control exists or is non-functional

### Root Cause Candidates (to investigate)
1. **Notification handler without dismiss logic** — `overlays.js` or `instruments.js` triggers alarm but does not wire up an acknowledge/dismiss button
2. **UI control missing** — Alert displays but no "OK", "Dismiss", or "Acknowledge" button on the UI
3. **Button exists but not wired** — HTML button present but not connected to a handler that clears the alarm state
4. **Alarm state persists in memory** — Even if operator taps the control, the in-memory `_d3kEngData.oil_crit` or notification state does not get reset

### Files to Investigate
- `instruments.js` — oil pressure handler and alarm state management
- `overlays.js` — alert rendering and dismissal
- `dashboard.html` or `index.html` — UI structure for alarm display
- Notification state in `app.py` or Flask backend (if persisted server-side)

### Reproduction Steps (verify next time on boat)
1. Start engine (oil pressure should show nominal: 30-50 PSI or similar)
2. Shut off engine
3. Wait for oil pressure alert to appear
4. Attempt to dismiss: look for button/tap/gesture to clear
5. Note whether alert can be dismissed
6. If not, check browser console for JS errors (`F12` → Console tab)

### Expected Behavior
- Alert triggers when oil pressure drops below threshold ✅ (working)
- Alert displays prominently (visual + optional audio) ✅ (working)
- Operator can dismiss/acknowledge alert with single tap or gesture ❌ (broken)
- Alert clears from screen after dismiss ❌ (broken)
- Dashboard returns to normal interactive state ❌ (blocked by stuck alert)

### Impact on Validation
- This bug was discovered **during on-boat validation of BUG-29/30/32**
- Does not block those validations but indicates incomplete alert handling system
- Related to M14 gauge tap functionality (see BUG-34 diagnostic panel)
- May affect other critical alerts (temperature, fuel, battery) when those sources become available

### Root Cause (S112 2026-07-31 — Diagnosed via Signal K API + code inspection)

**Signal K Layer:** ✅ WORKING CORRECTLY
- Oil pressure notification exists: `notifications.propulsion.port.lowOilPressure`
- Status: `canAcknowledge: true`, `canClear: false` (correct for engine alarms)
- Notification system properly configured to accept acknowledgment

**Dashboard Layer:** ❌ BROKEN — No Dismissal Mechanism

```
showCrit() [overlays.js:128]
├─ document.getElementById('critSc').classList.add('show')
├─ ticker.textContent = '⛔ CRITICAL ENGINE ALARM — SHUT DOWN ENGINE IMMEDIATELY'
├─ ticker.classList.add('hot')
└─ ❌ NO CODE TO HIDE IT — alert is STUCK

closeCrit() [overlays.js:137]
├─ document.getElementById('critSc').classList.remove('show')  ✅ Would fix it
├─ ticker.classList.remove('hot')
└─ BUT closeCrit() ONLY CALLED FROM:
   ├─ nav.js:165 → closeMenu() chain (not from alert dismiss)
   ├─ nav.js:158 → if (e.key === 'c') (user presses 'c' key)
   └─ ❌ NO UI BUTTON WIRED TO closeCrit()
   └─ ❌ NO AUTO-DISMISS WHEN OIL PRESSURE RECOVERS
```

### Call Chain Analysis

**When alert fires:**
1. Engine shuts off → oil pressure drops to 0 Pa
2. `instruments.js:210` detects critical condition
3. Calls: `if (typeof showCrit === 'function') showCrit();`
4. `showCrit()` adds 'show' class to `#critSc` overlay
5. Overlay appears on screen with "⛔ CRITICAL ENGINE ALARM"

**When alert should dismiss:**
- ❌ NOT when user taps screen (no button)
- ❌ NOT when oil pressure recovers (no listener)
- ✅ ONLY if user presses Escape key or closes a menu
- User is **stuck** until accidental menu close

### Files Involved

| File | Function | Line | Issue |
|------|----------|------|-------|
| `overlays.js` | `showCrit()` | 128-135 | Shows alert, never dismisses |
| `overlays.js` | `closeCrit()` | 137-145 | Exists but unreachable from UI |
| `instruments.js` | Oil pressure handler | 210 | Calls `showCrit()` correctly |
| `nav.js` | Menu close chain | 165 | Only place `closeCrit()` is called |
| `index.html` | Critical screen overlay | ? | `<div id="critSc">` — no dismiss button |

### Evidence (S112 Signal K Query)

```json
{
  "propulsion": {
    "port": {
      "lowOilPressure": {
        "state": "normal",
        "status": {
          "canAcknowledge": true,
          "canClear": false,
          "acknowledged": false
        }
      }
    }
  }
}
```

**What this means:** 
- Signal K is set up correctly to receive acknowledgments
- Dashboard is not sending acknowledgments
- Dashboard is not even providing a UI to do so

### Fix Options

**Option A (Recommended):** Add dismiss button
1. Add dismiss/acknowledge button to `#critSc` overlay in `index.html`
2. Wire it to call `closeCrit()` on click
3. Also call `closeCrit()` when oil pressure recovers (add listener to instruments.js:210)

**Option B:** Auto-dismiss on recovery
1. After calling `showCrit()`, add a listener for oil pressure to recover
2. When oil pressure > threshold, call `closeCrit()` automatically
3. Avoids need for manual button

**Option C:** Both
1. Add manual dismiss button (Option A)
2. Add auto-dismiss on recovery (Option B)
3. Gives operator both choices

### Severity Assessment
- **User Impact:** HIGH — alert blocks dashboard use until operator accidentally dismisses it
- **Safety Impact:** MEDIUM — operator may shut down engine correctly, but alert prevents further navigation
- **Frequency:** Always occurs when engine shuts down (oil pressure will drop)
- **Workaround:** Press Escape key or close a menu to dismiss

### Next Steps
1. Implement one of the fix options above (recommend Option C)
2. Add TDD test: engine shutdown → alert shows → dismiss button works → alert hides
3. Test on boat with engine running → shut down → verify single-tap dismissal
4. Confirm auto-dismiss works when operator restarts engine (oil pressure recovers)
5. Verify other critical alerts (temperature, fuel) don't have same issue
- Atomic spec: `deployment/docs/atomic-specs/BUG-41.md`. Tests: `tests/test_bug41_settings_route.py` (3 tests; test 3 static check passes; tests 1–2 need Flask on Pi). Commit: `b6870d9`.
- Verified post-deploy: `curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/settings` → **200**.

---

## BUG-45 — False Critical Engine Alerts on Pi Boot When Engine Is Off

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S113 2026-07-31** — §25.8 Tier 1 PASS | **Reported:** On-boat — oil pressure, coolant, and fuel firing CRITICAL alerts immediately after Pi reboot with engine off | **NOT on the boat Pi**
**Severity:** HIGH (creates alert fatigue — operator learns to ignore alarms, defeating the safety purpose)

### Symptom
1. Engine is OFF
2. Operator reboots Pi
3. Pi boots, dashboard loads, Signal K connects to N2K bus
4. **Within seconds: oil pressure CRITICAL, coolant CRITICAL, fuel ADVISORY/CRITICAL alerts fire**
5. All alerts are false — engine is not running

### Root Cause — Two Compounding Problems

**Problem 1 — No "engine running" gate**
The dashboard has no check for whether the engine is actually running before evaluating oil pressure and coolant temperature alarms. These two readings are only meaningful when `RPM > 0`. When engine is off:
- Oil pressure = 0 PSI → threshold ≤4 PSI crit → `showCrit()` fires immediately ← correct physically, wrong operationally
- Coolant temp = whatever Pangoo reports → may exceed 105°C crit threshold ← sensor data unreliable at startup

**Problem 2 — Pangoo startup values are unreliable**
From live raw CAN capture (S112), PGN 127489 from Pangoo (src 64) reports **temperature = 393K (120°C)** immediately at boot, even with engine off. The MerCruiser 454 critical threshold is 105°C. This fires the coolant critical alert falsely. The value stabilises to ~37°C (ambient) after ~25 seconds, but the dashboard has already triggered.

**Root cause chain:**
```
Pi boots → SK gets N2K data → Pangoo sends: oil=0Pa, temp=393K, fuel=0%
→ Dashboard WS receives all three → no engine-running gate → all three evaluate as CRITICAL
→ showCrit() + alertTicker fire → user sees 3 false alarms
```

### Files to Fix
- `instruments.js` — add engine-running gate: oil and coolant critical alerts must check `window._d3kEngData.rpm > 0` before firing `showCrit()` or `_setAlertTicker` at CRIT level
- `instruments.js` — add startup debounce: suppress all engine critical alerts for first 30 seconds of WebSocket connection (gives Pangoo time to settle)
- Consider: fuel alert is valid regardless of RPM but may need hysteresis (require 3 consecutive readings below threshold before firing)

### Expected Behaviour
- Pi boots → engine OFF → no critical alerts fire (oil=0 and temp are expected for a cold engine at rest)
- Engine starts → RPM > 0 → oil pressure monitoring activates
- Oil pressure drops below threshold while RPM > 0 → CRITICAL fires → correct

### Related Bugs
- **BUG-42** — alert cannot be dismissed (already broken; this bug makes it worse — false alerts stack)
- **BUG-44** — no voice on critical alert (voice would also fire falsely on boot)
- **BUG-31** — Pangoo src 64 frozen/unreliable values — root hardware issue

---

## BUG-44 — Critical Engine Alert Fires No Voice Warning (TTS Not Called from showCrit)

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S113 2026-07-31** — §25.8 Tier 1 PASS | **Reported:** On-boat — oil pressure critical alert appeared on screen with no voice announcement | **NOT on the boat Pi**
**Severity:** HIGH (operator may not see the visual alert in time; voice is the backup safety channel)

### Symptom
1. Engine shuts off — oil pressure drops to 0 PSI
2. Critical alert screen (`#critSc`) appears on dashboard ✅
3. Ticker updates to "⛔ CRITICAL ENGINE ALARM — SHUT DOWN ENGINE IMMEDIATELY" ✅
4. **No voice warning is spoken** ❌
5. If operator is not looking at the screen, the alert is missed entirely

### Root Cause
`showCrit()` in `overlays.js` (line 128) updates the DOM and ticker but **never calls the TTS system**:

```js
function showCrit() {
  document.getElementById('critSc').classList.add('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.textContent = '⛔ CRITICAL ENGINE ALARM — SHUT DOWN ENGINE IMMEDIATELY';
    ticker.classList.add('hot');
  }
  // ← NO TTS CALL HERE
}
```

The TTS infrastructure fully exists and is designed for this use case. `ai_bridge.py` (port 3002) has:
- `tts.speak_urgent(message, repeat=2)` for critical severity
- `POST /webhook/alert` endpoint — accepts `{"message": str, "severity": "info|warning|critical"}`
- `espeak-ng` as the TTS engine, already confirmed working on Pi

The connection is simply never made. `showCrit()` does not POST to `/webhook/alert`.

### Files to Fix
- `overlays.js` — `showCrit()` must POST to `http://localhost:3002/webhook/alert` with `severity: 'critical'`
- The fetch should be fire-and-forget (no `await`) so it does not block the DOM update
- Must respect the mute state — check `tts-mute.json` or use the mute flag before speaking

### Expected Behavior
- Engine critical alert fires → voice speaks: *"Critical engine alert. Oil pressure critical. Shut down engine immediately."* (spoken twice per `repeat=2` for critical severity)
- Alert repeats if pressure remains critical on next SK update AND the acknowledgement latch (BUG-42 fix) has not yet been set
- Muted state (helm mute button) must suppress voice — not bypass it

### Affected Alerts (same pattern likely)
`showCrit()` is only called for oil pressure (from `instruments.js:210`). However the same pattern — no TTS — likely applies to the advisory ticker (`_setAlertTicker`) for coolant and other non-critical states. Those should use `severity: 'warning'` (spoken once).

### Related Bugs
- **BUG-42** — critical screen cannot be dismissed (acknowledgement latch missing) — fix BUG-42 first; BUG-44 voice should fire once then be gated by the same latch
- **BUG-23** — voice note STT failing (separate voice pipeline — does not affect TTS output direction)

### Impact
- Discovered during on-boat S112 validation 2026-07-31
- Safety-relevant: operator may miss critical engine condition if screen not visible

---

## BUG-43 — Settings Unit Selection (Imperial/Metric) Has No Effect on Dashboard Gauges

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S114 2026-07-31** — TDD-verified with Playwright (8/8 pass post-fix, 7/8 fail pre-fix against the same test file) | **Reported:** On-boat, operator set imperial, gauges showed metric | **NOT on the boat Pi**
**Test:** `tests/bug43-unit-persistence.spec.ts` — asserts rendered DOM, incl. that depth/coolant thresholds still evaluate raw SI while displaying imperial
**Severity:** MEDIUM (operator expectation violated — settings page implies unit control that does not exist)

### Symptom
1. Operator opens d3kOS Settings → Units & Display section
2. Operator selects Imperial (°F, PSI, gal, ft) via the Measurement System toggle or individual unit dropdowns
3. Operator taps "Save Display Settings"
4. Toast appears: "✓ Display settings saved"
5. Dashboard engine gauges continue to display metric values — no change

### Root Cause
The "Save Display Settings" button in `settings.html` fires **only a toast notification** — no backend save, no localStorage write, no unit preference applied anywhere:

```html
<button class="btn btn-primary" onclick="showToast('&#10003; Display settings saved')">
  &#128190; Save Display Settings
</button>
```

The `instruments.js` file has **hardcoded unit conversions** with no unit-preference check:
- Oil pressure: always Pa → PSI (`v * 0.000145038`) — coincidentally imperial
- Coolant temperature: always K → °C (`temp_k - 273.15`) — metric
- Speed: always m/s → knots (via SK native) — nautical
- Depth: always metres — metric

There is no `app.py` POST endpoint for unit settings. There is no localStorage read in `instruments.js` at startup. The dropdowns and toggle in `settings.html` are purely cosmetic — they retain no state and apply nothing.

### Files to Fix
- `templates/settings.html` — save button needs real save logic (POST to Flask or localStorage)
- `app.py` — needs POST `/api/settings/units` endpoint OR frontend-only localStorage approach
- `instruments.js` — all unit conversion functions need to check saved preference at render time
- `vessel.env` — candidate location to persist unit preference server-side

### Expected Behavior
- User selects Imperial → temperature shows °F, pressure shows PSI, depth shows feet
- User selects Metric → temperature shows °C, pressure shows kPa, depth shows metres
- Setting persists across page refresh and Pi restart
- Gauge thresholds adjust to selected unit (e.g. oil pressure advisory shown in PSI not Pa)

### Scope of Change
All six gauge cells are affected: cellCoolant (°C vs °F), cellOil (PSI vs kPa), cellDepth (m vs ft), cellFuel (L vs gal), cellBat (V — unit-agnostic), cellSpeed (kts vs mph). Alert ticker messages also need unit-aware formatting.

### Impact
- Non-blocking for navigation but creates operator confusion
- Discovered during on-boat S112 validation session 2026-07-31

---

## BUG-46 — Dashboard Signal K WebSocket Hardcoded to `localhost`; No Live Data on Any Remote Browser

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S114 2026-07-31** — TDD-verified (3/3 fail pre-fix, 3/3 pass post-fix, same test file, no tunnel) | **NOT on the boat Pi**
**Test:** `tests/bug46-remote-host-signalk.spec.ts` — refuses to run against localhost, because a tunnel hides the defect
**Fixed in:** `instruments.js:9`, `boatlog-engine.js:15`, `helm-assistant.html:299` — all three now use `'ws://' + window.location.hostname + ':8099/...'`
**Side effect:** the BUG-43 suite now passes 8/8 against the Pi's real IP with no SSH tunnel.
**Logged:** 2026-07-31 S114 (found while building the BUG-43 Playwright test)
**Platform:** Pi (d3kOS dashboard — all gauges)
**Severity:** HIGH — every gauge is dead on any device except the Pi's own screen

### Symptom
Opening the d3kOS dashboard from a phone, tablet, or laptop shows every instrument
cell stuck at `---` forever. No engine data, no depth, no speed, no position.
The page loads and renders; only live data is missing. On the Pi's own touchscreen
everything works, which is why this was never noticed.

### Root Cause
```
deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js:9
const SK_WS_URL = 'ws://localhost:8099/signalk/v1/stream';
```
`localhost` is resolved by the **browser**, not the server. On a remote device it
points at that device's own loopback, where no Signal K server exists. The socket
never opens, `_markAllDash()` leaves every cell dashed, and nothing recovers.

Same defect in a second file:
```
static/js/boatlog-engine.js:15
var SK_URL = 'ws://localhost:8099/signalk/v1/stream';
```

### Evidence (S114)
Playwright loaded `http://192.168.1.237:3000` from the workstation. Deltas were
injected into the Pi's Signal K and confirmed present via the REST API, but every
dashboard cell stayed `---`. Injection was proven working; the dashboard simply
was not connected to Signal K.

### Fix (proposed — NOT yet applied)
Derive the host from the page, as was already done for the Gemini URL in BUG-34:
```js
const SK_WS_URL = 'ws://' + window.location.hostname + ':8099/signalk/v1/stream';
```
Apply the same change to `boatlog-engine.js`.

### Impact on other work
- This is almost certainly a blocker for the v0.9.4 PWA — the phone app cannot
  show live instruments while this exists.
- Any test harness driving the dashboard from another machine needs an SSH tunnel
  for port 8099 until this is fixed.

### Relation to BUG-34
Same class of defect. BUG-34 fixed a hardcoded Gemini URL by making it portable.
The Signal K socket was missed.

---

## BUG-47 — No Handler for `propulsion.port.coolantTemperature`; Coolant Gauge May Never Populate

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S114 2026-07-31** — TDD-verified (3/3 fail pre-fix, 3/3 pass post-fix) | **NOT on the boat Pi**
**Test:** `tests/bug47-propulsion-alias-gap.spec.ts` — computes the required aliases from the live
page, so a NEW propulsion.0.* handler added without its port alias also fails.
**Audit found TWO gaps, not one:** `propulsion.port.coolantTemperature` AND
`propulsion.port.trimTabPosition`. Both aliased.
**Logged:** 2026-07-31 S114 (found while building the BUG-43 Playwright test)
**Platform:** Pi (d3kOS dashboard — coolant gauge)
**Severity:** MEDIUM-HIGH — silent gauge failure, same class as BUG-29

### Symptom
The coolant temperature gauge may never display a value even when Signal K is
publishing coolant data, because the dashboard does not subscribe to the path
Signal K actually produces.

### Root Cause
`instruments.js` defines a handler for `propulsion.0.coolantTemperature` and the
BUG-29 alias block adds:
```
propulsion.port.revolutions      -> propulsion.0.revolutions
propulsion.port.oilPressure      -> propulsion.0.oilPressure
propulsion.port.temperature      -> propulsion.0.coolantTemperature
propulsion.port.drive.trimState  -> propulsion.0.trimTabPosition
```
**`propulsion.port.coolantTemperature` is absent from that list.** Signal K maps
NMEA 2000 PGN 127489 (Engine Parameters, Dynamic) to
`propulsion.<instance>.coolantTemperature` — so with a `port` instance the
published path has no handler and the delta is silently discarded.

### Evidence (S114)
Injecting `propulsion.port.coolantTemperature` produced no DOM change. Injecting
`propulsion.port.temperature` (the alias that exists) worked.

### Why this was not caught on the boat
The CX5106 has been absent from the N2K bus since S112, so no coolant data has
ever reached Signal K on the boat. The gauge appeared dead for a hardware reason,
masking this software defect underneath it. **It will still be dead after the
CX5106 is restored unless this is fixed.**

### Fix (proposed — NOT yet applied)
Add to the alias block in `instruments.js`:
```js
SK_HANDLERS['propulsion.port.coolantTemperature'] = SK_HANDLERS['propulsion.0.coolantTemperature'];
```
Audit the remaining `propulsion.0.*` handlers for the same gap.

### Relation to BUG-29
Identical class — dashboard subscribing to a path Signal K does not publish.
BUG-29's alias fix was incomplete. This is the sixth instance of this defect
class, which is why the contract test in Batch 3 of `V09994_FIX_PLAN.md` matters.

---

## BUG-48 — Every Other Service URL in the Dashboard Is Also Hardcoded to `localhost`

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S114 2026-07-31** — implemented by Tier 3 (Gemini 2.5-flash-lite), verified by Tier 1 §25.8 | **NOT on the boat Pi**
**Test:** `tests/bug48-no-hardcoded-localhost.spec.ts` — 19 tests, guards 9 served JS files
and 10 pages. Fails on ANY hardcoded localhost URL, so this defect class cannot return.
**Final count: 30 call sites across 18 files** (not the 17 first estimated — the initial
audit was truncated by a `head -30` and under-reported. Corrected by a full re-audit.)
**Round 1:** 18 sites. **Round 2:** 10 more. **Round 3:** 2 more found by the guard test —
`settings.html` `avnavUrl` (object property, missed by an `=`-anchored grep) and the
`index.html` AvNav iframe, which was wrongly declared out of scope and IS a real defect;
its `src` is now set from JS since Jinja cannot know the client's hostname.
**Deliberately unchanged:** `app.py` (server-side Python — `localhost` correctly means the
Pi) and operator-facing documentation copy that mentions localhost.
**Regression:** 33/33 across BUG-43 + BUG-46 + BUG-47 + BUG-48.
**Logged:** 2026-07-31 S114 (audit performed while fixing BUG-46)
**Platform:** Pi (d3kOS dashboard — all non-Signal-K services)
**Severity:** HIGH — most of the dashboard is non-functional on any remote device

### Symptom
BUG-46 fixed the Signal K WebSocket, so gauges now work from a phone or laptop.
Everything else on the dashboard still does not: AI navigation, cameras, AvNav,
anchor watch, document upload, manuals, and the weather panel all fail silently
when the dashboard is opened from any device other than the Pi's own screen.

### Root Cause
The same defect as BUG-46, repeated across ~17 more call sites. `localhost` is
resolved by the browser, so on a remote device it points at that device's own
loopback.

| File | Line | Hardcoded URL | Service |
|---|---|---|---|
| `static/js/helm.js` | 15 | `http://localhost:3001/ask` | Gemini |
| `static/js/instruments.js` | 10 | `http://localhost:8080/viewer/avnav_navi.php` | AvNav |
| `static/js/instruments.js` | 11 | `http://localhost:3002` | ai-bridge |
| `static/js/instruments.js` | 513 | `http://localhost/weather.html` | weather |
| `static/js/boatlog-engine.js` | 16 | `http://localhost:8095` | boatlog API |
| `static/js/cameras.js` | 7 | `http://localhost:8084` | cameras |
| `static/js/ai-bridge.js` | 7 | `http://localhost:3002` | ai-bridge |
| `static/js/panel-toggle.js` | 49, 116, 124 | `http://localhost:8080`, `:<port>`, `:8084` | AvNav / cameras |
| `templates/anchor-watch.html` | 203, 399 | `http://localhost:3002` + SSE stream | ai-bridge |
| `templates/ai-navigation.html` | 233 | `http://localhost:3001/ask` | Gemini |
| `templates/upload-documents.html` | 187 | `http://localhost:8081/upload/manual` | upload API |
| `templates/manage-documents.html` | 172, 246 | `http://localhost:8083/manuals/...` | manuals API |
| `templates/helm-assistant.html` | 645 | `http://localhost:3001/ask` | Gemini |
| `templates/marine-vision.html` | 476 | `http://localhost:8084` | cameras |
| `templates/index.html` | 191 | `src="http://localhost:{{ avnav_port }}"` | AvNav iframe |

### Fix (proposed — NOT yet applied)
Apply the established portable pattern used by BUG-34 and BUG-46:
```js
'http://' + window.location.hostname + ':<port>/...'
```
Better: introduce one shared helper (e.g. `d3kUrl(port, path)`) in a single file
and route every call site through it, so this class of defect cannot recur
one-file-at-a-time. That is a larger refactor and should be specced properly.

`templates/index.html:191` is server-rendered Jinja and may be fixable more
cleanly at the template layer — confirm before changing.

### Why this matters beyond the dashboard
This is very likely a blocker for the v0.9.4 PWA. A phone app that can render
gauges but cannot reach cameras, AI navigation, anchor watch or AvNav is not a
usable product.

### Relation to BUG-34 and BUG-46
Third and largest instance of the same class. BUG-34 fixed the Gemini URL in
`overlays.js`; BUG-46 fixed the Signal K socket. Neither swept the codebase,
which is why this kept resurfacing.

---

## BUG-49 — Header Brand Broken: Wordmark Invisible in Day Mode, Logo Broken in Both Modes

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S115 2026-08-01** — TDD-verified 3/3 fail pre-fix, 3/3 pass post-fix | **NOT on the boat Pi**
**Test:** `tests/bug49-header-brand.spec.ts` — asserts the asset returns 200 AND computed contrast ≥4.5:1 in BOTH themes.
**Measured pre-fix:** logo 404; day contrast **1.09:1** (`rgb(28,37,28)` on `rgb(0,50,0)`) — worse than the 1.37:1 hand-calculation, and night failed too, which the hand-calc missed.
**Fix:** restored `static/images/amboat-logo.png` (from `features/boot-splash/theme/`, md5 `92c88112`) and set an explicit `color:#FFFFFF` on `.sb-brand`. `--ink2`/`--ink3` tokens untouched per the S54 rule.
**Sizing — operator decision S115:** the restored logo rendered at 28px, which the operator judged
too small and asked for 4×. 4× is 112px, which is 2.3× the 48px status bar and would have cost
64px of chart height. Options were presented; **operator chose 64px with the bar grown 48→72px**
(2.3× the original, −24px chart height). Verified live: bar 72px, logo 64×64, no overflow.
Only `#sb` consumes `--sb-h`; sub-pages use `#status-bar`, independently hardcoded at 48px and
unaffected.

⚠ **The logo is 512×512 square** — at `height:28px` it renders as a 28×28 icon with NO words. The "wordmark" the operator saw was the broken image's alt text. **If a visible wordmark is wanted, that is a separate design change** (add a text element beside the logo) — NOT done, awaiting operator decision.
**Logged:** 2026-08-01 S115
**Platform:** Pi (d3kOS dashboard — status bar / header brand, top-left)
**Severity:** MEDIUM-HIGH — **AODA contrast violation** (Issue 1) + broken asset (Issue 2)

### Symptom — as reported by the operator

Top-left corner of the dashboard, the AtMyBoat logo and the wordmark "AtMyBoat d3kOS".

**Issue 1 — Wordmark invisible in DAY mode.**
The words are not visible in day mode. They ARE visible in night mode. The day-mode
text appears to be a **blue** colour against the day background; it should be a
contrasting colour (operator suggests white).

**Issue 2 — Logo image broken in BOTH day and night mode.**
The logo itself renders broken (missing/failed asset) regardless of theme.

### Root Cause — INVESTIGATED S115 2026-08-01. **Both issues are ONE defect.**

`templates/index.html:62`
```html
<img class="sb-brand" src="/static/images/amboat-logo.png" alt="AtMyBoat d3kOS" style="height:28px;width:auto;">
```

**The asset does not exist.** `static/images/` is absent from the canonical tree
AND from the lab Pi. Live read: `/static/images/amboat-logo.png` → **HTTP 404**;
`/opt/d3kos/services/dashboard/static/images/` → *No such file or directory*.

**Therefore the "wordmark" the operator sees is not a wordmark at all — it is the
`alt` text of the broken image.** The browser falls back to rendering
`alt="AtMyBoat d3kOS"` in place of the missing logo. That single fact explains
both reported symptoms:

- **Issue 2** (logo broken in both modes) = the 404.
- **Issue 1** (words invisible in day mode only) = the alt text inherits `--ink`,
  which has no contrast against the status-bar background in day mode.

**Measured contrast** — `#sb` background is `--bar`, which is dark green in BOTH
themes (`#003200` day, `#001A00` night). `.sb-brand` sets no `color`, so the alt
text inherits `--ink`:

| Mode | Text `--ink` | Bar `--bar` | Ratio | WCAG AA (4.5:1) |
|---|---|---|---|---|
| **Day** | `#040C04` near-black | `#003200` | **1.37:1** | ❌ **FAIL — effectively invisible** |
| Night | `#D6EDD6` pale | `#001A00` | 14.76:1 | ✅ PASS |

1.37:1 is why it disappears in day mode. The operator read it as "blue"; it is in
fact near-black on dark green.

**Restoring the image fixes both symptoms**, because there would be no alt text to
render. But the contrast defect must ALSO be fixed — alt text must stay readable
if the asset ever fails again, and day mode is the bright-sunlight helm case.

### Asset recovery — two identical copies exist in the repo
| Path | Size | md5 |
|---|---|---|
| `deployment/features/boot-splash/theme/amboat-logo.png` | 65,885 | `92c88112…` |
| `deployment/d3kOS/dashboard/static/images/amboat-logo.png` | 65,885 | `92c88112…` |

Byte-identical. **Use the boot-splash copy** — `deployment/d3kOS/dashboard/` is a
SUPERSEDED read-only reference tree. (`assets/atmyboat-logo-transparent.png` is a
different, 1.4 MB file — far too large for a 28 px header.)

### Proposed fix (NOT yet applied — awaiting operator approval)
1. Create `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/images/` and
   copy `amboat-logo.png` into it.
2. Add an explicit accessible colour to `.sb-brand` so the alt text is legible in
   both themes. White gives **14.42:1 day / 18.30:1 night** — both far above 4.5:1.
   Targeted selector only; **do NOT touch `--ink2`/`--ink3` tokens** (S54 rule).
3. Playwright test: assert the logo asset returns 200 AND the computed contrast
   passes 4.5:1 in both themes.

### Why this matters beyond cosmetics
Issue 1 is an **AODA / WCAG 2.0 AA violation**. The project standard is a hard
minimum 4.5:1 contrast on all colour pairs. Text that is invisible against its
background fails that outright, and the helm is a bright-sunlight environment
where day mode is the mode that matters most.

### Constraint on any fix
`d3kos.css` `--ink2` / `--ink3` opacity tokens already fail WCAG. **Never edit
those tokens** — use targeted selector overrides only. (Standing rule, S54.)

### Investigation Steps
- [ ] Identify the header brand markup and its CSS selector(s)
- [ ] Determine the day-mode and night-mode colour values actually applied
- [ ] Measure the day-mode contrast ratio against the day background
- [ ] Locate the logo asset path and confirm whether the file exists and is served
- [ ] Confirm whether this is repo state or Pi-only drift (live read, per S109 rule)

### Fix Steps
- [ ] Issue 1 — set a day-mode wordmark colour meeting ≥4.5:1 contrast
- [ ] Issue 2 — repair or replace the broken logo asset
- [ ] Playwright test asserting computed colour contrast in BOTH themes and that the logo asset returns 200
- [ ] Deploy to lab Pi and verify

---

## BUG-50 — Settings "System Status" reports GPS, AIS, OpenPlotter and AvNav as healthy when they are not

**Status:** `[~]` **FIXED + DEPLOYED TO LAB PI S117 2026-08-02 — TDD-verified 7/10 failing pre-fix → 10/10 pass. NOT on the boat Pi.**

**Fix:** `/status` now reports GPS and AIS from *data* rather than from server liveness.
`gps` is true only with a position present AND a timestamp ≤10 s old. `ais` is three-state
(`receiving` / `no_targets` / `no_data`) — never a green light for an ambiguous condition.
The always-green OpenPlotter row is deleted. AvNav is checked via its own status API and the
chart count is surfaced so blank charts are visible. `check_service()` no longer reports a
broken service as up.

**The two decisive validations:**
- **Freshness, not presence.** With the GPS feed stopped, Signal K *still holds the last
  position* — it never expires stale data. A presence-only check would report GPS healthy
  forever after the GPS died. `gps` correctly returned to `false`.
- **Self-vessel exclusion.** With own ship holding a fresh position and zero other vessels,
  `ais` returned `no_targets`, not `receiving`. Without this, any boat with a GPS fix would
  have reported a false `receiving` with no AIS receiver at all.

**Tier 3:** Gemini 2.5-flash-lite, 3 rounds, ~11,800 tokens. Round 1 rejected (7 defects),
round 2 accepted with 3 Tier 1 corrections, round 3 discarded as a severe regression.
**One Tier 1 spec defect** — a `2xx-only` rule for `check_service` — was caught by validation,
not review: ai-bridge 404s on `/` while answering 200 on `/anchor/state`, so 2xx-only reported
a live service as dead. Corrected to `< 500`.

Full detail, including the Tier 3 round-by-round verdict and all 10 acceptance checks:
`deployment/docs/atomic-specs/BUG-50.md`. Test: `tests/bug50-status-truthfulness.spec.ts`.

**Original diagnosis follows.**
**Platform:** Pi — dashboard Settings page
**Severity:** HIGH — this is a safety-relevant false negative. A missing indicator tells the operator nothing; a **green** indicator tells them something false. At the helm, "AIS ● VIA SK" reads as "my AIS is working."
**Reported by:** operator, S117, while reviewing the open bug list — *"in the setting page at the top should indicate if ais gps etc are working."*

### Symptom
Settings → Section 1 "📡 System Status — Live" shows eight indicators, four of which do not
measure what their label claims. They can only ever show green (or, for GPS/AIS, green whenever
the Signal K *service* is running), regardless of whether the underlying capability works.

**The design intent is correct — the rows, labels and sub-labels are all right. The checks behind
them were never written.**

### Proven live on the lab Pi, 2026-08-02

| Settings displays | Actual measured truth |
|---|---|
| GPS **● VIA SK** (green) | **No GPS position exists.** `/signalk/v1/api/vessels/self/navigation/position` → **404**, the path is not present |
| AIS Receiver **● VIA SK** (green) | **Zero AIS targets.** `/signalk/v1/api/vessels/` returns exactly **1** vessel — own ship |
| OpenPlotter **● RUNNING** (green) | **Never checked at all** — hardcoded |
| AvNav Charts **● LIVE** (green) | Only proves *something answers on port 8080* |

`/status` on the Pi at the time of writing:
`{"ai_bridge":true,"avnav":true,"gemini":true,"internet":true,"ollama":false,"signalk":true}`
— note that **GPS and AIS are not fields in this response at all.**

### Root cause — four distinct defects in one section

**1. GPS and AIS are wired to the Signal K server's liveness, not to their own data.**
`templates/settings.html`, `loadStatus()`:
```js
setSI('si-gps',  d.signalk, d.signalk ? '● VIA SK' : '○ NO SK');
setSI('si-ais',  d.signalk, d.signalk ? '● VIA SK' : '○ NO SK');
```
Both read `d.signalk`. Signal K running ⇒ both green. Neither queries a position, a fix quality,
a satellite count, an AIS target, or a data timestamp. `/status` in `app.py` never gathers any.

**2. OpenPlotter is hardcoded green and can never report a fault.**
```js
setSI('si-openplotter', true, '● RUNNING');     /* infra — always up */
```
No check of any kind. The comment "always up" is an assumption written as a fact.

**3. AvNav's check proves a web server answers, not that AvNav works.**
`check_service(AVNAV_PORT)` → `requests.get('http://localhost:8080', timeout=2)`. AvNav shows
**● LIVE** while charts are blank (expired o-charts — OB-O05, currently blocking) or while AIS
fetching is switched off inside AvNav — which is exactly the state BUG-19/BUG-20 described. During
that period AvNav's **own** status API reported `ais INACTIVE disabled` while this page showed LIVE.

**4. `check_service()` treats any HTTP response as healthy.** It catches only `RequestException`,
so a service returning **500** is reported as up. A broken service and a working one are
indistinguishable to this check.

### Why this matters — it has already misled, historically

**BUG-32** established that AIS never reached Signal K at all: `rtl_ais` was pushing into TCP 10110,
which Signal K itself occupies as its NMEA0183 **output**, so every AIS message was discarded.
**Throughout that entire period this page displayed AIS as green.** That is not hypothetical — it
is what the code does and what the operator would have seen.

This is the concrete, provable instance of the general failure described in **BUG-11**
(*"A device that is incompatible, misconfigured, or silently failing produces the same user
experience as a working device"*). BUG-50 is worse than the case BUG-11 describes: the failing
device does not merely look the same as a working one, it looks **actively healthy**.

### Relationship to BUG-11 — deliberately separate
- **BUG-11** is open-ended research: a brand-agnostic health framework covering AIS, GPS,
  microphone and speaker, with no root cause established and no design.
- **BUG-50** is a specific, measured defect in existing shipped code with a known root cause and a
  bounded fix. It does not need the framework and should not wait for it.
Fixing BUG-50 produces the working reference that BUG-11's framework can later generalise.

### Scope — operator-set S117
**GPS, AIS, OpenPlotter and AvNav only.** Microphone and speaker indicators were explicitly
excluded and remain part of BUG-11.

### Proposed fix — NOT applied, needs an atomic spec
Check for **data**, not for a **running process**:
- **GPS** — read `navigation.position` from Signal K; require lat/lon present AND a `timestamp`
  within a freshness window. Absent path or stale timestamp ⇒ not healthy. Consider surfacing
  fix quality / satellite count if `navigation.gnss.*` is available.
- **AIS** — count entries under `vessels/` excluding own ship, with a last-update timestamp.
  Zero targets is legitimately ambiguous (no vessels in range vs receiver dead), so the honest
  states are three, not two: **RECEIVING** (targets seen recently), **NO TARGETS** (receiver alive,
  nothing in range), **NO DATA / UNKNOWN**. Distinguishing the first two needs a receiver-liveness
  signal separate from target count — design decision required.
- **OpenPlotter** — actually probe port 8081, or remove the row. A row that cannot fail is worse
  than no row.
- **AvNav** — probe AvNav's own status API rather than the bare port, so blank charts and disabled
  AIS fetching are visible.
- **`check_service()`** — treat non-2xx as down, not up.

⚠ **Do not report a tri-state as a binary.** "Green or red" is what created this bug. Where the
truth is genuinely unknown, the indicator must say **UNKNOWN**, not green.

### Affected files
| File | Role |
|---|---|
| `opt/d3kos/services/dashboard/app.py` | `/status` route (~line 279) and `check_service()` (~line 90) — must gather GPS/AIS data, not just port liveness |
| `opt/d3kos/services/dashboard/templates/settings.html` | Section 1 status grid (~lines 37–55) and `loadStatus()` / `setSI()` (~lines 696–740) |

### Fix status
- [ ] Atomic spec authored
- [ ] Failing test written first (TDD) — must assert green is NOT shown when Signal K is up but GPS/AIS data is absent
- [ ] `/status` extended with real GPS and AIS checks
- [ ] OpenPlotter hardcoded `true` removed
- [ ] AvNav check upgraded beyond a bare port probe
- [ ] `check_service()` non-2xx handling corrected
- [ ] Deploy to lab Pi and verify against a known-absent GPS/AIS state
- [ ] On-boat validation with real GPS fix and real AIS targets

---

## BUG-51 — The test harness cannot distinguish a partial run from a complete one

**Status:** `[~]` **ITEMS 1–5 DONE — S117 2026-08-02. Every test file in the project now executes.
BUG-52 and BUG-53 carry the two real failures this uncovered.**

### What items 1–5 delivered
| # | Item | Result |
|---|---|---|
| 1 | `tests/run-all.sh` — the single runner | Playwright + Node + pytest, one honest total, per-category breakdown. **Exits non-zero if anything fails OR if any known file could not be executed.** |
| 2 | Loud preflight | Aborts with exit 2 and a rebuild hint if Chromium cannot launch or the base URL does not answer. **"Environment broken" can no longer look like "tests passing."** Sets `LD_LIBRARY_PATH` correctly so the fault cannot recur silently. |
| 3 | Three `localhost:5000` defaults corrected | `bug15`, `bug26`, `bug27` now default to the Pi. **4 of those 6 tests passed immediately** — they had never run. |
| 4 | Four `.test.js` → `.test.cjs` | All four now execute. `bug29` and `bug38` pass. `bug30` and `bug36` **fail on real assertions** → **BUG-52**. |
| 5 | `flask` available to pytest | Installed user-level to `~/.local` (system Python is PEP-668 managed; `python3-venv` unavailable, no passwordless sudo). Also fixed a **test defect** in `test_bug41_settings_route.py`: it never registered the module in `sys.modules` before `exec_module`, so `Flask(__name__)` could not resolve `root_path` and every render raised `TemplateNotFound` → 500 — *which looks exactly like the BUG-41 defect the test exists to detect*. Now 3/3 pass. |

### A fifth fault found while building the runner — flaky tests from shared state
`bug16-18-24-labsim-verification` **failed in a full parallel run and passed 6/6 twice in isolation.**
Several specs inject state into Signal K, which is **shared global state on the Pi**; run
concurrently they collide. Our own standard requires deterministic tests. The runner therefore
forces `--workers=1`. A runner that reports flaky results is not an honest runner.

### Baseline before this work vs after
| | Before | After |
|---|---|---|
| Files that could not execute | **4** (silently) | 0 |
| Tests that could never run | **6** (wrong host) + 28 (no browser) | 0 |
| Python tests erroring at setup | 2 | 0 |
| A command that runs everything | **none** | `./tests/run-all.sh` |
| Failures visible to the operator | subset only | **all of them** |

The two remaining failures (**BUG-52**, **BUG-53**) are now *visible*, which is the point. They were
always there.

### VERIFIED BASELINE — `./tests/run-all.sh`, serial, S117 2026-08-02
```
playwright ........... 56 passed, 2 failed, 0 skipped
node ................. 4 files passed, 2 files failed
pytest ............... 38 passed across files, 0 files with failures
NOT GREEN.
```
**94 individual tests pass; 0 files are unexecutable; 0 skipped.** The runner correctly reports
**NOT GREEN**, because two real defects are open:
- 2 Playwright failures → **BUG-53** (`bug26` asserts the localhost literal BUG-48 removed)
- 2 Node file failures → **BUG-52** (`bug30`, `bug36` — possible regression of two FIXED bugs)

**Serial execution confirmed to remove the flakiness:** parallel gave 55 passed / 3 failed with
`bug16` failing spuriously; serial gives 56 / 2, and `bug16` passes.

⚠ **Do not "fix" the NOT GREEN by relaxing the runner.** It is telling the truth. It goes green when
BUG-52 and BUG-53 are resolved, and not before. That is the entire purpose of BUG-51.
**Platform:** Development environment (WSL) — affects every verification claim ever made in this project
**Severity:** HIGH — this is a **verification integrity** defect. It does not break the product; it breaks our ability to know whether the product works.

### Symptom
Session logs report suite results as "33/33", "36/36", "47/47 green". **Those were real counts of
real subsets, reported as if they were the whole suite.** No single command runs all the tests, so
each session ran whatever happened to work and reported that number. A broken environment was
indistinguishable from a passing suite.

### Four independent faults, found S117

**1. Chromium could not launch at all.**
`chromium_headless_shell-1228` failed with `libnspr4.so: cannot open shared object file`.
**28 browser tests failed with `browserType.launch` / `page.goto ERR_ABORTED`, which reads as an
ordinary test failure rather than an environment fault.** Request-only specs pass regardless, which
is how it stayed hidden. Root cause: the `LD_LIBRARY_PATH` recorded in MEMORY.md omitted the
`root/` level. Correct path: `$HOME/.local/pw-libs/root/usr/lib/x86_64-linux-gnu`.

**2. Three spec files default to a host that does not exist.**
`bug15-cog-flashing`, `bug26-anchor-watch-origin`, `bug27-status-bar-legibility` all use
`process.env.BASE_URL ?? 'http://localhost:5000'` — the Flask **dev-server** default. Nothing has
ever served that here. The working specs default to `http://192.168.1.237:3000`. **These 6 tests
could never run unless someone set `BASE_URL` by hand.** With the correct URL, 4 of the 6 pass.

**3. Four Node test files cannot execute.**
`bug29-engine-path-aliases.test.js`, `bug30-depth-fallback.test.js`, `bug36-engine-data-cache.test.js`,
`bug38-diag-panel-ids.test.js` use `require()` while `package.json` sets `"type": "module"`.
Siblings correctly use `.cjs`. `npx playwright test` with no filter **aborts on them**, so a
full-suite run cannot even complete.

**4. `flask` is not installed in the Python test environment.**
`tests/test_bug41_settings_route.py` — 2 of 3 tests error at setup with `ModuleNotFoundError:
No module named 'flask'` because it imports `app.py` directly.

### What was hidden behind fault 3 — the serious part
Two tests are **genuinely failing** with real assertions, invisible because their files could not run:
```
bug30-depth-fallback     AssertionError: transducer depth must render
bug36-engine-data-cache  AssertionError: cache must initialise all-null
```
**BUG-30 and BUG-36 are both marked FIXED + DEPLOYED.** Tracked separately as **BUG-52**.

`bug26`'s assertions are stale — it demands `const AI_BRIDGE = 'http://localhost:3002'`, the exact
hardcoded localhost **BUG-48 deliberately removed**, and navigates to `/anchor-watch.html` which
404s (real route `/anchor-watch`). Tracked separately as **BUG-53**.

### Fix — operator-authorised S117, items 1–5
1. `tests/run-all.sh` — one runner for Playwright + Node + pytest, one honest total, per-category
   breakdown. **Non-zero exit if anything fails OR if any known test file was not executed.**
2. **Preflight that fails loudly** — abort with a clear message if Chromium cannot launch or the
   base URL does not answer. This is the guard that makes the class non-recurring: "environment
   broken" must never again look like "tests passing".
3. Correct the three `localhost:5000` defaults.
4. Rename the four `.test.js` → `.test.cjs`.
5. Make `flask` available to the Python tests.

### Root cause
No single entry point for the suite. Every session ran a subset and reported it as the whole. The
counts were honest arithmetic on a dishonest denominator.

---

## BUG-52 — bug30 and bug36 assertions fail; BUG-30 and BUG-36 are marked FIXED

**Status:** `[x]` **CLOSED — NOT A BUG — S118 2026-08-03 by operator decision. Diagnosed: the code
is correct in both cases; both test expectations are stale, superseded by later fixes.
Remaining depth behaviour to be verified on the boat.**
**Platform:** Test suite (not the dashboard)
**Severity:** Downgraded HIGH → LOW on diagnosis. No regression occurred.

### Symptom
With the module-system fault (BUG-51 fault 3) worked around, both files execute and **fail on real
assertions**:
```
tests/bug30-depth-fallback.test.cjs    AssertionError: transducer depth must render  ('13.8' !== '4.2')
tests/bug36-engine-data-cache.test.cjs AssertionError: cache must initialise all-null (extra key depth_m)
```
Both were invisible because the files could not run at all.

### Why this mattered
- **BUG-30** (depth reads `belowKeel`, Signal K publishes `belowTransducer`) — also cited as the
  resolution that **closed BUG-18**.
- **BUG-36** (S105 deploy silently removed the M14 `_d3kEngData` cache) — also cited as part of
  what **closed BUG-16**.

Had these been real regressions, BUG-18 and BUG-16 would have been closed on false evidence.
**They were not. Both closures stand.**

### Root cause — candidate 1 (stale tests) CONFIRMED, candidate 2 (regression) RULED OUT
Neither test touches hardware. Both are JSDOM harnesses that call `SK_HANDLERS` directly with
hardcoded values — no Signal K, no N2K bus, no Garmin, no depth sounder in the path. The failures
are therefore not attributable to absent lab hardware, and not to anything on the Pi.

**`bug36`** — asserts via `deepStrictEqual` that the cache has exactly five keys. `instruments.js:30`
has six:
```js
window._d3kEngData = { coolant_c:null, oil_psi:null, rpm:null, bat_v:null, fuel_pct:null, depth_m:null };
```
`depth_m` was added deliberately by **BUG-34 (S110 2026-07-29)** — `instruments.js:140`,
`// BUG-34: always store metres`. The test was written S108, two days earlier. **Code correct.**

**`bug30`** — injects 4.2 metres, expects the string `"4.2"`, receives `"13.8"`.
4.2 × 3.28084 = 13.78 → 13.8 ft. `instruments.js:134` sets `let _unitPrefs = { temp: 'F', depth: 'ft' }`
— imperial default, added by **BUG-43 (S114 2026-07-31)** per the operator's stated unit preference.
The conversion is at `instruments.js:142`. The test was written S108, six sessions before unit
conversion existed, and assumes metric. **Code correct.**

Same defect class as **BUG-53**: a later fix intentionally changed behaviour an earlier test had
frozen. Three such stale expectations are now known (`bug30`, `bug36`, `bug26`).

### ⚠ Carried forward — assertions that have never executed
`bug30` aborts at line 35, so **assertions 3, 4 and 5 never ran.** Those are the safety-critical ones:

- 3 — `belowTransducer` must NOT overwrite an existing `belowKeel` value (overwriting would
  **overstate clearance**)
- 4 — `belowKeel` arriving later must take over from a transducer reading
- 5 — the shallow-water alarm must still fire on both sources

This behaviour is **unverified — not proven broken, and not proven working.** Per operator decision
S118, it will be **verified on the boat** against the real Garmin depth source rather than by
repairing the JSDOM fixture. Until that is done, no claim should be made that depth-source priority
is proven.

### Consequence for the test runner — read before touching `run-all.sh`
The two stale test files were **not** modified when this bug was closed. `./tests/run-all.sh` will
therefore continue to report **2 node file failures and NOT GREEN**. That is now a *known and
accepted* red, not an unknown one. ⚠ **Do not silence the runner, relax the assertions, or delete
the files to obtain green** — that is the exact failure mode BUG-51 exists to prevent. The correct
resolution is to update the two expectations (metric→imperial, five keys→six) once the boat
verification above has confirmed the intended behaviour.

---

## BUG-53 — BUG-26's test asserts the hardcoded localhost that BUG-48 removed

**Status:** `[ ]` **OPEN — logged S117 2026-08-02. Deferred to next session by operator decision.**
**Platform:** Test suite
**Severity:** LOW — the code is correct; the test is stale.

### Symptom
`tests/bug26-anchor-watch-origin.spec.ts` fails on two counts, both test defects:
1. It navigates to `/anchor-watch.html`, which returns **404**. The real Flask route is
   `/anchor-watch` (200).
2. It asserts `expect(content).toContain("const AI_BRIDGE = 'http://localhost:3002'")` — the exact
   hardcoded localhost that **BUG-48 deliberately removed**. The served page now correctly has
   `AI_BRIDGE = 'http://' + window.location.hostname + ':3002'`, with 6 references, all correct.

### Root cause
A later fix (BUG-48) superseded the approach an earlier fix (BUG-26) took, and BUG-26's test was
never updated. The test now enforces the defect.

### Fix
- [ ] Point the test at `/anchor-watch`
- [ ] Assert the `window.location.hostname` form, not the localhost literal
- [ ] Confirm the test would still catch a regression to bare `/anchor/*` calls on :3000

---

## BUG-54 — Cloud export has failed silently every ~10 minutes since 2026-02-20

> ### ⚠ S135 2026-08-28 — PART 2 INVESTIGATION. The regression has a DATE.
>
> **Reproduced live** from the lab Pi journal, 2026-08-28 07:58:12:
> ```
> Uploading to https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/data-ingress.php
> ✗ Export upload failed: HTTP 400: <html>…<center><h1>400 Bad Request</h1></center><hr><center>nginx</center>
> ```
> Part 1's fix is working — the diagnostics are visible in the journal.
>
> #### ⛔ THE RECORD'S FRAMING IS WRONG — corrected
>
> This entry says *"Cloud export has failed silently every ~10 minutes since 2026-02-20."*
> **Not true.** The queue's own history:
>
> | Period | Outcome |
> |---|---|
> | 2026-02-20 → 03-26 | 110 failures — placeholder host `d3kos-cloud-api.example.com` |
> | 2026-03-26 → **04-22** | **237 SUCCESSES** (155 in March, 82 in April) |
> | **2026-04-22** → 08-28 | **99 nginx 400s** (1 Apr, 19 Jul, 79 Aug) — still accumulating |
>
> **Export worked for four weeks. The last success and the first nginx 400 are both 2026-04-22.**
> This is a **regression with a date**, not a permanent misconfiguration — which makes it findable.
> ⚠ **The count is 99 now, not the 63 recorded.** ⚠ Note Phase 4 went live 2026-04-12, ten days before.
> **Ask what changed on the server on or about 2026-04-22.**
>
> #### What S135 ELIMINATED — do not re-test these
>
> | Hypothesis | Verdict |
> |---|---|
> | Wrong URL / staging leftover | **No.** `amboat_base_url = https://atmyboat.com`; endpoint string correct. BUG-55 holds. |
> | Malformed header values | **No.** api_key 64 chars, device_token 36 chars, **zero non-printable or space characters** in either. |
> | Headers rejected by nginx | **No.** All three real headers POSTed to `atmyboat.com/` from the Pi → **HTTP 200**. Tested singly too — all 200. |
> | Body too large | **No.** Bodies of 1/16/64/128/256 KB POSTed to the homepage → all **200**. Real payloads are only **23–33 KB** (n=237 completed, median 25,650 B). |
> | Request never reaches the server | **No.** nginx answers with its own HTML error page. |
> | PHP rejecting it | **No.** **Zero `data-ingress` entries** in `mobile/error_log` across a full week (21–28 Aug). nginx rejects **before PHP** — confirmed, not assumed. |
> | `/exports/exports/` doubled path | **NOT A BUG.** The directory genuinely exists with 248 files and **all 473 queue entries use it consistently.** Checked before reporting. |
>
> #### Where that leaves it
>
> `GET` on `data-ingress.php` reaches PHP (**405**). `POST` is rejected by nginx (**400**). The same
> headers and comparable body sizes are accepted at `/`. **So the fault is specific to POST + that path,
> it began on 2026-04-22, and 237 payloads of the same shape succeeded before that date.**
>
> `Uncertainty flag: the actual nginx rule is still unidentified. nginx logs sit outside the web root and
> FTP cannot reach them. Everything above narrows the search; none of it names the cause.`
>
> **Next diagnostic — needs operator approval, it is a POST to a production data endpoint:**
> from the Pi, POST a minimal payload to `data-ingress.php`. If a small body succeeds where 25 KB fails,
> the cause is size- or content-dependent and can be bisected. If a minimal body **also** 400s, the cause
> is the path or method and the payload is irrelevant. **One request settles which.**
>
> ⚠ Also still unchecked: **the boat Pi's `failed_exports/` count.** The lab Pi's is **0**. Boat is out of
> scope per operator directive S135 — carry it on the boat test card.


**Status:** `[x]` **FULLY FIXED + VERIFIED S140 2026-09-01. Three-layer fix: (1) `python-requests` UA blocked by nginx → `User-Agent: Mozilla/5.0` in export_worker.py + cloud_agent.py; (2) Pi `cloud-config.json` `amboat_api_key` updated to match HostPapa's current key; (3) `sanitize_key()` WordPress polyfill added to data-ingress.php. First successful export confirmed in lab Pi journal: `✓ Export uploaded: q_20260901_150256`. NOT YET verified on boat Pi.**
**Platform:** Pi — `d3kos-export-manager`; worker at `/opt/d3kos/services/export/export_worker.py`
**Severity:** Part 1 MEDIUM (fixed). Part 2 pending — severity still gated on the boat-Pi check.

---

### ⚠ S118 CORRECTION — the original diagnosis in this record was WRONG

The S117 entry stated: *"Delivery fails, and logs nothing… no error recorded anywhere… there is no
failure reason field."* **That is false.** Every queue entry in
`/opt/d3kos/data/exports/export_queue.json` carries a `last_error` field, and it has been recording
the exact reason the entire time. Nothing was ever missing from the data — it simply never reached
the journal or any UI. **The fix that follows is about visibility, not about adding a reason field
that already existed.**

### This was never one failure — it is FOUR, in sequence
Distinct `last_error` values across the 187 failed + 2 pending queue entries:

| Count | Recorded error | Reading |
|---|---|---|
| 110 | `HTTPSConnectionPool(host='d3kos-cloud-api.example.com', port=443)` | **A placeholder hostname was live in config.** `example.com` was never replaced. This is the original Feb–Mar failure. |
| 63 | `HTTP 400: <html>…400 Bad Request…nginx…` | **The current failure.** |
| 7 | `Export file not found: /opt/d3kos/data/exports/exports/export_…` | Note the doubled `exports/exports/` path segment — likely a second, separate defect |
| 6 | `HTTP 401: {"success":false,"error":"Invalid API key."}` | PHP *was* reached and rejected the key |
| 2 | `Expecting value: line 1 column 1 (char 0)` | non-JSON response body |
| 1 | `HTTPSConnectionPool(host='atmyboat.com') Max retries` | transient network |

The 401s prove the endpoint exists and PHP is reachable. The current 400 returns **nginx's own HTML
error page**, not PHP JSON, so nginx is rejecting the request before PHP runs.

### PART 1 — ROOT CAUSE OF THE INVISIBILITY (fixed S118)
`export_worker.py` reports every delivery step with `print()`. Under systemd, stdout is a **socket,
not a TTY**, so CPython **block-buffers it at 8 KB**. The worker's `Processing export`,
`Uploading to…`, `✗ Export upload failed…` and `Archived failed export…` lines sat in that buffer
and never reached the journal.

`export-manager.py` uses the `logging` module, which writes to **stderr — line-buffered** — which is
exactly why its lines were always visible while the worker's never were. That asymmetry is what made
the failures look unlogged.

Verified on the Pi before the fix: `systemctl cat` showed **no** `PYTHONUNBUFFERED`, and
`/proc/<pid>/fd/1` was `socket:[7155]`.

**Fix:** one line in `/etc/systemd/system/d3kos-export-manager.service`:
```
Environment=PYTHONUNBUFFERED=1
```
No application code changed. Repo copy and Pi copy are md5-identical (`b155ec6e…`).

**Test:** `deployment/v0.9.9.4/tools/verify-bug54.sh` — asserts the unit declares the variable, that
the **running process** actually has it (catches an edited-but-never-reloaded unit), and that the
service is active. **2/3 failed pre-fix, 3/3 pass post-fix.**

**End-to-end evidence — journal, immediately after the fix:**
```
Processing export: q_20260803_075645
Uploading to https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/data-ingress.php
Archived failed export: /opt/d3kos/data/exports/failed_exports/q_20260803_075645_failed.json
✗ Export upload failed: HTTP 400: <html>
```

### PART 2 — THE HTTP 400 ITSELF — ✅ ROOT CAUSE FOUND + FIXED S140 2026-09-01

**Root cause: `python-requests` User-Agent is blocked by nginx on HostPapa globally.**

Confirmed by two diagnostic POSTs from WSL2 this session (operator-approved):
- `curl/8.5.0` UA → HTTP **401** (PHP ran, rejected fake key correctly — endpoint reachable)
- `python-requests/2.31.0` UA → HTTP **400** (nginx blocked, identical to the Pi's failure)

This is the **same nginx rule that caused BUG-56** (Admin CRM VM) — HostPapa nginx blocks
`python-requests` User-Agent on POST. BUG-56 was fixed in S138 by adding `User-Agent: Mozilla/5.0`
to the CRM VM's Python requests. `export_worker.py` was never given the same override.

The S135 investigation eliminated "headers" as a cause by testing the 3 custom headers (Content-Type,
Authorization, X-Device-Token) via curl — not via Python requests. The implicit User-Agent sent by
the `requests` library was never tested as a standalone hypothesis.

The 2026-04-22 regression date (10 days after Phase 4 went live) is consistent with HostPapa
tightening nginx security rules for the `/mobile/` path after the new PHP files were deployed.
237 exports succeeded before the rule was added; 99 have failed since.

**Fix applied S140:**
- `export_worker.py:300-307` — added `'User-Agent': 'Mozilla/5.0'` to the headers dict
- `cloud_agent.py:144-149` — added `'User-Agent': 'Mozilla/5.0'` to `make_headers()` (same pattern)

Both files in canonical Pi tree: `deployment/v0.9.9.4/opt/d3kos/services/`.

**Deploy required:** push both files to lab Pi and restart `d3kos-export-manager`. Then verify next
export attempt returns 401 (auth) instead of 400 (nginx) — confirming PHP is now reached. Once a
valid `amboat_api_key` is configured, exports should succeed end-to-end.

### ⚠ STILL OPEN — lab Pi posts to PRODUCTION, not staging
`cloud-config.json` sets `amboat_base_url = https://atmyboat.com`. The code default in
`export_worker.py` is `https://atmyboat.com/staging`, and the service still *logs* the staging URL at
startup — but the actual POST goes to **production**. A development Pi is configured to write
telemetry into the live AtMyBoat database. **Operator decision required: should it be, or should the
lab point at staging?**

### Still to do
- [ ] **Deploy fix to lab Pi** — push export_worker.py + cloud_agent.py, restart d3kos-export-manager
- [ ] **Verify on lab Pi** — next export should return 401 (not 400), confirming nginx now passes it
- [ ] **Check the boat Pi's `failed_exports/` count** — still unanswered; still sets true severity
- [ ] Operator decision: lab Pi → staging or production?
- [ ] Investigate the doubled `exports/exports/` path in the 7 "file not found" errors
- [ ] Decide whether export health belongs in the Settings status panel (BUG-50 class defect —
      nothing in the UI surfaces this even now that the journal does)
- [ ] Decide whether the 152 archived payloads should be retried or discarded

### Symptom
`/opt/d3kos/data/exports/failed_exports/` holds **148 failed export payloads**. The oldest is
`q_20260220_164416_failed.json` — **2026-02-20, over five months ago.** Thirteen were produced on
2026-08-02 alone, roughly one every 10 minutes to an hour.

**Nothing surfaces this.** No alert, no dashboard indicator, no entry in any bug record until now. It
was found only by listing files changed on the Pi today.

### What is established
- **Generation succeeds.** The journal logs `Export generated and queued: export_20260802_111702.json`
  followed by `POST /export/generate 200`.
- **Delivery fails, and logs nothing.** The payload is moved to `failed_exports/` with **no error
  recorded anywhere** — not in the journal, not in `/opt/d3kos/logs/`, not inside the payload itself.
  The failed file contains only the export data; **there is no failure reason field.**
- `d3kos-export-manager` is `active` and `enabled`. It is not crashing.
- Payload carries `installation_id`, `format_version: 1.0`, and 13 categories: engine_benchmark,
  boatlog, marine_vision_captures, marine_vision_snapshots, qr_codes, settings, system_alerts,
  onboarding, telemetry, gps, engine, system_health, version.

### ⚠ Triage question that must be answered FIRST
**Is the lab Pi supposed to be exporting to the cloud at all?**
This is a development device. If it was never paired for cloud sync, these failures may be entirely
expected here and the real questions become (a) why does a device that cannot sync keep queueing
exports every few minutes, and (b) **would this fail the same way on the boat**, where the data
genuinely matters?

Do not assume it is a defect, and do not assume it is benign. **Check the boat Pi's
`failed_exports/` directory before concluding anything** — if the boat is also accumulating them,
five months of vessel telemetry, boat-log entries and engine history have never reached the cloud.

### Why this is worth taking seriously regardless of the answer
1. **A silent failure with no reason recorded is the same defect class as BUG-50** — the system is
   unable to tell its owner that something is not working. There is no indicator for export health
   anywhere in the UI.
2. Five months of accumulation with nobody noticing is itself the finding.
3. If it affects the boat, the Fix My Pi / fleet / Find My Boat features that depend on this sync
   have been receiving nothing.

### Investigation steps
- [ ] **Check the boat Pi's `failed_exports/` count** — this determines severity entirely
- [ ] Establish whether the lab Pi is cloud-paired, and whether it should be
- [ ] Find the delivery code path and determine why the reason is discarded — **a failure that
      records no reason cannot be diagnosed**; fixing that comes before fixing the failure
- [ ] Determine the actual error (auth, endpoint, payload size, network egress)
- [ ] Decide whether export health belongs in the Settings status panel alongside the BUG-50 work
- [ ] Consider whether 148 stale payloads should be retried or discarded

### Not investigated further this session
Found at session close while answering "what was deployed to the Pi today". Logged per the standing
rule; no fix attempted, no files touched.

---

## BUG-55 — 17 code sites still point at atmyboat.com/staging; operator states all should be production

**Status:** `[~]` **FIXED + DEPLOYED LAB PI S118 2026-08-03 — all 17 sites repointed to production
plus the fleet path defect; guard test 4/4 pass; zero staging references remain in the canonical
tree or on the lab Pi. NOT on boat Pi.**
**Operator decision (S118):** *"it should all be pointing to production not staging at this point"*,
reaffirmed — the PWA included. The CLARIFICATION GATE below was answered: **everything, PWA
included.** The `app.js` `API_BASE`, `data-export.php` and `data-delete.php` URLs were repointed.

### What was changed
- **17 occurrences** of `atmyboat.com/staging` → `atmyboat.com` across **13 version-controlled files**
  (9 Category A fallbacks + Category B's `update_agent.py`, `fleet_push_service.py` ×2, `app.js` ×4,
  and `d3kos-diagnostic.service`'s `Documentation=` line).
- **Fleet path defect fixed at the same time:** `fleet_push_service.py` ×2 now carry the full
  `/wp-content/themes/twentytwenty-child/mobile/fleet-ingest.php` path, matching `fleet-push.env`.
- **`fleet-push.env`** corrected on the Pi. ⚠ **This file is Pi-only and NOT version-controlled** —
  same exposure class as `avnav_server.xml` (BUG-33). It travels with an SD clone but a rebuild from
  the repo silently reverts it. Guard test 3 exists specifically to catch that.
- Services restarted: `d3kos-export-manager`, `d3kos-cloud-agent`, `d3kos-alert-watcher`,
  `d3kos-fleet-push`, `d3kos-agents`. `d3kos-diagnostic` was already inactive and was not started.
  `app.js` is statically served — no restart needed.
- **All 13 files verified md5-identical between repo and Pi after deploy.**

### Side effect — a misleading log line is now correct
`export-manager.py:41`'s constant was why the service logged `Central API URL:
https://atmyboat.com/staging` while actually POSTing to production. It now logs
`Central API URL: https://atmyboat.com`. Observed during BUG-54; fixed here.

### Test
`deployment/v0.9.9.4/tools/verify-bug55.sh` — **4/4 pass.** Asserts: no staging URL in the canonical
tree; none live on the Pi; `fleet-push.env` carries production **and** the full theme path; and the
code default agrees with the env file. The script excludes itself from its own scan — it necessarily
names the forbidden string in its grep patterns, and self-failed on the first run until fixed.

### ⚠ NOT done — out of scope for this session
**No HostPapa live file was touched.** If a separate copy of the PWA is served from
`atmyboat.com/staging/app/`, repointing the Pi's `app.js` does not move it. Relocating or updating
the hosted PWA is a live-site modification requiring its own approval and an FTP deploy.

### ⚠ This does NOT fix BUG-54
BUG-54's HTTP 400 was **already** going to production (`cloud-config.json` set the key). Repointing
the defaults changed nothing about that failure. **BUG-54 Part 2 remains open.**

### Superseded — original S118 logging entry follows
**Platform:** Pi services (`/opt/d3kos/services/`), the PWA (`var/www/html/app.js`), and one config file
**Severity:** MIXED — see the two categories. Category B is live-wrong today; Category A is latent.
**Origin:** Found while diagnosing BUG-54, after the operator stated: *"it should all be pointing to
production not staging at this point."*

### Category A — staging as a FALLBACK DEFAULT (latent, 9 sites)
Pattern: `config.get('amboat_base_url', 'https://atmyboat.com/staging')`. These resolve to
**production today**, because `cloud-config.json` sets `amboat_base_url = https://atmyboat.com`. They
are only a trap: if that config key is ever missing, unreadable, or reset by a rebuild, the device
**silently starts talking to staging** with no error and no log line.

| File | Line |
|---|---|
| `opt/d3kos/services/ai/alert_watcher.py` | 320 |
| `opt/d3kos/services/alert_watcher.py` | 379 |
| `opt/d3kos/services/ota_upgrade.py` | 395 |
| `opt/d3kos/services/cloud-agent/ota_upgrade.py` | 406 |
| `opt/d3kos/services/diagnostic/diagnostic_agent.py` | 174 |
| `opt/d3kos/services/cloud_agent.py` | 689 |
| `opt/d3kos/services/cloud-agent/cloud_agent.py` | 604 |
| `opt/d3kos/services/export/export_worker.py` | 33 (`__init__` default) |
| `opt/d3kos/services/export/export-manager.py` | 41 (`CENTRAL_API_URL` constant) |

Note `export-manager.py:41` is why the service **logs** `Central API URL: https://atmyboat.com/staging`
at startup while actually POSTing to production — a misleading log line, observed during BUG-54.

### Category B — HARDCODED staging with no config override (live-wrong now, 5 sites)
These are talking to staging **right now**. `cloud-config.json` does not override them.

| File | Line | What it does |
|---|---|---|
| `opt/d3kos/services/agents/agents/update_agent.py` | 47 | `VERSION_URL` — **OTA version checks hit staging** |
| `opt/d3kos/services/fleet/config/fleet-push.env` | 1 | `FLEET_INGEST_URL` — fleet telemetry to staging |
| `opt/d3kos/services/fleet/fleet_push_service.py` | 40 | fleet ingest default → staging |
| `var/www/html/app.js` | 10 | `API_BASE` — **the whole PWA** |
| `var/www/html/app.js` | 2652, 2697 | `data-export.php`, `data-delete.php` |

### ⚠ A second defect found inside Category B
`fleet_push_service.py:40` defaults to `…/staging/mobile/fleet-ingest.php` — **missing the
`/wp-content/themes/twentytwenty-child/` path segment** that `fleet-push.env:1` includes. The two
disagree, so the code default is a 404 regardless of which environment it points at. Fix the path at
the same time as the host, not separately.

### ⚠ CLARIFICATION GATE — contradiction, do not resolve by assumption
`MOBILE_APP_STRATEGY_BRIEF.md` and MEMORY.md both record the documented architecture as
**"PWA hosted at `atmyboat.com/staging/app/`"**. If the PWA is *served from* staging, repointing its
`API_BASE` at production makes a page served from staging call production endpoints. That is a
deliberate architectural decision, not a find-and-replace. **Operator must confirm whether the PWA
itself has moved to production, or only the Pi-side services should repoint.**

### Fix steps (none executed)
- [ ] Operator decision on the PWA question above
- [ ] Category A: change the 9 fallback defaults to production (no behaviour change today; removes the trap)
- [ ] Category B (Pi-side): `update_agent.py`, `fleet-push.env`, `fleet_push_service.py` → production, **and fix the fleet path segment**
- [ ] Category B (PWA): only after the decision above
- [ ] `export-manager.py:41` — also corrects the misleading startup log line
- [ ] Re-run `tools/check-drift.sh`; keep repo and Pi md5-identical
- [ ] Consider: should `amboat_base_url` be the single source of truth, with **no** hardcoded fallback at all, so a missing key fails loudly instead of silently using the wrong environment?

---

## BUG-56 — Admin Console HTTP 400 Bad Request; HostPapa database API endpoint failing

**Status:** `[x]` **FIXED S138 2026-09-01 — three-layer fix: Wordfence WAF bypassed via WP REST API; VM config.json updated; nginx User-Agent block resolved in db.py. Dashboard shows green. MEDIUM → RESOLVED.**
**Severity: MEDIUM → RESOLVED.**

### S138 ACTUAL FIX — 2026-09-01 (final, verified)

**Three-layer root cause (each layer blocked independently):**

**Layer 1 — Wordfence WAF content-scan block (503):**
`crm-proxy.php` (renamed to `admin-crm-api.php`) was blocked by Wordfence because its content matches a webshell pattern: external Bearer auth + PDO DB queries + `php://input`. Wordfence scans file CONTENT, not just filenames. The block fires at the LiteSpeed server level; a subdirectory `.htaccess` with `php_value auto_prepend_file none` was tried and confirmed ineffective at that level.

**Fix:** WordPress REST API endpoint registered at `d3k/v1/crm` via `add_action('rest_api_init', ...)` in `functions.php`. Wordfence never blocks registered WP REST routes. All 12 actions ported from `admin-crm-api.php`: `test_db`, `get_customers`, `get_customer`, `update_tier`, `reset_fmp`, `get_audit_log`, `get_diagnostics`, `find_user_by_email`, `browse_table`, `get_fleets`, `get_fleet_detail`, `suspend_fleet`. Returns `WP_REST_Response` objects instead of `echo json_encode + exit`.

**Layer 2 — VM config.json wrong proxy_url:**
`config.json` had `proxy_url = .../admin-crm-api.php`. Updated to `https://atmyboat.com/wp-json/d3k/v1/crm`. Curl test of the REST endpoint immediately returned `{"ok":true,"db":"atmyb197_wp59874","server":"8.4.10-cll-lve"}` HTTP 200.

**Layer 3 — nginx/Wordfence User-Agent block (400 from nginx):**
After config.json fix, Flask still got HTTP 400. curl worked; Python `requests` didn't. Root cause: nginx (or Wordfence's nginx integration) returns 400 for requests with the `python-requests` User-Agent. Flask's `requests` library sends `python-requests/2.x.x` by default.

**Fix:** Added `"User-Agent": "Mozilla/5.0"` to `_headers` in `/home/d3kos-admin/db.py` line 10.

**Files changed:**

| Location | File | Change |
|----------|------|--------|
| HostPapa `mobile/` | `functions.php` (child theme) | WP REST endpoint `d3k/v1/crm` appended — 12 actions |
| HostPapa `mobile/` | `admin-config.php` | DB credentials corrected: both staging+production → `atmyb197_wp59874` / `CSSM3(T4AgGNWBW*` |
| HostPapa `mobile/` | `.htaccess` | `php_value auto_prepend_file none` added (ineffective but harmless) |
| VM `/home/d3kos-admin/config/` | `config.json` | `proxy_url` → `https://atmyboat.com/wp-json/d3k/v1/crm` |
| VM `/home/d3kos-admin/` | `db.py` | `_headers` dict — added `"User-Agent": "Mozilla/5.0"` |

**Verification:** Admin Console at `http://192.168.236.5:5000` — "HostPapa Database" indicator green. Confirmed by operator 2026-09-01.

**WSL2 → VM access note:** 192.168.236.5 (VirtualBox Host-Only) unreachable from WSL2 directly. All VM commands run via `plink.exe` at `/mnt/c/Users/donmo/AppData/Local/Microsoft/WindowsApps/plink.exe`. VM login: `skipper` / `d3kos2026$`. Sudo: `echo 'd3kos2026$' | sudo -S bash -c "..."`.

**Note on earlier S138 "fix" records:** An earlier entry in this session recorded `proxy_url → crm-proxy.php` as the fix. That was premature — Wordfence was still blocking the PHP file. The REST API + User-Agent fix above is the actual resolution.

---

## S135 INVESTIGATION — 2026-08-28

### The mechanism, end to end

The CRM does not hold endpoint URLs. It holds one `proxy_url` and **derives every endpoint by
string-replacing the filename out of it**:

```python
# app_patched.py:38-83
_tickets_url = config["proxy_url"].replace("api-admin.php", "admin-api-tickets.php")
_issues_url  = config["proxy_url"].replace("api-admin.php", "issue-api.php")
# ...9 endpoints derived this way
```

`DEPLOYMENT_INDEX.md:1226` records what then happened:

> VM `/home/d3kos-admin/config/config.json` — **[UPDATED — S58]** `proxy_url` changed from
> `.../mobile/admin-api.php` to `.../mobile/crm-proxy.php`.

**Once `proxy_url` ends in `crm-proxy.php`, every `.replace()` matches nothing and returns the string
unchanged.** Each call then POSTs its payload to `crm-proxy.php` regardless of which endpoint it meant.

Production `crm-proxy.php` (411 lines, 19,525 B) knows **12 actions** — `test_db`, `get_customers`,
`get_customer`, `update_tier`, `reset_fmp`, `get_audit_log`, `get_diagnostics`, `find_user_by_email`,
`browse_table`, `get_fleets`, `get_fleet_detail`, `suspend_fleet`. Anything else hits `:404-405`:

```php
http_response_code(400);
echo json_encode(['error' => 'Unknown action: ' . htmlspecialchars($action)]);
```

**That is the HTTP 400 reported in S120.** Not malformed headers, not nginx, not credentials — a proxy
correctly rejecting an action it does not implement, because the caller never redirected to the file
that does.

### ⚠ Both prior diagnoses were wrong, in opposite directions

- **S120** logged HTTP 400 and listed six candidate causes — malformed headers, bad POST body, PHP
  error, nginx constraints, auth failure, DB credentials. **The 400 was real and correctly observed.
  None of the six is the cause.**
- **S131** probed `api-admin.php`, got 404, and concluded *"THE ENDPOINT DOES NOT EXIST… This is a BUILD
  task, not a debugging task."* **It probed a placeholder string.** `api-admin.php` was never meant to
  be requested; the 404 is meaningless. It also declared all six S120 causes superseded — correct, but
  for the wrong reason.

⚠ **Writing `api-admin.php` — the S131 recommendation — would have created a file to satisfy a token in
a config string, and the CRM still would not have called it.**

### ⚠ There are TWO spellings of the placeholder, and that is decisive

| Module | Token used |
|---|---|
| `support-tickets/crm/app_patched.py` | `api-admin.php` |
| `autonomous-agents/crm/failure_routes.py` | `admin-api.php` |
| `autonomous-agents/crm/update_routes.py` | `admin-api.php` |
| `autonomous-agents/crm/fleet_versions_routes.py` | `admin-api.php` |
| `diagnostic-console/crm/ticket_diagnose_routes.py` | `admin-api.php` |

**`api-admin` vs `admin-api`.** Therefore **no single value of `proxy_url` can make both sets work** —
whatever it is set to, at least one group of call sites no-ops and posts to the wrong file. This is
true independently of the S58 change and would have broken eventually regardless.

### The real defect is the pattern, not the value

Deriving an endpoint URL by replacing a filename inside a base URL fails **silently** the moment the
configured filename changes. `str.replace()` on a non-match returns the original string — no exception,
no log line. The same class as BUG-54 (a swallowed diagnostic) and BUG-84 (an unverified assumption).

**Fix — in order:**
1. **Read `proxy_url` from the VM's `/home/d3kos-admin/config/config.json`.** That single value confirms
   which call sites are currently broken. It is the only remaining unknown.
2. **Change the config to a base *directory* URL** (`.../mobile/`) and have each module **append** its
   filename. Delete every `.replace()`.
3. **Unify the two spellings** as part of the same change, or the bug returns.
4. Add a startup assertion: if a derived URL still contains `admin-api` or `api-admin`, **fail loudly**.
   A guard that logs nothing is what allowed this to persist from S58.

`Uncertainty flag: the CRM VM (192.168.236.5) is UNREACHABLE from the lab network — ping returns 100%
packet loss. The current value of proxy_url could NOT be read this session; the S58 value is taken from
DEPLOYMENT_INDEX.md, which is a record, not a live read. Confirm before implementing. The two-spelling
finding above does NOT depend on it.`

### What the unblock condition becomes

`PHASE3-blocked-items.md` asks for *"crm-proxy.php from 192.168.236.5, to establish the exact contract
the console expects."* **Superseded.** `crm-proxy.php` lives on HostPapa and was read this session; its
12 actions are listed above. **All nine replacement targets already exist in production**
(`admin-api-tickets.php`, `diagnostic-bundle.php`, `diagnostic-fix.php`, `diagnostic-resolve.php`,
`diagnostic-past-cases.php`, `config-backup-status.php`, `issue-api.php`, `update-publish.php`,
`version-api.php`). **Nothing needs building.** The only thing still needed is **one config value off
the VM.**

⚠ **The repo's `crm-proxy.php` is 32 lines and knows 2 actions; production's is 411 lines and knows 12.**
Another instance of BUG-88 — do not audit this file from the repo copy.

### Related

- **BUG-88** — the repo copy is drastically stale; 32 production files unsourced
- **BUG-73 / BUG-75 / BUG-71** — same session, same lesson: a status code is a response, not a fact
- **BUG-54** — silent failure from a swallowed signal

## BUG-57 — Unauthorized mass user account creation via MailPoet exploitation

**Status:** `[x]` **CLOSED S140 2026-09-01 — MailPoet investigation complete. All three questions answered from live screenshots. MailPoet was NOT a vector. Only `/register/` was exploited; BUG-63 closed it. See S140 MailPoet findings below.**
Was: `[~]` HIGH/CONTAINED S135 2026-08-28. Was: `[ ]` CRITICAL — ACTIVE BREACH (S121).

---

## S140 MAILPOET INVESTIGATION — 2026-09-01 — CLOSED

**Q1 — Did MailPoet carry the 62,000 accounts?**
**NO.** Live MailPoet Subscribers page (screenshot 2026-09-01): **14 total subscribers**.
Breakdown: Subscribed 12, Unconfirmed 2, Unsubscribed 0, Inactive 0, Bounced 0.
Most recent subscription date: **February 2026**. Zero entries in the June–August 2026 attack window.
No bulk import events of any kind. No Logs tab in the Subscribers view.

**Conclusion:** The S121 record's claim that "MailPoet was a second confirmed vector" is **refuted by evidence**. MailPoet was never exploited. All 62,000 accounts came through `/register/`.

**Q2 — Are any MailPoet API keys exposed or unrotated?**
**CLEAN.** Key Activation tab (screenshot 2026-09-01): one MSS key exists, shown masked (not exposed), status "Your key is valid / MailPoet Sending Service is active." No external exposure. No rotation required.

**Q3 — Is "auto-create WordPress user on subscribe" enabled?**
**NO.** Answered S138 2026-09-01. Feature removed from MailPoet 7.1. Confirmed by full Advanced tab review (three screenshots 2026-09-01): no such setting exists in any tab.

**Root cause (final):** Sole confirmed attack vector = `/register/` endpoint calling `wp_create_user()` directly, bypassing all WordPress registration controls. Closed by BUG-63 device gate, live 2026-08-25. No MailPoet involvement.

**Other Advanced tab observations (S140):**
- Sending: MailPoet Sending Service (recommended) — correct
- Engagement tracking: Full — no security concern
- Spam protection on MailPoet forms: Built-in CAPTCHA (default) — correct
- Protect registration forms (WP /register/): No — moot; BUG-63 device gate closes /register/ independently
- Logging: Errors only — no import history recorded at this level

---

## ⚠ S135 RE-SCORING — 2026-08-28 — read this before the S121 record below

### The S121 containment record credits a control that did nothing

S121 recorded: *"Primary Vector Closed: Public registration disabled in WordPress
(Settings → General)."* **That control was a no-op.** BUG-63 later established that
`deployment/features/auth-pages/php/page-register.php:88` calls `wp_create_user()` **directly** — a
custom page template that never consults WordPress's `users_can_register`. Unticking "Anyone can
register" therefore changed nothing, while making the form appear closed.

**Consequence: between 2026-08-13 (S121) and 2026-08-22 (S127) the registration form was believed
closed and was in fact fully open.** The real containment was S127 setting `/register/` to Draft; the
real fix is BUG-63's device gate, live 2026-08-25.

⚠ `Uncertainty flag: the August drop in attack volume (72,628 POSTs in July → 188 in August) is NOT
explained by the registration setting. Candidates are the .htaccess hardening, the IP blocks, or the
botnet moving on. The cause was never established and should not be asserted.`

**Process lesson — the same one as BUG-08 and BUG-81:** a control was recorded as effective without
anyone reading the code path it was supposed to govern. *Verify against the code, not the setting.*

### Verified closed as of S135

| | Control | Evidence |
|---|---|---|
| ✅ | Registration vector — `/register/` device-gated; requires a server-issued 10-char code tied to an operator-approved device | BUG-63 `[x]` FIXED + LIVE 2026-08-25 (commits `d9915753` + `a3914b20`) |
| ✅ | `/wp-json/wp/v2/users` returns 403 | S121; re-confirmed by the deleted GATE 0 item G7 |
| ✅ | WP Activity Log installed; `.htaccess` hardened (REST, xmlrpc, SQLi patterns) | S121 |
| ✅ | 2FA enrolled on the admin account | BUG-69 Step 1, S128 |
| ✅ | 9 attacker IPs blocked | BUG-67, S128 |
| ✅ | 62,000 accounts removed; verification sweep found **0** remaining unverified subscriber accounts created ≥ 2026-06-01 | operator Aug 2026 + `cleanup-botnet-accounts.php`, S134-cont |

### Operator decisions — 2026-08-28 (S135)

| Item | Decision | Reason |
|---|---|---|
| **Severity** | CRITICAL/ACTIVE → **HIGH/CONTAINED** | The "active ongoing breach" label was false and was distorting prioritisation. MailPoet keeps it at HIGH. |
| **CAPTCHA on `/register/`** | **DROPPED — closed as redundant, not deferred** | The device gate requires a server-issued code tied to an operator-approved device. CAPTCHA proves "a human" and is strictly weaker. Adding it would harden a form bots can no longer submit to. **Do not re-raise this as outstanding work.** |
| **User notification of the 62,000 address holders** | **OUT OF SCOPE for v0.9.9.4** | Operator decision, S135. ⚠ This is a legal/privacy question (PIPEDA breach-notification and record-keeping), **not** a technical one. Recorded as out of scope, **not** as resolved. Do not treat this entry's closure as advice that no notification is required. |
| **MailPoet investigation** | **IN SCOPE — operator has MailPoet admin access** | The sole remaining open item. Spec: `atomic-specs/BUG-57-MAILPOET.md`. |

### S138 G8 RESOLVED — 2026-09-01

**Q3 — "Auto-create WordPress user on subscribe" — ANSWERED: feature does not exist in MailPoet 7.1.**

Operator inspected the full MailPoet Basics tab and Sign-up Confirmation tab (screenshots reviewed
2026-09-01). The setting is absent from both tabs and from the bottom of the Basics tab page.
MailPoet removed this feature in a version prior to 7.1 (the installed version, confirmed bottom-right
of screenshots). **This vector does not exist. BUG-57 stays HIGH/CONTAINED — does NOT re-escalate
to CRITICAL.**

**"Subscribe in comments" is checked** — now acceptable: BUG-60 (fixed same session) requires login
to comment, so only device-paired WP users see that checkbox.

Remaining open questions (Q1 and Q2 — lower priority, non-escalating):
1. MailPoet subscriber **import logs** for June–August 2026 — how the bulk accounts got into MailPoet
2. **MailPoet API keys** — exposure / rotation status

These are investigative, not blocking. BUG-57 can be closed for v0.9.9.4 purposes once Q1/Q2 are
reviewed; they do not affect the current security posture.

### The one thing still open (UPDATED S138)

**MailPoet was accessed directly and how was never established — but the "auto-create WP user"
vector is confirmed absent in MailPoet 7.1.** Q1 (import logs) and Q2 (API keys) remain, but
neither can re-escalate to CRITICAL given the current device gate. BUG-57 stays HIGH/CONTAINED.

Three questions — Q3 answered S138:
1. What do the MailPoet subscriber **import logs** show for June–August 2026 — bulk events, source IP, method?
2. Are any **MailPoet API keys** exposed or unrotated?
3. ~~Is **"auto-create WordPress user on subscribe"** enabled?~~ **ANSWERED S138: feature absent in MailPoet 7.1. Does not exist.**

**Superseded:** the "Immediate Remediation Steps" and "Prevention Checklist" sections below are the
S121 plan. Items 1–4, 8 are done; the CAPTCHA item is dropped per the table above; items 5–7 and 9
survive only insofar as they serve the MailPoet questions. Read the S135 tables above as authoritative.

---

### Symptoms
- **62,000+ unauthorized user accounts created** on atmyboat.com (all Subscriber role)
- Accounts created over period: June 2026 – ongoing (weekly basis)
- Spammers exploited MailPoet directly to inject spam campaigns
- No audit trail or notification when accounts were created
- No access logs showing which IP addresses or methods were used for account creation
- Operator manually removed 62,000 users; system continues to see new spam accounts weekly

### Timeline
- **June 2026:** Attack began
- **August 2026:** Operator discovered 62,000+ spam accounts; began manual removal
- **2026-08-13:** Reported to Claude Code; breach confirmed ongoing

### Root Cause — Under Investigation

**CONFIRMED VECTORS:**
1. ✅ **WordPress REST API is publicly exposed** — `/wp-json/wp/v2/users` endpoint readable (returns 401 on unauthenticated POST, so REST API itself is not directly exploited for user creation)
2. ✅ **MailPoet Plugin accessed directly by spammers** — unknown how they obtained credentials or bypassed authentication
3. ✅ **Public `/register/` page allows bulk account creation** — uses nonce protection, but vulnerable to automated bot submissions if nonce-parsing is implemented

**UNKNOWN VECTORS:**
1. **MailPoet auto-user-creation setting** — May have "auto-create WordPress user when email is added to list" enabled; spammers bulk-imported email addresses via API or form
2. **MailPoet authentication bypass** — Potential vulnerability in MailPoet plugin allowing unauthenticated access to subscriber import endpoints
3. **Automated bot attacking /register/form** — Parsing nonce from HTML response, then submitting automated registrations with random emails
4. **Third-party plugin vulnerability** — Unknown plugin may have an endpoint that auto-creates users or integrates with MailPoet

### Affected Systems

| System | Impact | Verified |
|--------|--------|----------|
| WordPress Users Table | 62,000+ spam Subscriber accounts created | ✅ Yes |
| MailPoet Subscribers List | All spam accounts added to mailing list | ✅ Yes |
| Spam Campaigns | Emails sent to boaters via MailPoet | ✅ Yes (operator removed users) |
| REST API (`/wp-json/`) | Publicly readable (low security risk, but exposed) | ✅ Yes |
| Admin Notification | Zero alerts/notifications when mass accounts created | ✅ Yes (confirmed gap) |
| Audit Logs | No record of account creation method or IP source | ⚠️ Unknown (see next steps) |

### Immediate Remediation Steps Required

**PRIORITY 1 — Within 24 hours:**

1. **Disable REST API user endpoint** via `.htaccess` on HostPapa:
   ```
   # Block unauthorized REST API user access
   <FilesMatch "^/wp-json/wp/v2/users.*">
       Deny from all
   </FilesMatch>
   ```

2. **Secure MailPoet subscriber import:**
   - MailPoet Admin → Subscribers → Settings → Check "Require authentication to import"
   - Review MailPoet API keys — regenerate any that may be exposed
   - Check MailPoet logs for bulk imports (Settings → Logs)

3. **Enable user account audit logging:**
   - Install plugin: **User Activity Log** or **WP Activity Log**
   - Log user creation, deletion, role changes
   - Set alert for bulk user creation (>10 users/hour)

4. **Block bot submissions to /register/:**
   - Disable nonce in /register/ temporarily OR
   - Add rate limiting: max 5 registration attempts per IP per 24 hours via `.htaccess` or plugin (e.g., **Wordfence**, **iThemes Security**)
   - Add CAPTCHA to /register/ form

**PRIORITY 2 — Within 1 week:**

5. **Investigate attack logs on HostPapa:**
   - Get raw access logs from cPanel: Metrics → Raw Access Logs
   - Search for:
     - `/register/` POST requests with high volume from single IP
     - `/wp-json/wp/v2/users` requests
     - MailPoet subscriber import endpoints
   - Identify attacker IP ranges and block via `.htaccess` or firewall

6. **Audit user metadata:**
   - Check if spam accounts have `atmyboat_email_verified` = `0` or `1`
   - If `= 0`, email verification bypass did NOT occur (they bypassed form nonce)
   - If `= 1`, email verification was either bypassed or automation verified emails (test MailPoet auto-verify)

7. **Review MailPoet event log:**
   - MailPoet Admin → Subscribers → Logs
   - Identify when the 62,000 accounts were added
   - Check if import was API-based or form-based

8. **Implement 2FA for admin accounts:**
   - Force 2FA on all admin and MailPoet-admin accounts
   - Require strong passwords (20+ chars, mixed case)

9. **Consider IP whitelisting:**
   - If your team accesses HostPapa/MailPoet from fixed IPs, whitelist them via `.htaccess`

### Files Affected

| File | Issue | Status |
|------|-------|--------|
| `page-register.php` | Public registration form (no rate limiting) | Needs rate limit |
| `inc/atmyboat-config.php` | May contain exposed API keys (if committed to Git) | Review .gitignore |
| REST API (WordPress core) | `/wp-json/wp/v2/users` publicly readable | Needs firewall rule |
| MailPoet plugin settings | Possible "auto-create user" setting enabled | Needs review |
| `.htaccess` on HostPapa | No protection rules defined | Needs rules added |

### For Don — What to Check on HostPapa

**Via cPanel (click-by-click):**

1. **File Manager:**
   - Navigate to `public_html/`
   - Find `.htaccess` file (may be hidden; enable "Show Hidden Files" in settings)
   - Check for any existing restrictions (if blank, add remediation rules above)

2. **Raw Logs:**
   - Click: **Metrics** → **Raw Access Logs**
   - Download logs for last 7 days
   - Search for `/register/` and `/wp-json/` patterns
   - Look for bulk POST requests from single IP

3. **Error Logs:**
   - Click: **Metrics** → **Error Logs**
   - Search for `400`, `401`, `403` errors around June 1 – August 13
   - Any patterns on specific endpoints?

4. **MailPoet (in WordPress Admin):**
   - Log in as admin at atmyboat.com/wp-admin/
   - Go: **MailPoet** → **Subscribers** → **Logs** tab
   - Search for bulk import events in June/July/August
   - Click any bulk import to see source IP and method

5. **WordPress Users List:**
   - Go: **Users** → Search for spam accounts (they all likely have similar naming or email patterns)
   - Spot-check user metadata: edit one spam user, scroll to bottom, look for `atmyboat_email_verified` value

### Prevention Checklist

- [ ] REST API user endpoint blocked via `.htaccess`
- [ ] MailPoet authentication hardened (API keys rotated, import restricted)
- [ ] Rate limiting added to `/register/` form
- [ ] CAPTCHA added to `/register/` form
- [ ] User activity logging plugin installed
- [ ] Admin accounts secured with 2FA
- [ ] Access logs downloaded and analyzed from HostPapa
- [ ] MailPoet event logs reviewed for bulk import source
- [ ] User metadata checked (email_verified flag status)
- [ ] Root cause hypothesis confirmed via logs

### Related Bugs

- **BUG-55:** REST API exposure discovered alongside BUG-57; both indicate infrastructure security gaps
- **BUG-54:** Similar HTTP 400 issues on endpoints; suggests HostPapa configuration needs review

---

## BUG-58 — HIGH: Exposed Remote Access API key in public GitHub repository

**Logged:** S129 2026-08-23
**Status:** `[x]` **CLOSED S140 2026-09-01 — history cleaned S129; boat Pi key rotation accepted as deferred to next in-person visit, not blocking closure.**
**Severity:** HIGH
**Platform:** GitHub (SkipperDon/d3kOS public-release branch)

### Symptom
Real Remote Access API key `***REDACTED-S131***` was publicly visible in the `SkipperDon/d3kOS` GitHub repository on the `public-release` branch. Found at 4 locations in `doc/REMOTE_ACCESS_SETUP.md` (lines 24, 44, 101, 106) and persisted in git history across 3+ commits. Additionally, 4 sensitive internal documentation files were present on the public branch.

### Root Cause
The key was pasted directly into a documentation file as a configuration example and committed without any credential-scanning gate. The `public-release` branch had no pre-commit hook to block real keys. The repo was then made public for marketing/transparency purposes with the key still in all historical commits.

### Affected Files / Paths
- `doc/REMOTE_ACCESS_SETUP.md` — key at 4 lines in latest commit AND in git history
- `SESSION_LOG.md` — internal dev journal; full session history exposed on public branch
- `deployment/docs/V09994_BUG_FIXES.md` — complete security vulnerability catalog exposed
- `deployment/docs/ARCH_CREDENTIAL_MAP.md` — system credential map exposed
- `deployment/docs/D3KOS_DEVICE_REGISTRATION_SPEC.md` — internal spec with security detail exposed

### Fix Applied (S129 2026-08-23)
1. Temp clone: `git clone --single-branch --branch public-release /home/boatiq/Helm-OS /tmp/helm-os-clean`
2. `git filter-repo --replace-text <(echo "***REDACTED-S131***==>YOUR_REMOTE_API_KEY_HERE")` — key redacted across all 835 commits
3. Simultaneously removed 4 sensitive files via `--path X --path Y --invert-paths` — reduced public-release history to 789 commits
4. `git fetch /tmp/helm-os-clean public-release:public-release --force` — updated original repo
5. `git push origin public-release --force` — pushed cleaned history to GitHub (operator ran directly)
6. Repo visibility: confirmed PUBLIC via `gh repo view`; `public-release` is default branch

### Verification
- `git log --oneline -S "***REDACTED-S131***" origin/public-release` → 0 results
- `gh repo view SkipperDon/d3kOS --json visibility` → `{"visibility":"PUBLIC"}`
- `git ls-tree public-release SESSION_LOG.md` → object not found (correct — removed)

### Remaining Work
- **Boat Pi key rotation:** `172.20.10.8:/opt/d3kos/config/cloud-config.json` still contains the exposed key. Must be updated on next hotspot visit. New key must be generated and deployed to both the Pi AND the atmyboat.com WordPress `cloud-agent-config` option.
- **Key generation:** new key should be generated via the existing key management mechanism (or manually via `openssl rand -base64 32`).

### Related Bugs
- **BUG-59:** Absence of pre-commit hooks allowed this key to be committed without warning
- **BUG-57:** Ongoing security context — atmyboat.com infrastructure needs holistic hardening

---

## BUG-59 — MEDIUM: No pre-commit credential scanning in d3kOS and atmyboat-forum repos

**Logged:** S129 2026-08-23
**Status:** CLOSED
**Severity:** MEDIUM
**Platform:** Both git repos (d3kOS / Helm-OS and atmyboat-forum)

### Symptom
Neither repository had a `.git/hooks/pre-commit` file. Real API keys could be staged and committed with no warning or block. BUG-58 occurred because of this absence.

### Root Cause
Pre-commit hooks were never installed. The existing `.gitignore` covers config files with raw keys (`api-keys.json`, `cloud-credentials.json`) but does not protect against a key being accidentally pasted into a documentation or code file.

### Fix Applied (S129 2026-08-23)
Pre-commit hook installed at:
- `/home/boatiq/Helm-OS/.git/hooks/pre-commit` (chmod 755)
- `/home/boatiq/atmyboat-forum/.git/hooks/pre-commit` (chmod 755)

Both hooks are identical. They scan every staged file for these patterns:
- `amboat_[a-zA-Z0-9]{20,}` — AMBOAT API key format
- `AIza[0-9A-Za-z_-]{35}` — Google/Gemini API key format
- `sk_live_[a-zA-Z0-9]{20,}` — Stripe live secret key
- `pk_live_[a-zA-Z0-9]{20,}` — Stripe live publishable key
- `sk-ant-api[a-zA-Z0-9_-]{40,}` — Anthropic API key
- `-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY` — Private key material

Allowed-through (whitelisted): `YOUR_[A-Z_]+`, `REDACTED`, `placeholder`, `example`, `[key]`, `...`

Key implementation detail: uses `grep -nEe "$PATTERN"` (not `-nE "$PATTERN"`) — the `-e` flag is required so that patterns beginning with `--` (like `-----BEGIN`) are not parsed as grep option flags.

### Verification
```bash
# Test 1 — real key blocked (example using a dead/rotated key matching amboat_[a-zA-Z0-9]{20,})
echo "amboat_[REDACTED-DEAD-KEY-32CHARS]" > /tmp/test-key.txt
git -C /home/boatiq/Helm-OS add /tmp/test-key.txt && git commit  # → exit 1 ⛔

# Test 2 — placeholder allowed
echo "YOUR_API_KEY_HERE" > /tmp/test-placeholder.txt
git -C /home/boatiq/Helm-OS add /tmp/test-placeholder.txt && git commit  # → exit 0 ✓
```

### Remaining Work / Limitations
- Hooks live in `.git/hooks/` which is NOT tracked by git. If either repo is re-cloned, the hooks will be absent and must be re-installed manually.
- The hooks do not scan binary files or files already in git history — they only protect against NEW commits.
- A `HOOKS_INSTALL.md` or CI-level check would provide more durable protection — deferred to v0.9.9.5.

### Related Bugs
- **BUG-58:** The direct incident this hook prevents from recurring

---

### History — BUG-61 S125 (superseded by REOPENED S126 entry — see below)

**Status (superseded):** `[x]` This was believed FIXED S125 2026-08-21 — fully operational, all assets loading, menu navigation working. **The fix was incomplete — see REOPENED S126 entry for the live status.**

### Symptoms
- `https://atmyboat.com/staging/` returns HTTP 404 "Page not found"
- WordPress is installed and running (PHP responding, REST API available)
- Staging has its own database `atmyb197_wp5888` (separate from production)
- Was working before S122; broke after malware remediation and WordPress restore

### Root Cause
- Staging WordPress database is configured with `siteurl = 'https://atmyboat.com/'` (production URL)
- Should be `siteurl = 'https://atmyboat.com/staging/'`
- When WordPress tries to load `/staging/`, it doesn't recognize the path because it's configured to serve production only
- Likely cause: S122 WordPress restore restored staging database from a backup that was already misconfigured, or the restore process didn't separate staging from production

### Attack Surface
- Staging is inaccessible — cannot test changes before deploying to production
- No isolation between staging and production — both share the same WordPress configuration

### Remediation Plan

**PHASE 1 — UPDATE STAGING DATABASE CONFIGURATION**

The staging database `atmyb197_wp5888` has two settings that need updating:
1. `wp_options.siteurl` → Change from `https://atmyboat.com/` to `https://atmyboat.com/staging/`
2. `wp_options.home` → Change from `https://atmyboat.com/` to `https://atmyboat.com/staging/`

Two options to fix:

**Option A — Via cPanel phpMyAdmin (easiest for you):**
1. Go to cPanel → phpMyAdmin
2. Select database `atmyb197_wp5888`
3. Click the `wp_options` table
4. Find rows with:
   - `option_name = 'siteurl'` → Change `option_value` to `https://atmyboat.com/staging/`
   - `option_name = 'home'` → Change `option_value` to `https://atmyboat.com/staging/`
5. Click "Go" to save
6. Test: `https://atmyboat.com/staging/` should load the WordPress homepage

**Option B — Via WordPress admin (if you can log in):**
1. Log in to `https://atmyboat.com/staging/wp-admin/` (if homepage is fixed)
2. Settings → General
3. Change "WordPress Address (URL)" to `https://atmyboat.com/staging/`
4. Change "Site Address (URL)" to `https://atmyboat.com/staging/`
5. Click Save Changes

### Verification
- Pre-fix: `https://atmyboat.com/staging/` → 404
- Post-fix: `https://atmyboat.com/staging/` → WordPress homepage loads

### Solution Implemented (S125 2026-08-21)

**Step 1 — Database Configuration**
- Identified table prefix: `wpax_` (not `wp_`)
- Updated `wpax_options` table via phpMyAdmin:
  - Row `option_name='siteurl'`: changed value from `https://atmyboat.com/` to `https://atmyboat.com/staging/`
  - Row `option_name='home'`: changed value from `https://atmyboat.com/` to `https://atmyboat.com/staging/`

**Step 2 — Maintenance Mode Removal**
- Deleted `/staging/wp-content/maintenance.php` via FTPS (ftp.atmyboat.com)
- Note: WP Toolkit maintenance files also exist (`maintenance/` directory, `maintenance.php-old`, `maintenance.php-old-old`) but were not interfering

**Verification**
- Pre-fix: HTTP 404 / "Page not found"
- Post-fix: HTTP 200 / WordPress homepage loads
- Page title: "AtMyBoat.com"
- REST API available: `https://atmyboat.com/staging/wp-json/`

### Secondary Issue Found (BUG-61B)

**Problem:** After database URLs fixed, CSS/JS files load with **double "staging"** path
- Example: `https://atmyboat.com/staging/staging/wp-content/themes/twentytwenty/style.css`
- Should be: `https://atmyboat.com/staging/wp-content/themes/twentytwenty/style.css`
- Result: Theme styling missing (CSS 404s), page shows text only

**Root Cause:** Child theme or WordPress is constructing URLs incorrectly for subdirectory installation. The theme's `functions.php` or stylesheet enqueueing is adding "/staging/" to paths that already include it.

**Fix Required:** Edit `/staging/wp-content/themes/twentytwenty-child/functions.php` to filter/correct stylesheet URLs. Alternatively, add filter to child theme's `functions.php`:

```php
add_filter('style_loader_src', function($src) {
    return str_replace('/staging/staging/', '/staging/', $src);
}, 10);

add_filter('script_loader_src', function($src) {
    return str_replace('/staging/staging/', '/staging/', $src);
}, 10);
```

**Status:** Requires code edit on staging child theme. Deferred pending operator decision.

### Notes
- This is NOT a malware issue — it's a configuration issue from the S122 restore
- Staging WordPress database now correctly configured
- Staging homepage and menu links now resolve to correct subdirectory paths
- Theme CSS/JS files require secondary fix (double path in URL construction)
- Staging database (atmyb197_wp5888) remains independent from production (atmyb197_wp59874)

---

## BUG-60 — Spam Comments Posted Automatically (atmyboat.com) — Require Approval Before Publishing

**Status:** `[x]` **FIXED S138 2026-09-01.** Severity **MEDIUM**.

### S138 FIX — 2026-09-01

**Prior state (recorded before changes):**
| Setting | State before fix |
|---|---|
| "Users must be registered and logged in to comment" | **UNCHECKED** |
| "Before a comment appears: Comment must be manually approved" | CHECKED (already set) |
| Moderation queue depth | 17 comments — all approved/posted, 0 pending |

**Fix applied (operator WP Admin → Settings → Discussion → Save Changes):**
- ☑ "Users must be registered and logged in to comment" → **enabled**
- ☑ "Comment must be manually approved" → confirmed enabled (was already set)

**Verification (live, 2026-09-01):**
- T1 PASS — anonymous GET of `/say-hello-to-my-little-buddy/`: `"You must be logged in to post a comment."` — comment form not rendered
- T3 PASS — `name="url"` not present in anonymous page (entire form suppressed, not just the field)
- T4 — pending (7-day spam queue check; no new test needed unless spam reappears)
- T5 — requires a logged-in device-paired user to attempt a comment and confirm it lands in moderation; low risk, deferred

**Note:** The `url` field question (Step 3 from atomic spec) is moot — the form is not rendered at all for anonymous visitors. Logged-in device-paired users can still see the field, but they are operator-approved accounts; this is acceptable.

### S143 UPDATE — 2026-09-04

**Operator revised settings 2026-09-04 (confirmed via WP Admin screenshot):**
- ☐ "Users must be registered and logged in to comment" → **UNCHECKED** (deliberate operator choice)
- ☑ "Comment must be manually approved" → confirmed enabled (unchanged)

**Rationale:** Open commenting (name + email only) with mandatory manual approval. Operator audits every comment before publishing. Acceptable because any registered commenter who is logged in is already a device-gated, operator-approved d3kOS user.

**Final status:** CLOSED. BUG-60 is resolved. Manual approval is the active control.

---

## ⚠ S135 VERIFICATION — 2026-08-28 — read before acting on the plan below

### The attack surface in this entry is wrong: no account is needed

This entry states *"Spammers create free accounts via `/register/` form… Each account immediately gains
ability to post comments."*

**That is not how the spam arrives.** Verified live 2026-08-28 against
`https://atmyboat.com/say-hello-to-my-little-buddy/` as an **anonymous, logged-out** visitor:

| Check | Result |
|---|---|
| `comment-form` rendered to anonymous visitor | **yes** (5 occurrences) |
| posts to `wp-comments-post.php` | **yes** |
| "You must be logged in to post a comment" | **absent** |
| Anti-spam plugin in markup — Akismet / reCAPTCHA / hCaptcha / Turnstile / CleanTalk | **none, zero of five** |
| Fields offered anonymously | `author`, `email`, **`url`**, `submit` |

⚠ **Therefore BUG-63's device gate does NOTHING for this vector.** Registration hardening and comment
spam are independent problems. Anyone can comment without an account, and the **author `url` field —
the exact payload target of link spam — is enabled with no filter in front of it.**

**This matters because it would have been easy to assume BUG-60 was solved by closing registration.
It is not.**

### The "~5 per day since 2026-08-15" claim is not supported by the published record

The comments RSS feed (`/comments/feed/`, 10 items) shows **no published comment later than
17 April 2026** — four months *before* this bug was logged on 2026-08-21.

Two of the ten are unmistakably spam and **were published live**: author `啪啪导航` (16 Apr 2026, 9-char
body) and author `333985` (15 Apr 2026, 22-char body). The remaining eight are genuine
(Skipper Don ×4, Irene ×3, Mark Fedak ×1). No external domains appear in any comment body — only
`atmyboat.com`.

`Uncertainty flag: the feed lists only APPROVED comments, so it cannot distinguish "moderation is now
enabled" from "no spam is arriving" from "the operator deletes spam quickly". What it does establish is
that spam WAS publishing live in April. The August "~5 per day" figure could not be corroborated and
should not be repeated as fact without a look at the moderation queue.`

⚠ **The state of `comment_moderation` could NOT be determined from outside** — it is not visible in
rendered HTML. **Do not record Phase 1 as done or not-done without reading the setting.** BUG-57's
S121 entry recorded a control as effective without checking it; that is the mistake to avoid here.

### Revised remediation — replaces PHASE 1–3 below

**Operator, one visit to `atmyboat.com/wp-admin/` → Settings → Discussion:**

1. ☑ **"Comment must be approved before appearing"** — as originally planned. Still correct.
2. ☑ **"Users must be registered and logged in to comment"** — **this is now the strong control, and it
   was not when this bug was written.** Before BUG-63, requiring login was near-useless because bots
   could self-register. **Now a commenter must hold a server-issued code tied to an
   operator-approved d3kOS device.** The device gate does not protect comments by itself — but it makes
   *this checkbox* into a hard barrier. Free, one click.
3. **Remove or filter the comment author `url` field**, or enable **Akismet**. Approval-before-publishing
   stops spam reaching readers; it does not stop it reaching the operator's queue. With no anti-spam
   layer at all, the queue becomes the new manual-deletion chore this bug was raised about.

⛔ **PHASE 2 below (reCAPTCHA on the registration form) is SUPERSEDED — do not do it.** Registration is
not the vector, and the operator closed CAPTCHA as redundant on 2026-08-28 (see BUG-57 S135). It would
harden a door the spam never uses.

### Verification

- [ ] Read the two Discussion settings and **record their actual state** before changing anything
- [ ] Check the moderation queue depth — that is the only real measure of current spam rate
- [ ] After enabling: submit one test comment logged-out → must be **refused** (login required)
- [ ] Re-check `/comments/feed/` after a week — no new spam authors

### Related

- **BUG-57** — the breach; **independent of this**, despite both involving bots
- **BUG-63** — closes registration; makes remediation step 2 viable, but does not fix this alone

---

### Symptoms *(original S125 record follows — attack-surface section superseded above)*
- ~5 spam comments per day posted to blog articles since 2026-08-15 (BUG-57 remediation)
- Comments contain promotional links and random spam text
- Comments appear live immediately after being submitted
- Operator must manually delete each spam comment
- No approval workflow before comment publication

### Root Cause
- WordPress comment moderation is not enabled
- `/register/` form accepts submissions without bot detection (CAPTCHA or similar)
- No pre-publication review queue for new comments

### Attack Surface
- Spammers create free accounts via `/register/` form (no CAPTCHA blocks automated submission)
- Each account immediately gains ability to post comments
- Comments appear live on blog without operator review — reduces site credibility, pollutes SEO

### Remediation Plan

**PHASE 1 — COMMENT APPROVAL QUEUE (Immediate, WP native)**
1. Log in to WordPress admin (`atmyboat.com/wp-admin/`)
2. Settings → Discussion
3. Check: **"Comment must be approved before appearing"**
4. Recommended: Also check **"Users must be registered and logged in to comment"** (blocks anonymous spam)
5. Save changes
6. Test: Submit a test comment from a new account → verify it appears in Moderation queue, not live

**PHASE 2 — REGISTRATION PROTECTION (Reduce account creation by bots)**
Option A (easiest): **reCAPTCHA v3 on registration form**
- Install plugin: Search plugins for "reCAPTCHA" (look for official Google or Wordfence versions)
- Get free reCAPTCHA keys from `console.cloud.google.com` (Google Cloud free tier)
- Enable on `/register/` form only
- reCAPTCHA v3 is silent (no "I'm not a robot" checkbox) — analyzes behaviour instead

Option B (if plugin unavailable): **WordPress native CAPTCHA plugin**
- Search: "Simple CAPTCHA" or "Really Simple CAPTCHA"
- Enable on registration form
- Shows math puzzle or image puzzle — blocks automated account creation

**PHASE 3 — MONITOR & TUNE (After Phase 1 deployed)**
- Check WordPress Moderation queue daily for 1 week
- Adjust spam filter settings if needed (Settings → Discussion → Akismet, if enabled)
- Count legitimate vs spam comments to validate effectiveness

### Files to Modify
- WordPress admin panel (no file edits) — all changes via GUI

### Verification
- Pre-Phase 1: Submit test comment → appears live immediately
- Post-Phase 1: Submit test comment → appears in Moderation queue, not live
- Post-Phase 2: Create new test account via `/register/` → form must show CAPTCHA

### Severity & Impact
- **Moderate:** Spam damages site credibility but doesn't expose user data or system access
- **Recurring:** ~5 comments/day = ~35/week, ~150/month if unchecked
- **Cost:** Operator manual review time; no financial loss

### Notes
- BUG-57 (malware) is remediated; this bug is a secondary attack vector using the free registration to spam content
- Same root cause class as BUG-57 (open registration), different attack pattern (comment spam vs account creation)
- Recommend deferring account deletion policy decision to next session (allow spam accounts to exist harmless in DB, or delete them?)
   - Add note: "Replace with your actual key from `/opt/d3kos/config/api-keys.json` on the Pi"
   - Never include real keys in README, examples, or tutorials

5. **Environment-based Configuration**
   - Move sensitive config to environment variables (`.env`, `cloud-config.json`)
   - Add these files to `.gitignore`
   - Document setup: "Copy `.env.template` to `.env`, fill in your keys"

6. **Key Rotation Policy**
   - Rotate keys annually (scheduled)
   - Rotate immediately on any breach or suspected compromise
   - Maintain audit log of key changes (timestamp, reason, old/new key hash)
   - Communicate rotation to all users (PIN, email)

7. **API Key Versioning**
   - Support multiple active keys (new key + old key for 7 days during rotation)
   - Allow users to revoke old keys manually
   - Track which client app/device is using which key

### Files Affected
| File | Action | Status |
|------|--------|--------|
| `.git/hooks/pre-commit` | Create secret scanning hook | Pending |
| `doc/REMOTE_ACCESS_SETUP.md` | Replace real key with placeholder | Pending |
| `deployment/docs/INSTALLATION.md` | Add key regeneration steps | Pending |
| `install-d3kos.sh` | Generate unique key per device | Pending |
| `.env.template` | Create secure config template | Pending |
| `.gitignore` | Add `.env`, config files | Pending |

### Testing

**Unit Tests:**
- `test_key_generation.py` — verify key uniqueness and format
- `test_pre_commit_hook.sh` — attempt to commit mock API keys, verify rejection
- `test_key_rotation.py` — rotate key, verify old key rejected, new key accepted

**Integration Tests:**
- Both Pis boot with new keys
- Remote Access API works with new keys
- Old key returns 401 on both Pis
- New clients can authenticate with new keys

### Prevention Going Forward

1. **Code Review Rule:** Reviewers check for any hardcoded credentials before merge
2. **CI/CD Gate:** Secrets scanning runs on every PR; fails if credentials detected
3. **Team Training:** All developers briefed on placeholder usage in docs/examples
4. **Security Policy:** Document in CLAUDE.md or governance files
5. **Audit:** Monthly scan of repos and deployment configs for leaked secrets


---

## BUG-61 — Staging WordPress Misconfigured — Double Path Issue (REOPENED S126)

**Status:** `[x]` **RESOLVED S137 2026-08-31 — eliminated by BUG-85 .htaccess fix. Live probe 2026-09-01: staging/about/ → 200, assets load correctly with no /staging/staging/ doubling. See BUG-85 for full verification record.**
⚠ **S131 probe (2026-08-24):** `https://atmyboat.com/staging/wp-admin/` returned HTTP `000` — no response at all, not a 404. This is a **different condition** from the double-path defect BUG-61 describes. Staging may be entirely down, not merely misconfigured. Do not assume the same root cause.

### Symptoms (Reconfirmed)
- `https://atmyboat.com/staging/` returns 404 or loads without CSS/JS/images
- `https://atmyboat.com/staging/wp-admin/` returns 404
- All asset URLs have double `/staging/staging/` path:
  - Example: `https://atmyboat.com/staging/staging/wp-content/themes/twentytwenty/style.css`
  - Should be: `https://atmyboat.com/staging/wp-content/themes/twentytwenty/style.css`

### Root Cause
**S125 action was incomplete.** The database `siteurl`/`home` were corrected, but the **CSS/JS URL rewriting** was identified as "BUG-61B" and deferred. The PHP filters were written but never applied to the child theme's `functions.php`.

### Required Fix
Apply the PHP URL correction filters from the S125 record (lines 4052–4059 of this document) to `/staging/wp-content/themes/twentytwenty-child/functions.php`:

```php
add_filter('style_loader_src', function($src) {
    return str_replace('/staging/staging/', '/staging/', $src);
}, 10);

add_filter('script_loader_src', function($src) {
    return str_replace('/staging/staging/', '/staging/', $src);
}, 10);
```

Then verify: `https://atmyboat.com/staging/` loads with full CSS/JS/images, and `https://atmyboat.com/staging/wp-admin/` is accessible (if authorized).

---

## BUG-62 — wp-admin Directory Exposed Without Authentication

**Status:** `[x]` **CLOSED — NOT A BUG — S131 2026-08-24. Confirmed a MISDIAGNOSIS by live probe, using the exact test this entry itself prescribed.** | Prior: `[!]` RE-VERIFICATION REQUIRED S127 | Prior: `[!]` LOGGED S126 as CRITICAL

### CLOSURE EVIDENCE — S131 2026-08-24 (live HTTP probe, production)

The S127 note said: *"Test the real paths (`/wp-admin/`, `/staging/wp-admin/`, `/wp-admin/includes/`) → if they redirect to `wp-login.php` / return 403, close as NOT A BUG."* That test was run:

```
GET /wp-admin/            -> 302  Location: /wp-login.php?redirect_to=%2Fwp-admin%2F&reauth=1
GET /wp-admin/includes/   -> 403
GET /staging/staging/wp-admin/ -> 404   (BUG-61's known-broken double-path URL)
GET /staging/wp-admin/    -> 000   (no response; staging separately unreachable)
```

**The authentication guard works.** `/wp-admin/` forces re-authentication; the includes directory is hard-403. The original CRITICAL was logged from `/staging/staging/wp-admin/` — the double-`/staging/` path that BUG-61 records as broken — and a 404 from a wrong URL is not an exposed directory. Enumeration, brute-force and version-detection were all *inferred* from that single 404; none was ever observed.

**Lesson recorded:** a severity rating derived from one unverified observation cost three sessions of CRITICAL-priority attention. The S127 instinct to flag it for re-verification rather than act on it was correct.

⚠ **Not closed by this:** BUG-61 (the double-path defect that produced the false signal) remains REOPENED, and `/staging/wp-admin/` returning no response at all is unexplained — noted under BUG-61, not here.
**⚠ RE-VERIFICATION REQUIRED — S127 2026-08-22. This may be a MISDIAGNOSIS. Do not act on it until confirmed by a live read.**

### ⚠ S127 Review Note — the evidence does not support the conclusion

The finding was logged from `https://atmyboat.com/staging/staging/wp-admin/` — which is
the **known-broken double-`/staging/` path from BUG-61**. That URL returns 404 because the
path is wrong, not because a directory is unprotected. **A 404 from a broken URL is not an
exposed admin directory**, and the symptom list below then infers enumeration, brute force
and version detection from that single 404 without any of them being observed.

Nothing here was verified against a live authenticated read. This is the same failure mode
the standing rule in CLAUDE.md Step 8 was written for: *"Before changing any label, verify
against the CODE, not the paperwork."*

**To resolve, test the REAL paths (operator, in a browser):**
1. `https://atmyboat.com/wp-admin/` → must redirect to `wp-login.php` when logged out
2. `https://atmyboat.com/staging/wp-admin/` (single `staging`) → same expectation
3. `https://atmyboat.com/wp-admin/includes/` → expect 403 or 404, never a file listing

If all three behave correctly, **close this as NOT A BUG**. WordPress guards `/wp-admin/`
by default; an unguarded one would be the exception, not the assumption. If any returns a
directory listing or an unauthenticated admin page, the bug is real and CRITICAL stands.

Note the operator *was* able to log into wp-admin normally in S127, which is consistent
with the guard being present and working.

### Symptoms (as logged S126 — unverified, see review note above)
- `https://atmyboat.com/staging/staging/wp-admin/` returns 404 (due to BUG-61 path doubling), but the directory structure exists and is reachable
- wp-admin directory lacks authentication guard — an attacker can:
  - Enumerate directory contents (`/plugins/`, `/themes/`, `/includes/`)
  - Brute-force login credentials without rate limiting
  - Exploit WordPress vulnerabilities without a valid session
  - Detect WordPress version and installed plugins

### Root Cause
WordPress staging environment has no `.htaccess` rule or authentication middleware blocking direct access to `/wp-admin/` directory. The directory should either:
1. Require login before serving any files
2. Be IP-whitelisted (admin IPs only)
3. Have rate limiting on login attempts

### Required Fix
**Option 1 — .htaccess file in `/staging/wp-admin/`:**
```apache
<Files ~ "\.php$">
    Order deny,allow
    Deny from all
    Allow from <YOUR_ADMIN_IP>
</Files>
```

**Option 2 — WordPress Security Plugin:**
- Install "Wordfence Security" or "iThemes Security"
- Configure to block wp-admin access except from whitelisted IPs or after successful login

**Option 3 — Cloudflare WAF Rule:**
- Block requests to `/staging/wp-admin/` except from your IP
- Rate limit login attempts to 5/minute

### Verification
- Pre-fix: `curl -I https://atmyboat.com/staging/wp-admin/` returns 404 but directory is listable
- Post-fix: Unauthenticated request returns 403 or redirects to login

---

## BUG-63 — Insecure User Registration Allows Unlimited Bot Account Creation

**Status:** `[x]` **FIXED + DEPLOYED LIVE S134-cont 2026-08-25**

### BUG-63 Fix Progress — S134-cont 2026-08-25

**Phase 1 — Code gate (COMPLETE — commit d9915753):**
- `device-registration.php`: `amboat_claim_registration_code()` atomic (SELECT FOR UPDATE + UPDATE WHERE status='valid' AND affected_rows=1); `amboat_rollback_registration_code()` T17; `amboat_registration_audit()`.
- `page-register.php`: `require_once device-registration.php` before POST block; code_input required field; alias replaces email-derived username (display_name + nickname = public alias; atmyboat_legal_name = private user_meta); claim-then-create order (T16 regression test); rollback on wp_create_user failure (T17).
- `verify-bug63.sh`: 11 tests — 11/11 PASS.

**Phase 2 — HTML form updated (S134-cont):**
- `page-register.php`: Added `alias` (display name) and `code_input` (d3kOS registration code) input fields to the HTML form — these were present in the PHP processing logic but missing from the rendered form.

**Phase 3 — Step 3 — Bulk cleanup + republish (COMPLETE — operator APPROVED S134-cont):**
- Botnet account cleanup: 0 remaining unverified accounts matching attack criteria (operator manually cleared 62k accounts prior; /register/ was in Draft since Aug 2026).
- `/register/` page (ID=339): status Draft → published.
- Deployment verified: curl confirms `alias` and `code_input` fields live at https://atmyboat.com/register/.
- All one-shot scripts deleted from server.

**Registration is now device-gated:** every new account requires a server-issued code from an operator-approved d3kOS device. Bots cannot register without one.

### Symptoms
- Bot accounts created daily with nonsense usernames: `user12345`, `testbot`, `spamuser999`, `user_xxx_123`, etc.
- No real-name validation — registration allows any username string
- No email domain verification — attackers can use disposable email addresses
- MailPoet plugin likely compromised — bots gain immediate access to newsletter subscriber lists
- Spam campaigns sent to real users within hours of account creation
- REST API `/wp-json/wp/v2/users/` accepts POST (returns 401, but form submission succeeds)

### Attack Pattern
1. Attacker writes script to bulk-submit `/register/` form with random usernames
2. Each account automatically gains `Subscriber` role (default WordPress behavior)
3. Subscriber role can access MailPoet, view subscriber lists, create campaigns
4. Spam emails sent to site's entire mailing list within minutes

### ✅ ROOT CAUSE CONFIRMED IN CODE — S127 2026-08-22

**File:** `deployment/features/auth-pages/php/page-register.php` (502 lines)

`/register/` is a **custom WordPress page template that calls `wp_create_user()` directly
at line 88.** It does not use WordPress's registration system at all.

**Consequence — the obvious fix would not have worked:** unticking
**Settings → General → "Anyone can register"** (`users_can_register`) has **no effect on
this form**, because the form never consults that setting. Anyone who "disabled
registration" in wp-admin and moved on would have left the hole fully open while believing
it closed. This is the single most important fact in this entry.

**What the form has:** a nonce — `wp_verify_nonce(...,'atmyboat_register_action')` at
line 55.
**What the nonce is worth against this attack: nothing.** It stops cross-site posting. It
does not stop a bot that GETs `/register/` first, scrapes the nonce out of the HTML, and
posts it back. That is three lines of script.

**What the form does NOT have** (grep-confirmed, S127): no CAPTCHA, no honeypot, no rate
limit, no username format check, no email-domain check.

**Why the accounts pile up despite email verification:** line 104 sets
`atmyboat_email_verified = '0'` and line 108 issues a verify token, and per the project's
auth pattern that meta key gates **login**. So the ~62k bot accounts (BUG-57) are almost
certainly unverified shells that cannot log in — **but `wp_create_user()` has already run,
so the row exists in `wp_users` regardless.** Verification gates login; it does not gate
account creation. That user table is what MailPoet reads to build its audience, which is
the link from BUG-57 to BUG-60 and to the spam campaigns in this bug.

Line 102 sets `atmyboat_tier = 'T0'` on every new account.

**Interim containment applied S127 (operator):** `/register/` page set to **Draft**, so the
template never renders and the POST handler never executes; `users_can_register` unticked
(closes the second door at `/wp-login.php?action=register`); comment moderation enabled
(BUG-60 Phase 1). ⚠ Draft status is a stopgap, not a fix — the vulnerable template is still
on disk and one status change away from live.

**Permanent fix:** replace this template per
`deployment/docs/D3KOS_DEVICE_REGISTRATION_SPEC.md` v2.0.0 — registration requires a
server-issued code from an operator-approved d3kOS device. **Do not re-publish
`/register/` until that form ships.**

### Root Causes
0. **CONFIRMED — `page-register.php:88` calls `wp_create_user()` directly**, bypassing
   `users_can_register` entirely. See the block above. The six items below are contributing
   weaknesses in that same form.
1. **No username format validation** — accepts `user123`, `testbot`, `xxx_yyy_zzz` (should require name-like format)
2. **No email domain whitelist** — accepts any domain including temporary email services
3. **No real-name field** — registration does not require first/last name
4. **MailPoet API not secured** — subscriber API accessible to any registered user; should require admin role
5. **No CAPTCHA on form** — automated submission undetected
6. **No rate limiting** — bulk account creation not throttled

### Operator Requirement
> "only permit human with real names to be added to the system"

### Required Fixes

**Phase 1 — Immediate (blocks 90% of bots):**
1. Add reCAPTCHA v3 to `/register/` form (silent, invisible to humans)
   - Install plugin: "Google reCAPTCHA by Wordfence" or "reCaptcha WP"
   - Get free keys from `console.cloud.google.com`
   - Enable on registration form only
   
2. Enable comment moderation (BUG-60 related):
   - WP Admin → Settings → Discussion → Check "Comment must be approved before appearing"

**Phase 2 — Strengthen username validation (blocks remaining bots):**
1. Add "Real Name" fields to registration form (first + last name required)
2. Add regex validation: username must be alphanumeric + underscore only, 5+ chars, must start with letter
3. Reject usernames matching pattern: `user\d+`, `test\w+`, `spam`, `bot`, `admin`, etc.
   - Use plugin: "Advanced Custom Fields" or code custom validator in child theme

**Phase 3 — MailPoet API security:**
1. Restrict MailPoet access to Admin role only (not Subscriber)
   - MailPoet → Settings → Permissions → Require "Manage MailPoet" capability for Subscribers = OFF
2. Rotate MailPoet API key
   - MailPoet → Settings → API → Generate new API key
   - Remove old key from all integrations

**Phase 4 — Rate limiting + audit logging:**
1. Install "Brute Force Protection" or "Wordfence" plugin
2. Limit registration to 5 accounts per IP per hour
3. Log all user creation events to a separate audit table
4. Alert operator when bulk account creation detected (>3 accounts from same IP in 10 minutes)

### Files to Modify (if coding, not plugin-based)
- `/register/` form (add real-name fields, username validation)
- MailPoet settings (restrict access to admin role)
- `.htaccess` or PHP middleware (rate limiting)
- Database audit trigger (log user creation events)

### Verification
- Pre-fix: Create account with username `user12345` and fake email → succeeds
- Post-Phase 1: Same attempt blocked by reCAPTCHA
- Post-Phase 2: Username `user12345` rejected; requires format like `john_doe`
- Post-Phase 3: Subscriber account cannot access MailPoet API

### Severity & Impact
- **CRITICAL:** Active ongoing attack, 62k+ accounts created (BUG-57), spam campaigns sent daily (BUG-60)
- **Blast radius:** Entire mailing list compromised; site credibility damaged; potential account takeover
- **Prevention value:** Blocks 95% of bot attacks; requires legitimate human signup effort

### Related Bugs
- **BUG-57:** 62,000+ unauthorized accounts created (initial attack vector, manually remediated)
- **BUG-60:** Spam comments posted via created accounts (secondary attack payload)
- **BUG-62:** wp-admin exposed without auth (tertiary attack surface)

---

## BUG-64 — My Account Page Lacks Security Controls

**Status:** `[x]` **CLOSED — NOT A BUG. S135 2026-08-28, operator decision, after a full source audit of
the LIVE file.** Was: `[!]` LOGGED S126 HIGH — potential privilege escalation and data exposure.
**Two minor hardening gaps found and split out to BUG-87. Neither is a vulnerability.**

---

## ⚠ S135 AUDIT — 2026-08-28 — every question below is answered; do not re-investigate

**What was audited:** the **deployed** file, not a repo copy.
`wp-content/themes/twentytwenty-child/page-my-account.php`, 23,345 B, md5 `400fa44e…`, 556 lines,
pulled over FTPS 2026-08-28.

⚠ **Three variants of this file exist. The live one matches `Helm-OS/deployment/features/auth-pages/php/`
(md5 `400fa44e…`); the `atmyboat-forum` working copy (md5 `a89e7176…`) is STALE.** Audit the Helm-OS
copy or the live file — not the forum repo. (`concepts/two-source-sync-rule` violated again.)

### Answers to the seven questions in "Attack Surface (To Investigate)"

| # | Question | Verdict | Evidence |
|---|---|---|---|
| 1 | Can any logged-in user access another user's account page? | **NO** | `:23` `if ( ! is_user_logged_in() )` gate; `:34` `$current_user = wp_get_current_user()`; `:35` `$user_id = $current_user->ID`. **No user identifier is read from any request** — the only `$_POST` reads are `account_action` and the nonce. **No IDOR is possible.** |
| 2 | Can a Subscriber escalate to Admin by editing their role? | **NO** | Zero occurrences of `set_role`, `add_cap`, `add_role`, or any `role` field. The one `wp_update_user` call (`:120`) writes `[ 'ID' => $user_id, 'user_email' => $new_email ]` and nothing else. **There is no role field to tamper with.** |
| 3 | Are email changes verified? | **YES** | `:120` updates the address, then `:125` sets `atmyboat_email_verified = '0'` and `:127` stores a 40-char token. That flag **gates login**, so an unverified change locks the account rather than silently taking effect. |
| 4 | Are password changes rate-limited / confirmed? | **Confirmed, not throttled** | `:92` `wp_check_password( $pw_cur, … )` **before** `:99` `wp_set_password()`; min 8 chars (`:95`); confirm-match (`:97`). `:100` comments the auth-cookie invalidation deliberately. **Throttling absent → BUG-87 R1.** |
| 5 | Is 2FA available/required? | **Out of scope for this file** | Admin 2FA is Wordfence Login Security — BUG-69 Step 1, done S128. |
| 6 | Can user data be exported/changed without verification? | **NO** | Export (`:41`) is GET-triggered but nonce-checked at `:43` against `'amboat_export_' . $user_id` — **user-scoped**, so one user's export nonce cannot fetch another's data. |
| 7 | Are admin-only pages protected from direct URL access? | **Not applicable here** | This file exposes no admin surface. |

### Additional checks performed beyond the original list

- **Direct SQL / injection:** **none.** Zero `$wpdb` references in the file.
- **CSRF:** protected, and carefully. `:84` verifies the nonce against `'amboat_acct_' . $act` —
  **action-scoped**, so a nonce minted for one action cannot be replayed against another. Only three
  actions exist: `change_password` (`:86`), `change_email` (`:109`), `delete_account` (`:149`).
- **Account deletion:** `:152` requires the literal string `DELETE MY ACCOUNT`; `:157`
  `wp_delete_user( $user_id, 1 )` **reassigns content to the admin rather than destroying posts**;
  then `wp_logout()` and a PRG redirect.

### Why this is closed

Every escalation and access-control question raised in S126 is answered in the negative by the code.
The entry was a list of things to check — reasonable to raise, and all the load-bearing ones hold.
**The page is better built than the entry assumed.**

⚠ **The S126 severity (HIGH, "potential privilege escalation") was assigned without reading the file.**
That is the same pattern as BUG-57's phantom containment and BUG-81's fabricated hardware model:
*a claim recorded before the source was read.* Cost here was low; the habit is what matters.

**Residual, split out — see BUG-87:** no throttling on the account actions (R1), and account deletion
does not re-prompt for the password (R2). Both are hardening. Neither is exploitable by an
unauthenticated party.

---

### Symptoms *(original S126 record follows — superseded by the audit above)*
- `/my-account/` page accessible without proper access controls
- Unclear what security protections exist on this page
- Potential for: unauthorized account access, privilege escalation, data exposure, email/password changes by unauthorized users

### Attack Surface (To Investigate)
1. Can any logged-in user access another user's account page?
2. Can a Subscriber user escalate to Admin by editing their role?
3. Are email changes rate-limited or verified?
4. Are password changes rate-limited?
5. Is 2FA (two-factor authentication) available or required?
6. Can user data (email, profile, preferences) be exported or changed without verification?
7. Are admin-only pages protected from direct URL access?

### Required Investigation
1. Test unauthorized access: log in as Subscriber, attempt to access `/my-account/user=admin`
2. Test privilege escalation: attempt to change role from Subscriber to Admin
3. Test email change: change email without verification
4. Test password change: change password without current-password confirmation
5. Test rate limiting: spam password reset requests, verify throttling
6. Review `/my-account/` source code in child theme for direct SQL queries or unsafe operations

### Required Fixes (Likely)
1. **Access control:** Only allow users to view/edit their own account; add `if ($user_id != get_current_user_id()) wp_die('Unauthorized');`
2. **Privilege escalation:** Remove or restrict role/capability fields from user edit form; prevent Subscribers from changing roles
3. **Email verification:** Require email confirmation before accepting email changes
4. **Password confirmation:** Require current password before allowing password change
5. **Rate limiting:** Limit password reset requests to 3 per hour per user; limit failed login attempts
6. **2FA option:** Install "Two Factor Authentication" plugin for additional security
7. **Code audit:** Review for SQL injection, privilege escalation, CSRF, XSS in user profile form

### Files to Review
- `/wp-content/themes/twentytwenty-child/templates/my-account.php` (if exists)
- `/wp-content/themes/twentytwenty/template-parts/` (if using parent theme)
- WP core: `/wp-admin/user-edit.php` (if linked to WP native form)
- Any custom PHP in `/wp-content/` handling user profile updates

### Severity & Impact
- **HIGH:** Could allow account takeover, privilege escalation, data theft
- **Ongoing risk:** Every registered user (including bots from BUG-63) has potential to exploit this page

---

## BUG-65 — `license.json` is unsigned and world-readable: any user can self-elevate to Tier 3

**Status:** `[~]` **STEPS 1+2 DONE S134-cont 2026-08-25 — 14/14 PASS. Step 3 (tier mismatch audit) DEPLOYED S140 2026-09-01 — live data-ingress.php confirmed: `tier_claimed` read from Pi body, mismatches logged to `amboat_registration_audit`, feature flags returned from server-side `$tier` (not Pi-claimed value). BUG-91 fixed fail-open default: T0 row added to feature_matrix, default changed `'T1'` → `'T0'`. ⚠ REMAINING: Finding 3 — 7 Pi features absent from server matrix (`camera`, `cloud_sync`, `engine_monitoring`, `maintenance_schedule`, `mobile_app`, `predictive_alerts`, `voice_assistant`) — feature matrix alignment deferred to v0.9.9.5.**

**Step 1 — `first-boot-setup.sh` promoted to canonical tree:**
- Canonical path: `deployment/v0.9.9.4/opt/d3kos/scripts/first-boot-setup.sh`
- Fallback branch (lines 148-149): `chown d3kos:d3kos /opt/d3kos/config/license.json` + `chmod 600 /opt/d3kos/config/license.json`
- STEP 6 re-asserts `chmod 600` after `chown -R` (guards against future regressions)
- sanitize.sh: confirmed `chmod 600` already present (BUG-78 T8/T9)
- T3 trap (naive chmod 600 → root:root 600 → d3kos cannot read): guarded by explicit `chown d3kos:d3kos` before mode change (T6 PASS)

**Step 2 — Tier audit fields in `export_worker.py`:**
- `_build_ingress_payload()` now appends: `tier_claimed` (from license.json), `tier_detected` (opencpn+subscription.key filesystem test), `opencpn_present` (bool), `subscription_key_present` (bool)
- Handles both int 3 and string "T3" tier forms (reuses _parse_tier logic inline)
- Server receives the claim + the detected value every export — mismatch is visible for human review
- **No auto-downgrade path** — flag for human review only; false positive at sea strips paid features

**Verifier:** `deployment/v0.9.9.4/tools/verify-bug65.sh` — 14/14 PASS
**Commit:** pending (this session)

**FORMERLY: LOGGED S127 2026-08-22. HIGH severity — licensing bypass. Found during the BUG-63 registration-architecture review, not by a user report.**

### Symptom
Editing one line of a plain text file on the Pi grants every paid feature:

```
sudo nano /opt/d3kos/config/license.json
# change  "tier": 0   ->   "tier": 3
```

Tier 2 (voice assistant, camera, AI analysis, predictive maintenance) and Tier 3 (unlimited
resets, fleet management, multi-boat) all unlock. Nothing detects it and nothing reverses it.

### Root Cause
Three compounding facts, all verified in code S127:

1. **The file is unsigned and mode 644.** Created at `opt/d3kos/scripts/first-boot-setup.sh:128-147`.
   No signature, no HMAC, no checksum — nothing binds the contents to anything.
2. **Tier is read and trusted verbatim.** `tier_service.py:21,29,128-160` reads `license.json`
   and returns the FEATURE_MATRIX gate directly. `app.py:412-417` and `:479-480` do the same,
   equally unguarded.
3. **Tier is only ever pushed DOWN from the server, never verified UP.** `export_worker.py:204-218`
   (`_sync_tier_from_response`) writes whatever the server returned into `license.json`, and
   `cloud_agent.py:292-300` / `:405-425` do likewise. There is no path where the Pi asks
   "is my claimed tier real?" and no path where the server checks what the Pi claims.

This is architecturally intended, not an oversight — MASTER_SYSTEM_SPEC §9.2 (L6429-6435)
states: *"No Phone-Home: All tier detection is local (no cloud checks) … No license key
validation servers."* Tier detection is a **local filesystem test** (L3298-3311): if
`/opt/opencpn` exists → Tier 2. Creating an empty directory is enough.

⚠ **§9.2 is itself now stale and contradicts the rest of the spec** — §8.3 central database
sync, telemetry export category #9, fleet management and `version-heartbeat.php` all phone
home continuously today. That contradiction should be resolved in MASTER_SYSTEM_SPEC
independently of this bug.

### Impact
- **Revenue:** Tier 2 is $9.99/month and Tier 3 $99.99/year (MASTER_SYSTEM_SPEC §6.3.4). Both are bypassed by a text edit.
- **Low exploit skill:** no tooling, no network, no reverse engineering. One file, one number.
- **Not remotely detectable today:** the server accepts the tier the Pi reports.
- **Does NOT affect forum registration.** The registration design in `D3KOS_DEVICE_REGISTRATION_SPEC.md` v2.0.0 gates on **operator approval**, not on tier, specifically because tier is not trustworthy. Recorded there in §5 as a known out-of-scope item.

### Fix Options (not yet chosen — needs an operator decision)
1. **Server-signed licence.** Server issues `license.json` signed with a private key; the Pi verifies with an embedded public key. Strongest, but requires the licence server that §9.2 explicitly rules out — so it is a **policy change**, not just an implementation.
2. **Server-side enforcement of paid features only.** Leave the local file alone; make the server refuse Tier 2/3 *cloud* operations unless its own record says the device is entitled. Cheaper, and it protects the features that actually cost money. Local-only features stay spoofable.
3. **Accept the risk, document it.** Consistent with the open-source posture of §9.2. Legitimate if the paid value is in the cloud services rather than the on-device code.

**Recommendation: option 2.** It closes the commercial exposure without contradicting the
offline-first design principle, and the server-side device registry needed for it is the
same one BUG-66 and the registration spec both require.

### Verification
- [ ] Reproduce: edit `tier` to 3 on the lab Pi, restart `tier_service`, confirm T3 features unlock
- [ ] Confirm the server accepts a fabricated tier in the next export/heartbeat
- [ ] After fix: fabricated tier must not unlock server-side Tier 2/3 operations

### Files
`opt/d3kos/scripts/first-boot-setup.sh:128-147` · `tier_service.py:21,29,128-160` ·
`app.py:412-417,479-480` · `export_worker.py:204-218` · `cloud_agent.py:292-300,405-425` ·
`doc/MASTER_SYSTEM_SPEC.md` §6.3.1 L3295-3311, §9.2 L6411-6435

---

## BUG-66 — One fleet-wide API key in cleartext on every Pi authenticates all 12 server endpoints

> ### ⚠ S135 2026-08-28 — PHASE C COVERAGE CORRECTION (read before trusting "6 endpoints migrated")
>
> Phase C's record states *"6 Pi→Server endpoints migrated to Ed25519"*. Verified against the production
> FTP listing on 2026-08-28: **three of the six are not deployed.**
>
> | Endpoint | In production? | Edited file lives in |
> |---|---|---|
> | `version-heartbeat.php` | ✅ yes — **verified live, returns 401** | `features/autonomous-agents/php/` |
> | `failure-report.php` | ✅ yes | `features/autonomous-agents/php/` |
> | `config-backup.php` | ✅ yes | `features/fi4-config-backup/php/` |
> | `fix-confirmed.php` | ❌ **no** | `features/autonomous-agents/php/` |
> | `community-markers-write.php` | ❌ **no** | `features/v0941-plan/php/` — a **DESIGN tree** |
> | `community-position.php` | ❌ **no** | `features/v0941-plan/php/` — a **DESIGN tree** |
>
> **This is not a live exposure** — an undeployed file cannot be attacked, and hardening it early is not
> wrong. It is a **coverage claim that overstates reality**: half the migration hardened files nobody
> serves. **Do not read "6 migrated" as "6 live".**
>
> ⚠ **Root of the trap: `deployment/features/v0941-plan/php/` is a DESIGN tree, not a deployment
> source.** It contains `page-community-ORIGINAL.php` and `page-dashboard-ORIGINAL.php` mockup variants
> beside the PHP. Nothing in it is deployed. Check where a file lives before counting it as shipped.
>
> **Open question carried from BUG-86:** is the `d3kos-device-auth` plugin currently ACTIVE on staging,
> or was it deactivated to stop the 2026-08-25 fatal? Needs `active_plugins` from `atmyb197_wp5888`.
> Found via BUG-76. Full detail: `V09994_BUG_FIXES.md` BUG-76.


**Status:** `[x]` **FULLY RESOLVED S140 2026-09-01 — LAB PI ENROLLED + VERIFIED. Phases A+B+C+D complete. Plugin active on live HostPapa. Lab Pi (`701e5754`) enrolled: keypair generated, POST /wp-json/amboat-device/v1/enrol → HTTP 200 `{"status":"pending"}`, operator approved via wp-admin, GET /amboat-device/v1/status → HTTP 200 `{"status":"approved"}`. Ed25519 auth chain verified end-to-end. Boat Pi enrolment deferred — requires on-boat access. Legacy AMBOAT_API_KEY fallback retained with audit logging until all Pi fleet enrolled.**

### PHASE A — S134 2026-08-25 — SERVER-SIDE (COMPLETE, AWAITING HOSTPAPA STAGING DEPLOY)

Files created at `deployment/v0.9.9.4-server/`:
- A1: `sql/device-auth-tables.sql` — 4 tables verbatim from registration spec §6
- A2: `mobile/device-auth.php` — shared Ed25519 verifier. verify_device_signature() + verify_device_request(). SELECT only — no INSERT/UPSERT. Unknown device_token → 401, never self-registers. WordPress transient nonce cache 600s.
- A3: `mobile/enrol.php`, `mobile/status.php`, `mobile/request-code.php` — REST endpoints at /wp-json/amboat-device/v1/{enrol,status,request-code}
- A4: `plugins/d3kos-device-auth/d3kos-device-auth.php` — WordPress plugin, REST registration, dbDelta schema creation, wp-admin approval queue
- TDD: `tools/verify-bug66-phase-a.sh` — 12/12 PASS (T3 = no INSERT in auth path; T8 = no UPSERT in enrol)
- Commit: 2f3dd7ea

**⚠ Deploy order: server before Pi. Awaiting operator APPROVED for HostPapa staging.**

### PHASE B COMPLETE — S134-cont 2026-08-25

**Status:** Pi-side Ed25519 keypair generation and signing helper.

#### Deliverables
- B1: `identity/regenerate-identity.sh` — step 4 added: generates `device-signing.key` (32 bytes raw Ed25519, mode 0600, set at `os.open` time) and `device-signing.pub` (32 bytes, 0644). SIGNING_KEY_FAILED flag gates the sentinel alongside SSH_REGEN_FAILED. Private key bytes never appear in log output (length extracted before print).
- B2: `services/device_sign.py` — `sign_device_request(path)` returns `{X-Device-Token, X-Timestamp, X-Nonce, X-Signature}`. `get_public_key_b64()` for the /enrol call. FileNotFoundError propagates — not swallowed. Importable by cloud_agent.py, export_worker.py, fleet_push_service.py via existing `sys.path`.
- TDD: `tools/verify-bug66-phase-b.sh` — 10/10 PASS (T3 = sentinel blocked on SIGNING_KEY_FAILED; T8 = FileNotFoundError not swallowed; T10 = raw key bytes not logged)
- Commit: e14fb26d

**⚠ Deploy order: server before Pi. Phase A still awaiting operator APPROVED for HostPapa staging.**

### PHASE C COMPLETE — S134-cont 2026-08-25

**6 Pi→Server endpoints migrated** (hash_equals(AMBOAT_API_KEY) → verify_device_request()):
version-heartbeat.php, failure-report.php, fix-confirmed.php, community-markers-write.php (Pi path),
community-position.php, config-backup.php. verify_device_request_server() added to device-auth.php
(plain PHP, reads $_SERVER); verify_device_request() accepts nullable WP_REST_Request (backward-compat).
Legacy Bearer key path retained in device-auth.php — every use written to amboat_registration_audit
event='legacy_key_used'. TDD: verify-bug66-phase-c.sh 9/9 PASS. Commit 5fae9a91.
⚠ fleet-create/join/status/map/analytics/leave use PWA JWT — AMBOAT_API_KEY absent (confirmed grep);
out of scope for AMBOAT_API_KEY replacement.

### PHASE D COMPLETE — S134-cont 2026-08-25

**version-heartbeat.php UPSERT replaced with UPDATE.** Origin confirmed: SESSION_LOG S33/S37 —
UPSERT added for pre-pairing auto-registration. Safe to remove now: Phase C auth rejects unknown
devices at 401 before reaching SQL. UPDATE … WHERE device_token=?; 404 unknown_device if
affected_rows=0; misleading 'safe' comment deleted with the statement.
Phase A gap: approval handler must INSERT initial row in amboat_devices on device approval.
TDD: verify-bug66-phase-d.sh 5/5 PASS. Commit b94ce203.

### SEVERITY REVIEW — S131 2026-08-24

BUG-72 (logged S131) establishes that `version-heartbeat.php` — the endpoint this entry's analysis rests on — returns **404 in production and is not deployed**. The blind-UPSERT self-registration vector described below is therefore **not currently live and not presently exploitable**.

That fact was put to the operator with two options: hold CRITICAL as a gate on the design, or drop to HIGH on live exposure. **Operator decision: hold CRITICAL.** Rationale: the flaw ships the moment the endpoint deploys, and v0.9.9.4 is gated on security. The design must be fixed **before** BUG-72's deployment, not after.

**Sequencing consequence:** BUG-66's fix is a prerequisite of BUG-72, not a parallel task.

**Status:** `[!]` **LOGGED S127 2026-08-22. CRITICAL severity if the shipped image carries a live key — see the UNVERIFIED flag. Found during the BUG-63 registration-architecture review.**

### Symptom
Every Pi→HostPapa call is authenticated by **one shared static secret common to the entire
fleet**, stored in cleartext at `/opt/d3kos/config/cloud-config.json` on every device.
There is **no per-device credential anywhere in the codebase** — a repo-wide grep for
`hmac|signature|sign(` returns only Stripe webhook code and an unrelated `error_signature`
log field.

### Root Cause
The canonical auth check, `deployment/features/autonomous-agents/php/version-heartbeat.php:30-42`:

```php
if (!preg_match('/^Bearer\s+(.+)$/i', $auth_header, $m) || !hash_equals(AMBOAT_API_KEY, $m[1])) { 401 }
if (empty($device_token)) { 400 }
```

The `device_token` is required to be **non-empty** and is otherwise **never checked against
any record**. Line 82 then does `INSERT INTO amboat_devices … ON DUPLICATE KEY UPDATE`, so
**any UUID presented alongside the shared key silently self-registers as a new device**
(confirmed in SESSION_LOG.md:2112 — the heartbeat was deliberately changed from UPDATE-only
to UPSERT).

`AMBOAT_API_KEY` is documented as fleet-wide in `deployment/docs/ARCH_CREDENTIAL_MAP.md:19-38`
("Shared secret authenticating Pi-to-HostPapa API calls") — one value in every Pi's
`cloud-config.json` and in one server `config.php`.

### Affected Endpoints (12, all header-auth only)
`version-heartbeat.php:31` · `fleet-create.php:34` · `fleet-join.php:33` ·
`fleet-status.php:33` · `fleet-map.php:49` · `fleet-analytics.php:53` · `fleet-leave.php:29` ·
`failure-report.php:26` · `fix-confirmed.php:26` · `community-markers-write.php:47` ·
`community-position.php:47` · `config-backup.php:45`

Only `config-backup.php:112-127` checks the device exists (`SELECT id FROM amboat_devices … `
→ 403 "Device not registered") — but an earlier heartbeat creates that row for free, so it
enforces ordering, not authentication.

### Impact
Anyone holding the key can, for **any** `device_token`:
- register arbitrary fake devices
- read and write fleet membership, analytics and map data
- read and write community position markers — **live vessel positions**
- submit false failure reports and fix confirmations
- read and write config backups

### ⚠ UNVERIFIED — the question that sets the severity
**Does the shipped `.img` contain a live `AMBOAT_API_KEY`, or a placeholder?**

`[UNVERIFIED INFERENCE — image contents not inspected]` The repo copy at
`deployment/v0.9.4/pi_source/cloud-config.json:2` is a template. If the built image ships a
**live** key, then publishing the image on GitHub Releases (MASTER_SYSTEM_SPEC §12.1 — public,
anonymous download) **publishes the fleet key to the world**, and every endpoint above is open
to anyone who downloads d3kOS. That is the same failure class as BUG-58 (key committed to a
public repo) at fleet scale.

**Check before anything else is decided:** mount the most recent `.img` and inspect
`/opt/d3kos/config/cloud-config.json`. This single check decides whether this is CRITICAL and
urgent or HIGH and architectural.

### Fix Direction
1. **Immediately, if the image carries a live key:** rotate it, and remove it from the image build so first boot fetches or generates credentials instead.
2. **Per-device credentials.** Replace the shared bearer with the same Ed25519 device keypair proposed in `D3KOS_DEVICE_REGISTRATION_SPEC.md` v2.0.0 §2 — one enrolment, one public key per device, every request signed. Solves this bug and the registration anchor with one mechanism.
3. **Stop trusting `device_token` from the request body.** Derive the identity from the verified signature, never from a client-supplied field.
4. **Remove the blind UPSERT** at `version-heartbeat.php:82` — an unknown device must be rejected or queued, never auto-created.

### Relationship to Other Bugs
- **BUG-58** — same class (key exposure), previously a documentation leak; this is systemic.
- **BUG-59** — Phase 2 key-management design should absorb this; per-device keys are the answer to both.
- **BUG-65** — same absent trust boundary, seen from the licensing side.
- **Registration spec v2.0.0** — §3.1 explains why the current identity chain cannot anchor trust; this bug is the evidence.

### Verification
- [ ] Inspect the shipped `.img` for a live key (decides severity)
- [ ] Confirm an arbitrary UUID + the key self-registers a device row on a test endpoint
- [ ] After fix: an unsigned or wrongly-signed request must be rejected on all 12 endpoints

### Files
`deployment/features/autonomous-agents/php/version-heartbeat.php:30-42,64-91` ·
the 11 other endpoints listed above ·
`deployment/v0.9.4/pi_source/cloud-config.json:2` ·
`deployment/docs/ARCH_CREDENTIAL_MAP.md:19-38` · `SESSION_LOG.md:2112`

---
## BUG-67 — Sustained wp-login.php Brute Force — Primary Attacker Not IP-Blocked

**Status:** `[x]` **CLOSED S140 2026-09-01 — all 9 IPs permanently blocked in Wordfence S128. Monitoring stance accepted; no outstanding action items.**

**Source:** Wordfence Live Traffic log analysis, 2026-08-23 session.

### Symptoms
- `91.92.243.239` (Netherlands / Frantech Solutions / bulletproof hosting) hit `/wp-login.php` every ~3 minutes from at least 3:07 AM to 7:30 AM on 2026-08-23 — approximately 88 requests over 4+ hours.
- All requests return ~10,389 bytes (Wordfence block page — the login form is NOT being served, but PHP executes for every blocked request).
- User-Agent: `Mozilla/5.0` only — characteristic of attack scripts using minimal UA strings.
- Eight secondary IPs made single wp-login.php attempts in the same window: `72.60.116.29`, `3.97.46.140`, `66.97.34.83`, `194.185.38.105`, `217.160.147.228`, `193.231.3.48`, `120.138.27.176`, `167.172.26.225` — all returning 2,917 bytes (lighter Wordfence response; may indicate different block tier).

### Root Cause
Wordfence extended protection is active and blocking (confirmed by operator this session — `/wp-config.php.bak` confirmed 404; `/register` confirmed 404; extended protection confirmed). However, no permanent IP block has been applied to `91.92.243.239`, so Wordfence's lockout mechanism re-evaluates it on every request rather than short-circuiting at `.htaccess`. The result is ~88 PHP executions in 4 hours that could be zero with a permanent IP block.

### Impact
- Server load from unnecessary PHP executions on every blocked attempt.
- Sustained attack pattern suggests automated tooling with retry logic — will continue indefinitely without a permanent block.
- Combined with BUG-69 (admin username `admin` publicly known + 2FA off), the brute force risk is elevated.

### Fix Direction
1. **Immediate (operator action in Wordfence UI):** Wordfence → Firewall → Blocking → Add `91.92.243.239` to the permanent blocked IP list. Reason: "Sustained brute force 2026-08-23."
2. **Also block secondary IPs:** `72.60.116.29`, `3.97.46.140`, `66.97.34.83`, `194.185.38.105`, `217.160.147.228`, `193.231.3.48`, `120.138.27.176`, `167.172.26.225`.
3. **Review Wordfence lockout threshold:** Wordfence → All Options → Brute Force Protection → "Lock out after how many login failures" — reduce if currently above 5.
4. **Enable 2FA** (see BUG-69) — makes a successful brute force useless even if the password is guessed.

### Verification
- [ ] `91.92.243.239` added to Wordfence permanent block list
- [ ] Wordfence Live Traffic shows 0 new requests from that IP
- [ ] 8 secondary IPs added to blocklist
- [ ] BUG-69 (2FA) resolved as the complementary control

### Files
Wordfence Live Traffic log 2026-08-23 · Wordfence → Firewall → Blocking (operator UI action)

---

## BUG-68 — offline-check.php Authentication Token Sent in URL Query String

**Status:** `[x]` FIXED + CLOSED S128 2026-08-23. All three remediation steps complete: (1) `offline-check.php` `$_GET['token']` → `$_POST['token']` — committed c18b63b, deployed to HostPapa production via cPanel File Manager. (2) AMBOAT_API_KEY rotated — `mobile/config.php` on HostPapa production updated; old token `***REDACTED-S131***` is dead. (3) cPanel cron updated to POST with new token. Lab Pi `/opt/d3kos/config/cloud-config.json` updated S128 2026-08-23. REMAINING: Boat Pi `cloud-config.json` — update next visit to hotspot (`172.20.10.8`).

**Source:** Wordfence Live Traffic log analysis, 2026-08-23 session.

### Symptoms
`/wp-content/themes/twentytwenty-child/mobile/offline-check.php` is called every hour on the hour (4:00 AM, 5:00 AM, 6:00 AM, 7:00 AM observed) by a scheduled job:
- Caller IP: `66.102.137.24` (Google infrastructure range — likely a HostPapa cPanel cron or a Google Cloud scheduled function)
- User-Agent: `Wget/1.19.5 (linux-gnu)`
- Full URL: `/wp-content/themes/twentytwenty-child/mobile/offline-check.php?token='***REDACTED-S131***'`
- Response: 24 bytes (check returns a short OK/FAIL response — the call is functioning)

The token `***REDACTED-S131***` is now present in:
- HostPapa web server access logs
- Wordfence Live Traffic database
- The current session's Wordfence log export (shared with Claude Code this session — noted for the record; no action taken on the token by Claude Code)

### Root Cause
The scheduled caller passes the authentication token as a GET query parameter (`?token=`). HTTP GET parameters appear in full in every server log, proxy log, CDN log, and browser history. This is a standard web security error — authentication secrets must travel in the request body (POST) or in an Authorization/custom header, never in the URL.

### Impact
- The token is now logged in at least two persistent log systems on HostPapa.
- If HostPapa's log files are ever accessed by a third party (support ticket, log rotation error, shared hosting neighbour), the token is exposed.
- The token must be considered compromised and rotated regardless of whether any attack has occurred.

### Fix Direction
1. **Immediately — rotate the token.** Generate a new token, update `offline-check.php` and the caller script/cron with the new value. The old token must be invalidated.
2. **Change the caller to POST.** Update the Wget (or cURL) cron command to: `wget --post-data="token=NEW_TOKEN" https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/offline-check.php`
3. **Update offline-check.php to read from POST.** Change `$_GET['token']` to `$_POST['token']` (or read an `Authorization` header). Reject GET requests.
4. **Locate the cron definition.** Check HostPapa cPanel → Cron Jobs for the Wget command, or inspect any Google Cloud Function / Cloud Scheduler job that calls this endpoint.

### Verification
- [ ] Old token `***REDACTED-S131***` no longer accepted by the endpoint (return 401 or 403)
- [ ] New token generated and deployed
- [ ] Caller updated to POST — Wordfence Live Traffic shows no further GET requests with token in URL
- [ ] 24-byte OK response still returned on hourly call (functionality preserved)

### Files
`/wp-content/themes/twentytwenty-child/mobile/offline-check.php` (HostPapa live) · caller cron definition (HostPapa cPanel → Cron Jobs or Google Cloud Scheduler)

---

## BUG-69 — Admin Username `admin` Publicly Enumerable via Forum URLs + 2FA Disabled

**Status:** `[x]` **FULLY RESOLVED S140 2026-09-01.** Step 1: 2FA activated S128 2026-08-23 (Wordfence TOTP). Step 2: admin username renamed S140 2026-09-01 — new admin account created with non-guessable username + 2FA enrolled, old `admin` account deleted with content reassigned. Verified: `/forum/users/admin/topics/` → page not found. Username no longer enumerable.

**Source:** Wordfence Live Traffic log analysis, 2026-08-23 session. 2FA status confirmed by operator.

### Symptoms
Forum profile URLs directly reveal the WordPress admin account's login username:
- `/forum/users/admin/topics/page/2/` — visited by `114.119.129.254` (PetalBot / China)
- `/forum/users/admin/engagements/page/2/` — visited by `101.42.231.118` (China)
- `/forum/users/admin/engagements/page/3/` — visited by `43.138.19.77` (China)

These IPs can confirm: the admin login username is `admin`. This is also the most commonly attempted username in every WordPress brute force tool's default wordlist.

Simultaneously, `91.92.243.239` is making ~88 automated login attempts per 4-hour window (BUG-67). With the username known and no second factor, the attack only needs to guess the password.

**2FA status confirmed OFF** by operator on 2026-08-23. Wordfence Login Security → Two-Factor Authentication is not configured on the admin account.

### Root Cause
1. WordPress/bbPress constructs forum profile URLs using the login username, making it publicly enumerable without any authentication.
2. No second authentication factor is configured on the admin account, so a successful password guess grants immediate full site access.

### Impact
- Attacker has username (`admin`), a confirmed attack tool targeting this site (BUG-67), and no second factor to overcome.
- A successful login grants full WordPress admin access: can publish content, install plugins, modify theme files, export user data, reset passwords of all 62,000 accounts.
- With 62,000 accounts in `wp_users` (BUG-57 context), a full admin compromise is a GDPR/privacy incident.

### Fix Direction
**Step 1 — Immediate (operator action, ~5 minutes):**
Enable Wordfence Login Security → Two-Factor Authentication on the admin account. Use any TOTP app (Google Authenticator, Authy, 1Password). This closes the active risk — even a correctly guessed password cannot log in without the TOTP code.

**Step 2 — Soon (operator action, ~15 minutes):**
Rename the `admin` account to a non-guessable username.
In wp-admin → Users → find the admin account → change the username (requires a plugin such as "Username Changer" as WordPress does not allow username edits natively, or: create a new admin user with a different username, migrate content, delete the `admin` account).

**Step 3 — Complementary:**
Resolve BUG-67 (IP block the persistent attacker) — these two bugs share a threat chain and should be fixed together.

### Verification
- [ ] Wordfence Login Security → 2FA enabled and TOTP app enrolled on admin account
- [ ] Test login: password alone must be rejected; password + TOTP code must succeed
- [ ] Admin username renamed (if Step 2 is applied): `/forum/users/admin/` returns 404; new profile URL uses the new username
- [ ] BUG-67 primary attacker IP-blocked

### Files
Wordfence Login Security (operator UI) · wp-admin → Users (operator UI) · `wp_users` table (admin account row)

---

## BUG-70 — public-release docs/ folder deleted — README has 6 broken links

**Logged:** 2026-08-23 (S129)
**Severity:** LOW (closed)
**Status:** `[x]` **CLOSED S130 2026-08-23 — commit `e630bfeb` fixed 2 broken links; all 11 README links verified resolving. Original S129 diagnosis was DISPROVED — no `docs/` folder ever existed on `public-release`; there were 2 broken links (not 6), both caused by deliberate 2026-08-20 key-containment deletions that predate S129.**

### Corrected Root Cause — S130 finding
S129's diagnosis was wrong on every material point:
- No `docs/` folder ever existed on `public-release` — the prescribed fix would have created a folder that never existed
- There were **2** broken links, not 6
- Both broken links were from deliberate 2026-08-20 deletions (key-containment), not the S129 cleanup
- S130 investigated, found the 2 links, fixed with commit `e630bfeb`, verified all 11 README links resolving

### Original Diagnosis — S129 (DISPROVED by S130)

### Symptom (S129 — disproved)
All 6 documentation links in `README.md` on the `public-release` branch are broken. Clicking any doc link on GitHub returns 404.

### Affected Links (S129 — disproved; actual broken count was 2)
- `docs/CX5106_CONFIGURATION_GUIDE.md`
- `docs/INSTALLATION.md`
- `docs/SIGNALK_CONFIGURATION.md`
- `docs/REMOTE_ACCESS_SETUP.md`
- `docs/OPENCPN_FLATPAK_OCHARTS.md`
- `docs/D3KOS_USER_MANUAL_v2.3.0.md`

### Root Cause (S129 — disproved)
During S129 public-release branch cleanup, Claude Code removed the `doc/` folder (including the above files) without reading README.md first to check what files it referenced. The Pre-Change File List rule and Pre-Edit Snapshot rule were not followed. No operator APPROVED was obtained before the deletion.

### Current State (S129 — superseded)
- Operator set `SkipperDon/d3kOS` repo back to private on 2026-08-23.
- `public-release` branch has broken README but is no longer publicly visible.
- Pre-session backup at: `.aao-backups/20260823_123500_S129/public-release-original.bundle.bak` (46MB)

### Fix Required (S129 — superseded; e630bfeb is the actual fix)
1. Extract the 6 doc files from the pre-session backup bundle
2. Place them under `docs/` folder on `public-release` branch (README links to `docs/`, plural)
3. Note: `D3KOS_USER_MANUAL_v2.3.0` existed as `.html` in backup — need operator decision on format
4. Commit and push when operator approves making repo public again

### Protocol Failures That Caused This
- Did not read README.md before cleanup
- Did not present Pre-Change File List and wait for 'APPROVED'
- Did not run `git status` before filter-repo work (AAO Section 17)
- Did not read CLAUDE.md after context compaction

## BUG-71 — `pair-device.php` returns HTTP 500 in production; no source exists in the repo

**Status:** `[x]` **FIXED + DEPLOYED S136 2026-08-28 — ABSPATH guard added at lines 17-19 (`if (!defined('ABSPATH')) exit;`). Deployed to HostPapa live. Commit be4485c9. Root cause: it was a WP AJAX handler, not a direct endpoint — the 500 fired only when fetched outside WordPress context.**
**Severity:** downgraded **HIGH → LOW.** It is not on the critical path and never was.

---

## S135 INVESTIGATION — 2026-08-28

**Unblocked by:** FTP access (condition G2 in `PHASE3-blocked-items.md`).
**First action taken, per that spec:** the file was brought under version control **byte-identical,
before any analysis** — commit `13eebcbc`, `deployment/v0.9.9.4-server/mobile/pair-device.php`,
3,306 B, md5 `b3ccd9f34d04a3c43a88eabd1aec4e1d`. No edits.

### The 500 is fully explained

`pair-device.php` is a **WordPress AJAX handler registration file**, not a routable endpoint. Its own
comments say so (`:17-18`), and `:20` is:

```php
add_action( 'wp_ajax_atmyboat_confirm_pairing', 'atmyboat_confirm_pairing' );
```

It is `require_once`d into WordPress by `functions.php:220` and invoked through
`admin-ajax.php?action=atmyboat_confirm_pairing`.

**It has no `ABSPATH` guard.** So an HTTP request straight to the file executes it outside WordPress,
`add_action()` is undefined, PHP fatals, and — with `display_errors` off — the response is
**HTTP 500 with an empty body.** That is exactly what S131 observed and recorded as "the fault is
inside the file". The fault is that the file was fetched at all.

⚠ **S131's reasoning was sound and still reached the wrong conclusion.** It noted the empty body was
"consistent with `error_reporting(0)`", and that sibling endpoints return 401/405 correctly — both true.
The missing step was asking *whether this file is an endpoint*. **A 500 from a PHP file proves the file
executed; it does not prove the file was meant to be requested.**

### The critical-path claim was wrong — correct the record

`PHASE3-blocked-items.md` states: *"It is step 2 of PWA device pairing… every PWA integration test for
a new device is blocked behind it. It is the critical path, not a side issue."*

**That is not correct.** The handler is registered (`functions.php:220` — verified present), so the
pairing path through `admin-ajax.php` is intact. Nothing is blocked by the 500.

`Uncertainty flag: the pairing round-trip was NOT executed end-to-end — that needs an authenticated
session and a real pi_id, which was out of scope for a read-only investigation. What is established is
that the handler is registered and the 500 is an artefact of direct fetch. Do not upgrade that to
"pairing works" without running it.`

### The one real defect

**`pair-device.php` is the ONLY file in `mobile/` that is a WordPress include and lacks the guard.**
Audited all 44 local `mobile/*.php`: exactly one has a top-level `add_action`/`add_filter` **and** no
`ABSPATH` reference — this file.

⚠ **The other 42 files without an `ABSPATH` reference are NOT defects.** They are standalone REST
endpoints meant to be fetched directly (`data-ingress.php` → 405, `version-heartbeat.php` → 401).
**Do not "fix" them by adding guards — that would break every Pi→server call.**

**Fix — three lines, at the top of the file:**

```php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
```

This matches `enrol.php` and makes a direct fetch return an empty 200 instead of a 500.
**Decision needed:** match `enrol.php`'s silent 200, or return an explicit 403? 403 is better practice;
200-empty is consistent with the existing codebase. Operator's call — it is cosmetic either way.

### Two further findings from the same investigation — logged separately

1. **`inc/atmyboat-functions.php:107`** requires this file via `get_template_directory()` — the
   **PARENT** theme — for a file that lives in the **child**. Identical trap to BUG-86. **Currently
   dormant: nothing requires `inc/atmyboat-functions.php`** (grep of `functions.php` and `inc/` returns
   nothing). A latent landmine, not an active fault. → **BUG-88**
2. **The repo holds 44 `mobile/*.php`; production has 76.** **32 production files exist nowhere in the
   repo.** This is the concrete measure of the "no canonical tree for the HostPapa side" root cause that
   BUG-72, BUG-76 and `PHASE3-server-canonical-tree.md` all reference. → **BUG-88**

### Definition of done

- [x] Source under version control, byte-identical, own commit (`13eebcbc`)
- [ ] `ABSPATH` guard added — operator picks 200-empty or 403
- [ ] Re-probe: direct GET returns **not-500**
- [ ] Pairing round-trip exercised once through `admin-ajax.php` to retire the uncertainty flag above
- [ ] `PHASE3-blocked-items.md` corrected — the critical-path claim must not survive
- [ ] Live deploy only with explicit operator `APPROVED`

### Related

- **BUG-88** — the parent-path landmine and the 32 unversioned production files
- **BUG-86** — the same parent-vs-child theme-path error, which did fire
- **BUG-72 / BUG-76** — same root cause: no server-side canonical tree

## BUG-72 — `version-heartbeat.php` was written but never deployed; BUG-66's live severity is overstated

**Logged:** 2026-08-24 (S131) · **Fixed:** S134 2026-08-25 · **Status:** `[~]` STAGING DONE — deployed and verified on HostPapa staging; live deploy requires explicit APPROVED.
**Platform:** HostPapa (atmyboat.com production)
**Severity:** MEDIUM — a designed endpoint is absent from production, and its absence changes the
risk assessment of a CRITICAL-rated bug.

### Symptom

```
GET .../twentytwenty-child/mobile/version-heartbeat.php  -> 404, 404   (re-probed, stable)
```

Source **does** exist in the repo at
`deployment/features/autonomous-agents/php/version-heartbeat.php` — so this is written-but-never-
deployed, not missing-entirely.

### Why this matters beyond the endpoint itself

**BUG-66's severity analysis is built on this file.** BUG-66 states that
`version-heartbeat.php:30-42` requires `device_token` to be non-empty and nothing else, and that
line 82's `INSERT … ON DUPLICATE KEY UPDATE` lets any UUID plus the fleet key silently
self-register a device.

That vector **is not currently live**, because the endpoint is not deployed.

⚠ BUG-66's CRITICAL rating should be re-scored against what is actually deployed rather than what
is in the repo. The underlying design flaw is real and must still be fixed before this endpoint
ships — but it is not presently exploitable. **Operator decision: does BUG-66 stay CRITICAL as a
release gate on the design, or drop to HIGH on the live exposure?**

### Root Cause

There is no canonical tree, manifest, or drift check for the HostPapa side of the system. PHP
deliverables live scattered across 8 `deployment/features/*/` folders with no record of what was
deployed where. This endpoint was written (2026-04-08, `autonomous-agents`) and simply never pushed.

### Fix Required

1. Establish the server-side canonical tree + manifest (the structural fix — see Related below).
2. Fix the BUG-66 design flaws **before** deploying: per-device credential instead of the shared
   fleet key; derive identity from a verified signature, never a client-supplied field; remove the
   blind UPSERT.
3. Deploy with explicit approval. Re-probe for a correct 401 on an unauthenticated GET.

### Related Bugs

- **BUG-66** — the design flaws in this endpoint; severity depends on this entry
- **BUG-71, BUG-73** — the same HostPapa state-tracking gap, different symptom

---

## BUG-73 — `fix-my-pi-billing.php` absent from both production and the repo; Fix My Pi payments cannot complete

**Status:** `[x]` **CLOSED — NOT A BUG. S135 2026-08-28. THE PREMISE IS WRONG ON BOTH COUNTS.**
The file exists in production **and** in the repo, byte-identical, and it works.
Was: `[ ]` OPEN, HIGH — revenue path.

---

## S135 INVESTIGATION — 2026-08-28

### The file exists in both places, and they are in sync

| Location | Size | md5 |
|---|---|---|
| Production `wp-content/themes/twentytwenty-child/mobile/fix-my-pi-billing.php` | 16,700 B | `767eee77c91f478dbac7fd43e63eb703` |
| Repo `atmyboat-forum/wp-content/themes/twentytwenty-child/mobile/fix-my-pi-billing.php` | 16,700 B | `767eee77c91f478dbac7fd43e63eb703` |

**Identical.** Its two siblings are also present and in sync — `fix-my-pi-app.php` (8,802 B) and
`fix-my-pi-job.php` (1,668 B).

### Why the 404 was not what it looked like

The file is a **392-line action router**. Requesting it without an `?action=` parameter falls through
to the default case at `:252`:

```php
amboat_send_error( 'Unknown action.', 404 );
```

**The 404 was the file answering correctly.** Proven by probe, 2026-08-28:

```
?action=webhook  -> 405   (:178 POST required — the route exists)
?action=bogus    -> 404   (:252 Unknown action)
(no action)      -> 404   (same default case)
```

A 405 on `?action=webhook` is only possible if the file is present, parsed, and routing.

### Root cause of the misdiagnosis — a repo search that covered one of two repos

S131 recorded *"Repo-wide search returns nothing for the billing half."* Confirmed S135:
`find /home/boatiq/Helm-OS -name fix-my-pi-billing.php` returns **nothing** — while the file sits in
`/home/boatiq/atmyboat-forum/`.

⚠ **This project has two repos. The search covered `Helm-OS/` only.** Combined with reading an HTTP 404
as "file absent" rather than as a response, that produced a HIGH-severity revenue-path bug for a file
that was present and working the whole time.

**Standing correction: `grep`/`find` for any atmyboat.com asset must cover BOTH `/home/boatiq/Helm-OS/`
and `/home/boatiq/atmyboat-forum/`.** See also `SESSION-START git check` — the same two-repo split
already caused a `git status` blind spot (S107).

### What is actually implemented — assessed, not assumed

`?action=create_session` (Stripe checkout, T1 $29.99) · `?action=webhook`
(`checkout.session.completed`) · `?action=request_free` (T2 decrement / T3 unlimited) · a refund path
(`:155`) · writes to `amboat_billing` (`:223`).

**Webhook signature verification is correct** (`:367-392`) — not a stub:
- parses `t` and `v1` from `HTTP_STRIPE_SIGNATURE`
- **rejects events older than 300 s** — replay protection present
- `hash_hmac('sha256', "$timestamp.$payload", STRIPE_WEBHOOK_SECRET)`
- compares with **`hash_equals()`** — constant-time, not `===`
- returns `null` on any failure; the caller then 400s

That is the reference implementation, including the constant-time comparison most integrations get
wrong. **There is no unsigned-webhook bypass.** Had verification been a stub, anyone could have POSTed
a forged `checkout.session.completed` and queued paid work for free — it is not.

### What this does to the G4 operator action

`PHASE3-blocked-items.md` framed the Stripe dashboard check as urgent: *"This determines whether the
exposure is theoretical or whether a customer has been charged for work never done."*

**Downgrade it to routine verification.** That concern rested on the webhook being absent, so Stripe
having nowhere to deliver the payment event. The webhook is present, wired and signature-verified —
there is **no structural reason** for a charge to complete without work being queued.

`Uncertainty flag: the end-to-end flow was NOT executed. Confirming that a real charge produces a
queued fix_my_pi command still needs the Stripe dashboard, and any test must use Stripe TEST mode only.
"The code is correct" is not "the flow has run". Do not close the G4 check on this entry alone.`

⚠ **BUG-10's precedent still applies and is unaffected by this closure:** Stripe webhooks were once left
pointing at `/staging/`. **Check where the Stripe dashboard currently points** — a correct webhook file
at the wrong URL fails exactly like a missing one. ⚠ And note **BUG-85**: anything aimed at a
`/staging/` page route is now served by production.

### Related

- **BUG-75** — same session, same shape: an endpoint declared 404/missing that is present and returns 405
- **BUG-71** — same session: a 500 read as "broken endpoint" when the file was not an endpoint
- **BUG-88** — 32 production files with no repo copy; the reason searches like this go wrong
- **BUG-10** — Stripe webhooks pointed at staging after the Phase 4 live push

## BUG-74 — `MASTER_SYSTEM_SPEC` §8.4.2 P5 names a credential file that does not exist; the real one is world-readable

**Logged:** 2026-08-24 (S131) · **Fixed:** S134 2026-08-25 · **Deployed lab Pi:** S134 2026-08-25 · **Platform:** Pi + spec · **Severity:** MEDIUM (HIGH as a contributing cause of BUG-66) · **Status:** `[x]` FIXED + DEPLOYED LAB PI — 7/7 PASS. `/opt/d3kos/tools/release-state.sh`. Commit b909b227.

### Symptom
§8.4.2 P5 specifies `/opt/d3kos/config/cloud-credentials.json` as *the* credential source for the
Pi→website pipeline, including a `cloud-credentials.json.example` template. Live read of the lab Pi:

```
cloud-config.json        644 d3kos:d3kos  312 bytes   <- the file that actually exists
cloud-credentials.json   ABSENT                       <- the file the spec requires
```

Any spec, script, or Tier 3 dispatch written from §8.4.2 literally targets a non-existent path.

### Compounding defect
`cloud-config.json` is mode **644 — world-readable**, and it carries the fleet-wide `AMBOAT_API_KEY`
(BUG-66). Same defect class as `license.json` at 644 (BUG-65). §8.4.2 P5 also states the file "must be
in `.gitignore`" — verify that covers the real filename, not just the specified one.

### Fix Required
1. Correct §8.4.2 P5 to `cloud-config.json` (done S131).
2. Change mode to `600` and confirm ownership.
3. Confirm `.gitignore` covers `cloud-config.json`.
4. Fold into the BUG-66 per-device credential work — do not fix in isolation.

### Related
BUG-66 (the key this file holds), BUG-65 (same 644 class), BUG-78 (this file ships in the image)

---

## BUG-75 — `MASTER_SYSTEM_SPEC` §8.4.2 P1 specifies a data-ingress URL that returns 404

**Status:** `[x]` **CLOSED S140 2026-09-01 — operator decision: no `/mobile/` alias. Short form removed from spec S131; full child-theme path is the canonical URL. Nothing in Pi code uses the short form.** Severity MEDIUM.

---

## ⚠ S135 — 2026-08-28

### This entry was logged correctly — noted deliberately

Re-probed 2026-08-28, reproducing the entry exactly:

```
/mobile/data-ingress.php                                       -> 404
/wp-content/themes/twentytwenty-child/mobile/data-ingress.php  -> 405   (POST-only)
```

⚠ **Correction to an S135 claim made earlier in this session:** BUG-75 was briefly grouped with BUG-73
as a "premise overturned by a live read." **That was wrong.** This entry recorded *both* probes and
stated that only the full child-theme path resolves. It is accurate and always was. Four premises were
overturned this session (BUG-72, 73, 71, 64) — **not** this one.

### Step 2 — the URL audit — COMPLETE, and it found three broken destinations

Step 2 asked for *"every Pi-side and Node-RED destination URL audited against the probe results, not
against the spec."* Done across the canonical Pi tree. **No Pi code uses the broken short
`/mobile/` form** — so the spec error never propagated into code. But the audit found three
destinations that 404 for other reasons → logged as **BUG-89**.

**`/staging` also appears three times in the tree — that is NOT a BUG-55 regression.** All three hits
are inside `tools/verify-bug55.sh`, the guard script, which necessarily contains the string it searches
for. BUG-55 holds.

### Step 3 — the only thing left, and it is an operator decision

**Should a `/mobile/` rewrite alias exist?**

- **No (recommended):** delete the short form from the spec. Nothing uses it, the full path works, and
  an alias is one more thing to keep in sync.
- **Yes:** it is a deliberate `.htaccess` change on HostPapa — **not** a documentation edit.
  ⚠ Sequence it **after BUG-85**: `/staging/.htaccess` is currently a copy of live's, so any rewrite
  work must not be tested through a staging path that production serves.

### Related

- **BUG-89** — the three broken destinations this audit found
- **BUG-54** — export failures; ⚠ still no evidence linking its HTTP 400 to this. Do not merge them.
- **BUG-76** — the naming-scheme conflict, which this audit **widened from three schemes to five**

### Symptom *(original S131 record — still accurate)*
§8.4.2 P1 states the "Required" endpoint is `https://atmyboat.com/mobile/data-ingress.php`. Probed:

```
/mobile/data-ingress.php                                        -> 404
/wp-content/themes/twentytwenty-child/mobile/data-ingress.php   -> 405   (correct: POST-only)
```

There is no `/mobile/` alias. The spec's required URL does not resolve; only the full child-theme path
does. `ARCH_SERVICE_MAP.md` has the correct path — the two documents disagree.

### Why it matters
BUG-54 records 110 export failures against a placeholder hostname and 63 against an nginx HTTP 400.
Anything built to §8.4.2 P1 would add a third failure mode. `Uncertainty flag: I have NOT established
that BUG-54's 400 is related to this. Do not merge the two diagnoses without evidence.`

### Fix Required
1. Correct §8.4.2 P1 to the full theme path (done S131).
2. Audit every Pi-side and Node-RED destination URL against the probe results, not against the spec.
3. Decide whether a `/mobile/` rewrite alias *should* exist — if the short path is wanted, that is a
   deliberate `.htaccess` change on HostPapa, not a doc edit. **Operator decision.**

### Related
BUG-54 (export failures), BUG-55 (staging→production repointing), BUG-76

---

## BUG-76 — Five endpoints specified as REQUIRED in §8.4.4 are all 404, and three documents name them three different ways

**Status:** `[x]` **FIXED S136 2026-08-28 — §8.4.4 corrected in MASTER_SYSTEM_SPEC v4.1; canonical names established from deployed reality (`data-ingress.php`, `community-get.php`, `community-markers.php`). Five phantom endpoint names removed. Commit be4485c9.**
**Severity:** HIGH → **MEDIUM.** The community/telemetry pipeline is **not** blocked; it runs by a
different route.

---

## S135 VERIFICATION — 2026-08-28

Read from the production FTP listing (76 files in `mobile/`), not inferred from HTTP codes.

### The five are genuinely absent — this one is real

| §8.4.4 name | Production | Repo |
|---|---|---|
| `community-markers-post.php` | **ABSENT** | absent |
| `community-markers-get.php` | **ABSENT** | absent |
| `telemetry-push.php` | **ABSENT** | **absent from BOTH repos — never written** |
| `community-benchmark.php` | **ABSENT** | **absent from BOTH repos — never written** |
| `community-position.php` | **ABSENT** | `features/v0941-plan/php/` only — a **design** tree |

⚠ **Note the distinction this session has had to make five times:** BUG-73 and BUG-75 were files that
existed and answered with 404/405. **These five are actually not there.** The difference was established
by an FTP directory listing, not by reading status codes. *Probe to find a candidate; list the directory
to conclude.*

### But the pipeline they are "required" for already works, by another path

| Deployed and working | Size | Role |
|---|---|---|
| `data-ingress.php` | 11,517 B | telemetry receiver — `export_worker.py:299` POSTs here; returns 405 on GET |
| `community-get.php` | 3,888 B | community read path |
| `community-markers.php` | 4,691 B | markers |

`export_worker.py` → `data-ingress.php` → `wpax_usermeta` → `community-get.php`. The S134-cont audit
reached the same conclusion independently: *"community map DOES NOT NEED these flows… fleet dots work
via this existing path."*

**So `telemetry-push` and `community-benchmark` are not missing implementations of a required
interface. They are a paper design that a working implementation bypassed.**

### Resolving the three-way naming conflict — decide from what is deployed

| Source | Name |
|---|---|
| `MASTER_SYSTEM_SPEC` §8.4.4 | `community-markers-post.php` / `community-markers-get.php` |
| `ARCH_SERVICE_MAP.md` | `community/markers.php` |
| **Production (authoritative)** | **`community-markers.php` + `community-get.php`** |

⚠ BUG-76's original recommendation was *"the flat `community-*.php` form, since those files exist."*
**Refine it: the canonical names are the two that are DEPLOYED.** A fourth name,
`community-markers-write.php`, exists in the design tree and must be retired, not adopted — otherwise
this becomes a four-way conflict.

### Fix required — spec correction, then a product decision

1. **Correct `MASTER_SYSTEM_SPEC` §8.4.4** to describe the deployed reality: `data-ingress.php`,
   `community-get.php`, `community-markers.php`. Remove `community-markers-post`/`-get` as REQUIRED —
   they never existed and nothing needs them.
2. **Correct `ARCH_SERVICE_MAP.md`** to the same names. ⚠ Three documents, one truth — fix both, or the
   conflict simply moves.
3. **Operator decision, not an implementation task:** are `telemetry-push` and `community-benchmark`
   wanted *capabilities*? They were never written. If yes they are **v0.9.9.5 features**; if no, delete
   them from the spec. **Do not build them to satisfy a document.**
4. Retire `community-markers-write.php` from `v0941-plan/` or rename it to the deployed name.

⚠ **`deployment/features/v0941-plan/php/` is a DESIGN tree, not a deployment source.** It holds
`page-community-ORIGINAL.php` and `page-dashboard-ORIGINAL.php` mockup variants alongside the PHP.
Nothing in it should be assumed deployed. This trapped BUG-66 Phase C — see below.

### ⚠ Knock-on finding for BUG-66 — recorded there too

BUG-66 Phase C reports *"6 Pi→Server endpoints migrated to Ed25519"*. **Three of the six are not in
production:**

| Endpoint | Deployed? | Where the edited file lives |
|---|---|---|
| `version-heartbeat.php` | ✅ yes (verified 401 live) | `features/autonomous-agents/php/` |
| `failure-report.php` | ✅ yes | `features/autonomous-agents/php/` |
| `config-backup.php` | ✅ yes | `features/fi4-config-backup/php/` |
| `fix-confirmed.php` | ❌ **no** | `features/autonomous-agents/php/` |
| `community-markers-write.php` | ❌ **no** | `features/v0941-plan/php/` (design tree) |
| `community-position.php` | ❌ **no** | `features/v0941-plan/php/` (design tree) |

**This is not a live exposure** — an undeployed file cannot be attacked. It is a **coverage claim that
overstates reality**: half the migration hardened files nobody serves. Correct BUG-66's status line so a
future session does not read "6 migrated" as "6 live".

### Related

- **BUG-66** — the overstated Phase C coverage
- **BUG-88** — 32 production files with no repo copy; the same absent-canonical-tree root cause
- **BUG-72 / BUG-75 / BUG-73** — same S131 sweep; those three premises were wrong, this one is right

## BUG-77 — `detectTier()` can never return Tier 1, yet Tier 1 is a defined tier and the registration design gates on it

**Logged:** 2026-08-24 (S131) · **Deployed lab Pi:** S134 2026-08-25 · **Platform:** Pi + spec · **Severity:** HIGH — blocks the device-tied registration design
**Status:** `[x]` **FIXED + DEPLOYED LAB PI S134 2026-08-25 — 9/9 PASS. `/opt/d3kos/services/tier/tier_service.py` + `/opt/d3kos/scripts/tier-manager.sh`. Commit 1facb1b2.**

#### Fix summary
- `tier_service.py`: `device_is_paired_and_approved()` — queries `/wp-json/amboat-device/v1/status`
  via Ed25519 signed channel; caches at `/opt/d3kos/state/tier1-approval.json` (mode 600);
  offline-first (cached result stands on server down); fail-closed (no cache + down → False);
  polls max once per 15 min; `status == 'approved'` is the exact trust anchor (`'pending'` is NOT Tier 1).
- `tier_service.py`: `detect_tier()` — ordering Tier 3 > Tier 2 > Tier 1 > Tier 0;
  `license.json` NOT consulted for Tier 1 (T8 trust-anchor: file cannot grant Tier 1 alone).
- `tier_service.py`: `/tier/status` and `/tier/feature/` use `detect_tier()`.
- `tier-manager.sh`: ordering fixed — `subscription.key` first, then paid subscription,
  then OpenCPN, then reads `tier1-approval.json` cache for boot-time Tier 1.
- `app.py`: two inline `int(str(t).replace('T',''))` sites replaced with `_parse_tier()`
  (deduplication — same BUG-29 class).
- TDD: `verify-bug77.sh` 9/9 PASS.
⚠ NOTED: `data-ingress.php feature_matrix` not in canonical tree — Pi-vs-server matrix comparison
  deferred until live HostPapa read. Log as new bug if values disagree.

### Symptom
§6.3.1's `detectTier()` has exactly three outcomes:

```
/opt/opencpn exists                      -> tier 2
/opt/d3kos/config/subscription.key exists -> tier 3
otherwise                                 -> tier 0
```

**There is no Tier 1 branch.** But §6.3.2 defines Tier 1 as a free tier carrying mobile app, QR
pairing, cloud sync, data export, push notifications and remote monitoring — and
`D3KOS_DEVICE_REGISTRATION_SPEC.md` v2.0.0 decision **D1** gates forum accounts on
*"Tier 1 or higher"*. **A gate on a value the detection logic cannot produce.**

### Live corroboration (lab Pi)
```
/opt/opencpn            EXISTS      -> detectTier() would return 2
subscription.key        ABSENT      -> the only documented path to tier 3
license.json            "tier": "T3"  mode 644 root:root
```
The Pi claims T3 with no subscription key present, and the file is trusted verbatim (BUG-65). Note also
the deployed value is the **string `"T3"`**, not the integer the spec shows, and the file carries six
fields §6.3.1 never mentions.

### Resolution — OPERATOR DECISION S131: Option (a)
`detectTier()` returns **1 when the device has a `device_token` that is paired and server-approved.**
Rationale: it makes Tier 1 mean something *checkable against the server* rather than something asserted
by a world-readable local file, and it folds device pairing and forum registration into one event — the
open question raised at `D3KOS_DEVICE_REGISTRATION_SPEC.md` §12.2.

Consequences to carry into the specs:
- Tier 1 becomes the first **server-verified** tier. Tier 0 stays purely local.
- The approval queue (registration spec §3) becomes the authority for Tier 1, so the trust anchor is
  the same human decision for both registration and tier — one mechanism, not two.
- Tier 2/3 remain filesystem/subscription tests for now; **BUG-65 still applies to them** and is not
  closed by this.

### Fix Required
1. Amend §6.3.1 with the Tier 1 branch (done S131).
2. Reconcile the deployed `license.json` schema with the spec (`"T3"` vs `3`, extra fields).
3. Implement the paired-and-approved check as part of the BUG-66 per-device credential work.
4. Test: an unpaired device must never report Tier 1.

### Related
BUG-65, BUG-66, BUG-63, `D3KOS_DEVICE_REGISTRATION_SPEC.md` D1 and §12.2

---

## BUG-78 — CRITICAL: the image builder never invokes the sanitizer, and the sanitizer misses every credential file

**Logged:** 2026-08-24 (S131) · **Fixed:** S134 2026-08-25 · **Deployed lab Pi:** S134 2026-08-25 · **Platform:** Image build / distribution · **Severity:** **CRITICAL** · **Status:** `[x]` FIXED + DEPLOYED LAB PI — 6/6 PASS. `/opt/d3kos/scripts/create-image.sh` + `/opt/d3kos/scripts/sanitize.sh`. Commit 23bef5ec. ⚠ §12.1 spec reconciliation still pending.


### ⚠ ROOT CAUSE CORRECTED — S131, before any fix was attempted

The symptom above was derived from §12.1 of `MASTER_SYSTEM_SPEC.md`. **A live read of the Pi shows
§12.1's script is fictional** — it matches nothing that exists. The real situation is worse in one way
and better in another, and the fix is different from what the original entry implied.

**Three cleanup scripts exist. None handles credentials. None is wired into the image build.**

| Script | Location | What it actually cleans | Invoked by the builder? |
|---|---|---|---|
| `create-image.sh` | **Pi only — absent from the repo** | `apt-get clean`, `journalctl --vacuum-size=50M`, `/tmp/*`, `/var/tmp/*` | it *is* the builder |
| `sanitize.sh` | **Pi only — absent from the repo** | SSH keys + host keys, chromium cookies/history/sessions, `license.json` reset, onboarding config, Signal K security config | **NO** |
| `pre-image-cleanup.sh` | **Repo only** | chromium cache | **NO — referenced nowhere in the codebase** |

Verified by grep against the deployed `create-image.sh`: **no call to `sanitize.sh`, `shrink-filesystem.sh`,
or any `install-*`/`configure-*` script.** It does not even remove `~/.bash_history`, which §12.1 claims.

**So there are three distinct defects, not one:**

**D1 — the sanitizer is never called.** A capable sanitizer exists and the image builder ignores it.
The image is therefore built from a *fully unsanitized* card: SSH host keys, chromium cookies, the live
`license.json`, and every credential.

**D2 — `sanitize.sh` misses all five credential/identity files.** Grep count in `sanitize.sh`:

```
cloud-config       0     <- holds the fleet-wide AMBOAT_API_KEY (BUG-66)
api-keys           0     <- Gemini / provider keys
device-token       0     <- device identity (BUG-39)
device-signing     0     <- future Ed25519 private key (registration spec §2.1)
subscription.key   0     <- grants Tier 3 by mere existence (BUG-65)
```

So even wiring D1 would leave the fleet key in the image.

**D3 — `sanitize.sh` STEP 8 re-creates BUG-65.** Its `license.json` rewrite ends with an explicit
`chmod 644`. The sanitizer hardcodes the world-readable mode. It also writes `"tier": 0` as an
**integer**, while the live file holds the **string** `"T3"` — confirming the schema divergence in
BUG-77 and meaning the two representations are not interchangeable in code.

**D4 — the tooling is unsourced.** `create-image.sh` and `sanitize.sh` exist only on the Pi. They are
production tooling with no version control and no review history — the same class as `pair-device.php`
(BUG-71). A fix applied on the Pi would be lost on the next reflash.

**What did NOT change:** the impact assessment stands. §12.1 hosts on GitHub Releases (public,
anonymous), and an image built today ships the fleet-wide key. `Uncertainty flag: no released .img has
been inspected. Whether one ALREADY carries a live key remains UNVERIFIED and is still the
highest-priority operator action.`

**Corrected fix path — see `atomic-specs/BUG-78.md`:**
1. Bring both scripts into the canonical tree first (D4). Nothing is edited on the Pi only.
2. Extend `sanitize.sh` with a credential-and-identity strip covering all five files (D2), and change
   its `license.json` mode to 600 (D3).
3. Wire `sanitize.sh` into `create-image.sh` *before* `dd` (D1), with a hard refusal to proceed if it
   fails.
4. Add a build-time assertion that **fails the build** if any secret survives. A checklist step is not
   sufficient — S129 demonstrated a documented manual step gets skipped under pressure.
5. First-boot regenerates everything, reusing the BUG-39 `.identity-regenerated` sentinel.

**Lesson recorded:** the original entry was written from the specification. The specification described a
script that does not exist. `MASTER_SYSTEM_SPEC` §12.1 must be treated as intent, never as ground truth
— and this is why an atomic spec's anchors are derived from the target file, never from a document.

### Symptom as originally logged (SUPERSEDED by the correction above)
§12.1's `create-image.sh` cleanup step removes exactly three things:

```
rm -rf /var/log/*      rm -rf /tmp/*      rm -rf ~/.bash_history
```

**`/opt/d3kos/config/` is never touched.** Live read of the lab Pi shows what would therefore be baked
into any image built from a configured card:

| File | Mode | Contents |
|---|---|---|
| `cloud-config.json` | **644** | fleet-wide `AMBOAT_API_KEY` (BUG-66) |
| `api-keys.json` | 600 | Gemini / provider keys |
| `license.json` | **644** | tier claim (BUG-65) |
| `device-token.json` | 664 | device identity |

§12.1 hosts the result on **GitHub Releases — public, anonymous download**, with a published SHA-256.

### Impact
Publishing an image built from a configured master card **publishes every credential on that card**.
This is the same failure class as BUG-58 (one key in one public doc), except it distributes the
**fleet-wide** key to every downloader, and the key authenticates 12 server endpoints. It also means
every d3kOS install would share one `device_token`, which is what BUG-39 exists to prevent.

`Uncertainty flag: no d3kOS .img has been inspected this session. Whether a released image ALREADY
carries live credentials is UNVERIFIED and is the single most important thing to check.`

### Fix Required
1. **Operator first:** inspect the most recent released `.img` (mount it, read `/opt/d3kos/config/`).
   If a live key is present, **rotate immediately and unpublish** — this outranks every other item.
2. Add an explicit credential-strip step to `create-image.sh`: delete `cloud-config.json`,
   `api-keys.json`, `license.json`, `device-token.json`, `device-signing.key`, and any `*.bak` of them.
3. Add a **build-time assertion that fails the build** if any of those files exist in the image root —
   a checklist step is not sufficient; this must be mechanically enforced.
4. Ensure first-boot generates all of them fresh, reusing the BUG-39 `.identity-regenerated` sentinel
   pattern so the master image cannot carry identity.
5. Amend §12.1 (done S131).

### Related
BUG-66 (the key), BUG-65 (license.json), BUG-39 (identity duplication), BUG-58 (same class, smaller
blast radius), BUG-74, `D3KOS_DEVICE_REGISTRATION_SPEC.md` §2.1 (keys must never be baked into the image)

---

## BUG-79 — §9.2 "No Phone-Home" is false, and §9 specifies almost no security architecture

**Logged:** 2026-08-24 (S131) · **Platform:** Spec · **Severity:** MEDIUM (root cause of BUG-65/66)
**Status:** `[x]` **FIXED S131 2026-08-24 — §9.2 corrected in MASTER_SYSTEM_SPEC v4.0; false "No Phone-Home" claims replaced with accurate description of what the system does. §9 security gap noted; design of record pointed to `D3KOS_DEVICE_REGISTRATION_SPEC.md` v2.0.0.**

### Symptom — the false claim
§9.2 states: *"All tier detection is local (no cloud checks) · No telemetry or analytics · No license
key validation servers."* Every clause is contradicted **by the same document**:

| §9.2 claim | Contradicted by |
|---|---|
| no cloud checks | §8.3 central database sync; §8.4 full Pi↔website pipeline |
| no telemetry | §8.3.1 category #9 — comprehensive telemetry & analytics export |
| no license validation servers | Stripe subscription webhooks (§6.3.4); fleet management; `version-heartbeat` |

Anyone designing to §9.2 designs for a system that does not exist. **This is the direct cause of the
BUG-65/66 design gap** — and of the S127 incident where a security scheme was revised three times
before the spec was read.

### Symptom — the deeper problem
§9 is **67 lines total** (L6369–6437) for the entire "Security & Licensing" section of a 7,189-line
specification. It contains no authentication model, no credential lifecycle, no key rotation, no
per-device identity, no threat model, and no data-protection requirements. There is almost no security
architecture to violate, which is why BUG-65 and BUG-66 are *architecturally intended* rather than
oversights.

### Fix Required
1. Correct §9.2's false claims and state what the system actually does (done S131).
2. **Do NOT author a full security architecture as a doc edit.** It is a design task requiring operator
   decisions on offline-first vs server enforcement. §9 now points to
   `D3KOS_DEVICE_REGISTRATION_SPEC.md` v2.0.0 as the live design of record, and to BUG-65/66/78.
3. Fold the resulting design back into §9 once BUG-65/66 are decided — **as a release-gate deliverable.**

### Related
BUG-65, BUG-66, BUG-77, BUG-78, `D3KOS_DEVICE_REGISTRATION_SPEC.md` §10 (flagged §9.2 as stale first)

---

## BUG-80 — §12.2 publishes WiFi credentials for an access point the same document marks NOT SUPPORTED

**Logged:** 2026-08-24 (S131) · **Platform:** Spec / public docs · **Severity:** MEDIUM

### Symptom
§12.2 step 9 instructs every new user: *"Connect to WiFi `d3kOS` (password: `<REDACTED — see spec §12.2>`)"*.

The DEFAULT CREDENTIALS table on page 1 of the **same document** lists that AP struck through and
marked **"❌ NOT SUPPORTED"**. So the flashing guide tells users to join a network the spec says does
not exist, using a password the spec publishes.

### Why this is not merely cosmetic
The same credential pair is live in `docs/INSTALLATION.md` on the `d3kOS` repo `main` branch, alongside
the SSH/desktop default account and its documented password (redacted here; see
`docs/INSTALLATION.md`) plus passwordless sudo. If that repo is made public again,
anyone within WiFi range of a default install has a documented path to root. **That is a product
decision, not a doc edit** — recorded here so it is not lost.



### OPERATOR EXEMPTION — S131 2026-08-24

**The default password is an accepted exception.** Operator decision, recorded so no future session re-raises it as a credential violation. The `d3kos` default account password and the WiFi AP password are exempt from the "no real credentials in the repo" rule and from the pre-commit scanner's intent.

**What remains open in this entry is NOT the credential — it is the contradiction:** §12.2 step 9 directs users to join an access point that the DEFAULT CREDENTIALS table on page 1 of the same document marks "❌ NOT SUPPORTED". One of the two is wrong, and a new user following the flashing guide is sent to a network that may not exist. That is a correctness defect regardless of the credential exemption.

### Fix Required
1. Reconcile §12.2 step 9 with the page-1 table — establish which is correct (done S131: flagged `[VERIFY]`, not silently deleted).
2. Establish what first-boot network access actually is, and document that instead.
3. ~~Operator decision on default credentials~~ — **CLOSED by the S131 exemption above.** No action.

### Related
BUG-78 (image ships credentials), BUG-58/59 (credential exposure class)

---

## BUG-81 — Setup wizard and the public CX5106 guide both instruct an 8-switch DIP layout that does not exist on the hardware

**Logged:** 2026-08-24 (S132) · **Platform:** Pi dashboard (setup wizard) + public GitHub docs
· **Severity:** **HIGH** — every d3kOS user with a CX5106 is told to configure their gateway
wrongly, and the incorrect guide is already public on `main` and linked twice from the README
· **Status:** `[~]` PARTIAL — lab Pi DONE; P2/P3 blocked on operator APPROVED for GitHub push.
  - **P1 FIXED + VERIFIED:** `setup.html` Step 5 rewritten — 7+2 block model, ratio tables, empirical fallback, Matsutec. **13/13 tests GREEN on lab Pi (commit ba0ec7f4 2026-08-25).**
  - **P4 FIXED:** Actisense→Matsutec in dropdown + ctxTitle; "(8 switches)"→"(7 switches)"; "Row 1"→"Block A".
  - **Step 0 DONE:** `doc/CX5106_CONFIGURATION_GUIDE.md` corrected (local-only); superseded original preserved.
  - **AODA FIXED:** `font-size: 18px` added to `.dip-block`, `.dip-switches`, `.dip-sw`, `.dip-why`, `.dip-install`, `.dip-context` — T11 GREEN.
  - **P2 OPEN:** `docs/CX5106_CONFIGURATION_GUIDE.md` on `origin/main` — needs explicit operator APPROVED.
  - **P3 FIXED S140 2026-09-01:** `doc/CX5106_USER_MANUAL.md` line 53 — corrected to two-block model (Block A 7 switches RPM ratio, Block B 2 switches); ASCII diagram updated to match.

### Symptom

The setup wizard's Step 5 ("Gateway Configuration") computes and displays CX5106 DIP switch
settings for the user to copy onto their hardware. The settings it produces do not correspond to
the device's actual switches. A user who follows the wizard sets their gateway to a configuration
that cannot be correct, because the switches the wizard describes do not exist.

The same incorrect model is published in `docs/CX5106_CONFIGURATION_GUIDE.md` on the public `main`
branch, which the README links from two places.

### Root cause

**A fabricated hardware model was written once from inference and carried forward into three
artifacts and a live wizard without ever being checked against the manufacturer's leaflet — a scan
of which has been sitting in this repo the whole time at
`assets/manuals/CX5106_10125_manual.pdf`.**

The actual hardware, read from leaflet sheets `D2026-A` / `D2026-B` and the device label:

- **Block A — 7 positions.** Not seven settings. One binary field holding the **RPM speed ratio**.
  Switch 1 is the LSB; `ratio = 1 + (sw1x1 + sw2x2 + sw3x4 + sw4x8 + sw5x16 + sw6x32 + sw7x64)`.
  Verified against all 16 rows the leaflet prints in full (ratios 1–16) and the 125–128 boundary
  rows. No exceptions.
- **Block B — 2 positions, physically separate.** Switch 1 = level-sender standard
  (OFF `0–190 Ω` European / ON `240–33 Ω` American, global to all tank inputs). Switch 2 = engine
  position (OFF PORT / ON STBD).

What the wizard asserts instead (`setup.html` lines 1237–1248):

```
/* Row 1 - 8 switches (Engine Configuration)
 *   SW1-2 : Engine instance  00=single/port  10=starboard
 *   SW3-4 : RPM sensor type  00=alternator W-terminal
 *   SW5-6 : Cylinder count   cylinderMap below
 *   SW7   : Stroke type      0=4-stroke  1=2-stroke
 *   SW8   : Gear ratio       0=1:1 direct drive
 *
 * Row 2 - 2 switches (Regional)
 *   SW1   : Tank sender  1=North America (240-33Ohm)  0=Europe (0-190Ohm)
 *   SW2   : Position     0=primary/port  1=starboard
 */
```

`buildDIPRow1()` (line 1253) returns an **8-element array for a 7-position switch**. The RPM
sensor type, stroke type, and gear ratio fields have no counterpart in the hardware. Cylinder
count is not a switch field at all — cylinders map to a *ratio* via the leaflet's §6.1 lookup
table, which is then encoded in binary across all seven positions.

**Of the 10 mappings the wizard defines, 2 are correct** — both on Block B (sender standard and
PORT/STBD). Every claim about Block A is wrong.

### Demonstration

Reference boat: MerCruiser 454 MAG MPI — 8-cylinder, 4-cycle, inboard gasoline.

| | Block A switches |
|---|---|
| Leaflet §6.1 → ratio 4 → encode | `ON ON OFF OFF OFF OFF OFF` |
| Wizard output (`cylinderMap['8'] = [0,1]` on SW5–6) | `OFF OFF OFF OFF OFF ON OFF OFF` |

They agree on **no position**, and the wizard emits one more switch than the device has. Ratio 4 is
one of the rows the leaflet prints in full, so this is confirmed against the printed table and not
only against the derived formula.

### Four parts

| Part | Defect | Location |
|---|---|---|
| **P1** | Wizard Step 5 computes and displays the 8-switch model | `deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/setup.html` lines 1237–1305, 1348–1361 |
| **P2** | **PUBLIC** — same model published and README-linked twice | `docs/CX5106_CONFIGURATION_GUIDE.md` on `origin/main` (525 lines); README lines 108 and 127 |
| **P3** | Same model stated in prose | `doc/CX5106_USER_MANUAL.md` line 53 — *"The CX5106 has 8 switches arranged in a row."* |
| **P4** | Device attributed to Actisense; the label plate carries **no brand** | `setup.html:796` (`<option>`), `setup.html:1328` (heading) |

On **P4**: the plate reads `CX5106  08221` with a CE mark and a recycling mark only. The same
wizard separately and correctly offers the Actisense **EMU-1** as a different gateway, so the two
were conflated. **The maker is already on record: `project_cx5106_status.md` names **Matsutec**,
established by S119 web research. So the fix is to replace "Actisense" with **Matsutec**, not to
mark it unknown.** `Uncertainty flag: Matsutec was not re-verified this session and the label plate
carries no brand, so it cannot be confirmed from the hardware in hand — it is a prior session's
sourced finding.` Separately, the "Pangoo" branding on a neighbouring N2K device (BUG-31) was
explicitly **not** confirmed as the CX5106's maker.

**Also from that S119 record — a spec discrepancy worth resolving during the P1 rewrite:** vendor
spec blurbs quote a speed-ratio range of **1–200**, while the leaflet's own §6.2 heading says
**1~127** and its 7-position switch can only express 1–128. If some variant really supports 200,
it cannot do so with seven binary positions. Treat 1–127 as authoritative for this unit.

### Fix path

1. **Publish** `docs/CX5106_DIP_SWITCH.md` (written S132 — teaches a first-time reader to derive
   and verify the setting from their own leaflet; includes the complete 1–127 ratio table the
   leaflet abbreviates). This replaces the one-line `hold` placeholder currently at that path on
   `main`.
2. **Add README links** to the new document.
3. **Rewrite wizard Step 5 (P1)** to the ratio model: collect engine type → look up ratio → encode
   to 7 positions → render Block A and Block B separately. Note the wizard already collects
   cylinders, cycle/fuel type and tank-sender standard, so no new input fields are needed.
4. **Correct or retire P2 and P3.** P2 is the priority — it is public and README-linked.
5. **Remove the Actisense attribution (P4).**

⚠ **P2 and steps 1–2 are PUBLIC-facing changes to `github.com/SkipperDon/d3kOS`. They require
explicit operator approval in-session before any GitHub change, per the standing deployment rule.**

### Verification evidence

- **PHOTOGRAPHIC CONFIRMATION on this project's own hardware.**
  `assets/images/cx5106_10125.png` is a photograph of an opened CX5106 and it shows the two-block
  layout directly: an upper blue block marked `ON` / `DIP` with positions numbered **1 2 3 4 5 6 7**,
  and a separate lower blue block marked `ON` with positions numbered **1 2**. Seven and two. Not
  eight in one row.
  **The wrong guide embeds this photograph.** `docs/CX5106_CONFIGURATION_GUIDE.md` references it at
  lines 23 and 332 under the heading "Physical DIP Switch Location — Visual Reference", directly
  beneath text asserting an 8-switch single row. The document has been carrying its own refutation
  since it was written, and the image links were broken (`../../assets/...`, resolving outside the
  repository), so the photograph never rendered and the contradiction was never visible to a
  reader. **Image paths corrected to `../assets/...` S132** in
  `doc/CX5106_CONFIGURATION_GUIDE.md` (×2) and `doc/CX5106_USER_MANUAL.md` (×1).
- Leaflet sheets `D2026-A` (spec, wiring, terminal label) and `D2026-B` (§6 RPM speed ratio),
  supplied by the operator as AVIF images 2026-08-24 and independently cross-checked against
  `assets/manuals/CX5106_10125_manual.pdf` (same two sheets, higher resolution).
- Encoding verified against every fully-printed row of the leaflet's table. Predict-and-check
  performed at ratio 13 (`switches 3,4`) and ratio 125 (`switches 3,4,5,6,7`) — both match.
- Terminal list independently validated: 4 sensor inputs on the left block + 9 on the right = 13,
  matching the leaflet's §2.2 statement "Up to 13 sensors can be collected".

### Not yet established

- `Uncertainty flag: whether the wrong ratio contributes to BUG-14` (CX5106 present at source 106,
  heartbeat PGN 126993 only, zero data PGNs). A wrong ratio would produce a **wrong RPM value**,
  not the **absence** of data PGNs, and would not explain the missing oil/temperature/fuel PGNs
  which do not depend on the ratio at all. **Do not record this as BUG-14's root cause.** Setting
  the ratio correctly is cheap to do while the enclosure is open; re-observe the bus for ≥130 s
  afterwards.
- `Uncertainty flag: the direction in which the ratio scales displayed RPM is not documented in the
  leaflet` and was not determined. The published guide therefore tells the reader to test both
  directions rather than asserting one.
- `Uncertainty flag: the S101 record of the fitted unit's switches ("SW1=ON, SW2=OFF, SW3=ON,
  SW6=ON") cannot be interpreted now that two blocks are known to exist` — it predates that
  discovery and does not say which block it refers to. If those four are Block A they encode ratio
  38 against a required 4, but that reading is an assumption. Verify against the physical unit.
  **The photograph disagrees with that record.** In `assets/images/cx5106_10125.png` only Block A
  position 1 is set toward `ON`; positions 2–7 all appear set away from it, which would be
  **ratio 2**, not the ratio 38 the S101 note implies. `Uncertainty flag: this is a reading of a
  photograph of unknown date at limited resolution, and the unit photographed may not be the fitted
  unit. It is not a substitute for inspecting the hardware.` Block B's absolute positions cannot be
  determined from the photograph at all — both of its switches are clearly in the *same* state as
  each other, but which state is not legible. **Neither Block A ratio 2 nor ratio 38 matches the
  ratio 4 required for an 8-cylinder 4-cycle engine, so on either reading the fitted unit needs
  changing.**

### Process note

This is the same failure mode as **BUG-08** (five fixes built on an untested docstring claim) and
**BUG-78** (a bug logged from `MASTER_SYSTEM_SPEC` §12.1 describing a script that does not exist):
**a plausible written premise was trusted in place of the primary source.** In this instance the
primary source was already in the repository.

### Related

BUG-14 (CX5106 no data PGNs), BUG-31 (false 0% fuel — closed; Block B switch 1 is a separate
mechanism worth checking while the case is open), BUG-08 and BUG-78 (same premise-over-source
failure mode)

### Documents

- `deployment/docs/CX5106_CONFIGURATION_FROM_MANUAL.md` — internal record: manual-derived truth
  plus the full artifact audit (S132)
- `docs/CX5106_DIP_SWITCH.md` — public guide, written S132, **not yet published**

---
## BUG-82 — `boatlog-export-api.py` binds `127.0.0.1`; all four :8095 endpoints are unreachable from any remote browser

**Logged:** 2026-08-28 (S135) · **Platform:** Pi (lab Pi `192.168.1.237`, confirmed live)
· **Severity:** **MEDIUM** — three user-facing Boat Log features silently fail whenever the dashboard
is opened over the LAN; the failures are invisible because every caller discards the error
· **Status:** `[x]` **FIXED S136 2026-08-28 — Option B (proxy via app.py). 3 proxy routes added: GET /api/boatlog/status, POST /voice-note, POST /export. BOATLOG_API='' in boat-log.html. refreshStatus() checks r.ok → visible error on 503. T1 PASS (78 entries from remote). T5 PASS (visible 'unavailable (HTTP 503)').**

### Symptom

Opening the Boat Log page from any browser that is not on the Pi itself: the service-status indicator,
voice-note upload, and CSV export all fail. No error is shown to the operator.

### Evidence — live, 2026-08-28

```
$ ss -tlnp | grep 8095
LISTEN 0  128  127.0.0.1:8095  0.0.0.0:*  users:(("python3",pid=1016,fd=3))
```

Source: `opt/d3kos/services/boatlog/boatlog-export-api.py:350` — `app.run(host='127.0.0.1', port=PORT)`.

Callers build the URL from the browser's own hostname, so they never reach a loopback-bound socket:

- `templates/boat-log.html:316` — `var BOATLOG_API = 'http://' + window.location.hostname + ':8095';`
- used at `:447` `/api/boatlog/status`, `:551` `/api/boatlog/voice-note`, `:591` `/api/boatlog/export`
- `static/js/boatlog-engine.js:16` — same construction

### Root cause

The Flask app binds loopback while every consumer addresses it by LAN hostname. This is the **server
side** of the BUG-46/48 defect class: BUG-46/48 removed hardcoded `localhost` from **front-end** code
because it resolves in the browser. Nobody then checked whether the **services** those pages call were
actually listening on an address the browser could reach. `boatlog-export-api.py` was not.

⚠ **`app.py` binding localhost is correct and unrelated** — that is server-side code making outbound
calls. This entry is about an inbound listener. Do not conflate them.

### Why it went unnoticed

Every caller swallows the failure:
`boat-log.html` uses bare `.catch()` chains, and `boatlog-engine.js:89` is an explicitly empty
`.catch(function () { /* API unavailable — localStorage copy already saved */ })`.
A connection refusal is indistinguishable from success. Same silent-failure shape as BUG-54.

### Fix required

1. Bind `0.0.0.0` (matching the other d3kOS service listeners), **or** proxy `/api/boatlog/*` through the
   dashboard on :3000. ⚠ **Binding wider is a security-surface change** — decide deliberately, and check
   it against the BUG-66/BUG-74 credential posture before doing it.
2. Replace the empty `.catch()` handlers with ones that surface the failure. A silent catch is what made
   this invisible for months.
3. Verify the Pi's own kiosk browser: if it loads the dashboard via `localhost:3000` these calls work
   locally today, which would explain why the feature ever appeared to function. `Uncertainty flag: the
   kiosk URL was not read this session.`

### Scope note

**BUG-24's Option A spec deliberately routes around this** by serving `GET /api/boatlog/entries` from
`app.py` on :3000 (same origin) rather than :8095. BUG-24 is **not** gated on BUG-82.

### Related

- **BUG-46 / BUG-48** — the front-end half of the same defect class
- **BUG-54** — silent failure caused by a swallowed diagnostic
- **BUG-24** — found during its investigation; routes around this one

---

## BUG-83 — `services/ai/alert_watcher.py` is a stale divergent copy of the `alert_watcher.py` systemd actually runs

**Logged:** 2026-08-28 (S135) · **Platform:** Pi (canonical tree + lab Pi)
· **Severity:** **MEDIUM** — a second, older copy of a live service sits in the tree with no marking;
the next person to edit "the alert watcher" has a 50% chance of editing the one that never runs
· **Status:** `[x]` **FIXED S136 2026-08-28 — stale `services/ai/alert_watcher.py` (v0.9.5, 338 lines) deleted from canonical tree. `services/alert_watcher.py` (v0.9.6, 405 lines) is the live superset. Commit be4485c9.**

### Symptom

Two files named `alert_watcher.py` exist in the canonical tree with different contents:

| Path | Version header | Lines | md5 | Runs? |
|---|---|---|---|---|
| `opt/d3kos/services/alert_watcher.py` | 0.9.6 | 405 | `2e94fe79…` | **YES** |
| `opt/d3kos/services/ai/alert_watcher.py` | 0.9.5 | 338 | `48b07c5e…` | no |

`etc/systemd/system/d3kos-alert-watcher.service` sets `WorkingDirectory=/opt/d3kos/services` and
`ExecStart=/usr/bin/python3 alert_watcher.py` — so the **root** copy is the live one.

### Root cause

The root copy is a **strict superset** of the `ai/` copy. `diff` shows the `ai/` version is missing:

```
USER_PREFS_FILE = Path('/opt/d3kos/config/user-preferences.json')
def load_alert_prefs()     — reads alert_prefs from user-preferences.json
def local_prefs_allow()    — applies enabled_types / quiet_hours locally
```

Nothing exists in `ai/` that is absent from root. So `ai/alert_watcher.py` is simply the older file, left
behind when the service gained local alert-preference handling.

⚠ **This is the same shape as the `cloud_agent.py` / `ota_upgrade.py` duplication that Phase 0.4
(BUG-28 Step 1) resolved** — 719-line superset vs 630-line copy, systemd running one of them. **Phase 0.4
did not catch this third instance.** The de-duplication pass was scoped to two named files rather than
driven by a search for the pattern.

### Fix required

⛔ **Promote, do not prune** — the standing trap from Phase 0.4. Confirm the superset relationship holds
at the moment of the fix (re-run the `diff`, do not trust this entry), then remove the stale `ai/` copy
in its own commit. **Deleting the wrong one destroys the only copy of `load_alert_prefs` and
`local_prefs_allow`.**

Then: **search for further instances rather than fixing this one and stopping.** Phase 0.4's method is
what let this survive. Run a basename-collision scan across `opt/d3kos/services/` and log whatever it
finds — do not cap the audit and call it coverage (STANDING TRAP 2).

### Verification

- `release-state.sh` reports `ai/alert_watcher.py` as tracked, so removing it changes `MANIFEST.md5` —
  regenerate as part of the change.
- Confirm `d3kos-alert-watcher.service` is still `active` after the removal.

### Related

- **BUG-28 Step 1 / Phase 0.4** — the same defect, twice, already fixed for `cloud_agent.py` and
  `ota_upgrade.py`
- **BUG-36** — a deploy that silently regressed a file, the failure mode duplicate copies enable

---
## BUG-84 — Unauthenticated one-shot scratch scripts left live on the staging web root

**Logged:** 2026-08-28 (S135) · **Platform:** HostPapa staging · **Severity:** **MEDIUM**
· **Status:** `[x]` **FIXED S135 2026-08-28 — both files deleted with operator approval.**

### Symptom

Two S134-cont one-shot tools were still present and publicly reachable ten days after use:

| File | Size | What it did |
|---|---|---|
| `staging/d3k-rawcheck.php` | 617 B | `file_get_contents('wp-config.php')`, regex-extracts `DB_NAME`/`DB_USER`/`DB_PASSWORD`, opens a PDO connection, `echo`s the `active_plugins` option. **No authentication.** |
| `staging/d3k-deactivate.php` | 1,039 B | Plugin-deactivation script. **No authentication.** Never executed by this session. |

### Why it matters

`d3k-rawcheck.php` is a credential-reading database client on a public URL. It happened to return HTTP
500 with an empty body because `$table_prefix` failed to parse (`Undefined array key 1`) and the query
hit a non-existent `options` table — and because `display_errors` is off. **Both of those are luck, not
controls.** One working query and it prints database internals to anyone who requests it.

⚠ `d3k-deactivate.php` on a public URL with no auth is the more direct risk: the plugin it would
deactivate is `d3kos-device-auth`, which is the BUG-63 registration gate. **A deactivation endpoint for
your anti-bot control, reachable by bots.**

### Root cause — a process gap, not a code defect

S134-cont's SESSION_LOG records the one-shot tools as *"committed + deleted"*. Three were
(`republish-register.php`, `probe-register-page.php`, `cleanup-botnet-accounts.php`). **These two were
not, and nothing checked.** The deletion was recorded as done because it was intended, not because it
was verified — the same failure shape as BUG-57's S121 "primary vector closed" entry and BUG-72's
"never deployed" record.

### Fix applied — S135 2026-08-28

Operator gave explicit in-session approval. Both files backed up byte-identically **before** deletion to
`.aao-backups/20260828_112110_S135/mirrored/staging/`, md5-verified against the remote copies, then
deleted over FTPS.

```
d3k-rawcheck.php    617 B  md5=709012b92806d17ede3fab60a5fd0361
d3k-deactivate.php 1039 B  md5=3e29054205356ca14a52ae1acf156bbc
```

Post-delete verification: FTP `LIST staging` → no `d3k-*` files remain; HTTP GET of both paths → 404.

### Prevention

⚠ **A one-shot tool is not deleted until a listing proves it.** Any future session that uploads a
temporary script must end by listing the directory and pasting the output — not by stating the file was
removed. Add this to the deploy close sequence.

### Related

- **BUG-57** — the same class of exposure this repo already suffered
- **BUG-85** — found in the same sweep

---

## BUG-85 — `/staging/.htaccess` is a copy of the live site's; every staging page-route is served or redirected by PRODUCTION

**Logged:** 2026-08-28 (S135) · **Platform:** HostPapa staging + live
· **Severity:** **HIGH** · **Status:** `[x]` **FIXED + VERIFIED — S136 deployed new `.htaccess`; S137 2026-08-31 full verification passed.**

### Fix applied (S136 + S137)

S136 deployed corrected `/staging/.htaccess`: `RewriteBase /staging/`, `RewriteRule . /staging/index.php [L]`.
S137 found that after the fix, staging ran its own WordPress instance for the first time, and `siteurl` in
`atmyb197_wp5888` had been set to `https://atmyboat.com/staging/staging`. Corrected to
`https://atmyboat.com/staging` via phpMyAdmin. Staging `.htaccess` regenerated via Settings → Permalinks → Save.

⚠ **Correction to the "do not fix siteurl" note below:** that warning was based on S135 pre-fix probes
where `siteurl` was correct. After the S136 fix, the siteurl legitimately required correction — these are
two different system states. The warning still applies to the S125/S126 era edits to `wpax_options`.

### Verification — 2026-08-31

```
GET https://atmyboat.com/staging/about/   -> 200, assets all /staging/wp-content/  ✓
GET https://atmyboat.com/staging/wp-admin/ -> 302 -> /staging/wp-login.php (no doubling) ✓
staging wp-admin navigation: working ✓
```

### Symptom — proven, 2026-08-28

```
GET https://atmyboat.com/staging/about/   -> 301 -> https://atmyboat.com/about/     (LIVE)
GET https://atmyboat.com/staging/blog/    -> 301                                     (LIVE)
GET https://atmyboat.com/staging/<random>.php
      -> 404 page whose assets are ALL at the live root:
         18x https://atmyboat.com/wp-content/...   0x https://atmyboat.com/staging/wp-content/...
         byte-comparable to the live root 404 (40,024 B)
```

`/staging/` itself works (200, 72 KB, correct `/staging/` asset URLs) because `index.php` is a **real
file**. Everything that is not a real file or directory leaves staging entirely.

### Root cause

`/staging/.htaccess` is a **verbatim copy of the live site's**, not one generated for a subdirectory
install:

```
39: RewriteBase /                    <- must be /staging/
43: RewriteRule . /index.php [L]     <- must be /staging/index.php
57: php_value auto_prepend_file '/home/atmyb197/public_html/wordfence-waf.php'   <- LIVE's WAF
```

With `RewriteBase /`, any non-file/non-dir request under `/staging/` is rewritten to the **live**
`index.php`. Live WordPress then canonical-redirects `/staging/about/` to `/about/`.

⚠ **`siteurl`/`home` are NOT the cause and must not be "fixed" again.** They are correct: the staging
homepage renders zero `staging/staging` occurrences and every asset resolves to `/staging/`.
`wp-config.php` defines neither `WP_SITEURL` nor `WP_HOME`. **Previous sessions edited `wpax_options`
chasing this symptom — do not repeat that.**

### Consequence — read this before trusting any past "verified on staging" claim

**Any test performed against a staging URL with a pretty permalink was executed against production, or
redirected to it.** That includes anything reached via `/staging/register/`, `/staging/app/`,
`/staging/community/` and similar. Direct `.php` file paths under
`/staging/wp-content/themes/...` are unaffected (they are real files) — which is why the S134-cont
endpoint deploys did behave sensibly.

`Uncertainty flag: the /staging/wp-admin/ -> /staging/staging/wp-login.php doubling is NOT yet explained
by this. wp-admin IS a real directory, so the rewrite should not fire on it. Cause unresolved — do not
assume this entry covers it.`

### Fix required

1. Regenerate `/staging/.htaccess` for a subdirectory install: `RewriteBase /staging/` and
   `RewriteRule . /staging/index.php [L]`. Easiest safe route is WordPress itself — Settings →
   Permalinks → Save, from **staging's** wp-admin (blocked today; see the uncertainty flag).
2. Point `auto_prepend_file` at staging's own `wordfence-waf.php`, or remove it.
3. ⚠ **Take a backup of `.htaccess` first.** A bad rewrite rule takes the whole path down.
4. Re-test with the three probes above. **`/staging/about/` returning staging content is the pass
   condition** — a 200 alone is not, because live returns 200 too.

### Related

- **BUG-61** — its remaining scope; BUG-61's front-end half is fixed, this is what is actually left
- **BUG-62** — closed NOT A BUG in S131 as a misdiagnosis of the `/staging/staging/` URL; consistent
- **BUG-84** — found in the same sweep

---

## BUG-86 — `d3kos-device-auth` plugin fataled every staging page load on 2026-08-25 (resolved before logging)

**Logged:** 2026-08-28 (S135) · **Platform:** HostPapa staging
· **Severity:** was CRITICAL while live · **Status:** `[x]` **RESOLVED BEFORE LOGGING — recorded for the
incident history, not as open work.**

### What happened

`staging/error_log`, 2026-08-25 18:49 UTC:

```
PHP Fatal error: Uncaught Error: Failed opening required
'/home/atmyb197/public_html/staging/wp-content/themes/twentytwenty/mobile/device-auth.php'
  in .../plugins/d3kos-device-auth/d3kos-device-auth.php:23
Stack: wp-settings.php(597) -> wp-config.php(102) -> wp-load.php(50)
       -> wp-blog-header.php(13) -> index.php(17)
```

The require resolved to the **parent** theme (`twentytwenty`) while `device-auth.php` was deployed to the
**child** (`twentytwenty-child`). Because the plugin loads from `wp-settings.php`, **every page load of
staging fataled** for the duration.

### Why it is not open

Verified 2026-08-28 by reading both deployed copies over FTPS:

| | Size | Directory function |
|---|---|---|
| staging plugin | 11,376 B | `get_stylesheet_directory()` ✅ |
| live plugin | 11,376 B | `get_stylesheet_directory()` ✅ |

Byte-identical and correct on both. The fatal came from an earlier build during the S134-cont deploy
iteration (`44a6e415` — *"device-auth.php fixed for standalone PHP context"*) and no longer reproduces.
Staging currently returns HTTP 200.

### What this leaves open — a question, not a defect

⚠ **Is the plugin currently ACTIVE on staging, or was it deactivated to stop the fatal?**
`d3k-deactivate.php` was created at 14:49 on the same day (see BUG-84), which suggests deactivation was
at least attempted. **If it is inactive, BUG-66 Phase A is not running on staging while the records say
it is.** Answering needs the `active_plugins` option out of `atmyb197_wp5888` — carry it into the
BUG-66 verification, do not assume either way.

### Documentation corrections established while investigating

Read directly from the two `wp-config.php` files, 2026-08-28:

| | Recorded | Actual |
|---|---|---|
| Staging DB | `atmyb197_wp302` | **`atmyb197_wp5888`** (prefix `wpax_`) |
| Live DB | `atmyb197_wp59874` | `atmyb197_wp59874` ✅ (prefix **`wpax_`** — was "unverified") |

⚠ **This explains the "`atmyb197_wp302` credentials are BROKEN" note in MEMORY.md — the credentials are
not broken, the database name is wrong.** The two databases are separate; there is no shared-DB problem.

### Related

- **BUG-66** — the plugin this concerns; the activation question belongs to its verification
- **BUG-84 / BUG-85** — same sweep

---
## BUG-87 — My Account actions are unthrottled, and account deletion does not re-prompt for the password

**Logged:** 2026-08-28 (S135) · **Platform:** atmyboat.com (live) · **Severity:** **LOW — hardening**
· **Status:** `[x]` **FIXED S136 2026-08-28 — R1: 5-failure transient throttle (15 min) on change_password. R2: wp_check_password + pw_delete input on delete_account. Wordfence confirmed does NOT protect this handler. Deployed live. 4/4 PASS.**

**File:** `wp-content/themes/twentytwenty-child/page-my-account.php` (live md5 `400fa44e…`).
⚠ Edit the **Helm-OS** copy at `deployment/features/auth-pages/php/page-my-account.php` — the
`atmyboat-forum` copy is stale (BUG-64 audit).

---

### R1 — No throttling on any account action

`change_password`, `change_email`, `delete_account` and the data export accept unlimited POSTs from a
valid session. Nothing records attempts, and there is no `transient`, cooldown or counter in the file.

**Concrete failure:** `:92` calls `wp_check_password( $pw_cur, … )` on every submission with no
back-off. **An attacker who has a session but does not know the password can brute-force the
current-password field through the account page.** That matters because the current password is the
gate on `change_password` — guessing it lets the session be converted into permanent account takeover
(change password → change email) rather than access that ends when the cookie expires.

`Uncertainty flag: Wordfence may already throttle these POSTs at the HTTP layer. This was NOT verified —
confirming it means submitting repeated failed passwords against the live site, which was not done.
Check the Wordfence rate-limiting configuration before writing any code; the fix may already exist one
layer up.`

**Fix options, cheapest first:**
1. Confirm Wordfence's existing rate limiting covers authenticated POSTs to this page — possibly no code.
2. A per-user transient counter: N failed `wp_check_password` attempts in M minutes → refuse and log.
3. ⚠ **Fail closed but do not lock the user out permanently** — a self-service account page that can be
   locked by an attacker is a denial-of-service on the legitimate owner. Time-boxed back-off only.

### R2 — `delete_account` does not require the current password

`:149-158` requires a valid action-scoped nonce and the literal string `DELETE MY ACCOUNT`. That is
sound against CSRF and against accidents. It is **not** sound against an unattended logged-in session:
anyone at the keyboard can type eleven words and destroy the account.

Mitigating factor already present: `:157` `wp_delete_user( $user_id, 1 )` **reassigns content to the
admin** rather than deleting posts, so the blast radius is the account, not its contributions.

**Fix:** require `wp_check_password()` on `delete_account`, exactly as `change_password` already does at
`:92`. The pattern is in the same file — reuse it, do not invent a second one.

---

### Tests

| # | Test | Pass condition |
|---|---|---|
| T1 | Submit `change_password` with a wrong current password N+1 times | request N+1 is refused/backed-off, not evaluated |
| T2 | Legitimate user changes password successfully after a wrong attempt | **not locked out** — proves R1's fix does not become a self-DoS |
| T3 | `delete_account` with correct confirmation string but wrong password | **rejected** |
| T4 | `delete_account` with correct confirmation string and correct password | succeeds; content reassigned to user 1 |
| **T5** | **Negative: remove the throttle, re-run T1** | T1 **fails** — proves the guard bites (STANDING TRAP 6) |

⚠ **T2 is the one that matters most.** A throttle that locks the real owner out is worse than no throttle.

### Definition of done

- [ ] Wordfence's existing coverage checked **first** — do not write code that duplicates it
- [ ] T1–T5 written before the fix; T1 and T3 observed failing pre-fix
- [ ] Edited in the Helm-OS copy; the stale `atmyboat-forum` copy reconciled or removed
- [ ] Deployed to live only with explicit operator `APPROVED`

### Related

- **BUG-64** — closed NOT A BUG; this is its residual
- **BUG-69** — admin 2FA, the adjacent control that is already done

---
## BUG-88 — 32 production PHP files exist nowhere in the repo, and a dormant parent-theme include waits to fatal

**Logged:** 2026-08-28 (S135) · **Platform:** atmyboat.com (live) + `atmyboat-forum` repo
· **Severity:** **MEDIUM** — this is the measurable form of a root cause three other bugs already name
· **Status:** `[x]` **FIXED S136 2026-08-28 — Part 1: 38 unsourced files captured byte-identical in atmyboat-forum commit 718b97a. config.php excluded (live creds) → gitignored; ⚠ OPERATOR: rotate Stripe/Gemini/API keys. Part 2: inc/atmyboat-functions.php deleted from repo and HostPapa live. T6 PASS: site healthy.**

---

### Part 1 — The repo does not know what production runs

| | `mobile/*.php` count |
|---|---|
| `atmyboat-forum` repo | **44** |
| Production (FTP listing, 2026-08-28) | **76** |

**32 files are running in production with no source anywhere in the repo.** BUG-71 was one of them until
S135 (commit `13eebcbc`); the other 31 are still unsourced.

This is the concrete measurement of the root cause that **BUG-72**, **BUG-76** and
`PHASE3-server-canonical-tree.md` all describe in the abstract: *"There is no canonical tree, manifest,
or drift check for the HostPapa side."* The Pi side has `MANIFEST.md5` and `release-state.sh`. The
server side has nothing, and the gap is 32 files wide.

⚠ **Consequences already observed this session, not hypothetical:**
- **BUG-71** — a production file with no repo copy; the bug survived multiple sessions partly because
  there was nothing to read.
- **BUG-64** — three variants of `page-my-account.php` exist; the `atmyboat-forum` copy is **stale** and
  live matches the Helm-OS copy instead.
- **BUG-84** — two scratch files sat in production for ten days because nothing compares the server
  against a manifest.

⚠ **Do not "fix" this by copying production into the repo wholesale.** `PHASE3-server-canonical-tree.md`
Step 1 is explicit: **pull the deployed files down and diff them against the repo copies — assume
nothing.** Some repo copies are newer than production, some are older, and at least one production file
(`page-my-account.php`) matches a *different* repo than the theme repo. A blind copy would overwrite
good source with stale source.

**⚠ Also do not cap the audit.** The 76/44 figure is `mobile/` only. The rest of the child theme, the
plugins directory and the `app/` tree were not counted. Count them before claiming coverage
(STANDING TRAP 2).

### Part 2 — A dormant parent-theme include

`atmyboat-forum/wp-content/themes/twentytwenty-child/inc/atmyboat-functions.php:107`:

```php
require_once get_template_directory() . '/mobile/pair-device.php';
```

`get_template_directory()` returns the **PARENT** theme (`twentytwenty`). The file lives in the
**child**. If this line ever executes, it is an unconditional fatal on every page load — **exactly the
failure BUG-86 caused on staging on 2026-08-25.**

**It is currently dormant.** A grep of `functions.php` and `inc/` finds nothing that requires
`inc/atmyboat-functions.php`, so the line never runs. The live include is `functions.php:220`, which
correctly uses `get_stylesheet_directory()`.

**Fix:** either delete `inc/atmyboat-functions.php` if it is dead, or correct line 107 to
`get_stylesheet_directory()`. **Do not simply leave it** — a dead file containing a site-killing line is
one careless `require` away from an outage, and the same mistake has already fired once.

⚠ **Search for other instances before closing.** `get_template_directory()` used to reach a child-theme
file is now a known recurring error in this codebase (BUG-86, and this). Grep the whole theme for it and
log what turns up — do not fix these two and declare the class closed.

### Definition of done

- [ ] Every `mobile/*.php` in production diffed against its repo copy (or recorded as absent) — no blind copy
- [ ] The 31 remaining unsourced files brought under version control byte-identical, own commit
- [ ] Count extended beyond `mobile/` and the true total reported
- [ ] `inc/atmyboat-functions.php` deleted or line 107 corrected
- [ ] Repo-wide grep for `get_template_directory()` reaching child-theme paths; findings logged
- [ ] Feeds `PHASE3-server-canonical-tree.md` Step 1 — this bug is that spec's evidence base

### Related

- **BUG-71** — where this was found; one of the 32
- **BUG-86** — the parent-theme include error that actually fired
- **BUG-64** — stale repo copy of a live file
- **BUG-72 / BUG-76** — same root cause, different symptom

---
## BUG-89 — Three Pi→server destination URLs 404; OTA version checks have never resolved

**Logged:** 2026-08-28 (S135) · **Platform:** Pi canonical tree → atmyboat.com
· **Severity:** **HIGH** — one of the three is the OTA update path · **Status:** `[x]` **RESOLVED 2026-09-01 — all three URLs confirmed resolving: `version.php` → 200 (valid JSON manifest); `community-markers.php` → 405 (POST-only, correct); `community-get.php` → 200. `community-api.py` code already used correct full paths; bug record's URL table was incorrect.**
Found by completing **BUG-75 Step 2** (audit every destination URL against probe results, not the spec).

### The three, all confirmed 404 on 2026-08-28

| Source | URL | Result |
|---|---|---|
| `opt/d3kos/services/agents/agents/update_agent.py:47` `VERSION_URL` | `…/mobile/version.php` | **404** |
| `opt/d3kos/services/community/community-api.py:49,73` | `atmyboat.com/api/community/markers` | **404** |
| `opt/d3kos/services/cloud/cloud-link-api.py:66` `webhook_url` default | `atmyboat.com/api/notify` | **404** |

Control: `…/mobile/version-api.php` → **401**. The theme path resolves and the probe method is sound;
these three are genuinely absent.

---

### 1. `version.php` — the OTA path, and BUG-55 half-fixed it

Production has `version-api.php`, `version-heartbeat.php` and `version-registry.php`. **There is no
`version.php`.**

⚠ **BUG-55 corrected this line's HOST and left its FILENAME wrong.** BUG-55 Category B recorded:
*"`VERSION_URL` was hardcoded to staging, so OTA version checks were hitting the test site."* The fix
moved it from **the wrong site** to **the right site and a file that does not exist**. Same silent
failure, new address. The verifier `verify-bug55.sh` checks for the *string* `atmyboat.com/staging`; it
never checked that the resulting URL resolves.

**Almost certainly the reason no OTA has ever run.** `PHASE4-release-engineering.md` notes *"a real OTA
(BUG-35's fix has never executed — no OTA has ever run)"*. An update agent whose version check 404s
never discovers an update, so the download-and-apply path is never entered.

`Uncertainty flag: that causal link is an inference from two facts (the URL 404s; no OTA has run). It
was NOT confirmed by reading update_agent.py's error handling or the Pi's journal. Confirm before
recording it as the cause of BUG-35's untested state.`

**Fix:** determine which endpoint is intended — `version-api.php` (401, auth-gated, most likely) or
`version-registry.php` — then correct line 47. ⚠ **Do not guess between them; read what each returns
and what `update_agent.py` expects to parse.**

### 2. `/api/community/markers` — a FIFTH naming scheme

`community-api.py` calls a REST-style path that does not exist. This is **not** one of the three schemes
BUG-76 catalogued — it is a fifth, and it is the one the **Pi's own code** uses:

| # | Source | Name |
|---|---|---|
| 1 | `MASTER_SYSTEM_SPEC` §8.4.4 | `community-markers-post.php` / `-get.php` |
| 2 | `ARCH_SERVICE_MAP.md` | `community/markers.php` |
| 3 | **Production (authoritative)** | **`community-markers.php`** |
| 4 | `features/v0941-plan/php/` (design tree) | `community-markers-write.php` |
| 5 | **`community-api.py:49,73` (Pi, live code)** | **`/api/community/markers`** |

⚠ **BUG-76 must be widened: five schemes, not three — and the running Pi code matches none of them.**
Whatever canonical name is chosen, `community-api.py` has to change too. A doc-only fix leaves the Pi
still calling a 404.

### 3. `/api/notify` — a default that resolves to nothing

`cloud-link-api.py:66` uses `data.get('webhook_url', 'https://atmyboat.com/api/notify')`. The **default**
404s. It only bites when a caller omits `webhook_url` — which is exactly the BUG-55 Category A shape:
*"latent fallback defaults that resolved correctly only because a config key happened to be set."*

**Fix:** either point the default at a real endpoint or **remove the default and fail loudly** on a
missing `webhook_url`. ⚠ A silent fallback to a 404 is worse than a missing-key error.

---

### The pattern across all three

Every one fails **silently**: a 404 on a background POST produces no operator-visible symptom. Same
class as BUG-54 (five months of invisible export failures) and BUG-56 (a no-op string replace).

⚠ **`verify-bug55.sh` and `release-state.sh` both pass while all three are broken**, because both check
*text* and *file identity*, never *whether a destination resolves*.

**Recommended systemic fix:** a `verify-endpoints.sh` that extracts every `atmyboat.com/...` literal from
the canonical tree and asserts each returns something other than 404. Sequential requests only —
Wordfence treats a parallel sweep as a scanner (`PHASE3-server-canonical-tree.md` Step 2).

### Definition of done

- [ ] `update_agent.py:47` pointed at the correct, verified endpoint
- [ ] `community-api.py` aligned with BUG-76's canonical-name decision
- [ ] `cloud-link-api.py:66` default fixed or removed in favour of a loud failure
- [ ] `verify-endpoints.sh` written; **plant a known-404 and watch it fail** before trusting it
- [ ] BUG-35's "no OTA has ever run" re-assessed once the version URL resolves
- [ ] Lab Pi only; boat Pi out of scope per operator directive S135

### Related

- **BUG-75** — the audit that found these · **BUG-76** — widened to five naming schemes
- **BUG-55** — fixed the host, missed the filename · **BUG-35 / PHASE4** — the untested OTA
- **BUG-54 / BUG-56** — the same silent-failure class

---
## BUG-90 — The registration audit trail has never recorded anything: `$wpdb->prefix` applied to a deliberately unprefixed table

**Logged:** 2026-08-28 (S135) · **Platform:** atmyboat.com (LIVE) · **Severity:** **HIGH**
· **Status:** `[x]` **FIXED + DEPLOYED S136 2026-08-28 — `$wpdb->prefix` removed from `device-registration.php:121` and all related consumers. Table `amboat_registration_audit` is deliberately unprefixed per `device-auth-tables.sql:9-10`. Deployed to HostPapa live. Commit be4485c9. ✅ VERIFIED S139 2026-09-01 — live DB query confirmed `amboat_registration_audit` contains 1 row; table is receiving writes. Gap closed.**

**This is the detection control for a repeat of BUG-57, and it has never worked.**

### Evidence — live error log, `public_html/error_log`

```
[26-Aug-2026 04:34:39 UTC] WordPress database error
  Table 'atmyb197_wp59874.wpax_amboat_registration_audit' doesn't exist
  for query SHOW FULL COLUMNS FROM `wpax_amboat_registration_audit`
  made by require('wp-blog-header.php'), … include('/themes/twentytwenty-child/page-register.php'),
          amboat_registration_audit
```

Dated **one day after** BUG-63 Step 3 put the device-gated `/register/` live.

### Root cause — a one-line prefix mismatch

| Role | Location | Table named |
|---|---|---|
| **Creator** | `v0.9.9.4-server/sql/device-auth-tables.sql:47` | `amboat_registration_audit` — **unprefixed** |
| **Creator** | `plugins/d3kos-device-auth/d3kos-device-auth.php:108` (dbDelta) | `amboat_registration_audit` — **unprefixed** |
| **Plugin's own insert** | `d3kos-device-auth.php:192` | `$wpdb->insert('amboat_registration_audit', …)` — **unprefixed, CORRECT** |
| **Consumer — the defect** | `features/auth-pages/php/device-registration.php:121` | `$table = $wpdb->prefix . 'amboat_registration_audit';` → **`wpax_amboat_registration_audit`** |

The unprefixed convention is **deliberate and documented** — `device-auth-tables.sql:9-10`:
*"Table names do NOT use the WordPress prefix — they use the amboat_ namespace directly, consistent
with the existing amboat_devices table in version-heartbeat.php."*

**`device-registration.php:121` did not follow it.** One line, one `$wpdb->prefix`.

### Impact

`page-register.php` calls `amboat_registration_audit()` in three places — `:105` `redeem_fail`,
`:114` `wp_create_user_failed`, `:162` **`account_created`**. **Every call targets a table that does not
exist, so no registration event has ever been recorded.**

⚠ **BUG-57's root-cause list includes, verbatim: *"No audit trail or notification when accounts were
created."*** BUG-63 was built to close that hole. **The audit half of it has been inert since the day it
went live.** If a second botnet ran tomorrow, the record would look exactly as empty as it did in June.

**Registration itself still works** — `$wpdb->insert()` on a missing table returns `false` and logs;
it does not throw, and the call sits after `wp_create_user()`. The `/register/` page returns 200 and
renders the gate (verified S135). **The failure is silent and affects only the audit trail** — which is
the worst place for it to be silent, because the audit trail is what you would consult to find out
whether anything went wrong.

Same class as BUG-54 (five months of invisible failures) and BUG-89 (three 404s nobody sees).

### Fix

Delete `$wpdb->prefix .` from `device-registration.php:121`.

⚠ **Before that, confirm which table actually exists in the live database.** Commit `904a4f47` claims
*"6 device auth tables created in live DB"*, which implies the **unprefixed** `amboat_registration_audit`
is present — but that has not been read. Two possibilities, opposite fixes:

- **Unprefixed table exists** → remove the prefix from the consumer. One-line fix.
- **Neither table exists** → the dbDelta never ran or failed; fix the creation path first. A consumer
  fix alone would then still write nowhere.

`Uncertainty flag: the live database was NOT queried this session. The error log proves only that the
PREFIXED table is absent. Do not apply the one-line fix until the unprefixed table is confirmed present
— otherwise the audit trail stays broken and the bug looks closed.`

⚠ **Audit every other consumer of these tables for the same mistake before closing.** `amboat_devices`,
`amboat_device_enrolments`, `amboat_registration_codes` and `amboat_device_accounts` share the
unprefixed convention. Grep for `$wpdb->prefix . 'amboat_` across both repos — do not fix this one and
declare the class closed (STANDING TRAP 2).

### Verification

- [ ] Confirm from the live DB which of the two table names exists
- [ ] Fix, then register one test account and **read the audit row back** — not "no error in the log"
- [ ] Grep both repos for `$wpdb->prefix . 'amboat_` and fix every hit
- [ ] Re-check `public_html/error_log` afterwards for a clean run

### Related

- **BUG-57** — the breach whose root cause included the absent audit trail
- **BUG-63** — the fix this defect silently hollows out
- **BUG-66** — created these tables; its Phase A dbDelta is the creator side
- **BUG-54 / BUG-89** — the same silent-failure class

---
## BUG-91 — The entitlement authority fails OPEN to Tier 1, and ignores the tier-audit fields the Pi sends it

**Logged:** 2026-08-28 (S135) · **Platform:** atmyboat.com (LIVE `data-ingress.php`)
· **Severity:** **HIGH — revenue** · **Status:** `[x]` **FIXED + DEPLOYED S136 2026-08-28 — T0 row added to `feature_matrix`; both `?: 'T1'` defaults changed to `?: 'T0'`; `?? $feature_matrix['T1']` fallback closed to T0; 7 missing feature keys added across all tiers (`camera`, `cloud_sync`, `engine_monitoring`, `maintenance_schedule`, `mobile_app`, `predictive_alerts`, `voice_assistant`). Deployed to HostPapa live. Commit be4485c9. ✅ VERIFIED S139 2026-09-01 — live DB query confirmed 0 users have missing/empty/zero `atmyboat_tier` meta. Fail-closed to T0 was safe; no paying customer affected. Gap closed.**
**Found by performing the FEATURE_MATRIX reconciliation that `BUG-65.md` §4 requires before Step 3.**

### The reconciliation itself came out clean — record that first

`BUG-65.md` §4 warned: *"there are already two matrices, one per platform. Reconcile them before adding
enforcement; if they disagree, the two sides differ on what a paid tier includes."*

**They do not disagree.** Parsed both and compared programmatically, 2026-08-28:

```
Pi     tier_service.py FEATURE_MATRIX  : tiers 0,1,2,3   17 features
Server data-ingress.php feature_matrix : tiers T1,T2,T3  11 features
Shared features: 10      VALUE MISMATCHES ACROSS T1/T2/T3: 0
```

**Zero.** BUG-77's deferred concern is answered: no divergence bug exists. The problems are structural.

---

### Finding 1 — two fail-open defaults to a PAID tier, in the entitlement authority itself

```php
148: $tier = amboat_get_user_meta( $user_id, 'atmyboat_tier' ) ?: 'T1';
227: $tier = amboat_get_user_meta( $user_id, 'atmyboat_tier' ) ?: 'T1';
272: $features = $feature_matrix[ $tier ] ?? $feature_matrix['T1'];
```

`?:` is a **falsy** test. `'0'`, `''`, `0`, `null` and "meta absent entirely" all collapse to `'T1'`.
Line 272 then does it again for any tier key the matrix lacks.

**A free user, or any user whose `atmyboat_tier` meta was never written, is served Tier 1 entitlements
by the server.** There is **no `T0` key in the server matrix at all** — so Tier 0 cannot be expressed,
only defaulted away.

⚠ **This is precisely what BUG-65 Step 3 exists to fix.** Step 3's premise is *"enforce paid features
server-side, where the secret lives."* **The server-side authority currently fails open to a paid tier.**
Step 3 cannot be written on top of this — the default must be closed first, or server enforcement
inherits the same bypass it was created to close.

⚠ **Fixing it is not simply changing `'T1'` to `'T0'`.** Adding a `T0` row and failing closed will
**strip features from any existing paying customer whose `atmyboat_tier` meta is missing or malformed.**
Count those users before changing the default. **A fail-closed default applied blind is an outage for
paying customers.**

### Finding 2 — the server ignores every audit field BUG-65 Step 2 sends it

`export_worker.py:239-242` appends `tier_claimed`, `tier_detected`, `opencpn_present`,
`subscription_key_present` on every export. Grep of the **live** `data-ingress.php` for all four:
**zero matches.**

⚠ **BUG-65's record is therefore wrong where it says:** *"Server receives the claim + the detected value
every export — mismatch is visible for human review."* **It is not visible.** Nothing reads the fields,
nothing stores them, no audit row is written, and there is nothing for a human to review.

**Step 2 is half-built: the Pi emits, the server discards.** The Pi-side work is real and correct — the
receiving half was never written. Correct the record, then build the consumer.

### Finding 3 — 7 Pi features have no server representation

Pi-only: `camera`, `cloud_sync`, `engine_monitoring`, `maintenance_schedule`, `mobile_app`,
`predictive_alerts`, `voice_assistant`. Server-only: `live_monitoring`.

⚠ **`cloud_sync` is the problem.** BUG-65 §4 classifies cloud sync as a **server-enforced** feature —
but the server matrix has no key for it. **The server cannot enforce an entitlement it cannot name.**
`camera`, `voice_assistant` and `predictive_alerts` are the Tier 2 features BUG-65's own symptom text
names as unlockable by forgery.

`mobile_app` / `engine_monitoring` vs `live_monitoring` may be the same concept under two names —
**verify rather than assume; if they are, unify the name; if not, both matrices are incomplete.**

---

### What this means for BUG-65 Step 3

**Step 3's prerequisite is now DONE** (the reconciliation) and it produced three blockers. Order:

1. Close the fail-open defaults — **after counting affected users**. Without this, server enforcement is decorative.
2. Add the missing feature keys, `cloud_sync` first.
3. Build the consumer for the Step 2 audit fields, and correct BUG-65's claim that it already exists.
4. **Then** write Step 3.

`Uncertainty flag: the live database was NOT queried. How many users have a missing or falsy
atmyboat_tier is UNKNOWN, and it decides whether closing the default is safe or an outage. Count first.`

### Related

- **BUG-65** — Step 3's blocker; its Step 2 "visible for human review" claim is corrected here
- **BUG-77** — deferred this exact comparison as needing a live HostPapa read; now done, no divergence
- **BUG-90** — same session, same shape: a control believed active that never ran

---

## BUG-92 — `services/fix_my_pi.py` is a stale 251-line copy; `cloud-agent/fix_my_pi.py` (333 lines) is the active superset

**Severity:** LOW | **Platform:** Pi — canonical tree | **Status:** `[x]` **FIXED S136 2026-08-28 — stale `services/fix_my_pi.py` (251 lines, v0.9.5) deleted from canonical tree. `cloud-agent/fix_my_pi.py` (333 lines, v0.9.6+) is the active superset that systemd runs. Commit f9ad6e0d.**
**Logged:** S136 2026-08-28 (BUG-83 §5 sweep)

### Symptom

Two copies of `fix_my_pi.py` exist in the canonical tree:

| Path | Lines | Notes |
|---|---|---|
| `services/fix_my_pi.py` | 251 | Missing `check_file_integrity()` and `hashlib` import |
| `services/cloud-agent/fix_my_pi.py` | 333 | Has file integrity check (diagnostic #6); **active — cloud_agent.py imports this via relative path** |

`cloud_agent.py` runs from `cloud-agent/` and imports `from fix_my_pi import run_diagnostics` — resolves
to the 333-line copy. The 251-line root copy is dead weight. The error message in `cloud_agent.py` points
to `/opt/d3kos/services/fix_my_pi.py` (root path) — this path description is wrong; the active import
resolves to `cloud-agent/fix_my_pi.py`.

### Root Cause

BUG-83 §5 pattern: a stale copy was not cleaned up when the cloud-agent version was extended.

### Fix

Delete `services/fix_my_pi.py` (root stale copy). Update the error message in `cloud_agent.py` to
reference the correct path `cloud-agent/fix_my_pi.py`.

### Affected Files

- `deployment/v0.9.9.4/opt/d3kos/services/fix_my_pi.py` — DELETE (stale)
- `deployment/v0.9.9.4/opt/d3kos/services/cloud-agent/cloud_agent.py` — error string correction

### signalk_client.py — NOT a bug (design note)

`services/ai/signalk_client.py` (145L, class-based `SignalKClient`) and `services/ai-bridge/utils/signalk_client.py`
(188L, function-based `get_navigation_snapshot`) are different implementations for different services.
`query_handler.py` uses the ai/ class; `ai-bridge` uses the utils/ function interface. Both are in active
use. Design smell (two SK interfaces) but not a stale-duplicate bug. If SK clients are ever unified, these
merge; not worth doing now.


---

## BUG-93 — GPS and Engine export collectors crash with JSONDecodeError when Signal K path returns 404

**Symptom:** Every export cycle on lab Pi logs:
```
✗ GPS error: Expecting value: line 1 column 1 (char 0)
✗ Engine error: Expecting value: line 1 column 1 (char 0)
```
Export continues successfully despite the errors (the `except` block catches them), but GPS and engine
data are always null in the export payload. The error message gives no indication of the true cause.

**Root Cause:** `collect_gps()` and `collect_engine()` in `export_categories.py` call `r.json()`
immediately after `requests.get()` without checking `r.status_code`. When Signal K returns HTTP 404
(path not present because the device has no GPS or NMEA 2000 source connected), the response body
is an HTML error page. Calling `.json()` on HTML raises `json.JSONDecodeError: Expecting value`.
The inner fuel and battery sub-requests already guard with `if r.status_code == 200:` — the outer
calls were missing the same guard.

**Platform:** Pi (lab Pi confirmed; boat Pi unaffected — SK has GPS via gpsd and N2K engine via CX5106).

**Affected Files:**
- `deployment/v0.9.9.4/opt/d3kos/services/export/export_categories.py` — `collect_gps()` and `collect_engine()`

**Fix:** Added `if r.status_code != 200: return empty_structure_with_note` guard before `r.json()`
in both functions. When SK returns non-200, the function returns null data with a `note` field
explaining the HTTP status code, and prints a clear log message (`SK returned 404 — no navigation data`).

**Verification (S140 2026-09-01):**
```
✗ GPS: SK returned 404 — no navigation data
✗ Engine: SK returned 404 — no propulsion data
✓ Export uploaded: q_20260901_152616
```
No more JSONDecodeError. Exports continue uploading successfully.

**Status:** `[x]` **FIXED S140 2026-09-01** — lab Pi verified. Boat Pi not yet tested (requires
GPS lock and CX5106 connected). SK paths (`/navigation`, `/propulsion/port`) are correct for the
boat Pi — fix is defensive only.

---

## BUG-94 — atmyboat.com has no page cache — server response time 632ms (threshold 600ms)

**Logged:** S142 2026-09-03
**Platform:** atmyboat.com (HostPapa shared hosting)
**Severity:** LOW — performance only; no data loss, no security impact; 32ms over threshold

**Symptom:** Website performance scanner reports "Critical — Page cache is not detected and the
server response time is slow." Specifically:
- Median server response time: 632ms (threshold: 600ms)
- No HTTP client caching headers detected (cache-control, expires, age, last-modified, etag, via,
  x-cache, x-litespeed-cache, cf-cache-status, etc.)
- No page cache plugin detected

**Root Cause:** No caching layer is configured at the WordPress level on the HostPapa site.
HostPapa shared hosting runs **Apache** (not LiteSpeed — confirmed S142 when LiteSpeed Cache
plugin showed "LSCache caching functions unavailable — requires LiteSpeed web server or QUIC.cloud").
Without a cache plugin, WordPress serves every page dynamically — PHP + MySQL per hit — with no
full-page cache and no HTTP caching headers set.

**Note on "Critical" label:** The scanner labels this Critical in its own severity scheme.
AAO severity is LOW — this is a performance issue only. The response time is 32ms over threshold,
the site is functional, and there is no security or data integrity impact.

**S142 investigation note:** LiteSpeed Cache plugin was installed first (incorrect recommendation
based on an unverified assumption that HostPapa uses LiteSpeed). Plugin warning confirmed Apache.
LiteSpeed Cache deactivated. Correct fix is WP Super Cache (Apache-compatible).

**Fix:** Install and activate **WP Super Cache**.
- Made by Automattic (WordPress team); works on Apache shared hosting.
- Generates static HTML files served directly by Apache — no server-level requirements.
- Sets HTTP caching headers (Last-Modified, ETag, Cache-Control) which satisfy the scanner.
- Free, no account required.

**Operator action (WP Admin — click-by-click):**
1. Plugins → Deactivate LiteSpeed Cache (cannot work on Apache — remove it)
2. Plugins → Add New Plugin
3. Search: `WP Super Cache`
4. Click Install Now → Activate
5. Settings → WP Super Cache → select **Caching On** → click **Update Status**

**Affected Files:** None (plugin install only — no repo files modified)

**Verification (S142 2026-09-03 — WP Super Cache built-in Cache Tester):**
```
Fetching http://atmyboat.com/ to prime cache: OK (0.html)
Fetching first copy of http://atmyboat.com/: OK (1.html)
Fetching second copy of http://atmyboat.com/: OK (2.html)
Page 1: 200 (OK)
Page 2: 200 (OK)
Page 1: 2026-09-03 12:12:14
Page 2: 2026-09-03 12:12:14
The timestamps on both pages match!
```
Matching timestamps confirm page 2 was served from the static HTML cache — not a fresh PHP/MySQL
render. Cache is functioning correctly.

**Status:** `[x]` **FIXED + VERIFIED S142 2026-09-03 — WP Super Cache installed, Caching ON,
cache tester passed (matching timestamps on both requests). LiteSpeed Cache deactivated (incompatible
with Apache). Original performance scanner re-run pending to confirm caching headers detected.**

---

## BUG-95 — export-on-boot.sh and export-daily.sh not deployed to Pi

**Logged:** S144 2026-09-04
**Platform:** Lab Pi (d3kOS v0.9.9.4)
**Severity:** MEDIUM — `d3kos-export-boot.service` and `d3kos-export-daily.service` fail at every
boot with exit code 203/EXEC (script file not found). Boot-time and daily scheduled exports have
never run on this Pi image.

**Symptom:** `systemctl list-units --state=failed` reports both services as failed at boot.
`journalctl` shows `203/EXEC` — the kernel could not execute the ExecStart binary because the path
does not exist.

**Root Cause:** Both scripts exist in the repo at `Helm-OS/scripts/export-on-boot.sh` and
`Helm-OS/scripts/export-daily.sh` but were never copied to `/opt/d3kos/scripts/` on the Pi during
image creation or any subsequent deploy. The systemd unit files reference these paths and were
registered, but the scripts themselves were omitted from the deploy.

**Affected Files:**
- `Helm-OS/scripts/export-on-boot.sh` (repo — correct, not on Pi)
- `Helm-OS/scripts/export-daily.sh` (repo — correct, not on Pi)
- `/etc/systemd/system/d3kos-export-boot.service` (Pi — registered, references missing script)
- `/etc/systemd/system/d3kos-export-daily.service` (Pi — registered, references missing script)

**Related:** BUG-54 (export failures / HTTP 400 to server). BUG-95 is a precondition failure —
the export scripts never start, independent of BUG-54's HTTP issue.

**Fix:** `scp` both scripts to `/opt/d3kos/scripts/` and verify they are executable. Then
`systemctl reset-failed d3kos-export-boot d3kos-export-daily` and confirm services run.

**Status:** `[~]` **FIXED LAB S144 2026-09-04 — both scripts copied to `/opt/d3kos/scripts/`,
permissions set 755, `systemctl reset-failed` run. Export-boot service started successfully
(ran, attempted upload — upload behaviour is BUG-54 scope, not BUG-95). Boot-time 203/EXEC
failure resolved. Boat Pi: scripts must be deployed at next in-person visit.**

---

## BUG-96 — detect-timezone.sh referenced by systemd unit but never written

**Logged:** S144 2026-09-04
**Platform:** Lab Pi (d3kOS v0.9.9.4)
**Severity:** LOW — timezone auto-detection has never run; Pi uses default/static timezone.
No data loss, no service outage.

**Symptom:** `d3kos-timezone-setup.service` fails at boot with exit code 203/EXEC. The unit
`ExecStart=/opt/d3kos/scripts/detect-timezone.sh` references a script that does not exist on the
Pi or in the repo.

**Root Cause:** The systemd unit file was written and registered, but the corresponding
`detect-timezone.sh` script was never authored. Unlike BUG-95 (scripts exist in repo, not deployed),
this script has no source anywhere.

**Affected Files:**
- `/etc/systemd/system/d3kos-timezone-setup.service` (Pi — registered, references nonexistent script)
- `/opt/d3kos/scripts/detect-timezone.sh` — DOES NOT EXIST (Pi or repo)

**Fix:** Write `detect-timezone.sh` (query IP geolocation API, call `timedatectl set-timezone`)
and deploy to Pi, OR disable the unit with `systemctl disable d3kos-timezone-setup.service` until
the script is written.

**Fix:** `deployment/v0.9.9.4/opt/d3kos/scripts/detect-timezone.sh` written S144.
Tries ip-api.com → worldtimeapi.org → ipapi.co (8s timeout each). Validates `Region/City`
format. Calls `timedatectl set-timezone`. Exits 0 always — API failure is non-fatal.
All log output to stderr so capture is clean inside command substitution.

**Verification (S144 manual run):**
```
[detect-timezone] Starting timezone detection (current: America/Toronto)
[detect-timezone] API 1 (ip-api.com) responded: America/Toronto
[detect-timezone] Detected timezone matches current — no change needed
exit: 0
```

**Status:** `[~]` **FIXED LAB S144 2026-09-04 — script written, deployed to Pi, manual test
passed (exit 0, correct timezone detected and matched). Takes effect cleanly on next reboot.
Boat Pi: deploy at next in-person visit.**

---

## BUG-98 — Tailscale apt keyring deleted but source list not removed; apt update fails at every boot

**Logged:** S144 2026-09-04
**Platform:** Lab Pi (d3kOS v0.9.9.4)
**Severity:** LOW — no service impact; causes a brief red warning notification at login and
pollutes journal with GPG errors on every apt update attempt.

**Symptom:** At login, a red Software Updater warning appears briefly. `xsession-errors`
contains: `up: Error updating cache - W: ... Failed to parse keyring
"/usr/share/keyrings/tailscale-archive-keyring.gpg" ... No such file or directory`.

**Root Cause:** Tailscale was removed from the Pi (standing instruction: "Tailscale: REMOVE
from Pi before v0.9.4 build begins"). The keyring file
`/usr/share/keyrings/tailscale-archive-keyring.gpg` was deleted, but
`/etc/apt/sources.list.d/tailscale.list` still exists and references it. Every `apt update`
(run automatically at login by the software updater) fails the GPG signature check and
produces the warning.

**Affected Files (Pi):**
- `/etc/apt/sources.list.d/tailscale.list` — must be deleted (references nonexistent keyring)
- `/usr/share/keyrings/tailscale-archive-keyring.gpg` — already absent

**Fix:** `sudo rm /etc/apt/sources.list.d/tailscale.list` then `sudo apt update` to verify
clean output.

**Status:** `[~]` **FIXED LAB S144 2026-09-04 — `/etc/apt/sources.list.d/tailscale.list` deleted.
`apt update` verified: no Tailscale errors. ⚠ Separate `free-x.de` GPG key warning remains —
different repo, different key, outside BUG-98 scope. Boat Pi: apply at next in-person visit.**

---

## BUG-99 — VNC xrandr autostart conflicts with Wayland/1920×1200 native monitor; background appears changed

**Logged:** S144 2026-09-04
**Platform:** Lab Pi (d3kOS v0.9.9.4)
**Severity:** LOW — cosmetic + log noise; all services function correctly at native resolution.

**Symptom:** (1) `.xsession-errors` contains xrandr error at every login:
`/usr/bin/xrandr: specified screen 1920x1080 not large enough for output HDMI-A-1 (1920x1200+0+0)`.
(2) Operator reports desktop background looks different from before.

**Root Cause — two independent issues sharing one trigger:**

*Issue A — VNC xrandr autostart:*
`/etc/xdg/autostart/vnc_xrandr.desktop` runs:
`sh -c "if ! (xrandr | grep -q -w connected) ; then /usr/bin/xrandr --fb 1920x1080 ; fi"`
Under labwc (Wayland), `xrandr` queries XWayland which does not expose the physical HDMI
monitor to X11, so `grep -q -w connected` returns false (no connected monitor seen). The
condition triggers and attempts `xrandr --fb 1920x1080` — but the actual Wayland output
(HDMI-A-1) is at its native **1920×1200** (preferred and current per `wlr-randr`). xrandr
cannot shrink the framebuffer smaller than the active output → error. The VNC script is a
Raspberry Pi OS VNC helper; it is irrelevant on a Pi with a physical monitor.

*Issue B — no wallpaper setter in labwc autostart:*
The labwc `~/.config/labwc/autostart` launches twofing, unclutter, and the d3kOS dashboard,
but contains no wallpaper command (`swaybg`, `wbg`, etc.). labwc renders its compositor
default background. Previously the desktop may have run a wallpaper via a different session
type or a tool that no longer runs under this session.

**Affected Files (Pi):**
- `/etc/xdg/autostart/vnc_xrandr.desktop` — VNC-only tool, must be disabled for this system
- `~/.config/labwc/autostart` — add wallpaper setter if a specific background is desired

**Fix Plan — see BUG-99 fix plan below.**

**Status:** `[~]` **FIXED LAB S144 2026-09-04.**
- **Part A:** `/etc/xdg/autostart/vnc_xrandr.desktop` — `Hidden=true` appended. Will not
  execute at next login. xrandr error will be gone.
- **Part B:** `~/.config/labwc/autostart` — `swaybg -c '#2d2d2d' &` inserted after header.
  `swaybg` v1.2.1 installed via apt. Dark grey background takes effect on next login/reboot.
  Backup at `~/.config/labwc/autostart.bak-bug99`.
- **Note:** `~/.config/labwc/autostart` is not tracked in the canonical repo tree — Pi-only
  file. Add to canonical tree if image rebuild is planned.
- **Boat Pi:** apply both changes at next in-person visit.

---

## BUG-101 — generate-reg-token.php returns HTTP 500 on POST; Pi registration blocked

**Logged:** S144 2026-09-04
**Platform:** HostPapa live (atmyboat.com) + Lab Pi (d3kOS v0.9.9.4)
**Severity:** HIGH — Pi registration flow completely blocked. No user can register via Pi
until resolved.

**Symptom:** Lab Pi calls `POST https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/generate-reg-token.php`
with correct credentials. HostPapa returns HTTP 500 with an empty body — PHP fatal error.
No JSON error object returned, no token generated.

**Investigation (S144):**
- Pi `api-keys.json` deployed: `amboat_api_key` present (39 chars, from `fleet-push.env`),
  `device_token` present (36-char UUID). Pi credentials confirmed correct.
- URL discovery: file does NOT exist at `https://atmyboat.com/mobile/generate-reg-token.php`
  (404). File IS at `https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/generate-reg-token.php`
  (returns 500 on POST, 500 on GET — file exists, PHP crashes).
- `app.py` has WRONG URL: `_AMBOAT_REG_ENDPOINT = 'https://atmyboat.com/mobile/generate-reg-token.php'`
  — this is a secondary bug (app.py URL needs correcting too).
- `generate-reg-token.php` opens with `require_once __DIR__ . '/config.php'` then calls
  `amboat_send_error()` and `amboat_get_db()` which are defined in `auth.php` (not in
  `config.php` directly). If `config.php` does not `require_once` `auth.php`, these calls
  are undefined → PHP fatal error → 500.

**Root Cause (suspected):**
`generate-reg-token.php` was new code added S143. The existing `config.php` on HostPapa
may not include `auth.php`, or `auth.php` may define `amboat_get_db()` differently than
the new script expects. All existing mobile endpoints (fleet-push, offline-check) work —
they were built when config.php was set up. `generate-reg-token.php` may rely on an
`auth.php` include that `config.php` does not provide.

**Secondary Bug:** `app.py:497` has wrong endpoint URL:
```python
_AMBOAT_REG_ENDPOINT = 'https://atmyboat.com/mobile/generate-reg-token.php'  # 404
# Correct:
_AMBOAT_REG_ENDPOINT = 'https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/generate-reg-token.php'
```

**Affected Files:**
- HostPapa: `wp-content/themes/twentytwenty-child/mobile/generate-reg-token.php` (server crash)
- HostPapa: `wp-content/themes/twentytwenty-child/mobile/config.php` (likely missing auth.php include)
- Pi canonical: `deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py:497` (wrong URL)
- Pi live: `/opt/d3kos/services/dashboard/app.py:497` (wrong URL, not yet fixed)

**Fix Plan:**
1. FTP to HostPapa → check PHP error log or add `error_reporting` to `generate-reg-token.php`
   temporarily to expose the fatal error
2. Verify `config.php` includes `auth.php` — if not, add the include
3. Fix `app.py:497` URL in canonical tree and redeploy to Pi
4. End-to-end test: Pi POST → HostPapa returns `{success:true, data:{token, register_url}}`

**Fix applied S144:**
Three root causes found and fixed:
1. **`generate-reg-token.php` missing `require_once __DIR__ . '/auth.php'`** — all four
   helper functions (`amboat_send_error`, `amboat_send_success`, `amboat_json_body`,
   `amboat_get_db`) are defined in `auth.php`. Every other mobile endpoint includes both
   `config.php` AND `auth.php`. This file only had `config.php`. Added the missing include.
   Deployed to HostPapa via FTPS (4,972 B size-verified). Committed `d33ce58` (atmyboat-forum).
2. **`app.py:497` wrong URL** — `https://atmyboat.com/mobile/generate-reg-token.php` (404)
   corrected to the theme path. Committed `448e7e4d` (Helm-OS).
3. **Missing `User-Agent` header** — nginx on HostPapa blocks `python-requests` UA.
   Added `'User-Agent': 'd3kOS/0.9.9.4 (Pi registration client)'` to the headers dict.
   Same commit `448e7e4d`.

**Verification:**
```json
{
  "success": true,
  "data": {
    "token":        "R-F5DZ5T4",
    "register_url": "https://atmyboat.com/register/?rt=F5DZ5T4",
    "expires_at":   "2026-09-04 23:59:50",
    "expires_min":  30
  }
}
```
Lab Pi → HostPapa → token generated. Registration flow end-to-end working.

**Status:** `[x]` **FIXED + DEPLOYED S144 2026-09-04.**

---

## BUG-100 — apt update GPG key warning for free-x.de repository

**Logged:** S144 2026-09-04
**Platform:** Lab Pi (d3kOS v0.9.9.4) — boat Pi status unknown
**Severity:** LOW — warning only; apt still functions. No security exposure confirmed.
**Symptom:** During BUG-98 apt cleanup investigation, a second apt GPG key warning was
observed for a `free-x.de` repository after the Tailscale source was deleted. Separate
from BUG-98.

**Root Cause (S144-cont 2026-09-04):** The free-x.de repo is the **AvNav apt repository**
— a core d3kOS component. The source was NOT orphaned. The real issue was twofold:
1. The GPG key file at `/usr/share/keyrings/avnav-archive-keyring.gpg` was only 32 bytes
   (essentially empty — written during initial Pi setup but never populated).
2. The source entry used `trusted=yes` (unsigned trust bypass) with no `signed-by=` reference.
   Newer apt/sqv (Sequoia PGP verifier) still attempts key verification even with `trusted=yes`,
   and logs a warning when the key is missing — repo IS used, warning is cosmetic only.

**Discovery Path (S144-cont):**
1. `grep -r "free-x.de" /etc/apt/sources.list.d/` → source is `/etc/apt/sources.list.d/avnav.list`
2. The source line had `trusted=yes` but no `signed-by=`. Newer sqv warns even with `trusted=yes`.
3. Probed `https://www.free-x.de/debian/` for common key file paths. Found `oss.boating.gpg`
   returns HTTP 200 (all others 404). Confirmed fingerprint `06B67AB0E988310475E75A2746E95F3C8A61623B`
   matches the required key via `gpg --list-packets`. Key is NOT on keyserver.ubuntu.com or
   keys.openpgp.org — must be fetched directly from `https://www.free-x.de/debian/oss.boating.gpg`.

**Affected Files (Pi):**
- `/etc/apt/sources.list.d/avnav.list` — source referencing free-x.de (AvNav repo)
- `/usr/share/keyrings/avnav-archive-keyring.gpg` — was 32-byte empty file, now populated

**Fix Applied (S144-cont 2026-09-04):**
1. `sudo curl -sS 'https://www.free-x.de/debian/oss.boating.gpg' -o /usr/share/keyrings/avnav-archive-keyring.gpg`
   — downloaded binary GPG public key (1,741 bytes). Key is NOT ASCII-armored — do NOT use `--dearmor`.
2. `sudo chmod 644 /usr/share/keyrings/avnav-archive-keyring.gpg`
   — sqv runs as `_apt` user; file must be world-readable (default was 600 → permission denied).
3. Source list updated to reference keyring and use HTTPS:
   - Before: `deb [arch=arm64 trusted=yes] http://www.free-x.de/debian trixie main`
   - After:  `deb [arch=arm64 signed-by=/usr/share/keyrings/avnav-archive-keyring.gpg] https://www.free-x.de/debian trixie main`
4. Backup: `/etc/apt/sources.list.d/avnav.list.bak-bug100`

**Verification:** `sudo apt update` → `Hit:6 https://www.free-x.de/debian trixie InRelease` — no warning, no error.

**Boat Pi:** Same fix required at next in-person visit. The empty keyring and `trusted=yes` source
line exist on any Pi built from the v0.9.9.4 image.

**Status:** `[x]` **FIXED LAB S144-cont 2026-09-04 — warning eliminated. Boat Pi: needs deployment.**

---

## BUG-97 — SK watchdog checks wrong port; Signal K health check always fails

**Logged:** S144 2026-09-04
**Platform:** Lab Pi (d3kOS v0.9.9.4)
**Severity:** LOW — watchdog always fails with exit code 1; SK and Node-RED are unaffected.
Watchdog is non-functional and produces a misleading failed-unit entry at every boot.

**Symptom:** `d3kos-sk-nodered-watchdog.service` fails at boot with exit code 1. Signal K
is healthy (active, ports 8375/10110/8099) and Node-RED is healthy (active, port 1880).

**Root Cause:** The watchdog inline script checks `curl http://localhost:3000/signalk` to verify
Signal K health. Port 3000 is the Flask d3kOS dashboard — not Signal K. Signal K runs on ports
8375 (admin UI), 10110 (NMEA), and 8099 (streaming). The curl returns HTTP 404 from Flask →
`SK_OK=0` (false negative) → the script executes `systemctl restart signalk` as user `d3kos`
(no sudo privilege) → permission denied → exit code 1.

**Affected Files:**
- `/etc/systemd/system/d3kos-sk-nodered-watchdog.service` — ExecStart inline bash script
  has wrong SK health URL (`localhost:3000/signalk`; correct is `localhost:8375/signalk/v1/api/`)

**Note:** The watchdog is `Type=oneshot` run by a timer — it is not a crash-restart loop.
However, compare with BUG-09 / BUG-23a: operator has a standing rule against watchdogs for AvNav.
This watchdog covers SK + Node-RED (different services). **Operator should decide whether this
watchdog stays, is fixed, or is disabled.**

**Fix (if keeping the watchdog):** Update the SK health check URL to
`http://localhost:8375/signalk/v1/api/` and run the unit as root (or add sudoers rule) so
`systemctl restart signalk/nodered` can execute.

**Status:** `[~]` **FIXED LAB S144 2026-09-04 — SK URL corrected to `http://localhost:8099/signalk`
(SK runs with `PORT=8099`; port 8375 is TCP stream only, not HTTP). `User=root` set so
`systemctl restart` has permission. Manual test: `status=0/SUCCESS`, SK_OK=1, NR_OK=1,
no restart triggered. Timer active (60s after boot, every 120s). Both canonical repo files
updated. Boat Pi: deploy at next in-person visit.**

---

## BUG-102 — Camera service restart-storms at Tier 0; d3kOS must run without cameras

**Logged:** S148 2026-09-05  
**Severity:** HIGH  
**Platform:** Pi — all v0.9.9.4.1 users on first boot (Tier 0)  
**Status:** `[ ]` OPEN

**Symptom:** On first boot (fresh image / sanitized Pi), `d3kos-camera-stream.service`
enters an infinite restart storm — "Start request repeated too quickly" floods the journal.
The service never transitions to a stable state. Operator requirement: d3kOS must run cleanly
at Tier 0 with no cameras connected or enabled.

**Root Cause (confirmed in code):**

1. `d3kos-camera-stream.service` has `ExecStartPre`:
   ```
   /bin/bash -c 'curl -s http://localhost:8093/tier/feature/camera | jq -e ".enabled == true" || exit 1'
   ```
2. On first boot, `cloud-config.json` is absent (deleted by `sanitize.sh`). The tier service
   (`tier_service.py:208`) logs: `"no cache + server down — returning False (fail closed)"` and
   returns Tier 0. Operator confirmed: **Tier 0 on first boot is correct and intentional.**
3. Tier 0 feature matrix has `camera: False` — `tier/feature/camera` returns `{"enabled": false}`.
4. ExecStartPre exits 1 → service fails.
5. `Restart=always` in the unit → systemd retries immediately → hits burst limit → "repeated
   too quickly" → service stuck in `failed` state, then retried again by subsequent triggers.

**The bug is not the tier check — it is the crash-loop.** A disabled feature must produce a
clean, stable no-op, not a storm.

**Affected Files:**
- `/etc/systemd/system/d3kos-camera-stream.service` — `ExecStartPre` + `Restart=always`
- `/opt/d3kos/services/marine-vision/camera_stream_manager.py` — no tier-disabled exit path

**Proposed Fix (minimal, two-part):**
1. In the service unit: change `Restart=always` → `Restart=on-failure`. Add
   `StartLimitIntervalSec=120` + `StartLimitBurst=3` so transient failures retry but a
   persistently-disabled feature gives up cleanly.
2. In `camera_stream_manager.py`: add a tier check at startup — if camera disabled,
   log `"Camera feature not enabled for this tier — exiting cleanly"` and `sys.exit(0)`.
   Modify (or remove) the ExecStartPre so exit 0 on disabled does not trigger a restart.

**Scope correction S148 (Fable):** FOUR units loop at Tier 0, not one — `d3kos-camera-stream`,
`d3kos-fish-detector`, `d3kos-voice` (all `ExecStartPre` tier checks → `failed`) and `d3kos-live`
(`live_session.py:874` `sys.exit(1)` when `cloud-config.json`/`device-token.json` absent → `Restart=on-failure`
every 10 s forever; the author already wrote the correct "stay up, don't restart-loop" pattern 8 lines
above for the aiortc case). **Fix mechanism decided:** `ExecCondition=` (systemd 257 on the Pi) — a
non-zero exit SKIPS the unit to `inactive` with no failure and no restart; `ConditionPathExists=` for
live; one `d3kos-tier-gated.timer` re-tries every 5 min. Unit-file edits only. **This is what fed
BUG-105** — a `failed` camera unit is what the detector inserted 6,837 rows about.
**Fix spec:** `atomic-specs/BUG-105.md` Step 5.

---

## BUG-103 — journald volatile storage; crash events are unrecoverable

**Logged:** S148 2026-09-05  
**Severity:** MEDIUM  
**Platform:** Pi — all versions  
**Status:** `[ ]` OPEN

**Symptom:** After a Pi crash or unexpected reboot, `journalctl --list-boots` shows only the
current boot. All logs from the previous session are permanently lost. Crash cause cannot be
determined. Operator confirmed: no power loss occurred — the Pi crashed and there is no
evidence of why.

**Root Cause (CONFIRMED S148):** Raspberry Pi OS ships
`/usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf` = `Storage=volatile` (SD-wear protection).
`/etc/systemd/journald.conf` is all defaults (`#Storage=auto`) and `/var/log/journal/` exists (empty,
created 2026-04-01) — so a past attempt to enable persistence never took: the vendor drop-in wins over
`journald.conf`. Only a drop-in in `/etc/systemd/journald.conf.d/` sorting after `40-` overrides it.
Journal lives in `/run/log/journal/` (tmpfs, 147 MB during the BUG-105 storm) and is wiped on reboot.
Consequence on 2026-09-05: the kernel-level cause of an 8-day-uptime freeze is unrecoverable.
**Fix spec:** `atomic-specs/BUG-105.md` Step 1 — `50-d3kos-persistent.conf`, 200 MB cap, weekly rotation.

**Verification:**
```bash
# On Pi — shows volatile if /var/log/journal/ does not exist or Storage=volatile
cat /etc/systemd/journald.conf | grep Storage
ls /var/log/journal/ 2>/dev/null || echo "NOT PERSISTENT"
```

**Affected Files:**
- `/etc/systemd/journald.conf` — `Storage=` setting

**Proposed Fix:**
1. Set `Storage=persistent` in `/etc/systemd/journald.conf`.
2. Set `SystemMaxUse=200M` to cap SD card use.
3. Create `/var/log/journal/` (systemd does this automatically when Storage=persistent).
4. Restart `systemd-journald` — logs persist across reboots immediately.

**SD card write concern:** Persistent logging increases write frequency. On an SD card this
is a long-term wear concern. Mitigation: `SystemMaxUse=200M`, `MaxFileSec=1week`,
`Compress=yes` (all in journald.conf). Logs rotate weekly and total size is capped.

**Note:** This bug means any past Pi crash cause is unrecoverable. Once BUG-103 is fixed,
future crashes will be diagnosable from `journalctl -b -1`.

---

## BUG-104 — sanitize.sh leaves lab Pi with SSH dead after reboot (lab-only)

**Logged:** S148 2026-09-05  
**Severity:** LOW (lab-only, not user-facing)  
**Platform:** Lab Pi only  
**Status:** `[ ]` OPEN

**Symptom:** After `sanitize.sh` runs on the lab Pi and the Pi is subsequently rebooted
(crash or manual), SSH port 22 refuses connections. `systemctl status ssh` shows failed.

**Root Cause:** `sanitize.sh` Step 4 deletes `/etc/ssh/ssh_host_*_key*`. The OS has two
keygen services (`sshd-keygen.service`, `regenerate_ssh_host_keys.service`) that regenerate
them, but BOTH have `ConditionFirstBoot=yes`. Because the lab Pi is past first-boot, this
condition is never met again — keygen is skipped, sshd fails to start.

**Why this does NOT affect real users:** A customer who flashes the image triggers a genuine
first boot. `ConditionFirstBoot=yes` is met, keygen runs, host keys are created, SSH works.
The lab Pi is the only machine where sanitize.sh runs on a non-first-boot system.

**Lab Recovery Procedure (manual, already applied S148):**
```bash
# On Pi console (keyboard + HDMI required):
sudo ssh-keygen -A
sudo systemctl start ssh && sudo systemctl enable ssh
# On WSL:
ssh-keygen -R 192.168.1.237
ssh -i ~/.ssh/id_d3kos d3kos@192.168.1.237
```

**Fix APPLIED S148-cont 2026-09-05:** `deployment/v0.9.9.4/home/d3kos/lab-restore.sh` —
a standalone script (NOT touched by `sanitize.sh`'s deletion list, confirmed by grep: it only
deletes specific named files, never a broad `/home/d3kos` wipe) that regenerates SSH host keys
and starts/enables sshd. **Deliberately NOT added to `sanitize.sh` itself** — doing so would bake
a single shared host keypair into every image built from that run, defeating the per-device
uniqueness `ConditionFirstBoot=yes` correctly provides for real customers. This script is a
console-run lab tool only, staged at `/home/d3kos/lab-restore.sh` on the Pi so it survives future
sanitize runs and needs no network access — which matters, since SSH being down is the exact
problem it solves. Deployed and executable on the lab Pi.


---

## BUG-105 — Self-healing runaway: remediation engine × issue detector storm crashed the lab Pi; ships in v0.9.9.4.1

**Logged:** S148 2026-09-05  
**Severity:** CRITICAL — release gate for v0.9.9.4.2  
**Platform:** Pi — every v0.9.9.4.1 install at Tier 0 (i.e. every fresh install)  
**Status:** `[x]` FIXED + DEPLOYED LAB S148 2026-09-05 — `verify-bug105.sh` 15/15 PASS, re-confirmed after full cold reboot. **24H SOAK PASS S152 2026-09-09** — Pi ran unattended 24+ hours, operator confirmed zero issues, no storm, no crash; Pi shut down cleanly by operator after soak. v0.9.9.4.2 soak gate CLEARED.

**Symptom:** Lab Pi froze hard (ARP unresolvable, no ping) ~09:55 EDT 2026-09-05 after 8 days uptime;
recovered only by power-cycle at 16:06. Operator confirmed no power loss. Post-boot: `d3kos-license-api`
dead (`start-limit-hit`), `d3kos-camera-stream` in permanent restart storm, PID 1 at 38% CPU,
`dbus-daemon` and `systemd-journald` elevated, 67,410 `systemctl` invocations in the first 21 minutes.

**Root cause (confirmed in code and on the live Pi):** two services form an unbounded positive-feedback loop.

1. `self-healing/issue_detector.py` polls every 60 s and **INSERTs a new `detected` row every poll** for
   any service whose `systemctl is-active` ≠ `active`. No dedup, no check for an existing open row.
   `issues.db` held **7,055 open rows**: 6,837 × "d3kos-camera-stream is not running" (since 2026-08-28
   06:52) + 218 × license-api.
2. `self-healing/remediation_engine.py` every 30 s SELECTs **all** `detected` rows and runs
   `systemctl restart <svc>` **once per row** — no attempt counter, no backoff, no terminal state; a
   failed row stays `detected` and is retried every cycle forever. With 7,055 rows that is ~170 s of
   back-to-back `systemctl restart` per 200 s cycle ≈ **40 restarts/sec, continuously, for 8 days.**
3. It restarts services **without checking whether they are already running.** `license-api` was healthy;
   218 back-to-back restarts tripped systemd's start-rate limit and left it `failed` — first at 10:36
   pre-crash, again at 16:09 post-boot. **The self-healing layer killed a working service.**
4. `remediation.log` is appended 3 lines per attempt with no rotation: **2.6 GB / 24,142,348 lines**
   on the SD card (est. ~1.3 GB/day at the final rate). Continuous SD write load for 8 days.
5. Why the storm exists at Tier 0: camera is a Tier ≥1 feature; at Tier 0 (correct on first boot —
   operator decision S148) `d3kos-camera-stream`'s ExecStartPre exits 1 → unit `failed` → detector
   inserts 1 row/min → engine load grows linearly, restart rate quadratically.

**Crash timeline (from `remediation.log` gap analysis + `issues.db`; journal was volatile — BUG-103):**
- 09:55:53 — last engine write before a **4-hour gap**. Engine wedged.
- 13:52:29 — last detector row (detector thread still limping).
- ~13:53 — full freeze (restored boot clock = 13:53:24 = last clock save).
- 16:06:35 — operator power-cycle (true boot time; journal "13:53" stamps are pre-NTP).
- 16:09:59 — post-boot engine reaches license-api rows → 218-restart burst → `start-limit-hit`.
`Uncertainty flag: the kernel-level failure mode (SD controller stall under sustained write vs PID 1
job saturation) is not provable — the journal was in RAM. BUG-103 fix makes the next one diagnosable.`

**Release impact:** `sanitize.sh` and `create-image.sh` never touch `/opt/d3kos/data/self-healing/` or
`/var/log/d3kos/`. **The 7,055-row `issues.db` was imaged into v0.9.9.4.1** [inference from the scripts;
the .img was not mounted — verify by mounting before v0.9.9.4.2 build]. Even with a clean DB, every
Tier-0 install regenerates the storm from minute one via item 5. **v0.9.9.4.1 is unstable at Tier 0.**

**Affected files (all md5-identical repo↔Pi, verified S148):**
- `opt/d3kos/services/self-healing/remediation_engine.py` — no is-active check, no cap, no per-service dedup, no log rotation
- `opt/d3kos/services/self-healing/issue_detector.py` — no dedup; flags `inactive` (clean stop) same as `failed`
- `opt/d3kos/scripts/sanitize.sh` — does not purge self-healing DB or `/var/log/d3kos/*.log`
- Units: `d3kos-remediation.service`, `d3kos-issue-detector.service` (both `Restart=always`, `User=root`)

**Mitigation applied lab Pi S148 (reversible):** `systemctl stop+disable d3kos-remediation d3kos-issue-detector`;
7,048 `detected` rows set `resolved` with `remediation_action='BUG-105 S148 purge'` (backup
`issues.db.pre-bug105.bak`); `remediation.log` truncated after saving `remediation.log.pre-bug105-tail.txt`
(5,000 lines); `license-api` reset-failed + started. **Boat Pi: same storm is running there right now
if camera is Tier-gated off — check `journalctl _COMM=systemctl | wc -l` at next visit.**

**Fix:** `deployment/docs/atomic-specs/BUG-105.md` — one spec covering BUG-103 → BUG-105 → BUG-102 in
dependency order, Sonnet-implementable, TDD.

**Related:** BUG-23a (same hot-loop shape, S116), BUG-09 (operator's standing rule against blind watchdogs
— this engine is exactly the class of watchdog that rule exists for), BUG-102, BUG-103.


---

## BUG-106 — Kiosk browser never launches on first boot at Tier 0 (blank grey screen)

**Logged:** S148 2026-09-05  
**Severity:** CRITICAL — release gate for v0.9.9.4.2 (folded into BUG-105 fix pass, same theme: first boot at Tier 0)  
**Platform:** Pi touchscreen — every v0.9.9.4.1 install on genuinely fresh first boot  
**Status:** `[x]` FIXED lab Pi S148 2026-09-05, applied live + committed to canonical tree

**Symptom:** Physical Pi touchscreen shows only the bare Wayland desktop (solid dark grey
`swaybg` wallpaper) — never the d3kOS dashboard or the setup wizard. Discovered live during
the BUG-105 verification session: after the crash + reboot, the lab Pi (in the same
`vessel.env`-absent state every fresh v0.9.9.4.1 install starts in) sat on a blank screen for
over an hour. **Operator: "that's great — this is the first time I've seen it boot to the
wizard,"** confirming the wizard screen had never actually rendered on this hardware before.

**Root Cause (confirmed live):** `~/.config/labwc/autostart` gates the kiosk browser launch on
the dashboard returning exactly HTTP 200:
```bash
until curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/ | grep -q 200; do
    sleep 2
done
/opt/d3kos/scripts/launch-d3kos.sh
```
At Tier 0 with `vessel.env` absent (the correct state for every fresh install — see BUG-102),
`app.py:236` returns **302 → `/setup`**, never 200. The `until … grep -q 200` loop therefore
**never exits on a genuine first boot**, and `launch-d3kos.sh` (which starts Chromium) never
runs. Confirmed live: the loop's shell (`sh /home/d3kos/.config/labwc/autostart`, PID 2908)
had been blocked since boot (16:07) with the dashboard steadily returning 302 the entire time.

**This is the same failure class as BUG-102** — code written assuming the dashboard is always
either "down" or "fully configured," with no allowance for the correct, common, in-between
state (up, but showing the setup wizard).

**Fix:** Accept either 200 or 302 as "reachable" — both mean the Flask app is up and the
kiosk browser should launch (it will simply render the setup wizard if the Pi isn't configured
yet, which is correct and desired):
```bash
until curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/ | grep -qE '^(200|302)$'; do
    sleep 2
done
```
**Affected file:** `/home/d3kos/.config/labwc/autostart` — previously **unsourced** (not in any
repo — same pattern as BUG-28/BUG-83's unversioned-script findings). Brought under version
control byte-identical first, then patched: `deployment/v0.9.9.4/home/d3kos/.config/labwc/autostart`.

**Immediate lab recovery (non-destructive, no reboot):** killed the stuck wait-loop shell,
launched `/opt/d3kos/scripts/launch-d3kos.sh` directly via `setsid` with the compositor's own
`DBUS_SESSION_BUS_ADDRESS`/`XDG_RUNTIME_DIR`/`WAYLAND_DISPLAY` env (read from the live `labwc`
and `wayvnc` process environs). Chromium came up cleanly, screen showed the setup wizard.

**Verification:** full reboot test — see BUG-105 record, Step 7 deploy log. Confirms the fixed
autostart script launches the kiosk automatically on real (not live-patched) boot.

**Related:** BUG-102 (same root cause family — code that only understands "off" and "fully
on," not the Tier-0/unconfigured middle state). Fixed together as part of the same
`atomic-specs/BUG-105.md` pass.


---

## BUG-107 — Password-change step: Enter key silently resubmits vessel wizard, never sets the password

**Logged:** S148-cont 2026-09-05  
**Severity:** CRITICAL — blocks first-run access to the dashboard entirely  
**Platform:** Pi dashboard setup wizard — every fresh v0.9.9.4.1 install (Tier 0, default password)  
**Status:** `[x]` FIXED + DEPLOYED lab Pi S148-cont 2026-09-05. Operator unblocked live
(password set to `d3kos2026` — operator's explicit decision, made knowing this is the
documented default; lab Pi only, not internet-facing); `password_changed` flag flipped;
`ONBOARDING_RUNS` reset to 0. Code fix deployed: `onkeydown` guard added to both password
fields, calling `submitPasswordChange()` and `preventDefault()` on Enter. Verified: exact
2-line diff against pre-fix backup, md5-identical repo↔Pi, dashboard restarted clean
(`GET /` still 200 after restart). **Not yet verified end-to-end in an actual browser** —
the fix is a client-side JS guard; no browser-automation test exists for this page.

**Symptom:** Operator completed the vessel setup wizard, but was repeatedly returned to what
looked like the same wizard instead of reaching the dashboard. Each attempt silently consumed
one of the 10 allowed onboarding runs (`ONBOARDING_RUNS` climbed to 7 with no vessel data change).
Navigating back does not help — `/` unconditionally redirects to `/setup` while the password is
still default (by design; see BUG-102/106 family).

**Root Cause (confirmed):**
1. `app.py:235-236` — `/` correctly redirects to `/setup?require_password=1` while
   `onboarding.json`'s `password_changed` is `false`.
2. `setup.html`'s client-side `checkDefaultPassword()` (DOMContentLoaded) correctly detects this
   (`/network/check-default-password` returns `{"default": true}` — confirmed live) and shows the
   `#wiz-password` step.
3. **The bug:** `#wiz-password`'s two `<input type="password">` fields (`#pw-new`, `#pw-confirm`)
   sit inside `<form id="wiz-form" method="POST" action="/setup">` — the SAME form used by the
   6-step vessel wizard. The submit button is correctly `type="button" onclick="submitPasswordChange()"`,
   but **nothing prevents the browser's default Enter-key behavior**: pressing Enter in either
   password field submits the *enclosing form* directly to `/setup` (the vessel wizard's own POST
   handler, `setup_post()`) instead of calling `submitPasswordChange()`, which POSTs JSON to
   `/network/change-password`. `grep` for `preventDefault`/`keydown` in `setup.html` returns nothing
   — zero protection exists.
4. Because the vessel fields were already filled from a prior run (sticky by design), the accidental
   submission silently resubmits the *same* vessel data — no visible error, no data loss — but
   increments `ONBOARDING_RUNS`, writes `vessel.env` again, and redirects to `/`, which redirects
   right back to `/setup?require_password=1` since the password was never touched. **Confirmed
   backend-side that this is not a server bug:** `/network/check-default-password` and `sudo chpasswd`
   (passwordless sudoers rule present) both work correctly when tested directly.

**Compounding harm:** every accidental resubmission burns one of the 10 `ONBOARDING_RUN_LIMIT`
attempts (`app.py:39`) for no reason — the user is never actually retrying the vessel wizard, they're
being silently defeated by the missing Enter-key guard. Reset live for the operator (`ONBOARDING_RUNS`
set back to 0 directly in `vessel.env`).

**Fix:** add an Enter-key guard to the password step that calls `submitPasswordChange()` and
prevents the default form submission, e.g. `onkeydown="if(event.key==='Enter'){event.preventDefault();submitPasswordChange();}"`
on `#pw-new` and `#pw-confirm`, or a single `keydown` listener scoped to `#wiz-password`. Broader
fix worth considering: move the password fields outside `wiz-form` entirely (a separate `<div>`,
not nested in any `<form>`) so this class of bug cannot recur for any future step added before the
password gate.

**Follow-up applied S148-cont 2026-09-05 (operator approved):** the UI hint text said "Cannot
be the default password," but `change_password()` (`app.py:364-397`) had no such check — only
a length check. Added a 3-line rejection: `if new_password == 'd3kos2026': return
{'success': False, 'error': 'Cannot reuse the factory default password'}, 400`. Deployed —
exact 4-line diff against pre-fix backup, md5-identical repo↔Pi, dashboard restarted clean.
Live-tested: POSTing `d3kos2026` to `/network/change-password` now correctly returns the
rejection; `GET /` unaffected (still 200) — the lab Pi's already-set password (an explicit
prior operator decision, made before this check existed) was not touched or invalidated.

**Immediate operator unblock (S148-cont, live, no reboot):** password set directly via
`sudo /usr/sbin/chpasswd` (matching the exact command the endpoint itself runs) + `onboarding.json`
`password_changed` set to `true` manually; `ONBOARDING_RUNS` reset to `0` in `vessel.env`.

**Related:** discovered immediately after BUG-106 (kiosk now shows the wizard) — same session,
same "first time this screen has ever rendered" territory. Not the same root cause, but the same
class of defect: functionality that was written but never exercised end-to-end before release.


---

## BUG-108 — AtMyBoat.com registration completely non-functional: `api-keys.json` has zero creation mechanism

**Logged:** S148-cont-2 2026-09-05  
**Severity:** CRITICAL — blocks the core registration/subscription business function on every fresh install  
**Platform:** Pi dashboard "Create Account" (Settings) — every v0.9.9.4.1 install, no exceptions  
**Status:** `[~]` BACKEND ONLY S149 2026-09-06 — Ed25519 migration deployed; `curl` verified; end-to-end NOT verified in browser or on phone

**⚠ S150 2026-09-06 — ROOT CAUSE DECOMPOSED. Read this before doing any further work on BUG-108.**

The backend is not the remaining problem. A live read of the Pi, the live HostPapa files and the live PWA established that the Ed25519 work done in S149 is correct and functioning: `/api/generate-reg-token` returns a valid `register_url`, and that URL resolves HTTP 200 with the code pre-filled in the form. What remained broken is the surrounding user path, which is **five separate defects** now tracked individually:

- **BUG-111** — `/register/` accepts a present-but-invalid or expired code without error, creating an unlinked T0 account and showing the success screen. This is the largest part of BUG-108's user-visible failure.
- **BUG-112** — the setup wizard never calls `/api/generate-reg-token`; Step 6 is a mobile-pairing screen whose QR encodes `d3kos://pair/<uuid>`, which no phone camera can act on.
- **BUG-113** — the QR library is CDN-only, so no QR renders without internet.
- **BUG-114** — the displayed code carries an `R-` prefix that both server validators reject, so manual entry always fails.
- **BUG-115** — the PWA `/app` login screen contains no route to registration at all (this is where the operator was looking when reporting "there is no way to register").

**Two premises from earlier records are now DISPROVED and must not be re-investigated:**
1. `DEVICE_UUID` is **not** blank (S149's hypothesis). `app.py:52` reads `/etc/machine-id` with a hostname-SHA256 fallback; the live lab Pi renders a populated UUID.
2. `/register/` is **not** device-gated, and the BUG-63-era "Draft" state no longer holds. The live page returns HTTP 200 with an unguarded, working "Create account" form, and registration is linked from the site header and footer. **Self-serve registration on the website works today.** The gap is discoverability from the PWA and the hand-off from the Pi — not a missing registration system.

**Operator decisions S150 that govern the fix:** (1) **one event** — redeeming the Pi's code creates the account *and* links the Pi, with Tier 1 following automatically, so device pairing folds into registration (this closes MASTER_SYSTEM_SPEC §12 Open Item #2); (2) **Tier 0 may register** — open web signup stays available and the code is a linking mechanism, not an entry gate, which reverses registration-spec decision D1.

**Implementation spec:** `deployment/docs/atomic-specs/BUG-111-118-REGISTRATION.md`

**Symptom:** Tapping "Get Registration Code" in Settings → Community → Create Account shows only a
bare error box — no QR code, no code text, no clickable link, nothing to type or scan. Discovered
live immediately after BUG-106/107, while the operator was testing the online registration flow the
newly-working kiosk finally let them reach.

**Root Cause (confirmed):** `/api/generate-reg-token` (`app.py:506-546`) reads
`/opt/d3kos/config/api-keys.json` for `amboat_api_key` before it can even attempt the HostPapa call:
```python
keys = json.loads(_APIKEYS_JSON.read_text())
api_key = keys.get('amboat_api_key', '')
```
Live test: `curl -X POST http://localhost:3000/api/generate-reg-token` →
`{"error":"Could not load Pi credentials: [Errno 2] No such file or directory: '/opt/d3kos/config/api-keys.json'"}`

`api-keys.json` is one of the five files `sanitize.sh`'s BUG-78 credential-strip deletes before every
image build (same family as `cloud-config.json`, `device-token.json`, etc.). **Unlike the other four,
which are documented as "regenerated on first boot" in the BUG-78 spec, `api-keys.json` has no
regeneration path at all** — confirmed by exhaustive search: no template file anywhere in the repo,
no reference in `first-boot-setup.sh`, no mention in `CREDENTIAL_VAULT.md`. It appears to have only
ever existed by being hand-placed once, outside any documented provisioning process.

**Why this is worse than BUG-102/BUG-106/BUG-107:** those blocked convenience features (camera,
kiosk display, password UX) that a Tier-0 user can live without. This blocks **every path to Tier 1**
— no registration means no subscription, no mobile app pairing via account, no forum access. Every
customer who has ever tried "Create Account" on a genuinely fresh v0.9.9.4.1 Pi has hit this exact
error.

**Compounding UX gap (operator-identified, same session):** even in the *success* case, the only
fallback if scanning fails is a button labeled "🔗 Open Register Page" with no visible URL text —
nothing a user can read aloud, copy by hand, or type on a different device. Normal QR UX (scan →
browser opens a plain `https://` URL directly, no app required) is the correct existing design intent
for *this* QR (unlike the separate Mobile Pairing QR, which intentionally needs the d3kOS app's own
scanner) — `d.register_url` from HostPapa is expected to be a normal link. The missing piece is only
the backend credential, not the QR mechanism itself. Additionally, the on-screen description text
("Get a one-time registration code for atmyboat.com/register/. Valid 30 minutes. Requires internet.")
does not explain what the code is for or how to use it — operator: "the description on the page needs
to be straightforward. It is not."

**Fix — requires an operator decision on approach:**
1. **(Immediate, lab-only, reversible)** Operator supplies the current `AMBOAT_API_KEY` (already
   known to exist in `mobile/config.php` on HostPapa — flagged for rotation, not yet rotated) so
   `api-keys.json` can be manually restored on the lab Pi for continued testing. Does not touch
   production; does not appear in any future image (sanitize.sh still strips it).
2. **(Proper, larger scope)** Either (a) build a first-boot provisioning step for this fleet secret,
   matching the pattern the other four files are documented — but never implemented — to follow, or
   (b) migrate `generate-reg-token.php`'s auth to the Ed25519 device-signing mechanism that
   `regenerate-identity.sh` already correctly self-provisions on every device's first boot (BUG-66
   Phase B) — closing this the same way other endpoints in that migration already have. Option (b)
   requires a **server-side PHP change on HostPapa**, which needs explicit pre-change file list +
   operator `APPROVED` per standing rule before any work begins.
**Fix applied S149 2026-09-06 (operator approved Ed25519 migration):**

- `app.py` (`/api/generate-reg-token`): replaced `api-keys.json` Bearer-key auth with Ed25519
  `sign_device_request('/amboat-device/v1/gen-reg-token')`. Endpoint now calls the WP REST path.
- `generate-reg-token.php`: added `d3kos_handle_gen_reg_token(WP_REST_Request)` handler (WP context,
  sodium available). Uses `amboat_reg_tokens` table (same as standalone path and `page-register.php`).
  Returns `{token: "R-ABCDEFG", register_url, expires_at, expires_min}` — unchanged format.
- `d3kos-device-auth.php` plugin: added `require_once` for `generate-reg-token.php` + route
  `amboat-device/v1/gen-reg-token`.
- `device-auth.php`: added OpenSSL Ed25519 fallback (for standalone path) + sodium constant fallbacks.
- Key finding: `generate-reg-token.php` (standalone PHP) on HostPapa has NO sodium extension.
  Solution: route Pi through `/wp-json/amboat-device/v1/gen-reg-token` (WP REST, sodium present).
  Path in signature must be `/amboat-device/v1/gen-reg-token` (WP_REST_Request::get_route() strips `/wp-json`).

**Verification:** `curl -X POST http://localhost:3000/api/generate-reg-token` on lab Pi →
`{"success":true,"data":{"token":"R-DF3A7WE","register_url":"https://atmyboat.com/register/?rt=DF3A7WE","expires_at":"2026-09-06 15:15:44","expires_min":30}}`

⚠ **Playwright UI test not yet written** — curl confirms the backend; the on-screen QR display and
registration flow at `atmyboat.com/register/?rt=DF3A7WE` have not been tested end-to-end in a browser.

3. **(UI, independent of 1/2, low-risk) APPLIED S148-cont-2 2026-09-05, operator approved** — added
   a visible plain-text URL row ("No camera? Type this into any browser:") alongside the existing
   "Open Register Page" button, and rewrote the description copy from jargon ("Get a one-time
   registration code...") to plain, action-first language ("Scan the QR code below with your phone
   to open AtMyBoat.com and create your free account..."). Deployed — exact diff confirmed, md5-
   identical repo↔Pi, dashboard restarted clean, `/settings` still 200.
   **⚠ Deploy-time discovery, unrelated to this bug's root cause but recorded for the record:** the
   lab Pi's live `settings.html` was 100 lines shorter than the canonical repo copy — the entire
   "Create Account" section (HTML + QR loader + `generateRegToken()`/`resetRegToken()` JS) existed
   in the repo but had **never actually been deployed to this Pi**. This deploy brought it into
   parity with the repo (plus the 3 UI fixes above) in one step. The backend route
   (`/api/generate-reg-token` in `app.py`) was already live and independently confirmed broken via
   direct `curl` before this — the missing frontend and the missing backend credential are two
   separate facts, both real, now both visible on screen as a proper error state instead of nothing
   at all.

**Related:** same root-cause family as BUG-102/BUG-106 (files `sanitize.sh` strips with no
regeneration path) and BUG-66 (fleet-wide shared secret authenticating multiple endpoints — a
standing CRITICAL concern this bug adds a fifth consumer to).


---

## BUG-109 — Test suite accuracy: 6 test code defects producing false failures

**Logged:** S149 2026-09-06 | **Severity:** MEDIUM (test integrity) | **Platform:** Repo / test suite
**Status:** `[x]` FIXED S149 2026-09-06

**Symptom:** `./tests/run-all.sh` reports 16 Playwright failures, 1 Node failure, 1 Pytest failure
(18 total) against the live lab Pi. Investigation shows the Pi and product code are correct for most
of these — the test code itself is wrong.

**Root cause:** Six distinct test code defects, all introduced at different times and never caught
because there was no CI gate and previous sessions trusted reported pass counts without running the
full suite under run-all.sh.

**Affected files:**
- `tests/contract-dashboard.spec.ts`
- `tests/bug26-anchor-watch-origin.spec.ts`
- `tests/bug13-speed-gauge.test.cjs`
- `tests/test_bug35_version_file.py`

**Individual findings and fixes (S149):**

### TS-1 — C3 wrong route URLs (contract-dashboard.spec.ts)
- **Error:** C3 route test checked `/anchor-watch.html`, `/boatlog.html`, `/ai-status` — all 404.
- **Root cause:** Flask routes are `/anchor-watch`, `/boat-log`, `/status` (no `.html`; `/ai-status` never existed).
- **Fix:** Updated `EXPECTED_ROUTES` to `/anchor-watch`, `/boat-log`, `/status`.

### TS-2 — C2 `CSS is not defined` (contract-dashboard.spec.ts)
- **Error:** `ReferenceError: CSS is not defined` — test called `CSS.escape()` directly in Node.js context.
- **Root cause:** `CSS.escape()` is a browser DOM API, not available in the Playwright Node runner.
- **Fix:** Replaced with `await page.evaluate((i) => CSS.escape(i), id)` to run it in the browser context.

### TS-3 — C2 compound selector CSS.escape corruption (contract-dashboard.spec.ts)
- **Error:** After TS-2 fix, 3 violations reported: `#posRpt .pr-big`, `#posRpt .pr-mid`, `#posRpt .pr-pos` absent from DOM.
- **Root cause:** `CSS.escape('posRpt .pr-big')` produces `posRpt\ \.pr-big` — escaping the space and dot turns a valid compound selector into a literal-ID lookup that never matches.
- **Verified:** Live `curl` of `http://192.168.1.237:3000/` confirmed all three elements exist in the rendered HTML.
- **Fix:** Skip CSS.escape for selectors containing a space (compound selectors from `querySelector`); use as-is with `#` prefix.

### TS-4 — bug26 wrong page URL (bug26-anchor-watch-origin.spec.ts)
- **Error:** Both bug26 tests navigate to `/anchor-watch.html` → 404 → test times out or checks 404 HTML body.
- **Root cause:** Flask route is `/anchor-watch` (no `.html`).
- **Fix:** Replaced both occurrences of `/anchor-watch.html` with `/anchor-watch`.

### TS-5 — bug13 stale sentinel and incomplete final condition (bug13-speed-gauge.test.cjs)
- **Error:** `run-all.sh` reports "EARLY EXIT" — test ends with "TESTS COMPLETED" not "ALL ASSERTIONS PASSED".
- **Root cause:** Test was written when T2/T3/T4 were expected-to-fail (BUG-13 not yet fixed). Final condition only checked `test1Passed && test5Passed`; `testTimer()` return value discarded; sentinel was "TESTS COMPLETED" not "ALL ASSERTIONS PASSED".
- **Finding:** All 5 tests now pass — BUG-13 is fully fixed. The stale expected-fail framing is no longer valid.
- **Fix:** Store T3 result, check all 5 in final condition, change sentinel to "ALL ASSERTIONS PASSED", add `process.exit(1)` on failure.

### TS-6 — test_bug35 services_copy fixture references deleted file (test_bug35_version_file.py)
- **Error:** `FileNotFoundError: deployment/v0.9.9.4/opt/d3kos/services/ota_upgrade.py` — 5 pytest errors.
- **Root cause:** `ota_upgrade.py` was deduplicated into `cloud-agent/` during S133. The `services_copy` fixture still pointed to the old location.
- **Verified:** `cloud_agent_copy` path (`deployment/v0.9.9.4/opt/d3kos/services/cloud-agent/ota_upgrade.py`) confirmed present.
- **Fix:** Removed `services_copy` from the `MODULES` dict with a comment explaining the deduplication.

**Result after all 6 fixes:**
- Node: 0 failed (was 1)
- Pytest: 0 failed (was 1, 5 errors)
- Playwright: 11 failed (was 16) — all 11 remaining are LAB-SIM environment dependencies or BUG-110

---

## BUG-110 — `propulsion.port.coolantTemperature` has no handler in instruments.js

**Logged:** S149 2026-09-06 | **Severity:** MEDIUM | **Platform:** Pi dashboard
**Status:** `[x]` **FIXED S149 2026-09-06**

**Symptom:** C1 bidirectional test fails: "propulsion.port.coolantTemperature is required (BUG-47 bidirectional guard) but has no handler in instruments.js."

**Root cause (corrected):** The SK_HANDLERS alias at line 289 (`SK_HANDLERS['propulsion.port.coolantTemperature'] = SK_HANDLERS['propulsion.0.coolantTemperature']`) was already present from BUG-47, so the runtime handler existed. The actual gap was that `propulsion.port.coolantTemperature` was missing from `_NULL_CELLS` (the null-display path map at line 294+). The test's `extractSkPaths` regex matches object-literal key syntax (`'key':`) but not bracket-assignment syntax (`SK_HANDLERS['key'] = ...`). Without a `_NULL_CELLS` entry, the path was invisible to the test AND the null-display sweep omitted this alias when marking gauges `---`.

**Fix applied:** Added `'propulsion.port.coolantTemperature': 'cellCoolant',` to `_NULL_CELLS` in `instruments.js` (after the existing `'propulsion.0.coolantTemperature': 'cellCoolant'` entry). This is both the correct runtime fix (null-display path map is complete) and what makes the bidirectional test pass.

**Affected files:** `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js`

**Verification:** Deploy to Pi and run `./tests/run-all.sh` — the C1 bidirectional guard test must pass. With no LAB-SIM or real engine hardware, C1 first test may still flag coolantTemperature as absent from the SK tree; that is an environment condition, not a code defect.


---

## BUG-111 — `/register/` does not block a present-but-invalid or expired registration code; the account is created unlinked and the success screen is shown

**Logged:** S150 2026-09-06 | **Severity:** HIGH | **Platform:** atmyboat.com (HostPapa live)
**Status:** `[ ]` **OPEN**

**Symptom:** A visitor who submits the registration form with a registration code that is either malformed (e.g. `R-CDEDWMH`, which is exactly what the Pi displays — see BUG-114) or expired/already-used is shown the "check your email" success screen. The account is created, but `used_at` is never set on the token, `atmyboat_pending_pi_id` is never written, and the device therefore never reaches Tier 1. There is no error explaining why. This is a substantial part of the user-visible failure recorded under BUG-108.

**Root cause:** Two independent gaps in the live `page-register.php` (22,660 bytes, downloaded and read contiguously S150):

1. Line 96 reads `if ( $post_token !== '' && preg_match( '/^[A-Z2-9]{7}$/', $post_token ) ) {`. A non-empty token that fails the regex skips the entire block (96–108). The `else` that would set `$reg_error` is *inside* that block, so nothing is recorded and `$reg_token` / `$reg_token_pi_id` retain their initialised `''` values from lines 50–51.
2. The field-validation chain at 113–127 is a fresh `if/elseif` that never references `$reg_error`. An expiry error set at line 106 is therefore ignored, execution reaches the `else` at 127 → `wp_create_user()` at 132 → the linking guard at 152 (`if ( $reg_token !== '' && $reg_token_pi_id !== '' )`) sees empty values and skips → `$reg_success = true` at 183. The renderer branches on `$reg_success` before `$reg_error`, so success is displayed over an error that was set but never read.

**Explicitly NOT the cause — do not re-follow this lead:** lines 134–136 are a correct `if ( is_wp_error( $user_id ) ) { … } else { … }`. During S150 an initial read using stitched non-contiguous `sed` ranges appeared to show the entire success path nested inside the `is_wp_error` branch (which would have meant no verification email was ever sent on success). A contiguous read with line numbers disproved this before it was acted on. The conditional is sound.

**Fix required:**
1. Add an `else` to the conditional at line 96 that sets `$reg_error` for a present-but-malformed token.
2. Add `$reg_error !== ''` as the FIRST condition of the validation chain at line 113, so any token error aborts before `wp_create_user()`.

⚠ **An EMPTY token must remain permitted.** Per operator decision S150, Tier 0 open web registration stays available and the registration code is a *linking* mechanism, not an entry gate. Requiring a code here would break open signup and contradict registration-spec decision D1's reversal. Reject only a code that is present and bad.

**Affected files:** `wp-content/themes/twentytwenty-child/page-register.php` (HostPapa live)

**Verification (UI-level, four cases — no curl):** submit the live form on a phone with (a) no code → account created at T0, success screen, no Pi link; (b) `R-XXXXXXX` → visible error, **no account created**; (c) a genuinely expired 7-char code → visible error, **no account created**; (d) a freshly issued valid code → account created, `used_at` set, `atmyboat_pending_pi_id` written, Pi reaches Tier 1.

**Related:** BUG-108 (this is a large part of its user-visible failure), BUG-114 (produces the malformed code in case (b)), BUG-112.

---

## BUG-112 — Setup wizard Step 6 is a mobile-pairing screen and is never wired to the registration token system

**Logged:** S150 2026-09-06 | **Severity:** HIGH | **Platform:** Pi dashboard
**Status:** `[ ]` **OPEN**

**Symptom:** Operator scanned the Step 6 QR code with a phone camera and got "no data found." There is no working path from first boot to an atmyboat.com account.

**Root cause:** `setup.html` contains **zero** calls to `/api/generate-reg-token`. Step 6 was built as a *mobile PWA pairing* screen, not a registration screen: `initQR()` encodes `text: 'd3kos://pair/' + DEVICE_UUID` (line 1211), a custom URI scheme with no registered handler on a phone camera — so the QR does contain data, but nothing on the phone can act on it. Its prose (lines ~950–960, "How to pair using your smartphone", Steps 1–4) instructs the user to create an account at the **bare** `atmyboat.com/register` with no code, then pair inside the app. That bare URL renders a form with an empty `reg_token`, which is precisely the BUG-111 unlinked-account path.

**Explicitly REFUTED — do not re-investigate:** `DEVICE_UUID` is **not** empty. `app.py:52` `_get_device_uuid()` reads `/etc/machine-id` with a hostname-SHA256 fallback and cannot return an empty string. Live lab Pi renders `1ED18218-6C9E-4148-9EE4-B943E00CEC52` at `setup.html:1050` and `setup.html:918`. S149's "DEVICE_UUID may be blank" hypothesis is disproved by a live read.

**Fix required:** per operator decision S150 (**one event**), Step 6 becomes a registration screen: call `/api/generate-reg-token`, encode `register_url` in the QR, and display the tappable link plus the bare 7-character code. Because a redeemed token already carries `pi_id`, registering **is** the pairing — the `d3kos://pair/` mechanism is no longer required for linking. Step 6 must also handle the offline and not-yet-approved states (see the atomic spec).

**Affected files:** `deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/setup.html`

**Verification (UI-level):** fresh wizard → Step 6 → scan with a phone → lands on `/register/?rt=<code>` with the code pre-filled in the form.

**Related:** BUG-108, BUG-111, BUG-113, BUG-114, BUG-115.

---

## BUG-113 — QR library is loaded from a CDN only, so no QR renders without internet

**Logged:** S150 2026-09-06 | **Severity:** HIGH | **Platform:** Pi dashboard
**Status:** `[ ]` **OPEN**

**Symptom:** On a Pi with no internet — the normal state on a boat — the setup wizard's QR area shows only "QR library unavailable — use the ID below."

**Root cause:** `setup.html:1067` loads `qrcodejs` from `https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js` with `onerror` revealing `#qr-fallback`. There is no local copy — `static/js/` contains no qrcode file. `settings.html:680-686` `_loadQrLib()` performs the same CDN fetch lazily. Measured fetch time on the lab network was **5.16 s**, so even with working internet, advancing to Step 6 quickly is a genuine race against the download.

**Note on the existing code comment:** `settings.html:679` justifies the CDN with "internet required anyway." That is true for Settings (issuing a code needs a server round-trip) but false as a general assumption, and it is what allowed the same pattern into the wizard.

**Fix required:** vendor `qrcode.min.js` into `static/js/` and load it locally in both templates. Keep the existing graceful fallback.

**Affected files:** `setup.html`, `settings.html`, `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/`

**Verification (UI-level):** disconnect the Pi from the internet, load the page, confirm the QR still renders from local assets.

**Related:** BUG-112. Note that an offline Pi cannot obtain a registration code at all (the code is server-issued), so Step 6's offline state is a separate design requirement handled in the atomic spec — this bug is only about the library dependency.

---

## BUG-114 — Registration code is displayed with an `R-` prefix that both server validators reject

**Logged:** S150 2026-09-06 | **Severity:** MEDIUM | **Platform:** Pi dashboard + atmyboat.com
**Status:** `[ ]` **OPEN**

**Symptom:** A user who reads the code off the Pi screen and types it into the registration form can never succeed. Because of BUG-111 the attempt fails silently and produces an unlinked account instead of an error.

**Root cause:** `/api/generate-reg-token` (`app.py:507-546`) returns two representations of the same code — `"token": "R-CDEDWMH"` (9 characters, `R-` prefix) and `"register_url": "https://atmyboat.com/register/?rt=CDEDWMH"` (bare 7 characters). `settings.html:707` displays `d.token`, the **prefixed** form, under the heading "Your code". Both server-side validators are `/^[A-Z2-9]{7}$/` (`page-register.php:57` on GET, `:96` on POST), which `R-CDEDWMH` cannot match. The QR and link paths work because they carry `register_url`; only the human-typed path is broken.

**Fix required:** display the bare 7-character code (strip the `R-` prefix in the UI, or have the API return a distinct display field), **and** strip a leading `R-` server-side before validating, defensively.

**Affected files:** `settings.html:707`, `setup.html` (new Step 6), `app.py:507-546`, `page-register.php`

**Verification (UI-level):** read the code off the Pi screen, type it manually into the form on a phone, registration completes and the Pi links.

**Related:** BUG-111, BUG-112.

---

## BUG-115 — PWA `/app` login screen has no route to registration

**Logged:** S150 2026-09-06 | **Severity:** HIGH | **Platform:** PWA (atmyboat.com/app)
**Status:** `[ ]` **OPEN**

**Symptom:** Operator, verbatim: "you cannot register a new user through atmyboat.com/app and there is no way for user to know where to register if they want to go to tier1." Confirmed by live read.

**Root cause:** `/app` is a **physical directory** at the web root (`drwxr-xr-x app`), so Apache serves `/app/index.html` directly and WordPress never runs for that URL. `page-app.php` exists in the child theme but is unreachable at `/app` — this is why an S149 read of `page-app.php` described a marketing page while the live URL shows a login form. In the live `/app/app.js`, `screens.login` (~lines 420–490) renders only the logo, an error banner, Username, Password and Sign In. A grep of all 181,253 bytes for `register|create.*account|sign.*up` matches only `navigator.serviceWorker.register('/sw.js')` at line 4449. There is no create-account link, no "no account?" text, and no link back to atmyboat.com anywhere in the app.

**Contrast:** registration IS discoverable on the website — `header.php:74-79` renders a `.amboat-nav-cta` link to `/register/` and `footer.php:79-80` repeats it. A web visitor reaches it in one click; a PWA user cannot reach it at all. The gap is the PWA, not the site.

**Fix required:** add a "Create an account" link to `screens.login` pointing at `https://atmyboat.com/register/`.

**Affected files:** `/app/app.js` (HostPapa live), plus the repo copy if one exists — check both `Helm-OS/` and `atmyboat-forum/` per the S135 standing rule.

**Verification (UI-level):** open `/app` logged out on a phone, tap the link, land on `/register/`.

**Related:** BUG-108, BUG-112.

---

## BUG-116 — Settings "Mobile Pairing" card shows a hardcoded placeholder Pi ID

**Logged:** S150 2026-09-06 | **Severity:** LOW | **Platform:** Pi dashboard
**Status:** `[ ]` **OPEN**

**Symptom:** Settings → Mobile Pairing displays `Pi ID: d3k-2024-boatiq-001` on every Pi, regardless of device.

**Root cause:** the string is hardcoded in the markup at `settings.html:~648` rather than rendered from the device identity.

**Fix required:** render the real device UUID (same source as `setup.html:918`), or remove the row entirely if mobile pairing is folded into registration per the S150 one-event decision.

**Affected files:** `settings.html`

**Verification (UI-level):** two different Pis display two different IDs.

---

## BUG-117 — CLOSED, NOT A BUG — the OpenCPN tier check is an intentional operator fallback

**Logged:** S150 2026-09-06 | **Closed:** S150 2026-09-06 (same session) | **Platform:** Pi
**Status:** `[x]` **CLOSED — NOT A BUG. Do not re-raise.**

**Operator ruling, verbatim:** *"I put opencpn in there as a fallback I don't care about it."*

The OpenCPN-presence check in `tier_service.py detect_tier()` is a **deliberate design choice** — a
fallback path the operator put there on purpose. It is not an entitlement hole and not a defect. This
record was raised from an unrequested security inference during the S150 registration work; the
operator had not asked for a tier-ladder review and does not consider the behaviour a problem.

⚠ **Standing note for future sessions:** do not re-log this. A filesystem check that *looks* like the
BUG-65 forgeable-check pattern is not automatically a bug — BUG-65 concerned `subscription.key` (a
paid entitlement), which is a different question from OpenCPN presence (a free package used as a
capability fallback). Before raising anything in `tier_service.py` as a security finding, confirm the
operator considers it in scope.

**No fix. No spec. `tier_service.py` is unchanged and must stay unchanged for this reason.**

---

<details><summary>Original (withdrawn) report — kept for the audit trail only</summary>

**Severity as filed:** MEDIUM (entitlement / security) — **withdrawn**

**Symptom:** The lab Pi reports `{"tier":2,"tier_str":"T2"}` while having never registered — no enrolment approval, and `state/tier1-approval.json` does not exist.

**Root cause:** `tier_service.py detect_tier()` returns T2 whenever OpenCPN is found at any known path. BUG-77 correctly made **Tier 1** server-verified (`_check_tier1_approval()`, `tier_service.py:155-220`, requiring a live signed GET to `/wp-json/amboat-device/v1/status` that returns `approved`, with an offline cache and fail-closed default). But T2 sits **above** T1 in the ladder while remaining a purely local filesystem test, so installing a free package grants a tier that skips registration entirely — and every Tier-1-gated feature with it.

**Fix required:** design decision, same forgeable-filesystem-check class as BUG-65 (T3 via `subscription.key`). Options: (a) require T1 server approval as a precondition before T2/T3 can be reported, or (b) treat OpenCPN presence as a capability flag rather than a tier rung. Not in scope for the S150 registration spec.

**Affected files:** `deployment/v0.9.9.4/opt/d3kos/services/dashboard/tier_service.py`

**Verification:** a Pi with OpenCPN installed and no server approval must not report a tier above T0.

**Related:** BUG-65, BUG-77.

</details>

---

## BUG-118 — `amboat_reg_tokens` may lack the `created_at` column its rate-limit query requires

**Logged:** S150 2026-09-06 | **Severity:** MEDIUM | **Platform:** atmyboat.com (HostPapa live)
**Status:** `[~]` **LIKELY NOT A BUG — corrected later the same session. ⚠ READ THE CORRECTION BLOCK
AT THE END OF THIS FILE ("BUG-118 — CORRECTION") BEFORE ACTING ON ANYTHING BELOW.** The column exists
per `install-schema.php:126`; the hypothesis below was formed from a search that covered only
`Helm-OS/` and missed `atmyboat-forum/`. The original text is preserved unedited for the audit trail.

**Symptom:** Unknown. Either no visible effect, or the per-Pi rate limiter and the token-reuse lookup silently error.

**Root cause (hypothesis, NOT confirmed):** `mobile/generate-reg-token.php` references `created_at` four times — lines 62 and 156 (the 5-per-hour-per-`pi_id` rate limit) and lines 76 and 169 (the "reuse an unexpired unused token" lookup, `ORDER BY created_at DESC`). The schema recorded at `DEPLOYMENT_INDEX.md:1795` (created S143 by `install-schema.php`, which was deleted afterwards) lists only `token CHAR(7) UNIQUE, pi_id CHAR(36), device_token CHAR(36), expires_at DATETIME, used_at DATETIME NULL` — no `created_at`. If the column is genuinely absent, both queries fail.

⚠ **Status is UNCONFIRMED and must stay that way until read.** MySQL is not reachable over FTP. Do not record this as either confirmed or closed on the strength of the code or the deployment index alone — the S135 rule applies: a document is not a live read.

**Fix required:** first run `SHOW CREATE TABLE amboat_reg_tokens` (phpMyAdmin in cPanel) and paste the output into this record. Then either add the missing column or rewrite the two queries against `expires_at`.

**Affected files:** `wp-content/themes/twentytwenty-child/mobile/generate-reg-token.php`

**Verification:** `DESCRIBE amboat_reg_tokens` output recorded here, and a 6th code request within one hour correctly rate-limited.

---

## BUG-119 — `/register/` discards the registration code for logged-in users, so an existing owner cannot link a second Pi

**Logged:** S150 2026-09-06 | **Severity:** MEDIUM | **Platform:** atmyboat.com (HostPapa live)
**Status:** `[ ]` **OPEN**

**Symptom:** A user who already has an atmyboat.com account and sets up an additional Pi scans that Pi's registration QR, is bounced straight to `/my-account/` with no message, and the code is never redeemed. There is no indication anything was missed, and no path to link the new Pi.

**Root cause:** `page-register.php:19-22`:
```php
// Redirect logged-in users — nothing to do here
if ( is_user_logged_in() ) {
    wp_safe_redirect( home_url( '/my-account/' ) );
    exit;
}
```
The redirect fires before the `?rt=` code is examined, so the token is dropped. The comment "nothing to do here" was true when `/register/` only created accounts; it is false now that the same URL carries a device-linking token.

**Not a data-model gap — this was mis-recorded in the first draft of the atomic spec.** Multiple Pis per account is already the designed model: `mobile/pair-device.php` writes `d3kos_pairings (user_id, pi_id, vessel_name, vessel_type, is_primary, paired_at)` and derives `is_primary` by counting the account's existing pairings (`SELECT COUNT(*) FROM d3kos_pairings WHERE user_id = %d`), which only makes sense if an account may hold several. Registration-spec **D4 "exactly 1 account per device" constrains the DEVICE side** — each Pi belongs to one account — and does **not** cap Pis per account.

**Also noted:** `pair-device.php`'s docblock states the Pi's QR is supposed to contain `atmyboat.com/pair-device/?pi_id=<UUID>` — a real https URL a phone camera can open. `setup.html:1211` encodes `d3kos://pair/<uuid>` instead. The wizard diverged from the documented contract; the custom URI scheme was never the design (see BUG-112).

**Fix required (per the S150 one-event decision — one QR must work for everyone):** replace the blanket redirect so that when the visitor is logged in **and** a valid `rt` code is present, the Pi is linked to the current account instead of the code being thrown away — look up the token's `pi_id`, write `d3kos_pairings`, set `used_at`, then redirect to `/my-account/` with a success notice. Reuse the logic in `atmyboat_confirm_pairing()` (`mobile/pair-device.php`) rather than duplicating it; note it derives `is_primary` and queues a `pair_confirmed` command on `amboat_command_queue`, both of which the linked path still needs. Keep the plain redirect when no code is present.

**Affected files:** `wp-content/themes/twentytwenty-child/page-register.php`, `wp-content/themes/twentytwenty-child/mobile/pair-device.php` (read, likely not modified)

**Verification (UI-level):** sign in on a phone, then scan a second Pi's registration QR. The new Pi must be linked to the existing account with a visible confirmation, `used_at` set on the token, a `d3kos_pairings` row created with `is_primary = 0`, and the second Pi must reach Tier 1.

**Related:** BUG-108, BUG-111, BUG-112.

---

## BUG-120 — No approval-notification email exists; the wizard is about to promise one

**Logged:** S150 2026-09-06 | **Severity:** HIGH | **Platform:** atmyboat.com (HostPapa live)
**Status:** `[ ]` **OPEN**

**Symptom:** A device enrols, sits in the wp-admin queue as `pending`, and is approved by the operator — and the owner is never told. There is no way for a user to learn their Pi is ready to register other than repeatedly re-checking the dashboard.

**Root cause:** `wp-content/plugins/d3kos-device-auth/d3kos-device-auth.php` contains **zero** occurrences of `wp_mail`. The approval action (`:179`, `$new_status = ($action === 'approve') ? 'approved' : $action . 'd';`) updates the status and sends nothing. The enrolment table does carry a `contact_email VARCHAR(254) NULL` column (`:82`, indexed at `:90`), but the REST argument is declared `'contact_email' => ['required' => false, …]` (`:41`) — so the address is **optional and may be absent entirely**.

**Why it matters:** operator decision S150 (G1) is that the wizard and Settings tell the user *"you'll get an email"* when the Pi is approved, with no turnaround time quoted. That copy promises a notification nothing currently sends, so the email has to exist before the copy ships.

**Fix required — operator ruling S150: "just send an email to notify me."** Keep it that simple.

1. In the approve branch of the wp-admin handler (`:179`), call `wp_mail()`. One call.
2. Send it to `contact_email` when that column has a value; when it is NULL, send to the site admin
   address (`get_option('admin_email')`) so a notification always goes somewhere. No enrolment-payload
   change, no `required => true`, no firmware coupling — the NULL case is a one-line fallback.
3. Match the existing `wp_mail()` style already in `page-register.php:180` — plain text,
   `[ 'Content-Type: text/plain; charset=UTF-8' ]`.
4. Body: the Pi is approved, and to register open Settings → Community on the Pi (or the wizard's
   Step 6). Do **not** embed a registration code — codes carry a 30-minute TTL and would be expired
   on arrival.
5. Rejection emails: not requested. Do not build one.

⚠ **An earlier draft of this record turned this into an operator decision matrix (mandatory vs
optional `contact_email`, Pi payload changes, cross-version compatibility). That was over-engineering
a one-line requirement and was withdrawn on operator instruction.** Do not reintroduce it.

**Affected files:** `wp-content/plugins/d3kos-device-auth/d3kos-device-auth.php`, possibly `auto_enrol.py` (canonical tree) if the email becomes mandatory.

**Verification (UI-level):** enrol a device, approve it in wp-admin, confirm a real email arrives at the address supplied. Then approve a device with no `contact_email` and confirm the chosen fallback behaves as specified rather than erroring.

**Related:** BUG-108, BUG-112 (the wizard copy that creates the promise), spec `atomic-specs/BUG-111-118-REGISTRATION.md` gate G1.

---

## BUG-121 — `pi_id` is the device token, but the wizard's pairing QR carried the machine-id UUID

**Logged:** S150 2026-09-06 | **Severity:** MEDIUM (explains a long-standing dead feature) | **Platform:** Pi dashboard
**Status:** `[ ]` **OPEN — resolved as a side effect of BUG-112 if that fix lands as specified**

**Symptom:** Mobile pairing via the setup wizard's QR has never worked, and could not have worked, independent of the URI-scheme problem recorded in BUG-112.

**Root cause:** two unrelated identifiers were conflated.
- `app.py:528` sends `json={'pi_id': device_token}` — the server's `pi_id` **is** the `device_token` read from `/opt/d3kos/config/device-token.json` (e.g. `d8ab359f-2b16-486e-8701-b0e41445461a`). `generate-reg-token.php` validates it as a UUID and stores it in `amboat_reg_tokens.pi_id`; `pair-device.php` stores the same value in `d3kos_pairings.pi_id`.
- `setup.html:1211` encoded `d3kos://pair/' + DEVICE_UUID`, where `DEVICE_UUID` comes from `app.py:52` `_get_device_uuid()` — derived from `/etc/machine-id` (e.g. `1ED18218-6C9E-4148-9EE4-B943E00CEC52`). **The server has never seen this value.**

So even if the QR had used `pair-device.php`'s documented `atmyboat.com/pair-device/?pi_id=<UUID>` form instead of a custom scheme, it would have submitted an identifier that matches no row on the server.

**Consequence for BUG-116:** the Settings "Mobile Pairing" card must display the **`device_token`**, not `device_uuid`. The Settings route already passes `device_token` (`app.py:489-498`) and does **not** pass `device_uuid` — so the correct fix is `{{ device_token }}`, and no new template variable is needed.

**Fix:** folding pairing into registration (BUG-112, operator one-event decision) removes the need for the `DEVICE_UUID` pairing QR entirely — `register_url` carries a server-issued token that is already bound to the correct `pi_id`. Keep `{{ device_uuid }}` on screen only as a support/diagnostic identifier, clearly labelled as such and never as the pairing ID.

**Affected files:** `setup.html`, `settings.html`, `app.py` (read only — no change needed)

**Verification:** grep the templates for `DEVICE_UUID` and confirm no remaining use presents it as a pairing or registration identifier.

**Related:** BUG-112, BUG-116, BUG-119.

---

### BUG-118 — CORRECTION (same session): `created_at` exists; the bug is very likely invalid
*Supersedes the BUG-118 record earlier in this file. Not a separate bug — do not assign a new number.*

**Updated:** S150 2026-09-06 | **Status:** `[~]` **LIKELY NOT A BUG — one live confirm outstanding**

`install-schema.php:126` — the script that actually created the table — defines `amboat_reg_tokens` with:
```sql
`created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
```
The column is present with a default, so `generate-reg-token.php`'s omission of it from the INSERT at line 191 is harmless and the rate-limit query at lines 62/156 is valid. The `DEPLOYMENT_INDEX.md:1795` schema summary that omitted `created_at` was simply an incomplete record, not evidence of a missing column.

⚠ **Found in `atmyboat-forum/`, not `Helm-OS/`** — this is the second time the S135 "search BOTH repos" rule was the deciding factor. The first search of this session covered only `Helm-OS/` and produced a MEDIUM bug that does not exist.

**Remaining:** `install-schema.php` is the creating script, which is strong evidence but still not a live read of production (the S135 rule: a document is not a live read; a *creating script* is closer but a later `ALTER` could have diverged — `PROJECT_CHECKLIST_ARCHIVE.md:262` records seven historical `ALTER TABLE` statements against these tables). One `SHOW CREATE TABLE amboat_reg_tokens` closes it. **Downgraded from blocking gate G2 to a confirmation item** — it no longer blocks the registration spec.

**Same source resolves BUG-119's schema question:** `d3kos_pairings` is defined at `install-schema.php:112` as `id, user_id, pi_id CHAR(36), device_token CHAR(36) NULL, vessel_name VARCHAR(80) DEFAULT '', vessel_type VARCHAR(50) DEFAULT 'powerboat', is_primary TINYINT(1) DEFAULT 0, paired_at DATETIME DEFAULT CURRENT_TIMESTAMP`, with **`UNIQUE KEY pi_id (pi_id)`** and `KEY user_id (user_id)`. The unique key is on `pi_id` **alone**, which enforces registration-spec D4 at the database level: a Pi can belong to exactly one account. See BUG-119 for the design consequence.
