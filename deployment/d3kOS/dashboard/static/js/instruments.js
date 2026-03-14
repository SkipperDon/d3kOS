/**
 * instruments.js — d3kOS v0.9.2.2
 * Instrument row toggle, alert dot logic, cell context menu.
 * Session 1: static demo values + row toggle.
 * Session 2: Signal K WebSocket, alert thresholds, AvNav waypoint poll, Route AI SSE.
 */

/* ── CONFIG ── */
const SK_WS_URL    = 'ws://localhost:8099/signalk/v1/stream';
const AVNAV_API    = 'http://localhost:8080/viewer/avnav_navi.php';
const AI_BRIDGE    = 'http://localhost:3002';
const FUEL_CAP_L   = 150;   // TODO: expose in vessel.env when settings page covers it
const WP_POLL_MS   = 15000; // waypoint cell refresh interval
const SK_RECONNECT = 5000;  // WebSocket reconnect delay

/* ── ALERT THRESHOLDS (spec Section 23) ── */
const THR = {
  coolant: { adv: 88,   alrt: 98,   crit: 105  },  // °C, above = alarm
  oil:     { adv: 30,   alrt: 25,   crit: 20   },  // PSI, below = alarm
  bat:     { adv: 12.4, alrt: 12.0, crit: 11.5 },  // V, below = alarm
  depth:   { adv: 3,    alrt: 2,    crit: 1    },  // m, below = alarm
  fuel:    { adv: 0.25, alrt: 0.15, crit: 0.10 },  // fraction, below = alarm
};

/* ── CELL STATE ── */
function _setCellState(id, state) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('adv', 'alrt', 'crit');
  if (state) {
    el.classList.add(state);
    el.onclick = openDiag;
    el.style.cursor = 'pointer';
  } else {
    el.onclick = null;
    el.style.cursor = '';
  }
  updateAlertDots();
}

function _setVal(id, html) {
  const el = document.getElementById(id);
  if (!el) return;
  const v = el.querySelector('.ic-v');
  if (v) v.innerHTML = html;
}

function _setUnit(id, text) {
  const el = document.getElementById(id);
  if (!el) return;
  const u = el.querySelector('.ic-u');
  if (u) u.textContent = text;
}

/* ── ALERT TICKER ── */
let _alertTickerMsg = null;

function _setAlertTicker(msg) {
  _alertTickerMsg = msg;
  const el = document.getElementById('ticker');
  if (!el || el.classList.contains('hot')) return;
  el.textContent = msg;
  el.style.color = '#FFD454';
}

function _clearAlertTicker(tag) {
  // Only clear if the current alert message belongs to this tag
  if (_alertTickerMsg && tag && !_alertTickerMsg.includes(tag)) return;
  _alertTickerMsg = null;
  const el = document.getElementById('ticker');
  if (!el) return;
  el.style.color = '';
  el.textContent = typeof TICKS !== 'undefined' ? TICKS[0]
                 : 'AI FIRST OFFICER ACTIVE — ALL SYSTEMS NOMINAL';
}

/* ── THRESHOLD EVALUATORS ── */
function _evalAbove(val, thr) {
  if (val >= thr.crit) return 'crit';
  if (val >= thr.alrt) return 'alrt';
  if (val >= thr.adv)  return 'adv';
  return null;
}

function _evalBelow(val, thr) {
  if (val <= thr.crit) return 'crit';
  if (val <= thr.alrt) return 'alrt';
  if (val <= thr.adv)  return 'adv';
  return null;
}

/* ── UNIT CONVERTERS ── */
function _latStr(lat) {
  const d = Math.abs(lat), deg = Math.floor(d);
  return deg + '°' + ((d - deg) * 60).toFixed(1) + (lat >= 0 ? 'N' : 'S');
}
function _lonStr(lon) {
  const d = Math.abs(lon), deg = Math.floor(d);
  return deg + '°' + ((d - deg) * 60).toFixed(1) + (lon >= 0 ? 'E' : 'W');
}

/* ── HAVERSINE + BEARING (for waypoint cell) ── */
function _nm(lat1, lon1, lat2, lon2) {
  const R = 3440.065, toRad = Math.PI / 180;
  const dLat = (lat2 - lat1) * toRad, dLon = (lon2 - lon1) * toRad;
  const a = Math.sin(dLat / 2) ** 2
          + Math.cos(lat1 * toRad) * Math.cos(lat2 * toRad) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}
function _brg(lat1, lon1, lat2, lon2) {
  const toRad = Math.PI / 180;
  const dLon = (lon2 - lon1) * toRad;
  const y = Math.sin(dLon) * Math.cos(lat2 * toRad);
  const x = Math.cos(lat1 * toRad) * Math.sin(lat2 * toRad)
          - Math.sin(lat1 * toRad) * Math.cos(lat2 * toRad) * Math.cos(dLon);
  return (Math.round(Math.atan2(y, x) * 180 / Math.PI) + 360) % 360;
}

/* ── SIGNAL K HANDLERS ── */
let _gpsLat = null, _gpsLon = null;  // shared for waypoint distance calc

const SK_HANDLERS = {
  'navigation.speedOverGround': (v) => {
    const kts = (v * 1.944).toFixed(1);
    _setVal('cellSpeed', kts);
    _setUnit('cellSpeed', 'kts · SOG');
    // Expose for position report
    const pr = document.querySelector('#posRpt .pr-big');
    if (pr) pr.textContent = kts + ' kts';
  },

  'navigation.courseOverGroundTrue': (v) => {
    const deg = Math.round(v * 180 / Math.PI);
    _setVal('cellCourse', deg + '°');
    _setUnit('cellCourse', 'true');
    const prm = document.querySelector('#posRpt .pr-mid');
    if (prm) prm.textContent = 'Course ' + deg + '° True';
  },

  'navigation.position': (v) => {
    if (!v || v.latitude == null) return;
    _gpsLat = v.latitude;
    _gpsLon = v.longitude;
    const ls = _latStr(v.latitude), lo = _lonStr(v.longitude);
    _setVal('cellPos', ls + '<br>' + lo);
    const prp = document.querySelector('#posRpt .pr-pos');
    if (prp) prp.textContent = ls + ' · ' + lo;
  },

  'environment.depth.belowKeel': (v) => {
    _setVal('cellDepth', v.toFixed(1));
    const state = _evalBelow(v, THR.depth);
    _setCellState('cellDepth', state);
    _setUnit('cellDepth', state ? 'metres · ' + state : 'metres');
  },

  'propulsion.0.coolantTemperature': (v) => {
    const c = v - 273.15, disp = c.toFixed(0);
    _setVal('cellCoolant', disp + '°');
    const state = _evalAbove(c, THR.coolant);
    _setCellState('cellCoolant', state);
    _setUnit('cellCoolant', state ? 'C · ' + state + ' ↑ tap for AI' : 'C · normal');
    if (state === 'crit') {
      _setAlertTicker('⛔ CRITICAL — COOLANT ' + disp + '°C — REDUCE RPM NOW');
    } else if (state === 'alrt') {
      _setAlertTicker('⚠ ALERT — COOLANT ' + disp + '°C — REDUCE SPEED');
    } else if (state === 'adv') {
      _setAlertTicker('⚠ ADVISORY — COOLANT ' + disp + '°C — MONITOR');
    } else {
      _clearAlertTicker('COOLANT');
    }
  },

  'propulsion.0.oilPressure': (v) => {
    const psi = Math.round(v * 0.000145038);
    _setVal('cellOil', psi.toString());
    const state = _evalBelow(psi, THR.oil);
    _setCellState('cellOil', state);
    _setUnit('cellOil', state ? 'PSI · ' + state : 'PSI · normal');
    if (state === 'crit') {
      _setAlertTicker('⛔ CRITICAL — OIL PRESSURE ' + psi + ' PSI — TAKE ACTION NOW');
      if (typeof showCrit === 'function') showCrit();
    } else if (state) {
      _setAlertTicker('⚠ ' + state.toUpperCase() + ' — OIL PRESSURE ' + psi + ' PSI');
    } else {
      _clearAlertTicker('OIL PRESSURE');
    }
  },

  'propulsion.0.revolutions': (v) => {
    _setVal('cellRpm', Math.round(v * 60).toString());
    _setUnit('cellRpm', 'rev / min');
  },

  'propulsion.0.trimTabPosition': (v) => {
    const deg = Math.round(v * 180 / Math.PI);
    _setVal('cellTrim', (deg >= 0 ? '+' : '') + deg + '°');
    _setUnit('cellTrim', 'degrees');
  },

  'tanks.fuel.0.currentLevel': (v) => {
    const pct = Math.round(v * 100);
    const litres = Math.round(v * FUEL_CAP_L);
    const state = _evalBelow(v, THR.fuel);
    _setVal('cellFuel', pct + '%');
    _setCellState('cellFuel', state);
    if (state) {
      _setUnit('cellFuel', litres + ' L · ' + state);
    } else {
      const hrs = litres / 12; // ~12L/hr cruise estimate
      const hh = Math.floor(hrs), mm = Math.round((hrs - hh) * 60);
      _setUnit('cellFuel', litres + ' L · ' + hh + 'h ' + mm + 'm');
    }
  },

  'electrical.batteries.0.voltage': (v) => {
    _setVal('cellBat', v.toFixed(1));
    const state = _evalBelow(v, THR.bat);
    _setCellState('cellBat', state);
    _setUnit('cellBat', state ? 'V · ' + state : 'V · ' + (v > 13.0 ? 'charging' : 'normal'));
  },
};

/* ── NULL PATH MAP (path → cell id) ── */
const _NULL_CELLS = {
  'navigation.speedOverGround':       'cellSpeed',
  'navigation.courseOverGroundTrue':  'cellCourse',
  'navigation.position':              'cellPos',
  'environment.depth.belowKeel':      'cellDepth',
  'propulsion.0.coolantTemperature':  'cellCoolant',
  'propulsion.0.oilPressure':         'cellOil',
  'propulsion.0.revolutions':         'cellRpm',
  'propulsion.0.trimTabPosition':     'cellTrim',
  'tanks.fuel.0.currentLevel':        'cellFuel',
  'electrical.batteries.0.voltage':   'cellBat',
};

function _markAllDash() {
  Object.values(_NULL_CELLS).forEach(id => {
    _setVal(id, '---');
    _setCellState(id, null);
  });
  const wp = document.getElementById('cellWp');
  if (wp) {
    const dest = wp.querySelector('.ic-dest'), v = wp.querySelector('.ic-v');
    const eta  = wp.querySelector('.ic-eta');
    if (dest) dest.textContent = 'No data';
    if (v)    v.innerHTML      = '---';
    if (eta)  eta.textContent  = '';
  }
}

/* ── SIGNAL K WEBSOCKET ── */
let _skWs = null, _skReconnectTimer = null, _skOfflineMsg = false;

function _connectSK() {
  if (_skWs &&
      (_skWs.readyState === WebSocket.OPEN ||
       _skWs.readyState === WebSocket.CONNECTING)) return;
  try {
    _skWs = new WebSocket(SK_WS_URL);
  } catch {
    _skReconnectTimer = setTimeout(_connectSK, SK_RECONNECT);
    return;
  }

  _skWs.onopen = () => {
    clearTimeout(_skReconnectTimer);
    if (_skOfflineMsg) {
      _skOfflineMsg = false;
      const el = document.getElementById('ticker');
      if (el && !el.classList.contains('hot') && !_alertTickerMsg) {
        el.style.color = '';
        el.textContent = typeof TICKS !== 'undefined' ? TICKS[0]
                       : 'AI FIRST OFFICER ACTIVE — ALL SYSTEMS NOMINAL';
      }
    }
  };

  _skWs.onmessage = (evt) => {
    let data;
    try { data = JSON.parse(evt.data); } catch { return; }
    if (!data.updates) return;
    for (const update of data.updates) {
      if (!update.values) continue;
      for (const { path, value } of update.values) {
        if (value == null) {
          const id = _NULL_CELLS[path];
          if (id) { _setVal(id, '---'); _setCellState(id, null); }
          continue;
        }
        const handler = SK_HANDLERS[path];
        if (handler) { try { handler(value); } catch { /* ignore bad values */ } }
      }
    }
  };

  _skWs.onclose = () => {
    _skWs = null;
    _markAllDash();
    const el = document.getElementById('ticker');
    if (el && !el.classList.contains('hot') && !_alertTickerMsg) {
      el.textContent = 'SIGNAL K OFFLINE — RECONNECTING';
      el.style.color = '#FFD454';
      _skOfflineMsg = true;
    }
    _skReconnectTimer = setTimeout(_connectSK, SK_RECONNECT);
  };

  _skWs.onerror = () => { _skWs.close(); };
}

/* ── AVNAV WAYPOINT POLL ── */
async function _pollWaypoint() {
  try {
    const res = await fetch(AVNAV_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'request=api&type=route&command=getleg',
    });
    _updateWaypointCell(await res.json());
  } catch { /* AvNav unavailable — leave cell as-is */ }
}

function _updateWaypointCell(data) {
  const wp   = document.getElementById('cellWp');
  if (!wp) return;
  const dest = wp.querySelector('.ic-dest');
  const vEl  = wp.querySelector('.ic-v');
  const eta  = wp.querySelector('.ic-eta');

  if (!data.active || !data.to) {
    if (dest) dest.textContent = 'No active route';
    if (vEl)  vEl.innerHTML    = '---';
    if (eta)  eta.textContent  = '';
    return;
  }

  if (dest) dest.textContent = data.to.name || 'Waypoint';

  if (_gpsLat != null && data.to.lat != null) {
    const nm  = _nm(_gpsLat, _gpsLon, data.to.lat, data.to.lon);
    const brg = _brg(_gpsLat, _gpsLon, data.to.lat, data.to.lon);
    if (vEl) vEl.innerHTML = nm.toFixed(1)
                           + ' <span style="font-size:28px;opacity:.6">nm</span>';
    // ETA from current SOG
    const sogEl = document.getElementById('cellSpeed');
    const sog   = sogEl ? parseFloat(sogEl.querySelector('.ic-v').textContent) || 0 : 0;
    let etaTxt  = 'Bearing ' + brg + '° T';
    if (sog > 0.5) {
      const d = new Date();
      d.setMinutes(d.getMinutes() + (nm / sog) * 60);
      etaTxt = 'ETA ' + d.toTimeString().slice(0, 5) + ' · Bearing ' + brg + '° T';
    }
    if (eta) eta.textContent = etaTxt;
  } else {
    if (vEl) vEl.innerHTML = '--- <span style="font-size:28px;opacity:.6">nm</span>';
    if (eta) eta.textContent = 'Bearing ---';
  }
}

/* ── ROUTE AI SSE (:3002/stream) ── */
let _routeSSE = null;

function _connectRouteSSE() {
  if (_routeSSE) return;
  try {
    _routeSSE = new EventSource(AI_BRIDGE + '/stream');
    _routeSSE.addEventListener('route', (evt) => {
      try { _updateRouteWidget(JSON.parse(evt.data)); } catch { /* ignore */ }
    });
    _routeSSE.onerror = () => {
      _routeSSE.close();
      _routeSSE = null;
      setTimeout(_connectRouteSSE, 30000);
    };
  } catch { /* SSE not available */ }
}

function _updateRouteWidget(d) {
  const txt   = document.getElementById('route-text');
  const meta  = document.getElementById('route-meta');
  const badge = document.querySelector('.rw-badge');
  if (txt  && d.analysis)  txt.innerHTML   = d.analysis;
  if (meta && d.timestamp) meta.textContent = 'Updated '
    + new Date(d.timestamp).toLocaleTimeString();
  if (badge && d.source) badge.textContent  = d.source === 'ollama' ? 'OLLAMA' : 'GEMINI';
}

/* exposed for Route AI widget "Analyze Now" tap */
function triggerRouteAnalysis() {
  toast('Route analysis requested…');
  fetch(AI_BRIDGE + '/route/analyze', { method: 'POST' })
    .catch(() => toast('AI Bridge unavailable'));
}

/* ── ROW TOGGLE — Both / Engine / Nav ── */
function showRow(which) {
  const showE = which === 'both' || which === 'engine';
  const showN = which === 'both' || which === 'nav';
  document.getElementById('rowEngine').classList.toggle('hidden', !showE);
  document.getElementById('rowNav').classList.toggle('hidden', !showN);
  document.getElementById('rpBoth').classList.toggle('on',   which === 'both');
  document.getElementById('rpEngine').classList.toggle('on', which === 'engine');
  document.getElementById('rpNav').classList.toggle('on',    which === 'nav');
  const hints = {
    both:   'Engine + Nav',
    engine: 'Engine instruments',
    nav:    'Navigation instruments',
  };
  document.getElementById('rowHint').textContent = hints[which];
  updateAlertDots();
}

/* ── ALERT DOTS ── */
function updateAlertDots() {
  const hasEngineAlert = !!document.querySelector(
    '#rowEngine .ic.adv, #rowEngine .ic.alrt, #rowEngine .ic.crit');
  const hasNavAlert    = !!document.querySelector(
    '#rowNav .ic.adv, #rowNav .ic.alrt, #rowNav .ic.crit');
  const showE = !document.getElementById('rowEngine').classList.contains('hidden');
  const showN = !document.getElementById('rowNav').classList.contains('hidden');
  document.getElementById('engineAlert').classList.toggle('show', !showE && hasEngineAlert);
  document.getElementById('navAlert').classList.toggle('show',    !showN && hasNavAlert);
}

/* ── CELL CONTEXT MENU ── */
function openCtx(e, name) {
  e.preventDefault();
  e.stopPropagation();
  const m = document.getElementById('ctx');
  document.getElementById('ctxTtl').textContent = name;
  m.style.left = Math.min(e.clientX, window.innerWidth - 230) + 'px';
  m.style.top  = Math.max(e.clientY - 180, 60) + 'px';
  m.classList.add('show');
  setTimeout(() => document.addEventListener('click', hideCtx, { once: true }), 10);
}

function hideCtx() { document.getElementById('ctx').classList.remove('show'); }

/* ── INIT ── */
function _init() {
  showRow('both');
  _connectSK();
  _pollWaypoint();
  setInterval(_pollWaypoint, WP_POLL_MS);
  _connectRouteSSE();
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', _init);
} else {
  _init();
}
