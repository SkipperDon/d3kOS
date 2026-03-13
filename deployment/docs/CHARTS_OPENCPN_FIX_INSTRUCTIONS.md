# Claude Code Task Instruction — Charts / OpenCPN Windowed Mode Fix
**Project:** d3kOS
**Files to change:** `index.html`, `charts.html`
**Risk level (AAO):** Low — editing two HTML files, reversible, no services touched
**Pre-action statement required:** Yes — state each file change before executing

---

## CONTEXT — Read Before Touching Any File

d3kOS runs Chromium as a kiosk application on a Raspberry Pi under a Wayland compositor (labwc). The main menu (`index.html`) runs fullscreen. Some menu items need Chromium to step back to **windowed mode** so the Pi desktop is exposed alongside the browser — this is done by calling `POST /window/windowed` on the keyboard API (port 8087, proxied by nginx).

The established pattern for buttons that require windowed mode is `goWindowed()` followed by a 350 ms delay then navigation. This pattern is already working and in production for **Helm**, **AI Assistant**, and **Onboarding**. Do not change those buttons.

**Correct behaviour for Charts (what Don confirmed):**
1. User taps Charts on main menu
2. Chromium exits fullscreen → Pi desktop becomes visible alongside Chromium
3. Browser navigates to `charts.html`
4. User taps "Launch OpenCPN Chart Plotter" on `charts.html`
5. Chromium stays windowed — OpenCPN opens on the Pi desktop
6. User freely switches between OpenCPN and the Chromium window
7. **There is no requirement to return to fullscreen when OpenCPN is closed** — the user controls that manually via the Toggle Fullscreen button already present on `index.html`

---

## TASK 1 — Fix `index.html`

**File location on Pi:** `/var/www/html/index.html`

### What is broken
The `charts` case in the `navigateToPage()` function does **not** call `goWindowed()`. It fires a direct Node-RED fetch to launch OpenCPN without first exiting fullscreen, so OpenCPN opens hidden behind Chromium. It also skips `charts.html` entirely, bypassing the instructions and launch button on that page.

### Find this exact block (the entire `charts` case inside `navigateToPage()`):

```javascript
        case 'charts':
          // Launch OpenCPN (auto-install if needed)
          alert('Launching Charts...\n\nOpenCPN will open in a moment.\nFirst time may take 30-60 seconds to install.');
          fetch('http://localhost:1880/launch-opencpn', {
            method: 'POST',
            mode: 'no-cors'
          }).catch((error) => {
            console.error('Failed to launch Charts:', error);
            alert('Failed to launch Charts. Please check the system.');
          });
          break;
```

### Replace it with exactly this:

```javascript
        case 'charts':
          goWindowed(function() { window.location.href = '/charts.html'; });
          break;
```

**Why:** This is identical in structure to the working helm, ai-assistant, and onboarding cases. `goWindowed()` calls `/window/windowed`, waits 350 ms, then navigates to `charts.html`. The fullscreen exit happens before the page change.

---

## TASK 2 — Fix `charts.html`

**File location on Pi:** `/var/www/html/charts.html`

### What is broken
The `launchOpenCPN()` function fires the Node-RED launch endpoint directly with no windowed-mode step. If the user navigates to `charts.html` from the corrected `index.html` the window will already be windowed — but the function should still defensively ensure windowed mode in case the page is ever reached by another path. The `alert()` calls also block the thread on a touch device and interfere with the fetch.

### Find this entire function:

```javascript
    function launchOpenCPN() {
      fetch('http://localhost:1880/launch-opencpn', { method: 'POST', mode: 'no-cors' })
        .then(() => {
          alert('🗺️ Launching OpenCPN...\n\n✓ GPS data automatically connected\n✓ Access via VNC or connected display\n\nNote: O-charts plugin requires manual installation (see instructions above)');
        })
        .catch(() => {
          alert('🗺️ Launching OpenCPN...\n\nIf it doesn\'t appear:\n• Check VNC connection\n• Launch from desktop menu');
        });
    }
```

### Replace it with exactly this:

```javascript
    function launchOpenCPN() {
      // Ensure Chromium is windowed so OpenCPN is visible on the Pi desktop.
      // The user can freely switch between OpenCPN and this browser window.
      fetch('/window/windowed', { method: 'POST' }).catch(function() {});
      // Small delay to let the window compositor settle before firing the launch.
      setTimeout(function() {
        fetch('http://localhost:1880/launch-opencpn', { method: 'POST', mode: 'no-cors' })
          .catch(function(error) {
            console.error('Failed to launch OpenCPN:', error);
          });
      }, 400);
    }
```

**Why:** Defensively calls `/window/windowed` first. Removes `alert()` calls that block the touch thread. 400 ms delay gives the compositor time to settle before Node-RED receives the launch command. No auto-return to fullscreen — user controls that.

---

## TASK 3 — Verify No Regressions

After making both changes, confirm the following by reading the files back:

1. **`index.html` — `navigateToPage()` switch block** — verify the `charts` case now reads:
   ```javascript
   case 'charts':
     goWindowed(function() { window.location.href = '/charts.html'; });
     break;
   ```

2. **`index.html` — other `goWindowed` cases unchanged** — confirm `helm`, `ai-assistant`, and `onboarding` cases are untouched.

3. **`index.html` — DOMContentLoaded** — confirm `fetch('/window/fullscreen', {method:'POST'})` is still present. This ensures the main menu returns to fullscreen when navigated back to.

4. **`charts.html` — `launchOpenCPN()`** — verify the function now calls `/window/windowed` before the setTimeout/fetch.

5. **`charts.html` — back button** — confirm `onclick="window.location.href='/'"` is still present on the `← Main Menu` nav button. When the user returns to `/`, `index.html` will call `/window/fullscreen` on load, restoring fullscreen naturally if the user wants to return to normal kiosk mode.

---

## WHAT NOT TO CHANGE

- Do not modify any systemd service files
- Do not modify `keyboard-api.py` or any Python API
- Do not modify nginx `default` config
- Do not modify any `.desktop` files
- Do not modify `helm.html`, `ai-assistant.html`, or `onboarding.html`
- Do not add any fullscreen-restore logic triggered by OpenCPN closing — this is intentionally omitted per operator instruction

---

## EXPECTED BEHAVIOUR AFTER FIX

```
User taps Charts
  → goWindowed() fires → /window/windowed called → Chromium exits fullscreen
  → 350 ms delay
  → Browser navigates to /charts.html
  → Pi desktop is now visible alongside the Chromium window
  → User taps "Launch OpenCPN Chart Plotter"
    → /window/windowed called (defensive, already windowed)
    → 400 ms delay
    → POST http://localhost:1880/launch-opencpn fires
    → OpenCPN opens on Pi desktop — VISIBLE
  → User switches freely between OpenCPN and Chromium
  → If user taps ← Main Menu in Chromium
    → index.html loads → /window/fullscreen fires → kiosk fullscreen restored
```

---

## STATUS — 2026-03-12

**Task 1 DONE** — `index.html` charts case updated to `goWindowed()` → `/charts.html`. Deployed to Pi.

**Task 2 DONE** — `charts.html` `launchOpenCPN()` rewritten — `alert()` removed, `/window/windowed` added, 400ms delay added. Deployed to Pi.

**Remaining issue:** `http://localhost:1880/launch-opencpn` fetch still fails — Node-RED (port 1880) is not proxied through nginx. Chromium cannot reach `localhost:1880` directly from page context.

**Pending fix (next session — v0.9.2):**
1. Add `location /launch-opencpn { proxy_pass http://127.0.0.1:1880; }` to nginx default config
2. Update `charts.html` `launchOpenCPN()` to call `/launch-opencpn` (relative path, through nginx)
3. Audit all other `http://localhost:1880` calls across HTML files for the same issue
4. `sudo nginx -t && sudo systemctl reload nginx` + test

---

## RELEASE PACKAGE MANIFEST

```
### Release Package Manifest
- Version: current → hotfix
- Update type: hotfix
- Changed files:
  | File        | Pi Path               | Partition | Change                                      |
  |-------------|-----------------------|-----------|---------------------------------------------|
  | index.html  | /var/www/html/        | base      | charts case: add goWindowed, navigate to charts.html, remove alert+direct-launch |
  | charts.html | /var/www/html/        | base      | launchOpenCPN: add /window/windowed call, remove alert calls |
- Pre-install steps: none
- Post-install steps: Hard-refresh Chromium (Ctrl+Shift+R or restart d3kos-browser service)
- Rollback: Restore previous index.html and charts.html from backup or git
- Health check: Tap Charts on main menu — Chromium should exit fullscreen and navigate to charts.html. Tap Launch — OpenCPN should appear on desktop.
- Plain-language release notes: Charts button now exits fullscreen before navigating, matching the same pattern used by Helm and AI Assistant. OpenCPN will be visible on the Pi desktop. User can switch freely between the two apps. No auto-fullscreen on OpenCPN close — user controls that manually.
```
