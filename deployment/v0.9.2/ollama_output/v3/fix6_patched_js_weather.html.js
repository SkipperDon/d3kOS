// Configuration
const SIGNALK_WS = 'ws://' + window.location.hostname + '/signalk/v1/stream?subscribe=none';
const UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutes
const AUTOLOG_INTERVAL = 30 * 60 * 1000; // 30 minutes

// Default position: Lake Simcoe, Ontario (fallback when GPS unavailable)
let currentPosition = { lat: 44.4167, lon: -79.3333 };
let hasGPSFix = false; // Track if we have actual GPS data
let weatherData = null;
let lastLogTime = null;
let currentZoom = 9; // Default zoom level
let currentOverlay = 'wind'; // Default overlay
let lastRadarPosition = { lat: null, lon: null }; // Track last radar update position
let gpsResolved = false;

// Signal K connection
let signalkWS = null;


window.addEventListener('measurementSystemChanged', function() {
  updateRadar();  // reload Windy embed with updated units
});

function connectSignalK() {
  signalkWS = new WebSocket(SIGNALK_WS);

  signalkWS.onopen = () => {
    console.log('Signal K connected');
    // Subscribe to GPS position
    signalkWS.send(JSON.stringify({
      context: 'vessels.self',
      subscribe: [
        { path: 'navigation.position', period: 5000 }
      ]
    }));
  };

  signalkWS.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.updates) {
        data.updates.forEach(update => {
          if (update.values) {
            update.values.forEach(value => {
              if (value.path === 'navigation.position' && value.value) {
                currentPosition.lat = value.value.latitude;
                currentPosition.lon = value.value.longitude;
                hasGPSFix = true;
                updateLocation();
                if (!weatherData) {
                  fetchWeatherData();
                }
              }
            });
          }
        });
      }
    } catch (err) {
      console.error('Signal K parse error:', err);
    }
  };

  signalkWS.onerror = (error) => {
    console.error('Signal K error:', error);
  };

  signalkWS.onclose = () => {
    console.log('Signal K disconnected, reconnecting...');
    setTimeout(connectSignalK, 5000);
  };
}

function updateLocation() {
  if (currentPosition.lat && currentPosition.lon) {
    document.getElementById('locationCoords').textContent =
      `${currentPosition.lat.toFixed(5)}°, ${currentPosition.lon.toFixed(5)}°`;

    // Only update radar if position changed significantly (>0.01 degrees ~1km)
    const positionChanged = !lastRadarPosition.lat ||
      Math.abs(currentPosition.lat - lastRadarPosition.lat) > 0.01 ||
      Math.abs(currentPosition.lon - lastRadarPosition.lon) > 0.01;

    if (positionChanged) {
      updateRadar();
      lastRadarPosition.lat = currentPosition.lat;
      lastRadarPosition.lon = currentPosition.lon;
    }
  }
}

function updateRadar() {
  if (!currentPosition.lat || !currentPosition.lon) return;

  // Use Windy.com embedded map with current overlay and zoom
  const windyUrl = `https://embed.windy.com/embed2.html?lat=${currentPosition.lat}&lon=${currentPosition.lon}&detailLat=${currentPosition.lat}&detailLon=${currentPosition.lon}&width=100%&height=100%&zoom=${currentZoom}&level=surface&overlay=${currentOverlay}&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=kt&metricTemp=%C2%B0C&radarRange=-1`;

  document.getElementById('radarFrame').src = windyUrl;
  document.getElementById('locationName').textContent = 'Current Position';
}

// Map control functions
function zoomIn() {
  if (currentZoom < 15) {
    currentZoom++;
    updateRadar();
  }
}

function zoomOut() {
  if (currentZoom > 3) {
    currentZoom--;
    updateRadar();
  }
}

function recenterMap() {
  // Force radar update to recenter on current position
  if (currentPosition.lat && currentPosition.lon) {
    lastRadarPosition.lat = null; // Reset to force update
    lastRadarPosition.lon = null;
    updateRadar();
  }
}

function changeOverlay(overlay) {
  currentOverlay = overlay;
  updateRadar();

  // Update button states
  document.querySelectorAll('.overlay-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  document.getElementById('btn-' + overlay).classList.add('active');
}

// Initialize overlay buttons
function initOverlayButtons() {
  const buttons = {
    'btn-wind': 'wind',
    'btn-clouds': 'clouds',
    'btn-radar': 'radar'
  };

  Object.keys(buttons).forEach(btnId => {
    const btn = document.getElementById(btnId);
    const overlay = buttons[btnId];

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      changeOverlay(overlay);
    });

    btn.addEventListener('touchend', (e) => {
      e.preventDefault();
      changeOverlay(overlay);
    });
  });
}

// Initialize map control buttons
function initMapControls() {
  const zoomInBtn = document.getElementById('zoom-in');
  const zoomOutBtn = document.getElementById('zoom-out');
  const recenterBtn = document.getElementById('recenter');

  // Zoom In
  zoomInBtn.addEventListener('click', (e) => {
    e.preventDefault();
    zoomIn();
  });
  zoomInBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    zoomIn();
  });

  // Zoom Out
  zoomOutBtn.addEventListener('click', (e) => {
    e.preventDefault();
    zoomOut();
  });
  zoomOutBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    zoomOut();
  });

  // Recenter
  recenterBtn.addEventListener('click', (e) => {
    e.preventDefault();
    recenterMap();
  });
  recenterBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    recenterMap();
  });
}

// Navigation button touch support
const navBtn = document.getElementById('nav-main-menu');
if (navBtn) {
  navBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    window.location.href = 'index.html';
  });
}

async function initPosition() {
  try {
    const r = await fetch('/signalk/v1/api/vessels/self/navigation/position', { signal: AbortSignal.timeout(4000) });
    const d = await r.json();
    if (d.value && d.value.latitude && d.value.longitude) {
      currentPosition = { lat: d.value.latitude, lon: d.value.longitude };
      gpsResolved = true;
    }
  } catch (e) { /* fallback to Lake Simcoe */ }
  initMap(); // call map init after position resolved
}

function initMap() {
  // Load radar with default position on page load
  updateRadar();
  fetchWeatherData(); // Fetch initial weather data
  initOverlayButtons();
  initMapControls();
}

async function fetchWeatherData() {
  if (!currentPosition.lat || !currentPosition.lon) {
    console.log('No GPS position yet');
    return;
  }

  try {
    // Open-Meteo Marine API
    const marineUrl = `https://marine-api.open-meteo.com/v1/marine?latitude=${currentPosition.lat}&longitude=${currentPosition.lon}&current=wave_height,wave_direction,wave_period,wind_wave_height,wind_wave_direction,wind_wave_period&hourly=wave_height,wave_direction,wave_period&timezone=auto`;

    const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${currentPosition.lat}&longitude=${currentPosition.lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m&hourly=temperature_2m,precipitation_probability,weather_code,visibility,wind_speed_10m,wind_gusts_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto`;

    const [marineResponse, weatherResponse] = await Promise.all([
      fetch(marineUrl),
      fetch(weatherUrl)
    ]);

    const marineData = await marineResponse.json();
    const weatherDataRaw = await weatherResponse.json();

    weatherData = {
      marine: marineData,
      weather: weatherDataRaw,
      timestamp: new Date().toISOString()
    };

    displayWeatherData();
    updateAutologStatus();

  } catch (error) {
    console.error('Weather fetch error:', error);
    document.getElementById('conditionsPanel').innerHTML =
      '<div class="error">Failed to load weather data. Check internet connection.</div>';
  }
}

function displayWeatherData() {
  if (!weatherData) return;

  const marine = weatherData.marine.current;
  const weather = weatherData.weather.current;
  const hourly = weatherData.weather.hourly;

  const timestamp = new Date(weatherData.timestamp).toLocaleString();
  const weatherCode = getWeatherDescription(weather.weather_code);
  const visibility = hourly.visibility ? (hourly.visibility[0] / 1000).toFixed(1) : 'N/A';

  // Check for warnings
  const warnings = [];
  if (weather.wind_gusts_10m > 25) {
    warnings.push({
      title: 'High Wind Warning',
      description: `Wind gusts up to ${weather.wind_gusts_10m.toFixed(1)} kt`,
      critical: weather.wind_gusts_10m > 35
    });
  }
  if (marine.wave_height && marine.wave_height > 2.0) {
    warnings.push({
      title: 'High Seas Warning',
      description: `Wave height ${marine.wave_height.toFixed(1)} m`,
      critical: marine.wave_height > 3.5
    });
  }
  if (weather.precipitation > 5.0) {
    warnings.push({
      title: 'Heavy Precipitation',
      description: `${weather.precipitation.toFixed(1)} mm/hr`,
      critical: weather.precipitation > 10.0
    });
  }

  let html = `
    <div class="timestamp">${timestamp}</div>
  `;

  // Warnings/Alerts
  if (warnings.length > 0) {
    warnings.forEach(warning => {
      html += `
        <div class="alert-box ${warning.critical ? 'critical' : ''}">
          <div class="alert-title">${warning.title}</div>
          <div class="alert-description">${warning.description}</div>
        </div>
      `;
    });
  }

  // Wind Conditions
  html += `
    <div class="data-group">
      <h2>Wind Conditions</h2>
      <div class="data-row">
        <span class="data-label">Wind Speed</span>
        <span class="data-value">${weather.wind_speed_10m.toFixed(1)} kt</span>
      </div>
      <div class="data-row">
        <span class="data-label">Wind Direction</span>
        <span class="data-value">${weather.wind_direction_10m}° (${getWindDirection(weather.wind_direction_10m)})</span>
      </div>
      <div class="data-row">
        <span class="data-label">Gusts</span>
        <span class="data-value ${weather.wind_gusts_10m > 25 ? 'warning' : ''}">${weather.wind_gusts_10m.toFixed(1)} kt</span>
      </div>
    </div>
  `;
  // Sea State
  const waveHeightVal = marine.wave_height ? marine.wave_height.toFixed(1) + " m" : "N/A";
  const waveDirectionVal = marine.wave_direction ? marine.wave_direction + "° (" + getWindDirection(marine.wave_direction) + ")" : "N/A";
  const wavePeriodVal = marine.wave_period ? marine.wave_period.toFixed(1) + " s" : "N/A";
  const seaStateVal = marine.wave_height ? getSeaState(marine.wave_height) : "Inland";
  
  html += `
    <div class="data-group">
      <h2>Sea State</h2>
      <div class="data-row">
        <span class="data-label">Wave Height</span>
        <span class="data-value ${marine.wave_height && marine.wave_height > 2.0 ? "warning" : ""}">${waveHeightVal}</span>
      </div>
      <div class="data-row">
        <span class="data-label">Wave Direction</span>
        <span class="data-value">${waveDirectionVal}</span>
      </div>
      <div class="data-row">
        <span class="data-label">Wave Period</span>
        <span class="data-value">${wavePeriodVal}</span>
      </div>
      <div class="data-row">
        <span class="data-label">Sea State</span>
        <span class="data-value">${seaStateVal}</span>
      </div>
    </div>
  `;

  // Atmospheric Conditions
  html += `
    <div class="data-group">
      <h2>Atmospheric</h2>
      <div class="data-row">
        <span class="data-label">Weather</span>
        <span class="data-value">${weatherCode}</span>
      </div>
      <div class="data-row">
        <span class="data-label">Visibility</span>
        <span class="data-value">${visibility} km</span>
      </div>
      <div class="data-row">
        <span class="data-label">Temperature</span>
        <span class="data-value">${weather.temperature_2m.toFixed(1)}°C</span>
      </div>
      <div class="data-row">
        <span class="data-label">Humidity</span>
        <span class="data-value">${weather.relative_humidity_2m}%</span>
      </div>
      <div class="data-row">
        <span class="data-label">Barometric Pressure</span>
        <span class="data-value">${weather.surface_pressure.toFixed(1)} hPa</span>
      </div>
      <div class="data-row">
        <span class="data-label">Precipitation</span>
        <span class="data-value ${weather.precipitation > 5.0 ? 'warning' : ''}">${weather.precipitation.toFixed(1)} mm</span>
      </div>
    </div>
  `;

  document.getElementById('conditionsPanel').innerHTML = html;
}

function getWeatherDescription(code) {
  const codes = {
    0: 'Clear sky',
    1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Foggy', 48: 'Depositing rime fog',
    51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
    61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
    71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
    80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
    95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
  };
  return codes[code] || 'Unknown';
}

function getWindDirection(degrees) {
  const dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  return dirs[Math.round(degrees / 22.5) % 16];
}

function getSeaState(waveHeight) {
  if (waveHeight < 0.1) return 'Calm (glassy)';
  if (waveHeight < 0.5) return 'Calm (rippled)';
  if (waveHeight < 1.25) return 'Smooth';
  if (waveHeight < 2.5) return 'Slight';
  if (waveHeight < 4.0) return 'Moderate';
  if (waveHeight < 6.0) return 'Rough';
  if (waveHeight < 9.0) return 'Very rough';
  if (waveHeight < 14.0) return 'High';
  return 'Very high';
}

function updateAutologStatus() {
  const now = Date.now();
  if (!lastLogTime) {
    lastLogTime = now;
  }
  const elapsed = now - lastLogTime;
  const remaining = AUTOLOG_INTERVAL - elapsed;
  const minutes = Math.floor(remaining / 60000);

  document.getElementById('autologStatus').textContent =
    `Auto-log: Next in ${minutes} min`;
}

async function logToBoatlog() {
  if (!weatherData || !currentPosition.lat || !currentPosition.lon) {
    console.log('No weather data to log');
    return;
  }

  const marine = weatherData.marine.current;
  const weather = weatherData.weather.current;

  const logEntry = {
    timestamp: new Date().toISOString(),
    type: 'weather',
    position: {
      latitude: currentPosition.lat,
      longitude: currentPosition.lon
    },
    weather: {
      wind_speed: weather.wind_speed_10m,
      wind_direction: weather.wind_direction_10m,
      wind_gusts: weather.wind_gusts_10m,
      wave_height: marine.wave_height,
      wave_direction: marine.wave_direction,
      wave_period: marine.wave_period,
      temperature: weather.temperature_2m,
      pressure: weather.surface_pressure,
      precipitation: weather.precipitation,
      visibility: weatherData.weather.hourly.visibility ? weatherData.weather.hourly.visibility[0] : null,
      weather_code: weather.weather_code,
      description: getWeatherDescription(weather.weather_code)
    }
  };

  try {
    // TODO: Replace with actual boatlog API endpoint
    console.log('Weather logged to boatlog:', logEntry);

    // Update last log time
    lastLogTime = Date.now();
    updateAutologStatus();

    // Visual feedback
    const statusEl = document.getElementById('autologStatus');
    statusEl.textContent = 'Auto-log: Saved ✓';
    statusEl.style.borderColor = 'var(--color-accent)';
    setTimeout(() => {
      statusEl.style.borderColor = '';
      updateAutologStatus();
    }, 3000);

  } catch (error) {
    console.error('Boatlog error:', error);
    const statusEl = document.getElementById('autologStatus');
    statusEl.textContent = 'Auto-log: Failed ✗';
    statusEl.style.borderColor = 'var(--color-critical)';
    setTimeout(() => {
      statusEl.style.borderColor = '';
      updateAutologStatus();
    }, 3000);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', initPosition);