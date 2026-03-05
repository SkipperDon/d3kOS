// === Benchmark JavaScript ===

let currentTest = null;
let tests = [];
let baseline = null;
let testTimer = null;
let testDuration = 30 * 60; // 30 minutes in seconds
let signalKConnected = false;
let signalKSocket = null;
let metricsUpdateInterval = null;

// Engine metrics
let metrics = {
  rpm: 0,
  boost: 143,
  temp: null,
  oil: null,
  voltage: null,
  trim: 0
};

// Thresholds for warnings/critical
const thresholds = {
  rpm: { warning: 3000, critical: 3500 },
  boost: { warning: 200, critical: 250 },
  temp: { warning: 95, critical: 105 },
  oil: { warning: 150, critical: 100 },
  voltage: { warning: 11, critical: 10 }
};

// Load data from localStorage
function loadData() {
  const savedTests = localStorage.getItem('d3kos-benchmark-tests');
  if (savedTests) {
    tests = JSON.parse(savedTests);
  }

  const savedBaseline = localStorage.getItem('d3kos-benchmark-baseline');
  if (savedBaseline) {
    baseline = JSON.parse(savedBaseline);
    displayBaseline();
  }

  const savedCurrentTest = localStorage.getItem('d3kos-current-benchmark');
  if (savedCurrentTest) {
    currentTest = JSON.parse(savedCurrentTest);
    resumeTest();
  }

  updateDisplay();
}

// Save data to localStorage
function saveData() {
  localStorage.setItem('d3kos-benchmark-tests', JSON.stringify(tests));
  if (baseline) {
    localStorage.setItem('d3kos-benchmark-baseline', JSON.stringify(baseline));
  }
  if (currentTest) {
    localStorage.setItem('d3kos-current-benchmark', JSON.stringify(currentTest));
  } else {
    localStorage.removeItem('d3kos-current-benchmark');
  }
}

// Start benchmark test
function startTest() {
  if (currentTest) {
    alert('A test is already in progress!');
    return;
  }

  currentTest = {
    id: Date.now(),
    startTime: new Date().toISOString(),
    endTime: null,
    duration: 0,
    samples: [],
    avgMetrics: {}
  };

  document.getElementById('btn-start-test').disabled = true;
  document.getElementById('btn-stop-test').disabled = false;
  document.getElementById('btn-save-baseline').disabled = true;

  document.getElementById('test-status').classList.remove('inactive');
  document.getElementById('test-status').classList.add('active');
  document.getElementById('status-text').textContent = 'Test In Progress';

  startTestTimer();
  saveData();
}

// Stop benchmark test
function stopTest() {
  if (!currentTest) return;

  if (confirm('Stop the test? This will save the current data.')) {
    currentTest.endTime = new Date().toISOString();
    currentTest.duration = Math.floor((new Date(currentTest.endTime) - new Date(currentTest.startTime)) / 1000);

    // Calculate averages
    calculateAverages();

    tests.unshift(currentTest);
    currentTest = null;

    document.getElementById('btn-start-test').disabled = false;
    document.getElementById('btn-stop-test').disabled = true;
    document.getElementById('btn-save-baseline').disabled = false;

    document.getElementById('test-status').classList.remove('active');
    document.getElementById('test-status').classList.add('inactive');
    document.getElementById('status-text').textContent = 'Test Completed';
    document.getElementById('test-description').textContent = 'Test data saved. You can now save this as your baseline.';

    stopTestTimer();
    saveData();
    updateDisplay();
  }
}

// Save current test as baseline
function saveBaseline() {
  if (tests.length === 0) {
    alert('No test data available to save as baseline!');
    return;
  }

  if (baseline && !confirm('This will replace your existing baseline. Continue?')) {
    return;
  }

  baseline = tests[0];
  displayBaseline();
  saveData();
  alert('Baseline saved successfully!');

  document.getElementById('btn-save-baseline').disabled = true;
}

// Resume test after page reload
function resumeTest() {
  document.getElementById('btn-start-test').disabled = true;
  document.getElementById('btn-stop-test').disabled = false;
  document.getElementById('btn-save-baseline').disabled = true;

  document.getElementById('test-status').classList.remove('inactive');
  document.getElementById('test-status').classList.add('active');
  document.getElementById('status-text').textContent = 'Test In Progress';

  startTestTimer();
}

// Test timer
function startTestTimer() {
  stopTestTimer();
  testTimer = setInterval(updateTestTimer, 1000);
  metricsUpdateInterval = setInterval(sampleMetrics, 5000); // Sample every 5 seconds
}

function stopTestTimer() {
  if (testTimer) {
    clearInterval(testTimer);
    testTimer = null;
  }
  if (metricsUpdateInterval) {
    clearInterval(metricsUpdateInterval);
    metricsUpdateInterval = null;
  }
}

// Update test timer
function updateTestTimer() {
  if (!currentTest) return;

  const now = Date.now();
  const start = new Date(currentTest.startTime).getTime();
  const elapsed = Math.floor((now - start) / 1000);
  const remaining = Math.max(0, testDuration - elapsed);

  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;

  document.getElementById('test-timer').textContent =
    `${minutes}:${seconds.toString().padStart(2, '0')}`;

  const progress = (elapsed / testDuration) * 100;
  document.getElementById('progress-bar').style.width = Math.min(progress, 100) + '%';

  // Auto-stop at 30 minutes
  if (remaining === 0) {
    stopTest();
  }
}

// Sample current metrics
function sampleMetrics() {
  if (!currentTest) return;

  const sample = {
    timestamp: new Date().toISOString(),
    rpm: metrics.rpm,
    boost: metrics.boost,
    temp: metrics.temp,
    oil: metrics.oil,
    voltage: metrics.voltage,
    trim: metrics.trim
  };

  currentTest.samples.push(sample);
  saveData();
}

// Calculate average metrics
function calculateAverages() {
  if (!currentTest || currentTest.samples.length === 0) return;

  const totals = {
    rpm: 0,
    boost: 0,
    temp: 0,
    oil: 0,
    voltage: 0,
    trim: 0
  };

  currentTest.samples.forEach(sample => {
    Object.keys(totals).forEach(key => {
      totals[key] += sample[key] || 0;
    });
  });

  const count = currentTest.samples.length;
  currentTest.avgMetrics = {
    rpm: (totals.rpm / count).toFixed(0),
    boost: (totals.boost / count).toFixed(0),
    temp: (totals.temp / count).toFixed(1),
    oil: (totals.oil / count).toFixed(0),
    voltage: (totals.voltage / count).toFixed(1),
    trim: (totals.trim / count).toFixed(0)
  };
}

// Display baseline info
function displayBaseline() {
  if (!baseline) return;

  const date = new Date(baseline.startTime);
  document.getElementById('baseline-summary').textContent =
    `Avg RPM: ${baseline.avgMetrics.rpm}, Boost: ${baseline.avgMetrics.boost} kPa, Temp: ${baseline.avgMetrics.temp}°C`;
  document.getElementById('baseline-date').textContent =
    `Established: ${date.toLocaleString()}`;
  document.getElementById('baseline-info').style.display = 'block';
}

// Update metric displays
function updateMetricDisplays() {
  document.getElementById('metric-rpm').textContent = metrics.rpm;
  document.getElementById('metric-boost').textContent = metrics.boost;
  document.getElementById('metric-temp').textContent = metrics.temp !== null ? metrics.temp : '--';
  document.getElementById('metric-oil').textContent = metrics.oil !== null ? metrics.oil : '--';
  document.getElementById('metric-voltage').textContent = metrics.voltage !== null ? metrics.voltage.toFixed(1) : '--';
  document.getElementById('metric-trim').textContent = (metrics.trim * 100).toFixed(0);

  // Update card states based on thresholds
  updateCardState('card-rpm', metrics.rpm, thresholds.rpm);
  updateCardState('card-boost', metrics.boost, thresholds.boost);
  if (metrics.temp !== null) updateCardState('card-temp', metrics.temp, thresholds.temp);
  if (metrics.oil !== null) updateCardState('card-oil', metrics.oil, thresholds.oil, true); // Reverse for oil pressure
  if (metrics.voltage !== null) updateCardState('card-voltage', metrics.voltage, thresholds.voltage, true); // Reverse for voltage
}

// Update card state (warning/critical)
function updateCardState(cardId, value, threshold, reverse = false) {
  const card = document.getElementById(cardId);
  card.classList.remove('warning', 'critical');

  if (reverse) {
    if (value <= threshold.critical) {
      card.classList.add('critical');
    } else if (value <= threshold.warning) {
      card.classList.add('warning');
    }
  } else {
    if (value >= threshold.critical) {
      card.classList.add('critical');
    } else if (value >= threshold.warning) {
      card.classList.add('warning');
    }
  }
}

// Update display
function updateDisplay() {
  updateTestList();
  updateMetricDisplays();
}

// Update test list
function updateTestList() {
  const testList = document.getElementById('test-list');

  if (tests.length === 0) {
    testList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔬</div>
        <div class="empty-state-text">No tests recorded yet. Run your first baseline test!</div>
      </div>
    `;
    return;
  }

  testList.innerHTML = tests.map((test, index) => {
    const date = new Date(test.startTime);
    const duration = Math.floor(test.duration / 60);

    return `
      <div class="test-item" onclick="viewTest(${index})">
        <div class="test-date">
          ${date.toLocaleDateString()}<br>
          ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
        <div class="test-details">
          <div class="test-detail">
            <span class="test-detail-label">Duration</span>
            <span class="test-detail-value">${duration} min</span>
          </div>
          <div class="test-detail">
            <span class="test-detail-label">Avg RPM</span>
            <span class="test-detail-value">${test.avgMetrics.rpm || '--'}</span>
          </div>
          <div class="test-detail">
            <span class="test-detail-label">Avg Boost</span>
            <span class="test-detail-value">${test.avgMetrics.boost || '--'} kPa</span>
          </div>
          <div class="test-detail">
            <span class="test-detail-label">Samples</span>
            <span class="test-detail-value">${test.samples.length}</span>
          </div>
        </div>
        <div class="test-actions">
          <button class="btn btn-small" onclick="deleteTest(${index}); event.stopPropagation();">Delete</button>
        </div>
      </div>
    `;
  }).join('');
}

// View test details
function viewTest(index) {
  const test = tests[index];
  const date = new Date(test.startTime);
  const duration = Math.floor(test.duration / 60);

  alert(`Test Details\n\nDate: ${date.toLocaleString()}\nDuration: ${duration} minutes\nSamples: ${test.samples.length}\n\nAverage Metrics:\nRPM: ${test.avgMetrics.rpm || '--'}\nBoost: ${test.avgMetrics.boost || '--'} kPa\nTemp: ${test.avgMetrics.temp || '--'}°C\nOil Pressure: ${test.avgMetrics.oil || '--'} kPa\nVoltage: ${test.avgMetrics.voltage || '--'} V`);
}

// Delete test
function deleteTest(index) {
  if (confirm('Delete this test?')) {
    tests.splice(index, 1);
    saveData();
    updateDisplay();
  }
}

// Export data
function exportData() {
  const data = {
    tests: tests,
    baseline: baseline,
    exportDate: new Date().toISOString()
  };

  const dataStr = JSON.stringify(data, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `d3kos-benchmark-${new Date().toISOString().split('T')[0]}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

// Go back to main menu
function goBack() {
  if (currentTest && !confirm('Test in progress! Exit anyway?')) {
    return;
  }
  window.location.href = '/';
}

// Connect to Signal K
function connectSignalK() {
  try {
    signalKSocket = new WebSocket('ws://localhost:8085/signalk/v1/stream?subscribe=none');

    signalKSocket.onopen = () => {
      console.log('Signal K connected');
      signalKConnected = true;
      document.getElementById('connection-status').classList.add('connected');
      document.getElementById('connection-text').textContent = 'Connected to Signal K';

      // Subscribe to engine data
      signalKSocket.send(JSON.stringify({
        context: 'vessels.self',
        subscribe: [
          { path: 'propulsion.port.revolutions', period: 1000 },
          { path: 'propulsion.port.boostPressure', period: 1000 },
          { path: 'propulsion.port.temperature', period: 1000 },
          { path: 'propulsion.port.oilPressure', period: 1000 },
          { path: 'electrical.batteries.*.voltage', period: 1000 },
          { path: 'propulsion.port.drive.trimState', period: 1000 }
        ]
      }));
    };

    signalKSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.updates) {
        data.updates.forEach(update => {
          update.values.forEach(value => {
            if (value.path === 'propulsion.port.revolutions') {
              metrics.rpm = Math.round(value.value * 60); // Hz to RPM
            } else if (value.path === 'propulsion.port.boostPressure') {
              metrics.boost = Math.round(value.value / 1000); // Pa to kPa
            } else if (value.path === 'propulsion.port.temperature') {
              metrics.temp = (value.value - 273.15).toFixed(1); // K to C
            } else if (value.path === 'propulsion.port.oilPressure') {
              metrics.oil = Math.round(value.value / 1000); // Pa to kPa
            } else if (value.path.includes('voltage')) {
              metrics.voltage = value.value;
            } else if (value.path === 'propulsion.port.drive.trimState') {
              metrics.trim = value.value;
            }
          });
        });
        updateMetricDisplays();
      }
    };

    signalKSocket.onerror = () => {
      console.error('Signal K connection error');
      signalKConnected = false;
    };

    signalKSocket.onclose = () => {
      console.log('Signal K disconnected');
      signalKConnected = false;
      document.getElementById('connection-status').classList.remove('connected');
      document.getElementById('connection-text').textContent = 'Performance Testing & Baseline Establishment';

      // Reconnect after 5 seconds
      setTimeout(connectSignalK, 5000);
    };
  } catch (error) {
    console.error('Failed to connect to Signal K:', error);
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  loadData();
  connectSignalK();
  updateMetricDisplays();

  // Update metrics display every second
  setInterval(updateMetricDisplays, 1000);
});