/**
 * helm.js — d3kOS v0.9.2.2
 * HELM voice overlay and split-pane mic.
 * Session 1: demo/stub. Session 2: Web Speech API wired to :3001/ask.
 *
 * recognition.lang is read from <html lang="..."> which Flask injects
 * from vessel.env UI_LANG (e.g. "en-GB").
 */

const HELM_LANG = document.documentElement.lang || 'en-GB';

let _helmOn = false;
let _helmTimer = null;

function openHelm() {
  _helmOn = true;
  document.getElementById('helmOv').classList.add('show');
  document.getElementById('hPill').classList.add('live');
  document.getElementById('helmBtn').classList.add('live');

  // Demo: auto-close after 3.5s and show a canned response
  _helmTimer = setTimeout(() => {
    closeHelm();
    setTimeout(() => {
      const ticker = document.getElementById('ticker');
      if (ticker) {
        ticker.textContent = 'HELM HEARD: "FUEL RANGE AT CURRENT SPEED" — RESPONDING IN AI PANEL';
        ticker.style.opacity = '1';
      }
      openSplit('ai');
      toast('Helm answered — see AI Nav panel');
      setTimeout(() => {
        if (ticker) ticker.textContent = TICKS[0];
      }, 5000);
    }, 350);
  }, 3500);
}

function closeHelm() {
  _helmOn = false;
  clearTimeout(_helmTimer);
  document.getElementById('helmOv').classList.remove('show');
  document.getElementById('hPill').classList.remove('live');
  document.getElementById('helmBtn').classList.remove('live');
}

/* ── SPLIT PANE MIC ── */
let _micOn = false;

function toggleMic() {
  _micOn = !_micOn;
  const btn = document.getElementById('spMic');
  btn.classList.toggle('live', _micOn);
  btn.textContent = _micOn ? '⏹' : '🎤';

  if (_micOn) {
    toast('Listening — speak your question (' + HELM_LANG + ')');
    // Demo: capture after 3s
    setTimeout(() => {
      _micOn = false;
      btn.classList.remove('live');
      btn.textContent = '🎤';
      const field = document.getElementById('aiField');
      if (field) field.value = 'What is my fuel range at current speed?';
      toast('Voice captured — processing…');
    }, 3000);
  }
}
