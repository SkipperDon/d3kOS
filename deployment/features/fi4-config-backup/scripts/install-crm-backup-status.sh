#!/bin/bash
# Runs on the VM — finds the CRM app_patched.py and installs backup_status files
set -e

echo "--- Searching for CRM app location ---"
CRM_APP=$(find /home /opt /srv /var/www 2>/dev/null -name "app_patched.py" | head -1)

if [ -z "$CRM_APP" ]; then
    echo "ERROR: Cannot find app_patched.py on this VM."
    echo "Manual check: ls /home/ and ls /home/d3kos-admin/"
    ls /home/ 2>/dev/null || true
    ls /home/d3kos-admin/ 2>/dev/null || true
    exit 1
fi

CRM_DIR=$(dirname "$CRM_APP")
echo "Found CRM at: $CRM_DIR"

cp /tmp/app_patched.py "$CRM_DIR/app_patched.py"
echo "Installed app_patched.py"

mkdir -p "$CRM_DIR/templates"
cp /tmp/backup_status.html "$CRM_DIR/templates/backup_status.html"
echo "Installed backup_status.html"

SERVICE=$(systemctl list-units --type=service 2>/dev/null | grep -i "crm\|admin" | awk '{print $1}' | head -1)
if [ -n "$SERVICE" ]; then
    systemctl restart "$SERVICE"
    echo "Restarted service: $SERVICE"
else
    echo "WARNING: Could not find admin-crm service. Restart manually."
fi

echo "DONE"
