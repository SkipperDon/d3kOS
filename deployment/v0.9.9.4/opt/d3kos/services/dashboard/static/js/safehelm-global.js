/* safehelm-global.js — SafeHelm collision advisory, status-bar pill.
 * Self-injecting: one <script> tag on any d3kOS page activates it.
 * Pill sits in the header — no fixed bottom bar, no content coverage.
 * BUG-48: host resolved from window.location — never hardcoded.
 * AODA: all text ≥18px, buttons ≥48×48px.
 */
(function () {
  'use strict';

  if (document.getElementById('sh-pill')) return;

  var HOST        = window.location.hostname;
  var SSE_URL     = 'http://' + HOST + ':3000/api/safehelm/sse';
  var ACK_URL     = 'http://' + HOST + ':3000/api/safehelm/ack';
  var DISMISS_URL = 'http://' + HOST + ':3000/api/safehelm/dismiss';
  var _state      = {};
  var _es         = null;
  var _disabled   = false;   /* session-only; resets on page reload */
  var _panelOpen  = false;

  /* ── Inject CSS ── */
  var style = document.createElement('style');
  style.textContent =
    '#sh-pill{display:inline-flex;align-items:center;gap:6px;' +
    'padding:0 14px;height:38px;min-width:48px;border-radius:19px;cursor:pointer;' +
    'font-family:\'Chakra Petch\',monospace;font-size:18px;font-weight:700;' +
    'background:#0d0d0d;border:2px solid #1e4d1e;color:#00CC00;' +
    'white-space:nowrap;flex-shrink:0;transition:border-color .2s,color .2s;' +
    'user-select:none;-webkit-user-select:none;}' +

    '#sh-pill.sh-warn{border-color:#ffaa00;color:#ffcc44;}' +
    '#sh-pill.sh-crit{border-color:#ff2222;color:#ff5555;' +
    'animation:sh-pill-flash 0.5s step-end infinite;}' +
    '@keyframes sh-pill-flash{0%,100%{color:#ff5555}50%{color:#661111}}' +
    '#sh-pill.sh-off{color:#444;border-color:#2a2a2a;}' +
    '#sh-pill.sh-err{color:#ff8800;border-color:#553300;}' +

    '#sh-panel{display:none;position:fixed;left:0;right:0;' +
    'background:#0d0d0d;border-bottom:2px solid #1a1a1a;z-index:1001;' +
    'font-family:\'Chakra Petch\',monospace;font-size:18px;color:#ccc;' +
    'padding:10px 16px;flex-direction:column;gap:8px;' +
    'box-shadow:0 4px 16px rgba(0,0,0,.5);}' +
    '#sh-panel.open{display:flex;}' +

    '.sh-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;' +
    'background:#111;border-radius:5px;padding:6px 12px;' +
    'border:1px solid #333;min-height:52px;}' +
    '.sh-row.critical{border-color:#ff2222;}' +
    '.sh-row.warning{border-color:#ffaa00;}' +
    '.sh-row.advisory{border-color:#2255aa;}' +
    '.sh-mmsi{font-size:18px;opacity:.75;}' +
    '.sh-rule{font-size:18px;font-weight:700;}' +
    '.sh-cpa{font-size:18px;opacity:.85;margin-right:auto;}' +
    '.sh-btn{background:transparent;border:1px solid #444;color:#aaa;' +
    'font-size:18px;min-width:52px;min-height:48px;padding:4px 12px;' +
    'border-radius:4px;cursor:pointer;white-space:nowrap;font-family:inherit;}' +
    '.sh-btn:active{background:#1a1a1a;}' +

    '#sh-adv{font-size:18px;color:#555;padding:2px 0;}' +

    '#sh-dis-btn{align-self:flex-start;background:transparent;' +
    'border:1px solid #2a2a2a;color:#555;font-family:inherit;' +
    'font-size:18px;min-height:48px;padding:4px 18px;border-radius:4px;cursor:pointer;}' +
    '#sh-dis-btn:active{color:#888;}' +

    '#sh-ena-btn{align-self:flex-start;background:transparent;' +
    'border:1px solid #1e4d1e;color:#00CC00;font-family:inherit;' +
    'font-size:18px;min-height:48px;padding:4px 18px;border-radius:4px;cursor:pointer;}' +
    '#sh-ena-btn:active{color:#fff;}';

  document.head.appendChild(style);

  /* ── Build pill ── */
  var pill = document.createElement('div');
  pill.id = 'sh-pill';
  pill.setAttribute('role', 'button');
  pill.setAttribute('aria-label', 'SafeHelm — tap to expand');
  pill.textContent = '⛵ SafeHelm';
  pill.addEventListener('click', togglePanel);

  /* ── Build expand panel ── */
  var panel = document.createElement('div');
  panel.id = 'sh-panel';

  var rows = document.createElement('div');
  rows.id = 'sh-rows';
  panel.appendChild(rows);

  var adv = document.createElement('div');
  adv.id = 'sh-adv';
  adv.textContent = 'Advisory only — captain remains responsible';
  panel.appendChild(adv);

  var disBtn = document.createElement('button');
  disBtn.id = 'sh-dis-btn';
  disBtn.textContent = 'Disable SafeHelm (this session)';
  disBtn.addEventListener('click', function (e) { e.stopPropagation(); disable(); });
  panel.appendChild(disBtn);

  var enaBtn = document.createElement('button');
  enaBtn.id = 'sh-ena-btn';
  enaBtn.textContent = 'Re-enable SafeHelm';
  enaBtn.style.display = 'none';
  enaBtn.addEventListener('click', function (e) { e.stopPropagation(); enable(); });
  panel.appendChild(enaBtn);

  /* ── Inject into DOM ── */
  function injectDOM() {
    /* Pill: on index.html insert before .sb-right; on other pages before #clock */
    var sbRight = document.querySelector('.sb-right');
    var clock   = document.getElementById('clock') || document.getElementById('clk');
    var sb      = document.getElementById('sb') || document.getElementById('status-bar');

    if (sbRight) {
      sbRight.parentNode.insertBefore(pill, sbRight);
    } else if (clock) {
      clock.parentNode.insertBefore(pill, clock);
    } else if (sb) {
      sb.appendChild(pill);
    } else {
      document.body.insertBefore(pill, document.body.firstChild);
    }

    /* Panel is fixed — append to body; set top to status bar height */
    document.body.appendChild(panel);
    panel.style.top = ((sb && sb.offsetHeight) || 48) + 'px';

    connect();
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

  /* ── Disable / Enable (session-only) ── */
  function disable() {
    _disabled = true;
    if (_es) { _es.close(); _es = null; }
    _panelOpen = false;
    panel.classList.remove('open');
    pill.textContent = '⛵';
    pill.setAttribute('aria-label', 'SafeHelm disabled — tap to re-enable');
    pill.classList.remove('sh-warn', 'sh-crit', 'sh-err');
    pill.classList.add('sh-off');
    rows.innerHTML = '<div style="font-size:18px;color:#555;">SafeHelm is disabled for this session.</div>';
    disBtn.style.display = 'none';
    enaBtn.style.display = '';
  }

  function enable() {
    _disabled = false;
    _panelOpen = false;
    panel.classList.remove('open');
    pill.classList.remove('sh-off');
    pill.setAttribute('aria-label', 'SafeHelm — tap to expand');
    disBtn.style.display = '';
    enaBtn.style.display = 'none';
    connect();
  }

  /* ── SSE ── */
  function connect() {
    if (_disabled) return;
    if (_es) { _es.close(); _es = null; }
    _es = new EventSource(SSE_URL);
    _es.onopen = function () {
      pill.classList.remove('sh-err', 'sh-off');
    };
    _es.onmessage = function (e) {
      try {
        var msg = JSON.parse(e.data);
        if (msg.type === 'state') handleState(msg);
      } catch (_) {}
    };
    _es.onerror = function () {
      pill.textContent = '⚠ SafeHelm';
      pill.classList.remove('sh-warn', 'sh-crit');
      pill.classList.add('sh-err');
      _es.close(); _es = null;
      if (!_disabled) setTimeout(connect, 5000);
    };
  }

  function handleState(msg) {
    _state = {};
    (msg.alerts || []).forEach(function (a) { _state[a.mmsi] = a; });
    render();
  }

  function render() {
    if (_disabled) return;
    var mmsis = Object.keys(_state);
    pill.classList.remove('sh-warn', 'sh-crit');

    if (mmsis.length === 0) {
      pill.textContent = '⛵ SafeHelm';
      rows.innerHTML = '<div style="font-size:18px;color:#00CC00;opacity:.7;">No qualifying traffic</div>';
      return;
    }

    var topTier = 'advisory';
    mmsis.forEach(function (mmsi) {
      var t = _state[mmsi].tier;
      if (t === 'critical') topTier = 'critical';
      else if (t === 'warning' && topTier !== 'critical') topTier = 'warning';
    });

    pill.textContent = '⛵ ' + mmsis.length + (topTier === 'critical' ? ' ⚠' : topTier === 'warning' ? ' !' : '');
    if (topTier === 'critical') pill.classList.add('sh-crit');
    else if (topTier === 'warning') pill.classList.add('sh-warn');

    rows.innerHTML = '';
    mmsis.forEach(function (mmsi) {
      var a   = _state[mmsi];
      var row = document.createElement('div');
      row.className = 'sh-row ' + a.tier;
      row.innerHTML =
        '<span class="sh-mmsi">' + mmsi + '</span>' +
        '<span class="sh-rule">' + ruleLabel(a.rule) + '</span>' +
        '<span class="sh-cpa">CPA ' + Math.round(a.cpa_m) + 'm</span>' +
        '<button class="sh-btn" onclick="shAck(\'' + mmsi + '\')">ACK</button>' +
        '<button class="sh-btn" onclick="shDismiss(\'' + mmsi + '\')">✕</button>';
      rows.appendChild(row);
    });
  }

  function ruleLabel(r) {
    return ({
      rule14_headon:                      'Head-On',
      rule15_giveway:                     'Give-Way →',
      rule15_standon:                     'Stand-On ←',
      rule15_standon_unconfirmed:         'Stand-On? ←',
      rule13_being_overtaken:             'Overtaken',
      rule13_overtaking:                  'Overtaking',
      rule13_being_overtaken_unconfirmed: 'Overtaken?',
      rule18_giveway:                     'R18 Give-Way',
    })[r] || r;
  }

  window.shAck = function (mmsi) {
    fetch(ACK_URL, { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mmsi: mmsi }) });
  };
  window.shDismiss = function (mmsi) {
    fetch(DISMISS_URL, { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mmsi: mmsi }) });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectDOM);
  } else {
    injectDOM();
  }
})();
