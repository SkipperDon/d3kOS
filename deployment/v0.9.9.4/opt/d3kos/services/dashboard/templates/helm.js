/**
 * helm.js — d3kOS v0.9.2.3
 * HELM voice overlay (Web Speech API) + AI Nav panel text input.
 * sendAI(text) → POST :3001/ask → chat bubbles in split pane.
 *
 * recognition.lang is read from <html lang="..."> which Flask injects
 * from vessel.env UI_LANG (e.g. "en-GB").
 *
 * Session 1: demo stubs.
 * Session 2: Web Speech API + live :3001 AI calls.
 * Session C (v0.9.2.3): HELM mute toggle — I-07.
 */

const HELM_LANG  = document.documentElement.lang || 'en-GB';
const GEMINI_URL = 'http://localhost:3001/ask';

let _helmOn    = false;
let _helmTimer = null;
let _helmRec   = null;  // SpeechRecognition instance for HELM overlay

/* ── HELM MUTE (I-07) ── */
/* Persists across page reload. Mutes TTS speech synthesis only.
   HELM still listens and processes voice when muted. */
let helmMuted = localStorage.getItem('d3kHelmMute') === '1';

function toggleHelmMute() {
  helmMuted = !helmMuted;
  localStorage.setItem('d3kHelmMute', helmMuted ? '1' : '0');
  /* Cancel any active browser speech synthesis */
  if (helmMuted && window.speechSynthesis) window.speechSynthesis.cancel();
  _updateMuteBtn();
  if (typeof toast === 'function') {
    toast(helmMuted ? 'HELM muted \u2014 listening only' : 'HELM unmuted \u2014 voice active');
  }
}

function _updateMuteBtn() {
  const btn = document.getElementById('helmMuteBtn');
  if (btn) {
    if (helmMuted) {
      btn.textContent = '\uD83D\uDD07 MUTED';
      btn.classList.add('muted');
    } else {
      btn.textContent = '\uD83D\uDD0A TALKING';
      btn.classList.remove('muted');
    }
  }
  /* Update nav button state label and muted class */
  const helmBtn = document.getElementById('helmBtn');
  const stateEl = document.getElementById('helmState');
  if (helmBtn) {
    helmBtn.classList.toggle('muted', helmMuted);
  }
  if (stateEl && !helmBtn.classList.contains('live')) {
    stateEl.textContent = helmMuted ? 'MUTED' : 'WATCHING';
  }
}

/* ── WEB SPEECH API ── */
function _newRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const r        = new SR();
  r.lang         = HELM_LANG;
  r.interimResults = false;
  r.maxAlternatives = 1;
  return r;
}

/* ── HELM LISTENING OVERLAY ── */
function openHelm() {
  _helmOn = true;
  document.getElementById('helmOv').classList.add('show');
  document.getElementById('hPill').classList.add('live');
  document.getElementById('helmBtn').classList.add('live');
  const stateEl = document.getElementById('helmState');
  if (stateEl) stateEl.textContent = 'LISTENING';

  const r = _newRecognition();
  if (r) {
    r.onresult = (evt) => {
      const text = evt.results[0][0].transcript;
      closeHelm();
      setTimeout(() => { openSplit('ai'); sendAI(text); }, 200);
    };
    r.onerror = () => {
      // Mic unavailable or permission denied — open AI panel for text input
      closeHelm();
      setTimeout(() => { openSplit('ai'); toast('Voice unavailable — type your question'); }, 200);
    };
    r.onend = () => { if (_helmOn) closeHelm(); };
    try {
      r.start();
      _helmRec   = r;
      _helmTimer = setTimeout(closeHelm, 10000); // safety: close after 10s silence
    } catch {
      // r.start() threw synchronously — fall back immediately
      closeHelm();
      setTimeout(() => { openSplit('ai'); toast('Voice unavailable — type your question'); }, 200);
    }
  } else {
    // No Web Speech API — open AI panel for text input
    closeHelm();
    openSplit('ai');
    toast('Voice unavailable — type your question');
  }
}

function closeHelm() {
  _helmOn = false;
  clearTimeout(_helmTimer);
  if (_helmRec) { try { _helmRec.stop(); } catch {} _helmRec = null; }
  document.getElementById('helmOv').classList.remove('show');
  document.getElementById('hPill').classList.remove('live');
  document.getElementById('helmBtn').classList.remove('live');
  /* Restore state label */
  const stateEl = document.getElementById('helmState');
  if (stateEl) stateEl.textContent = helmMuted ? 'MUTED' : 'WATCHING';
}

/* ── SPLIT PANE MIC ── */
let _micOn  = false;
let _micRec = null;

function toggleMic() {
  if (_micOn) { _stopMic(); return; }

  _micOn = true;
  const btn = document.getElementById('spMic');
  if (btn) { btn.classList.add('live'); btn.textContent = '⏹'; }

  const r = _newRecognition();
  if (r) {
    r.onresult = (evt) => {
      const text = evt.results[0][0].transcript;
      const field = document.getElementById('aiField');
      if (field) field.value = text;
      _stopMic();
      sendAI(text);
    };
    r.onerror = _stopMic;
    r.onend   = _stopMic;
    r.start();
    _micRec = r;
  } else {
    toast('Speech API not available — type your question');
    _stopMic();
  }
}

function _stopMic() {
  _micOn = false;
  if (_micRec) { try { _micRec.stop(); } catch {} _micRec = null; }
  const btn = document.getElementById('spMic');
  if (btn) { btn.classList.remove('live'); btn.textContent = '🎤'; }
}

/* ── AI SEND + CHAT BUBBLES ── */
function sendAI(text) {
  if (!text || !text.trim()) return;
  const field = document.getElementById('aiField');
  if (field) field.value = '';

  _addBubble(text, true);

  const ticker = document.getElementById('ticker');
  if (ticker && !ticker.classList.contains('hot')) {
    ticker.textContent = 'HELM: "'
      + text.slice(0, 55) + (text.length > 55 ? '…' : '')
      + '" — PROCESSING';
  }

  fetch(GEMINI_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text }),
  })
    .then(r => r.json())
    .then(d => {
      const resp = d.response || d.answer || d.text || '(no response)';
      const src  = d.source  || 'ai';
      const tok  = d.tokens  || d.token_count || null;
      _addBubble(resp, false, src, tok);
      const srcLbl = document.getElementById('aiSourceLbl');
      if (srcLbl) srcLbl.textContent = src === 'ollama'
        ? 'OLLAMA \u00b7 OFFLINE AI'
        : 'GEMINI 2.5 FLASH \u00b7 ONLINE';
      if (ticker && !ticker.classList.contains('hot')) {
        ticker.textContent = 'HELM ANSWERED · ' + src.toUpperCase()
          + (tok ? ' · ' + tok + ' TOKENS' : '');
        setTimeout(() => {
          if (ticker && !ticker.classList.contains('hot')) {
            ticker.textContent = typeof TICKS !== 'undefined' ? TICKS[0]
                               : 'AI FIRST OFFICER ACTIVE — ALL SYSTEMS NOMINAL';
          }
        }, 6000);
      }
    })
    .catch(() => {
      _addBubble('AI service unavailable — check connections.', false, 'error');
      if (ticker && !ticker.classList.contains('hot')) {
        ticker.textContent = 'AI BRIDGE UNAVAILABLE';
      }
    });
}

function _addBubble(text, isMe, source, tokens) {
  const body = document.querySelector('#tab-ai .sp-body');
  if (!body) return;
  const div = document.createElement('div');
  div.className = 'ai-msg ' + (isMe ? 'me' : 'bot');
  if (isMe) {
    div.textContent = text;
  } else {
    div.innerHTML = _sanitizeAI(text);
    if (source || tokens) {
      const meta = document.createElement('div');
      meta.className = 'meta';
      meta.textContent = [source, tokens ? tokens + ' tokens' : '', 'not stored']
        .filter(Boolean).join(' · ');
      div.appendChild(meta);
    }
  }
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

function _sanitizeAI(text) {
  // Escape HTML, then allow bold (**...**) and newlines only
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    .replace(/\n/g, '<br>');
}

/* ── WIRE TEXT FIELD (Enter to send) ── */
function _wireField() {
  const field = document.getElementById('aiField');
  if (field) {
    field.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendAI(field.value);
    });
  }
}

function _helmInit() {
  _wireField();
  _updateMuteBtn(); // Set initial mute button state from localStorage
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', _helmInit);
} else {
  _helmInit();
}
