# Atomic Spec — BUG-38 (`overlays.js` writes to three DOM IDs `index.html` never defines)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-27 (S108) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-38 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** `wiki/questions/2026-07-27-v0994-tier3-spec-questions.md` — **read Q0.1–Q0.5 and Q38.1–Q38.3 first**
**Depends on:** nothing. **Blocks:** BUG-16 acceptance (with BUG-36).

---

## Tier-1 finding

`openDiag()` in `overlays.js` addresses the diagnostic panel by **ID**:

```js
const title  = document.getElementById('diagTitle');
const grid   = document.getElementById('diagGrid');
const aiTxt  = document.getElementById('diagAiTxt');
```

`index.html` defines the panel with **classes only** — `.diag-head-title`, `.diag-grid`,
`.diag-ai-txt` — and the single ID `diagBack`. Verified with jsdom: all three `getElementById`
lookups return `null`. Every write in `openDiag()` is guarded (`if (title) …`), so nothing throws —
**the panel just silently never populates.**

This is **present in the v0.9.9.2 release itself**, not a deployment gap: the deployed `index.html`
is md5-identical to the release copy, and both repo trees agree (`295f287c…`). DEPLOYMENT_INDEX
records these IDs as added in S39; that change was never committed anywhere.

Second defect in the same block: the panel ships with **fabricated readings** — "Coolant Temperature
High", 92 °C, 52 PSI, 2250 RPM, and a written-out AI paragraph recommending an RPM reduction. Those
are invented numbers shown to a skipper. Same class of defect as BUG-34.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-38   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-38 — give the diagnostic panel the three IDs overlays.js needs,
            and remove the fabricated demo readings

FILE TO EDIT (exactly one)
  deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/index.html
  The diagnostic panel is the <div id="diagBack"> block, ~lines 365-406.

CHANGE — three ID additions plus two content clearances.

  (A) ADD id="diagTitle"  to the existing <div class="diag-head-title"> (~line 371)
      KEEP the class. KEEP its current text ("Coolant Temperature High") —
      openDiag() always overwrites it, and an empty heading collapses the header
      layout. See Q38.2.

          <div class="diag-head-title" id="diagTitle">Coolant Temperature High</div>

  (B) ADD id="diagGrid" to the existing <div class="diag-grid"> (~line 375) AND
      DELETE the three hardcoded demo cards inside it, leaving it empty:

          <div class="diag-grid" id="diagGrid"></div>

      The deleted content is the three <div class="dc ..."> blocks for
      Coolant Temp / Oil Pressure / RPM (~lines 376-390). openDiag() fills this
      element via _diagBuildCards() on every open.

  (C) ADD id="diagAiTxt" to the existing <div class="diag-ai-txt"> (~line 394) AND
      REPLACE its fabricated AI paragraph with a single neutral placeholder:

          <div class="diag-ai-txt" id="diagAiTxt">Tap an engine gauge to run a diagnostic.</div>

      The deleted content is the two-paragraph invented analysis (~lines 395-396).

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT remove or rename any existing CSS class. Styling comes from the classes;
    overlays.js addresses by ID. Both must coexist.
  • Do NOT touch the three <button class="diag-btn64"> elements (~lines 399-403).
    "REDUCE TO 1800 RPM" and "FULL AI BRIEF" are a separate missing-S41 change and
    are OUT OF SCOPE for this bug. See Q38.3.
  • Do NOT touch .diag-head-ico, .diag-head-over, .diag-head, .diag-body, .diag-ai,
    .diag-ai-lbl, .diag-btns, or the #diagBack wrapper.
  • Do NOT edit overlays.js. Do NOT add a null-guard there — the guards already exist.
  • Do NOT edit d3kos.css. Empty containers must not be restyled.
  • Do NOT edit any other file. Do NOT regenerate MANIFEST.md5 (Q0.4).
  • Do NOT deploy to the Pi (Q0.2).

INTERFACE CONTRACT
  Parsing templates/index.html as HTML yields:
    getElementById('diagTitle')  -> the element that also has class diag-head-title
    getElementById('diagGrid')   -> the element that also has class diag-grid,
                                    containing ZERO .dc children
    getElementById('diagAiTxt')  -> the element that also has class diag-ai-txt,
                                    containing no fabricated numbers
    getElementById('diagBack')   -> unchanged, still present
  No other element gains or loses an id. The three buttons are unchanged.

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, then fix)
  File: tests/bug38-diag-panel-ids.test.js      (plain Node — no server needed)
  Run : node tests/bug38-diag-panel-ids.test.js
  Tier 1 has PROVEN jsdom parses this Jinja template correctly — the 14 Jinja tags
  are inert text for HTML parsing purposes.

    const { JSDOM } = require('jsdom');
    const fs = require('fs');
    const assert = require('assert');

    const T = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/index.html';
    const doc = new JSDOM(fs.readFileSync(T, 'utf8')).window.document;

    // 1 — the three IDs overlays.js requires must resolve
    for (const id of ['diagTitle', 'diagGrid', 'diagAiTxt']) {
      assert.ok(doc.getElementById(id), `#${id} must exist (overlays.js getElementById)`);
    }

    // 2 — IDs must sit on the correct existing elements, classes preserved
    assert.ok(doc.getElementById('diagTitle').classList.contains('diag-head-title'),
              'diagTitle must keep class diag-head-title');
    assert.ok(doc.getElementById('diagGrid').classList.contains('diag-grid'),
              'diagGrid must keep class diag-grid');
    assert.ok(doc.getElementById('diagAiTxt').classList.contains('diag-ai-txt'),
              'diagAiTxt must keep class diag-ai-txt');

    // 3 — no fabricated readings left in the panel
    assert.strictEqual(doc.querySelectorAll('#diagGrid .dc').length, 0,
                       'demo cards must be removed from #diagGrid');
    const ai = doc.getElementById('diagAiTxt').textContent;
    for (const bogus of ['92', '1800 RPM', '105', '98']) {
      assert.ok(!ai.includes(bogus), `fabricated value "${bogus}" must not remain in #diagAiTxt`);
    }

    // 4 — REGRESSION: wrapper and buttons untouched
    assert.ok(doc.getElementById('diagBack'), '#diagBack must survive');
    assert.strictEqual(doc.querySelectorAll('.diag-btn64').length, 3,
                       'the three action buttons must be untouched');
    assert.ok(doc.querySelector('.diag-ai-lbl'), '.diag-ai-lbl must survive');

    console.log('BUG-38: ALL ASSERTIONS PASSED');

  EXPECTED BEFORE THE FIX: assertion 1 fails immediately —
    "#diagTitle must exist (overlays.js getElementById)"
  Tier 1 confirmed the current pre-fix state: diagTitle/diagGrid/diagAiTxt all
  absent, .diag-head-title/.diag-grid/.diag-ai-txt all present, 3 demo cards.
  If it does not fail first, STOP and escalate.

DONE WHEN
  • The test FAILED before your edit and PASSES after.
  • git diff shows: 3 id attributes added, the 3 demo cards removed, the AI
    paragraph replaced by one placeholder line. Nothing else.
  • No class attribute anywhere was changed or removed.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • .diag-head-title / .diag-grid / .diag-ai-txt not found, or already carry ids
                                     → CLARIFICATION (template differs from expectation)
  • Removing the demo cards visibly breaks the panel layout when empty
                                     → ADVICE (may need a CSS min-height — do NOT edit CSS yourself)
  • You think the buttons should also change
                                     → ADVICE (out of scope — Q38.3)
  • jsdom cannot parse the template   → SOLUTION-REQUEST (contradicts Tier-1's proof)

PRE-FLIGHT SELF-CHECK
  1. How many ids do I add?          → exactly 3
  2. Do I remove any class?          → no, never
  3. Do I touch the buttons?         → no
  4. Does #diagTitle keep its text?  → yes; #diagGrid and #diagAiTxt do not
  5. Do I edit overlays.js?          → no

RETURN TO TIER 1
  • The diff
  • Terminal output showing fail-before / pass-after
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. Exactly three `id=` attributes added; every original `class=` intact.
2. `#diagGrid` empty; `#diagAiTxt` contains only the placeholder; no invented numbers survive
   anywhere in the `#diagBack` block.
3. The three `.diag-btn64` buttons byte-identical to before.
4. Test genuinely failed first — require the pre-fix output.
5. **Cannot verify remotely:** that the panel renders correctly once empty, and that live values
   appear. Needs BUG-36 (cache), BUG-29 (real data) and a deploy plus an on-screen check.

## Out of scope
Pi deployment · the "REDUCE TO 1800 RPM" / "FULL AI BRIEF" buttons (missing S41 change, own spec) ·
`overlays.js` · `d3kos.css` · BUG-34 thresholds.
