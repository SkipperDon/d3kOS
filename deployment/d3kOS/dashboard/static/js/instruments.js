/**
 * instruments.js — d3kOS v0.9.2.2
 * Instrument row toggle, alert dot logic, cell context menu.
 * Session 1: static demo values. Session 2: Signal K WebSocket.
 */

/* ── ROW TOGGLE — Both / Engine / Nav ── */
function showRow(which) {
  const showE = which === 'both' || which === 'engine';
  const showN = which === 'both' || which === 'nav';
  document.getElementById('rowEngine').classList.toggle('hidden', !showE);
  document.getElementById('rowNav').classList.toggle('hidden', !showN);
  document.getElementById('rpBoth').classList.toggle('on',   which === 'both');
  document.getElementById('rpEngine').classList.toggle('on', which === 'engine');
  document.getElementById('rpNav').classList.toggle('on',    which === 'nav');
  const hints = {
    both:   'Engine + Nav',
    engine: 'Engine instruments',
    nav:    'Navigation instruments',
  };
  document.getElementById('rowHint').textContent = hints[which];
  // Alert dots on hidden tabs
  const hasEngineAlert = !!document.querySelector('#rowEngine .ic.adv, #rowEngine .ic.alrt, #rowEngine .ic.crit');
  const hasNavAlert    = !!document.querySelector('#rowNav .ic.adv, #rowNav .ic.alrt, #rowNav .ic.crit');
  document.getElementById('engineAlert').classList.toggle('show', !showE && hasEngineAlert);
  document.getElementById('navAlert').classList.toggle('show',    !showN && hasNavAlert);
}

// Default: both rows visible on load
window.addEventListener('DOMContentLoaded', () => showRow('both'));

/* ── CELL CONTEXT MENU ── */
function openCtx(e, name) {
  e.preventDefault();
  const m = document.getElementById('ctx');
  document.getElementById('ctxTtl').textContent = name;
  m.style.left = Math.min(e.clientX, window.innerWidth - 230) + 'px';
  m.style.top  = Math.max(e.clientY - 180, 60) + 'px';
  m.classList.add('show');
  setTimeout(() => document.addEventListener('click', hideCtx, { once: true }), 10);
}

function hideCtx() {
  document.getElementById('ctx').classList.remove('show');
}
