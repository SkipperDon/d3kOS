/**
 * d3kOS PWA — Application Logic
 * Vanilla JS SPA. No frameworks, no build step.
 * Runs on GitHub Pages, talks to atmyboat.com PHP endpoints.
 */

'use strict';

// ── Config ────────────────────────────────────────────────────────────────────
const API_BASE     = 'https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile';

// Normalize tier — DB may store "3" (integer) or "T3" (string). Always return "T0"…"T3".
function normalizeTier(raw) {
  if (!raw) return 'T1';
  const s = String(raw).trim();
  if (/^T[0-3]$/.test(s)) return s;        // already "T3"
  if (/^[0-3]$/.test(s))  return 'T' + s;  // "3" → "T3"
  return 'T1';
}
const APP_VERSION  = '0.9.4';      // PWA version
const LATEST_D3KOS = 'v0.9.2.2';  // Latest known Pi firmware — update each d3kOS release

// ── State ─────────────────────────────────────────────────────────────────────
const state = {
  token:       null,   // app_token UUID
  userId:      null,
  username:    null,
  displayName: null,
  tier:        'T1',
  vessels:     [],
  vessel:      null,   // selected vessel object
  dashboard:   null,   // last dashboard-data.php response
  alerts:      [],
  boatlog:     null,
  alertCount:  0,
  currentScreen: 'dashboard',
  mediaList:   [],
  mediaStorage: null,
  fleetId:      null,   // current fleet_id (persisted in localStorage)
  fleetData:    null,   // last fleet-map.php response data
  fleetAnalytics: null, // last fleet-analytics.php response data
};

// ── Persistence ───────────────────────────────────────────────────────────────
function saveSession() {
  localStorage.setItem('amboat_token',    state.token       || '');
  localStorage.setItem('amboat_user_id',  state.userId      || '');
  localStorage.setItem('amboat_username', state.username    || '');
  localStorage.setItem('amboat_tier',     state.tier        || 'T1');
  if (state.vessel) {
    localStorage.setItem('amboat_vessel', JSON.stringify(state.vessel));
  }
}

function loadSession() {
  state.token       = localStorage.getItem('amboat_token')    || null;
  state.userId      = localStorage.getItem('amboat_user_id')  || null;
  state.username    = localStorage.getItem('amboat_username') || null;
  state.tier        = normalizeTier(localStorage.getItem('amboat_tier') || 'T1');
  const v = localStorage.getItem('amboat_vessel');
  if (v) { try { state.vessel = JSON.parse(v); } catch { state.vessel = null; } }
  loadFleetSession();
}

function clearSession() {
  ['amboat_token','amboat_user_id','amboat_username','amboat_tier','amboat_vessel']
    .forEach(k => localStorage.removeItem(k));
  state.token = state.userId = state.username = state.vessel = null;
  state.tier  = 'T1';
}

// ── API ───────────────────────────────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...opts.headers };
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

  const res = await fetch(`${API_BASE}/${path}`, {
    ...opts,
    headers,
  });

  const data = await res.json().catch(() => ({ success: false, error: 'Invalid response from server.' }));

  if (!data.success) {
    throw new Error(data.error || `HTTP ${res.status}`);
  }
  return data.data;
}

async function apiLogin(username, password) {
  const res = await fetch(`${API_BASE}/user-login.php`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json().catch(() => ({ success: false, error: 'Invalid response.' }));
  if (!data.success) throw new Error(data.error || 'Login failed.');
  return data.data;
}

async function apiListVessels() {
  return apiFetch('list-vessels.php');
}

async function apiDashboard(piId) {
  const qs = piId ? `?pi=${encodeURIComponent(piId)}` : '';
  return apiFetch(`dashboard-data.php${qs}`);
}

// Send a command to the Pi via app-command.php (app auth, not Pi auth).
// Returns { command_id: 123 } — use apiPollCommand to check completion.
async function apiSendCommand(piId, commandType, payload = {}) {
  return apiFetch('app-command.php', {
    method: 'POST',
    body: JSON.stringify({ pi_installation_id: piId, command: commandType, payload }),
  });
}

// Poll the status of a queued command.
// Returns { command_id, command, status, result, created_at, completed_at }
async function apiPollCommand(commandId) {
  return apiFetch(`app-command.php?command_id=${encodeURIComponent(commandId)}`);
}

// Request Fix My Pi for the given Pi.
// T1 → returns { tier:'T1', checkout_url }
// T2 → returns { tier:'T2', command_id, fmp_remaining }
// T3 → returns { tier:'T3', command_id, fmp_remaining:'unlimited' }
async function apiFmpRequest(piId, issue = '') {
  return apiFetch('fix-my-pi-app.php?action=request', {
    method: 'POST',
    body: JSON.stringify({ pi_installation_id: piId, issue }),
  });
}

// Poll for the latest fix_my_pi command for this Pi (used by T1 post-payment flow).
async function apiFmpPollLatest(piId) {
  return apiFetch(`fix-my-pi-app.php?action=latest_fmp&pi_id=${encodeURIComponent(piId)}`);
}

// Fetch last 24 h of engine snapshots for trend sparklines.
async function apiEngineHistory(piId) {
  return apiFetch(`engine-history.php?pi=${encodeURIComponent(piId)}`);
}

// Fetch full alert list for a Pi (newest-first).
async function apiAlertsList(piId, limit = 50, offset = 0) {
  return apiFetch(`alerts-list.php?pi=${encodeURIComponent(piId)}&limit=${limit}&offset=${offset}`);
}

// Clear all alerts for a Pi, or specific IDs.
async function apiClearAlerts(piId, ids = null) {
  const body = ids ? { pi: piId, ids } : { pi: piId };
  return apiFetch('clear-alerts.php', { method: 'POST', body: JSON.stringify(body) });
}

// Fetch full boatlog entry list for a Pi (newest-first).
async function apiBoatlogList(piId, limit = 30, offset = 0) {
  return apiFetch(`boatlog-list.php?pi=${encodeURIComponent(piId)}&limit=${limit}&offset=${offset}`);
}

// ── RTC Signaling API ────────────────────────────────────────────────────────

// Post a WebRTC offer to the signaling server. Returns { session_id }.
async function apiTurnCredentials() {
  return apiFetch('turn-credentials.php');
}

async function apiRtcOffer(piId, sdp, iceCandidates) {
  return apiFetch('rtc-signal.php?action=offer', {
    method: 'POST',
    body: JSON.stringify({ pi_id: piId, sdp, ice_candidates: iceCandidates }),
  });
}

// Poll for the Pi's answer. Returns { ready, sdp, ice_candidates } or { ready: false }.
async function apiRtcPollAnswer(sessionId) {
  return apiFetch(`rtc-signal.php?action=poll_answer&session_id=${encodeURIComponent(sessionId)}`);
}

// Send additional ICE candidates from the app to the signaling server (trickle ICE).
async function apiRtcAppIce(sessionId, iceCandidates) {
  return apiFetch('rtc-signal.php?action=app_ice', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, ice_candidates: iceCandidates }),
  });
}

// ── PDF Report API ────────────────────────────────────────────────────────────

// Ask Gemini to analyse vessel data. Returns { analysis, recommendations }.
async function apiAnalyseReport(vesselSummary) {
  return apiFetch('pdf-analyze.php', {
    method: 'POST',
    body: JSON.stringify({ vessel_summary: vesselSummary }),
  });
}

// Store a finished PDF on HostPapa. Returns { report_id, url, vessel_name, created_at }.
async function apiStoreReport(piId, vesselName, pdfBase64, periodStart, periodEnd, snapshotCount) {
  return apiFetch('pdf-store.php', {
    method: 'POST',
    body: JSON.stringify({
      pi_id: piId,
      vessel_name: vesselName,
      pdf_b64: pdfBase64,
      period_start: periodStart,
      period_end: periodEnd,
      snapshot_count: snapshotCount,
    }),
  });
}

// Fetch the user's report library (newest-first). Returns { total, reports: [...] }
async function apiListReports(piId, limit = 20, offset = 0) {
  const qs = piId
    ? `?pi=${encodeURIComponent(piId)}&limit=${limit}&offset=${offset}`
    : `?limit=${limit}&offset=${offset}`;
  return apiFetch(`list-reports.php${qs}`);
}

// Confirm QR pairing from the app.
// pi_id is the UUID from the Pi's QR code (atmyboat.com/pair-device/?pi_id=<UUID>)
async function apiPairDevice(piId, vesselName, vesselType) {
  return apiFetch('pair-device-app.php', {
    method: 'POST',
    body: JSON.stringify({ pi_id: piId, vessel_name: vesselName, vessel_type: vesselType }),
  });
}

// ── Router ────────────────────────────────────────────────────────────────────
const screens = {};

function navigate(screenId) {
  state.currentScreen = screenId;
  updateNavActive(screenId);
  const fn = screens[screenId];
  if (fn) {
    getEl('screen').innerHTML = '';
    fn();
  }
}

function updateNavActive(screenId) {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.screen === screenId);
  });
}

// ── DOM helpers ───────────────────────────────────────────────────────────────
function getEl(id) { return document.getElementById(id); }

function backButton(ariaLabel, onClick) {
  const btn = el('button', { class: 'back-btn', 'aria-label': ariaLabel, onClick });
  btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 18 9 12 15 6"/></svg> Back';
  return btn;
}

function el(tag, attrs = {}, ...children) {
  const elem = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') elem.className = v;
    else if (k.startsWith('on')) elem.addEventListener(k.slice(2).toLowerCase(), v);
    else elem.setAttribute(k, v);
  }
  for (const child of children) {
    if (typeof child === 'string') elem.appendChild(document.createTextNode(child));
    else if (child) elem.appendChild(child);
  }
  return elem;
}

function fmtTime(iso) {
  if (!iso) return '—';
  try {
    // Server returns bare datetime strings with no timezone (HostPapa runs UTC).
    // Append Z so JS parses as UTC and toLocaleTimeString converts to phone's local time.
    const s = iso.trim().includes('T') || iso.trim().endsWith('Z') ? iso : iso.trim().replace(' ', 'T') + 'Z';
    const d = new Date(s);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) + ' ' +
           d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  } catch { return iso; }
}

function fmtDate(iso) {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  } catch { return iso; }
}

function fmtVal(v, unit = '', decimals = 1) {
  if (v === null || v === undefined) return '—';
  return (typeof v === 'number' ? v.toFixed(decimals) : v) + (unit ? '\u00a0' + unit : '');
}

function spinner() {
  return el('div', { class: 'spinner', 'aria-label': 'Loading', role: 'status' });
}

// Build a simple SVG sparkline from an array of numbers (nulls skipped).
// opts: { width, height, color, label }
function sparkline(values, opts = {}) {
  const { width = 280, height = 44, color = '#00b4d8' } = opts;
  const pts = values.filter(v => v !== null && v !== undefined && !isNaN(v));
  if (pts.length < 2) return null;

  const min = Math.min(...pts);
  const max = Math.max(...pts);
  const range = max - min || 1;
  const pad = 3;

  const points = pts.map((v, i) => {
    const x = pad + (i / (pts.length - 1)) * (width - pad * 2);
    const y = pad + (1 - (v - min) / range) * (height - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', String(height));
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('class', 'sparkline-svg');

  const pl = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
  pl.setAttribute('points', points);
  pl.setAttribute('fill', 'none');
  pl.setAttribute('stroke', color);
  pl.setAttribute('stroke-width', '2');
  pl.setAttribute('stroke-linejoin', 'round');
  pl.setAttribute('stroke-linecap', 'round');
  svg.appendChild(pl);
  return svg;
}

// Compare 'v0.9.2.2' style version strings. Returns true if a < b.
function versionLessThan(a, b) {
  const pa = (a || '').replace(/^v/, '').split('.').map(Number);
  const pb = (b || '').replace(/^v/, '').split('.').map(Number);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const na = pa[i] || 0, nb = pb[i] || 0;
    if (na < nb) return true;
    if (na > nb) return false;
  }
  return false;
}

// Parse pi_id UUID from a QR code string.
// QR format: https://atmyboat.com/pair-device/?pi_id=<UUID>  OR  bare UUID
function extractPiId(qrText) {
  try {
    const url = new URL(qrText.startsWith('http') ? qrText : 'https://' + qrText);
    const id  = url.searchParams.get('pi_id');
    if (id && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)) {
      return id;
    }
  } catch { /* fall through */ }
  const bare = qrText.trim();
  if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(bare)) {
    return bare;
  }
  return null;
}

// ── Header update ─────────────────────────────────────────────────────────────
function updateHeader(vesselName = null, online = null) {
  const nameEl = getEl('header-vessel');
  const dotEl  = getEl('online-dot');
  if (vesselName !== null) {
    nameEl.textContent = vesselName;
    // MB4 — boat switcher: make vessel name tappable when account has >1 vessel
    const multiVessel = state.vessels && state.vessels.length > 1;
    if (multiVessel) {
      nameEl.classList.add('vessel-switcher');
      nameEl.setAttribute('role', 'button');
      nameEl.setAttribute('tabindex', '0');
      nameEl.setAttribute('aria-label', `Switch vessel — currently ${vesselName}`);
      nameEl.onclick    = () => navigate('select-vessel');
      nameEl.onkeydown  = e => { if (e.key === 'Enter' || e.key === ' ') navigate('select-vessel'); };
    } else {
      nameEl.classList.remove('vessel-switcher');
      nameEl.removeAttribute('role');
      nameEl.removeAttribute('tabindex');
      nameEl.removeAttribute('aria-label');
      nameEl.onclick   = null;
      nameEl.onkeydown = null;
    }
  }
  if (online !== null) {
    dotEl.className = 'online-dot ' + (online ? 'online' : 'offline');
    dotEl.setAttribute('title',      online ? 'Online' : 'Offline');
    dotEl.setAttribute('aria-label', online ? 'Vessel online' : 'Vessel offline');
  }
}

function updateAlertBadge(count) {
  const badge = getEl('alert-badge');
  if (!badge) return;
  badge.textContent = count;
  badge.style.display = count > 0 ? 'flex' : 'none';
}

// ── Login Screen ──────────────────────────────────────────────────────────────
screens.login = function renderLogin() {
  const container = getEl('screen');
  const errBanner = el('div', { class: 'error-banner', id: 'login-error', role: 'alert' });

  const usernameInput = el('input', {
    type: 'text', id: 'login-user', placeholder: 'Username or email',
    autocomplete: 'username', autocapitalize: 'none',
  });
  const passwordInput = el('input', {
    type: 'password', id: 'login-pass', placeholder: 'Password',
    autocomplete: 'current-password',
  });
  const submitBtn = el('button', { class: 'btn btn-primary', type: 'submit' }, 'Sign In');

  async function doLogin() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    if (!username || !password) {
      showError('Username and password are required.');
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing in…';
    errBanner.classList.remove('visible');
    try {
      const data = await apiLogin(username, password);
      state.token       = data.app_token;
      state.userId      = data.user_id;
      state.username    = data.username;
      state.displayName = data.display_name;
      state.tier        = normalizeTier(data.tier);
      saveSession();
      showAppUI();
      await loadVessels();
    } catch (err) {
      showError(err.message || 'Login failed. Check your credentials.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign In';
    }
  }

  function showError(msg) {
    errBanner.textContent = msg;
    errBanner.classList.add('visible');
  }

  // Allow Enter key on both fields
  usernameInput.addEventListener('keydown', e => { if (e.key === 'Enter') passwordInput.focus(); });
  passwordInput.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
  submitBtn.addEventListener('click', doLogin);

  container.appendChild(
    el('div', { id: 'login-screen' },
      el('div', { class: 'login-logo' },
        svgAnchor(),
        el('h2', {}, 'AtMyBoat'),
        el('p',  {}, 'd3kOS Mobile Companion'),
      ),
      errBanner,
      el('div', { class: 'field' },
        el('label', { for: 'login-user' }, 'Username'),
        usernameInput,
      ),
      el('div', { class: 'field' },
        el('label', { for: 'login-pass' }, 'Password'),
        passwordInput,
      ),
      submitBtn,
    )
  );

  usernameInput.focus();
};

function svgAnchor() {
  // Use the existing app icon (same as home screen / browser tab)
  const img = document.createElement('img');
  img.src    = 'icons/icon-192.png';
  img.width  = 72;
  img.height = 72;
  img.alt    = 'AtMyBoat';
  img.style.cssText = 'border-radius:16px;display:block;margin:0 auto;';
  return img;
}

// ── Vessel Selector ───────────────────────────────────────────────────────────
screens['select-vessel'] = function renderVesselSelect() {
  const container = getEl('screen');
  container.appendChild(el('p', { class: 'card-title', style: 'margin-bottom:16px' }, 'Select Vessel'));

  if (state.vessels.length === 0) {
    const pairBtn = el('button', {
      class: 'btn btn-primary',
      style: 'margin-top: 16px;',
    }, 'Pair a Vessel');
    pairBtn.addEventListener('click', () => navigate('pair'));

    container.appendChild(
      el('div', { class: 'empty-state' },
        el('p', {}, 'No vessels paired to your account.'),
        el('p', { style: 'font-size: 0.9rem; color: var(--text-muted);' },
          'Scan the QR code on your Pi\'s Settings page to link your vessel.'),
        pairBtn,
      )
    );
    return;
  }

  const list = el('div', { class: 'card', style: 'padding: 0; overflow: hidden;' });

  state.vessels.forEach(v => {
    const btn = el('button', {
      class: 'vessel-item',
      'aria-label': `Select ${v.vessel_name}`,
    },
      el('div', { class: 'vessel-icon' }, vesselSvg()),
      el('div', { class: 'vessel-info' },
        el('div', { class: 'vessel-name' }, v.vessel_name),
        el('div', { class: 'vessel-meta' },
          v.vessel_type + (v.is_primary ? ' · Primary' : '') +
          (v.d3kos_version ? ' · v' + v.d3kos_version : ''),
        ),
      ),
      el('div', { class: 'vessel-status ' + (v.online ? 'online' : 'offline') }),
    );
    btn.addEventListener('click', async () => {
      state.vessel = v;
      saveSession();
      navigate('dashboard');
      await refreshDashboard();
    });
    list.appendChild(btn);
  });

  container.appendChild(list);
};

function vesselSvg() {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('width', '24');
  svg.setAttribute('height', '24');
  svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = `
    <path d="M4 17 Q12 22 20 17 L18 11 H6 Z" stroke="#00b4d8" stroke-width="1.8"
          fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 11 V5 L17 10" stroke="#00b4d8" stroke-width="1.8"
          fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  `;
  return svg;
}

// ── Dashboard Screen ──────────────────────────────────────────────────────────
screens.dashboard = function renderDashboard() {
  const container = getEl('screen');

  if (!state.vessel && state.vessels.length > 1) {
    navigate('select-vessel');
    return;
  }

  if (!state.dashboard) {
    container.appendChild(spinner());
    refreshDashboard();
    return;
  }

  const d = state.dashboard;
  const online = d.online;

  // DEP6: firmware update banner
  if (d.d3kos_version && versionLessThan(d.d3kos_version, LATEST_D3KOS)) {
    const banner = el('div', { class: 'update-banner', role: 'status' },
      `Update available: d3kOS ${LATEST_D3KOS} — go to Settings to upgrade.`,
    );
    container.appendChild(banner);
  }

  // Sync line
  container.appendChild(
    el('div', { class: 'synced-at' },
      'Last sync: ' + fmtTime(d.synced_at),
    )
  );

  // Status card
  const statusCard = el('div', { class: 'card' });
  statusCard.appendChild(el('div', { class: 'card-title' }, 'Vessel Status'));
  const sb = el('span', { class: 'status-badge ' + (online ? 'online' : 'offline') });
  sb.innerHTML = (online
    ? '<svg width="10" height="10" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="#22c55e"/></svg> Online'
    : '<svg width="10" height="10" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="#94a3b8"/></svg> Offline');
  statusCard.appendChild(sb);

  if (d.d3kos_version) {
    const vEl = el('div', { style: 'margin-top: 8px; font-size: 0.82rem; color: var(--text-muted)' });
    vEl.innerHTML = `d3kOS <span class="tier-badge">${d.tier || 'T1'}</span> · v${d.d3kos_version}`;
    statusCard.appendChild(vEl);
  }
  container.appendChild(statusCard);

  // Engine card
  if (d.engine) {
    const eng = d.engine;
    const engCard = el('div', { class: 'card' });
    engCard.appendChild(el('div', { class: 'card-title' }, 'Engine'));

    const rpmClass  = eng.rpm > 4000 ? 'danger' : eng.rpm > 2500 ? 'warn' : '';
    const tempClass = eng.coolant_temp > 95 ? 'danger' : eng.coolant_temp > 85 ? 'warn' : '';
    const fuelClass = eng.fuel_level < 15 ? 'danger' : eng.fuel_level < 30 ? 'warn' : '';
    // Oil pressure in kPa: < 138 kPa (~20 psi) = critical, < 207 kPa (~30 psi) = warn
    const oilClass  = eng.oil_pressure !== null
      ? (eng.oil_pressure < 138 ? 'danger' : eng.oil_pressure < 207 ? 'warn' : '')
      : '';

    const statItems = [
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'RPM'),
        el('div', { class: `stat-value ${rpmClass}` }, fmtVal(eng.rpm, '', 0)),
      ),
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Coolant'),
        el('div', { class: `stat-value ${tempClass}` }, fmtVal(eng.coolant_temp, '°C')),
      ),
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Fuel'),
        el('div', { class: `stat-value ${fuelClass}` }, fmtVal(eng.fuel_level, '%', 0)),
      ),
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Engine Hours'),
        el('div', { class: 'stat-value' }, fmtVal(eng.engine_hours, 'h')),
      ),
    ];
    // Only show oil pressure if the Pi is sending it
    if (eng.oil_pressure !== null && eng.oil_pressure !== undefined) {
      statItems.push(
        el('div', { class: 'stat-item' },
          el('div', { class: 'stat-label' }, 'Oil Press.'),
          el('div', { class: `stat-value ${oilClass}` }, fmtVal(eng.oil_pressure, 'kPa', 0)),
        )
      );
    }
    // Only show battery voltage if the Pi is sending it (requires NMEA2000 battery monitor)
    if (eng.battery_voltage !== null && eng.battery_voltage !== undefined) {
      const batClass = eng.battery_voltage < 11.8 ? 'danger' : eng.battery_voltage < 12.2 ? 'warn' : '';
      statItems.push(
        el('div', { class: 'stat-item' },
          el('div', { class: 'stat-label' }, 'Battery'),
          el('div', { class: `stat-value ${batClass}` }, fmtVal(eng.battery_voltage, 'V')),
        )
      );
    }

    engCard.appendChild(el('div', { class: 'stat-grid' }, ...statItems));
    const engDetailBtn = el('button', {
      class: 'btn btn-ghost',
      style: 'margin-top: 12px; width: 100%;',
    }, 'View 24h History');
    engDetailBtn.addEventListener('click', () => navigate('engine'));
    engCard.appendChild(engDetailBtn);
    container.appendChild(engCard);
  }

  // Position card
  if (d.position) {
    const pos = d.position;
    const posCard = el('div', { class: 'card' });
    posCard.appendChild(el('div', { class: 'card-title' }, 'Position'));
    posCard.appendChild(el('div', { class: 'stat-grid' },
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Latitude'),
        el('div', { class: 'stat-value' }, pos.lat.toFixed(5) + '°'),
      ),
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Longitude'),
        el('div', { class: 'stat-value' }, pos.lng.toFixed(5) + '°'),
      ),
    ));
    // Google Maps link
    const mapsLink = el('a', {
      class: 'position-link',
      href: `https://www.google.com/maps?q=${pos.lat},${pos.lng}`,
      target: '_blank',
      rel: 'noopener noreferrer',
    }, '📍 View on map');
    posCard.appendChild(mapsLink);
    container.appendChild(posCard);
  }

  // System health card
  if (d.system) {
    const sys = d.system;
    const sysCard = el('div', { class: 'card' });
    sysCard.appendChild(el('div', { class: 'card-title' }, 'System Health'));
    const cpuClass = sys.cpu_temp > 75 ? 'danger' : sys.cpu_temp > 60 ? 'warn' : '';
    const diskClass = sys.disk_used_pct > 90 ? 'danger' : sys.disk_used_pct > 75 ? 'warn' : '';
    sysCard.appendChild(el('div', { class: 'stat-grid' },
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'CPU Temp'),
        el('div', { class: `stat-value ${cpuClass}` }, fmtVal(sys.cpu_temp, '°C')),
      ),
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Disk Used'),
        el('div', { class: `stat-value ${diskClass}` }, fmtVal(sys.disk_used_pct, '%', 0)),
      ),
    ));
    container.appendChild(sysCard);
  }

  // Alerts summary
  if (d.alerts && d.alerts.count > 0) {
    const alertCard = el('div', { class: 'card' });
    alertCard.appendChild(el('div', { class: 'card-title' }, `Alerts (${d.alerts.count})`));
    (d.alerts.latest || []).slice(0, 3).forEach(a => {
      alertCard.appendChild(
        el('div', { class: 'alert-item' },
          el('div', { class: 'alert-type' }, a.alert_type || 'alert'),
          el('div', { class: 'alert-msg'  }, a.message || ''),
          el('div', { class: 'alert-time' }, fmtTime(a.triggered_at)),
        )
      );
    });
    container.appendChild(alertCard);
  }

  // Latest boatlog entry
  if (d.boatlog && d.boatlog.latest_entry) {
    const entry = d.boatlog.latest_entry;
    const blCard = el('div', { class: 'card' });
    blCard.appendChild(el('div', { class: 'card-title' }, 'Latest Log Entry'));
    blCard.appendChild(
      el('div', { class: 'log-item' },
        el('div', { class: 'log-type' }, entry.entry_type || 'log'),
        el('div', { class: 'log-content' }, entry.content || ''),
        el('div', { class: 'log-time' }, fmtTime(entry.entry_timestamp)),
      )
    );
    container.appendChild(blCard);
  }

  // Quick-action row: Go Live + My Reports + Media
  const qa = el('div', { class: 'quick-actions three-col' });

  const liveBtn = el('button', { class: 'btn btn-live', onClick: () => navigate('live') });
  liveBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M6.3 6.3a8 8 0 0 0 0 11.4M17.7 6.3a8 8 0 0 1 0 11.4M3.5 3.5a14 14 0 0 0 0 17M20.5 3.5a14 14 0 0 1 0 17"/></svg> Live';
  qa.appendChild(liveBtn);

  const reportsBtn = el('button', { class: 'btn btn-reports', onClick: () => navigate('reports') });
  reportsBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg> Reports';
  qa.appendChild(reportsBtn);

  const mediaBtn = el('button', { class: 'btn btn-media', onClick: () => navigate('live') });
  mediaBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg> Media';
  qa.appendChild(mediaBtn);

  container.appendChild(qa);

  // Refresh button
  container.appendChild(
    el('button', { class: 'btn btn-ghost', onClick: async () => {
      container.innerHTML = '';
      container.appendChild(spinner());
      await refreshDashboard();
    }}, 'Refresh')
  );
};

async function refreshDashboard() {
  try {
    const piId = state.vessel ? state.vessel.pi_installation_id : null;
    const data = await apiDashboard(piId);
    state.dashboard = data;
    state.alertCount = data.alerts ? data.alerts.count : 0;
    updateHeader(data.vessel_name || state.vessel?.vessel_name, data.online);
    updateAlertBadge(state.alertCount);
    if (state.currentScreen === 'dashboard') {
      getEl('screen').innerHTML = '';
      screens.dashboard();
    }
  } catch (err) {
    if (state.currentScreen === 'dashboard') {
      const container = getEl('screen');
      container.innerHTML = '';
      container.appendChild(
        el('div', { class: 'error-banner visible', role: 'alert' }, err.message)
      );
    }
  }
}

// ── Live Screen ───────────────────────────────────────────────────────────────

const RTC_STUN = [
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
  { urls: 'stun:stun.cloudflare.com:3478' },
];

// Active peer connection — stored so we can close it when leaving the screen.
let _livePC = null;

// Binary file transfer state — one file at a time, Pi → app via WebRTC data channel.
let _currentTransfer = null; // { filename, chunks[], md5, mediaType }
let _liveRecording   = false; // true while Pi is recording video

function handleFileStart(msg) {
  _currentTransfer = { filename: msg.filename, chunks: [], md5: msg.md5, mediaType: msg.media_type };
}

function handleBinaryChunk(buffer) {
  if (_currentTransfer) _currentTransfer.chunks.push(buffer);
}

function handleFileEnd(msg, dc) {
  if (!_currentTransfer || _currentTransfer.filename !== msg.filename) return;
  const xfer = _currentTransfer;
  _currentTransfer = null;

  // Concatenate all chunks into a single ArrayBuffer
  const total    = xfer.chunks.reduce((n, c) => n + c.byteLength, 0);
  const combined = new Uint8Array(total);
  let offset = 0;
  for (const chunk of xfer.chunks) {
    combined.set(new Uint8Array(chunk), offset);
    offset += chunk.byteLength;
  }

  saveMediaToDevice(combined.buffer, xfer.filename);

  // ACK so Pi deletes the original file
  if (dc && dc.readyState === 'open') {
    dc.send(JSON.stringify({ type: 'transfer_complete', filename: xfer.filename }));
  }
  showLiveNotification(`✓ Saved to device: ${xfer.filename}`);
}

function saveMediaToDevice(buffer, filename) {
  const mimeType = filename.endsWith('.mp4') ? 'video/mp4' : 'image/jpeg';
  const blob     = new Blob([buffer], { type: mimeType });
  const url      = URL.createObjectURL(blob);
  const a        = document.createElement('a');
  a.href         = url;
  a.download     = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 1500);
}

function showLiveNotification(text) {
  const notif = document.getElementById('live-notif');
  if (!notif) return;
  notif.textContent = text;
  notif.style.opacity = '1';
  clearTimeout(notif._hideTimer);
  notif._hideTimer = setTimeout(() => { notif.style.opacity = '0'; }, 4000);
}

function showStorageWarning(pct, freeGb) {
  const el_ = document.getElementById('live-storage-warn');
  if (!el_) return;
  el_.textContent = `⚠ Disk ${pct}% full — only ${freeGb.toFixed(1)} GB free. Transfer or delete files.`;
  el_.style.display = 'block';
}

function updateRecordState(isRecording) {
  _liveRecording = isRecording;
  const btn = document.getElementById('live-record-btn');
  if (!btn) return;
  if (isRecording) {
    btn.textContent = '⏹ Stop';
    btn.classList.add('recording');
  } else {
    btn.textContent = '🔴 Record';
    btn.classList.remove('recording');
  }
}

screens.live = function renderLive() {
  const container = getEl('screen');
  const piId = state.vessel ? state.vessel.pi_installation_id : null;

  // Back button row
  const header = el('div', { class: 'screen-header' });
  const backBtn = backButton('Back to dashboard', () => {
      if (_livePC) { _livePC.close(); _livePC = null; }
      navigate('dashboard');
    });
  header.appendChild(backBtn);
  header.appendChild(el('span', { class: 'screen-title' }, 'Live Feed'));
  container.appendChild(header);

  // Status bar
  const statusBar = el('div', { class: 'live-status-bar', id: 'live-status', role: 'status' });
  statusBar.textContent = 'Connecting…';
  container.appendChild(statusBar);

  // Sensor grid
  const grid = el('div', { class: 'live-sensors-grid', id: 'live-grid' });
  [
    ['RPM',         '—', 'live-rpm'],
    ['Coolant',     '—', 'live-coolant'],
    ['Oil Pres.',   '—', 'live-oil'],
    ['Fuel',        '—', 'live-fuel'],
    ['Engine Hrs',  '—', 'live-hours'],
    ['Battery',     '—', 'live-batt'],
    ['SOG',         '—', 'live-sog'],
    ['COG',         '—', 'live-cog'],
    ['Heading',     '—', 'live-hdg'],
    ['Position',    '—', 'live-pos'],
  ].forEach(([label, val, id]) => {
    const cell = el('div', { class: 'live-cell' });
    cell.appendChild(el('div', { class: 'live-cell-label' }, label));
    cell.appendChild(el('div', { class: 'live-cell-val', id }, val));
    grid.appendChild(cell);
  });
  container.appendChild(grid);

  // Camera panel (hidden until camera is active)
  const camPanel = el('div', { class: 'live-camera-panel', id: 'live-cam-panel', hidden: true });
  const videoEl = el('video', { id: 'live-video', autoplay: 'true', playsinline: 'true', muted: 'true' });
  camPanel.appendChild(videoEl);
  const camClose = el('button', { class: 'cam-close-btn', 'aria-label': 'Close camera',
    onClick: () => {
      if (_livePC && _livePC._dataChannel && _livePC._dataChannel.readyState === 'open') {
        _livePC._dataChannel.send(JSON.stringify({ type: 'camera_stop' }));
      }
      camPanel.hidden = true;
      videoEl.srcObject = null;
    }
  }, '✕');
  camPanel.appendChild(camClose);
  container.appendChild(camPanel);

  // Camera slot buttons (populated once connected)
  const camRow = el('div', { class: 'live-cam-row', id: 'live-cam-row', hidden: true });
  camRow.appendChild(el('span', { class: 'live-cam-label' }, 'Camera:'));
  container.appendChild(camRow);

  // Storage warning (shown by Pi push if disk >= 90%)
  const storageWarnEl = el('div', {
    class: 'storage-warning', id: 'live-storage-warn',
    role: 'alert', style: 'display:none',
  });
  container.appendChild(storageWarnEl);

  // Live notification line (capture/record feedback)
  const notifEl = el('div', { class: 'live-notification', id: 'live-notif', 'aria-live': 'polite' });
  container.appendChild(notifEl);

  // Capture / Record / Media Library controls — enabled once data channel opens
  const ctrlRow = el('div', { class: 'live-controls-row', id: 'live-ctrl-row' });

  const captureBtn = el('button', { class: 'btn-capture', id: 'live-capture-btn' }, '📷 Photo');
  captureBtn.disabled = true;
  captureBtn.addEventListener('click', () => {
    const dc_ = _livePC && _livePC._dataChannel;
    if (dc_ && dc_.readyState === 'open') {
      dc_.send(JSON.stringify({ type: 'capture_request' }));
      showLiveNotification('📷 Capturing photo…');
    }
  });

  const recordBtn = el('button', { class: 'btn-record', id: 'live-record-btn' }, '🔴 Record');
  recordBtn.disabled = true;
  recordBtn.addEventListener('click', () => {
    const dc_ = _livePC && _livePC._dataChannel;
    if (!dc_ || dc_.readyState !== 'open') return;
    if (_liveRecording) {
      dc_.send(JSON.stringify({ type: 'record_stop' }));
      showLiveNotification('⏹ Stopping recording…');
    } else {
      dc_.send(JSON.stringify({ type: 'record_start' }));
      showLiveNotification('🔴 Recording started…');
    }
  });

  const mediaLibBtn = el('button', { class: 'btn-media-lib', id: 'live-media-btn' }, '📁 Media');
  mediaLibBtn.disabled = true;
  mediaLibBtn.addEventListener('click', () => {
    const dc_ = _livePC && _livePC._dataChannel;
    if (dc_ && dc_.readyState === 'open') {
      dc_.send(JSON.stringify({ type: 'media_list_request' }));
    }
    navigate('media');
  });

  ctrlRow.appendChild(captureBtn);
  ctrlRow.appendChild(recordBtn);
  ctrlRow.appendChild(mediaLibBtn);
  container.appendChild(ctrlRow);

  if (!piId) {
    setLiveStatus('No vessel selected. Return to Dashboard.', 'error');
    return;
  }

  if (!window.RTCPeerConnection) {
    setLiveStatus('WebRTC not supported on this browser.', 'error');
    return;
  }

  // Close any existing session
  if (_livePC) { _livePC.close(); _livePC = null; }

  startLiveSession(piId).catch(err => {
    setLiveStatus(`Connection failed: ${err.message}`, 'error');
  });
};

function setLiveStatus(text, cls = '') {
  const bar = document.getElementById('live-status');
  if (!bar) return;
  bar.textContent = text;
  bar.className = 'live-status-bar' + (cls ? ' ' + cls : '');
}

function updateLiveCell(id, val) {
  const el_ = document.getElementById(id);
  if (el_) el_.textContent = val;
}

function applyLiveSensors(data) {
  const d = data.sensors || data;
  if (d.rpm != null)           updateLiveCell('live-rpm',     Math.round(d.rpm) + ' RPM');
  if (d.coolant_temp != null)  updateLiveCell('live-coolant', d.coolant_temp.toFixed(1) + ' °C');
  if (d.oil_pressure != null)  updateLiveCell('live-oil',     Math.round(d.oil_pressure) + ' kPa');
  if (d.fuel_level != null)    updateLiveCell('live-fuel',    d.fuel_level.toFixed(1) + ' %');
  if (d.engine_hours != null)  updateLiveCell('live-hours',   d.engine_hours.toFixed(1) + ' h');
  if (d.battery_v != null)     updateLiveCell('live-batt',    d.battery_v.toFixed(2) + ' V');
  if (d.sog != null)           updateLiveCell('live-sog',     d.sog.toFixed(1) + ' kn');
  if (d.cog != null)           updateLiveCell('live-cog',     Math.round(d.cog) + '°');
  if (d.heading != null)       updateLiveCell('live-hdg',     Math.round(d.heading) + '°');
  if (d.lat != null && d.lon != null) {
    updateLiveCell('live-pos', d.lat.toFixed(4) + ', ' + d.lon.toFixed(4));
  }
}

async function startLiveSession(piId) {
  // Fetch TURN credentials from server — kept server-side so the API key is never in client code.
  // Falls back to STUN-only if the endpoint fails (LAN will still work).
  let iceServers = RTC_STUN;
  try {
    const turnData = await apiTurnCredentials();
    if (turnData && turnData.ice_servers) iceServers = turnData.ice_servers;
  } catch { /* non-fatal — STUN fallback */ }

  const pc = new RTCPeerConnection({ iceServers });
  _livePC = pc;

  // Declare video receive intent BEFORE createOffer so the browser includes a
  // video m-line in the SDP. Without this the Pi has no video section to bind
  // DummyVideoTrack to and crashes with "None is not in list".
  pc.addTransceiver('video', { direction: 'recvonly' });

  // Data channel for sensor readings
  const dc = pc.createDataChannel('sensors');
  dc.binaryType = 'arraybuffer'; // Safari sends Blob by default; force ArrayBuffer for binary transfers
  pc._dataChannel = dc;

  // Camera track handler
  pc.ontrack = (evt) => {
    const panel = document.getElementById('live-cam-panel');
    const video = document.getElementById('live-video');
    if (panel && video && evt.streams && evt.streams[0]) {
      video.srcObject = evt.streams[0];
      panel.hidden = false;
    }
  };

  // Collect ICE candidates for trickle
  const iceCandidates = [];
  let sessionId = null;

  pc.onicecandidate = (evt) => {
    if (evt.candidate) {
      iceCandidates.push(evt.candidate.toJSON());
      // Send trickle ICE to server if we already have a session
      if (sessionId) {
        apiRtcAppIce(sessionId, [evt.candidate.toJSON()]).catch(() => {});
      }
    }
  };

  // Create offer
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  // Wait up to 2s for initial ICE gathering
  await new Promise(resolve => {
    if (pc.iceGatheringState === 'complete') { resolve(); return; }
    const check = () => { if (pc.iceGatheringState === 'complete') resolve(); };
    pc.addEventListener('icegatheringstatechange', check);
    setTimeout(resolve, 2000);
  });

  // Send offer to signaling server
  setLiveStatus('Signaling Pi…');
  let offerResp;
  try {
    offerResp = await apiRtcOffer(piId, pc.localDescription.sdp, iceCandidates);
  } catch (e) {
    setLiveStatus('Signaling failed: ' + e.message, 'error');
    return;
  }
  sessionId = offerResp.session_id;

  // Connection time tracking for UX messages
  const connStart = Date.now();
  let warnedSlow = false;

  // Poll for Pi's answer
  setLiveStatus('Waiting for boat…');
  let answer = null;
  for (let i = 0; i < 60; i++) {
    const elapsed = Date.now() - connStart;
    if (!warnedSlow && elapsed > 10000) {
      setLiveStatus('Still connecting — is the boat online?');
      warnedSlow = true;
    }
    if (elapsed > 30000 && !warnedSlow) {
      setLiveStatus('Connection taking longer than usual…');
    }
    if (elapsed > 120000) {
      setLiveStatus('Unable to connect. Check boat is online and try again.', 'error');
      pc.close();
      return;
    }
    try {
      const resp = await apiRtcPollAnswer(sessionId);
      if (resp.ready) { answer = resp; break; }
    } catch { /* keep polling */ }
    await new Promise(r => setTimeout(r, 2000));
  }

  if (!answer) {
    setLiveStatus('No response from boat. Try again.', 'error');
    pc.close();
    return;
  }

  // Apply Pi's answer
  await pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp: answer.sdp }));
  if (answer.ice_candidates) {
    for (const c of answer.ice_candidates) {
      await pc.addIceCandidate(new RTCIceCandidate(c)).catch(() => {});
    }
  }

  setLiveStatus('Establishing P2P connection…');

  // Wait for data channel to open.
  // Race guard: on fast LAN connections the channel can open before onopen is assigned —
  // check readyState first so we don't wait 30s for an event that already fired.
  if (dc.readyState !== 'open') {
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Data channel timed out')), 30000);
      dc.onopen  = () => { clearTimeout(timeout); resolve(); };
      dc.onerror = (e) => { clearTimeout(timeout); reject(e); };
    });
  }

  setLiveStatus('● Live — updating every 5s', 'connected');

  // Enable capture / record / media controls now that data channel is open
  ['live-capture-btn', 'live-record-btn', 'live-media-btn'].forEach(id => {
    const b = document.getElementById(id);
    if (b) b.disabled = false;
  });

  // Request camera slots from Pi
  try { dc.send(JSON.stringify({ type: 'camera_slots_request' })); } catch {}

  // Receive all data channel messages — sensors, camera slots, media, binary chunks
  dc.onmessage = (evt) => {
    // Binary ArrayBuffer — file chunk from Pi
    if (evt.data instanceof ArrayBuffer) {
      handleBinaryChunk(evt.data);
      return;
    }
    try {
      const msg = JSON.parse(evt.data);
      switch (msg.type) {
        case 'sensors':
          applyLiveSensors(msg);
          break;
        case 'camera_slots':
          renderCameraSlotButtons(msg.slots, dc);
          break;
        case 'file_start':
          handleFileStart(msg);
          break;
        case 'file_end':
          handleFileEnd(msg, dc);
          break;
        case 'storage_warning':
          showStorageWarning(msg.percent_used, msg.free_gb);
          break;
        case 'capture_result':
          showLiveNotification(
            msg.success ? `📷 Photo saved: ${msg.filename}` : `Capture failed: ${msg.error || 'unknown error'}`
          );
          break;
        case 'record_started':
          updateRecordState(true);
          break;
        case 'record_stopped':
          updateRecordState(false);
          showLiveNotification(`🎬 Video saved: ${msg.filename}`);
          break;
        case 'media_list':
          state.mediaList    = msg.files   || [];
          state.mediaStorage = msg.storage || null;
          if (state.currentScreen === 'media') screens.media();
          break;
        case 'delete_ack':
          showLiveNotification(`🗑 Deleted: ${msg.filename}`);
          state.mediaList = (state.mediaList || []).filter(f => f.filename !== msg.filename);
          if (state.currentScreen === 'media') screens.media();
          break;
      }
    } catch {}
  };

  pc.onconnectionstatechange = () => {
    if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
      setLiveStatus('Connection lost.', 'error');
    }
  };
}

function renderCameraSlotButtons(slots, dc) {
  const row = document.getElementById('live-cam-row');
  if (!row || !slots || slots.length === 0) return;
  // Clear existing slot buttons
  while (row.children.length > 1) row.removeChild(row.lastChild);
  slots.forEach(slot => {
    const btn = el('button', { class: 'btn btn-cam-slot',
      onClick: () => {
        if (dc && dc.readyState === 'open') {
          dc.send(JSON.stringify({ type: 'camera_request', slot: String(slot.slot_id) }));
        }
      }
    }, slot.label || `Camera ${slot.slot_id}`);
    row.appendChild(btn);
  });
  row.hidden = false;
}


// ── Reports Screen ────────────────────────────────────────────────────────────

screens.reports = function renderReports() {
  const container = getEl('screen');
  const piId = state.vessel ? state.vessel.pi_installation_id : null;

  // Header + back
  const header = el('div', { class: 'screen-header' });
  header.appendChild(backButton('Back to dashboard', () => navigate('dashboard')));
  header.appendChild(el('span', { class: 'screen-title' }, 'Engine Reports'));
  container.appendChild(header);

  // Generate button
  const genBtn = el('button', { class: 'btn btn-reports', id: 'gen-report-btn',
    onClick: () => generateReport(piId, container, genBtn)
  });
  genBtn.innerHTML = '+ Generate New Report';
  container.appendChild(genBtn);

  // Report list area
  const listArea = el('div', { id: 'reports-list' });
  listArea.appendChild(spinner());
  container.appendChild(listArea);

  loadReports(piId, listArea);
};

async function loadReports(piId, listArea) {
  try {
    const data = await apiListReports(piId);
    renderReportList(data.reports || [], data.total || 0, listArea);
  } catch (err) {
    listArea.innerHTML = '';
    listArea.appendChild(
      el('div', { class: 'error-banner visible', role: 'alert' }, 'Failed to load reports: ' + err.message)
    );
  }
}

function renderReportList(reports, total, listArea) {
  listArea.innerHTML = '';
  if (reports.length === 0) {
    listArea.appendChild(
      el('div', { class: 'empty-state' },
        el('p', {}, 'No reports yet.'),
        el('p', {}, 'Generate your first engine health report above.'),
      )
    );
    return;
  }

  listArea.appendChild(el('div', { class: 'reports-total' }, `${total} report${total !== 1 ? 's' : ''}`));

  reports.forEach(r => {
    const card = el('div', { class: 'report-card' });

    const name = r.vessel_name || 'My Vessel';
    const period = r.period_start && r.period_end
      ? `${r.period_start} → ${r.period_end}`
      : 'All available data';
    const size   = r.file_size_kb ? ` · ${r.file_size_kb} KB` : '';
    const snaps  = r.snapshot_count ? ` · ${r.snapshot_count} readings` : '';

    card.appendChild(el('div', { class: 'report-name' }, name));
    card.appendChild(el('div', { class: 'report-meta' }, `Generated ${fmtDate(r.created_at)}`));
    card.appendChild(el('div', { class: 'report-meta' }, period + snaps + size));

    const btnRow = el('div', { class: 'report-btn-row' });

    // Primary action: Save / Share — stays inside the PWA, no browser trap
    const saveBtn = el('button', { class: 'btn btn-reports', style: 'font-size:0.9rem',
      onClick: () => saveReport(r)
    }, 'Save / Share');
    btnRow.appendChild(saveBtn);

    card.appendChild(btnRow);
    listArea.appendChild(card);
  });
}

async function saveReport(report) {
  const fileName = `vessel-report-${report.vessel_name ? report.vessel_name.replace(/\s+/g,'-') : report.report_id}-${(report.created_at||'').slice(0,10)}.pdf`;

  try {
    // Fetch the PDF binary
    const resp = await fetch(report.url);
    if (!resp.ok) throw new Error('Could not download report.');
    const blob = await resp.blob();

    // Try Web Share API first (keeps user in PWA — no browser trap)
    if (navigator.share) {
      const file = new File([blob], fileName, { type: 'application/pdf' });
      const shareData = {
        title: `Vessel Health Report — ${report.vessel_name || 'My Vessel'}`,
        text: `Generated ${(report.created_at || '').slice(0, 10)} by d3kOS via AtMyBoat.com`,
        files: [file],
      };
      if (navigator.canShare && navigator.canShare(shareData)) {
        await navigator.share(shareData);
        return;
      }
      // Fallback: share URL only
      await navigator.share({ title: shareData.title, text: shareData.text, url: report.url });
      return;
    }

    // Fallback for browsers without Web Share: trigger download via anchor click
    const objUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = objUrl;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(objUrl); }, 1000);

  } catch (err) {
    if (err.name !== 'AbortError') {
      alert('Could not save report: ' + err.message);
    }
  }
}

// shareReport kept for internal use but no longer called from buttons
async function shareReport(report) {
  const note = window.prompt('Add a note for the recipient (optional):', '');
  if (note === null) return;

  try {
    const resp = await fetch(report.url);
    const blob = await resp.blob();
    const file = new File([blob], `engine-report-${report.report_id}.pdf`, { type: 'application/pdf' });

    const shareData = {
      title: `Engine Health Report — ${report.vessel_name || 'My Vessel'}`,
      text: note || `Engine health report generated ${fmtDate(report.created_at)} by d3kOS via AtMyBoat.com`,
      files: [file],
    };

    if (navigator.canShare && navigator.canShare(shareData)) {
      await navigator.share(shareData);
    } else {
      // Fallback: share URL only (no file)
      await navigator.share({
        title: shareData.title,
        text: shareData.text,
        url: report.url,
      });
    }
  } catch (err) {
    if (err.name !== 'AbortError') {
      alert('Share failed: ' + err.message);
    }
  }
}

async function generateReport(piId, container, genBtn) {
  if (!piId) {
    alert('No vessel selected. Return to Dashboard and select a vessel.');
    return;
  }

  if (!window.jspdf) {
    alert('PDF library not loaded. Please check your connection and reload the app.');
    return;
  }

  const listArea = document.getElementById('reports-list');
  const setStatus = (msg) => { genBtn.textContent = msg; };

  genBtn.disabled = true;
  setStatus('Collecting data…');
  if (listArea) { listArea.innerHTML = ''; listArea.appendChild(spinner()); }

  try {
    // ── 1. Collect data in parallel ──────────────────────────────────────────
    const today       = new Date();
    const thirtyAgo   = new Date(today); thirtyAgo.setDate(today.getDate() - 30);
    const fmtD        = d => d.toISOString().slice(0, 10);
    const periodEnd   = fmtD(today);
    const periodStart = fmtD(thirtyAgo);

    const vesselName  = (state.vessel && state.vessel.vessel_name) || 'My Vessel';

    const [dashData, alertsData, histData] = await Promise.allSettled([
      apiDashboard(piId),
      apiAlertsList(piId, 50, 0),
      apiEngineHistory(piId),
    ]);

    const dash    = dashData.status    === 'fulfilled' ? dashData.value    : null;
    const alerts  = alertsData.status  === 'fulfilled' ? alertsData.value  : { total: 0, alerts: [] };
    const history = histData.status    === 'fulfilled' ? histData.value    : [];

    // ── 2. Compute engine stats from history ─────────────────────────────────
    const engRows = Array.isArray(history) ? history.filter(r => r.rpm !== null && r.rpm > 0) : [];
    const engineAvailable = engRows.length > 0;
    const avg = (arr, key) => {
      const vals = arr.map(r => parseFloat(r[key])).filter(v => !isNaN(v));
      return vals.length ? (vals.reduce((s, v) => s + v, 0) / vals.length).toFixed(1) : null;
    };

    // ── 3. Build alert breakdown ──────────────────────────────────────────────
    const alertList   = alerts.alerts || [];
    const alertTotal  = alerts.total || 0;
    const bySeverity  = { critical: 0, warning: 0, info: 0 };
    const typeCount   = {};
    alertList.forEach(a => {
      const sev = (a.severity || 'info').toLowerCase();
      bySeverity[sev] = (bySeverity[sev] || 0) + 1;
      const t = a.type || a.message || 'unknown';
      typeCount[t] = (typeCount[t] || 0) + 1;
    });
    const topTypes = Object.entries(typeCount).sort((a, b) => b[1] - a[1]).slice(0, 5).map(e => e[0]);

    // ── 4. Call Gemini for analysis ───────────────────────────────────────────
    setStatus('Analysing…');
    const vesselSummary = {
      vessel_name:        vesselName,
      d3kos_version:      dash ? dash.d3kos_version : 'unknown',
      uptime:             dash && dash.system ? dash.system.uptime || 'unknown' : 'unknown',
      storage_pct:        dash && dash.system ? dash.system.disk_used_pct : null,
      cpu_temp_c:         dash && dash.system ? dash.system.cpu_temp : null,
      alert_total:        alertTotal,
      alert_critical:     bySeverity.critical,
      alert_warning:      bySeverity.warning,
      alert_types:        topTypes,
      recent_alerts:      alertList.slice(0, 5).map(a => ({
        severity: a.severity, message: a.message, created_at: a.created_at
      })),
      engine_available:   engineAvailable,
      engine_rpm_avg:     engineAvailable ? avg(engRows, 'rpm') : null,
      engine_oil_avg:     engineAvailable ? avg(engRows, 'oil_pressure_kpa') : null,
      engine_coolant_avg: engineAvailable ? avg(engRows, 'coolant_temp_c') : null,
      engine_battery_avg: engineAvailable ? avg(engRows, 'battery_voltage_v') : null,
    };

    let aiResult;
    try {
      aiResult = await apiAnalyseReport(vesselSummary);
    } catch (_) {
      aiResult = {
        analysis: 'AI analysis could not be completed at this time. All vessel data shown is accurate.',
        recommendations: [{ issue: 'AI unavailable', action: 'Retry generating the report when internet connection is stable.' }],
      };
    }

    // ── 5. Build PDF with jsPDF ───────────────────────────────────────────────
    setStatus('Building PDF…');
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

    const ML = 15;            // left margin
    const MR = 15;            // right margin
    const PW = 210 - ML - MR; // printable width (180mm)
    const PH = 297;
    let y = 0;

    const navy = [10, 22, 40];
    const white = [255, 255, 255];
    const dark  = [30, 41, 59];
    const muted = [100, 116, 139];
    const red   = [220, 38, 38];
    const amber = [217, 119, 6];
    const green = [22, 163, 74];

    // Report ID derived from current timestamp
    const reportTag = 'RPT-' + periodEnd.replace(/-/g, '') + '-' + Math.random().toString(36).slice(2,8).toUpperCase();

    // ── Cover header ──────────────────────────────────────────────────────────
    doc.setFillColor(...navy);
    doc.rect(0, 0, 210, 34, 'F');
    doc.setTextColor(...white);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(17);
    doc.text('VESSEL HEALTH REPORT', ML, 13);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8.5);
    doc.text(`${vesselName}  ·  Generated: ${periodEnd}  ·  Report ID: ${reportTag}`, ML, 21);
    doc.text(`Period: ${periodStart} to ${periodEnd}  ·  d3kOS AI First Mate via AtMyBoat.com`, ML, 28);

    y = 42;

    // ── Helper: section bar ───────────────────────────────────────────────────
    const sectionBar = (title) => {
      if (y > PH - 30) { doc.addPage(); y = 18; }
      doc.setFillColor(...navy);
      doc.rect(ML, y, PW, 7, 'F');
      doc.setTextColor(...white);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(8.5);
      doc.text(title, ML + 3, y + 5);
      doc.setTextColor(...dark);
      y += 10;
    };

    // ── Helper: label/value row ───────────────────────────────────────────────
    const row = (label, value, colorArr) => {
      if (y > PH - 18) { doc.addPage(); y = 18; }
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(...muted);
      doc.text(label, ML + 3, y);
      doc.setTextColor(...(colorArr || dark));
      doc.text(String(value ?? '—'), ML + 70, y);
      y += 5.5;
    };

    // ── Helper: paragraph ─────────────────────────────────────────────────────
    const para = (text, indent) => {
      const lines = doc.splitTextToSize(text, PW - 8);
      lines.forEach(line => {
        if (y > PH - 18) { doc.addPage(); y = 18; }
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...dark);
        doc.text(line, ML + (indent || 3), y);
        y += 5;
      });
      y += 2;
    };

    // ── SYSTEM HEALTH ─────────────────────────────────────────────────────────
    sectionBar('SYSTEM HEALTH');
    if (dash) {
      const sys = dash.system || {};
      const cpuC = sys.cpu_temp > 75 ? red : sys.cpu_temp > 60 ? amber : green;
      const dskC = sys.disk_used_pct > 90 ? red : sys.disk_used_pct > 75 ? amber : green;
      row('d3kOS Version',  dash.d3kos_version || '—');
      row('Tier',           dash.tier || 'T1');
      row('Last Sync',      dash.synced_at ? dash.synced_at.replace('T', ' ').slice(0, 16) : '—');
      if (sys.cpu_temp != null) row('CPU Temperature', sys.cpu_temp + ' °C', cpuC);
      if (sys.disk_used_pct != null) row('Storage Used', sys.disk_used_pct + '%', dskC);
      if (sys.uptime) row('Uptime', sys.uptime);
    } else {
      para('System health data not available for this report period.');
    }
    y += 3;

    // ── ENGINE DATA ───────────────────────────────────────────────────────────
    sectionBar('ENGINE DATA');
    if (engineAvailable) {
      const rpmAvg  = avg(engRows, 'rpm');
      const oilAvg  = avg(engRows, 'oil_pressure_kpa');
      const ctAvg   = avg(engRows, 'coolant_temp_c');
      const batAvg  = avg(engRows, 'battery_voltage_v');
      const oilC    = oilAvg < 138 ? red : oilAvg < 207 ? amber : green;
      const batC    = batAvg < 11.8 ? red : batAvg < 12.2 ? amber : green;
      row('Readings (24h)',  engRows.length);
      if (rpmAvg)  row('Average RPM',          rpmAvg + ' RPM');
      if (oilAvg)  row('Avg Oil Pressure',      oilAvg + ' kPa', oilC);
      if (ctAvg)   row('Avg Coolant Temp',       ctAvg + ' °C');
      if (batAvg)  row('Avg Battery Voltage',    batAvg + ' V', batC);
    } else {
      para('No NMEA 2000 engine data was received during this report period.');
      para('To enable engine monitoring: verify Signal K is running on the Pi and can see your NMEA 2000 bus.');
    }
    y += 3;

    // ── ALERT SUMMARY ─────────────────────────────────────────────────────────
    sectionBar('ALERT SUMMARY — LAST 30 DAYS');
    row('Total Alerts', alertTotal);
    row('Critical', bySeverity.critical, bySeverity.critical > 0 ? red : green);
    row('Warning',  bySeverity.warning,  bySeverity.warning > 0 ? amber : green);
    row('Info',     bySeverity.info);
    if (topTypes.length) {
      y += 2;
      doc.setFontSize(8.5);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...muted);
      doc.text('Most frequent:', ML + 3, y);
      y += 5;
      topTypes.forEach(t => {
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...dark);
        doc.setFontSize(8.5);
        const cnt = typeCount[t];
        if (y > PH - 18) { doc.addPage(); y = 18; }
        doc.text(`• ${t} (${cnt})`, ML + 6, y);
        y += 4.5;
      });
    }
    y += 3;

    // ── Recent alerts detail ──────────────────────────────────────────────────
    if (alertList.length > 0) {
      sectionBar('RECENT ALERTS');
      alertList.slice(0, 8).forEach(a => {
        const sev  = (a.severity || 'info').toLowerCase();
        const sevC = sev === 'critical' ? red : sev === 'warning' ? amber : dark;
        if (y > PH - 18) { doc.addPage(); y = 18; }
        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...sevC);
        doc.text(`[${(a.severity || 'info').toUpperCase()}]`, ML + 3, y);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...dark);
        const msgLines = doc.splitTextToSize(a.message || '', PW - 40);
        doc.text(msgLines[0] || '', ML + 24, y);
        doc.setTextColor(...muted);
        doc.text((a.created_at || '').slice(0, 16), ML + PW - 36, y);
        y += 5;
      });
      y += 3;
    }

    // ── AI ANALYSIS ───────────────────────────────────────────────────────────
    sectionBar('AI ANALYSIS & RECOMMENDATIONS');
    para(aiResult.analysis || '');
    y += 2;

    (aiResult.recommendations || []).forEach((rec, i) => {
      if (y > PH - 24) { doc.addPage(); y = 18; }
      doc.setFontSize(9);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...navy);
      doc.text(`${i + 1}. ${rec.issue || ''}`, ML + 3, y);
      y += 5;
      const actLines = doc.splitTextToSize(rec.action || '', PW - 12);
      actLines.forEach(line => {
        if (y > PH - 18) { doc.addPage(); y = 18; }
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...dark);
        doc.setFontSize(8.5);
        doc.text(line, ML + 6, y);
        y += 4.5;
      });
      y += 2;
    });

    // ── Footer on each page ───────────────────────────────────────────────────
    const totalPages = doc.getNumberOfPages();
    for (let p = 1; p <= totalPages; p++) {
      doc.setPage(p);
      doc.setDrawColor(226, 232, 240);
      doc.line(ML, 285, 210 - MR, 285);
      doc.setFontSize(7);
      doc.setTextColor(...muted);
      doc.text(`Report ID: ${reportTag}  ·  ${vesselName}  ·  Generated ${periodEnd}  ·  d3kOS AI First Mate  ·  AtMyBoat.com`, ML, 290);
      doc.text(`Page ${p} of ${totalPages}`, 210 - MR, 290, { align: 'right' });
    }

    // ── 6. Upload to HostPapa ─────────────────────────────────────────────────
    setStatus('Saving to server…');
    const pdfBase64 = doc.output('datauristring').split(',')[1];
    const stored = await apiStoreReport(piId, vesselName, pdfBase64, periodStart, periodEnd, engRows.length);

    // ── 7. Reload list ────────────────────────────────────────────────────────
    genBtn.textContent = '+ Generate New Report';
    genBtn.disabled = false;
    if (listArea) loadReports(piId, listArea);

  } catch (err) {
    genBtn.textContent = '+ Generate New Report';
    genBtn.disabled = false;
    if (listArea) {
      listArea.innerHTML = '';
      listArea.appendChild(
        el('div', { class: 'error-banner visible', role: 'alert' }, 'Report failed: ' + err.message)
      );
    }
  }
}


// ── Media Screen ──────────────────────────────────────────────────────────────
// Accessed via "Media Library" button on the live screen (requires active data channel).

screens.media = function renderMedia() {
  const container = getEl('screen');
  container.innerHTML = '';

  // Header
  const header = el('div', { class: 'screen-header' });
  header.appendChild(backButton('Back to live screen', () => navigate('live')));
  header.appendChild(el('span', { class: 'screen-title' }, 'Media Library'));
  container.appendChild(header);

  // Storage indicator
  const sto = state.mediaStorage;
  if (sto) {
    const cls = sto.percent_used >= 90 ? 'danger' : sto.percent_used >= 75 ? 'warn' : '';
    const stoEl = el('div', { class: `media-storage-bar ${cls}`, id: 'media-storage-warn' },
      `Pi storage: ${sto.percent_used}% used · ${sto.free_gb.toFixed(1)} GB free`
    );
    container.appendChild(stoEl);
  }

  // No live connection guard
  const dc_ = _livePC && _livePC._dataChannel;
  if (!dc_ || dc_.readyState !== 'open') {
    container.appendChild(
      el('div', { class: 'empty-state' },
        el('p', {}, '📡 No live connection.'),
        el('p', {}, 'Go live first — then tap Media Library to browse files on the Pi.'),
      )
    );
    return;
  }

  const files = state.mediaList || [];

  if (files.length === 0) {
    // Show spinner while waiting for list to arrive (media_list_request already sent)
    const wrap = el('div', {});
    wrap.appendChild(spinner());
    wrap.appendChild(el('p', {
      style: 'text-align:center;font-size:0.9rem;color:var(--text-muted);margin-top:8px;',
    }, 'Loading media from Pi…'));
    container.appendChild(wrap);
    return;
  }

  // Transfer All button
  const transferAllBtn = el('button', {
    class: 'btn btn-ghost media-transfer-all',
    onClick: () => {
      if (!dc_ || dc_.readyState !== 'open') return;
      files.forEach(f => {
        dc_.send(JSON.stringify({ type: 'transfer_request', filename: f.filename }));
      });
      showLiveNotification(`📥 Transferring ${files.length} file(s)…`);
    }
  }, `📥 Transfer All (${files.length})`);
  container.appendChild(transferAllBtn);

  // File list
  const listCard = el('div', { class: 'card', style: 'padding: 0 16px; overflow: hidden;' });

  files.forEach(f => {
    const isVideo  = f.media_type === 'video' || f.filename.endsWith('.mp4');
    const thumb    = isVideo ? '🎬' : '📷';
    const sizeKb   = f.size_bytes ? (f.size_bytes / 1024).toFixed(0) + ' KB' : '';
    const modTime  = f.modified_at ? fmtTime(f.modified_at) : '';

    const item = el('div', { class: 'media-item' });
    item.appendChild(el('div', { class: 'media-thumb' }, thumb));

    const info = el('div', { class: 'media-info' });
    info.appendChild(el('div', { class: 'media-filename' }, f.filename));
    info.appendChild(el('div', { class: 'media-meta' }, [sizeKb, modTime].filter(Boolean).join(' · ')));
    item.appendChild(info);

    const actions = el('div', { class: 'media-actions' });

    // Transfer button
    const xferBtn = el('button', { class: 'btn-media-action',
      onClick: () => {
        if (dc_ && dc_.readyState === 'open') {
          dc_.send(JSON.stringify({ type: 'transfer_request', filename: f.filename }));
          showLiveNotification(`📥 Transferring: ${f.filename}`);
        }
      }
    }, '↓ Get');
    actions.appendChild(xferBtn);

    // Delete button
    const delBtn = el('button', { class: 'btn-media-action danger',
      onClick: () => {
        if (!confirm(`Delete ${f.filename} from the Pi?`)) return;
        if (dc_ && dc_.readyState === 'open') {
          dc_.send(JSON.stringify({ type: 'delete_request', filename: f.filename }));
          showLiveNotification(`🗑 Deleting: ${f.filename}`);
        }
      }
    }, '✕ Del');
    actions.appendChild(delBtn);

    item.appendChild(actions);
    listCard.appendChild(item);
  });

  container.appendChild(listCard);

  // SCP note link
  container.appendChild(
    el('p', { class: 'list-footnote', style: 'margin-top:12px;' },
      'To bulk-copy files via SCP, see MEDIA_README.txt on the Pi at /home/d3kos/camera-recordings/'
    )
  );
};


// ── Alerts Screen ─────────────────────────────────────────────────────────────
// Alert type → color mapping for badges
const ALERT_COLORS = {
  engine_temp:    'var(--red)',
  engine_rpm:     'var(--amber)',
  fuel_low:       'var(--amber)',
  disk_full:      'var(--amber)',
  service_down:   'var(--red)',
  network:        'var(--accent)',
  config:         'var(--amber)',
  ota:            'var(--accent)',
};

screens.alerts = function renderAlerts() {
  const container = getEl('screen');
  const piId = state.vessel ? state.vessel.pi_installation_id : null;

  function renderList(total, alerts) {
    container.innerHTML = '';

    // ── Header row: title + Clear All button ──────────────────────────────
    const headerRow = el('div', {
      style: 'display:flex;align-items:center;justify-content:space-between;margin-bottom:16px'
    },
      el('div', { class: 'card-title', style: 'margin:0' },
        total > 0 ? `Alerts (${total})` : 'Alerts'
      )
    );

    if (total > 0 && piId) {
      const clearBtn = el('button', {
        style: [
          'background:transparent',
          'border:1px solid var(--red)',
          'color:var(--red)',
          'border-radius:20px',
          'padding:6px 16px',
          'font-size:14px',
          'font-weight:600',
          'cursor:pointer',
          'touch-action:manipulation',
          'min-height:40px',
          'white-space:nowrap',
        ].join(';'),
      }, '🗑 Clear All');

      clearBtn.addEventListener('click', () => {
        clearBtn.disabled = true;
        clearBtn.textContent = 'Clearing…';
        apiClearAlerts(piId)
          .then(() => { renderList(0, []); updateAlertBadge(0); })
          .catch(() => { clearBtn.disabled = false; clearBtn.textContent = '🗑 Clear All'; });
      });
      headerRow.appendChild(clearBtn);
    }
    container.appendChild(headerRow);

    if (alerts.length === 0) {
      container.appendChild(
        el('div', { class: 'empty-state' }, el('p', {}, '✓ No alerts'))
      );
      return;
    }

    // ── Alert rows ────────────────────────────────────────────────────────
    const card = el('div', { class: 'card', style: 'padding:0;overflow:hidden' });
    alerts.forEach(a => {
      const typeColor = ALERT_COLORS[a.alert_type] || 'var(--text-muted)';
      const typeBadge = el('div', { class: 'alert-type-badge' }, a.alert_type || 'alert');
      typeBadge.style.color       = typeColor;
      typeBadge.style.borderColor = typeColor;

      // Dismiss (✕) button per row
      const dismissBtn = el('button', {
        'aria-label': 'Dismiss alert',
        style: [
          'background:transparent',
          'border:none',
          'color:var(--text-muted)',
          'font-size:18px',
          'cursor:pointer',
          'padding:4px 8px',
          'min-height:40px',
          'line-height:1',
          'touch-action:manipulation',
          'flex-shrink:0',
        ].join(';'),
      }, '✕');

      const row = el('div', { class: 'alert-item alert-item-full' },
        el('div', { class: 'alert-item-top' },
          typeBadge,
          el('div', { class: 'alert-time' }, fmtTime(a.triggered_at)),
          dismissBtn,
        ),
        el('div', { class: 'alert-msg' }, a.message || ''),
      );

      dismissBtn.addEventListener('click', () => {
        dismissBtn.disabled = true;
        apiClearAlerts(piId, [a.id]).then(() => {
          row.style.transition = 'opacity 0.2s';
          row.style.opacity = '0';
          setTimeout(() => {
            row.remove();
            total = Math.max(0, total - 1);
            updateAlertBadge(total);
            // Update header count
            const title = container.querySelector('.card-title');
            if (title) title.textContent = total > 0 ? `Alerts (${total})` : 'Alerts';
            if (total === 0) renderList(0, []);
          }, 200);
        }).catch(() => { dismissBtn.disabled = false; });
      });

      card.appendChild(row);
    });
    container.appendChild(card);

    if (total > alerts.length) {
      container.appendChild(
        el('p', { class: 'list-footnote' }, `Showing ${alerts.length} of ${total} alerts.`)
      );
    }
  }

  // Show cached data immediately while fetching
  const cached = state.dashboard && state.dashboard.alerts;
  if (cached) {
    renderList(cached.count, cached.latest || []);
  } else {
    container.innerHTML = '';
    container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:16px' }, 'Alerts'));
    container.appendChild(spinner());
  }

  if (!piId) return;

  apiAlertsList(piId).then(data => {
    renderList(data.total, data.alerts || []);
    updateAlertBadge(data.total);
  }).catch(() => { /* keep cached view on error */ });
};

// ── Boatlog Screen ────────────────────────────────────────────────────────────
const BOATLOG_TYPE_COLORS = {
  note:     'var(--accent)',
  voice:    'var(--green)',
  engine:   'var(--amber)',
  position: 'var(--accent)',
  weather:  '#a78bfa',
  alert:    'var(--red)',
};

screens.boatlog = function renderBoatlog() {
  const container = getEl('screen');
  const piId = state.vessel ? state.vessel.pi_installation_id : null;

  // Track which entries are expanded
  const expanded = new Set();

  function renderList(total, entries) {
    container.innerHTML = '';
    const headerText = total > 0 ? `Boat Log (${total})` : 'Boat Log';
    container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:16px' }, headerText));

    if (entries.length === 0) {
      container.appendChild(
        el('div', { class: 'empty-state' },
          el('p', {}, 'No boatlog entries yet.'),
        )
      );
      return;
    }

    const card = el('div', { class: 'card', style: 'padding: 0; overflow: hidden;' });
    entries.forEach((e, idx) => {
      const typeColor = BOATLOG_TYPE_COLORS[e.entry_type] || 'var(--text-muted)';
      const typeBadge = el('div', { class: 'log-type-badge' }, e.entry_type || 'log');
      typeBadge.style.color       = typeColor;
      typeBadge.style.borderColor = typeColor;

      const content = e.content || '';
      const isLong  = content.length > 80;
      const preview = isLong ? content.slice(0, 80) + '…' : content;
      const isOpen  = expanded.has(idx);

      const contentEl = el('div', { class: 'log-content' }, isOpen ? content : preview);

      const row = el('div', { class: 'log-item log-item-full' },
        el('div', { class: 'log-item-top' },
          typeBadge,
          el('div', { class: 'log-time' }, fmtTime(e.entry_timestamp)),
        ),
        contentEl,
      );

      if (isLong) {
        row.style.cursor = 'pointer';
        row.setAttribute('role', 'button');
        row.setAttribute('tabindex', '0');
        row.addEventListener('click', () => {
          if (expanded.has(idx)) {
            expanded.delete(idx);
            contentEl.textContent = preview;
          } else {
            expanded.add(idx);
            contentEl.textContent = content;
          }
        });
        row.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') row.click(); });
      }

      card.appendChild(row);
    });
    container.appendChild(card);

    if (total > entries.length) {
      container.appendChild(
        el('p', { class: 'list-footnote' },
          `Showing ${entries.length} of ${total} entries.`)
      );
    }
  }

  // Show cached latest entry while fetching
  const cached = state.dashboard && state.dashboard.boatlog && state.dashboard.boatlog.latest_entry;
  if (cached) {
    renderList(1, [cached]);
  } else {
    container.innerHTML = '';
    container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:16px' }, 'Boat Log'));
    container.appendChild(spinner());
  }

  if (!piId) return;

  apiBoatlogList(piId).then(data => {
    renderList(data.total, data.entries || []);
  }).catch(() => { /* keep cached view on error */ });
};

// ── Engine Screen ─────────────────────────────────────────────────────────────
// Accessed via "View 24h History" button on dashboard engine card.
screens.engine = function renderEngine() {
  const container = getEl('screen');
  const piId = state.vessel ? state.vessel.pi_installation_id : null;

  container.innerHTML = '';
  container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:8px' }, 'Engine'));

  const backBtn = el('button', {
    class: 'btn btn-ghost',
    style: 'margin-bottom:16px;',
  }, '← Dashboard');
  backBtn.addEventListener('click', () => navigate('dashboard'));
  container.appendChild(backBtn);

  if (!piId) {
    container.appendChild(
      el('div', { class: 'empty-state' }, el('p', {}, 'No vessel selected.'))
    );
    return;
  }

  // Current values from dashboard cache
  const eng = state.dashboard && state.dashboard.engine;
  if (eng) {
    const rpmClass  = eng.rpm > 4000 ? 'danger' : eng.rpm > 2500 ? 'warn' : '';
    const tempClass = eng.coolant_temp > 95 ? 'danger' : eng.coolant_temp > 85 ? 'warn' : '';
    const fuelClass = eng.fuel_level < 15 ? 'danger' : eng.fuel_level < 30 ? 'warn' : '';
    const oilClass  = eng.oil_pressure !== null && eng.oil_pressure !== undefined
      ? (eng.oil_pressure < 138 ? 'danger' : eng.oil_pressure < 207 ? 'warn' : '') : '';
    const curCard = el('div', { class: 'card' });
    curCard.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:8px;font-size:0.9rem;' }, 'Current'));
    const curItems = [
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'RPM'),
        el('div', { class: `stat-value ${rpmClass}` }, fmtVal(eng.rpm, '', 0)),
      ),
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Coolant'),
        el('div', { class: `stat-value ${tempClass}` }, fmtVal(eng.coolant_temp, '°C')),
      ),
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Fuel'),
        el('div', { class: `stat-value ${fuelClass}` }, fmtVal(eng.fuel_level, '%', 0)),
      ),
      el('div', { class: 'stat-item' },
        el('div', { class: 'stat-label' }, 'Engine Hours'),
        el('div', { class: 'stat-value' }, fmtVal(eng.engine_hours, 'h')),
      ),
    ];
    if (eng.oil_pressure !== null && eng.oil_pressure !== undefined) {
      curItems.push(
        el('div', { class: 'stat-item' },
          el('div', { class: 'stat-label' }, 'Oil Press.'),
          el('div', { class: `stat-value ${oilClass}` }, fmtVal(eng.oil_pressure, 'kPa', 0)),
        )
      );
    }
    if (eng.battery_voltage !== null && eng.battery_voltage !== undefined) {
      const batClass = eng.battery_voltage < 11.8 ? 'danger' : eng.battery_voltage < 12.2 ? 'warn' : '';
      curItems.push(
        el('div', { class: 'stat-item' },
          el('div', { class: 'stat-label' }, 'Battery'),
          el('div', { class: `stat-value ${batClass}` }, fmtVal(eng.battery_voltage, 'V')),
        )
      );
    }
    curCard.appendChild(el('div', { class: 'stat-grid' }, ...curItems));
    if (eng.snapshot_at) {
      curCard.appendChild(el('div', {
        style: 'font-size:0.82rem;color:var(--text-muted);margin-top:8px;',
      }, 'Sampled: ' + fmtTime(eng.snapshot_at)));
    }
    container.appendChild(curCard);
  }

  // Sparkline placeholder — shown while history loads
  const chartCard = el('div', { class: 'card' });
  chartCard.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:12px;font-size:0.9rem;' }, '24h Trend'));
  const chartsWrap = el('div', {});
  chartsWrap.appendChild(spinner());
  chartCard.appendChild(chartsWrap);
  container.appendChild(chartCard);

  apiEngineHistory(piId).then(data => {
    const snaps = data.snapshots || [];
    chartsWrap.innerHTML = '';

    if (snaps.length < 2) {
      chartsWrap.appendChild(
        el('p', { style: 'font-size:0.9rem;color:var(--text-muted);' },
          'Not enough data yet. Engine history builds up over time.')
      );
      return;
    }

    const rpms    = snaps.map(s => s.rpm);
    const temps   = snaps.map(s => s.coolant_temp);
    const oils    = snaps.map(s => s.oil_pressure_kpa);
    const fuels   = snaps.map(s => s.fuel_level_pct);
    const bats    = snaps.map(s => s.battery_voltage_v);
    const hours   = snaps.map(s => s.engine_hours_h);
    const tFirst  = fmtTime(snaps[0].snapshot_at);
    const tLast   = fmtTime(snaps[snaps.length - 1].snapshot_at);
    const timeRange = el('div', {
      style: 'font-size:0.82rem;color:var(--text-muted);margin-bottom:12px;',
    }, `${tFirst} → ${tLast}`);
    chartsWrap.appendChild(timeRange);

    // Include oil pressure and battery sparklines only if the Pi is sending them
    const hasOil = oils.some(v => v !== null && !isNaN(v));
    const hasBat = bats.some(v => v !== null && !isNaN(v));
    const chartSeries = [
      { label: 'RPM',             values: rpms,  color: '#00b4d8', unit: ''    },
      { label: 'Coolant (°C)',    values: temps, color: '#f59e0b', unit: '°C'  },
      { label: 'Oil Press. (kPa)',values: oils,  color: '#ef4444', unit: 'kPa', skip: !hasOil },
      { label: 'Battery (V)',     values: bats,  color: '#22c55e', unit: 'V',   skip: !hasBat },
      { label: 'Fuel (%)',        values: fuels, color: '#60a5fa', unit: '%'   },
    ];

    chartSeries.filter(s => !s.skip).forEach(({ label, values, color, unit }) => {
      const pts = values.filter(v => v !== null && !isNaN(v));
      if (pts.length < 2) return;

      const minV = Math.min(...pts);
      const maxV = Math.max(...pts);
      const lastV = pts[pts.length - 1];

      const section = el('div', { class: 'sparkline-section' });
      section.appendChild(
        el('div', { class: 'sparkline-header' },
          el('span', { class: 'sparkline-label' }, label),
          el('span', { class: 'sparkline-last', style: `color:${color}` },
            lastV.toFixed(unit === '' ? 0 : 1) + (unit ? '\u00a0' + unit : '')),
        )
      );
      const svg = sparkline(values, { color });
      if (svg) section.appendChild(svg);
      section.appendChild(
        el('div', { class: 'sparkline-range' },
          el('span', {}, minV.toFixed(unit === '' ? 0 : 1) + (unit ? '\u00a0' + unit : '')),
          el('span', {}, maxV.toFixed(unit === '' ? 0 : 1) + (unit ? '\u00a0' + unit : '')),
        )
      );
      chartsWrap.appendChild(section);
    });

    // Engine hours trend (displayed as a stat row, not a sparkline)
    const hourPts = hours.filter(v => v !== null && !isNaN(v));
    if (hourPts.length >= 2) {
      const delta = hourPts[hourPts.length - 1] - hourPts[0];
      if (delta > 0) {
        chartsWrap.appendChild(
          el('div', { class: 'sparkline-section' },
            el('div', { class: 'sparkline-header' },
              el('span', { class: 'sparkline-label' }, 'Engine Hours'),
              el('span', { class: 'sparkline-last' },
                hourPts[hourPts.length - 1].toFixed(1) + '\u00a0h'),
            ),
            el('div', { style: 'font-size:0.82rem;color:var(--text-muted);margin-top:2px;' },
              `+${delta.toFixed(2)} h this period`),
          )
        );
      }
    }
  }).catch(() => {
    chartsWrap.innerHTML = '';
    chartsWrap.appendChild(
      el('p', { style: 'font-size:0.9rem;color:var(--text-muted);' },
        'Could not load history. Check your connection.')
    );
  });
};

// ── Settings Screen ───────────────────────────────────────────────────────────
screens.settings = function renderSettings() {
  const container = getEl('screen');

  // Account info
  const accountCard = el('div', { class: 'card' });
  accountCard.appendChild(el('div', { class: 'card-title' }, 'Account'));
  [
    ['Username',    state.username    || '—'],
    ['Tier',        state.tier        || 'T1'],
  ].forEach(([label, value]) => {
    accountCard.appendChild(
      el('div', { class: 'settings-item' },
        el('div', { class: 'settings-label' }, label),
        el('div', { class: 'settings-value' }, value),
      )
    );
  });
  container.appendChild(accountCard);

  // Vessel info
  if (state.vessel) {
    const v = state.vessel;
    const vesselCard = el('div', { class: 'card' });
    vesselCard.appendChild(el('div', { class: 'card-title' }, 'Active Vessel'));
    [
      ['Name',        v.vessel_name     || '—'],
      ['Type',        v.vessel_type     || '—'],
      ['d3kOS',       v.d3kos_version ? 'v' + v.d3kos_version : '—'],
      ['Pi ID',       v.pi_installation_id || '—'],
      ['Status',      v.online ? 'Online' : 'Offline'],
    ].forEach(([label, value]) => {
      vesselCard.appendChild(
        el('div', { class: 'settings-item' },
          el('div', { class: 'settings-label' }, label),
          el('div', { class: 'settings-value mono' }, value),
        )
      );
    });

    // Switch vessel button (T3 only)
    if (state.tier === 'T3' && state.vessels.length > 1) {
      vesselCard.appendChild(
        el('button', {
          class: 'btn btn-ghost',
          style: 'margin-top: 12px;',
          onClick: () => navigate('select-vessel'),
        }, 'Switch Vessel')
      );
    }

    container.appendChild(vesselCard);
  }

  // OTA Upgrade
  const otaCard = el('div', { class: 'card' });
  otaCard.appendChild(el('div', { class: 'card-title' }, 'OTA Upgrade'));
  const otaDesc = el('div', { style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;' },
    'Trigger a d3kOS software upgrade on your vessel.'
  );
  const otaBtn    = el('button', { class: 'btn btn-ghost' }, 'Start Upgrade');
  const otaResult = el('div', { style: 'margin-top: 8px; font-size: 0.9rem; display: none;' });

  otaBtn.addEventListener('click', async () => {
    if (!state.vessel) {
      otaResult.textContent  = 'No vessel selected.';
      otaResult.style.color  = 'var(--red)';
      otaResult.style.display = 'block';
      return;
    }
    otaBtn.disabled    = true;
    otaBtn.textContent = 'Sending…';
    otaResult.style.display = 'none';

    try {
      const { command_id } = await apiSendCommand(state.vessel.pi_installation_id, 'ota_upgrade', {});
      otaResult.textContent  = `Command queued (#${command_id}). Waiting for Pi to connect…`;
      otaResult.style.color  = 'var(--text-muted)';
      otaResult.style.display = 'block';
      otaBtn.textContent = 'Upgrading…';

      // Poll for completion every 10 s, timeout after 20 min
      let elapsed = 0;
      const MAX_WAIT = 20 * 60 * 1000;
      const pollId = setInterval(async () => {
        elapsed += 10000;
        try {
          const status = await apiPollCommand(command_id);
          if (status.status === 'completed') {
            clearInterval(pollId);
            otaResult.textContent  = '✓ Upgrade complete. Pi is restarting.';
            otaResult.style.color  = 'var(--green)';
            otaBtn.disabled    = false;
            otaBtn.textContent = 'Start Upgrade';
          } else if (status.status === 'failed') {
            clearInterval(pollId);
            const msg = status.result?.error || 'Upgrade failed.';
            otaResult.textContent  = '✗ ' + msg;
            otaResult.style.color  = 'var(--red)';
            otaBtn.disabled    = false;
            otaBtn.textContent = 'Start Upgrade';
          } else if (elapsed >= MAX_WAIT) {
            clearInterval(pollId);
            otaResult.textContent  = 'Timed out — Pi did not respond within 20 minutes.';
            otaResult.style.color  = 'var(--red)';
            otaBtn.disabled    = false;
            otaBtn.textContent = 'Start Upgrade';
          } else {
            otaResult.textContent = `Upgrading… (${Math.round(elapsed / 60000)}m elapsed)`;
          }
        } catch { /* poll failure is non-fatal — keep trying */ }
      }, 10000);

    } catch (err) {
      otaResult.textContent  = '✗ ' + (err.message || 'Command failed.');
      otaResult.style.color  = 'var(--red)';
      otaResult.style.display = 'block';
      otaBtn.disabled    = false;
      otaBtn.textContent = 'Start Upgrade';
    }
  });

  otaCard.appendChild(otaDesc);
  otaCard.appendChild(otaBtn);
  otaCard.appendChild(otaResult);

  // T3 multi-Pi: "Update All Vessels" — queues ota_upgrade for every paired Pi
  if (state.tier === 'T3' && state.vessels && state.vessels.length > 1) {
    const allOtaSep = el('div', { style: 'border-top: 1px solid var(--border); margin: 16px 0;' });
    const allOtaLabel = el('div', {
      style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;',
    }, `Update all ${state.vessels.length} paired vessels at once.`);
    const allOtaBtn = el('button', { class: 'btn btn-ghost' }, 'Update All Vessels');
    const allOtaRows = el('div', { style: 'margin-top: 12px;' });

    allOtaBtn.addEventListener('click', async () => {
      allOtaBtn.disabled = true;
      allOtaBtn.textContent = 'Queuing…';
      allOtaRows.innerHTML = '';

      // Queue ota_upgrade for each vessel and track per-Pi status
      const jobs = await Promise.all(state.vessels.map(async (v) => {
        const row = el('div', { style: 'display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--border);' });
        const nameEl   = el('span', { style: 'font-size: 0.85rem;' }, v.vessel_name || v.pi_installation_id);
        const statusEl = el('span', { style: 'font-size: 0.85rem; color: var(--text-muted);' }, 'Queuing…');
        row.appendChild(nameEl);
        row.appendChild(statusEl);
        allOtaRows.appendChild(row);

        try {
          const { command_id } = await apiSendCommand(v.pi_installation_id, 'ota_upgrade', {});
          statusEl.textContent = 'Queued';
          return { command_id, statusEl, vessel: v };
        } catch (err) {
          statusEl.textContent = '✗ Failed to queue';
          statusEl.style.color = 'var(--red)';
          return null;
        }
      }));

      allOtaBtn.textContent = 'Upgrading All…';

      // Poll each queued job — stop when completed/failed/timed-out
      const MAX_WAIT = 20 * 60 * 1000;
      jobs.filter(Boolean).forEach(({ command_id, statusEl }) => {
        let elapsed = 0;
        statusEl.textContent = 'Waiting for Pi…';
        const pollId = setInterval(async () => {
          elapsed += 10000;
          try {
            const s = await apiPollCommand(command_id);
            if (s.status === 'completed') {
              clearInterval(pollId);
              statusEl.textContent = '✓ Done';
              statusEl.style.color = 'var(--green)';
            } else if (s.status === 'failed') {
              clearInterval(pollId);
              statusEl.textContent = '✗ ' + (s.result?.error || 'Failed');
              statusEl.style.color = 'var(--red)';
            } else if (elapsed >= MAX_WAIT) {
              clearInterval(pollId);
              statusEl.textContent = 'Timed out';
              statusEl.style.color = 'var(--red)';
            } else {
              statusEl.textContent = `${Math.round(elapsed / 60000)}m…`;
            }
          } catch { /* poll failure non-fatal */ }
        }, 10000);
      });

      // Re-enable button when all jobs have a terminal state
      const checkAllDone = setInterval(() => {
        const texts = Array.from(allOtaRows.querySelectorAll('span:last-child')).map(s => s.textContent);
        const allDone = texts.every(t => t.startsWith('✓') || t.startsWith('✗') || t === 'Timed out');
        if (allDone) {
          clearInterval(checkAllDone);
          allOtaBtn.disabled = false;
          allOtaBtn.textContent = 'Update All Vessels';
        }
      }, 5000);
    });

    otaCard.appendChild(allOtaSep);
    otaCard.appendChild(allOtaLabel);
    otaCard.appendChild(allOtaBtn);
    otaCard.appendChild(allOtaRows);
  }

  container.appendChild(otaCard);

  // Fix My Pi
  const fmpCard = el('div', { class: 'card' });
  fmpCard.appendChild(el('div', { class: 'card-title' }, 'Fix My Pi'));

  const fmpUsed = state.dashboard?.fmp_used_month ?? null;
  const fmpDesc = state.tier === 'T0'
    ? 'Not available on T0. Upgrade your plan to access Fix My Pi.'
    : state.tier === 'T1'
      ? 'Run a full diagnostic and repair on your Pi. $29.99 per incident. Automatic refund if unsuccessful.'
      : state.tier === 'T2'
        ? `Run a full diagnostic and repair. ${fmpUsed !== null ? (3 - fmpUsed) + ' of 3 free checks remaining this month.' : '3 free checks per month.'}`
        : 'Run a full diagnostic and repair. Unlimited (T3).';

  fmpCard.appendChild(el('div', {
    style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;',
  }, fmpDesc));

  if (state.tier !== 'T0') {
    const fmpBtn = el('button', { class: 'btn btn-ghost' },
      state.tier === 'T1' ? 'Pay $29.99 — Start Fix' :
      state.tier === 'T2' ? 'Use Free Check' : 'Start Diagnostics'
    );
    fmpBtn.addEventListener('click', () => navigate('fixmypi'));
    fmpCard.appendChild(fmpBtn);
  }
  container.appendChild(fmpCard);

  // Pair New Vessel (T3 multi-boat or any user without a vessel)
  const showPairBtn = (state.tier === 'T3') || (state.vessels.length === 0);
  if (showPairBtn) {
    const pairCard = el('div', { class: 'card' });
    pairCard.appendChild(el('div', { class: 'card-title' }, 'Pair a Vessel'));
    pairCard.appendChild(el('div', { style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;' },
      state.tier === 'T3' ? 'Add another vessel to your account.' : 'Link your d3kOS Pi to this account.'
    ));
    const pairNavBtn = el('button', { class: 'btn btn-ghost' }, 'Scan QR Code');
    pairNavBtn.addEventListener('click', () => navigate('pair'));
    pairCard.appendChild(pairNavBtn);
    container.appendChild(pairCard);
  }

  // TS3/TS4 — Locked features upgrade section
  // Show features locked for this tier with upgrade CTAs.
  const LOCKED_FEATURES = [
    {
      name:    'PDF Reports',
      desc:    'Download monthly engine performance and trip reports.',
      minTier: 'T2',
      label:   'T2+',
    },
    {
      name:    'SMS Alerts',
      desc:    'Receive anchor drag, engine fault, and critical alerts by text.',
      minTier: 'T2',
      label:   'T2+',
    },
    {
      name:    'Multiple Phones',
      desc:    'Share access with your crew or family — up to 3 devices.',
      minTier: 'T2',
      label:   'T2+',
    },
    {
      name:    'Fleet Management',
      desc:    'Monitor and manage multiple vessels from one account.',
      minTier: 'T3',
      label:   'T3',
    },
  ];
  const tierRank = { T0: 0, T1: 1, T2: 2, T3: 3 };
  const userRank = tierRank[state.tier] ?? 1;
  const lockedForUser = LOCKED_FEATURES.filter(f => tierRank[f.minTier] > userRank);

  if (lockedForUser.length > 0) {
    const upgradeSection = el('div', { class: 'locked-features-section' });
    upgradeSection.appendChild(
      el('div', { class: 'card-title', style: 'margin-bottom: 12px;' }, 'Upgrade Your Plan')
    );
    const upgradeUrl = API_BASE.replace('/wp-content/themes/twentytwenty-child/mobile', '/upgrade');
    lockedForUser.forEach(feature => {
      const featureCard = el('div', { class: 'locked-feature-card' });

      const titleRow = el('div', { class: 'locked-feature-top' });
      titleRow.appendChild(
        el('span', { class: 'locked-feature-name' },
          '\uD83D\uDD12 ' + feature.name)   // 🔒
      );
      titleRow.appendChild(
        el('span', { class: 'locked-badge' }, feature.label)
      );
      featureCard.appendChild(titleRow);

      featureCard.appendChild(
        el('div', { class: 'locked-feature-desc' }, feature.desc)
      );

      const upgradeBtn = el('a', {
        href:   upgradeUrl,
        target: '_blank',
        rel:    'noopener noreferrer',
        class:  'btn btn-ghost locked-upgrade-btn',
        'aria-label': `Upgrade to ${feature.minTier} to unlock ${feature.name}`,
      }, `Upgrade to ${feature.minTier} →`);
      featureCard.appendChild(upgradeBtn);

      upgradeSection.appendChild(featureCard);
    });
    container.appendChild(upgradeSection);
  }

  // Contact Support
  const supportCard = el('div', { class: 'card' });
  supportCard.appendChild(el('div', { class: 'card-title' }, 'Support'));
  supportCard.appendChild(el('div', {
    style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;',
  }, 'Send a message to Skipper Don. We respond within 1 business day.'));
  const supportBtn = el('button', { class: 'btn btn-ghost' }, 'Contact Support');
  supportBtn.addEventListener('click', () => navigate('support'));
  supportCard.appendChild(supportBtn);
  container.appendChild(supportCard);

  // My Tickets
  const ticketsCard = el('div', { class: 'card' });
  ticketsCard.appendChild(el('div', { class: 'card-title' }, 'My Tickets'));
  const ticketsList = el('div', { style: 'margin-top: 4px;' });
  ticketsList.textContent = 'Loading…';
  ticketsCard.appendChild(ticketsList);
  container.appendChild(ticketsCard);

  (async () => {
    try {
      const data = await apiFetch('ticket-list.php');
      ticketsList.innerHTML = '';
      const tickets = data.tickets || [];
      if (tickets.length === 0) {
        ticketsList.appendChild(el('div', {
          style: 'font-size: 0.9rem; color: var(--text-muted); padding: 6px 0;',
        }, 'No tickets yet.'));
        return;
      }
      const statusLabel = { open: 'Open', in_progress: 'In Progress', resolved: 'Resolved' };
      const statusColor = { open: '#f59e0b', in_progress: '#3b82f6', resolved: '#22c55e' };
      tickets.forEach(t => {
        const row = el('div', {
          style: 'display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--border); cursor: pointer;',
          role: 'button',
          tabindex: '0',
          'aria-label': `Ticket ${t.ticket_id}: ${t.subject}`,
        });
        const idSpan = el('span', {
          style: 'font-size: 0.8rem; color: var(--text-muted); min-width: 48px;',
        }, `#${t.ticket_id}`);
        const subj = el('span', {
          style: 'flex: 1; font-size: 0.95rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;',
        }, t.subject);
        const badge = el('span', {
          style: `font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 12px; background: ${statusColor[t.status] || '#94a3b8'}22; color: ${statusColor[t.status] || '#64748b'}; white-space: nowrap;`,
        }, statusLabel[t.status] || t.status);
        row.appendChild(idSpan);
        row.appendChild(subj);
        row.appendChild(badge);
        const openTicket = () => {
          localStorage.setItem('support_ticket_id', String(t.ticket_id));
          navigate('support');
        };
        row.addEventListener('click', openTicket);
        row.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') openTicket(); });
        ticketsList.appendChild(row);
      });
    } catch {
      ticketsList.textContent = 'Could not load tickets.';
    }
  })();

  // Privacy & Data
  const privacyCard = el('div', { class: 'card' });
  privacyCard.appendChild(el('div', { class: 'card-title' }, 'Privacy & Data'));
  privacyCard.appendChild(el('div', {
    style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;',
  }, 'Download a copy of your data or permanently delete your account.'));

  const exportBtn = el('button', { class: 'btn btn-ghost', style: 'margin-bottom: 8px;' }, 'Download My Data');
  exportBtn.addEventListener('click', async () => {
    exportBtn.disabled = true;
    exportBtn.textContent = 'Preparing…';
    try {
      const token = localStorage.getItem('app_token') || '';
      const res = await fetch('https://atmyboat.com/app/data-export.php', {
        headers: { 'Authorization': 'Bearer ' + token },
      });
      if (!res.ok) throw new Error('Export failed');
      const json = await res.text();
      const blob = new Blob([json], { type: 'application/json' });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = 'atmyboat-data-export.json';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert('Could not export data. Please try again or contact support.');
    } finally {
      exportBtn.disabled = false;
      exportBtn.textContent = 'Download My Data';
    }
  });
  privacyCard.appendChild(exportBtn);

  const deleteAccountBtn = el('button', {
    class: 'btn btn-danger',
    style: 'display: block;',
  }, 'Delete My Account');
  let deleteStep = 0;
  deleteAccountBtn.addEventListener('click', async () => {
    if (deleteStep === 0) {
      deleteStep = 1;
      deleteAccountBtn.textContent = 'Tap again to confirm permanent deletion';
      deleteAccountBtn.style.opacity = '0.7';
      setTimeout(() => {
        if (deleteStep === 1) {
          deleteStep = 0;
          deleteAccountBtn.textContent = 'Delete My Account';
          deleteAccountBtn.style.opacity = '';
        }
      }, 5000);
      return;
    }
    deleteStep = 0;
    deleteAccountBtn.disabled = true;
    deleteAccountBtn.textContent = 'Deleting…';
    try {
      const token = localStorage.getItem('app_token') || '';
      const res = await fetch('https://atmyboat.com/app/data-delete.php', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm: true }),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Delete failed');
      alert('Your account data has been deleted. You will now be signed out.');
      clearSession();
      showLoginUI();
    } catch {
      alert('Could not delete account. Please contact skipperdon@atmyboat.com.');
      deleteAccountBtn.disabled = false;
      deleteAccountBtn.textContent = 'Delete My Account';
    }
  });
  privacyCard.appendChild(deleteAccountBtn);
  container.appendChild(privacyCard);

  // Sign out
  container.appendChild(
    el('button', {
      class: 'btn btn-danger',
      style: 'margin-top: 8px;',
      onClick: () => {
        clearSession();
        showLoginUI();
      },
    }, 'Sign Out')
  );
};

// ── Support Screen ────────────────────────────────────────────────────────────
screens.support = function renderSupport() {
  const container = getEl('screen');

  // Header with back chevron
  const header = el('div', { class: 'screen-header' });
  const backBtn = el('button', {
    class: 'back-btn',
    'aria-label': 'Back to Settings',
  }, '‹');
  backBtn.addEventListener('click', () => navigate('settings'));
  header.appendChild(backBtn);
  header.appendChild(el('span', { class: 'screen-title' }, 'Contact Support'));
  container.appendChild(header);

  const card = el('div', { class: 'card' });

  // Sent confirmation state
  const sentMsg = el('div', {
    class: 'support-sent',
    style: 'display: none;',
  });
  sentMsg.appendChild(el('div', { class: 'support-sent-icon' }, '✓'));
  const sentTitle = el('p', { style: 'font-size: 1rem; font-weight: 600; margin-bottom: 8px;' },
    'Message sent');
  sentMsg.appendChild(sentTitle);
  const sentSub = el('p', { style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;' },
    `We'll respond to ${state.username || 'you'} within 1 business day.`);
  sentMsg.appendChild(sentSub);

  const ticketRow = el('div', {
    style: 'display: none; background: var(--surface-2, rgba(255,255,255,0.05)); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.9rem;',
  });
  sentMsg.appendChild(ticketRow);

  const checkStatusBtn = el('button', {
    class: 'btn btn-ghost',
    style: 'display: none; margin-bottom: 8px; width: 100%;',
  }, 'Check Ticket Status');
  checkStatusBtn.addEventListener('click', async () => {
    const tid = parseInt(localStorage.getItem('support_ticket_id') || '0', 10);
    if (!tid) return;
    checkStatusBtn.disabled = true;
    checkStatusBtn.textContent = 'Checking…';
    try {
      const res = await apiFetch(`ticket-status.php?ticket_id=${tid}`);
      const labels = { open: 'Open', in_progress: 'In Progress', resolved: 'Resolved' };
      ticketRow.innerHTML = '';
      ticketRow.appendChild(el('span', {}, `Ticket #${res.ticket_id} — `));
      ticketRow.appendChild(el('strong', {}, labels[res.status] || res.status));
      if (res.admin_note) {
        ticketRow.appendChild(el('p', { style: 'margin-top: 6px; color: var(--text-muted);' }, res.admin_note));
      }
      ticketRow.style.display = 'block';
      checkStatusBtn.disabled = false;
      checkStatusBtn.textContent = 'Refresh Status';
    } catch (err) {
      checkStatusBtn.disabled = false;
      checkStatusBtn.textContent = 'Check Ticket Status';
    }
  });
  sentMsg.appendChild(checkStatusBtn);

  // ── Diagnostic consent panel (shown when ticket_id exists) ───────────────
  const diagPanel = el('div', {
    style: 'display: none; border-top: 1px solid var(--border, rgba(255,255,255,0.1)); margin-top: 16px; padding-top: 16px;',
  });

  const diagTitle = el('p', {
    style: 'font-size: 0.95rem; font-weight: 600; margin-bottom: 6px;',
  }, 'Remote Diagnostic Support');

  const diagDesc = el('p', {
    style: 'font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;',
  }, 'Allow our support team to remotely collect diagnostic data from your vessel for this ticket.');

  const diagStatus = el('div', {
    style: 'display: none; font-size: 0.85rem; margin-bottom: 10px; padding: 8px 12px; border-radius: 6px; background: var(--surface-2, rgba(255,255,255,0.05));',
  });

  const requestDiagBtn = el('button', {
    class: 'btn btn-primary',
    style: 'width: 100%; margin-bottom: 8px;',
  }, 'Request Diagnostic Support');

  const revokeBtn = el('button', {
    class: 'btn btn-ghost',
    style: 'display: none; width: 100%; margin-bottom: 8px;',
  }, 'Revoke Diagnostic Access');

  let diagPollTimer = null;

  function startDiagPoll(tid) {
    if (diagPollTimer) return;
    diagPollTimer = setInterval(async () => {
      try {
        const s = await apiFetch(`diagnostic-status.php?ticket_id=${tid}`);
        updateDiagUI(s, tid);
        if (s.bundle_ready || s.consent_status === 'expired' || s.consent_status === 'revoked' || s.consent_status === 'none') {
          clearInterval(diagPollTimer);
          diagPollTimer = null;
        }
      } catch (_) {}
    }, 30000);
  }

  function stopDiagPoll() {
    if (diagPollTimer) { clearInterval(diagPollTimer); diagPollTimer = null; }
  }

  function updateDiagUI(s, tid) {
    const status = s.consent_status || 'none';
    diagStatus.style.display = 'block';

    if (s.bundle_ready) {
      const kb = s.bundle_size_bytes ? Math.round(s.bundle_size_bytes / 1024) : '?';
      diagStatus.textContent = `Bundle received (${kb} KB) — support team is reviewing.`;
      diagStatus.style.background = 'rgba(34,197,94,0.15)';
      requestDiagBtn.style.display = 'none';
      revokeBtn.style.display = 'none';
    } else if (status === 'active') {
      const exp = s.expires_at ? new Date(s.expires_at.replace(' ', 'T') + 'Z').toLocaleTimeString() : '';
      diagStatus.textContent = `Diagnostic access granted — Pi is collecting data${exp ? ' (expires ' + exp + ')' : ''}.`;
      diagStatus.style.background = 'rgba(59,130,246,0.15)';
      requestDiagBtn.style.display = 'none';
      revokeBtn.style.display = 'block';
    } else if (status === 'revoked') {
      diagStatus.textContent = 'Diagnostic access revoked.';
      diagStatus.style.background = 'var(--surface-2, rgba(255,255,255,0.05))';
      requestDiagBtn.style.display = 'block';
      revokeBtn.style.display = 'none';
    } else if (status === 'expired') {
      diagStatus.textContent = 'Diagnostic session expired. You may request another.';
      diagStatus.style.background = 'var(--surface-2, rgba(255,255,255,0.05))';
      requestDiagBtn.style.display = 'block';
      revokeBtn.style.display = 'none';
    } else {
      requestDiagBtn.style.display = 'block';
      revokeBtn.style.display = 'none';
    }
  }

  // Show consent dialog
  requestDiagBtn.addEventListener('click', () => {
    const tid = parseInt(localStorage.getItem('support_ticket_id') || '0', 10);
    if (!tid) return;

    // Build inline consent dialog
    const overlay = el('div', {
      style: 'position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 24px;',
    });
    const dialog = el('div', {
      style: 'background: var(--surface-1, #1e1e2e); border-radius: 12px; padding: 24px; max-width: 380px; width: 100%;',
    });
    dialog.appendChild(el('h3', { style: 'font-size: 1.1rem; font-weight: 700; margin-bottom: 12px;' }, 'Allow Diagnostic Collection?'));
    dialog.appendChild(el('p', { style: 'font-size: 0.85rem; color: var(--text-muted); margin-bottom: 10px;' },
      'The following will be sent to AtMyBoat support for this ticket only:'));
    const list = el('ul', { style: 'font-size: 0.85rem; color: var(--text-muted); margin: 0 0 16px 18px; line-height: 1.8;' });
    ['System logs (last 24 hours)', 'Service status (d3kOS services)', 'Process list, disk & memory usage',
      'Config files (API keys removed)'].forEach(item => {
      list.appendChild(el('li', {}, item));
    });
    dialog.appendChild(list);
    dialog.appendChild(el('p', { style: 'font-size: 0.8rem; color: var(--text-muted); margin-bottom: 16px;' },
      'Access expires in 2 hours. You can revoke it at any time.'));

    const btnRow = el('div', { style: 'display: flex; gap: 10px;' });

    const approveBtn = el('button', { class: 'btn btn-primary', style: 'flex: 1;' }, 'Approve');
    approveBtn.addEventListener('click', async () => {
      approveBtn.disabled = true;
      approveBtn.textContent = 'Sending…';
      try {
        const res = await apiFetch('diagnostic-consent.php', {
          method: 'POST',
          body: JSON.stringify({ ticket_id: tid }),
        });
        overlay.remove();
        diagStatus.style.display = 'block';
        diagStatus.textContent = 'Diagnostic access granted — Pi is collecting data.';
        diagStatus.style.background = 'rgba(59,130,246,0.15)';
        requestDiagBtn.style.display = 'none';
        revokeBtn.style.display = 'block';
        startDiagPoll(tid);
      } catch (err) {
        approveBtn.disabled = false;
        approveBtn.textContent = 'Approve';
        dialog.appendChild(el('p', { style: 'color: #f87171; font-size: 0.85rem; margin-top: 8px;' },
          err.message || 'Failed — please try again.'));
      }
    });

    const declineBtn = el('button', { class: 'btn btn-ghost', style: 'flex: 1;' }, 'Decline');
    declineBtn.addEventListener('click', () => overlay.remove());

    btnRow.appendChild(approveBtn);
    btnRow.appendChild(declineBtn);
    dialog.appendChild(btnRow);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
  });

  // Revoke consent
  revokeBtn.addEventListener('click', async () => {
    const tid = parseInt(localStorage.getItem('support_ticket_id') || '0', 10);
    if (!tid) return;
    revokeBtn.disabled = true;
    revokeBtn.textContent = 'Revoking…';
    try {
      await apiFetch('diagnostic-revoke.php', {
        method: 'POST',
        body: JSON.stringify({ ticket_id: tid }),
      });
      stopDiagPoll();
      diagStatus.textContent = 'Diagnostic access revoked.';
      diagStatus.style.background = 'var(--surface-2, rgba(255,255,255,0.05))';
      revokeBtn.style.display = 'none';
      requestDiagBtn.style.display = 'block';
    } catch (_) {}
    revokeBtn.disabled = false;
    revokeBtn.textContent = 'Revoke Diagnostic Access';
  });

  diagPanel.appendChild(diagTitle);
  diagPanel.appendChild(diagDesc);
  diagPanel.appendChild(diagStatus);
  diagPanel.appendChild(requestDiagBtn);
  diagPanel.appendChild(revokeBtn);
  sentMsg.appendChild(diagPanel);

  const backToSettings = el('button', {
    class: 'btn btn-ghost',
    style: 'width: 100%; margin-top: 8px;',
  }, 'Back to Settings');
  backToSettings.addEventListener('click', () => navigate('settings'));
  sentMsg.appendChild(backToSettings);

  // Form
  const form = el('div', { class: 'support-form' });
  form.appendChild(el('p', {
    style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 16px;',
  }, 'Describe your issue and we\'ll get back to you. Your vessel and account info will be included automatically.'));

  const textarea = el('textarea', {
    class: 'support-textarea',
    placeholder: 'Describe your issue…',
    maxlength: '500',
    rows: '6',
    'aria-label': 'Support message',
  });
  form.appendChild(textarea);

  const charCount = el('div', { class: 'support-char-count' }, '0 / 500');
  textarea.addEventListener('input', () => {
    charCount.textContent = `${textarea.value.length} / 500`;
  });
  form.appendChild(charCount);

  const errorMsg = el('div', { class: 'support-error', style: 'display: none;' });
  form.appendChild(errorMsg);

  const sendBtn = el('button', { class: 'btn btn-primary', style: 'margin-top: 12px; width: 100%;' }, 'Send Message');
  sendBtn.addEventListener('click', async () => {
    const msg = textarea.value.trim();
    if (!msg || msg.length < 10) {
      errorMsg.textContent = 'Please enter at least 10 characters.';
      errorMsg.style.display = 'block';
      return;
    }
    errorMsg.style.display = 'none';
    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending…';

    try {
      const result = await apiFetch('support-request.php', {
        method: 'POST',
        body: JSON.stringify({ message: msg }),
      });
      if (result.ticket_id) {
        localStorage.setItem('support_ticket_id', String(result.ticket_id));
        sentTitle.textContent = `Message sent — Ticket #${result.ticket_id}`;
        ticketRow.textContent = `Reference: #${result.ticket_id}`;
        ticketRow.style.display = 'block';
        checkStatusBtn.style.display = 'block';
        diagPanel.style.display = 'block';
      }
      form.style.display = 'none';
      sentMsg.style.display = 'block';
    } catch (err) {
      errorMsg.textContent = err.message || 'Failed to send. Please try again.';
      errorMsg.style.display = 'block';
      sendBtn.disabled = false;
      sendBtn.textContent = 'Send Message';
    }
  });
  form.appendChild(sendBtn);

  // ── Restore state if ticket_id already in localStorage ───────────────────
  const existingTid = parseInt(localStorage.getItem('support_ticket_id') || '0', 10);
  if (existingTid) {
    sentTitle.textContent = `Ticket #${existingTid}`;
    ticketRow.textContent = `Reference: #${existingTid}`;
    ticketRow.style.display = 'block';
    checkStatusBtn.style.display = 'block';
    diagPanel.style.display = 'block';
    form.style.display = 'none';
    sentMsg.style.display = 'block';
    // Fetch current diagnostic status
    apiFetch(`diagnostic-status.php?ticket_id=${existingTid}`)
      .then(s => updateDiagUI(s, existingTid))
      .catch(() => {});
  }

  card.appendChild(sentMsg);
  card.appendChild(form);
  container.appendChild(card);
};

// ── Pair Screen ───────────────────────────────────────────────────────────────
// Three phases: scanning → confirm → done
screens.pair = function renderPair() {
  const container = getEl('screen');

  // Phase state
  let videoStream = null;
  let scanInterval = null;
  let detectedPiId = null;

  function stopCamera() {
    if (scanInterval) { clearInterval(scanInterval); scanInterval = null; }
    if (videoStream)  { videoStream.getTracks().forEach(t => t.stop()); videoStream = null; }
  }

  // ── Phase 1: Scanning ────────────────────────────────────────────────────
  function showScanning() {
    container.innerHTML = '';

    const title = el('div', { class: 'card-title', style: 'margin-bottom: 8px;' }, 'Pair a Vessel');
    const hint  = el('div', { style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 16px;' },
      'Point your camera at the QR code on your Pi\'s Settings page.');

    const video  = el('video', { autoplay: 'true', playsinline: 'true',
                                  style: 'width:100%;border-radius:8px;background:#000;' });
    const canvas = el('canvas', { style: 'display:none;' });
    const status = el('div', { style: 'margin-top: 12px; font-size: 0.9rem; color: var(--text-muted);' },
      'Starting camera…');

    const backBtn = el('button', {
      class: 'btn btn-ghost',
      style: 'margin-top: 12px;',
    }, 'Cancel');
    backBtn.addEventListener('click', () => {
      stopCamera();
      navigate(state.vessels.length > 0 ? 'dashboard' : 'select-vessel');
    });

    container.appendChild(title);
    container.appendChild(hint);
    container.appendChild(video);
    container.appendChild(canvas);
    container.appendChild(status);
    container.appendChild(backBtn);

    // Request rear camera
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
      .then(stream => {
        videoStream      = stream;
        video.srcObject  = stream;
        status.textContent = 'Scanning…';

        // Sample frames for QR every 250 ms
        scanInterval = setInterval(() => {
          if (video.readyState < video.HAVE_ENOUGH_DATA) return;

          canvas.width  = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx  = canvas.getContext('2d');
          ctx.drawImage(video, 0, 0);
          const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);

          // jsQR is loaded from CDN — check it is available
          if (typeof jsQR !== 'function') {
            status.textContent = 'QR scanner not loaded. Check your connection.';
            return;
          }

          const code = jsQR(imgData.data, imgData.width, imgData.height);
          if (code) {
            const piId = extractPiId(code.data);
            if (piId) {
              stopCamera();
              detectedPiId = piId;
              showConfirm(piId);
            } else {
              status.textContent = 'QR code found but not a d3kOS device. Try again.';
            }
          }
        }, 250);
      })
      .catch(err => {
        status.textContent = 'Camera access denied. Allow camera in browser settings.';
        status.style.color = 'var(--red)';
        console.error('Camera error:', err);
      });
  }

  // ── Phase 2: Confirm vessel details ─────────────────────────────────────
  function showConfirm(piId) {
    container.innerHTML = '';

    const title = el('div', { class: 'card-title', style: 'margin-bottom: 8px;' }, 'Name Your Vessel');
    const hint  = el('div', { style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 16px;' },
      'Pi ID: ' + piId.slice(0, 8) + '…');

    const nameInput = el('input', {
      type: 'text', placeholder: 'e.g. Morning Star', maxlength: '80',
      style: 'width:100%;margin-bottom:12px;',
    });

    const typeSelect = el('select', { style: 'width:100%;margin-bottom:16px;' });
    [
      ['powerboat', 'Powerboat'],
      ['sailboat',  'Sailboat'],
      ['catamaran', 'Catamaran'],
      ['trawler',   'Trawler'],
      ['pontoon',   'Pontoon'],
      ['other',     'Other'],
    ].forEach(([val, label]) => {
      const opt = el('option', { value: val }, label);
      typeSelect.appendChild(opt);
    });

    const errBanner = el('div', { class: 'error-banner', role: 'alert' });
    const confirmBtn = el('button', { class: 'btn btn-primary', style: 'width:100%;' }, 'Confirm Pairing');
    const backBtn2   = el('button', {
      class: 'btn btn-ghost',
      style: 'margin-top: 8px; width:100%;',
    }, 'Back — Scan Again');
    backBtn2.addEventListener('click', () => showScanning());

    confirmBtn.addEventListener('click', async () => {
      const vesselName = nameInput.value.trim();
      const vesselType = typeSelect.value;

      if (!vesselName) {
        errBanner.textContent = 'Please enter a vessel name.';
        errBanner.classList.add('visible');
        return;
      }

      confirmBtn.disabled    = true;
      confirmBtn.textContent = 'Pairing…';
      errBanner.classList.remove('visible');

      try {
        await apiPairDevice(piId, vesselName, vesselType);
        showDone(vesselName);
      } catch (err) {
        errBanner.textContent = err.message || 'Pairing failed. Please try again.';
        errBanner.classList.add('visible');
        confirmBtn.disabled    = false;
        confirmBtn.textContent = 'Confirm Pairing';
      }
    });

    // Allow Enter in name field to submit
    nameInput.addEventListener('keydown', e => { if (e.key === 'Enter') confirmBtn.click(); });

    container.appendChild(title);
    container.appendChild(hint);
    container.appendChild(el('label', { style: 'font-size:0.9rem;display:block;margin-bottom:4px;' }, 'Vessel Name'));
    container.appendChild(nameInput);
    container.appendChild(el('label', { style: 'font-size:0.9rem;display:block;margin-bottom:4px;' }, 'Vessel Type'));
    container.appendChild(typeSelect);
    container.appendChild(errBanner);
    container.appendChild(confirmBtn);
    container.appendChild(backBtn2);

    nameInput.focus();
  }

  // ── Phase 3: Success ────────────────────────────────────────────────────
  function showDone(vesselName) {
    container.innerHTML = '';
    container.appendChild(
      el('div', { class: 'empty-state' },
        el('div', { style: 'font-size: 2rem; margin-bottom: 12px;' }, '✓'),
        el('p', { style: 'font-weight: 700;' }, vesselName + ' paired!'),
        el('p', { style: 'font-size:0.9rem; color: var(--text-muted);' },
          'Your Pi will sync automatically within a few minutes.'),
      )
    );

    const goBtn = el('button', { class: 'btn btn-primary', style: 'margin-top: 16px;' }, 'Go to Dashboard');
    goBtn.addEventListener('click', async () => {
      // Reload vessels so the new pairing appears
      await loadVessels();
    });
    container.appendChild(goBtn);
  }

  showScanning();
};

// ── Fix My Pi Screen ──────────────────────────────────────────────────────────
// Three phases: disclaimer → progress → result
screens.fixmypi = function renderFixMyPi() {
  const container = getEl('screen');
  const piId = state.vessel ? state.vessel.pi_installation_id : null;

  if (!piId) {
    container.appendChild(
      el('div', { class: 'empty-state' },
        el('p', {}, 'No vessel selected. Return to Settings and select a vessel first.'),
        el('button', { class: 'btn btn-ghost', style: 'margin-top:12px;',
            onClick: () => navigate('settings') }, 'Back to Settings'),
      )
    );
    return;
  }

  // ── Phase 1: Disclaimer ─────────────────────────────────────────────────────
  function showDisclaimer() {
    container.innerHTML = '';
    container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom: 8px;' }, 'Fix My Pi'));

    const tier = state.tier || 'T1';

    // Tier-specific header
    let costLine = '';
    if (tier === 'T0') {
      container.appendChild(
        el('div', { class: 'empty-state' },
          el('p', {}, 'Fix My Pi is not available on T0.'),
          el('p', { style: 'font-size:0.9rem;color:var(--text-muted)' },
            'Upgrade your plan at atmyboat.com/upgrade.'),
          el('button', { class: 'btn btn-ghost', style: 'margin-top:12px;',
              onClick: () => navigate('settings') }, 'Back'),
        )
      );
      return;
    }
    if (tier === 'T1') costLine = '$29.99 — automatic refund if unsuccessful.';
    if (tier === 'T2') costLine = 'Uses 1 of your 3 monthly free checks.';
    if (tier === 'T3') costLine = 'Unlimited (T3 Admiral).';

    const disclaimerCard = el('div', { class: 'card' },
      el('div', { class: 'fmp-disclaimer-title' }, 'What Fix My Pi does'),
      el('ul', { class: 'fmp-disclaimer-list' },
        el('li', {}, 'Checks all d3kOS services — restarts any that have crashed'),
        el('li', {}, 'Checks disk space — trims oversized logs if needed'),
        el('li', {}, 'Verifies all required config files exist and are valid'),
        el('li', {}, 'Tests outbound network connectivity to AtMyBoat.com'),
      ),
      el('div', { class: 'fmp-disclaimer-title', style: 'margin-top:12px;' }, 'What it does not do'),
      el('ul', { class: 'fmp-disclaimer-list' },
        el('li', {}, 'Does not upgrade d3kOS software (use OTA Upgrade for that)'),
        el('li', {}, 'Does not recover from hardware failure or SD card corruption'),
        el('li', {}, 'No guarantee that all issues can be resolved remotely'),
      ),
      el('div', { class: 'fmp-cost-line' }, costLine),
    );
    container.appendChild(disclaimerCard);

    const errEl = el('div', { class: 'error-banner', role: 'alert' });
    container.appendChild(errEl);

    const startBtn = el('button', { class: 'btn btn-primary', style: 'margin-top:8px;' },
      tier === 'T1' ? 'Pay $29.99 and Start' :
      tier === 'T2' ? 'Use Free Check' : 'Start Diagnostics'
    );
    const backBtn = el('button', {
      class: 'btn btn-ghost', style: 'margin-top:8px;',
      onClick: () => navigate('settings'),
    }, 'Cancel');
    container.appendChild(startBtn);
    container.appendChild(backBtn);

    startBtn.addEventListener('click', async () => {
      startBtn.disabled    = true;
      startBtn.textContent = 'Starting…';
      errEl.classList.remove('visible');
      try {
        const data = await apiFmpRequest(piId);
        if (data.tier === 'T1' && data.checkout_url) {
          // Stripe configured — open checkout, then show payment-wait phase
          window.open(data.checkout_url, '_blank', 'noopener');
          showPaymentWait();
        } else {
          // T2/T3, or T1 test mode (Stripe not yet configured)
          showProgress(data.command_id, data.tier, data.fmp_remaining);
        }
      } catch (err) {
        errEl.textContent = err.message || 'Failed to start. Please try again.';
        errEl.classList.add('visible');
        startBtn.disabled    = false;
        startBtn.textContent = tier === 'T1' ? 'Pay $29.99 and Start' :
                               tier === 'T2' ? 'Use Free Check' : 'Start Diagnostics';
      }
    });
  }

  // ── Phase 2a: T1 — waiting for Stripe payment confirmation ─────────────────
  function showPaymentWait() {
    container.innerHTML = '';
    container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom: 8px;' }, 'Fix My Pi'));
    container.appendChild(el('div', { class: 'card' },
      el('div', { style: 'text-align:center;padding:16px 0;' },
        spinner(),
        el('div', { style: 'margin-top:12px;font-size:0.9rem;color:var(--text-muted);' },
          'Waiting for payment confirmation…'),
        el('div', { style: 'margin-top:8px;font-size:0.85rem;color:var(--text-muted);' },
          'Complete checkout in the browser tab that opened.'),
      )
    ));

    const cancelBtn = el('button', {
      class: 'btn btn-ghost', style: 'margin-top:8px;',
      onClick: () => showDisclaimer(),
    }, 'Cancel');
    container.appendChild(cancelBtn);

    // Poll latest_fmp every 5s — once command appears, switch to progress phase
    let elapsed = 0;
    const MAX_WAIT = 15 * 60 * 1000; // 15 min (Stripe session timeout)
    const pollId = setInterval(async () => {
      elapsed += 5000;
      try {
        const data = await apiFmpPollLatest(piId);
        if (data.found) {
          clearInterval(pollId);
          if (data.status === 'completed' || data.status === 'failed') {
            showResult(data.result, data.status);
          } else {
            showProgress(data.command_id, 'T1', null);
          }
        }
      } catch { /* poll failure is non-fatal — keep trying */ }
      if (elapsed >= MAX_WAIT) {
        clearInterval(pollId);
        container.innerHTML = '';
        container.appendChild(
          el('div', { class: 'error-banner visible', role: 'alert' },
            'Payment not confirmed after 15 minutes. If you completed payment, check atmyboat.com/dashboard for status.')
        );
        container.appendChild(el('button', {
          class: 'btn btn-ghost', style: 'margin-top:8px;',
          onClick: () => navigate('settings'),
        }, 'Back to Settings'));
      }
    }, 5000);
  }

  // ── Phase 2b: Command queued — polling for Pi to execute and report back ────
  function showProgress(commandId, tier, fmpRemaining) {
    container.innerHTML = '';
    container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom: 8px;' }, 'Fix My Pi'));

    const statusEl = el('div', { style: 'font-size:0.9rem;color:var(--text-muted);margin-top:8px;' },
      'Diagnostic queued — waiting for Pi to connect…');
    const subEl = el('div', { style: 'font-size:0.85rem;color:var(--text-muted);margin-top:4px;' },
      'Pi polls for commands every 30 seconds.');

    if (fmpRemaining !== null && fmpRemaining !== undefined) {
      const remEl = el('div', {
        style: 'font-size:0.85rem;color:var(--text-muted);margin-top:4px;',
      }, tier === 'T2'
          ? `${fmpRemaining} free check${fmpRemaining === 1 ? '' : 's'} remaining this month.`
          : 'Unlimited checks (T3).');
      container.appendChild(
        el('div', { class: 'card' },
          el('div', { style: 'text-align:center;padding:16px 0;' }, spinner()),
          statusEl, subEl, remEl,
        )
      );
    } else {
      container.appendChild(
        el('div', { class: 'card' },
          el('div', { style: 'text-align:center;padding:16px 0;' }, spinner()),
          statusEl, subEl,
        )
      );
    }

    // Poll command status every 10s, timeout after 10 min
    let elapsed = 0;
    const MAX_WAIT = 10 * 60 * 1000;
    const pollId = setInterval(async () => {
      elapsed += 10000;
      try {
        const data = await apiPollCommand(commandId);
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(pollId);
          showResult(data.result, data.status);
        } else if (elapsed >= MAX_WAIT) {
          clearInterval(pollId);
          statusEl.textContent = 'Pi did not respond within 10 minutes. Check that your Pi is powered on and connected.';
          statusEl.style.color = 'var(--red)';
          subEl.style.display  = 'none';
          container.appendChild(el('button', {
            class: 'btn btn-ghost', style: 'margin-top:8px;',
            onClick: () => navigate('settings'),
          }, 'Back to Settings'));
        } else {
          statusEl.textContent = `Running diagnostics… (${Math.round(elapsed / 60000)}m elapsed)`;
        }
      } catch { /* poll failure is non-fatal */ }
    }, 10000);
  }

  // ── Phase 3: Result display ─────────────────────────────────────────────────
  function showResult(result, cmdStatus) {
    container.innerHTML = '';
    container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom: 8px;' }, 'Fix My Pi — Report'));

    if (!result) {
      container.appendChild(
        el('div', { class: 'error-banner visible', role: 'alert' },
          cmdStatus === 'failed'
            ? 'Diagnostic failed. No report returned. If you paid, a refund will be issued automatically.'
            : 'No report data received.')
      );
      container.appendChild(el('button', {
        class: 'btn btn-ghost', style: 'margin-top:12px;',
        onClick: () => navigate('settings'),
      }, 'Back to Settings'));
      return;
    }

    const overall = result.ok;
    const summaryCard = el('div', { class: 'card' });
    const statusBadge = el('div', {
      class: 'fmp-result-badge ' + (overall ? 'ok' : 'fail'),
    }, overall ? '✓ All clear' : '✗ Issues found');
    summaryCard.appendChild(statusBadge);

    if (result.timestamp) {
      summaryCard.appendChild(el('div', {
        style: 'font-size:0.82rem;color:var(--text-muted);margin-top:6px;',
      }, 'Completed: ' + fmtTime(result.timestamp)));
    }
    container.appendChild(summaryCard);

    // Checks table
    if (result.checks && result.checks.length > 0) {
      const checksCard = el('div', { class: 'card' });
      checksCard.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:8px;' }, 'Checks'));
      result.checks.forEach(c => {
        const label = c.service || c.check || c.config || 'check';
        const shortLabel = label.replace('/opt/d3kos/config/', '').replace('d3kos-', '');
        let detail = '';
        if (c.state)     detail = c.state;
        if (c.free_mb)   detail = `${c.free_mb}MB free (${c.used_pct}% used)`;
        if (c.http_status) detail = `HTTP ${c.http_status}`;
        if (c.reason)    detail = c.reason;
        if (!c.ok && c.recovered) detail += ' → recovered';

        checksCard.appendChild(
          el('div', { class: 'fmp-check-row' },
            el('span', { class: 'fmp-check-icon ' + (c.ok || c.recovered ? 'ok' : 'fail') },
              c.ok ? '✓' : c.recovered ? '↺' : '✗'),
            el('div', { class: 'fmp-check-info' },
              el('div', { class: 'fmp-check-name' }, shortLabel),
              detail ? el('div', { class: 'fmp-check-detail' }, detail) : null,
            ),
          )
        );
      });
      container.appendChild(checksCard);
    }

    // Actions taken
    if (result.actions_taken && result.actions_taken.length > 0) {
      const actCard = el('div', { class: 'card' });
      actCard.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:8px;' }, 'Actions Taken'));
      result.actions_taken.forEach(a => {
        actCard.appendChild(el('div', { class: 'fmp-action-item' }, a));
      });
      container.appendChild(actCard);
    }

    // Errors
    if (result.errors && result.errors.length > 0) {
      const errCard = el('div', { class: 'card' });
      errCard.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:8px;' }, 'Errors'));
      result.errors.forEach(e => {
        errCard.appendChild(el('div', { class: 'fmp-error-item' }, e));
      });
      container.appendChild(errCard);
    }

    // T1 refund notice on failure
    if (!overall && state.tier === 'T1') {
      container.appendChild(
        el('div', { class: 'card', style: 'border-color:var(--amber);' },
          el('div', { style: 'font-size:0.9rem;color:var(--amber);' },
            'A refund will be issued automatically to your payment method within 5–10 business days. '
            + 'Contact skipperdon@atmyboat.com if you have questions.'),
        )
      );
    }

    container.appendChild(el('button', {
      class: 'btn btn-ghost', style: 'margin-top:8px;',
      onClick: () => navigate('settings'),
    }, 'Back to Settings'));
  }

  // Entry point: check for post-payment return
  if (state._fmpPostPayment === piId) {
    state._fmpPostPayment = null;
    showPaymentWait();
  } else {
    showDisclaimer();
  }
};

// ── Fleet Screen (T3 only) ────────────────────────────────────────────────────

// Fleet API helpers
function apiFleetMap(fleetId)       { return apiFetch(`fleet-map.php?fleet_id=${fleetId}`); }
function apiFleetAnalytics(fleetId) { return apiFetch(`fleet-analytics.php?fleet_id=${fleetId}`); }
function apiFleetCreate(name, fleetType) {
  return apiFetch('fleet-create.php', {
    method: 'POST',
    body: JSON.stringify({ name, fleet_type: fleetType }),
  });
}
function apiFleetJoin(fleetCode) {
  return apiFetch('fleet-join.php', {
    method: 'POST',
    body: JSON.stringify({ fleet_code: fleetCode.toUpperCase() }),
  });
}
function apiFleetStatus()            { return apiFetch('fleet-status.php'); }
function apiFleetLeave(fleetId) {
  return apiFetch('fleet-leave.php', {
    method: 'POST',
    body: JSON.stringify({ fleet_id: fleetId }),
  });
}

// Fleet state persisted in localStorage
function saveFleetSession() {
  if (state.fleetId) localStorage.setItem('amboat_fleet_id', String(state.fleetId));
  else               localStorage.removeItem('amboat_fleet_id');
}
function loadFleetSession() {
  const fid = localStorage.getItem('amboat_fleet_id');
  state.fleetId = fid ? parseInt(fid, 10) : null;
}

// Show fleet nav button for all tiers — T1/T2 see locked upgrade card, T3 sees full screen
function updateFleetNavVisibility() {
  const btn = document.getElementById('fleet-nav-btn');
  if (btn) btn.style.display = '';
}

// ── Fleet setup screen (join or create) ──────────────────────────────────────
function renderFleetSetup() {
  const container = getEl('screen');

  const header = el('div', { class: 'screen-header' });
  header.appendChild(el('span', { class: 'screen-title' }, 'Fleet Management'));
  container.appendChild(header);

  // Show spinner while checking existing membership
  const statusCard = el('div', { class: 'card' });
  statusCard.appendChild(spinner());
  container.appendChild(statusCard);

  // Check if this device is already in a fleet (e.g. localStorage cleared after joining)
  apiFleetStatus().then(status => {
    statusCard.innerHTML = '';

    if (status) {
      // Already in a fleet — show membership card with view + leave/delete
      _renderFleetMembershipCard(statusCard, status);
      return;
    }

    // Not in a fleet — show join/create form
    _renderFleetJoinCreate(statusCard);

  }).catch(() => {
    // Status check failed — still show join/create (let the actions surface the real error)
    statusCard.innerHTML = '';
    _renderFleetJoinCreate(statusCard);
  });
}

// ── Existing membership card ──────────────────────────────────────────────────
function _renderFleetMembershipCard(card, status) {
  const isOwner = status.role === 'owner';
  const roleLabel = isOwner ? 'Fleet Owner' : 'Member';

  card.appendChild(el('div', { class: 'card-title' }, status.fleet_name));
  card.appendChild(el('p', { style: 'font-size:1rem;color:var(--text-muted);margin-bottom:4px;' },
    `Role: ${roleLabel}  ·  ${status.member_count} vessel${status.member_count !== 1 ? 's' : ''}`
  ));
  card.appendChild(el('p', { style: 'font-size:1.2rem;font-weight:700;letter-spacing:0.12em;color:var(--accent);margin-bottom:16px;' },
    `Code: ${status.fleet_code}`
  ));

  const viewBtn = el('button', { class: 'btn btn-primary', style: 'width:100%;margin-bottom:8px;' }, 'View Fleet Map →');
  viewBtn.addEventListener('click', () => {
    state.fleetId = status.fleet_id;
    saveFleetSession();
    state.fleetData     = null;
    state.fleetAnalytics = null;
    navigate('fleet');
  });
  card.appendChild(viewBtn);

  const actionLabel = isOwner ? 'Delete Fleet' : 'Remove Me From Fleet';
  const leaveBtn = el('button', {
    class: 'btn btn-ghost',
    style: 'width:100%;color:var(--red);border-color:var(--red);',
  }, actionLabel);
  const leaveMsg = el('div', { style: 'margin-top:8px;font-size:0.95rem;display:none;' });

  let confirmPending = false;
  leaveBtn.addEventListener('click', async () => {
    if (!confirmPending) {
      // First tap: ask for confirmation
      confirmPending = true;
      leaveBtn.textContent = isOwner
        ? '⚠ Tap again to DELETE fleet and all data'
        : '⚠ Tap again to confirm — removes your vessel from this fleet';
      leaveBtn.style.background = 'var(--red)';
      leaveBtn.style.color = '#fff';
      return;
    }
    leaveBtn.disabled    = true;
    leaveBtn.textContent = isOwner ? 'Deleting…' : 'Leaving…';
    leaveMsg.style.display = 'none';
    try {
      await apiFleetLeave(status.fleet_id);
      state.fleetId        = null;
      state.fleetData      = null;
      state.fleetAnalytics = null;
      saveFleetSession();
      navigate('fleet');
    } catch (err) {
      leaveMsg.textContent   = err.message || `Could not ${isOwner ? 'delete fleet' : 'remove vessel from fleet'}.`;
      leaveMsg.style.color   = 'var(--red)';
      leaveMsg.style.display = 'block';
      leaveBtn.disabled    = false;
      leaveBtn.textContent = actionLabel;
      confirmPending = false;
    }
  });

  card.appendChild(leaveBtn);
  card.appendChild(leaveMsg);
}

// ── Join / Create form ────────────────────────────────────────────────────────
function _renderFleetJoinCreate(card) {
  card.appendChild(el('div', { class: 'card-title' }, 'Join or Create a Fleet'));
  card.appendChild(el('p', { style: 'font-size:1rem;color:var(--text-muted);margin-bottom:16px;line-height:1.6;' },
    'A fleet lets you monitor multiple vessels from one screen. Enter a 6-character fleet code to join an existing fleet, or create a new one.'
  ));

  // ── Join section ──
  const joinTitle = el('div', { style: 'font-weight:700;font-size:1rem;margin-bottom:8px;' }, 'Join a Fleet');
  const codeInput = el('input', {
    type: 'text',
    maxlength: '6',
    placeholder: 'Fleet code (e.g. ABC123)',
    class: 'input-field',
    style: 'text-transform:uppercase;letter-spacing:0.1em;font-size:1.1rem;',
    'aria-label': 'Fleet code',
  });
  const joinBtn = el('button', { class: 'btn btn-primary', style: 'margin-top:8px;width:100%;' }, 'Join Fleet');
  const joinMsg = el('div', { style: 'margin-top:8px;font-size:0.95rem;display:none;' });

  joinBtn.addEventListener('click', async () => {
    const code = codeInput.value.trim().toUpperCase();
    if (code.length !== 6) {
      joinMsg.textContent   = 'Enter a 6-character fleet code.';
      joinMsg.style.color   = 'var(--red)';
      joinMsg.style.display = 'block';
      return;
    }
    joinBtn.disabled    = true;
    joinBtn.textContent = 'Joining…';
    joinMsg.style.display = 'none';
    try {
      const data = await apiFleetJoin(code);
      state.fleetId = data.fleet_id;
      saveFleetSession();
      navigate('fleet');
    } catch (err) {
      joinMsg.textContent   = err.message || 'Could not join fleet.';
      joinMsg.style.color   = 'var(--red)';
      joinMsg.style.display = 'block';
      joinBtn.disabled    = false;
      joinBtn.textContent = 'Join Fleet';
    }
  });

  card.appendChild(joinTitle);
  card.appendChild(codeInput);
  card.appendChild(joinBtn);
  card.appendChild(joinMsg);

  // ── Divider ──
  card.appendChild(el('hr', { style: 'margin:20px 0;border-color:var(--border);' }));

  // ── Create section ──
  const createTitle = el('div', { style: 'font-weight:700;font-size:1rem;margin-bottom:8px;' }, 'Create a New Fleet');
  const nameInput = el('input', {
    type: 'text',
    maxlength: '100',
    placeholder: 'Fleet name (e.g. My Charter Fleet)',
    class: 'input-field',
    'aria-label': 'Fleet name',
  });
  const typeSelect = el('select', {
    class: 'input-field',
    style: 'margin-top:8px;',
    'aria-label': 'Fleet type',
  });
  [['charter', 'Charter'], ['fishing', 'Fishing'], ['marina', 'Marina'], ['other', 'Other']].forEach(([v, l]) => {
    typeSelect.appendChild(el('option', { value: v }, l));
  });
  const createBtn = el('button', { class: 'btn btn-ghost', style: 'margin-top:8px;width:100%;' }, 'Create Fleet');
  const createMsg = el('div', { style: 'margin-top:8px;font-size:0.95rem;display:none;' });

  createBtn.addEventListener('click', async () => {
    const name = nameInput.value.trim();
    if (!name) {
      createMsg.textContent   = 'Fleet name is required.';
      createMsg.style.color   = 'var(--red)';
      createMsg.style.display = 'block';
      return;
    }
    createBtn.disabled    = true;
    createBtn.textContent = 'Creating…';
    createMsg.style.display = 'none';
    try {
      const data = await apiFleetCreate(name, typeSelect.value);
      state.fleetId = data.fleet_id;
      saveFleetSession();
      createMsg.innerHTML   = `Fleet created! Share code <strong style="font-size:1.3em;letter-spacing:0.1em;color:var(--accent)">${data.fleet_code}</strong> with other vessels to join.`;
      createMsg.style.color = 'var(--text)';
      createMsg.style.display = 'block';
      createBtn.textContent = 'View Fleet →';
      createBtn.disabled    = false;
      createBtn.onclick     = () => navigate('fleet');
    } catch (err) {
      createMsg.textContent   = err.message || 'Could not create fleet.';
      createMsg.style.color   = 'var(--red)';
      createMsg.style.display = 'block';
      createBtn.disabled    = false;
      createBtn.textContent = 'Create Fleet';
    }
  });

  card.appendChild(createTitle);
  card.appendChild(nameInput);
  card.appendChild(typeSelect);
  card.appendChild(createBtn);
  card.appendChild(createMsg);
}

// ── Fleet map + vessel list (main fleet view) ─────────────────────────────────
function renderFleetMap(fleetData, analytics) {
  const container = getEl('screen');
  const vessels   = fleetData.vessels || [];
  const summary   = analytics ? analytics.fleet_summary : null;

  // Header row: fleet name + refresh button
  const header = el('div', { class: 'screen-header' });
  header.appendChild(el('span', { class: 'screen-title' }, fleetData.fleet_name || 'Fleet'));
  const refreshBtn = el('button', {
    class: 'btn btn-ghost',
    style: 'padding:6px 12px;font-size:0.9rem;',
    'aria-label': 'Refresh fleet data',
  }, 'Refresh');
  refreshBtn.addEventListener('click', () => {
    state.fleetData     = null;
    state.fleetAnalytics = null;
    navigate('fleet');
  });
  header.appendChild(refreshBtn);
  container.appendChild(header);

  // Toggle buttons: Map / List / Analytics
  const toggleBar     = el('div', { class: 'fleet-toggle-bar', role: 'tablist' });
  const mapTabBtn     = el('button', { class: 'fleet-tab active', role: 'tab', 'aria-selected': 'true',  id: 'tab-map'       }, 'Map');
  const listTabBtn    = el('button', { class: 'fleet-tab',        role: 'tab', 'aria-selected': 'false', id: 'tab-list'      }, 'Vessels');
  const analyticsTabBtn = el('button', { class: 'fleet-tab',      role: 'tab', 'aria-selected': 'false', id: 'tab-analytics' }, 'Analytics');
  toggleBar.appendChild(mapTabBtn);
  toggleBar.appendChild(listTabBtn);
  toggleBar.appendChild(analyticsTabBtn);
  container.appendChild(toggleBar);

  // Content panels
  const mapPanel       = el('div', { id: 'fleet-map-panel',       role: 'tabpanel', 'aria-labelledby': 'tab-map'       });
  const listPanel      = el('div', { id: 'fleet-list-panel',      role: 'tabpanel', 'aria-labelledby': 'tab-list',      style: 'display:none;' });
  const analyticsPanel = el('div', { id: 'fleet-analytics-panel', role: 'tabpanel', 'aria-labelledby': 'tab-analytics', style: 'display:none;' });
  container.appendChild(mapPanel);
  container.appendChild(listPanel);
  container.appendChild(analyticsPanel);

  function setActiveTab(active) {
    [mapTabBtn, listTabBtn, analyticsTabBtn].forEach(btn => {
      btn.classList.remove('active');
      btn.setAttribute('aria-selected', 'false');
    });
    [mapPanel, listPanel, analyticsPanel].forEach(p => { p.style.display = 'none'; });
    active.btn.classList.add('active');
    active.btn.setAttribute('aria-selected', 'true');
    active.panel.style.display = '';
    if (active.onShow) active.onShow();
  }

  mapTabBtn.addEventListener('click', () => setActiveTab({
    btn: mapTabBtn, panel: mapPanel,
    onShow: () => { if (window._fleetLeafletMap) window._fleetLeafletMap.invalidateSize(); },
  }));
  listTabBtn.addEventListener('click', () => setActiveTab({ btn: listTabBtn, panel: listPanel }));
  analyticsTabBtn.addEventListener('click', () => setActiveTab({
    btn: analyticsTabBtn, panel: analyticsPanel,
    onShow: () => _initAnalyticsChart(),
  }));

  // ── MAP PANEL ──────────────────────────────────────────────────────────────
  const mapDiv = el('div', { id: 'leaflet-map', style: 'width:100%;height:340px;border-radius:8px;overflow:hidden;' });
  mapPanel.appendChild(mapDiv);

  // Fleet summary strip below map
  if (summary) {
    const strip = el('div', { class: 'fleet-summary-strip' });
    [
      ['Active 24h',    summary.vessels_active_24h ?? '—'],
      ['Engine Hours',  summary.total_engine_hours  != null ? summary.total_engine_hours.toFixed(0) + 'h' : '—'],
      ['Avg RPM',       summary.fleet_avg_rpm        != null ? Math.round(summary.fleet_avg_rpm)           : '—'],
    ].forEach(([label, value]) => {
      const item = el('div', { class: 'fleet-stat-item' });
      item.appendChild(el('div', { class: 'fleet-stat-value' }, String(value)));
      item.appendChild(el('div', { class: 'fleet-stat-label' }, label));
      strip.appendChild(item);
    });
    mapPanel.appendChild(strip);
  }

  // Init Leaflet map (after DOM insertion, requestAnimationFrame to ensure size)
  requestAnimationFrame(() => {
    if (typeof L === 'undefined') {
      mapDiv.innerHTML = '<p style="padding:16px;color:var(--text-muted);font-size:0.95rem;">Map unavailable — Leaflet did not load. Check internet connection.</p>';
      return;
    }

    // Compute centroid of all vessels with GPS
    const withGPS = vessels.filter(v => v.lat != null && v.lon != null);
    const centerLat = withGPS.length ? withGPS.reduce((s, v) => s + v.lat, 0) / withGPS.length : 43.65;
    const centerLon = withGPS.length ? withGPS.reduce((s, v) => s + v.lon, 0) / withGPS.length : -79.38;

    // Destroy old map instance if any (navigating back to fleet)
    if (window._fleetLeafletMap) {
      try { window._fleetLeafletMap.remove(); } catch { /* ignore */ }
      window._fleetLeafletMap = null;
    }

    const map = L.map('leaflet-map', { zoomControl: true, attributionControl: false });
    window._fleetLeafletMap = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© OpenStreetMap',
    }).addTo(map);

    map.setView([centerLat, centerLon], withGPS.length > 1 ? 12 : 14);

    // Status color by age
    function markerColor(ageMin) {
      if (ageMin == null)  return '#6b7280';  // grey — no data
      if (ageMin <= 10)    return '#22c55e';  // green
      if (ageMin <= 60)    return '#f59e0b';  // amber
      return '#ef4444';                        // red
    }

    withGPS.forEach(v => {
      const color = markerColor(v.age_minutes);
      const icon = L.divIcon({
        className: '',
        html: `<div style="width:14px;height:14px;border-radius:50%;background:${color};border:2px solid rgba(255,255,255,0.8);box-shadow:0 0 6px rgba(0,0,0,0.5);"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7],
        popupAnchor: [0, -10],
      });

      const shortTok = v.device_token ? v.device_token.slice(-8) : 'unknown';
      const ageStr   = v.age_minutes != null ? `${v.age_minutes}m ago` : 'unknown';
      const sogStr   = v.sog != null ? `${v.sog} kn` : '—';
      const cogStr   = v.cog != null ? `${Math.round(v.cog)}°` : '—';
      const roleStr  = v.role === 'owner' ? ' (owner)' : '';

      const popup = `
        <div style="font-family:Nunito,sans-serif;font-size:14px;min-width:140px;">
          <strong>${shortTok}${roleStr}</strong><br>
          <span style="color:#6b7280;">Last seen: ${ageStr}</span><br>
          SOG ${sogStr} &nbsp; COG ${cogStr}
        </div>`;

      L.marker([v.lat, v.lon], { icon }).addTo(map).bindPopup(popup);
    });

    // Fit all markers if multiple
    if (withGPS.length > 1) {
      try {
        const bounds = L.latLngBounds(withGPS.map(v => [v.lat, v.lon]));
        map.fitBounds(bounds, { padding: [30, 30], maxZoom: 14 });
      } catch { /* ignore bounds errors */ }
    }
  });

  // ── LIST PANEL ─────────────────────────────────────────────────────────────
  // Per-vessel analytics lookup map
  const analyticsMap = {};
  if (analytics && analytics.vessels) {
    analytics.vessels.forEach(av => { analyticsMap[av.device_token] = av; });
  }

  vessels.forEach(v => {
    const av        = analyticsMap[v.device_token];
    const ageMin    = v.age_minutes;
    const shortTok  = v.device_token ? v.device_token.slice(-8) : 'unknown';
    const isOwner   = v.role === 'owner';

    // Status dot color
    let dotColor = '#6b7280';
    if (ageMin != null) {
      if (ageMin <= 10) dotColor = '#22c55e';
      else if (ageMin <= 60) dotColor = '#f59e0b';
      else dotColor = '#ef4444';
    }

    const card = el('div', { class: 'card fleet-vessel-card' });

    // Title row: token + role badge + status dot
    const titleRow = el('div', { class: 'fleet-vessel-title-row' });
    const dot = el('span', { class: 'fleet-vessel-dot', style: `background:${dotColor};`, 'aria-hidden': 'true' });
    const namePart = el('span', { class: 'fleet-vessel-name' }, shortTok);
    titleRow.appendChild(dot);
    titleRow.appendChild(namePart);
    if (isOwner) {
      titleRow.appendChild(el('span', { class: 'fleet-role-badge' }, 'owner'));
    }
    card.appendChild(titleRow);

    // Stat rows
    const stats = [
      ['Last seen',     ageMin != null ? `${ageMin} min ago` : '—'],
      ['SOG',           v.sog  != null ? `${v.sog} kn`       : '—'],
      ['COG',           v.cog  != null ? `${Math.round(v.cog)}°` : '—'],
    ];
    if (av) {
      stats.push(['Engine hrs', av.engine_hours_7d != null ? av.engine_hours_7d.toFixed(1) + 'h (7d)' : '—']);
      stats.push(['Avg RPM',    av.avg_rpm_24h     != null ? Math.round(av.avg_rpm_24h)                : '—']);
    }
    stats.forEach(([label, value]) => {
      card.appendChild(
        el('div', { class: 'stat-item' },
          el('div', { class: 'stat-label' }, label),
          el('div', { class: 'stat-value' }, String(value)),
        )
      );
    });

    listPanel.appendChild(card);
  });

  // "Leave fleet" link at bottom
  const leaveBtn = el('button', {
    class: 'btn btn-ghost',
    style: 'margin-top:8px;width:100%;color:var(--red);border-color:var(--red);',
  }, 'Leave Fleet');
  leaveBtn.addEventListener('click', () => {
    if (!confirm('Leave this fleet? Your vessel will no longer appear on the fleet map.')) return;
    state.fleetId = null;
    state.fleetData = null;
    state.fleetAnalytics = null;
    saveFleetSession();
    navigate('fleet');
  });
  listPanel.appendChild(leaveBtn);

  // ── ANALYTICS PANEL ────────────────────────────────────────────────────────
  _renderAnalyticsPanel(analyticsPanel, analytics, fleetData);
}

// ── Fleet analytics panel ─────────────────────────────────────────────────────
function _renderAnalyticsPanel(container, analytics, fleetData) {
  const vessels = analytics ? (analytics.vessels || []) : [];
  const summary = analytics ? analytics.fleet_summary : null;

  // ── Fleet summary cards ──
  if (summary) {
    const summaryRow = el('div', { class: 'fleet-analytics-summary' });
    [
      ['Active 24h',    String(summary.vessels_active_24h ?? '—')],
      ['Total Hours',   summary.total_engine_hours != null ? summary.total_engine_hours.toFixed(0) + 'h' : '—'],
      ['Fleet Avg RPM', summary.fleet_avg_rpm      != null ? String(Math.round(summary.fleet_avg_rpm))   : '—'],
      ['Alerts (30d)',  summary.fleet_alerts_30d   != null ? String(summary.fleet_alerts_30d)            : '—'],
    ].forEach(([label, value]) => {
      const card = el('div', { class: 'fleet-analytics-stat' });
      card.appendChild(el('div', { class: 'fleet-analytics-stat-value' }, value));
      card.appendChild(el('div', { class: 'fleet-analytics-stat-label' }, label));
      summaryRow.appendChild(card);
    });
    container.appendChild(summaryRow);
  }

  // ── Best / Worst vessel ──
  const withHours = vessels.filter(v => v.engine_hours_total != null);
  if (withHours.length >= 2) {
    const sorted   = [...withHours].sort((a, b) => b.engine_hours_total - a.engine_hours_total);
    const most     = sorted[0];
    const least    = sorted[sorted.length - 1];
    const bwCard   = el('div', { class: 'card fleet-analytics-bw' });
    bwCard.appendChild(el('div', { class: 'card-title', style: 'font-size:0.95rem;margin-bottom:8px;' }, 'Engine Hours — Fleet Range'));
    const bwRow = el('div', { style: 'display:flex;gap:12px;' });
    [
      ['Most hrs', most.device_token.slice(-8),   most.engine_hours_total.toFixed(0) + 'h',  'var(--amber)'],
      ['Least hrs', least.device_token.slice(-8), least.engine_hours_total.toFixed(0) + 'h', 'var(--accent)'],
    ].forEach(([lbl, name, val, color]) => {
      const cell = el('div', { style: 'flex:1;text-align:center;' });
      cell.appendChild(el('div', { style: `font-size:1.4rem;font-weight:700;color:${color};font-family:'JetBrains Mono',monospace;` }, val));
      cell.appendChild(el('div', { style: 'font-size:0.85rem;color:var(--text-muted);' }, name));
      cell.appendChild(el('div', { style: 'font-size:0.75rem;color:var(--text-muted);margin-top:2px;' }, lbl));
      bwRow.appendChild(cell);
    });
    bwCard.appendChild(bwRow);
    container.appendChild(bwCard);
  }

  // ── Engine hours bar chart ──
  const chartCard = el('div', { class: 'card' });
  chartCard.appendChild(el('div', { class: 'card-title', style: 'font-size:0.95rem;margin-bottom:12px;' }, 'Engine Hours per Vessel (7-day)'));
  const canvasWrap = el('div', { style: 'position:relative;height:200px;' });
  const canvas     = el('canvas', { id: 'fleet-eng-chart', 'aria-label': 'Engine hours bar chart' });
  canvasWrap.appendChild(canvas);
  chartCard.appendChild(canvasWrap);

  if (vessels.length === 0) {
    chartCard.appendChild(el('p', { style: 'font-size:0.95rem;color:var(--text-muted);padding:8px 0;' }, 'No vessel data available yet.'));
  }
  container.appendChild(chartCard);

  // Store data for lazy chart init (called when tab becomes visible)
  container._chartData = {
    labels: vessels.map(v => v.device_token.slice(-8)),
    hours7d: vessels.map(v => v.engine_hours_7d ?? 0),
  };

  // ── Per-vessel stats table ──
  if (vessels.length > 0) {
    const tableCard = el('div', { class: 'card' });
    tableCard.appendChild(el('div', { class: 'card-title', style: 'font-size:0.95rem;margin-bottom:10px;' }, 'Vessel Stats (24h average)'));

    vessels.forEach(v => {
      const row = el('div', { class: 'fleet-analytics-row' });
      const roleTag = v.role === 'owner'
        ? el('span', { class: 'fleet-role-badge', style: 'font-size:0.7rem;padding:1px 6px;' }, 'owner')
        : null;

      const nameCell = el('div', { class: 'fleet-analytics-vessel-name' });
      nameCell.appendChild(document.createTextNode(v.device_token.slice(-8) + ' '));
      if (roleTag) nameCell.appendChild(roleTag);
      row.appendChild(nameCell);

      const statsCell = el('div', { class: 'fleet-analytics-vessel-stats' });
      [
        ['RPM',      v.avg_rpm_24h     != null ? Math.round(v.avg_rpm_24h)        : '—'],
        ['Cool',     v.avg_coolant_24h != null ? v.avg_coolant_24h.toFixed(0) + '°C' : '—'],
        ['Oil',      v.avg_oil_24h     != null ? v.avg_oil_24h.toFixed(0) + ' kPa'  : '—'],
        ['Hrs 7d',   v.engine_hours_7d != null ? v.engine_hours_7d.toFixed(1) + 'h'  : '—'],
        ['Alerts',   v.alerts_30d      != null ? String(v.alerts_30d.total ?? 0)     : '—'],
      ].forEach(([label, value]) => {
        const stat = el('div', { class: 'fleet-analytics-mini-stat' });
        stat.appendChild(el('span', { class: 'fleet-analytics-mini-val' }, String(value)));
        stat.appendChild(el('span', { class: 'fleet-analytics-mini-lbl' }, label));
        statsCell.appendChild(stat);
      });
      row.appendChild(statsCell);
      tableCard.appendChild(row);
    });
    container.appendChild(tableCard);
  }

  // ── Alert history (30d) breakdown ──
  const alertVessels = vessels.filter(v => v.alerts_30d && v.alerts_30d.total > 0);
  if (alertVessels.length > 0) {
    const alertCard = el('div', { class: 'card' });
    alertCard.appendChild(el('div', { class: 'card-title', style: 'font-size:0.95rem;margin-bottom:10px;' }, 'Alert History — Last 30 Days'));
    alertVessels.forEach(v => {
      const row = el('div', { class: 'fleet-analytics-row' });
      const nameCell = el('div', { class: 'fleet-analytics-vessel-name' });
      nameCell.appendChild(document.createTextNode(v.device_token.slice(-8)));
      if (v.role === 'owner') {
        const badge = el('span', { class: 'fleet-role-badge', style: 'font-size:0.7rem;padding:1px 6px;margin-left:4px;' }, 'owner');
        nameCell.appendChild(badge);
      }
      row.appendChild(nameCell);
      const statsCell = el('div', { class: 'fleet-analytics-vessel-stats' });
      const types = Object.entries(v.alerts_30d).filter(([k]) => k !== 'total');
      if (types.length === 0) {
        const s = el('div', { class: 'fleet-analytics-mini-stat' });
        s.appendChild(el('span', { class: 'fleet-analytics-mini-val' }, String(v.alerts_30d.total)));
        s.appendChild(el('span', { class: 'fleet-analytics-mini-lbl' }, 'total'));
        statsCell.appendChild(s);
      } else {
        types.forEach(([type, cnt]) => {
          const label = type.replace('engine_', '').replace(/_/g, ' ');
          const s = el('div', { class: 'fleet-analytics-mini-stat' });
          s.appendChild(el('span', { class: 'fleet-analytics-mini-val', style: 'color:var(--amber);' }, String(cnt)));
          s.appendChild(el('span', { class: 'fleet-analytics-mini-lbl' }, label));
          statsCell.appendChild(s);
        });
      }
      row.appendChild(statsCell);
      alertCard.appendChild(row);
    });
    container.appendChild(alertCard);
  }

  // ── CSV export ──
  const csvBtn = el('button', {
    class: 'btn btn-ghost',
    style: 'width:100%;margin-top:4px;',
    'aria-label': 'Download fleet analytics as CSV',
  }, 'Download CSV');
  csvBtn.addEventListener('click', () => _exportFleetCSV(analytics, fleetData));
  container.appendChild(csvBtn);
}

// Lazy chart init — called when analytics tab becomes visible
function _initAnalyticsChart() {
  const container = document.getElementById('fleet-analytics-panel');
  if (!container || !container._chartData) return;
  const canvas = document.getElementById('fleet-eng-chart');
  if (!canvas) return;
  if (canvas._chartInstance) { canvas._chartInstance.destroy(); }

  const { labels, hours7d } = container._chartData;
  if (!labels.length || typeof Chart === 'undefined') return;

  canvas._chartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Engine hours (7d)',
        data: hours7d,
        backgroundColor: 'rgba(0, 180, 216, 0.7)',
        borderColor:     'rgba(0, 180, 216, 1)',
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.parsed.y.toFixed(1)}h`,
          },
        },
      },
      scales: {
        x: {
          ticks: { color: '#94a3b8', font: { family: "'Nunito', sans-serif", size: 12 } },
          grid:  { color: 'rgba(255,255,255,0.05)' },
        },
        y: {
          ticks: {
            color: '#94a3b8',
            font: { family: "'JetBrains Mono', monospace", size: 11 },
            callback: v => v + 'h',
          },
          grid: { color: 'rgba(255,255,255,0.07)' },
          beginAtZero: true,
        },
      },
    },
  });
}

// CSV export — generates and triggers download client-side
function _exportFleetCSV(analytics, fleetData) {
  if (!analytics) return;
  const now     = new Date().toISOString().slice(0, 16).replace('T', ' ');
  const fname   = `fleet-${fleetData.fleet_name || 'export'}-${now}.csv`.replace(/[^a-z0-9.\-_]/gi, '_');
  const rows    = [
    ['Fleet', fleetData.fleet_name || '', 'Generated', now, 'Fleet ID', analytics.fleet_id || ''],
    [],
    ['Vessel (last 8)', 'Role', 'Engine Hrs Total', 'Engine Hrs 7d', 'Avg RPM 24h', 'Avg Coolant 24h (°C)', 'Avg Oil 24h (kPa)', 'Alerts 30d Total', 'Alerts: Overtemp', 'Alerts: Oil Pressure', 'Alerts: Roughness', 'Last Seen', 'Age (min)'],
  ];

  (analytics.vessels || []).forEach(v => {
    const al = v.alerts_30d || {};
    rows.push([
      v.device_token.slice(-8),
      v.role,
      v.engine_hours_total ?? '',
      v.engine_hours_7d    ?? '',
      v.avg_rpm_24h        != null ? Math.round(v.avg_rpm_24h) : '',
      v.avg_coolant_24h    ?? '',
      v.avg_oil_24h        ?? '',
      al.total             ?? 0,
      al.engine_overtemp   ?? 0,
      al.engine_oil_pressure ?? 0,
      al.engine_roughness  ?? 0,
      v.last_seen          ?? '',
      v.age_minutes        ?? '',
    ]);
  });

  const csv  = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = fname;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

screens.fleet = function renderFleet() {
  const container = getEl('screen');

  // T3 gate — nav button is hidden for T1/T2 but guard here too
  if (state.tier !== 'T3') {
    const header = el('div', { class: 'screen-header' });
    header.appendChild(el('span', { class: 'screen-title' }, 'Fleet Management'));
    container.appendChild(header);

    const card = el('div', { class: 'card', style: 'text-align:center;padding:32px 24px;' });

    // Lock icon
    card.appendChild(el('div', { style: 'font-size:2.8rem;margin-bottom:16px;line-height:1;', 'aria-hidden': 'true' }, '🔒'));

    card.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:12px;' }, 'Fleet Management'));
    card.appendChild(el('p', { style: 'font-size:1rem;color:var(--text-muted);line-height:1.7;margin-bottom:8px;' },
      'Monitor multiple vessels on a live map, track engine health across your fleet, and share your fleet code with other operators.'
    ));
    card.appendChild(el('p', { style: 'font-size:0.95rem;color:var(--text-muted);margin-bottom:24px;' },
      `Available on Tier 3. You are currently on ${state.tier || 'Tier 1'}.`
    ));

    const upgradeBtn = el('a', {
      href: API_BASE.replace('/wp-content/themes/twentytwenty-child/mobile', '/upgrade'),
      target: '_blank',
      rel: 'noopener noreferrer',
      class: 'btn btn-primary locked-upgrade-btn',
      style: 'display:inline-block;width:100%;box-sizing:border-box;',
    }, 'Upgrade to Tier 3 →');
    card.appendChild(upgradeBtn);

    container.appendChild(card);
    return;
  }

  // No fleet joined yet
  if (!state.fleetId) {
    renderFleetSetup();
    return;
  }

  // Fleet joined — load data
  if (!state.fleetData) {
    container.appendChild(spinner());
    Promise.allSettled([
      apiFleetMap(state.fleetId),
      apiFleetAnalytics(state.fleetId),
    ]).then(([mapResult, analyticsResult]) => {
      if (mapResult.status === 'rejected') {
        // Fleet not found (deleted, left, or network error) — reset
        state.fleetId = null;
        saveFleetSession();
        navigate('fleet');
        return;
      }
      state.fleetData      = mapResult.value;
      state.fleetAnalytics = analyticsResult.status === 'fulfilled' ? analyticsResult.value : null;
      navigate('fleet');
    }).catch(() => {
      container.innerHTML = '';
      container.appendChild(el('p', { style: 'padding:16px;color:var(--red);' },
        'Failed to load fleet data. Check connection and try again.'
      ));
    });
    return;
  }

  renderFleetMap(state.fleetData, state.fleetAnalytics);
};

// ── App shell toggle ──────────────────────────────────────────────────────────
function showLoginUI() {
  getEl('app-header').style.display  = 'none';
  getEl('bottom-nav').style.display  = 'none';
  state.currentScreen = 'login';
  getEl('screen').innerHTML = '';
  screens.login();
}

function showAppUI() {
  getEl('app-header').style.display  = '';
  getEl('bottom-nav').style.display  = '';
  updateFleetNavVisibility();
}

// ── Vessel load on app start ──────────────────────────────────────────────────
async function loadVessels() {
  try {
    const data = await apiListVessels();
    state.vessels = data.vessels || [];

    // Auto-select vessel: restore saved → prefer is_primary → fallback to first
    if (!state.vessel) {
      if (state.vessels.length === 1) {
        state.vessel = state.vessels[0];
        saveSession();
      } else if (state.vessels.length > 1) {
        // Restore previously saved vessel if it's still in the list
        const savedId = state.vessel?.pi_installation_id;
        if (savedId) {
          state.vessel = state.vessels.find(v => v.pi_installation_id === savedId) || null;
        }
        // MB5: fall back to the primary boat, then first boat
        if (!state.vessel) {
          state.vessel = state.vessels.find(v => v.is_primary) || state.vessels[0];
          saveSession();
        }
      }
    }

    // If returning from Stripe T1 FMP payment, route to FMP screen
    if (state._fmpPostPayment) {
      const fmpPiId = state._fmpPostPayment;
      const fmpVessel = state.vessels.find(v => v.pi_installation_id === fmpPiId);
      if (fmpVessel) { state.vessel = fmpVessel; saveSession(); }
      showAppUI();
      navigate('fixmypi');
      return;
    }

    // Show vessel selector if T3 + multiple vessels
    if (state.tier === 'T3' && state.vessels.length > 1 && !state.vessel) {
      showAppUI();
      navigate('select-vessel');
    } else {
      showAppUI();
      navigate('dashboard');
      await refreshDashboard();
    }
  } catch (err) {
    // Non-fatal — proceed to dashboard with no vessel list
    showAppUI();
    navigate('dashboard');
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
function init() {
  // Register service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  }

  // Wire bottom nav
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const screen = btn.dataset.screen;
      if (screen) navigate(screen);
    });
  });

  // Load persisted session
  loadSession();

  // Handle Stripe FMP return (T1 payment success) — must run after loadSession
  const _fmpParams = new URLSearchParams(window.location.search);
  if (_fmpParams.get('fmp') === 'paid' && _fmpParams.get('pi') && state.token) {
    state._fmpPostPayment = _fmpParams.get('pi');
    history.replaceState({}, '', window.location.pathname);
  }

  if (state.token) {
    showAppUI();
    // Restore dashboard if cached
    navigate('dashboard');
    loadVessels().then(() => refreshDashboard());
  } else {
    showLoginUI();
  }

  // Auto-refresh every 5 minutes when app is visible
  setInterval(() => {
    if (!document.hidden && state.token && state.currentScreen === 'dashboard') {
      refreshDashboard();
    }
  }, 5 * 60 * 1000);
}

document.addEventListener('DOMContentLoaded', init);
