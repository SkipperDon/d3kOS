# OpenCPN Pinch-Zoom — twofing Solution

**Date:** 2026-03-09 (confirmed working at session start)
**Status:** RESOLVED — two-finger zoom working in OpenCPN
**Symptom:** OpenCPN did not respond to two-finger pinch gestures on the touchscreen.

---

## Why OpenCPN Cannot Use Wayland Touch Directly

OpenCPN Flatpak runs under XWayland (the Flatpak manifest sets `sockets=x11`). It receives X11 input events, not native Wayland touch events. Two-finger touch gestures from the ILITEK touchscreen never reach OpenCPN as pinch events.

---

## Solution: twofing

`twofing` is a daemon that reads raw touch input directly from the Linux input device, interprets two-finger gestures, and emits X11 scroll/zoom events that XWayland applications (including OpenCPN Flatpak) understand.

**Source:** https://github.com/plippo/twofing

Built from source on the Pi. Patched for Wayland XInput fallback — the stock twofing assumes a running X display for its XInput output; the patch allows it to target XWayland.

---

## Setup

### 1. udev Rule
File: `/etc/udev/rules.d/40-twofing-ilitek.rules`

Creates a stable symlink `/dev/twofingtouch` pointing to the ILITEK touchscreen input device (`/dev/input/event0`).

```
SUBSYSTEM=="input", ATTRS{name}=="ILITEK ILITEK-TP", SYMLINK+="twofingtouch"
```

### 2. labwc Autostart
File: `/home/d3kos/.config/labwc/autostart`

twofing starts before OpenCPN is launched:
```
twofing --device=/dev/twofingtouch &
```

### 3. OpenCPN Flatpak Permissions
```bash
sudo flatpak override --device=input --device=dri org.opencpn.OpenCPN
```

Required so the Flatpak sandbox can access the touchscreen input device.

---

## Touchscreen Device Reference

| Property | Value |
|----------|-------|
| Device name | `ILITEK ILITEK-TP` |
| Input node | `/dev/input/event0` |
| udev symlink | `/dev/twofingtouch` |
| Display output | `HDMI-A-2` |

---

## Result

Two-finger pinch zoom works in OpenCPN Flatpak. Confirmed working on Pi.
