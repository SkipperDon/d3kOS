# Touch Scroll Fix — labwc mouseEmulation

**Date:** 2026-03-09
**Status:** RESOLVED — confirmed working by user
**Symptom:** Scrolling failed on all d3kOS pages in Chromium kiosk mode after touchscreen was connected.

---

## Root Cause

`/home/d3kos/.config/labwc/rc.xml` had `mouseEmulation="yes"` on the ILITEK touchscreen device.

labwc was converting all ILITEK USB touchscreen events into synthetic mouse pointer events before passing them to Wayland clients. Chromium received `pointerType="mouse"` on every touch event.

`touch-scroll.js v2.0` explicitly filters out mouse events:
```javascript
if (e.pointerType === "mouse") return;
```

Result: no touch events ever reached the scroll logic. Scrolling was completely broken.

---

## Fix

File: `/home/d3kos/.config/labwc/rc.xml`

```xml
<!-- BEFORE (broken) -->
<touch deviceName="ILITEK ILITEK-TP" mapToOutput="HDMI-A-2" mouseEmulation="yes"/>

<!-- AFTER (fixed) -->
<touch deviceName="ILITEK ILITEK-TP" mapToOutput="HDMI-A-2" mouseEmulation="no"/>
```

Repo copy: `deployment/pi_config/rc.xml`

Reboot required after this change.

---

## Display Mapping

Confirmed via `wlr-randr`: active display is `HDMI-A-2`. The `mapToOutput="HDMI-A-2"` attribute was already correct.

---

## What "mouseEmulation" Does

When `mouseEmulation="yes"`, labwc synthesizes mouse button/motion events from touch contact. This is intended for applications that only understand mouse input. Chromium on Wayland handles touch natively — mouse emulation breaks it.

Setting `mouseEmulation="no"` passes raw touch events through to Chromium, which processes them correctly as pointer events with `pointerType="touch"`.

---

## Result

All d3kOS pages scroll correctly after reboot. Settings page, navigation, boatlog, dashboard — all confirmed working.
