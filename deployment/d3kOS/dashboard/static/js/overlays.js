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

/* ── ENGINE DIAGNOSTIC ── */
function openDiag() { document.getElementById('diagBack').classList.add('show'); }
function closeDiag() { document.getElementById('diagBack').classList.remove('show'); }

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
