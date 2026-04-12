#!/bin/bash
# Runs on the VM — installs CRM backup-status files to /home/d3kos-admin/
set -e

CRM_DIR=/home/d3kos-admin

echo "Installing to $CRM_DIR ..."

cp /tmp/app_patched.py "$CRM_DIR/app.py"
echo "  app.py installed"

mkdir -p "$CRM_DIR/templates"
cp /tmp/backup_status.html "$CRM_DIR/templates/backup_status.html"
echo "  templates/backup_status.html installed"

# Add Backup Status nav link to base.html (idempotent)
python3 << 'PYEOF'
import sys
base = '/home/d3kos-admin/templates/base.html'
try:
    with open(base) as f:
        content = f.read()
    if 'backup_status' in content:
        print('  base.html nav link already present (skipped)')
        sys.exit(0)
    marker = "url_for('publish_update')"
    if marker not in content:
        print('  WARNING: publish_update anchor not found in base.html — nav link not added')
        sys.exit(0)
    new_link = "            <li><a href=\"{{ url_for('backup_status') }}\" {% if request.endpoint == 'backup_status' %}class=\"active\"{% endif %}>Backup Status</a></li>"
    pos = content.find(marker)
    line_end = content.find('\n', pos) + 1
    content = content[:line_end] + new_link + '\n' + content[line_end:]
    with open(base, 'w') as f:
        f.write(content)
    print('  base.html nav link added')
except Exception as e:
    print(f'  ERROR patching base.html: {e}')
PYEOF

# Find and restart the CRM service
SERVICE=$(systemctl list-units --type=service 2>/dev/null | grep -i "crm\|admin" | awk '{print $1}' | head -1)
if [ -n "$SERVICE" ]; then
    systemctl restart "$SERVICE"
    echo "  Restarted: $SERVICE"
else
    # Try common names directly
    systemctl restart admin-crm.service 2>/dev/null && echo "  Restarted: admin-crm.service" || \
    systemctl restart d3kos-crm.service  2>/dev/null && echo "  Restarted: d3kos-crm.service"  || \
    echo "  WARNING: Could not find CRM service — start manually: sudo systemctl restart admin-crm.service"
fi

echo "DONE"
