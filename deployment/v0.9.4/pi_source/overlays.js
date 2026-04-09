/**
 * overlays.js — d3kOS v0.9.2.2
 * All modal/overlay open-close functions + toast.
 */

/* ── TOAST ── */
function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.display = 'block';
  clearTimeout(t._tid);
  t._tid = setTimeout(() => { t.style.display = 'none'; }, 3000);
}

/* ── AI ALERT CARD ── */
function showAlert() {
  document.getElementById('alertCard').classList.add('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.textContent = '⚠ AIS ALERT — VESSEL CPA 0.18NM IN 4 MINUTES — HOLD COURSE';
    ticker.classList.add('hot');
  }
}

function closeAlert() {
  document.getElementById('alertCard').classList.remove('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.classList.remove('hot');
    ticker.textContent = TICKS[0];
  }
}

/* ── ENGINE DIAGNOSTIC (M14 — live Gemini analysis) ── */
async function openDiag(triggeredCell) {
  const back   = document.getElementById('diagBack');
  const title  = document.getElementById('diagTitle');
  const grid   = document.getElementById('diagGrid');
  const aiTxt  = document.getElementById('diagAiTxt');
  if (!back) return;
  back.classList.add('show');

  // Tier gate — T2+ only
  let tier = 0;
  try {
    const tr = await fetch('/config/tier');
    const td = await tr.json();
    tier = td.tier || 0;
  } catch {}

  if (tier < 2) {
    if (title) title.textContent = 'AI Engine Diagnostic';
    if (grid)  grid.innerHTML = '';
    if (aiTxt) aiTxt.innerHTML =
      '<span style="color:var(--teal-bright)">&#128274;</span> AI Engine Diagnostic is available on T2 and above.<br><br>' +
      'Upgrade at <b>atmyboat.com</b> to unlock real-time AI analysis of your engine readings.';
    return;
  }

  // Build data cards from live cache
  const eng = window._d3kEngData || {};
  if (grid)  grid.innerHTML = _diagBuildCards(eng);
  if (title) title.textContent = _diagCellLabel(triggeredCell) ? _diagCellLabel(triggeredCell) + ' Alarm' : 'Engine Analysis';
  if (aiTxt) aiTxt.innerHTML  = '&#9203; Sending readings to Gemini&hellip;';

  // Build Gemini prompt
  const readings = _diagReadingsSummary(eng);
  const triggered = _diagCellLabel(triggeredCell);
  const prompt = 'Engine diagnostic. ' +
    (triggered ? 'The ' + triggered + ' alarm just triggered. ' : '') +
    'Current readings: ' + readings + '. ' +
    'Diagnose the most likely cause in 2-3 sentences. Give one immediate action.';

  try {
    const r = await fetch('http://localhost:8097/gemini/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ message: prompt })
    });
    const d = await r.json();
    if (aiTxt) aiTxt.innerHTML = (d.response || 'No response from Gemini.').replace(/
/g, '<br>');
    if (title && d.response) title.textContent = triggered ? triggered + ' — AI Analysis' : 'Engine Analysis';
  } catch {
    if (aiTxt) aiTxt.innerHTML = '&#9888; Gemini is not available. Check internet connection or verify the Gemini proxy is running at port 8097.';
  }
}

function closeDiag() { document.getElementById('diagBack').classList.remove('show'); }

function _diagCellLabel(id) {
  const m = { cellCoolant:'coolant temperature', cellOil:'oil pressure', cellRpm:'RPM', cellBat:'battery voltage', cellDepth:'depth', cellFuel:'fuel' };
  return id ? (m[id] || '') : '';
}

function _diagReadingsSummary(eng) {
  const p = [];
  if (eng.coolant_c != null) p.push('coolant ' + eng.coolant_c.toFixed(0) + '°C');
  if (eng.oil_psi   != null) p.push('oil ' + eng.oil_psi + ' PSI');
  if (eng.rpm       != null) p.push('RPM ' + eng.rpm);
  if (eng.bat_v     != null) p.push('battery ' + eng.bat_v + 'V');
  if (eng.fuel_pct  != null) p.push('fuel ' + Math.round(eng.fuel_pct * 100) + '%');
  return p.length ? p.join(', ') : 'no live readings available (Signal K offline)';
}

function _diagBuildCards(eng) {
  const thr = typeof THR !== 'undefined' ? THR : {coolant:{adv:88,alrt:98,crit:105},oil:{adv:30,alrt:25,crit:20},bat:{adv:12.4,alrt:12.0,crit:11.5}};
  function _stateAbove(v, t) { if (v==null) return null; if (v>=t.crit) return 'Critical'; if (v>=t.alrt) return 'Alert'; if (v>=t.adv) return 'Advisory'; return null; }
  function _stateBelow(v, t) { if (v==null) return null; if (v<=t.crit) return 'Critical'; if (v<=t.alrt) return 'Alert'; if (v<=t.adv) return 'Advisory'; return null; }
  const cards = [
    { lbl:'Coolant', val: eng.coolant_c!=null ? eng.coolant_c.toFixed(0)+'°C':'—', st: _stateAbove(eng.coolant_c, thr.coolant) },
    { lbl:'Oil Pressure', val: eng.oil_psi!=null ? eng.oil_psi+' PSI':'—', st: _stateBelow(eng.oil_psi, thr.oil) },
    { lbl:'RPM', val: eng.rpm!=null ? eng.rpm:'—', st: null },
    { lbl:'Battery', val: eng.bat_v!=null ? eng.bat_v+'V':'—', st: _stateBelow(eng.bat_v, thr.bat) },
  ];
  return cards.map(c => '<div class="dc' + (c.st ? ' bad' : '') + '"><div class="dc-lbl">' + c.lbl + '</div><div class="dc-val">' + c.val + '</div><div class="dc-note">' + (c.st ? '&#9888; ' + c.st : '&#10003; Normal') + '</div></div>').join('');
}

/* ── CRITICAL SCREEN ── */
function showCrit() {
  document.getElementById('critSc').classList.add('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.textContent = '⛔ CRITICAL — OIL PRESSURE 8 PSI — TAKE ACTION NOW';
    ticker.classList.add('hot');
  }
}

function closeCrit() {
  document.getElementById('critSc').classList.remove('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.classList.remove('hot');
    ticker.textContent = TICKS[0];
  }
}

/* ── POSITION REPORT ── */
function showPosRpt() {
  document.getElementById('posRpt').classList.add('show');
  const bar = document.getElementById('prBar');
  if (bar) {
    bar.style.animation = 'none';
    void bar.offsetWidth; // force reflow
    bar.style.animation = 'prBar 4s linear forwards';
  }
  setTimeout(closePosRpt, 4300);
}

function closePosRpt() { document.getElementById('posRpt').classList.remove('show'); }

/* ── PORT ARRIVAL BANNER ── */
function closeArr() {
  const el = document.getElementById('arrival-widget');
  if (el) el.classList.remove('show');
}
