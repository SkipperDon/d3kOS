/* safehelm-widget.js — ADV-1 footer collision advisory widget.
 * BUG-48: never hardcode localhost — resolve from window.location.
 * Connects to SafeHelm SSE via dashboard proxy /api/safehelm/sse.
 */
(function () {
  'use strict';

  /* BUG-48 compliant host resolution */
  var HOST = window.location.hostname;
  var DASH_API = 'http://' + HOST + ':3000';
  var SSE_URL  = DASH_API + '/api/safehelm/sse';
  var ACK_URL  = DASH_API + '/api/safehelm/ack';
  var DISMISS_URL = DASH_API + '/api/safehelm/dismiss';

  var widget    = document.getElementById('safehelm-widget');
  var alertsDiv = document.getElementById('sh-alerts');
  var statusEl  = document.getElementById('sh-status');
  var explainEl = document.getElementById('sh-explain');

  if (!widget) return;   /* widget not present on this page */

  var _state = {};        /* mmsi -> alert object */
  var _flashTimer = null;

  /* ── SSE connection ── */
  function connect() {
    var es = new EventSource(SSE_URL);
    es.onmessage = function (e) {
      try {
        var msg = JSON.parse(e.data);
        if (msg.type === 'state') handleState(msg);
      } catch (_) {}
    };
    es.onerror = function () {
      statusEl.textContent = '⚠ SafeHelm offline';
      statusEl.style.color = '#ff4444';
      setTimeout(connect, 5000);
      es.close();
    };
    es.onopen = function () {
      statusEl.textContent = '⛵ SafeHelm';
      statusEl.style.color = '#00CC00';
    };
  }

  /* ── State handler ── */
  function handleState(msg) {
    var alerts = msg.alerts || [];
    _state = {};
    alerts.forEach(function (a) { _state[a.mmsi] = a; });
    render();
  }

  /* ── Render ── */
  function render() {
    alertsDiv.innerHTML = '';

    var mmsis = Object.keys(_state);
    if (mmsis.length === 0) {
      var noAlert = document.createElement('span');
      noAlert.id = 'sh-no-alerts';
      noAlert.textContent = 'No qualifying traffic';
      alertsDiv.appendChild(noAlert);
      clearFlash();
      return;
    }

    var topTier = 'advisory';
    mmsis.forEach(function (mmsi) {
      var a = _state[mmsi];
      if (a.tier === 'critical') topTier = 'critical';
      else if (a.tier === 'warning' && topTier !== 'critical') topTier = 'warning';

      var div = document.createElement('div');
      div.className = 'sh-alert ' + a.tier;
      div.innerHTML = [
        '<span class="sh-alert-mmsi">' + mmsi + '</span>',
        '<span class="sh-alert-rule">' + ruleLabel(a.rule) + '</span>',
        '<span class="sh-alert-cpa">CPA ' + Math.round(a.cpa_m) + 'm</span>',
        '<button class="sh-btn" onclick="shAck(\'' + mmsi + '\')">ACK</button>',
        '<button class="sh-btn" onclick="shDismiss(\'' + mmsi + '\')">✕</button>',
      ].join('');
      div.addEventListener('click', function (e) {
        if (e.target.classList.contains('sh-btn')) return;
        showExplain(a);
      });
      alertsDiv.appendChild(div);
    });

    setFlash(topTier);
  }

  /* ── Flash border at 2 Hz for critical ── */
  function setFlash(tier) {
    widget.classList.remove('flash-critical', 'flash-warning');
    if (tier === 'critical') widget.classList.add('flash-critical');
    else if (tier === 'warning') widget.classList.add('flash-warning');
  }
  function clearFlash() {
    widget.classList.remove('flash-critical', 'flash-warning');
  }

  /* ── Explainability panel ── */
  function showExplain(a) {
    explainEl.textContent = ruleLabel(a.rule) + ' — MMSI ' + a.mmsi +
      ' | CPA ' + Math.round(a.cpa_m) + ' m | TCPA ' + Math.round(a.tcpa_s) + ' s' +
      ' | State: ' + a.state;
    explainEl.classList.add('visible');
  }
  document.addEventListener('click', function (e) {
    if (!explainEl.contains(e.target) && !alertsDiv.contains(e.target)) {
      explainEl.classList.remove('visible');
    }
  });

  /* ── Rule label map ── */
  function ruleLabel(rule) {
    var map = {
      'rule14_headon':                    'Head-On',
      'rule15_giveway':                   'Give-Way →',
      'rule15_standon':                   'Stand-On ←',
      'rule15_standon_unconfirmed':       'Stand-On? ←',
      'rule13_being_overtaken':           'Overtaken',
      'rule13_overtaking':                'Overtaking',
      'rule13_being_overtaken_unconfirmed': 'Overtaken?',
      'rule18_giveway':                   'R18 Give-Way',
    };
    return map[rule] || rule;
  }

  /* ── ACK / Dismiss ── */
  window.shAck = function (mmsi) {
    fetch(ACK_URL, {method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({mmsi: mmsi})});
  };
  window.shDismiss = function (mmsi) {
    fetch(DISMISS_URL, {method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({mmsi: mmsi})});
  };

  /* ADV-1: always-visible advisory line. Captain remains responsible at all times. */
  (function addAdvisoryLine() {
    var line = document.createElement('div');
    line.style.cssText = 'font-size:18px;color:#888;white-space:nowrap;flex-shrink:0;';
    line.textContent = 'Advisory only — captain remains responsible';
    widget.appendChild(line);
  })();

  connect();
})();
