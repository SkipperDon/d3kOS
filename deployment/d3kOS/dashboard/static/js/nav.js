/**
 * nav.js — d3kOS v0.9.2.2
 * Clock, ticker, bottom nav, split pane, More menu, window toggle,
 * keyboard shortcuts, connectivity status polling.
 * Theme functions are in theme.js (loaded before this file).
 */

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
  'SIGNAL K STREAM ACTIVE — ALL SYSTEMS NOMINAL',
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
  document.querySelectorAll('.nb').forEach(x => {
    x.classList.remove('on');
    x.classList.remove('nb-active');
  });
  b.classList.add('nb-active');
}

/* ── SUPPRESS BEFOREUNLOAD DIALOGS (AvNav iframe + Speech API triggers) ── */
window.addEventListener('beforeunload', function(e) {
  delete e.returnValue;
}, true);

/* ── INTERNAL NAVIGATION — stops HELM speech before navigating ── */
function navTo(url) {
  if (typeof closeHelm === 'function') closeHelm();
  window.location = url;
}

/* ── SPLIT PANE ── */
function openSplit(t) {
  document.getElementById('split').classList.add('open');
  showTab(null, t);
}

function closeSplit() {
  document.getElementById('split').classList.remove('open');
  document.querySelectorAll('.nb').forEach((b, i) => {
    b.classList.remove('on');
    b.classList.toggle('nb-active', i === 0);
  });
  if (typeof clearCamIntervals === 'function') clearCamIntervals();
}

function showTab(btn, t) {
  const displayMap = { ai: 'flex', wx: 'flex', cam: 'block' };
  ['ai', 'wx', 'cam'].forEach(x => {
    const el = document.getElementById('tab-' + x);
    if (el) el.style.display = x === t ? (displayMap[x] || 'block') : 'none';
  });
  document.querySelectorAll('.sp-tab').forEach(b =>
    b.classList.toggle('on', b.getAttribute('onclick')?.includes("'" + t + "'"))
  );
  if (t === 'wx')  loadWindy();
  if (t === 'cam' && typeof loadCameras === 'function') loadCameras();
}

/* ── WINDY WEATHER (free public embed — no API key required) ── */
let _wxOverlay = 'waves';

function _windyUrl(lat, lon, overlay) {
  const product = overlay === 'rain' ? 'nowcast' : 'ecmwf';
  return 'https://embed.windy.com/embed2.html'
    + '?lat=' + lat + '&lon=' + lon
    + '&detailLat=' + lat + '&detailLon=' + lon
    + '&zoom=9&level=surface'
    + '&overlay=' + overlay
    + '&product=' + product
    + '&menu=&message=true&marker=true&calendar=now&pressure='
    + '&type=map&location=coordinates&detail='
    + '&metricWind=kt&metricTemp=%C2%B0C&radarRange=-1';
}

function loadWindy() {
  const frame = document.getElementById('windyFrame');
  if (!frame) return;
  // Use GPS from instruments.js if available, else fall back to home port area
  const lat = window.d3kGpsLat || 43.65;
  const lon = window.d3kGpsLon || -79.38;
  if (frame.dataset.overlay !== _wxOverlay || !frame.dataset.loaded) {
    frame.src = _windyUrl(lat, lon, _wxOverlay);
    frame.dataset.overlay = _wxOverlay;
    frame.dataset.loaded  = '1';
  }
}

function setWxView(overlay) {
  _wxOverlay = overlay;
  ['Waves', 'Rain', 'Wind'].forEach(v => {
    const btn = document.getElementById('wxBtn' + v);
    if (btn) btn.classList.toggle('on', v.toLowerCase() === overlay);
  });
  const frame = document.getElementById('windyFrame');
  if (frame) {
    frame.dataset.overlay = '';  // force reload
    loadWindy();
  }
}

/* ── MORE MENU ── */
function openMenu()  { document.getElementById('menuBack').classList.add('open');  }
function closeMenu() { document.getElementById('menuBack').classList.remove('open'); }

/* ── OPENCPN LAUNCH (Node-RED via /launch/opencpn) ── */
function launchOpenCPN() {
  fetch('/launch/opencpn', { method: 'POST' })
    .then(r => r.json())
    .then(d => toast(d.ok ? 'OpenCPN launching\u2026' : 'OpenCPN unavailable'))
    .catch(() => toast('OpenCPN unavailable'));
}

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
