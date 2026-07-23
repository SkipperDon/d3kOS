# Atomic Spec — BUG-27 (Helm status bar text not readable at 1 m — AODA)

**Format:** AAO §23.5 Atomic Spec, §25 escalation-enabled (see
`aao-methodology-repo/docs/TIER_ESCALATION_AND_VERIFICATION_PROTOCOL.md`)
**Created:** 2026-07-23 by Tier 1 (Opus 4.8). Target sizes accepted by operator.
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-27 · PROJECT_CHECKLIST.md PART 17 · checklist item D-09

---

## Tier-1 finding (why the sizes are 28/26, not 18)

The BUG-27 tracker states the root cause is "font size below 18px." **Direct code
inspection contradicts this.** In the helm/main dashboard status bar (`#sb`) of
`deployment/d3kOS/dashboard/static/css/d3kos.css`:

| Element | Selector | Current | Note |
|---|---|---|---|
| Vessel name | `.sb-vessel` (~line 183) | **18px** | exactly AT the AODA floor, not below |
| Clock | `#clk` (~line 246) | **22px** | already above the floor |
| Ticker | `.sb-ticker` (~line 187) | 18px | not reported by operator — OUT OF SCOPE |

The operator reported **both** vessel name and clock illegible at ~1 m on the
10.1" screen, yet both already meet/exceed the 18px minimum. The real defect:
**18px is the AODA accessibility floor, not a readable-at-1-metre size.** The fix
is to raise the two helm-critical, operator-named elements to a helm-distance
size. Target "readable at 1 m" has no numeric definition (Clarification Gate #5),
so Tier 1 recommended and the operator accepted **28px (vessel) / 26px (clock)**.
Final legibility can only be confirmed on the physical screen (Hardware Claim
Protocol — see verification).

`#status-bar` (~line 1046) is the **settings-page** bar, a different component —
explicitly out of scope.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-27  (AAO §23.5 Atomic Spec · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE      : [IMPLEMENT] — Tier 3
BUG            : BUG-27 — Helm status bar text not readable at 1 m (AODA)
GOVERNING RULE : 18px is the AODA FLOOR, not a max. Helm-critical text must be
                 readable at ~1 m on a 10.1" screen.

CONTEXT (read ONLY this file)
  deployment/d3kOS/dashboard/static/css/d3kos.css

TARGET ELEMENTS (helm/main dashboard status bar #sb — NOT the settings bar)
  1. .sb-vessel   — vessel name   — currently font-size: 18px  (~line 183)
  2. #clk         — clock         — currently font-size: 22px  (~line 246)

CHANGE
  .sb-vessel : font-size 18px → 28px
  #clk       : font-size 22px → 26px
  Change font-size ONLY. Touch nothing else in either rule.

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT edit #status-bar or "#status-bar #clock" (~line 1046/1070) — that is
    the SETTINGS page bar, a different component, out of scope.
  • Do NOT edit .sb-ticker (18px) — not part of this bug.
  • Do NOT touch color, height (--sb-h), padding, layout, letter-spacing,
    font-family, or the --ink2/--ink3 opacity tokens.
  • Do NOT edit any file other than d3kos.css.
  • Do NOT deploy to the Pi. Repo edit only — deployment is a separate, operator-
    authorized High-risk step.

INTERFACE CONTRACT
  After the change, getComputedStyle(.sb-vessel).fontSize === "28px"
                    getComputedStyle(#clk).fontSize        === "26px"
  No other computed font-size in the file changes.

FAILING TEST FIRST (TDD — write and run BEFORE the fix; it MUST fail first)
  File: tests/bug27-status-bar-legibility.spec.ts   (Playwright, TypeScript)
  Precondition: dashboard served (Flask app running) at BASE_URL; a vessel_name set.

    import { test, expect } from '@playwright/test';
    const BASE = process.env.BASE_URL ?? 'http://localhost:5000';

    test('BUG-27: helm status bar vessel name is >= 28px', async ({ page }) => {
      await page.goto(BASE + '/');                    // main dashboard (index.html)
      const px = await page.locator('.sb-vessel').first()
        .evaluate(el => parseFloat(getComputedStyle(el).fontSize));
      await expect(px).toBeGreaterThanOrEqual(28);    // fails at current 18px
    });

    test('BUG-27: helm status bar clock is >= 26px', async ({ page }) => {
      await page.goto(BASE + '/');
      const px = await page.locator('#clk').first()
        .evaluate(el => parseFloat(getComputedStyle(el).fontSize));
      await expect(px).toBeGreaterThanOrEqual(26);    // fails at current 22px
    });
  Run: npx playwright test tests/bug27-status-bar-legibility.spec.ts
  Screenshot on failure is Playwright default; keep it.

DONE WHEN
  • Both tests FAILED before the edit and PASS after.
  • git diff shows ONLY two font-size values changed in d3kos.css. Nothing else.

ESCALATE-IF  (emit the 🔺 ESCALATION block — do NOT guess)
  • .sb-vessel or #clk is NOT found in d3kos.css, or its current value is not
    18px / 22px respectively            → CLARIFICATION (Pi/repo may differ)
  • You cannot make either test FAIL before the fix
                                        → SOLUTION-REQUEST (test/setup problem)
  • The fix appears to need any file other than d3kos.css
                                        → ADVICE (scope question)
  • The app won't serve so the test can't run
                                        → CLARIFICATION (how to run the harness)

PRE-FLIGHT SELF-CHECK (answer from THIS spec before coding; if you can't, escalate)
  1. Which file?  → d3kos.css only
  2. What proves done? → both Playwright assertions flip fail→pass, diff = 2 values
  3. What am I forbidden to touch? → #status-bar, .sb-ticker, all non-font-size props

RETURN TO TIER 1
  • The two-line diff
  • Test output showing fail-before / pass-after
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## The escalation block (Tier 3 emits this instead of guessing)

```
🔺 ESCALATION — BUG-27 / <sub-task>
Tier asking     : <Sonnet Tier 3 | Haiku Tier 3>
Type            : [CLARIFICATION | ADVICE | SOLUTION-REQUEST]
Blocking?       : [BLOCKED — cannot proceed | PROCEEDING on assumption below]
Question        : <one specific, bounded question>
Why it blocks   : <what changes in the code depending on the answer>
Options I see   : (1) ...  (2) ...
My provisional  : <best guess> — Confidence: NN/100
If I'm wrong    : <consequence>
```

---

## Tier-1 verification pass (run on Tier 3's return — §25.8)

1. Confirm both tests **failed** at 18px/22px before the edit and **pass** at 28/26 after.
2. `git diff` shows **exactly two** font-size values changed in d3kos.css — `#status-bar` and `.sb-ticker` untouched, no color/layout/token changes.
3. No regression in the stated scope.
4. **Cannot verify remotely (Hardware Claim Protocol):** whether 28/26px is actually
   legible at ~1 m on the physical 10.1" screen. Acceptance for that is an operator
   on-boat/on-Pi check after deploy — NOT something Tier 1 or Tier 3 may claim as done.

## Out of scope for this spec
- Pi deployment of the changed CSS (separate operator-authorized High-risk step).
- `.sb-ticker` (18px) and `#status-bar` (settings page) — not part of BUG-27.
