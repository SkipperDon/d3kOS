/**
 * connectivity-check.js
 * Polls /status every 30 s and updates indicator icons + menu status bar.
 *
 * Status endpoint (app.py /status) checks:
 *   internet   — http://captive.apple.com
 *   avnav      — http://localhost:8080
 *   gemini     — http://localhost:3001
 *   ai_bridge  — http://localhost:3002 (Phase 5)
 *   signalk    — http://localhost:8099
 *   ollama     — http://192.168.1.36:11434
 */

const POLL_INTERVAL = 30000;

function updateIndicators(status) {
  // Top status bar icons
  const map = {
    'ind-internet':  status.internet,
    'ind-avnav':     status.avnav,
    'ind-gemini':    status.gemini,
    'ind-ai-bridge': status.ai_bridge,
    'ind-signalk':   status.signalk,
    'ind-ollama':    status.ollama,
  };
  for (const [id, alive] of Object.entries(map)) {
    const el = document.getElementById(id);
    if (!el) continue;
    el.classList.toggle('active', alive);
    el.classList.toggle('error',  !alive);
    const label = el.title.split(':')[0];
    el.title = `${label}: ${alive ? 'Online' : 'Offline'}`;
  }

  // Expose internet state for panel-toggle.js weather checks
  window.d3kOnline = status.internet;

  // Bottom status bar on main menu
  updateMenuStatusBar(status);
}

function updateMenuStatusBar(s) {
  const bar = document.getElementById('menu-status-bar');
  if (!bar) return;
  bar.innerHTML = [
    dot(s.internet,   'Internet'),
    dot(s.avnav,      'AvNav :8080'),
    dot(s.signalk,    'SignalK :8099'),
    dot(s.gemini,     'AI :3001'),
    dot(s.ai_bridge,  'AI Bridge :3002'),
    dot(s.ollama,     'Ollama LAN'),
  ].join('');
}

function dot(alive, label) {
  const cls = alive ? 'dot-on' : 'dot-off';
  const sym = alive ? '●' : '●';
  return `<span class="status-dot ${cls}" title="${label}">${sym} ${label}</span>`;
}

async function pollStatus() {
  try {
    const res  = await fetch('/status');
    const data = await res.json();
    updateIndicators(data);
  } catch {
    updateIndicators({
      internet:  false,
      avnav:     false,
      gemini:    false,
      ai_bridge: false,
      signalk:   false,
      ollama:    false,
    });
  }
}

function updateClock() {
  const el = document.getElementById('clock');
  if (el) el.textContent = new Date().toLocaleTimeString();
}

setInterval(pollStatus,    POLL_INTERVAL);
setInterval(updateClock,   1000);
pollStatus();    // immediate first call
updateClock();
