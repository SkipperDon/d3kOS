/**
 * d3kOS i18n loader — applies translations to all data-i18n elements on page load.
 * Keys: "ui.dashboard", "ui.back", "alerts.high_temp", "onboarding.welcome", etc.
 * Fetches current language from /api/language, then loads JSON from /api/i18n/<code>.
 * Falls back silently to English text already in the HTML if API is unreachable.
 */
(function () {
  'use strict';

  function getNestedKey(obj, dotKey) {
    return dotKey.split('.').reduce(function (o, k) {
      return o && o[k] !== undefined ? o[k] : null;
    }, obj);
  }

  function applyTranslations(translations) {
    var dir = translations.dir || 'ltr';
    document.documentElement.setAttribute('dir', dir);
    document.documentElement.setAttribute('lang', translations.lang_code || 'en');

    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      var value = getNestedKey(translations, key);
      if (value) {
        el.textContent = value;
      }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-placeholder');
      var value = getNestedKey(translations, key);
      if (value) {
        el.setAttribute('placeholder', value);
      }
    });

    document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-title');
      var value = getNestedKey(translations, key);
      if (value) {
        el.setAttribute('title', value);
      }
    });
  }

  function loadTranslations(langCode) {
    return fetch('/api/i18n/' + langCode, { signal: AbortSignal.timeout(3000) })
      .then(function (r) { return r.json(); })
      .then(function (data) { applyTranslations(data); })
      .catch(function () { /* silent fallback — HTML already has English text */ });
  }

  function init() {
    fetch('/api/language', { signal: AbortSignal.timeout(2000) })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var lang = (d.language || 'en').toLowerCase();
        if (lang !== 'en') {
          loadTranslations(lang);
        }
      })
      .catch(function () { /* no language API — stay with HTML defaults */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
