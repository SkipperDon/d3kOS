/**
 * d3kOS Touch Scroll Polyfill v1.0
 *
 * Problem: Chromium 144 on Wayland with ILITEK touchscreen sends raw pointer
 * events, not touch gesture events. The browser's built-in scroll gesture
 * detector never fires, so CSS touch-action / overflow-y: auto does nothing
 * for swipe scrolling.
 *
 * Solution: Intercept touchstart/touchmove/touchend directly and manually
 * apply the delta to scrollTop of the nearest scrollable ancestor. Add
 * momentum (velocity decay) on touchend for natural feel.
 *
 * Rules:
 *   - All listeners use { passive: true } — no blocking of taps or clicks
 *   - Never calls preventDefault() — buttons, links, inputs all work normally
 *   - Ignores horizontal-dominant swipes (left/right navigation gestures)
 *   - Applies to every scrollable element on the page automatically
 */
(function () {
  'use strict';

  // Walk up the DOM tree to find the nearest ancestor that can scroll vertically
  function getScrollParent(el) {
    while (el && el !== document.documentElement) {
      const style = window.getComputedStyle(el);
      const ov = style.overflowY;
      if ((ov === 'auto' || ov === 'scroll') && el.scrollHeight > el.clientHeight + 2) {
        return el;
      }
      el = el.parentElement;
    }
    // Fall back to the document scroll element
    if (document.documentElement.scrollHeight > window.innerHeight + 2) {
      return document.documentElement;
    }
    return null;
  }

  var startX  = 0;
  var startY  = 0;
  var lastY   = 0;
  var lastT   = 0;
  var vel     = 0;      // px/ms, direction-signed
  var target  = null;
  var rafId   = null;
  var locked  = false;  // true = horizontal swipe, ignore this gesture

  document.addEventListener('touchstart', function (e) {
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    var t = e.touches[0];
    startX = t.clientX;
    startY = lastY = t.clientY;
    lastT  = performance.now();
    vel    = 0;
    locked = false;
    target = getScrollParent(e.target);
  }, { passive: true });

  document.addEventListener('touchmove', function (e) {
    if (!target) return;
    var t  = e.touches[0];
    var dx = Math.abs(t.clientX - startX);
    var dy = Math.abs(t.clientY - startY);

    // Lock out horizontal swipes (e.g. carousels, left-nav gesture)
    if (!locked && dx > dy && dx > 8) { locked = true; }
    if (locked) return;

    var now = performance.now();
    var dt  = now - lastT || 1;
    var delta = lastY - t.clientY;
    vel     = delta / dt;
    target.scrollTop += delta;
    lastY   = t.clientY;
    lastT   = now;
  }, { passive: true });

  document.addEventListener('touchend', function () {
    if (!target || locked || Math.abs(vel) < 0.05) { target = null; return; }
    var v = vel * 16;   // scale velocity to px/frame at 60 fps
    var tgt = target;
    target  = null;

    function coast() {
      if (Math.abs(v) < 0.5) return;
      tgt.scrollTop += v;
      v *= 0.90;        // friction coefficient — 0.88 = snappy, 0.94 = glide
      rafId = requestAnimationFrame(coast);
    }
    coast();
  }, { passive: true });

}());
