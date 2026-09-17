# ── Fleet Version Routes — insert before `if __name__ == '__main__':` in app.py ──
# v0.9.8 S33 — Fleet version visibility dashboard
# v0.9.9.5 D23 — OTA push/cancel/history routes added S169
#
# INTEGRATION STEPS:
#
# 1. Add helper near other proxy helpers in app.py:
#
#   def proxy_call_versions(params):
#       """GET to version-api.php — Bearer auth."""
#       try:
#           r = _requests.get(
#               config["proxy_url"] + "version-api.php",  # BUG-56: base-directory, no .replace()
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
#   def proxy_call_ota(params):
#       """GET to ota-admin.php — Bearer auth."""
#       try:
#           r = _requests.get(
#               config["proxy_url"] + "ota-admin.php",
#               params=params,
#               headers=_issues_headers,
#               timeout=10,
#           )
#           r.raise_for_status()
#           return r.json()
#       except Exception as e:
#           app.logger.error(f"proxy_call_ota error: {e}")
#           return None
#
#   def proxy_post_ota(payload):
#       """POST to ota-admin.php — Bearer auth."""
#       try:
#           r = _requests.post(
#               config["proxy_url"] + "ota-admin.php",
#               json=payload,
#               headers=_issues_headers,
#               timeout=15,
#           )
#           r.raise_for_status()
#           return r.json()
#       except Exception as e:
#           app.logger.error(f"proxy_post_ota error: {e}")
#           return None
#
# 2. Add "fleet_versions.html" to templates/ on VM.
# 3. Add nav link in base.html: <a href="{{ url_for('fleet_versions') }}">Fleet Versions</a>


@app.route('/fleet-versions')
@login_required
def fleet_versions():
    data     = proxy_call_versions({'action': 'fleet'})
    dist     = proxy_call_versions({'action': 'distribution'})
    ota_data = proxy_call_ota({'action': 'status_all'})
    ota_status = ota_data.get('devices', {}) if ota_data else {}
    return render_template(
        'fleet_versions.html',
        devices      = data.get('devices', []) if data else [],
        summary      = data.get('summary', {}) if data else {},
        latest_ver   = data.get('latest_version', '') if data else '',
        distribution = dist.get('distribution', []) if dist else [],
        ota_status   = ota_status,
        error        = None if data else 'Could not load fleet version data.',
    )


@app.route('/ota-push', methods=['POST'])
@login_required
def ota_push():
    payload = {
        'action':        'push',
        'pi_id':         request.form.get('pi_id', '').strip(),
        'version':       request.form.get('version', '').strip(),
        'download_url':  request.form.get('download_url', '').strip(),
        'sha256':        request.form.get('sha256', '').strip(),
        'release_notes': request.form.get('release_notes', '').strip(),
    }
    if not all([payload['pi_id'], payload['version'], payload['download_url'], payload['sha256']]):
        return jsonify({'success': False, 'error': 'All fields required'}), 400

    result = proxy_post_ota(payload)
    if result and result.get('success'):
        return jsonify(result)
    err = result.get('error', 'unknown') if result else 'no response from HostPapa'
    return jsonify({'success': False, 'error': err}), 500


@app.route('/ota-cancel', methods=['POST'])
@login_required
def ota_cancel():
    command_id = request.json.get('command_id') if request.is_json else request.form.get('command_id')
    result = proxy_post_ota({'action': 'cancel', 'command_id': int(command_id or 0)})
    if result and result.get('success'):
        return jsonify(result)
    return jsonify({'success': False, 'error': 'cancel failed'}), 500


@app.route('/ota-history')
@login_required
def ota_history():
    pi_id = request.args.get('pi_id', '').strip()
    if not pi_id:
        return jsonify({'success': False, 'error': 'pi_id required'}), 400
    result = proxy_call_ota({'action': 'history', 'pi_id': pi_id})
    if result:
        return jsonify(result)
    return jsonify({'success': False, 'error': 'history fetch failed'}), 500


@app.route('/ota-fetch-sha256')
@login_required
def ota_fetch_sha256():
    """Server-side fetch of companion .sha256 file — avoids browser CORS."""
    url = request.args.get('url', '').strip()
    if not url.startswith('https://github.com/'):
        return jsonify({'success': False, 'error': 'url must be a github.com URL'}), 400
    sha_url = url + '.sha256'
    try:
        r = _requests.get(sha_url, timeout=10, headers={'User-Agent': 'd3kOS-admin/1.0'})
        r.raise_for_status()
        sha = r.text.strip().split()[0]  # "abc123  filename.tar.gz" → take first token
        if len(sha) == 64 and all(c in '0123456789abcdefABCDEF' for c in sha):
            return jsonify({'success': True, 'sha256': sha.lower()})
        return jsonify({'success': False, 'error': 'unexpected sha256 file format'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
