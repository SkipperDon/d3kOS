/**
 * d3kOS PWA — Application Logic
 * Vanilla JS SPA. No frameworks, no build step.
 * Runs on GitHub Pages, talks to atmyboat.com/staging PHP endpoints.
 */

'use strict';

// ── Config ────────────────────────────────────────────────────────────────────
const API_BASE     = 'https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile';
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
  state.tier        = localStorage.getItem('amboat_tier')     || 'T1';
  const v = localStorage.getItem('amboat_vessel');
  if (v) { try { state.vessel = JSON.parse(v); } catch { state.vessel = null; } }
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

// Fetch full boatlog entry list for a Pi (newest-first).
async function apiBoatlogList(piId, limit = 30, offset = 0) {
  return apiFetch(`boatlog-list.php?pi=${encodeURIComponent(piId)}&limit=${limit}&offset=${offset}`);
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
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) + ' ' +
           d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
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
  if (vesselName !== null) nameEl.textContent = vesselName;
  if (online !== null) {
    dotEl.className = 'online-dot ' + (online ? 'online' : 'offline');
    dotEl.setAttribute('title', online ? 'Online' : 'Offline');
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
      state.tier        = data.tier;
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
  // Simple anchor/boat icon
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 64 64');
  svg.setAttribute('width', '64');
  svg.setAttribute('height', '64');
  svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = `
    <circle cx="32" cy="32" r="30" fill="#0f2040" stroke="#00b4d8" stroke-width="2"/>
    <path d="M32 14 L32 38 M24 32 L40 32" stroke="#00b4d8" stroke-width="2.5"
          stroke-linecap="round"/>
    <path d="M18 40 Q32 50 46 40" stroke="#00b4d8" stroke-width="2.5"
          stroke-linecap="round" fill="none"/>
  `;
  return svg;
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

    const rpmClass = eng.rpm > 4000 ? 'danger' : eng.rpm > 2500 ? 'warn' : '';
    const tempClass = eng.coolant_temp > 95 ? 'danger' : eng.coolant_temp > 85 ? 'warn' : '';
    const fuelClass = eng.fuel_level < 15 ? 'danger' : eng.fuel_level < 30 ? 'warn' : '';

    engCard.appendChild(el('div', { class: 'stat-grid' },
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
    ));
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
    const headerText = total > 0 ? `Alerts (${total})` : 'Alerts';
    container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:16px' }, headerText));

    if (alerts.length === 0) {
      container.appendChild(
        el('div', { class: 'empty-state' },
          el('p', {}, '✓ No alerts'),
        )
      );
      return;
    }

    const card = el('div', { class: 'card', style: 'padding: 0; overflow: hidden;' });
    alerts.forEach(a => {
      const typeColor = ALERT_COLORS[a.alert_type] || 'var(--text-muted)';
      const typeBadge = el('div', { class: 'alert-type-badge' }, a.alert_type || 'alert');
      typeBadge.style.color       = typeColor;
      typeBadge.style.borderColor = typeColor;
      card.appendChild(
        el('div', { class: 'alert-item alert-item-full' },
          el('div', { class: 'alert-item-top' },
            typeBadge,
            el('div', { class: 'alert-time' }, fmtTime(a.triggered_at)),
          ),
          el('div', { class: 'alert-msg' }, a.message || ''),
        )
      );
    });
    container.appendChild(card);

    if (total > alerts.length) {
      container.appendChild(
        el('p', { class: 'list-footnote' },
          `Showing ${alerts.length} of ${total} alerts.`)
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
    const curCard = el('div', { class: 'card' });
    curCard.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:8px;font-size:0.9rem;' }, 'Current'));
    curCard.appendChild(el('div', { class: 'stat-grid' },
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
    ));
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
    const fuels   = snaps.map(s => s.fuel_level_pct);
    const hours   = snaps.map(s => s.engine_hours_h);
    const tFirst  = fmtTime(snaps[0].snapshot_at);
    const tLast   = fmtTime(snaps[snaps.length - 1].snapshot_at);
    const timeRange = el('div', {
      style: 'font-size:0.82rem;color:var(--text-muted);margin-bottom:12px;',
    }, `${tFirst} → ${tLast}`);
    chartsWrap.appendChild(timeRange);

    [
      { label: 'RPM',          values: rpms,  color: '#00b4d8', unit: '' },
      { label: 'Coolant (°C)', values: temps, color: '#f59e0b', unit: '°C' },
      { label: 'Fuel (%)',     values: fuels, color: '#22c55e', unit: '%' },
    ].forEach(({ label, values, color, unit }) => {
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
        if (data.tier === 'T1') {
          // Open Stripe checkout in new tab, then show payment-wait phase
          window.open(data.checkout_url, '_blank', 'noopener');
          showPaymentWait();
        } else {
          // T2/T3 — command queued immediately
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
