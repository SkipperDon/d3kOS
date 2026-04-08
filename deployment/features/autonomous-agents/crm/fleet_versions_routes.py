# ── Fleet Version Routes — insert before `if __name__ == '__main__':` in app.py ──
# v0.9.8 S33 — Fleet version visibility dashboard
#
# INTEGRATION STEPS:
#
# 1. Add helper near other proxy helpers in app.py:
#
#   def proxy_call_versions(params):
#       """GET to version-api.php — Bearer auth."""
#       try:
#           r = _requests.get(
#               config["proxy_url"].replace("admin-api.php", "version-api.php"),
#               params=params,
#               headers=_issues_headers,   # same Bearer + Content-Type
#               timeout=10,
#           )
#           r.raise_for_status()
#           return r.json()
#       except Exception as e:
#           app.logger.error(f"proxy_call_versions error: {e}")
#           return None
#
# 2. Add "fleet_versions.html" to templates/ on VM.
# 3. Add nav link in base.html: <a href="{{ url_for('fleet_versions') }}">Fleet Versions</a>


@app.route('/fleet-versions')
@login_required
def fleet_versions():
    data  = proxy_call_versions({'action': 'fleet'})
    dist  = proxy_call_versions({'action': 'distribution'})
    return render_template(
        'fleet_versions.html',
        devices      = data.get('devices', []) if data else [],
        summary      = data.get('summary', {}) if data else {},
        latest_ver   = data.get('latest_version', '') if data else '',
        distribution = dist.get('distribution', []) if dist else [],
        error        = None if data else 'Could not load fleet version data.',
    )
