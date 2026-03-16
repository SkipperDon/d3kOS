/* boatlog-engine.js — d3kOS v0.9.2.3 Session D
   Engine start/stop detection via Signal K WebSocket.
   Captures automatic entries into the boat log on:
     - Engine start (RPM transitions 0 → running)
     - Every 30 minutes while engine is running
     - Engine stop (RPM transitions running → 0)
     - Any alert threshold crossing (oil low, coolant high, battery out of range)
   Saves each entry to localStorage (key: d3kos-boatlog-entries)
   and POSTs to boatlog-export-api.py at :8095.
*/

(function () {
  'use strict';

  var SK_URL           = 'ws://localhost:8099/signalk/v1/stream';
  var API_URL          = 'http://localhost:8095';
  var LS_KEY           = 'd3kos-boatlog-entries';
  var RPM_THRESHOLD_HZ = 3;                    /* 3 Hz = 180 RPM — engine considered running */
  var SNAPSHOT_MS      = 30 * 60 * 1000;       /* 30-minute running snapshot interval */
  var ARCHIVE_DAYS     = 90;                    /* entries older than 90 days are pruned */

  /* Alert thresholds — flag crossing only once until condition recovers */
  var THRESHOLDS = {
    oil_psi:   { low: 10,   high: null  },
    coolant_c: { low: null, high: 100   },
    battery_v: { low: 11.8, high: 15.0  }
  };

  var _state = {
    rpm_hz:        0,
    oil_psi:       null,
    coolant_c:     null,
    battery_v:     null,
    fuel_pct:      null,
    engineRunning: false,
    snapshotTimer: null,
    ws:            null,
    retryTimer:    null,
    alertFired:    {}   /* tracks which alert keys are currently active */
  };

  /* ── localStorage helpers ── */

  function _load() {
    try { return JSON.parse(localStorage.getItem(LS_KEY)) || []; }
    catch (e) { return []; }
  }

  function _save(entries) {
    /* Prune entries older than ARCHIVE_DAYS */
    var cutoff = Date.now() - (ARCHIVE_DAYS * 86400000);
    var pruned = entries.filter(function (e) {
      return new Date(e.timestamp).getTime() > cutoff;
    });
    localStorage.setItem(LS_KEY, JSON.stringify(pruned));
  }

  /* ── Build one engine log entry ── */
  function _buildEntry(event) {
    return {
      timestamp: new Date().toISOString(),
      type:      'engine',
      event:     event,                                /* start | running | stop | alert_* */
      rpm:       Math.round((_state.rpm_hz || 0) * 60),
      oil_psi:   _state.oil_psi   !== null ? Math.round(_state.oil_psi)                  : null,
      coolant_c: _state.coolant_c !== null ? Math.round(_state.coolant_c * 10) / 10      : null,
      battery_v: _state.battery_v !== null ? Math.round(_state.battery_v * 10) / 10      : null,
      fuel_pct:  _state.fuel_pct  !== null ? Math.round(_state.fuel_pct * 100)           : null
    };
  }

  /* ── Record and persist entry ── */
  function _record(event) {
    var entry   = _buildEntry(event);
    var entries = _load();
    entries.unshift(entry);
    _save(entries);

    /* Re-render list if boat-log page is open */
    if (typeof window.renderEntries === 'function') {
      window.renderEntries();
    }

    /* POST to API — fire and forget; localStorage copy is the source of truth */
    fetch(API_URL + '/api/boatlog/engine-entry', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(entry)
    }).catch(function () { /* API unavailable — localStorage copy already saved */ });
  }

  /* ── Engine state machine ── */
  function _checkEngineState(rpmHz) {
    var isRunning = rpmHz > RPM_THRESHOLD_HZ;

    if (!_state.engineRunning && isRunning) {
      _state.engineRunning = true;
      _record('start');
      /* Begin 30-min snapshot timer */
      _state.snapshotTimer = setInterval(function () {
        _record('running');
      }, SNAPSHOT_MS);
    }

    if (_state.engineRunning && !isRunning) {
      _state.engineRunning = false;
      clearInterval(_state.snapshotTimer);
      _state.snapshotTimer = null;
      _record('stop');
      /* Clear all alert states on stop */
      _state.alertFired = {};
    }
  }

  /* ── Alert threshold checker ── */
  function _checkThresholds() {
    if (!_state.engineRunning) return;

    var active = {};

    if (_state.oil_psi !== null && _state.oil_psi < THRESHOLDS.oil_psi.low) {
      active['oil_low'] = true;
    }
    if (_state.coolant_c !== null && _state.coolant_c > THRESHOLDS.coolant_c.high) {
      active['coolant_high'] = true;
    }
    if (_state.battery_v !== null) {
      if (_state.battery_v < THRESHOLDS.battery_v.low)  active['battery_low']  = true;
      if (_state.battery_v > THRESHOLDS.battery_v.high) active['battery_high'] = true;
    }

    /* Fire entry only on new alert transitions (not repeat) */
    Object.keys(active).forEach(function (key) {
      if (!_state.alertFired[key]) {
        _state.alertFired[key] = true;
        _record('alert_' + key);
      }
    });

    /* Clear recovered conditions so they can re-fire if they recur */
    Object.keys(_state.alertFired).forEach(function (key) {
      if (!active[key]) {
        _state.alertFired[key] = false;
      }
    });
  }

  /* ── Signal K path handlers ── */
  var _SK = {
    'propulsion.0.revolutions': function (v) {
      _state.rpm_hz = v;
      _checkEngineState(v);
    },
    'propulsion.0.oilPressure': function (v) {
      _state.oil_psi = v * 0.000145038;   /* Pa → PSI */
      _checkThresholds();
    },
    'propulsion.0.coolantTemperature': function (v) {
      _state.coolant_c = v - 273.15;      /* K → °C */
      _checkThresholds();
    },
    'electrical.batteries.0.voltage': function (v) {
      _state.battery_v = v;
      _checkThresholds();
    },
    'tanks.fuel.0.currentLevel': function (v) {
      _state.fuel_pct = v;                /* 0–1 fraction */
    }
  };

  /* ── WebSocket connection ── */
  function _connect() {
    try {
      _state.ws = new WebSocket(SK_URL + '?subscribe=none');
    } catch (e) {
      _scheduleRetry();
      return;
    }

    _state.ws.onopen = function () {
      _state.ws.send(JSON.stringify({
        context: 'vessels.self',
        subscribe: [
          { path: 'propulsion.0.revolutions',        period: 1000  },
          { path: 'propulsion.0.oilPressure',        period: 2000  },
          { path: 'propulsion.0.coolantTemperature', period: 2000  },
          { path: 'electrical.batteries.0.voltage',  period: 5000  },
          { path: 'tanks.fuel.0.currentLevel',       period: 10000 }
        ]
      }));
    };

    _state.ws.onmessage = function (evt) {
      var msg;
      try { msg = JSON.parse(evt.data); } catch (e) { return; }
      if (!msg.updates) return;
      msg.updates.forEach(function (upd) {
        if (!upd.values) return;
        upd.values.forEach(function (item) {
          if (_SK[item.path] && item.value !== null) {
            _SK[item.path](item.value);
          }
        });
      });
    };

    _state.ws.onclose = function () { _scheduleRetry(); };
    _state.ws.onerror = function () { /* onclose fires after onerror */ };
  }

  function _scheduleRetry() {
    if (_state.retryTimer) return;
    _state.retryTimer = setTimeout(function () {
      _state.retryTimer = null;
      _connect();
    }, 5000);
  }

  /* ── Start ── */
  _connect();

})();
