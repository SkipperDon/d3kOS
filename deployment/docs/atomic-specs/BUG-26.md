# Atomic Spec — BUG-26 (Anchor Watch "Set Anchor" fails — wrong origin)

**Format:** AAO §23.5 / §25. Created 2026-07-23 by Tier 1 (Opus).
**Tracker:** `V09994_BUG_FIXES.md` BUG-26 · Diagnosis: `runbooks/GROUP-A-services.md`

## Tier-1 finding (confirmed on Pi 192.168.1.237)
Anchor endpoints are served by **ai-bridge on `:3002`** — verified live: `GET /anchor/set`
→ 405 (exists, POST-only), `/anchor/state` → 200; ai-bridge source defines `/anchor/set`,
`/anchor/clear`, `/anchor/dismiss`, `/anchor/advice`, `/anchor/state`, `/anchor/activate`.
The **dashboard `:3000` serves NONE** (all 404). `anchor-watch.html` fetches bare `/anchor/*`,
which resolve to `:3000` → 404 → Set Anchor never arms (K-02).
The SAME file already reaches ai-bridge directly for SSE:
`new EventSource('http://localhost:3002/stream')` (~line 396). So the fix is to route the
anchor fetches to that same `:3002` base. Backend is fine — this is a frontend origin bug.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-26  (AAO §23.5 · §25)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : Anchor Watch "Set Anchor" fails — the page calls /anchor/* on the
            dashboard origin (:3000, no such routes → 404) instead of ai-bridge (:3002).

CONTEXT (read ONLY this file)
  templates/anchor-watch.html
  (dashboard dir: deployment/d3kOS/dashboard/templates/anchor-watch.html)

ROOT CAUSE (confirmed on Pi)
  ai-bridge (:3002) serves /anchor/set|clear|dismiss|advice|state.
  Dashboard (:3000) serves none. anchor-watch.html fetches bare '/anchor/*' → 404.

CHANGE (this file only)
  1. Near the top of the page <script> (~line 182, before function setAnchor), add:
        const AI_BRIDGE = 'http://localhost:3002';
     (matches ai-bridge.js and the existing SSE base already used in THIS file.)
  2. Prefix ALL FIVE anchor fetch() URLs with AI_BRIDGE (change ONLY the URL arg):
        fetch('/anchor/set'      → fetch(AI_BRIDGE + '/anchor/set'      (~line 294)
        fetch('/anchor/clear'    → fetch(AI_BRIDGE + '/anchor/clear'    (~line 311)
        fetch('/anchor/dismiss'  → fetch(AI_BRIDGE + '/anchor/dismiss'  (~line 317)
        fetch('/anchor/advice'   → fetch(AI_BRIDGE + '/anchor/advice'   (~line 329)
        fetch('/anchor/state'    → fetch(AI_BRIDGE + '/anchor/state'    (~line 343)
     Keep method / headers / body / .then handlers identical.

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT change the SSE EventSource line (already http://localhost:3002) — leave as-is.
  • Do NOT change request bodies, headers, methods, or response handlers.
  • Do NOT edit app.py or add backend routes — the backend already exists on :3002.
  • Do NOT edit any file other than anchor-watch.html.

FAILING TEST FIRST (TDD)
  Ideal (Playwright, route interception): click #btn-set → assert the outbound request
  URL is http://localhost:3002/anchor/set (BEFORE the fix it is same-origin :3000).
  KNOWN ENV LIMITATION — PRE-APPROVED SUBSTITUTION (§25.5.1): Playwright browser deps are
  unavailable in the Tier-3 env. If Playwright cannot run, substitute a source check that
  asserts (a) all 5 anchor fetch() calls are prefixed with AI_BRIDGE and (b) NO bare
  fetch('/anchor/ remains — AND create the Playwright test file for later. Document it in
  the Decision Log. This substitution is pre-approved for the browser-dep case ONLY;
  escalate if anything else blocks you.

DONE WHEN
  • Test fails before / passes after (or source check: 0 bare '/anchor/' fetches; 5 AI_BRIDGE-prefixed).
  • git diff shows ONLY the const addition + 5 URL prefixes in anchor-watch.html — nothing else.

ESCALATE-IF (🔺 block — do NOT guess)
  • The 5 fetch calls are not at the described lines / have a different shape → CLARIFICATION
  • anchor-watch.html already defines AI_BRIDGE or a conflicting const → ADVICE
  • Anything beyond anchor-watch.html appears required → ADVICE (scope)

PRE-FLIGHT SELF-CHECK (answer from THIS spec; else escalate)
  1. Which file? → anchor-watch.html only
  2. What proves done? → 5 fetches point at AI_BRIDGE; diff = const + 5 prefixes
  3. Forbidden? → SSE line, bodies/headers/methods/handlers, app.py, other files

RETURN TO TIER 1
  • diff · test-or-source-check output · Decision Log (deviation or "none")
═══════════════════════════════════════════════════════════════════════
```

## Tier-1 verification (on return — §25.8)
1. `git diff`: exactly the `const AI_BRIDGE` addition + 5 URL prefixes; nothing else.
2. No bare `fetch('/anchor/` remains; SSE line unchanged; no app.py change.
3. **Cannot verify remotely:** actual arming + alarm audio. On-Pi integration check
   (curl `:3002/anchor/set` responds; after deploy, click SET ANCHOR → status arms;
   alarm plays to the Pi audio device). Operator/Tier-1 does this after deploy.

## Note
Alarm-sound (K-03) is downstream of arming — retest once Set Anchor works. Audio playback
device exists on the Pi (card 2 Headphones); on-boat speaker routing may differ.
