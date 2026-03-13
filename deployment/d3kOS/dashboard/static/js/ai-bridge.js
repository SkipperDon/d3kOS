/**
 * d3kOS AI Bridge — dashboard integration
 * Connects to SSE stream at localhost:3002/stream
 * Handles route widget, arrival briefing, anchor watch alerts
 */

const AI_BRIDGE = 'http://localhost:3002';

let _bridgeSource = null;

function connectAIBridge() {
  if (_bridgeSource) return;

  try {
    _bridgeSource = new EventSource(AI_BRIDGE + '/stream');

    _bridgeSource.addEventListener('heartbeat', () => {
      // Connection alive — update AI Bridge indicator if visible
      _setIndicator('ind-ai-bridge', true);
    });

    _bridgeSource.addEventListener('route_update', (e) => {
      const d = JSON.parse(e.data);
      _handleRouteUpdate(d);
    });

    _bridgeSource.addEventListener('arrival_briefing', (e) => {
      const d = JSON.parse(e.data);
      _handleArrivalBriefing(d);
    });

    _bridgeSource.addEventListener('anchor_alert', (e) => {
      const d = JSON.parse(e.data);
      _handleAnchorAlert(d);
    });

    _bridgeSource.addEventListener('anchor_advice', (e) => {
      const d = JSON.parse(e.data);
      const el = document.getElementById('anchor-advice');
      if (el) {
        el.textContent = d.advice || '';
        el.style.display = 'block';
      }
    });

    _bridgeSource.addEventListener('voyage_summary', (e) => {
      const d = JSON.parse(e.data);
      _handleVoyageSummary(d);
    });

    _bridgeSource.onerror = () => {
      _setIndicator('ind-ai-bridge', false);
      // Reconnect after 15 seconds — do not hammer the server
      _bridgeSource.close();
      _bridgeSource = null;
      setTimeout(connectAIBridge, 15000);
    };

  } catch (err) {
    _setIndicator('ind-ai-bridge', false);
    setTimeout(connectAIBridge, 15000);
  }
}

// ── Route Widget ─────────────────────────────────────────────────────────────

function _handleRouteUpdate(d) {
  const stateEl = document.getElementById('route-state');
  const textEl  = document.getElementById('route-text');
  const metaEl  = document.getElementById('route-meta');
  if (!stateEl) return;

  switch (d.state) {
    case 'ACTIVE':
      stateEl.textContent = d.offline ? 'OFFLINE AI' : '';
      stateEl.className   = d.offline ? 'ai-state offline' : 'ai-state hidden';
      textEl.textContent  = d.text || '';
      metaEl.textContent  = d.route_name
        ? `${d.route_name}  •  ${d.sog_kts || 0}kts  •  ${d.cog_deg || 0}°`
        : '';
      break;

    case 'NO_ROUTE':
      stateEl.textContent = 'No active route';
      stateEl.className   = 'ai-state dim';
      textEl.textContent  = '';
      metaEl.textContent  = '';
      break;

    case 'UPDATING':
      stateEl.textContent = 'Analyzing...';
      stateEl.className   = 'ai-state dim';
      break;

    case 'NO_GPS':
      stateEl.textContent = 'Waiting for GPS';
      stateEl.className   = 'ai-state dim';
      textEl.textContent  = '';
      break;

    case 'AI_UNAVAILABLE':
      stateEl.textContent = 'AI unavailable';
      stateEl.className   = 'ai-state warn';
      textEl.textContent  = d.text || '';
      break;

    default:
      stateEl.textContent = d.state || '';
      stateEl.className   = 'ai-state dim';
  }
}

function triggerRouteAnalysis() {
  fetch(AI_BRIDGE + '/analyze-route', { method: 'POST' })
    .then(r => r.json())
    .then(d => {
      const stateEl = document.getElementById('route-state');
      if (stateEl) {
        stateEl.textContent = 'Analyzing...';
        stateEl.className   = 'ai-state dim';
      }
    })
    .catch(() => {});
}

// ── Arrival Briefing ─────────────────────────────────────────────────────────

function _handleArrivalBriefing(d) {
  const widget = document.getElementById('arrival-widget');
  const dest   = document.getElementById('arrival-dest');
  const text   = document.getElementById('arrival-text');
  if (!widget) return;

  if (dest) dest.textContent = `${d.destination}  •  ${d.distance_nm}nm  •  ${d.offline ? 'OFFLINE AI' : 'Gemini'}`;
  if (text) text.textContent = d.briefing || '';
  widget.style.display = 'block';
}

// ── Anchor Watch ─────────────────────────────────────────────────────────────

function _handleAnchorAlert(d) {
  const widget = document.getElementById('anchor-widget');
  const text   = document.getElementById('anchor-text');
  const meta   = document.getElementById('anchor-meta');
  if (!widget) return;

  if (text) text.textContent = `DRIFT: ${d.drift_m}m  (limit: ${d.max_radius_m}m)`;
  if (meta) meta.textContent = `Direction: ${d.drift_bearing}°  •  Speed: ${d.sog_kts}kts  •  ${_formatTime(d.timestamp)}`;
  widget.style.display = 'block';

  // Pulse the screen
  document.body.classList.add('anchor-alarm-active');
}

function dismissAnchorAlarm() {
  fetch(AI_BRIDGE + '/anchor/dismiss', { method: 'POST' })
    .then(() => {
      const widget = document.getElementById('anchor-widget');
      if (widget) widget.style.display = 'none';
      document.body.classList.remove('anchor-alarm-active');
    })
    .catch(() => {});
}

function getAnchorAdvice() {
  const el = document.getElementById('anchor-advice');
  if (el) {
    el.textContent = 'Getting AI advice...';
    el.style.display = 'block';
  }
  fetch(AI_BRIDGE + '/anchor/advice')
    .then(r => r.json())
    .then(d => {
      if (el) el.textContent = d.advice || 'AI unavailable.';
    })
    .catch(() => {
      if (el) el.textContent = 'AI unavailable.';
    });
}

// ── Voyage Summary ────────────────────────────────────────────────────────────

function _handleVoyageSummary(d) {
  // Voyage summaries go to the settings page voyage panel.
  // If settings is open, refresh it — otherwise a subtle notification only.
  const notice = document.getElementById('voyage-notice');
  if (notice) {
    notice.textContent = 'New voyage summary ready — see Settings > Voyage Summaries';
    notice.style.display = 'block';
  }
}

// ── Panel helpers ─────────────────────────────────────────────────────────────

function togglePanel(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

function closeWidget(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'none';
}

function _setIndicator(id, up) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.toggle('ind-up',   up);
    el.classList.toggle('ind-down', !up);
  }
}

function _formatTime(isoStr) {
  if (!isoStr) return '';
  try {
    return new Date(isoStr).toLocaleTimeString();
  } catch (e) {
    return isoStr;
  }
}

// ── Auto-connect when AvNav screen is shown ───────────────────────────────────
// connectivity-check.js updates indicators — we hook in after page load
window.addEventListener('pageshow', () => {
  connectAIBridge();
});
