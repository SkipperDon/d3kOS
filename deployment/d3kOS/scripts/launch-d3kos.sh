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
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' \
  /home/boatiq/.config/chromium/Default/Preferences 2>/dev/null
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' \
  /home/boatiq/.config/chromium/Default/Preferences 2>/dev/null

# Launch Chromium as maximised app window
# Note: binary is 'chromium' on Debian/Raspberry Pi OS (not 'chromium-browser')
chromium \
  --app=http://localhost:3000 \
  --start-maximized \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --disable-restore-last-session \
  --disable-session-crashed-bubble \
  --disable-features=TranslateUI \
  --enable-features=OverlayScrollbar \
  --check-for-update-interval=31536000 \
  --ozone-platform=wayland \
  --use-gl=angle \
  --use-angle=swiftshader
