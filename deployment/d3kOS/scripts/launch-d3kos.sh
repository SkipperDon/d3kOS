#!/bin/bash
# d3kOS launch script
# Location: /home/boatiq/Helm-OS/deployment/d3kOS/scripts/launch-d3kos.sh
# Pi deploy path: copy to same path on Pi, chmod +x
#
# Architecture: --app --start-maximized (NOT --kiosk)
# Reason: Wayland layer stack — kiosk puts Chromium above Squeekboard (top layer),
# making the on-screen keyboard permanently invisible. Maximised normal window
# sits below Squeekboard. labwc strips decorations via rc.xml windowRules.
# See: deployment/d3kOS/docs/D3KOS_UI_SPEC_ADDENDUM_01.md Section C

# Prevent crash-restore prompt on next boot
CHROMIUM_PREFS="$HOME/.config/chromium/Default/Preferences"
if [ -f "$CHROMIUM_PREFS" ]; then
  sed -i 's/"exited_cleanly":false/"exited_cleanly":true/g' "$CHROMIUM_PREFS"
  sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/g'   "$CHROMIUM_PREFS"
fi

# Clear stale session files to prevent crash-restore dialog
rm -f "$HOME/.config/chromium/Default/Sessions/"* \
       "$HOME/.config/chromium/Default/Current"* \
       "$HOME/.config/chromium/Default/Last"* 2>/dev/null || true

# Launch Chromium as maximised app window (no address bar, no tabs)
# Note: binary is 'chromium' on Debian/Raspberry Pi OS (not 'chromium-browser')
# --app=http://localhost/ uses nginx (not :3000 Flask direct) — enables theme-color title bar
chromium \
  --app=http://localhost/ \
  --start-maximized \
  --force-device-scale-factor=1 \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --check-for-update-interval=31536000 \
  --disable-session-crashed-bubble \
  --hide-crash-restore-bubble \
  --disable-restore-session-state \
  --disable-translate \
  --disable-features=TranslateUI,OverlayScrollbar \
  --ozone-platform=wayland \
  --touch-events=enabled \
  --enable-pinch \
  --pull-to-refresh=0 \
  --enable-features=TouchpadAndWheelScrollLatching,AsyncWheelEvents
