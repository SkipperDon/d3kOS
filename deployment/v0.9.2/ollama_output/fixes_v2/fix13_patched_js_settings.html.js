// Replace alert-based functions with real API calls:

function restartSignalK() {
  if (!confirm('Restart Signal K? Engine data will pause briefly.')) return;
  fetch('/settings/action/restart-signalk', {method:'POST'})
    .then(r => r.json())
    .then(d => showToast(d.success ? '✓ Signal K restarting...' : '✗ ' + d.error));
}

function restartNodered() {
  if (!confirm('Restart Node-RED? Dashboard will reload.')) return;
  fetch('/settings/action/restart-nodered', {method:'POST'})
    .then(r => r.json())
    .then(d => showToast(d.success ? '✓ Node-RED restarting...' : '✗ ' + d.error));
}

function rebootSystem() {
  if (!confirm('Reboot the system now?')) return;
  fetch('/settings/action/reboot', {method:'POST'})
    .then(() => { showToast('🔄 Rebooting...'); setTimeout(() => location.reload(), 15000); });
}