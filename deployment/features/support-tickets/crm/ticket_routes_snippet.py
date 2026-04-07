# ── Support Ticket Routes — insert before `if __name__ == '__main__':` in app.py ──
# v0.9.7 Phase 2: notify_customer flag passed through on update
#
# NOTE: These routes proxy to admin-api-tickets.php (separate from admin-api.php).
# Add this helper near proxy_call() in app.py:
#
#   def proxy_call_tickets(payload):
#       """Proxy to admin-api-tickets.php — same auth pattern as proxy_call."""
#       try:
#           r = requests.post(
#               PROXY_BASE_URL.replace('admin-api.php', 'admin-api-tickets.php'),
#               json=payload,
#               headers={'X-Admin-Key': AMBOAT_ADMIN_API_KEY},
#               timeout=10,
#           )
#           r.raise_for_status()
#           return r.json()
#       except Exception as e:
#           app.logger.error(f'proxy_call_tickets error: {e}')
#           return None
#
# OR: if proxy_call() already accepts a url parameter, pass the tickets endpoint.


@app.route('/tickets')
def tickets():
    status  = request.args.get('status', '')
    page    = int(request.args.get('page', 1))

    payload = {'action': 'get_tickets', 'page': page}
    if status:
        payload['status'] = status

    data = proxy_call_tickets(payload)

    # Open count for badge on tabs
    open_data  = proxy_call_tickets({'action': 'get_tickets', 'status': 'open', 'page': 1})
    open_count = open_data.get('total', 0) if open_data else 0

    return render_template(
        'tickets.html',
        ticket         = None,
        tickets        = data.get('tickets', []) if data else [],
        total          = data.get('total', 0) if data else 0,
        page           = data.get('page', 1) if data else 1,
        pages          = data.get('pages', 1) if data else 1,
        current_status = status,
        open_count     = open_count,
    )


@app.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    data = proxy_call_tickets({'action': 'get_ticket', 'ticket_id': ticket_id})
    if not data or not data.get('success'):
        return 'Ticket not found', 404
    return render_template('tickets.html', ticket=data.get('ticket'))


@app.route('/ticket/<int:ticket_id>/update', methods=['POST'])
def ticket_update(ticket_id):
    payload = {
        'action':          'update_ticket',
        'ticket_id':       ticket_id,
        'status':          request.form.get('status', ''),
        'admin_note':      request.form.get('admin_note', ''),
        'notify_customer': request.form.get('notify_customer') == '1',
    }
    proxy_call_tickets(payload)
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))
