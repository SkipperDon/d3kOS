#!/bin/bash
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

# configure-touchscreen.sh - Configure touchscreen calibration and on-screen keyboard
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

log "Starting d3kOS touchscreen configuration..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
    exit 1
fi

# Detect touchscreen device
log "Detecting touchscreen device..."

TOUCH_DEVICE=$(xinput list | grep -i "touch\|ILITEK" | grep -o 'id=[0-9]*' | head -1 | cut -d= -f2)

if [ -z "$TOUCH_DEVICE" ]; then
    warn "No touchscreen device detected"
    warn "This is normal if running headless or without touchscreen"
    TOUCH_DEVICE="auto"
else
    log "  Touchscreen device ID: $TOUCH_DEVICE"
    TOUCH_NAME=$(xinput list --name-only $TOUCH_DEVICE)
    log "  Device name: $TOUCH_NAME"
fi

# Configure Wayland text-input protocol for Squeekboard
log "Configuring Wayland text-input support..."

LABWC_CONFIG_DIR="/home/d3kos/.config/labwc"
mkdir -p "$LABWC_CONFIG_DIR"

# Create labwc rc.xml for keyboard support
cat > "$LABWC_CONFIG_DIR/rc.xml" <<'EOF'
<?xml version="1.0"?>
<labwc_config>
  <keyboard>
    <default />
  </keyboard>

  <mouse>
    <default />
  </mouse>

  <!-- Touch input support -->
  <touch>
    <default />
  </touch>

  <!-- Window rules -->
  <windowRules>
    <!-- Chromium kiosk -->
    <windowRule identifier="chromium">
      <action name="Maximize"/>
    </windowRule>

    <!-- Squeekboard always on top -->
    <windowRule identifier="sm.puri.Squeekboard">
      <action name="ToggleAlwaysOnTop"/>
    </windowRule>
  </windowRules>
</labwc_config>
EOF

chown d3kos:d3kos "$LABWC_CONFIG_DIR/rc.xml"
log "  labwc configuration created: $LABWC_CONFIG_DIR/rc.xml"

# Configure Squeekboard (on-screen keyboard)
log "Configuring Squeekboard..."

SQUEEKBOARD_CONFIG_DIR="/home/d3kos/.local/share/squeekboard"
mkdir -p "$SQUEEKBOARD_CONFIG_DIR"

# Create Squeekboard settings
cat > "$SQUEEKBOARD_CONFIG_DIR/settings.yaml" <<EOF
# Squeekboard configuration for d3kOS
# Auto-show keyboard when text fields are focused

appearance:
  wide_layout: true
  theme: default

behavior:
  auto_show: true
  auto_hide: true
  haptic_feedback: false

layout:
  default: us
  available:
    - us
    - us_wide
EOF

chown -R d3kos:d3kos "$SQUEEKBOARD_CONFIG_DIR"
log "  Squeekboard settings created: $SQUEEKBOARD_CONFIG_DIR/settings.yaml"

# Configure environment variables for Wayland
log "Configuring Wayland environment variables..."

ENV_FILE="/etc/environment.d/50-d3kos-wayland.conf"
mkdir -p "$(dirname "$ENV_FILE")"

cat > "$ENV_FILE" <<EOF
# d3kOS Wayland environment configuration

# Qt Wayland support
QT_QPA_PLATFORM=wayland
QT_WAYLAND_DISABLE_WINDOWDECORATION=1

# GTK Wayland support
GDK_BACKEND=wayland

# Enable text-input protocol for on-screen keyboard
WAYLAND_DISPLAY=wayland-0
XDG_RUNTIME_DIR=/run/user/1000

# Firefox/Chromium Wayland
MOZ_ENABLE_WAYLAND=1
MOZ_DBUS_REMOTE=1
EOF

log "  Wayland environment file created: $ENV_FILE"

# Configure udev rules for touchscreen
log "Configuring udev rules for touchscreen..."

UDEV_RULES_FILE="/etc/udev/rules.d/99-d3kos-touchscreen.rules"

cat > "$UDEV_RULES_FILE" <<'EOF'
# d3kOS Touchscreen udev rules
# Ensure touchscreen is accessible to d3kos user

# ILITEK touchscreen
SUBSYSTEM=="input", ATTRS{name}=="ILITEK*", MODE="0660", GROUP="input"
SUBSYSTEM=="usb", ATTRS{idVendor}=="222a", ATTRS{idProduct}=="0001", MODE="0660", GROUP="input"

# Generic HID touchscreen
SUBSYSTEM=="input", KERNEL=="event*", ATTRS{name}=="*Touch*", MODE="0660", GROUP="input"
EOF

log "  udev rules created: $UDEV_RULES_FILE"

# Reload udev rules
log "Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger

# Add d3kos user to input group
log "Adding d3kos user to input group..."
usermod -a -G input d3kos 2>/dev/null || warn "Could not add d3kos to input group"

# Configure touch gestures (disabled for simplicity)
log "Configuring touch gestures..."

GESTURE_CONFIG="/home/d3kos/.config/libinput-gestures.conf"
mkdir -p "$(dirname "$GESTURE_CONFIG")"

cat > "$GESTURE_CONFIG" <<'EOF'
# d3kOS touch gestures configuration
# Gestures disabled for marine helm use (accidental touches)

# Uncomment to enable swipe gestures:
# gesture swipe up 3     xdotool key Super_L+Up
# gesture swipe down 3   xdotool key Super_L+Down
# gesture swipe left 3   xdotool key Alt+Left
# gesture swipe right 3  xdotool key Alt+Right
EOF

chown d3kos:d3kos "$GESTURE_CONFIG"
log "  Gesture config created (gestures disabled): $GESTURE_CONFIG"

# Calibration notes
log ""
log "=========================================="
log "Touchscreen Configuration Complete!"
log "=========================================="
log "Device: $TOUCH_DEVICE"
log "Wayland text-input: Configured"
log "Squeekboard: Configured (auto-show)"
log "udev rules: Applied"
log "Gestures: Disabled"
log ""
log "CALIBRATION NOTES:"
log "  For manual calibration, use:"
log "    xinput_calibrator"
log "  Or libinput debug-events for testing"
log ""
log "Reboot required to apply all changes."
log "=========================================="

exit 0
