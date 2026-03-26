/**
 * d3kOS PWA — Application Logic
 * Vanilla JS SPA. No frameworks, no build step.
 * Runs on GitHub Pages, talks to atmyboat.com/staging PHP endpoints.
 */

'use strict';

// ── Config ────────────────────────────────────────────────────────────────────
const API_BASE = 'https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile';

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

async function apiSendCommand(piId, commandType, payload = {}) {
  return apiFetch('command-queue.php', {
    method: 'POST',
    body: JSON.stringify({ pi_installation_id: piId, command: commandType, payload }),
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
    container.appendChild(
      el('div', { class: 'empty-state' },
        el('p', {}, 'No vessels paired to your account.'),
        el('p', {}, 'Visit atmyboat.com to pair your d3kOS device.'),
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
screens.alerts = function renderAlerts() {
  const container = getEl('screen');
  container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:16px' }, 'Active Alerts'));

  const data = state.dashboard;
  if (!data) {
    container.appendChild(spinner());
    return;
  }

  const alerts = (data.alerts && data.alerts.latest) || [];

  if (alerts.length === 0) {
    container.appendChild(
      el('div', { class: 'empty-state' },
        el('p', {}, '✓ No active alerts'),
      )
    );
    return;
  }

  const card = el('div', { class: 'card', style: 'padding: 0; overflow: hidden;' });
  alerts.forEach(a => {
    card.appendChild(
      el('div', { class: 'alert-item' },
        el('div', { class: 'alert-type' }, a.alert_type || 'alert'),
        el('div', { class: 'alert-msg'  }, a.message || ''),
        el('div', { class: 'alert-time' }, fmtTime(a.triggered_at)),
      )
    );
  });
  container.appendChild(card);
};

// ── Boatlog Screen ────────────────────────────────────────────────────────────
screens.boatlog = function renderBoatlog() {
  const container = getEl('screen');
  container.appendChild(el('div', { class: 'card-title', style: 'margin-bottom:16px' }, 'Boat Log'));

  const data = state.dashboard;
  if (!data) {
    container.appendChild(spinner());
    return;
  }

  const entry = data.boatlog && data.boatlog.latest_entry;
  if (!entry) {
    container.appendChild(
      el('div', { class: 'empty-state' },
        el('p', {}, 'No boatlog entries yet.'),
      )
    );
    return;
  }

  const card = el('div', { class: 'card', style: 'padding: 0; overflow: hidden;' });
  card.appendChild(
    el('div', { class: 'log-item' },
      el('div', { class: 'log-type' }, entry.entry_type || 'log'),
      el('div', { class: 'log-content' }, entry.content || ''),
      el('div', { class: 'log-time' }, fmtTime(entry.entry_timestamp)),
    )
  );
  container.appendChild(card);

  container.appendChild(
    el('p', { style: 'font-size: 0.82rem; color: var(--text-muted); margin-top: 8px;' },
      'Full boatlog history is available at atmyboat.com/dashboard'
    )
  );
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
  const otaStatus = el('div', { style: 'font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;' },
    'Trigger a d3kOS software upgrade on your vessel.'
  );
  const otaBtn = el('button', { class: 'btn btn-ghost' }, 'Check for Update');
  const otaResult = el('div', { style: 'margin-top: 8px; font-size: 0.9rem; display: none;' });

  otaBtn.addEventListener('click', async () => {
    if (!state.vessel) { otaResult.textContent = 'No vessel selected.'; otaResult.style.display = 'block'; return; }
    otaBtn.disabled = true;
    otaBtn.textContent = 'Sending…';
    try {
      await apiSendCommand(state.vessel.pi_installation_id, 'ota_upgrade', {});
      otaResult.textContent = '✓ Upgrade command queued. Your Pi will update when it next syncs.';
      otaResult.style.color = 'var(--green)';
    } catch (err) {
      otaResult.textContent = '✗ ' + (err.message || 'Command failed.');
      otaResult.style.color = 'var(--red)';
    } finally {
      otaResult.style.display = 'block';
      otaBtn.disabled = false;
      otaBtn.textContent = 'Check for Update';
    }
  });

  otaCard.appendChild(otaStatus);
  otaCard.appendChild(otaBtn);
  otaCard.appendChild(otaResult);
  container.appendChild(otaCard);

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

    // Auto-select: if single vessel or if a vessel was previously selected, use that
    if (!state.vessel) {
      if (state.vessels.length === 1) {
        state.vessel = state.vessels[0];
        saveSession();
      } else if (state.vessels.length > 1) {
        // Restore previously selected if still in list
        const savedId = state.vessel?.pi_installation_id;
        if (savedId) {
          state.vessel = state.vessels.find(v => v.pi_installation_id === savedId) || state.vessels[0];
        }
      }
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
