function restartSignalK() {
  if (!confirm('Restart Signal K? Engine data will pause briefly.')) return;
  fetch('/settings/action/restart-signalk', {method:'POST'})
    .then(r => r.json())
    .then(d => showToast(d.success ? '✓ Signal K restarting...' : '✗ ' + d.error));
}