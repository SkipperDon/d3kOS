/**
 * d3kOS Touch Scroll Polyfill v2.0
 *
 * Uses Pointer Events API as primary path — catches ILITEK USB touchscreen
 * input that Chromium/Wayland delivers as pointer events (not touch events).
 * Touch events kept as fallback. No double-scroll: pointer path sets flag.
 *
 */
(function () {
  "use strict";

  var startX = 0, startY = 0, lastY = 0, lastT = 0;
  var vel = 0, locked = false, target = null, rafId = null;
  var activeId = null, handledByPointer = false;

  function getScrollParent(el) {
    while (el && el !== document.documentElement) {
      var ov = window.getComputedStyle(el).overflowY;
      if ((ov === "auto" || ov === "scroll") && el.scrollHeight > el.clientHeight + 2) {
        return el;
      }
      el = el.parentElement;
    }
    if (document.documentElement.scrollHeight > window.innerHeight + 2) {
      return document.documentElement;
    }
    return null;
  }

  function onStart(clientX, clientY, el) {
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    startX = clientX; startY = lastY = clientY;
    lastT = performance.now(); vel = 0; locked = false;
    target = getScrollParent(el);
  }

  function onMove(clientX, clientY) {
    if (!target) return;
    var dx = Math.abs(clientX - startX);
    var dy = Math.abs(clientY - startY);
    if (!locked && dx > dy && dx > 8) { locked = true; }
    if (locked) return;
    var now = performance.now();
    var delta = lastY - clientY;
    vel = delta / (now - lastT || 1);
    target.scrollTop += delta;
    lastY = clientY; lastT = now;
  }

  function onEnd() {
    if (!target || locked || Math.abs(vel) < 0.05) { target = null; return; }
    var v = vel * 16, tgt = target;
    target = null;
    function coast() {
      if (Math.abs(v) < 0.5) return;
      tgt.scrollTop += v; v *= 0.90;
      rafId = requestAnimationFrame(coast);
    }
    coast();
  }

  /* Pointer Events — primary (covers touch-as-pointer on Wayland) */
  document.addEventListener("pointerdown", function (e) {
    if (e.pointerType === "mouse") return;
    activeId = e.pointerId;
    handledByPointer = true;
    onStart(e.clientX, e.clientY, e.target);
  }, { passive: true });

  document.addEventListener("pointermove", function (e) {
    if (e.pointerId !== activeId) return;
    onMove(e.clientX, e.clientY);
  }, { passive: true });

  document.addEventListener("pointerup", function (e) {
    if (e.pointerId !== activeId) return;
    activeId = null; onEnd();
  }, { passive: true });

  document.addEventListener("pointercancel", function (e) {
    if (e.pointerId !== activeId) return;
    activeId = null; target = null;
  }, { passive: true });

  /* Touch Events — fallback (prevents double-firing via flag) */
  document.addEventListener("touchstart", function (e) {
    if (handledByPointer) return;
    if (e.touches.length !== 1) return;
    onStart(e.touches[0].clientX, e.touches[0].clientY, e.target);
  }, { passive: true });

  document.addEventListener("touchmove", function (e) {
    if (handledByPointer || e.touches.length !== 1) return;
    onMove(e.touches[0].clientX, e.touches[0].clientY);
  }, { passive: true });

  document.addEventListener("touchend", function () {
    if (handledByPointer) { handledByPointer = false; return; }
    onEnd();
  }, { passive: true });

}());
