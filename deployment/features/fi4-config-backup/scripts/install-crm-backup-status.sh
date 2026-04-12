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
