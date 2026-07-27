/**
 * d3kOS On-Screen Keyboard Fix v2.1
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
 * v2.1 fixes: If the textarea was already focused (e.g. from a page-load
 * auto-focus), el.focus() is a no-op — Chromium does not re-register
 * zwp_text_input_v3, so squeekboard shows but cannot type. Fix: call el.blur()
 * first to force a fresh focus activation. Also added _recentlyShown 800ms
 * guard to suppress the blur-triggered hide that fires when squeekboard
 * briefly steals Wayland input focus on key tap.
 *
 * Layout adjustment (preventing keyboard from covering the input) is handled
 * per-page (helm.html, ai-assistant.html) at element level — which fires
 * before this document-level handler during event bubbling, ensuring layout
 * is settled before the keyboard is shown.
 *
 * Add to any page that has text inputs:
 *   <script src="/js/keyboard-fix.js"></script>
 */
(function () {
  'use strict';

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
