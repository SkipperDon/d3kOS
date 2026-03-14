/**
 * cameras.js — d3kOS v0.9.2.2 Session 3
 * Cameras tab: loads slot list from :8084, renders forward-watch primary view
 * + display_in_grid 2×2 grid. Polls /camera/frame/<slot_id> at 500ms.
 */

const CAM_API   = 'http://localhost:8084';
const CAM_FPS   = 500;   // ms between frame refreshes

let _camIntervals = [];

/**
 * Stop all running camera frame refresh intervals.
 * Called by closeSplit() and before each loadCameras() run.
 */
function clearCamIntervals() {
  _camIntervals.forEach(id => clearInterval(id));
  _camIntervals = [];
}

/**
 * Load slot list from camera API and build the cameras tab.
 * Called by showTab() in nav.js when the Cameras tab is activated.
 */
async function loadCameras() {
  clearCamIntervals();

  const msgEl     = document.getElementById('cam-msg');
  const primaryEl = document.getElementById('cam-primary');
  const gridEl    = document.getElementById('cam-grid');
  if (!msgEl || !primaryEl || !gridEl) return;

  // Reset to loading state
  msgEl.style.display  = 'flex';
  msgEl.textContent    = 'Loading cameras\u2026';
  primaryEl.style.display = 'none';
  primaryEl.querySelector('img').src = '';
  gridEl.innerHTML     = '';

  // Fetch slot list
  let slots;
  try {
    const res = await fetch(CAM_API + '/camera/slots');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    slots = await res.json();
  } catch {
    msgEl.innerHTML = 'Camera system unavailable &mdash; :8084 not reachable.<br>'
      + '<a href="/settings#section6" style="color:var(--g-txt);font-size:12px;">Camera Setup in Settings &rarr;</a>';
    return;
  }

  if (!Array.isArray(slots) || slots.length === 0) {
    msgEl.innerHTML = 'No camera slots defined.<br>'
      + '<a href="/settings#section6" style="color:var(--g-txt);font-size:12px;">Camera Setup in Settings &rarr;</a>';
    return;
  }

  msgEl.style.display = 'none';

  // ── Forward watch slot — full-width primary view ──────────────────────────
  const fwSlot = slots.find(s => s.roles && s.roles.forward_watch);
  if (fwSlot) {
    primaryEl.style.display = 'block';
    const lblEl = primaryEl.querySelector('#cam-primary-lbl');
    if (lblEl) lblEl.textContent = '\u25b6 ' + fwSlot.label.toUpperCase();
    const imgEl = document.getElementById('cam-primary-img');
    if (imgEl) {
      if (fwSlot.assigned) {
        imgEl.src = _frameUrl(fwSlot.slot_id);
        _camIntervals.push(setInterval(() => {
          imgEl.src = _frameUrl(fwSlot.slot_id);
        }, CAM_FPS));
      } else {
        _setImgPlaceholder(imgEl, fwSlot.label + ' — No camera assigned');
      }
    }
  }

  // ── Grid: display_in_grid slots (excluding forward watch already shown) ───
  const gridSlots = slots.filter(s =>
    s.roles && s.roles.display_in_grid && (!fwSlot || s.slot_id !== fwSlot.slot_id)
  );

  gridSlots.forEach(slot => {
    const cell = document.createElement('div');
    cell.style.cssText = 'position:relative;aspect-ratio:4/3;background:var(--panel);'
      + 'border-radius:8px;overflow:hidden;border:1px solid var(--rule,rgba(0,0,0,.08));';

    if (slot.assigned) {
      const img = document.createElement('img');
      img.style.cssText = 'width:100%;height:100%;object-fit:cover;display:block;';
      img.alt = slot.label;
      img.src = _frameUrl(slot.slot_id);
      _camIntervals.push(setInterval(() => {
        img.src = _frameUrl(slot.slot_id);
      }, CAM_FPS));
      cell.appendChild(img);
    } else {
      const ph = document.createElement('div');
      ph.style.cssText = 'display:flex;flex-direction:column;align-items:center;'
        + 'justify-content:center;height:100%;color:var(--ink3);'
        + 'font-family:"Chakra Petch",sans-serif;font-size:11px;letter-spacing:.05em;gap:8px;';
      ph.innerHTML = '<span style="font-size:28px">&#128247;</span>NO CAMERA ASSIGNED';
      cell.appendChild(ph);
    }

    // Slot label overlay
    const lbl = document.createElement('div');
    lbl.style.cssText = 'position:absolute;bottom:0;left:0;right:0;'
      + 'background:rgba(0,0,0,.55);color:#fff;'
      + 'font-family:"Chakra Petch",sans-serif;font-size:10px;font-weight:700;'
      + 'letter-spacing:.08em;padding:4px 8px;';
    lbl.textContent = slot.label.toUpperCase();
    cell.appendChild(lbl);

    gridEl.appendChild(cell);
  });

  // If nothing ended up visible
  if (!fwSlot && gridSlots.length === 0) {
    msgEl.style.display = 'flex';
    msgEl.innerHTML = 'No cameras configured for display.<br>'
      + '<a href="/settings#section6" style="color:var(--g-txt);font-size:12px;">Camera Setup in Settings &rarr;</a>';
  }
}

function _frameUrl(slotId) {
  return CAM_API + '/camera/frame/' + slotId + '?t=' + Date.now();
}

function _setImgPlaceholder(imgEl, text) {
  // Replace img with a text placeholder div of the same dimensions
  const ph = document.createElement('div');
  ph.style.cssText = imgEl.style.cssText
    + 'display:flex;flex-direction:column;align-items:center;justify-content:center;'
    + 'color:var(--ink3);font-family:"Chakra Petch",sans-serif;font-size:11px;gap:8px;';
  ph.innerHTML = '<span style="font-size:32px">&#128247;</span>' + text;
  imgEl.replaceWith(ph);
}
