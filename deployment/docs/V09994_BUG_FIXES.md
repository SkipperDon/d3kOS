# v0.9.9.4 Bug Fixes — Investigation & Status
**Version:** 1.1.0 | **Created:** 2026-04-21 S65 | **Updated:** 2026-04-21 S65 | **Status:** IN PROGRESS

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
