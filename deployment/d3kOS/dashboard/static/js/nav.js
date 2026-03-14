/**
 * nav.js — d3kOS v0.9.2.2
 * Theme (day/night with manual override fix), clock, ticker,
 * bottom nav, split pane, More menu, window toggle,
 * keyboard shortcuts, connectivity status polling.
 */

/* ── THEME — Bug 1 fix: manual selection persists across autoTheme ticks ── */
let manualTheme = false;

function setTheme(t, manual) {
  if (manual) manualTheme = true;
  if (t === 'night') document.body.setAttribute('data-night', '');
  else               document.body.removeAttribute('data-night');
  document.getElementById('btnD').classList.toggle('on', t === 'day');
  document.getElementById('btnN').classList.toggle('on', t === 'night');
}

function autoTheme() {
  if (manualTheme) return;
  const h = new Date().getHours();
  setTheme(h >= 7 && h < 20 ? 'day' : 'night');
}

autoTheme();
setInterval(autoTheme, 60000);

/* ── CLOCK ── */
function tick() {
  const el = document.getElementById('clk');
  if (el) el.textContent = new Date().toLocaleTimeString('en-CA', {
    hour12: false, hour: '2-digit', minute: '2-digit',
  });
}
setInterval(tick, 1000);
tick();

/* ── TICKER ── */
const TICKS = [
  'AI FIRST OFFICER ACTIVE — ALL SYSTEMS NOMINAL',
  'GEMINI 2.5 FLASH ONLINE — ROUTE ANALYZED',
  'SIGNAL K STREAM ACTIVE — AIS TARGETS IN RANGE',
  'ANCHOR WATCH AVAILABLE — TAP HELM TO ACTIVATE',
  'VOYAGE LOG READY — CURRENT TRACK RECORDING',
];
let _tickIdx = 0;
let _tickerPaused = false;

setInterval(() => {
  if (_tickerPaused) return;
  const el = document.getElementById('ticker');
  if (!el) return;
  el.style.opacity = '0';
  setTimeout(() => {
    _tickIdx = (_tickIdx + 1) % TICKS.length;
    el.textContent = TICKS[_tickIdx];
    el.style.transition = 'opacity .4s';
    el.style.opacity = '1';
  }, 300);
}, 5500);

/* ── BOTTOM NAV ── */
function setNav(b) {
  document.querySelectorAll('.nb').forEach(x => x.classList.remove('on'));
  b.classList.add('on');
}

/* ── SPLIT PANE ── */
function openSplit(t) {
  document.getElementById('split').classList.add('open');
  showTab(null, t);
}

function closeSplit() {
  document.getElementById('split').classList.remove('open');
  document.querySelectorAll('.nb').forEach((b, i) => b.classList.toggle('on', i === 0));
}

function showTab(btn, t) {
  ['ai', 'wx', 'cam'].forEach(x => {
    const el = document.getElementById('tab-' + x);
    if (el) el.style.display = x === t ? (x === 'ai' ? 'flex' : 'block') : 'none';
  });
  document.querySelectorAll('.sp-tab').forEach(b =>
    b.classList.toggle('on', b.getAttribute('onclick')?.includes("'" + t + "'"))
  );
}

/* ── MORE MENU ── */
function openMenu()  { document.getElementById('menuBack').classList.add('open');  }
function closeMenu() { document.getElementById('menuBack').classList.remove('open'); }

/* ── WINDOWED MODE TOGGLE (keyboard-api.py :8087) ── */
function toggleWindowedMode() {
  closeMenu();
  fetch('http://localhost:8087/window/toggle', { method: 'POST' })
    .then(r => r.json())
    .then(d => toast(d.windowed ? 'Windowed Mode' : 'Fullscreen Mode'))
    .catch(() => toast('Window toggle unavailable'));
}

/* ── KEYBOARD SHORTCUTS ── */
document.addEventListener('keydown', e => {
  if (e.key === 'd') setTheme('day', true);
  if (e.key === 'n') setTheme('night', true);
  if (e.key === 'h') openHelm();
  if (e.key === 'm') openMenu();
  if (e.key === '1') { setNav(document.querySelectorAll('.nb')[2]); openSplit('ai'); }
  if (e.key === '2') { setNav(document.querySelectorAll('.nb')[1]); openSplit('wx'); }
  if (e.key === '3') { setNav(document.querySelectorAll('.nb')[4]); openSplit('cam'); }
  if (e.key === 'a') showAlert();
  if (e.key === 'g') openDiag();
  if (e.key === 'c') showCrit();
  if (e.key === 'r') showPosRpt();
  if (e.key === 'p') {
    const el = document.getElementById('arrival-widget');
    if (el) el.classList.add('show');
  }
  if (e.key === 'Escape') {
    closeMenu(); closeSplit(); closeAlert(); closeDiag(); closeCrit(); closeHelm();
  }
});

/* ── CONNECTIVITY — polls /status, updates ticker on service failures ── */
const POLL_MS = 30000;

async function pollStatus() {
  try {
    const res  = await fetch('/status');
    const data = await res.json();
    window.d3kOnline = data.internet;
    _reportStatus(data);
  } catch {
    window.d3kOnline = false;
    _reportStatus({ internet: false, avnav: false, gemini: false,
                    ai_bridge: false, signalk: false, ollama: false });
  }
}

function _reportStatus(s) {
  // Build failure list for ticker — only report if something is down
  const failures = [];
  if (!s.internet)   failures.push('INTERNET');
  if (!s.avnav)      failures.push('AVNAV');
  if (!s.signalk)    failures.push('SIGNAL K');
  if (!s.ai_bridge)  failures.push('AI BRIDGE');
  if (!s.gemini)     failures.push('AI PROXY');

  if (failures.length && !_tickerPaused) {
    const el = document.getElementById('ticker');
    if (el && !el.classList.contains('hot')) {
      el.textContent = 'OFFLINE: ' + failures.join(' · ');
    }
  }
}

setInterval(pollStatus, POLL_MS);
window.addEventListener('pageshow', pollStatus);
