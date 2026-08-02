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
