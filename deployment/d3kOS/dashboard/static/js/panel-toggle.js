/**
 * panel-toggle.js
 * Screen navigation and weather panel control for d3kOS dashboard.
 *
 * Screens: menu | avnav | weather | placeholder
 * Weather:
 *   windy — https://embed.windy.com  (requires internet)
 *   radar — https://www.rainviewer.com (requires internet)
 *
 * Coordinates default to Toronto area (43.7, -79.4).
 * Phase 4 will read vessel lat/lon from Signal K and update these dynamically.
 *
 * Reads window.D3K_CONFIG set by index.html inline script:
 *   { avnavUrl, geminiPort }
 */

const WINDY_URL =
  'https://embed.windy.com/embed2.html?lat=43.7&lon=-79.4' +
  '&zoom=5&level=surface&overlay=waves&menu=&message=&marker=' +
  '&calendar=now&pressure=&type=map&location=coordinates' +
  '&detail=&detailLat=43.7&detailLon=-79.4' +
  '&metricWind=kts&metricTemp=%C2%B0C&radarRange=-1';

const RADAR_URL =
  'https://www.rainviewer.com/map.html?loc=43.7,-79.4,6' +
  '&oFa=0&oC=1&oU=0&oCS=1&oF=0&oAP=0&rmt=4&animate=1' +
  '&snow=1&sm=1&sn=0&c=3';

/** Switch to a screen by ID (menu | avnav | weather | placeholder). */
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const target = document.getElementById('screen-' + id);
  if (target) target.classList.add('active');

  // Back button visible on all non-menu screens
  const backBtn = document.getElementById('btn-back');
  if (backBtn) backBtn.style.display = (id === 'menu') ? 'none' : 'inline-block';
}

function goMenu() {
  showScreen('menu');
}

/** Open AvNav — lazy-loads iframe on first visit. */
function showAvNav() {
  const frame = document.getElementById('avnav-frame');
  if (frame && !frame.src) {
    const cfg = window.D3K_CONFIG || {};
    frame.src = cfg.avnavUrl || 'http://localhost:8080';
  }
  showScreen('avnav');
}

/** Open weather screen with a given tab active (windy | radar). */
function showWeather(type) {
  showScreen('weather');
  if (!window.d3kOnline) {
    document.getElementById('offline-notice').style.display = 'block';
    document.getElementById('windy-frame').style.display    = 'none';
    document.getElementById('radar-frame').style.display    = 'none';
    setWeatherTab(null);
    return;
  }
  document.getElementById('offline-notice').style.display = 'none';
  switchWeatherTab(type);
}

/** Switch Windy / Radar tabs on the weather screen. */
function switchWeatherTab(type) {
  const windyFrame = document.getElementById('windy-frame');
  const radarFrame = document.getElementById('radar-frame');
  const offline    = document.getElementById('offline-notice');

  if (!window.d3kOnline) {
    offline.style.display     = 'block';
    windyFrame.style.display  = 'none';
    radarFrame.style.display  = 'none';
    setWeatherTab(null);
    return;
  }

  offline.style.display = 'none';

  if (type === 'windy') {
    if (!windyFrame.src) windyFrame.src = WINDY_URL;   // lazy load on first open
    windyFrame.style.display = 'block';
    radarFrame.style.display = 'none';
  } else {
    if (!radarFrame.src) radarFrame.src = RADAR_URL;   // lazy load on first open
    radarFrame.style.display = 'block';
    windyFrame.style.display = 'none';
  }
  setWeatherTab(type);
}

function setWeatherTab(type) {
  const tw = document.getElementById('tab-windy');
  const tr = document.getElementById('tab-radar');
  if (tw) tw.classList.toggle('active', type === 'windy');
  if (tr) tr.classList.toggle('active', type === 'radar');
}

/** Show placeholder screen for features coming in a later phase. */
function showPlaceholder(title, phase) {
  const t = document.getElementById('ph-title');
  const s = document.getElementById('ph-sub');
  if (t) t.textContent = title;
  if (s) s.textContent = 'Coming in ' + phase;
  showScreen('placeholder');
}

/** Open AI Navigation in a new browser tab. */
function openAI() {
  const cfg  = window.D3K_CONFIG || {};
  const port = cfg.geminiPort || '3001';
  window.open('http://localhost:' + port, '_blank');
}

/**
 * Open Marine Vision cameras in a new browser tab.
 * Camera system runs at port 8084 (camera_stream_manager.py — v0.9.2).
 */
function openCameras() {
  window.open('http://localhost:8084', '_blank');
}

/** Trigger OpenCPN launch via Node-RED POST (route: /launch/opencpn). */
function launchOpenCPN() {
  fetch('/launch/opencpn', { method: 'POST' })
    .then(r => r.json())
    .then(d => { if (!d.ok) console.warn('OpenCPN launch error:', d.error); })
    .catch(e => console.warn('OpenCPN launch failed:', e));
}
