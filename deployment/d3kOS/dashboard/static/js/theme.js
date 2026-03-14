/**
 * theme.js — d3kOS v0.9.2.2
 * Day/Night theme switching with manual override (Bug 1 fix).
 * Loaded before nav.js. Sets globals: manualTheme, setTheme, autoTheme.
 *
 * Bug 1 fix: autoTheme() never overrides a manual selection.
 * The auto timer still runs every 60s but returns immediately if
 * the user has tapped DAY or NIGHT this session.
 */

let manualTheme = false;

function setTheme(t, manual) {
  if (manual) manualTheme = true;
  if (t === 'night') document.body.setAttribute('data-night', '');
  else               document.body.removeAttribute('data-night');
  const btnD = document.getElementById('btnD');
  const btnN = document.getElementById('btnN');
  if (btnD) btnD.classList.toggle('on', t === 'day');
  if (btnN) btnN.classList.toggle('on', t === 'night');
}

function autoTheme() {
  if (manualTheme) return;
  const h = new Date().getHours();
  setTheme(h >= 7 && h < 20 ? 'day' : 'night');
}

autoTheme();
setInterval(autoTheme, 60000);
