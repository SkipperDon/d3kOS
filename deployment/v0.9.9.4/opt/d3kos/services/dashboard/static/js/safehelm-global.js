/* safehelm-global.js — persistent SafeHelm collision advisory widget.
 * Self-injecting: one <script> tag on any d3kOS page activates it.
 * Always-on: auto-connects to SSE on load, no toggle required.
 * BUG-48: host resolved from window.location — never hardcoded.
 * AODA: all text ≥18px, ACK/Dismiss buttons ≥48×48px.
 */
(function () {
  'use strict';

  /* Skip if already injected on this page */
  if (document.getElementById('safehelm-widget')) return;

  /* ── Inject CSS ── */
  var style = document.createElement('style');
  style.textContent =
    '#safehelm-widget{position:fixed;bottom:0;left:0;right:0;z-index:900;' +
    'background:#0a0a0a;border-top:2px solid #1a1a1a;' +
    'font-family:\'Chakra Petch\',monospace;font-size:18px;color:#ccc;' +
    'display:flex;align-items:center;min-height:52px;padding:4px 12px;' +
    'gap:12px;transition:border-color 0.15s;}' +
    '#safehelm-widget.flash-critical{animation:sh-flash 0.5s step-end infinite;}' +
    '@keyframes sh-flash{0%,100%{border-top-color:#ff2222}50%{border-top-color:#1a1a1a}}' +
    '#safehelm-widget.flash-warning{border-top-color:#ffaa00;}' +
    '#sh-status{flex:0 0 auto;font-size:18px;color:#00CC00;white-space:nowrap;}' +
    '#sh-alerts{flex:1;display:flex;gap:8px;flex-wrap:wrap;align-items:center;overflow:hidden;}' +
    '.sh-alert{display:flex;align-items:center;gap:6px;background:#111;border-radius:4px;' +
    'padding:4px 8px;font-size:18px;border:1px solid #333;min-height:48px;}' +
    '.sh-alert.critical{border-color:#ff2222;color:#ff6666;}' +
    '.sh-alert.warning{border-color:#ffaa00;color:#ffcc44;}' +
    '.sh-alert.advisory{border-color:#2255aa;color:#88aaff;}' +
    '.sh-alert-mmsi{font-size:18px;opacity:0.75;}' +
    '.sh-alert-rule{font-size:18px;font-weight:bold;}' +
    '.sh-alert-cpa{font-size:18px;opacity:0.85;}' +
    '.sh-btn{background:transparent;border:1px solid #444;color:#aaa;font-size:18px;' +
    'min-width:48px;min-height:48px;padding:4px 10px;border-radius:4px;cursor:pointer;white-space:nowrap;}' +
    '.sh-btn:active{background:#1a1a1a;}' +
    '.sh-explain{display:none;position:fixed;bottom:56px;left:8px;right:8px;' +
    'background:#0d0d0d;border:1px solid #333;border-radius:6px;padding:12px 16px;' +
    'font-size:18px;color:#ccc;z-index:901;max-height:40vh;overflow-y:auto;}' +
    '.sh-explain.visible{display:block;}' +
    '#sh-no-alerts{font-size:18px;color:#00CC00;opacity:0.7;}' +
    '#sh-dismiss{background:transparent;border:none;color:#555;font-size:22px;' +
    'min-width:48px;min-height:48px;cursor:pointer;flex-shrink:0;padding:0 8px;}' +
    '#sh-dismiss:active{color:#aaa;}';
  document.head.appendChild(style);

  var _dismissed = false;   /* user hid the bar; re-shows on new alert */

  /* ── Inject widget HTML ── */
  var widget = document.createElement('div');
  widget.id = 'safehelm-widget';
  widget.setAttribute('aria-label', 'SafeHelm Collision Advisory');
  widget.innerHTML =
    '<span id="sh-status">⛵ SafeHelm</span>' +
    '<div id="sh-alerts"><span id="sh-no-alerts">No qualifying traffic</span></div>';

  /* ADV-1 — always visible per W1 requirement */
  var adv = document.createElement('div');
  adv.id = 'sh-adv-line';
  adv.style.cssText = 'font-size:18px;color:#888;white-space:nowrap;flex-shrink:0;';
  adv.textContent = 'Advisory only — captain remains responsible';
  widget.appendChild(adv);

  /* Dismiss button — hides bar; auto-restores on new alert */
  var dismissBtn = document.createElement('button');
  dismissBtn.id = 'sh-dismiss';
  dismissBtn.setAttribute('aria-label', 'Hide SafeHelm bar');
  dismissBtn.title = 'Hide (reappears on new alerts)';
  dismissBtn.textContent = '−';   /* − */
  dismissBtn.addEventListener('click', function () {
    _dismissed = true;
    widget.style.display = 'none';
  });
  widget.appendChild(dismissBtn);

  var explain = document.createElement('div');
  explain.className = 'sh-explain';
  explain.id = 'sh-explain';

  document.body.appendChild(widget);
  document.body.appendChild(explain);

  /* ── Endpoints — BUG-48 compliant ── */
  var HOST        = window.location.hostname;
  var SSE_URL     = 'http://' + HOST + ':3000/api/safehelm/sse';
  var ACK_URL     = 'http://' + HOST + ':3000/api/safehelm/ack';
  var DISMISS_URL = 'http://' + HOST + ':3000/api/safehelm/dismiss';
  var _state      = {};
  var _es         = null;

  function getEl(id) { return document.getElementById(id); }

  /* ── SSE connection with auto-reconnect ── */
  function connect() {
    if (_es) { _es.close(); _es = null; }
    var statusEl = getEl('sh-status');
    _es = new EventSource(SSE_URL);
    _es.onopen = function () {
      if (statusEl) { statusEl.textContent = '⛵ SafeHelm'; statusEl.style.color = '#00CC00'; }
    };
    _es.onmessage = function (e) {
      try {
        var msg = JSON.parse(e.data);
        if (msg.type === 'state') handleState(msg);
      } catch (_) {}
    };
    _es.onerror = function () {
      if (statusEl) { statusEl.textContent = '⚠ SafeHelm offline'; statusEl.style.color = '#ff4444'; }
      _es.close(); _es = null;
      setTimeout(connect, 5000);
    };
  }

  function handleState(msg) {
    _state = {};
    (msg.alerts || []).forEach(function (a) { _state[a.mmsi] = a; });
    render();
  }

  function render() {
    var alertsDiv = getEl('sh-alerts');
    var w         = getEl('safehelm-widget');
    if (!alertsDiv || !w) return;
    alertsDiv.innerHTML = '';
    var mmsis = Object.keys(_state);
    if (mmsis.length === 0) {
      var noAlert = document.createElement('span');
      noAlert.id = 'sh-no-alerts';
      noAlert.textContent = 'No qualifying traffic';
      alertsDiv.appendChild(noAlert);
      w.classList.remove('flash-critical', 'flash-warning');
      return;   /* leave bar hidden if user dismissed it with no active alerts */
    }
    /* New alert — restore bar even if user dismissed it */
    if (_dismissed) { _dismissed = false; w.style.display = 'flex'; }
    var topTier = 'advisory';
    mmsis.forEach(function (mmsi) {
      var a = _state[mmsi];
      if (a.tier === 'critical') topTier = 'critical';
      else if (a.tier === 'warning' && topTier !== 'critical') topTier = 'warning';
      var div = document.createElement('div');
      div.className = 'sh-alert ' + a.tier;
      div.innerHTML =
        '<span class="sh-alert-mmsi">' + mmsi + '</span>' +
        '<span class="sh-alert-rule">' + ruleLabel(a.rule) + '</span>' +
        '<span class="sh-alert-cpa">CPA ' + Math.round(a.cpa_m) + 'm</span>' +
        '<button class="sh-btn" onclick="shAck(\'' + mmsi + '\')">ACK</button>' +
        '<button class="sh-btn" onclick="shDismiss(\'' + mmsi + '\')">✕</button>';
      div.addEventListener('click', function (e) {
        if (e.target.classList.contains('sh-btn')) return;
        showExplain(a);
      });
      alertsDiv.appendChild(div);
    });
    w.classList.remove('flash-critical', 'flash-warning');
    if (topTier === 'critical') w.classList.add('flash-critical');
    else if (topTier === 'warning') w.classList.add('flash-warning');
  }

  function showExplain(a) {
    var el = getEl('sh-explain');
    if (!el) return;
    el.textContent = ruleLabel(a.rule) + ' — MMSI ' + a.mmsi +
      ' | CPA ' + Math.round(a.cpa_m) + ' m | TCPA ' + Math.round(a.tcpa_s) + ' s' +
      ' | State: ' + a.state;
    el.classList.add('visible');
  }

  document.addEventListener('click', function (e) {
    var el = getEl('sh-explain');
    var ad = getEl('sh-alerts');
    if (el && ad && !el.contains(e.target) && !ad.contains(e.target)) {
      el.classList.remove('visible');
    }
  });

  function ruleLabel(rule) {
    return ({
      rule14_headon:                     'Head-On',
      rule15_giveway:                    'Give-Way →',
      rule15_standon:                    'Stand-On ←',
      rule15_standon_unconfirmed:        'Stand-On? ←',
      rule13_being_overtaken:            'Overtaken',
      rule13_overtaking:                 'Overtaking',
      rule13_being_overtaken_unconfirmed:'Overtaken?',
      rule18_giveway:                    'R18 Give-Way',
    })[rule] || rule;
  }

  window.shAck = function (mmsi) {
    fetch(ACK_URL, { method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({mmsi: mmsi}) });
  };
  window.shDismiss = function (mmsi) {
    fetch(DISMISS_URL, { method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({mmsi: mmsi}) });
  };

  /* ── Position bar above any existing fixed bottom element ── */
  function positionBar() {
    var bot      = document.getElementById('bot');       /* index.html nav bar */
    var inputBar = document.getElementById('input-bar'); /* ai-navigation.html */
    var offset = 0;
    if (bot)      offset = bot.offsetHeight;
    else if (inputBar) offset = inputBar.offsetHeight;
    widget.style.bottom = offset ? offset + 'px' : '0';
  }

  /* ── Auto-connect and position ── */
  function init() {
    positionBar();
    connect();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
