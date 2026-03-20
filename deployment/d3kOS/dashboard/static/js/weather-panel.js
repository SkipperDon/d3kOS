/**
 * weather-panel.js — d3kOS v0.9.2.3
 * Left-side overlay: live weather conditions panel.
 * Items: I-11, I-12, I-13
 *
 * - GPS from Signal K REST navigation.position
 * - Weather from Open-Meteo (free, no API key)
 * - Marine from Open-Meteo Marine API (free, no API key)
 * - Auto-logs weather snapshot to localStorage every 30 min while panel open
 * - Falls back to Lake Simcoe (43.4167, -79.3333) if GPS unavailable
 *
 * Public API:
 *   openWeatherPanel()    — fetch data + slide panel in
 *   closeWeatherPanel()   — slide panel out, stop auto-log timer
 *   toggleWeatherPanel()  — called by Weather nav button
 */

const WX_FALLBACK_LAT = 43.4167;
const WX_FALLBACK_LON = -79.3333;

let _wxOpen = false;
let _wxAutoLogTimer = null;
let _wxLat = WX_FALLBACK_LAT;
let _wxLon = WX_FALLBACK_LON;

/* ── GPS from Signal K ── */
async function _wxGetGPS() {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 3000);
    const r = await fetch(
      'http://localhost:8099/signalk/v1/api/vessels/self/navigation/position',
      { signal: ctrl.signal }
    );
    clearTimeout(t);
    if (!r.ok) return null;
    const d = await r.json();
    if (d && d.value && typeof d.value.latitude === 'number') {
      return { lat: d.value.latitude, lon: d.value.longitude };
    }
    return null;
  } catch { return null; }
}

/* ── Open-Meteo current weather ── */
async function _wxFetchWeather(lat, lon) {
  try {
    const p = new URLSearchParams({
      latitude: lat,
      longitude: lon,
      current: [
        'temperature_2m',
        'relative_humidity_2m',
        'precipitation',
        'weather_code',
        'surface_pressure',
        'wind_speed_10m',
        'wind_direction_10m',
        'wind_gusts_10m',
        'visibility'
      ].join(','),
      timezone: 'auto',
      forecast_days: 1
    });
    const r = await fetch('https://api.open-meteo.com/v1/forecast?' + p);
    return r.ok ? await r.json() : null;
  } catch { return null; }
}

/* ── Open-Meteo Marine API ── */
async function _wxFetchMarine(lat, lon) {
  try {
    const p = new URLSearchParams({
      latitude: lat,
      longitude: lon,
      current: 'wave_height,wave_direction,wave_period,wind_wave_height',
      timezone: 'auto',
      forecast_days: 1
    });
    const r = await fetch('https://marine-api.open-meteo.com/v1/marine?' + p);
    return r.ok ? await r.json() : null;
  } catch { return null; }
}

/* ── WMO weather code → plain English ── */
function _wxDesc(code) {
  const m = {
    0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Fog', 48: 'Icy fog',
    51: 'Light drizzle', 53: 'Drizzle', 55: 'Heavy drizzle',
    61: 'Light rain', 63: 'Rain', 65: 'Heavy rain',
    71: 'Light snow', 73: 'Snow', 75: 'Heavy snow',
    80: 'Rain showers', 81: 'Heavy showers', 82: 'Violent showers',
    95: 'Thunderstorm', 96: 'Thunderstorm + hail', 99: 'Severe thunderstorm'
  };
  return m[code] || 'Conditions unknown';
}

/* ── Degrees → compass point ── */
function _wxWindDir(deg) {
  const dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE',
                'S','SSW','SW','WSW','W','WNW','NW','NNW'];
  return dirs[Math.round(deg / 22.5) % 16];
}

/* ── Wave height → sea state label ── */
function _wxSeaState(h) {
  if (h < 0.1)  return 'Calm (glassy)';
  if (h < 0.5)  return 'Calm (rippled)';
  if (h < 1.25) return 'Slight';
  if (h < 2.5)  return 'Moderate';
  if (h < 4.0)  return 'Rough';
  if (h < 6.0)  return 'Very rough';
  if (h < 9.0)  return 'High';
  if (h < 14.0) return 'Very high';
  return 'Phenomenal';
}

/* ── Weather code → alert level ── */
function _wxAlertLevel(code) {
  if ([95, 96, 99].includes(code)) return 'critical';
  if ([80, 81, 82, 65, 75].includes(code)) return 'warning';
  return 'none';
}

/* ── Build panel inner HTML ── */
function _wxBuildHTML(wx, marine) {
  const c = wx ? wx.current : null;
  const m = marine ? marine.current : null;
  let h = '';

  /* Alert banner */
  if (c) {
    const lvl = _wxAlertLevel(c.weather_code);
    if (lvl !== 'none') {
      const cls = lvl === 'critical' ? 'wx-alert wx-crit' : 'wx-alert wx-warn';
      h += `<div class="${cls}">&#9888; ${_wxDesc(c.weather_code).toUpperCase()}</div>`;
    }
  }

  /* Conditions heading */
  if (c) {
    h += `<div class="wx-cond-head">${_wxDesc(c.weather_code)}</div>`;
  }

  /* Wind */
  if (c) {
    h += `<div class="wx-sec">
      <div class="wx-sec-ttl">WIND</div>
      <div class="wx-row">
        <span class="wx-k">Speed</span>
        <span class="wx-v">${c.wind_speed_10m}<span class="wx-u"> km/h</span></span>
      </div>
      <div class="wx-row">
        <span class="wx-k">Direction</span>
        <span class="wx-v">${_wxWindDir(c.wind_direction_10m)}<span class="wx-u"> ${c.wind_direction_10m}&deg;</span></span>
      </div>
      <div class="wx-row">
        <span class="wx-k">Gusts</span>
        <span class="wx-v">${c.wind_gusts_10m}<span class="wx-u"> km/h</span></span>
      </div>
    </div>`;
  }

  /* Sea state */
  if (m) {
    const wh = typeof m.wave_height === 'number' ? m.wave_height.toFixed(1) : '--';
    const wp = typeof m.wave_period  === 'number' ? m.wave_period            : '--';
    const ww = typeof m.wind_wave_height === 'number'
      ? `<div class="wx-row"><span class="wx-k">Wind waves</span><span class="wx-v">${m.wind_wave_height.toFixed(1)}<span class="wx-u"> m</span></span></div>`
      : '';
    h += `<div class="wx-sec">
      <div class="wx-sec-ttl">SEA STATE</div>
      <div class="wx-row">
        <span class="wx-k">Wave height</span>
        <span class="wx-v">${wh}<span class="wx-u"> m &middot; ${_wxSeaState(m.wave_height)}</span></span>
      </div>
      <div class="wx-row">
        <span class="wx-k">Direction</span>
        <span class="wx-v">${_wxWindDir(m.wave_direction)}<span class="wx-u"> ${m.wave_direction}&deg;</span></span>
      </div>
      <div class="wx-row">
        <span class="wx-k">Period</span>
        <span class="wx-v">${wp}<span class="wx-u"> s</span></span>
      </div>
      ${ww}
    </div>`;
  } else {
    h += `<div class="wx-sec">
      <div class="wx-sec-ttl">SEA STATE</div>
      <div class="wx-no-data">Marine data unavailable</div>
    </div>`;
  }

  /* Atmospheric */
  if (c) {
    const vis = typeof c.visibility === 'number'
      ? (c.visibility / 1000).toFixed(1) + ' km'
      : '--';
    h += `<div class="wx-sec">
      <div class="wx-sec-ttl">ATMOSPHERIC</div>
      <div class="wx-row">
        <span class="wx-k">Pressure</span>
        <span class="wx-v">${c.surface_pressure}<span class="wx-u"> hPa</span></span>
      </div>
      <div class="wx-row">
        <span class="wx-k">Temperature</span>
        <span class="wx-v">${c.temperature_2m}<span class="wx-u"> &deg;C</span></span>
      </div>
      <div class="wx-row">
        <span class="wx-k">Humidity</span>
        <span class="wx-v">${c.relative_humidity_2m}<span class="wx-u"> %</span></span>
      </div>
      <div class="wx-row">
        <span class="wx-k">Visibility</span>
        <span class="wx-v">${vis}</span>
      </div>
      <div class="wx-row">
        <span class="wx-k">Precipitation</span>
        <span class="wx-v">${c.precipitation}<span class="wx-u"> mm</span></span>
      </div>
    </div>`;
  }

  /* GPS source note */
  h += `<div class="wx-gps-note">&#128205; ${_wxLat.toFixed(4)}&deg;, ${_wxLon.toFixed(4)}&deg;</div>`;

  return h;
}

/* ── Auto-log weather snapshot to localStorage ── */
/* BUG FIX 1 (Session E): key was 'd3kBoatLog', field was 'ts'.
   boat-log.html uses key 'd3kos-boatlog-entries' and reads 'timestamp' + 'text'.
   Entry format now matches boatlog-engine.js schema. */
function _wxLogSnapshot(wx, marine) {
  const c = wx    ? wx.current    : {};
  const m = marine ? marine.current : {};

  /* Build a human-readable text summary for boat-log.html renderEntries() */
  const parts = [];
  if (c.wind_speed_10m !== undefined)
    parts.push('Wind ' + c.wind_speed_10m + ' km/h ' + _wxWindDir(c.wind_direction_10m));
  if (m && m.wave_height !== undefined)
    parts.push('Waves ' + m.wave_height.toFixed(1) + 'm');
  if (c.temperature_2m !== undefined)
    parts.push(c.temperature_2m + '\u00b0C');
  if (c.surface_pressure !== undefined)
    parts.push(c.surface_pressure + ' hPa');
  parts.push('\u{1F4CD} ' + _wxLat.toFixed(4) + '\u00b0, ' + _wxLon.toFixed(4) + '\u00b0');

  const entry = {
    timestamp: new Date().toISOString(),
    type:      'weather',
    text:      parts.join(' \u00b7 '),
  };

  /* Save to localStorage — same key and format as boat-log.html and boatlog-engine.js */
  try {
    const arr = JSON.parse(localStorage.getItem('d3kos-boatlog-entries') || '[]');
    arr.unshift(entry);
    if (arr.length > 500) arr.length = 500;
    localStorage.setItem('d3kos-boatlog-entries', JSON.stringify(arr));
  } catch { /* storage full — ignore */ }
}

/* ── Update Weather nav button active state ── */
function _wxSetNavActive(active) {
  document.querySelectorAll('#bot .nb').forEach(b => {
    const lbl = b.querySelector('.nb-lbl');
    if (lbl && lbl.textContent.trim() === 'Weather') {
      b.classList.toggle('on', active);
    } else if (active) {
      b.classList.remove('on');
    }
  });
  /* If deactivating, restore Dashboard */
  if (!active) {
    const first = document.querySelector('#bot .nb');
    if (first) first.classList.add('on');
  }
}

/* ── Open panel: fetch data, slide in ── */
async function openWeatherPanel() {
  const panel = document.getElementById('wxPanel');
  const body  = document.getElementById('wxPanelBody');
  if (!panel) return;

  _wxOpen = true;

  /* GPS first (non-blocking — fall back immediately if unavailable) */
  const gps = await _wxGetGPS();
  if (gps) { _wxLat = gps.lat; _wxLon = gps.lon; }

  /* Show loading state, then slide open */
  if (body) body.innerHTML = '<div class="wx-loading">Loading conditions&hellip;</div>';
  panel.classList.add('open');
  _wxSetNavActive(true);

  /* Fetch both weather APIs in parallel */
  try {
    const [wx, marine] = await Promise.all([
      _wxFetchWeather(_wxLat, _wxLon),
      _wxFetchMarine(_wxLat, _wxLon)
    ]);
    if (body) body.innerHTML = _wxBuildHTML(wx, marine);

    /* Log on open, then every 30 minutes */
    _wxLogSnapshot(wx, marine);
    _wxAutoLogTimer = setInterval(async () => {
      const [w2, m2] = await Promise.all([
        _wxFetchWeather(_wxLat, _wxLon),
        _wxFetchMarine(_wxLat, _wxLon)
      ]);
      if (body) body.innerHTML = _wxBuildHTML(w2, m2);
      _wxLogSnapshot(w2, m2);
    }, 30 * 60 * 1000);

  } catch {
    if (body) body.innerHTML =
      '<div class="wx-loading">Unable to load weather data.<br>Check internet connection.</div>';
  }
}

/* ── Close panel ── */
function closeWeatherPanel() {
  _wxOpen = false;
  clearInterval(_wxAutoLogTimer);
  _wxAutoLogTimer = null;

  const panel = document.getElementById('wxPanel');
  if (panel) panel.classList.remove('open');
  _wxSetNavActive(false);
}

/* ── Toggle (Weather nav button) ── */
function toggleWeatherPanel() {
  if (_wxOpen) closeWeatherPanel();
  else openWeatherPanel();
}
