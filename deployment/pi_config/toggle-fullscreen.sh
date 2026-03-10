#!/bin/bash
# Toggle fullscreen for Chromium on Wayland
# Uses state file to track current mode; wlrctl for direct Wayland window control
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0

STATE_FILE=/tmp/d3kos-fullscreen-state
STATE=$(cat "$STATE_FILE" 2>/dev/null || echo "fullscreen")

if [ "$STATE" = "fullscreen" ]; then
  # Exit fullscreen -> windowed maximized
  wtype -k F11
  sleep 0.3
  wlrctl toplevel maximize app_id:chromium
  echo "windowed" > "$STATE_FILE"
else
  # Exit windowed -> fullscreen
  wlrctl toplevel fullscreen app_id:chromium
  echo "fullscreen" > "$STATE_FILE"
fi
