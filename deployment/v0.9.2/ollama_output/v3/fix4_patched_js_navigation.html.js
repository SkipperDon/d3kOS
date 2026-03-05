// === Navigation JavaScript ===

let signalKSocket = null;
let signalKConnected = false;
let navData = {
  position: { latitude: null, longitude: null },
  speedOverGround: null,
  courseOverGroundTrue: null,
  heading: null,
  depth: null,
  gnss: {
    satellites: null,
    horizontalDilution: null,
    methodQuality: null
  }
};
let aisTargets = {};
let lastDataTime = null;

// Load data on startup
window.addEventListener('DOMContentLoaded', () => {
  // Fetch initial data immediately
  fetch('/signalk/v1/api/vessels/self')
    .then(r => r.json())
    .then(data => {
      console.log('Initial data fetched:', data);
      // Update position
      if (data.navigation && data.navigation.position && data.navigation.position.value) {
        navData.position.latitude = data.navigation.position.value.latitude;
        navData.position.longitude = data.navigation.position.value.longitude;
        updatePosition();
      }
      // Update other nav data
      if (data.navigation) {
        if (data.navigation.speedOverGround && data.navigation.speedOverGround.value != null) {
          navData.speedOverGround = data.navigation.speedOverGround.value;
          updateSOG();
        }
        if (data.navigation.courseOverGroundTrue && data.navigation.courseOverGroundTrue.value != null) {
          navData.courseOverGroundTrue = data.navigation.courseOverGroundTrue.value;
          updateCOG();
        }
        if (data.navigation.headingTrue && data.navigation.headingTrue.value != null) {
          navData.heading = data.navigation.headingTrue.value;
          updateHeading();
        }
        if (data.environment && data.environment.depth && data.environment.depth.belowKeel && data.environment.depth.belowKeel.value != null) {
          navData.depth = data.environment.depth.belowKeel.value;
          updateDepth();
        }
        if (data.navigation.gnss) {
          if (data.navigation.gnss.satellites && data.navigation.gnss.satellites.value != null) {
            navData.gnss.satellites = data.navigation.gnss.satellites.value;
          }
          if (data.navigation.gnss.horizontalDilution && data.navigation.gnss.horizontalDilution.value != null) {
            navData.gnss.horizontalDilution = data.navigation.gnss.horizontalDilution.value;
          }
          if (data.navigation.gnss.methodQuality && data.navigation.gnss.methodQuality.value != null) {
            navData.gnss.methodQuality = data.navigation.gnss.methodQuality.value;
          }
          updateGPSStatus();
        }
      }
      lastDataTime = new Date();
    })
    .catch(err => console.error('Failed to fetch initial data:', err));

  connectSignalK();
  setInterval(updateDataAge, 1000);
});


window.addEventListener('measurementSystemChanged', function() {
  updateSOG();
  updateDepth();
});

function connectSignalK() {
  try {
    signalKSocket = new WebSocket('ws://' + window.location.hostname + '/signalk/v1/stream?subscribe=none');

    signalKSocket.onopen = () => {
      console.log('Signal K connected');
      signalKConnected = true;
      document.getElementById('connection-status').classList.add('connected');
      document.getElementById('connection-text').textContent = 'GPS Position & AIS Targets';

      // Subscribe to navigation data
      signalKSocket.send(JSON.stringify({
        context: 'vessels.self',
        subscribe: [
          { path: 'navigation.position' },
          { path: 'navigation.speedOverGround' },
          { path: 'navigation.courseOverGroundTrue' },
          { path: 'navigation.headingTrue' },
          { path: 'environment.depth.belowKeel' },
          { path: 'navigation.gnss.satellites' },
          { path: 'navigation.gnss.horizontalDilution' },
          { path: 'navigation.gnss.methodQuality' }
        ]
      }));

      // Subscribe to AIS targets
      signalKSocket.send(JSON.stringify({
        context: 'vessels.*',
        subscribe: [
          { path: 'navigation.position' },
          { path: 'name' },
          { path: 'navigation.speedOverGround' },
          { path: 'navigation.courseOverGroundTrue' }
        ]
      }));
    };

    signalKSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.updates) {
        processSignalKUpdate(data);
      }
    };

    signalKSocket.onerror = (error) => {
      console.error('Signal K error:', error);
      signalKConnected = false;
      document.getElementById('connection-status').classList.remove('connected');
    };

    signalKSocket.onclose = () => {
      console.log('Signal K disconnected');
      signalKConnected = false;
      document.getElementById('connection-status').classList.remove('connected');
      setTimeout(connectSignalK, 5000);
    };

  } catch (error) {
    console.error('Failed to connect to Signal K:', error);
  }
}

function processSignalKUpdate(data) {
  lastDataTime = new Date();

  data.updates.forEach(update => {
    const context = data.context || 'vessels.self';

    update.values.forEach(value => {
      const path = value.path;
      const val = value.value;

      // Handle own vessel data
      if (context === 'vessels.self') {
        if (path === 'navigation.position' && val) {
          navData.position.latitude = val.latitude;
          navData.position.longitude = val.longitude;
          updatePosition();
        } else if (path === 'navigation.speedOverGround' && val !== null) {
          navData.speedOverGround = val;
          updateSOG();
        } else if (path === 'navigation.courseOverGroundTrue' && val !== null) {
          navData.courseOverGroundTrue = val;
          updateCOG();
        } else if (path === 'navigation.headingTrue' && val !== null) {
          navData.heading = val;
          updateHeading();
        } else if (path === 'environment.depth.belowKeel' && val !== null) {
          navData.depth = val;
          updateDepth();
        } else if (path === 'navigation.gnss.satellites' && val !== null) {
          navData.gnss.satellites = val;
          updateGPSStatus();
        } else if (path === 'navigation.gnss.horizontalDilution' && val !== null) {
          navData.gnss.horizontalDilution = val;
          updateGPSStatus();
        } else if (path === 'navigation.gnss.methodQuality' && val !== null) {
          navData.gnss.methodQuality = val;
          updateGPSStatus();
        }
      } else if (context.startsWith('vessels.') && context !== 'vessels.self') {
        // Handle AIS target data
        const mmsi = context.split('.')[1];
        if (!aisTargets[mmsi]) {
          aisTargets[mmsi] = {};
        }

        if (path === 'name') {
          aisTargets[mmsi].name = val;
        } else if (path === 'navigation.position' && val) {
          aisTargets[mmsi].position = val;
        } else if (path === 'navigation.speedOverGround') {
          aisTargets[mmsi].sog = val;
        } else if (path === 'navigation.courseOverGroundTrue') {
          aisTargets[mmsi].cog = val;
        }

        updateAISTargets();
      }
    });
  });
}

function updatePosition() {
  const lat = navData.position.latitude;
  const lon = navData.position.longitude;

  if (lat !== null && lon !== null) {
    document.getElementById('latitude').textContent = formatLatitude(lat);
    document.getElementById('longitude').textContent = formatLongitude(lon);
    document.getElementById('position-display').classList.remove('no-data');
  } else {
    document.getElementById('latitude').textContent = '--';
    document.getElementById('longitude').textContent = '--';
    document.getElementById('position-display').classList.add('no-data');
  }
}

function updateSOG() {
  const sog = navData.speedOverGround;
  if (sog !== null) {
    const knots = sog * 1.944; // m/s to knots
    document.getElementById('sog').textContent =
      (typeof Units !== 'undefined') ? Units.speed.toDisplay(knots) : knots.toFixed(1) + ' kts';
    document.getElementById('card-sog').classList.remove('no-data');
  } else {
    document.getElementById('sog').textContent = '--';
    document.getElementById('card-sog').classList.add('no-data');
  }
}

function updateCOG() {
  const cog = navData.courseOverGroundTrue;
  if (cog !== null) {
    const degrees = radiansToDegrees(cog);
    document.getElementById('cog').textContent = Math.round(degrees);
    document.getElementById('cog-cardinal').textContent = degreesToCardinal(degrees);
    document.getElementById('card-cog').classList.remove('no-data');
  } else {
    document.getElementById('cog').textContent = '--';
    document.getElementById('cog-cardinal').textContent = '--';
    document.getElementById('card-cog').classList.add('no-data');
  }
}

function updateHeading() {
  const heading = navData.heading;
  if (heading !== null) {
    const degrees = radiansToDegrees(heading);
    document.getElementById('heading').textContent = Math.round(degrees);
    document.getElementById('heading-cardinal').textContent = degreesToCardinal(degrees);
    document.getElementById('card-heading').classList.remove('no-data');
  } else {
    document.getElementById('heading').textContent = '--';
    document.getElementById('heading-cardinal').textContent = '--';
    document.getElementById('card-heading').classList.add('no-data');
  }
}

function updateDepth() {
  const depth = navData.depth;
  if (depth !== null) {
    const depthFt = depth * 3.28084; // Signal K depth is meters; Units.depth expects feet
    document.getElementById('depth').textContent =
      (typeof Units !== 'undefined') ? Units.depth.toDisplay(depthFt) : depth.toFixed(1) + ' m';
    document.getElementById('card-depth').classList.remove('no-data');
  } else {
    document.getElementById('depth').textContent = '--';
    document.getElementById('card-depth').classList.add('no-data');
  }
}

function updateGPSStatus() {
  const satellites = navData.gnss.satellites;
  const hdop = navData.gnss.horizontalDilution;
  const quality = navData.gnss.methodQuality;

  if (satellites !== null) {
    document.getElementById('satellites').textContent = satellites;
    const satElement = document.getElementById('gps-satellites');
    if (satellites >= 4) {
      satElement.classList.add('good');
    } else {
      satElement.classList.remove('good');
    }
  } else {
    document.getElementById('satellites').textContent = '--';
  }

  if (hdop !== null) {
    document.getElementById('hdop').textContent = hdop.toFixed(1);
    const hdopElement = document.getElementById('gps-hdop');
    if (hdop < 2) {
      hdopElement.classList.add('good');
    } else {
      hdopElement.classList.remove('good');
    }
  } else {
    document.getElementById('hdop').textContent = '--';
  }

  if (quality !== null) {
    const qualityText = getFixQualityText(quality);
    document.getElementById('fix-quality').textContent = qualityText;
    const fixElement = document.getElementById('gps-fix');
    if (quality === 'DGNSS' || quality === 'RTK') {
      fixElement.classList.add('good');
    } else if (quality === 'GNSS') {
      fixElement.classList.add('good');
    } else {
      fixElement.classList.remove('good');
    }
  } else {
    document.getElementById('fix-quality').textContent = '--';
  }
}

function updateAISTargets() {
  const container = document.getElementById('ais-container');
  const noTargets = document.getElementById('no-targets');

  const targetList = Object.entries(aisTargets).filter(([mmsi, data]) => {
    return data.name && data.position;
  });

  if (targetList.length === 0) {
    noTargets.style.display = 'block';
    return;
  }

  noTargets.style.display = 'none';

  // Calculate distance and bearing to each target
  const ownPos = navData.position;
  if (ownPos.latitude && ownPos.longitude) {
    targetList.forEach(([mmsi, data]) => {
      const dist = calculateDistance(
        ownPos.latitude, ownPos.longitude,
        data.position.latitude, data.position.longitude
      );
      const bearing = calculateBearing(
        ownPos.latitude, ownPos.longitude,
        data.position.latitude, data.position.longitude
      );
      data.distance = dist;
      data.bearing = bearing;
    });

    // Sort by distance
    targetList.sort((a, b) => a[1].distance - b[1].distance);
  }

  // Render targets
  container.innerHTML = targetList.map(([mmsi, data]) => {
    const sog = data.sog ? (data.sog * 1.944).toFixed(1) : '--';
    const cog = data.cog ? Math.round(radiansToDegrees(data.cog)) : '--';
    const dist = data.distance !== undefined ? data.distance.toFixed(2) : '--';
    const bearing = data.bearing !== undefined ? Math.round(data.bearing) : '--';

    return `
      <div class="ais-target">
        <div class="ais-name">🚢 ${data.name || 'Unknown'}</div>
        <div class="ais-info">
          <div class="ais-info-item">
            <div class="ais-info-label">MMSI</div>
            <div class="ais-info-value">${mmsi}</div>
          </div>
          <div class="ais-info-item">
            <div class="ais-info-label">Distance</div>
            <div class="ais-info-value">${dist} nm</div>
          </div>
          <div class="ais-info-item">
            <div class="ais-info-label">Bearing</div>
            <div class="ais-info-value">${bearing}°</div>
          </div>
          <div class="ais-info-item">
            <div class="ais-info-label">Speed</div>
            <div class="ais-info-value">${sog} kts</div>
          </div>
          <div class="ais-info-item">
            <div class="ais-info-label">Course</div>
            <div class="ais-info-value">${cog}°</div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function updateDataAge() {
  if (lastDataTime) {
    const ageSeconds = Math.floor((new Date() - lastDataTime) / 1000);
    const ageElement = document.getElementById('data-age');
    document.getElementById('data-age').textContent = ageSeconds + 's';

    const ageStatusElement = document.getElementById('gps-age');
    if (ageSeconds < 2) {
      ageStatusElement.classList.add('good');
    } else {
      ageStatusElement.classList.remove('good');
    }
  }
}

// Helper functions
function formatLatitude(lat) {
  const dir = lat >= 0 ? 'N' : 'S';
  const absLat = Math.abs(lat);
  const deg = Math.floor(absLat);
  const min = (absLat - deg) * 60;
  return `${deg}°${min.toFixed(3)}' ${dir}`;
}

function formatLongitude(lon) {
  const dir = lon >= 0 ? 'E' : 'W';
  const absLon = Math.abs(lon);
  const deg = Math.floor(absLon);
  const min = (absLon - deg) * 60;
  return `${deg}°${min.toFixed(3)}' ${dir}`;
}

function radiansToDegrees(radians) {
  return radians * 180 / Math.PI;
}

function degreesToCardinal(degrees) {
  const cardinals = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const index = Math.round(degrees / 22.5) % 16;
  return cardinals[index];
}

function getFixQualityText(quality) {
  const qualityMap = {
    'no GPS': 'No Fix',
    'GNSS': 'GPS',
    'DGNSS': 'DGPS',
    'RTK': 'RTK',
    'Float RTK': 'Float RTK'
  };
  return qualityMap[quality] || quality;
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  // Haversine formula
  const R = 3440.065; // Earth radius in nautical miles
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

function calculateBearing(lat1, lon1, lat2, lon2) {
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const y = Math.sin(dLon) * Math.cos(lat2 * Math.PI / 180);
  const x = Math.cos(lat1 * Math.PI / 180) * Math.sin(lat2 * Math.PI / 180) -
            Math.sin(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.cos(dLon);
  const bearing = Math.atan2(y, x) * 180 / Math.PI;
  return (bearing + 360) % 360;
}

function launchOpenCPN() {
  alert('🗺️ Launching OpenCPN Chart Plotter...\n\nOpenCPN will open on the desktop. Access it via VNC or connect a monitor to the Raspberry Pi.\n\nOpenCPN automatically connects to Signal K for real-time boat data.');

  // Launch OpenCPN via remote command
  fetch('/cgi-bin/launch-opencpn.sh')
    .then(response => {
      if (!response.ok) {
        console.log('OpenCPN launch via HTTP failed, trying alternative method');
      }
    })
    .catch(error => {
      console.log('OpenCPN launch error:', error);
    });
}

function refreshData() {
  location.reload();
}

function goBack() {
  window.location.href = '/';
}