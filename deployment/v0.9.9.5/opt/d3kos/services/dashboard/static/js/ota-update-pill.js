/* ota-update-pill.js — OTA update notification pill.
 * Self-injecting: one <script> tag on any d3kOS page activates it.
 * Pill sits in the header — no fixed bottom bar, no content coverage.
 * BUG-48: host resolved from window.location — never hardcoded.
 * AODA: all text ≥18px, buttons ≥48×48px.
 */
(function () {
  'use strict';

  if (document.getElementById('ota-pill')) return;

  var HOST           = window.location.hostname;
  var STATUS_URL     = 'http://' + HOST + ':3000/api/ota/status';
  var TRIGGER_URL    = 'http://' + HOST + ':3000/api/ota/trigger';
  var _state         = { available: false, version: null, notes: null };
  var _panelOpen     = false;
  var _installing    = false;
  var _pollInterval  = null;

  /* ── Inject CSS ── */
  var style = document.createElement('style');
  style.textContent =
    '#ota-pill{display:none;align-items:center;gap:6px;' +
    'padding:0 16px;height:40px;min-width:48px;border-radius:20px;cursor:pointer;' +
    'font-family:\'Chakra Petch\',monospace;font-size:20px;font-weight:700;' +
    'background:#111;border:2px solid #f59e0b;color:#ffffff;' +
    'white-space:nowrap;flex-shrink:0;transition:border-color .2s;' +
    'user-select:none;-webkit-user-select:none;}' +
    '#ota-pill.ota-show{display:inline-flex;}' +

    '#ota-panel{display:none;position:fixed;left:0;right:0;' +
    'background:#111;border-bottom:3px solid #f59e0b;z-index:1001;' +
    'font-family:\'Chakra Petch\',monospace;font-size:20px;color:#ffffff;' +
    'font-weight:700;padding:12px 16px;flex-direction:column;gap:10px;' +
    'box-shadow:0 6px 20px rgba(0,0,0,.7);}' +
    '#ota-panel.open{display:flex;}' +

    '#ota-msg{font-size:20px;font-weight:700;color:#ffffff;}' +
    '#ota-notes{font-size:18px;font-weight:400;color:#cccccc;margin:4px 0;}' +

    '.ota-btn{background:#222;border:2px solid #f59e0b;color:#ffffff;' +
    'font-size:18px;font-weight:700;min-width:120px;min-height:48px;padding:6px 20px;' +
    'border-radius:6px;cursor:pointer;white-space:nowrap;font-family:inherit;}' +
    '.ota-btn:active{background:#333;}' +
    '.ota-btn:disabled{background:#555;color:#999;cursor:not-allowed;border-color:#777;}' +

    '.ota-btn-group{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;}';

  document.head.appendChild(style);

  /* ── Build pill ── */
  var pill = document.createElement('div');
  pill.id = 'ota-pill';
  pill.setAttribute('role', 'button');
  pill.setAttribute('aria-label', 'OTA Update Available — tap to expand');
  pill.textContent = '🔄 Update Available';
  pill.addEventListener('click', togglePanel);

  /* ── Build expand panel ── */
  var panel = document.createElement('div');
  panel.id = 'ota-panel';

  var msg = document.createElement('div');
  msg.id = 'ota-msg';
  panel.appendChild(msg);

  var notes = document.createElement('div');
  notes.id = 'ota-notes';
  panel.appendChild(notes);

  var btnGroup = document.createElement('div');
  btnGroup.className = 'ota-btn-group';

  var dismissBtn = document.createElement('button');
  dismissBtn.className = 'ota-btn';
  dismissBtn.textContent = 'Dismiss';
  dismissBtn.addEventListener('click', function (e) { e.stopPropagation(); dismiss(); });
  btnGroup.appendChild(dismissBtn);

  var updateBtn = document.createElement('button');
  updateBtn.className = 'ota-btn';
  updateBtn.textContent = 'Update d3kOS';
  updateBtn.addEventListener('click', function (e) { e.stopPropagation(); triggerUpdate(updateBtn, dismissBtn); });
  btnGroup.appendChild(updateBtn);

  panel.appendChild(btnGroup);

  /* ── Inject into DOM ── */
  function injectDOM() {
    var sbRight  = document.querySelector('.sb-right');   /* index.html */
    var hdrRight = document.querySelector('.hdr-right');  /* marine-vision.html */
    var sb       = document.getElementById('sb') || document.getElementById('status-bar');
    var header   = document.querySelector('header');
    var dnInSb   = sb && sb.querySelector('.dn');         /* engine-monitor, anchor-watch */
    var clock    = document.getElementById('clock') || document.getElementById('clk');

    if (sbRight) {
      /* index.html: pill between ticker and Pi health */
      sbRight.parentNode.insertBefore(pill, sbRight);
    } else if (hdrRight) {
      /* marine-vision.html: pill before DAY/NGT buttons */
      hdrRight.insertBefore(pill, hdrRight.firstChild);
    } else if (dnInSb) {
      /* engine-monitor, anchor-watch: pill before the .dn day/night container */
      sb.insertBefore(pill, dnInSb);
    } else if (clock) {
      clock.parentNode.insertBefore(pill, clock);
    } else if (sb) {
      sb.appendChild(pill);
    } else {
      document.body.insertBefore(pill, document.body.firstChild);
    }

    /* Panel is fixed — append to body; set top to header/status-bar height */
    document.body.appendChild(panel);
    var topEl = sb || header;
    panel.style.top = ((topEl && topEl.offsetHeight) || 48) + 'px';

    startPolling();
  }

  /* ── Panel toggle ── */
  function togglePanel() {
    _panelOpen = !_panelOpen;
    panel.classList.toggle('open', _panelOpen);
  }

  document.addEventListener('click', function (e) {
    if (_panelOpen && !pill.contains(e.target) && !panel.contains(e.target)) {
      _panelOpen = false;
      panel.classList.remove('open');
    }
  });

  /* ── Check localStorage for dismissed version ── */
  function isDismissed() {
    var dismissed = localStorage.getItem('ota-dismissed');
    return dismissed === _state.version;
  }

  /* ── Dismiss: save version to localStorage, hide pill ── */
  function dismiss() {
    localStorage.setItem('ota-dismissed', _state.version);
    _panelOpen = false;
    panel.classList.remove('open');
    pill.classList.remove('ota-show');
  }

  /* ── Trigger update: POST to /api/ota/trigger, disable buttons, show installing ── */
  function triggerUpdate(updateBtn, dismissBtn) {
    _installing = true;
    updateBtn.disabled = true;
    dismissBtn.disabled = true;
    msg.textContent = 'Installing…';

    fetch(TRIGGER_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
      .then(function (res) {
        if (!res.ok) {
          msg.textContent = 'Update trigger failed. Please try again.';
          updateBtn.disabled = false;
          dismissBtn.disabled = false;
          _installing = false;
        }
        /* On success, leave "Installing…" message; polling will detect completion */
      })
      .catch(function (_) {
        msg.textContent = 'Network error. Please try again.';
        updateBtn.disabled = false;
        dismissBtn.disabled = false;
        _installing = false;
      });
  }

  /* ── Poll status every 30 seconds ── */
  function startPolling() {
    pollOnce();
    _pollInterval = setInterval(pollOnce, 30000);
  }

  function pollOnce() {
    fetch(STATUS_URL)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        _state = data;
        render();
      })
      .catch(function (_) {
        /* Silently continue on network error; show nothing in pill. */
      });
  }

  function render() {
    if (isDismissed()) {
      pill.classList.remove('ota-show');
      return;
    }

    if (_state.available) {
      pill.classList.add('ota-show');
      msg.textContent = 'd3kOS ' + (_state.version || 'update') + ' available';
      notes.textContent = _state.notes || '';
    } else {
      pill.classList.remove('ota-show');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectDOM);
  } else {
    injectDOM();
  }
})();
