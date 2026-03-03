#!/usr/bin/env bash
# d3kOS v0.9.2 — Full Deployment Script
# Deploys Metric/Imperial conversion system to the Pi.
# Usage: ./deploy.sh [PI_IP]
# Pi must be reachable via SSH before running.

set -euo pipefail

PI="${1:-192.168.1.237}"
SSH_USER="d3kos"
SSH_KEY="${HOME}/.ssh/id_d3kos"
SSH="ssh -i ${SSH_KEY} -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${SSH_USER}@${PI}"
SCP="scp -i ${SSH_KEY} -o ConnectTimeout=10 -o StrictHostKeyChecking=no"
DEPLOY_DIR="$(cd "$(dirname "$0")/.." && pwd)"

green() { printf '\033[0;32m[OK] %s\033[0m\n' "$1"; }
blue()  { printf '\033[0;34m[>>] %s\033[0m\n' "$1"; }
red()   { printf '\033[0;31m[FAIL] %s\033[0m\n' "$1"; }

echo ""
echo "d3kOS v0.9.2 — Metric/Imperial Deployment"
echo "Target: ${SSH_USER}@${PI}"
echo "=================================================="

# ── Preflight: confirm Pi is reachable ──────────────────────────────
blue "Checking Pi connectivity..."
if ! ping -c 1 -W 3 "$PI" &>/dev/null; then
  red "Cannot reach $PI — check network and try again."
  exit 1
fi
if ! $SSH "echo ok" &>/dev/null 2>&1; then
  red "SSH to ${SSH_USER}@${PI} failed — check credentials or run ssh-copy-id."
  exit 1
fi
green "Pi is reachable"

# ── Step 1: Create remote directory structure ───────────────────────
blue "Creating remote directories..."
$SSH "sudo mkdir -p /var/www/html/js \
                    /opt/d3kos/services/config \
                    /opt/d3kos/config && \
      sudo chown -R ${SSH_USER}:${SSH_USER} /opt/d3kos"
green "Remote directories ready"

# ── Step 2: Deploy units.js ─────────────────────────────────────────
blue "Deploying units.js..."
$SCP "${DEPLOY_DIR}/js/units.js" "${SSH_USER}@${PI}:/tmp/units.js"
$SSH "sudo cp /tmp/units.js /var/www/html/js/units.js && \
      sudo chown www-data:www-data /var/www/html/js/units.js && \
      sudo chmod 644 /var/www/html/js/units.js"
green "units.js deployed to /var/www/html/js/units.js"

# ── Step 3: Deploy test script ──────────────────────────────────────
blue "Deploying test_units.js to Pi home dir..."
$SCP "${DEPLOY_DIR}/tests/test_units.js" "${SSH_USER}@${PI}:/home/${SSH_USER}/test_units.js"
green "test_units.js deployed"

# ── Step 4: Run unit tests on Pi ────────────────────────────────────
blue "Running unit tests on Pi..."
$SSH "node /home/${SSH_USER}/test_units.js"
green "Unit tests passed on Pi"

# ── Step 5: Install Python dependencies ─────────────────────────────
blue "Installing python3-flask and python3-flask-cors via apt..."
$SSH "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q python3-flask python3-flask-cors"
green "Python dependencies installed"

# ── Step 6: Deploy preferences-api.py ──────────────────────────────
blue "Deploying preferences-api.py..."
$SCP "${DEPLOY_DIR}/python/preferences-api.py" \
     "${SSH_USER}@${PI}:/tmp/preferences-api.py"
$SSH "cp /tmp/preferences-api.py /opt/d3kos/services/config/preferences-api.py && \
      chmod 755 /opt/d3kos/services/config/preferences-api.py"
green "preferences-api.py deployed"

# ── Step 7: Deploy default config (only if not already present) ─────
blue "Deploying default user-preferences.json (if new)..."
$SCP "${DEPLOY_DIR}/config/user-preferences.json" "/tmp/user-preferences.json.default"
$SSH "if [ ! -f /opt/d3kos/config/user-preferences.json ]; then \
        cp /tmp/user-preferences.json.default /opt/d3kos/config/user-preferences.json; \
        echo 'Created new user-preferences.json'; \
      else \
        echo 'user-preferences.json already exists — preserving existing preferences'; \
      fi"
green "Config file handled"

# ── Step 8: Deploy systemd service ─────────────────────────────────
blue "Deploying systemd service..."
$SCP "${DEPLOY_DIR}/systemd/d3kos-preferences-api.service" \
     "${SSH_USER}@${PI}:/tmp/d3kos-preferences-api.service"
$SSH "sudo cp /tmp/d3kos-preferences-api.service \
              /etc/systemd/system/d3kos-preferences-api.service && \
      sudo systemctl daemon-reload && \
      sudo systemctl enable d3kos-preferences-api && \
      sudo systemctl restart d3kos-preferences-api"
green "Systemd service enabled and started"

# ── Step 9: Configure nginx proxy ───────────────────────────────────
blue "Checking nginx proxy configuration..."
NGINX_CONF="/etc/nginx/sites-enabled/default"
# Only add the proxy block if it doesn't already exist
HAS_PROXY=$($SSH "grep -c 'proxy_pass.*8107' $NGINX_CONF 2>/dev/null || echo 0")
if [ "$HAS_PROXY" -eq 0 ]; then
  blue "Adding /api/preferences proxy block to nginx..."
  $SSH "sudo sed -i '/^}$/i \\
\\tlocation /api/preferences {\\
\\t\\tproxy_pass http://127.0.0.1:8107/api/preferences;\\
\\t\\tproxy_set_header Host \$host;\\
\\t\\tproxy_set_header X-Real-IP \$remote_addr;\\
\\t\\tadd_header Cache-Control \"no-store\";\\
\\t}' $NGINX_CONF && \
    sudo nginx -t && \
    sudo systemctl reload nginx"
  green "Nginx proxy block added and nginx reloaded"
else
  green "Nginx proxy already configured — skipping"
fi

# ── Step 10: Verify service is running ─────────────────────────────
blue "Verifying service health..."
sleep 2
HEALTH=$($SSH "curl -sf http://localhost:8107/health" 2>/dev/null || echo "FAIL")
if echo "$HEALTH" | grep -q '"ok"'; then
  green "Preferences API is healthy: $HEALTH"
else
  red "Preferences API health check failed: $HEALTH"
  $SSH "sudo journalctl -u d3kos-preferences-api -n 20 --no-pager"
  exit 1
fi

# ── Step 11: Verify nginx proxy ─────────────────────────────────────
PROXY=$($SSH "curl -sf http://localhost/api/preferences" 2>/dev/null || echo "FAIL")
if echo "$PROXY" | grep -q "measurement_system"; then
  green "Nginx proxy working: $PROXY"
else
  red "Nginx proxy not responding correctly: $PROXY"
  exit 1
fi

# ── Deployment Summary ──────────────────────────────────────────────
echo ""
echo "=================================================="
echo "d3kOS v0.9.2 Deployment Complete"
echo ""
echo "Deployed files:"
echo "  /var/www/html/js/units.js"
echo "  /opt/d3kos/services/config/preferences-api.py"
echo "  /opt/d3kos/config/user-preferences.json"
echo "  /etc/systemd/system/d3kos-preferences-api.service"
echo ""
echo "Next steps:"
echo "  1. Run integration tests: ./test_api.sh ${PI}"
echo "  2. Manual check: http://${PI}/settings.html (Measurement toggle)"
echo "  3. Manual check: http://${PI} (Dashboard gauges show correct units)"
echo "  4. After all checks pass: git commit and tag v0.9.2"
echo ""
