#!/bin/bash
# configure-autostart.sh - Enable all d3kOS services and kiosk mode
# Part of d3kOS Distribution Preparation
# Session-Dist-2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log "Starting d3kOS autostart configuration..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
    exit 1
fi

# List of d3kOS services to enable
D3KOS_SERVICES=(
    "d3kos-license-api"
    "d3kos-tier-manager"
    "d3kos-tier-api"
    "d3kos-export-manager"
    "d3kos-export"
    "d3kos-upload"
    "d3kos-ai-api"
    "d3kos-camera-stream"
    "d3kos-fish-detector"
    "d3kos-notifications"
    "d3kos-manuals-api"
    "d3kos-health"
    "d3kos-history"
    "d3kos-first-boot"
)

# Voice service - disabled by default due to touchscreen conflict
D3KOS_DISABLED_SERVICES=(
    "d3kos-voice"
)

log "Enabling d3kOS services..."
SUCCESS_COUNT=0
SKIP_COUNT=0
ERROR_COUNT=0

for service in "${D3KOS_SERVICES[@]}"; do
    if [ -f "/etc/systemd/system/${service}.service" ]; then
        log "  Enabling ${service}.service..."
        if systemctl enable "${service}.service" 2>/dev/null; then
            ((SUCCESS_COUNT++))
        else
            warn "  Failed to enable ${service}.service"
            ((ERROR_COUNT++))
        fi
    else
        warn "  Service file not found: /etc/systemd/system/${service}.service"
        ((SKIP_COUNT++))
    fi
done

log "Disabling services that should not auto-start..."
for service in "${D3KOS_DISABLED_SERVICES[@]}"; do
    if [ -f "/etc/systemd/system/${service}.service" ]; then
        log "  Disabling ${service}.service (manual start only)..."
        systemctl disable "${service}.service" 2>/dev/null || true
    fi
done

# Enable system services
log "Enabling system services..."

# Signal K
if systemctl list-unit-files | grep -q "signalk.service"; then
    log "  Enabling signalk.service..."
    systemctl enable signalk 2>/dev/null || warn "  Could not enable signalk"
else
    warn "  signalk.service not found"
fi

# Node-RED
if systemctl list-unit-files | grep -q "nodered.service"; then
    log "  Enabling nodered.service..."
    systemctl enable nodered 2>/dev/null || warn "  Could not enable nodered"
else
    warn "  nodered.service not found"
fi

# gpsd
if systemctl list-unit-files | grep -q "gpsd.service"; then
    log "  Enabling gpsd.service..."
    systemctl enable gpsd 2>/dev/null || warn "  Could not enable gpsd"
else
    warn "  gpsd.service not found"
fi

# nginx
if systemctl list-unit-files | grep -q "nginx.service"; then
    log "  Enabling nginx.service..."
    systemctl enable nginx 2>/dev/null || warn "  Could not enable nginx"
else
    warn "  nginx.service not found"
fi

# Configure Chromium kiosk mode autostart
log "Configuring Chromium kiosk mode..."

AUTOSTART_DIR="/home/d3kos/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/d3kos-browser.desktop"

mkdir -p "$AUTOSTART_DIR"

cat > "$DESKTOP_FILE" <<'EOF'
[Desktop Entry]
Type=Application
Name=d3kOS Browser
Exec=/usr/bin/chromium --kiosk --noerrdialogs --disable-infobars --no-first-run --check-for-update-interval=31536000 --start-maximized http://localhost/
Comment=d3kOS Kiosk Mode Browser
X-GNOME-Autostart-enabled=true
EOF

chown -R d3kos:d3kos "$AUTOSTART_DIR"
chmod 644 "$DESKTOP_FILE"

log "  Chromium kiosk autostart configured: $DESKTOP_FILE"

# Configure labwc (Wayland compositor) autostart
log "Configuring labwc autostart..."

LABWC_AUTOSTART="/home/d3kos/.config/labwc/autostart"
mkdir -p "$(dirname "$LABWC_AUTOSTART")"

cat > "$LABWC_AUTOSTART" <<'EOF'
#!/bin/bash
# d3kOS labwc autostart

# Start Squeekboard (on-screen keyboard)
squeekboard &

# Start Chromium in kiosk mode (after 3 second delay)
sleep 3
/usr/bin/chromium --kiosk --noerrdialogs --disable-infobars --no-first-run --check-for-update-interval=31536000 --start-maximized http://localhost/ &
EOF

chmod +x "$LABWC_AUTOSTART"
chown d3kos:d3kos "$LABWC_AUTOSTART"

log "  labwc autostart configured: $LABWC_AUTOSTART"

# Configure Plymouth boot splash
log "Configuring Plymouth boot splash..."

if command -v plymouth-set-default-theme &>/dev/null; then
    # Check if d3kos theme exists
    if plymouth-set-default-theme -l | grep -q "pix"; then
        log "  Setting Plymouth theme to 'pix'..."
        plymouth-set-default-theme -R pix 2>/dev/null || warn "  Could not set Plymouth theme"

        # Update initramfs
        log "  Updating initramfs (this may take a minute)..."
        update-initramfs -u || warn "  Could not update initramfs"
    else
        warn "  Plymouth theme 'pix' not found, keeping default"
    fi
else
    warn "  Plymouth not installed"
fi

# Reload systemd daemon
log "Reloading systemd daemon..."
systemctl daemon-reload

# Summary
log ""
log "=========================================="
log "Autostart Configuration Complete!"
log "=========================================="
log "d3kOS services enabled: $SUCCESS_COUNT"
log "Services skipped: $SKIP_COUNT"
log "Errors: $ERROR_COUNT"
log ""
log "Chromium kiosk: Configured"
log "labwc autostart: Configured"
log "Plymouth splash: Configured"
log ""
log "Reboot required to apply all changes."
log "=========================================="

exit 0
