/**
 * d3kOS On-Screen Keyboard Fix v2.2
 *
 * Problem: With labwc mouseEmulation="no", ILITEK touch events arrive as real
 * touch (not synthetic mouse clicks). el.click() does NOT trigger
 * zwp_text_input_v3.enable() in Chromium Wayland, so squeekboard never appears.
 *
 * Fix: On touch of any text input, POST to /keyboard/show which calls
 * dbus-send sm.puri.OSK0.SetVisible boolean:true — directly showing squeekboard
 * without relying on the Wayland text input protocol.
 * On blur, POST to /keyboard/hide to dismiss.
 *
 * v2.1: If the textarea was already focused (e.g. from a page-load auto-focus),
 * el.focus() is a no-op — Chromium does not re-register zwp_text_input_v3, so
 * squeekboard shows but cannot type. Fix: call el.blur() first to force a fresh
 * focus activation. Added _recentlyShown 800ms guard to suppress the
 * blur-triggered hide that fires when squeekboard briefly steals Wayland input
 * focus on key tap.
 *
 * ── v2.2 — BUG-08, S116 2026-08-01 ──────────────────────────────────────────
 * This file previously existed ONLY under nginx at /var/www/html/js/, and the
 * Flask dashboard template loaded it with an absolute `/js/keyboard-fix.js`.
 * Flask serves static from /static/, so on localhost:3000 — the URL the kiosk
 * actually runs — that returned 404 and THIS SCRIPT NEVER LOADED. Every prior
 * analysis of BUG-08 was therefore against the nginx page, not the live one.
 * Now served from Flask static, with matching /keyboard/* proxy routes in app.py.
 *
 * v2.2 also adds a same-machine guard. Since BUG-46 the dashboard is reachable
 * from a phone or laptop. squeekboard only exists on the Pi's own screen, so
 * without this guard a remote user tapping a textarea would pop the on-screen
 * keyboard up on the boat's helm display.
 *
 * Layout adjustment (preventing keyboard from covering the input) is handled
 * per-page at element level — which fires before this document-level handler
 * during event bubbling, ensuring layout is settled before the keyboard shows.
 *
 * Add to any Flask-served page that has text inputs:
 *   <script src="/static/js/keyboard-fix.js"></script>
 */
(function () {
  'use strict';

  // BUG-08 v2.2: squeekboard runs on the Pi's own display. Showing it because a
  // remote browser focused a field would raise a keyboard at the helm for no
  // reason. Only act when this page is being viewed on the Pi itself.
  var host = window.location.hostname;
  if (host !== 'localhost' && host !== '127.0.0.1') {
    return;
  }

  var TEXT_INPUT_TYPES = ['text', 'number', 'password', 'search', 'email', 'tel', 'url', ''];
  var activeInput = null;
  var _recentlyShown = false;
  var _recentlyShownTimer = null;

  function showKeyboard() {
    _recentlyShown = true;
    clearTimeout(_recentlyShownTimer);
    _recentlyShownTimer = setTimeout(function () { _recentlyShown = false; }, 800);
    fetch('/keyboard/show', { method: 'POST' }).catch(function () {});
  }

  function hideKeyboard() {
    if (_recentlyShown) return;
    fetch('/keyboard/hide', { method: 'POST' }).catch(function () {});
  }

  document.addEventListener('pointerup', function (e) {
    if (e.pointerType !== 'touch') return;

    var el = e.target;
    var isTextInput = (
      el.tagName === 'TEXTAREA' ||
      (el.tagName === 'INPUT' && TEXT_INPUT_TYPES.indexOf((el.type || '').toLowerCase()) !== -1)
    );

    if (!isTextInput) return;

    // Remove hide listener from previously focused input
    if (activeInput && activeInput !== el) {
      activeInput.removeEventListener('blur', hideKeyboard);
    }
    activeInput = el;

    // Blur first to force Chromium to re-register zwp_text_input_v3,
    // even if the element was already focused (e.g. from auto-focus on load).
    el.blur();
    el.focus();
    el.addEventListener('blur', hideKeyboard, { once: true });
    showKeyboard();
  }, { passive: true });

}());
