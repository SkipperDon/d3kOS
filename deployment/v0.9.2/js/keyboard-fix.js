/**
 * d3kOS On-Screen Keyboard Fix v2.0
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

  function showKeyboard() {
    fetch('/keyboard/show', { method: 'POST' }).catch(function () {});
  }

  function hideKeyboard() {
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

    el.focus();
    el.addEventListener('blur', hideKeyboard, { once: true });
    showKeyboard();
  }, { passive: true });

}());
