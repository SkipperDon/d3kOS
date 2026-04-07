#!/usr/bin/env python3
"""
patch-vm-app.py — Run ON the VM to patch app.py and base.html for v0.9.7 tickets.
Upload this file to the VM via pscp.exe, then run with plink.
"""

import re
import shutil
from datetime import datetime

APP_PY    = '/home/d3kos-admin/app.py'
BASE_HTML = '/home/d3kos-admin/templates/base.html'
TS = datetime.now().strftime('%Y%m%d_%H%M%S')

TICKETS_BLOCK = '''

# ── Support Ticket Routes (v0.9.7) ────────────────────────────────────────────

def proxy_call_tickets(payload):
    """Proxy to admin-api-tickets.php on HostPapa."""
    import requests as _req
    try:
        # Derive tickets URL from the existing proxy URL constant
        base = PROXY_URL if 'PROXY_URL' in dir() else ADMIN_API_URL
        url  = re.sub(r'admin-api\\.php', 'admin-api-tickets.php', base)
        key  = ADMIN_API_KEY if 'ADMIN_API_KEY' in dir() else AMBOAT_ADMIN_API_KEY
        r    = _req.post(url, json=payload, headers={'X-Admin-Key': key}, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        app.logger.error(f'proxy_call_tickets error: {e}')
        return None


@app.route('/tickets')
def tickets():
    status = request.args.get('status', '')
    page   = int(request.args.get('page', 1))
    payload = {'action': 'get_tickets', 'page': page}
    if status:
        payload['status'] = status
    data       = proxy_call_tickets(payload)
    open_data  = proxy_call_tickets({'action': 'get_tickets', 'status': 'open', 'page': 1})
    open_count = (open_data or {}).get('total', 0)
    return render_template(
        'tickets.html',
        ticket         = None,
        tickets        = (data or {}).get('tickets', []),
        total          = (data or {}).get('total', 0),
        page           = (data or {}).get('page', 1),
        pages          = (data or {}).get('pages', 1),
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
    proxy_call_tickets({
        'action':     'update_ticket',
        'ticket_id':  ticket_id,
        'status':     request.form.get('status', ''),
        'admin_note': request.form.get('admin_note', ''),
    })
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))
'''

# ── Patch app.py ──────────────────────────────────────────────────────────────
with open(APP_PY, 'r') as f:
    lines = f.readlines()

if any('proxy_call_tickets' in l for l in lines):
    print('app.py already patched — skipping')
else:
    shutil.copy(APP_PY, f'{APP_PY}.bak_{TS}')
    print(f'Backup: {APP_PY}.bak_{TS}')

    # Find the __main__ line (handles both quote styles)
    main_idx = None
    for i, line in enumerate(lines):
        if re.search(r"""if\s+__name__\s*==\s*['"]__main__['"]""", line):
            main_idx = i
            break

    if main_idx is not None:
        lines.insert(main_idx, TICKETS_BLOCK)
        print(f'Inserted ticket routes before line {main_idx} (__main__ block)')
    else:
        # Last resort: append at end of file
        lines.append(TICKETS_BLOCK)
        print('WARNING: __main__ not found — appended routes at end of file')

    with open(APP_PY, 'w') as f:
        f.writelines(lines)
    print('app.py written.')

# ── Patch base.html ───────────────────────────────────────────────────────────
with open(BASE_HTML, 'r') as f:
    html = f.read()

if "url_for('tickets')" in html or 'url_for("tickets")' in html:
    print('base.html already patched — skipping')
else:
    shutil.copy(BASE_HTML, f'{BASE_HTML}.bak_{TS}')
    print(f'Backup: {BASE_HTML}.bak_{TS}')

    NAV = (
        '\n          <li><a href="{{ url_for(\'tickets\') }}"'
        ' {% if request.endpoint in (\'tickets\', \'ticket_detail\', \'ticket_update\') %}'
        'class="active"{% endif %}>Tickets</a></li>'
    )

    # Try after Fleets link first, then before DB Explorer, then before </ul>
    for pattern in [
        r"(<li><a href=\"\{\{ url_for\('fleets'\) \}\}\"[^<]*</a></li>)",
        r"(<li><a[^>]*>DB\s*Explorer)",
        r"(</ul>)",
    ]:
        m = re.search(pattern, html)
        if m:
            html = html[:m.end()] + NAV + html[m.end():]
            print(f'Inserted Tickets nav link (matched: {pattern[:30]}…)')
            break
    else:
        print('WARNING: could not find nav insertion point — add Tickets link manually')

    with open(BASE_HTML, 'w') as f:
        f.write(html)
    print('base.html written.')

print('\nDone. Restarting admin-crm.service…')
