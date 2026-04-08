# ── Failure Intelligence Routes — insert before `if __name__ == '__main__':` in app.py ──
# v0.9.8 FI3 — Issue Lifecycle Dashboard
#
# INTEGRATION STEPS:
#
# 1. Add helper near proxy_call() in app.py:
#
#   def proxy_call_issues(payload):
#       """Proxy to issue-api.php — uses X-Admin-Key auth (same as admin-api.php)."""
#       try:
#           r = requests.get(
#               config["proxy_url"].replace("admin-api.php", "issue-api.php"),
#               params=payload,
#               headers={"X-Admin-Key": config["admin_api_key"]},
#               timeout=10,
#           )
#           r.raise_for_status()
#           return r.json()
#       except Exception as e:
#           app.logger.error(f"proxy_call_issues error: {e}")
#           return None
#
#   def proxy_post_issues(payload):
#       """POST to issue-api.php."""
#       try:
#           r = requests.post(
#               config["proxy_url"].replace("admin-api.php", "issue-api.php"),
#               json=payload,
#               headers={"X-Admin-Key": config["admin_api_key"]},
#               timeout=10,
#           )
#           r.raise_for_status()
#           return r.json()
#       except Exception as e:
#           app.logger.error(f"proxy_post_issues error: {e}")
#           return None
#
# 2. Add "failures.html" to templates/ directory on VM.
#
# 3. Add nav link in base.html:
#    <a href="{{ url_for('failures') }}">Failure Intel</a>


@app.route('/failures')
@login_required
def failures():
    status = request.args.get('status', '')
    page   = max(1, request.args.get('page', 1, type=int))

    params = {'action': 'list', 'page': page}
    if status:
        params['status'] = status

    data = proxy_call_issues(params)

    stats_data = proxy_call_issues({'action': 'stats'})
    stats = stats_data.get('stats', {}) if stats_data else {}

    return render_template(
        'failures.html',
        issue          = None,
        issues         = data.get('issues', []) if data else [],
        total          = data.get('total', 0) if data else 0,
        page           = data.get('page', 1) if data else 1,
        pages          = data.get('pages', 1) if data else 1,
        current_status = status,
        stats          = stats,
    )


@app.route('/failure/<int:issue_id>')
@login_required
def failure_detail(issue_id):
    data = proxy_call_issues({'action': 'get', 'id': issue_id})
    if not data or not data.get('success'):
        return 'Issue not found', 404
    return render_template(
        'failures.html',
        issue       = data.get('issue'),
        affected    = data.get('affected', []),
        resolutions = data.get('resolutions', []),
        reports     = data.get('reports', []),
        issues      = None,
        stats       = {},
    )


@app.route('/failure/<int:issue_id>/update', methods=['POST'])
@login_required
def failure_update(issue_id):
    payload = {'action': 'update', 'id': issue_id}

    new_status = request.form.get('status', '')
    if new_status:
        payload['status'] = new_status

    version = request.form.get('fixed_in_version', '').strip()
    if version:
        payload['fixed_in_version'] = version

    validation = request.form.get('validation_device', '').strip()
    if validation:
        payload['validation_device'] = validation

    proxy_post_issues(payload)
    return redirect(url_for('failure_detail', issue_id=issue_id))
