# Group A — Service/Connectivity Bugs · Diagnostic Runbook

**Bugs:** BUG-25 (Gemini can't connect), BUG-26 (Anchor Watch Set Anchor fails), BUG-23 (Boat Log voice note not transcribed)
**Sweep:** 2026-07-23, read-only SSH to HOME Pi `192.168.1.237` (`d3kos`). NOT the boat hotspot — network-dependent checks flagged.
**Format:** diagnostic runbook (not a TDD atomic spec) — these are diagnose-first bugs. No fixes applied; group-fix after review per bug modus operandi.

---

## BUG-25 — AI Navigation (Gemini) cannot connect

**Live findings (home Pi):**
- `d3kos-gemini.service` (port 3001) — **active, enabled**. `/status` → `{"gemini_key":true,"model":"gemini-2.5-flash-lite","online":true}` ✅ key present, correct model, online.
- `d3kos-gemini-proxy.service` (port 8097) — **active, enabled**. `/` → 404 (no root handler, normal); `/gemini/test` → **000 (no response in 5s)**.
- Live config `/opt/d3kos/services/gemini-nav/config/gemini.env` = `gemini-2.5-flash-lite` ✅. The bad `gemini-2.5-flash` (503-prone) appears ONLY in `.bak-*` and `.ota-backup/` files — **not** the active config.
- **`curl https://www.google.com` from the Pi → 000 (no internet egress right now).**

**Most likely cause:** NOT a d3kOS config/service bug. Services are up, key present, model correct. The failure is **network egress** — Gemini needs the internet and the Pi could not reach Google. The `/gemini/test` 000 is consistent with an outbound call hanging. On-boat, the tracker's candidate #5 (hotspot lacks internet) is the prime suspect.

**Remaining checks:**
- [ ] ON-BOAT: from the Pi on the boat network, `curl -m5 https://generativelanguage.googleapis.com` (or google.com) — does it egress? If 000/timeout → connectivity is the bug, not d3kOS.
- [ ] Confirm the boat hotspot actually has upstream internet (phone data on, not just LAN).
- [ ] If internet IS present but Gemini still fails: `journalctl -u d3kos-gemini -n 40` and re-test `/gemini/test`.

**Recommended:** reclassify BUG-25 as connectivity/environment unless on-boot internet is confirmed present AND Gemini still fails. Do not change config — it is correct.

---

## BUG-26 — Anchor Watch "Set Anchor" fails (K-02); no alarm (K-03)

**Live findings:**
- No `d3kos-anchor*` service. Anchor Watch is a dashboard page route only: `app.py:588 @app.route('/anchor-watch')`.
- `anchor-watch.html:291 setAnchor()` → `fetch('/anchor/set', {POST})` — a **same-origin** call to the dashboard (`:3000`). Also `/anchor/clear`, `/anchor/dismiss`, `/anchor/state`, `/anchor/advice`.
- `app.py` defines **no `/anchor/set` route** (grep `@app.route(.*anchor` returns only `/anchor-watch`).
- Inconsistency: `ai-bridge.js` calls `AI_BRIDGE (:3002) + '/anchor/dismiss'`, but `anchor-watch.html` calls bare `/anchor/set` on `:3000`.
- Audio playback devices present at home: HDMI ×2 + `card 2 bcm2835 Headphones`.

**Most likely cause:** endpoint mismatch — the page POSTs to `/anchor/set` on the dashboard origin, but that route isn't served there (likely 404), so arming never happens (K-02). Alarm (K-03) can't be reached because anchor was never set.

**Remaining checks:**
- [ ] `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:3000/anchor/set` on the Pi — expect 404 if the route is missing.
- [ ] Grep for a blueprint / other .py in the dashboard dir registering `/anchor/*`; check if anything proxies `:3000/anchor/*` → `:3002` (ai-bridge). If ai-bridge owns anchor state, the page should call `AI_BRIDGE + '/anchor/set'`, not `/anchor/set`.
- [ ] Once arming works: test alarm playback to `card 2` (on-boat speaker device may differ).

**Recommended fix (after confirm):** either add the `/anchor/set` (+ clear/state/advice) routes to the dashboard, or point `anchor-watch.html` at the correct base URL (AI_BRIDGE) — TBD by where anchor state is actually managed. This is a real code bug, not a stopped service.

---

## BUG-23 — Boat Log voice note not transcribed (H-03)

**Live findings:**
- `d3kos-boatlog-api.service` — active, enabled ✅.
- `d3kos-voice.service` ("Hybrid Voice Assistant", `voice-assistant-hybrid.py`) — active, but degraded.
- `d3kos-voice-watchdog.service` — **FAILED**: log says *"Only 1 thread(s) running (expected 2+). Restarting… CRITICAL: Restart failed - still only 1 thread(s)."* The voice subsystem is running under-strength.
- No `whisper` / `faster-whisper` / `stt` service found. (Faster-Whisper STT is a v0.9.9.5 D13 future item, not built.)
- **No capture (mic) device** in `arecord -l` at home — but the USB mic is likely boat-only.

**Most likely cause:** unresolved — two candidate threads: (a) the voice subsystem is degraded (watchdog failing on thread count), and/or (b) there is no local STT engine, so boat-log transcription may depend on the voice assistant or a path that isn't wired. The mic being absent at home blocks record-testing here.

**Remaining checks:**
- [ ] Trace the boat-log voice-note path: which endpoint does the record→stop UI POST to, and what performs transcription? (`grep -rn voice /opt/d3kos/services/dashboard/... ` + boatlog-api source.)
- [ ] `journalctl -u d3kos-voice -n 60` — why only 1 thread? Is STT a thread of the voice assistant?
- [ ] Decide whether voice-note transcription is even implemented locally, or was assumed (relate to D13 Faster-Whisper, which is NOT built).
- [ ] ON-BOAT: with the USB mic connected, `arecord -l` shows a capture device; record a test note and watch `journalctl -u d3kos-boatlog-api -f`.

**Recommended:** do not restart the watchdog blindly — find why the voice assistant runs with 1 thread first. Likely a real subsystem/feature-gap bug, possibly a "not built" gap for STT.

---

## Summary for review (group-fix, do not one-off)

| Bug | Verdict from sweep | Type |
|---|---|---|
| BUG-25 | Services UP, config CORRECT, :3001 online — failure is **internet egress** (google=000). | Connectivity/env, likely NOT a d3kOS bug |
| BUG-26 | `/anchor/set` POSTed to `:3000` but no such route — endpoint mismatch. | Real code bug |
| BUG-23 | voice-watchdog FAILED (1 thread), no local STT service found, no mic at home. | Subsystem degraded and/or feature gap |

**On-boat-only confirmations needed:** BUG-25 internet egress on hotspot; BUG-23 mic capture + record test. Everything else is confirmable from the home Pi.
