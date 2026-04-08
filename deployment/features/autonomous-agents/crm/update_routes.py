# ── Update Publisher Routes — insert before `if __name__ == '__main__':` in app.py ──
# v0.9.8 S32 — Update lifecycle management
#
# INTEGRATION STEPS:
#
# 1. Add helper near other proxy helpers in app.py:
#
#   _publish_url     = config["proxy_url"].replace("admin-api.php", "update-publish.php")
#   _publish_headers = {"Authorization": f"Bearer {config['proxy_api_key']}", "Content-Type": "application/json"}
#
#   def proxy_call_publish(params):
#       try:
#           r = _requests.get(_publish_url, params=params, headers=_publish_headers, timeout=10)
#           r.raise_for_status()
#           return r.json()
#       except Exception as e:
#           app.logger.error(f"proxy_call_publish error: {e}")
#           return None
#
#   def proxy_post_publish(payload):
#       try:
#           r = _requests.post(_publish_url, json=payload, headers=_publish_headers, timeout=15)
#           r.raise_for_status()
#           return r.json()
#       except Exception as e:
#           app.logger.error(f"proxy_post_publish error: {e}")
#           return None
#
# 2. Add "publish_update.html" to templates/ on VM.
# 3. Add nav link in base.html: <a href="{{ url_for('publish_update') }}">Publish Update</a>


@app.route('/publish-update', methods=['GET', 'POST'])
@login_required
def publish_update():
    message = None
    error   = None

    if request.method == 'POST':
        action = request.form.get('action', 'publish')

        if action == 'deactivate':
            vid = request.form.get('id', '')
            result = proxy_post_publish({'action': 'deactivate', 'id': int(vid)})
            if result and result.get('success'):
                message = result.get('message', 'Version deactivated.')
            else:
                error = 'Deactivate failed.'

        elif action == 'reactivate':
            vid = request.form.get('id', '')
            result = proxy_post_publish({'action': 'reactivate', 'id': int(vid)})
            if result and result.get('success'):
                message = result.get('message', 'Version reactivated.')
            else:
                error = 'Reactivate failed.'

        else:  # publish
            services_raw = request.form.get('services_to_restart', '').strip()
            services = [s.strip() for s in services_raw.split(',') if s.strip()]

            payload = {
                'action':              'publish',
                'update_type':         request.form.get('update_type', 'incremental'),
                'version':             request.form.get('version', '').strip(),
                'url':                 request.form.get('url', '').strip(),
                'checksum':            request.form.get('checksum', '').strip(),
                'released':            request.form.get('released', '').strip(),
                't1_upgrade':          request.form.get('t1_upgrade') == '1',
                'services_to_restart': services,
                'release_notes':       request.form.get('release_notes', '').strip(),
            }

            if not payload['version']:
                error = 'Version is required.'
            else:
                result = proxy_post_publish(payload)
                if result and result.get('success'):
                    message = result.get('message', f"v{payload['version']} published.")
                else:
                    error = f"Publish failed: {result.get('error', 'unknown') if result else 'no response'}"

    # Always load current state and history
    current_data  = proxy_call_publish({'action': 'current'})
    history_data  = proxy_call_publish({'action': 'list'})
    current_inc   = current_data.get('incremental') if current_data else None
    current_major = current_data.get('major') if current_data else None
    history       = history_data.get('versions', []) if history_data else []

    return render_template(
        'publish_update.html',
        current_inc   = current_inc,
        current_major = current_major,
        history       = history,
        message       = message,
        error         = error,
    )
