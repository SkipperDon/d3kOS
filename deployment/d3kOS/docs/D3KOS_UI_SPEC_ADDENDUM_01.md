# d3kOS UI Spec — Addendum 01
**Document:** `D3KOS_UI_SPEC_ADDENDUM_01.md`
**Amends:** `D3KOS_UI_SPEC.md` v1.0.0
**Version:** 1.0.0
**Date:** 2026-03-13
**Author:** Skipper Don / AtMyBoat.com
**Status:** APPROVED — supersedes conflicting content in D3KOS_UI_SPEC.md

---

## CLAUDE CODE: HOW TO USE THIS DOCUMENT

Read this addendum immediately after `D3KOS_UI_SPEC.md` at the start of every session.
Where this document conflicts with the base spec, **this document wins**.
The base spec is not wrong — this addendum extends and corrects specific sections only.
Sections not mentioned here remain unchanged.

---

## WHAT THIS ADDENDUM CHANGES

| Base Spec Section | Original Content | Status |
|---|---|---|
| Section 2 — Technology Stack | `--kiosk` mode listed | **REPLACED** |
| Section 4 — Hard Rules | No kiosk rule | **RULE ADDED** |
| Section 19 — Chromium Kiosk Mode | Full section | **REPLACED** |
| Section 24 — File Structure | No `scripts/` directory | **UPDATED** |
| Session 1 Build Plan (FINDINGS) | No window toggle step | **UPDATED** |

---

## REASON FOR CHANGE — READ THIS FIRST

This is not a preference change. This is a hard architectural constraint.

**The problem with `--kiosk` and `--start-fullscreen`:**

Raspberry Pi OS Trixie uses the **Wayland display protocol** with **labwc** as the compositor.
Under Wayland, every window is assigned a layer. The layer stack from bottom to top is:

```
background → bottom → normal windows → top → FULLSCREEN WINDOWS → overlay → lockscreen
```

Squeekboard (the system on-screen keyboard) renders on the **top** layer.
Chromium in `--kiosk` or `--start-fullscreen` mode renders on the **fullscreen** layer.
**The fullscreen layer is above the top layer.**
Squeekboard is therefore completely hidden behind Chromium in either fullscreen mode.
There is no workaround, configuration option, or flag that changes this.
It is a fundamental property of the Wayland layer protocol.

**The solution:**

Run Chromium as a **maximised normal window** using `--app --start-maximized`.
A maximised normal window sits on the **normal windows** layer — below Squeekboard.
The labwc compositor is configured to strip all window decorations from Chromium.
The result is visually identical to kiosk mode.
The result is functionally correct — Squeekboard floats above Chromium and works.

**This is the only correct architecture for a touch-input kiosk on Wayland/labwc.**

---

## ADDENDUM SECTION A — REPLACEMENT FOR SPEC SECTION 2 (TECHNOLOGY STACK)

Replace the Browser row in the technology stack table:

| Component | Technology |
|---|---|
| Browser | Chromium `--app --start-maximized` — NOT `--kiosk` (see Addendum Section C) |

All other rows unchanged.

---

## ADDENDUM SECTION B — NEW HARD RULE (APPENDS SPEC SECTION 4)

Add Rule 11:

> **11. Never use `--kiosk` or `--start-fullscreen`** — both modes place Chromium on the Wayland fullscreen layer, above Squeekboard, making the on-screen keyboard permanently invisible. Use `--app --start-maximized` exclusively. See Addendum Section C.

---

## ADDENDUM SECTION C — FULL REPLACEMENT FOR SPEC SECTION 19

**Delete Spec Section 19 in its entirety. Replace with the following.**

---

### 19. Display Mode — Maximised App Window (Wayland / labwc)

#### 19.1 Architecture Decision

d3kOS runs Chromium as a **maximised app window**, not in kiosk mode.

`--app` strips the browser chrome (tab bar, URL bar, toolbar). The window fills the display.
`--start-maximized` keeps the window on the Wayland normal layer, below Squeekboard.
labwc is configured to remove window decorations so no titlebar is visible.

**To anyone looking at the display: this is indistinguishable from kiosk mode.**
**To Wayland: this is a normal maximised window that Squeekboard can legally sit above.**

Do not change this to `--kiosk` or `--start-fullscreen`. See Addendum Reason section above.

---

#### 19.2 Chromium Launch Command

```bash
chromium-browser \
  --app=http://localhost:3000 \
  --start-maximized \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --disable-restore-last-session \
  --disable-session-crashed-bubble \
  --disable-features=TranslateUI \
  --enable-features=OverlayScrollbar \
  --check-for-update-interval=31536000 \
  --ozone-platform=wayland
```

This command lives in the launch script at:
`/home/boatiq/Helm-OS/deployment/d3kOS/scripts/launch-d3kos.sh`

---

#### 19.3 Launch Script — Full File

```bash
#!/bin/bash
# d3kOS launch script
# Location: /home/boatiq/Helm-OS/deployment/d3kOS/scripts/launch-d3kos.sh

# Prevent crash-restore prompt on next boot
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' \
  /home/boatiq/.config/chromium/Default/Preferences 2>/dev/null
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' \
  /home/boatiq/.config/chromium/Default/Preferences 2>/dev/null

# Launch Chromium as maximised app window
chromium-browser \
  --app=http://localhost:3000 \
  --start-maximized \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --disable-restore-last-session \
  --disable-session-crashed-bubble \
  --disable-features=TranslateUI \
  --enable-features=OverlayScrollbar \
  --check-for-update-interval=31536000 \
  --ozone-platform=wayland
```

Make executable:
```bash
chmod +x /home/boatiq/Helm-OS/deployment/d3kOS/scripts/launch-d3kos.sh
```

---

#### 19.4 labwc Configuration — Window Rules

File: `/home/boatiq/.config/labwc/rc.xml`

Add the following `<windowRules>` block. If the file already contains a `<windowRules>` block,
add the two rules inside the existing block. Do not create a duplicate block.

**IMPORTANT: Preserve the existing ILITEK touch rule:**
```xml
<touch deviceName="ILITEK ILITEK-TP" mouseEmulation="no" />
```
This entry MUST remain in rc.xml. Losing it breaks all scroll (converts touch to mouse).
Do not remove it when editing rc.xml.

```xml
<windowRules>
  <!-- Strip title bar and decorations from Chromium -->
  <windowRule identifier="chromium*" serverDecoration="no"/>
  <!-- Maximise on open, hide from taskbar and window switcher -->
  <windowRule identifier="chromium*"
              skipTaskbar="yes"
              skipWindowSwitcher="yes">
    <action name="Maximize"/>
  </windowRule>
</windowRules>
```

**Verify the identifier:** Run `lswt` or `wlrctl toplevel list` while Chromium is open to confirm
the app_id. It will be either `chromium` or `chromium-browser`. Use `chromium*` to match both.

After editing rc.xml, reload labwc without rebooting:
```bash
labwc --reconfigure
```

---

#### 19.5 labwc Autostart

File: `/home/boatiq/.config/labwc/autostart`

Ensure the following entries are present. Do not remove existing entries unless explicitly listed
here as to be removed.

```bash
# Hide cursor on touchscreen (no cursor visible on helm display)
unclutter-xfixes --hide-on-touch &

# Enable Squeekboard system keyboard
gsettings set org.gnome.desktop.a11y.applications screen-keyboard-enabled true

# DO NOT start wf-panel-pi — no taskbar behind d3kOS
# wf-panel-pi &    ← comment out or remove if present

# Launch d3kOS after compositor is ready
sleep 3 && /home/boatiq/Helm-OS/deployment/d3kOS/scripts/launch-d3kos.sh &
```

---

#### 19.6 Squeekboard — On-Screen Keyboard

Squeekboard is the system on-screen keyboard for Raspberry Pi OS Trixie on Wayland.

**How it works with d3kOS:**
- Squeekboard is always running in the background (started via autostart)
- When any `<input>` or `<textarea>` receives focus, Squeekboard automatically slides up
- When the field loses focus (blur), Squeekboard dismisses automatically
- Chromium window is resized by the compositor to accommodate the keyboard height
- The active input field is never hidden behind the keyboard
- No code in d3kOS is required to show or hide Squeekboard

**This is why `--app --start-maximized` is required.**
Squeekboard does this correctly only when Chromium is on the normal window layer.

**Language configuration — 18 languages:**
Squeekboard reads the active keyboard layout from the system input-sources setting:
```bash
gsettings get org.gnome.desktop.input-sources sources
# Returns: [('xkb', 'us'), ('xkb', 'de'), ('xkb', 'ar'), ...]
```

All language configuration is done at the OS level via `raspi-config` or Settings.
d3kOS does **not** manage keyboard layouts.
d3kOS does **not** install, configure, or modify Squeekboard.
All 18 languages (Arabic, Japanese, Ukrainian, German, etc.) are handled by the OS.

**The only d3kOS responsibility for language:**
Set `recognition.lang` in `helm.js` based on `UI_LANG` from `vessel.env`.
See Section 19.8 below.

**Install Squeekboard if not present:**
```bash
sudo apt install squeekboard
```

**Verify Squeekboard is running:**
```bash
systemctl --user status squeekboard
# or force show for testing:
busctl call --user sm.puri.OSK0 /sm/puri/OSK0 sm.puri.OSK0 SetVisible b true
```

---

#### 19.7 Windowed Mode Toggle

d3kOS provides a windowed mode toggle in the More menu. This allows Don to temporarily
restore the window (e.g. to access the desktop for diagnostics) and return to maximised mode.

**Required system package:**
```bash
sudo apt install wlrctl
```

`wlrctl` is a native Wayland tool that communicates directly with the labwc compositor.
It requires no daemon, no xdotool, no X11 bridge.

**Implementation note:** These endpoints should be added to `keyboard-api.py` at :8087,
which already handles window state management. Do NOT add them to `app.py` — that would
duplicate the existing window control service.

**Endpoints — add to `keyboard-api.py`:**

```python
import subprocess

_window_maximized = True  # Track state server-side

@app.route('/window/maximize', methods=['POST'])
def window_maximize():
    global _window_maximized
    _window_maximized = True
    subprocess.Popen(['wlrctl', 'toplevel', 'maximize', 'on',
                      'app_id:chromium'])
    return jsonify({'maximized': True})

@app.route('/window/restore', methods=['POST'])
def window_restore():
    global _window_maximized
    _window_maximized = False
    subprocess.Popen(['wlrctl', 'toplevel', 'maximize', 'off',
                      'app_id:chromium'])
    return jsonify({'maximized': False})

@app.route('/window/state')
def window_state():
    return jsonify({'maximized': _window_maximized})
```

**More menu button — in `nav.js`:**

```javascript
// Windowed mode toggle — More menu button id="btnWindowMode"
async function toggleWindowMode() {
  const { maximized } = await fetch('/window/state').then(r => r.json());
  const endpoint = maximized ? '/window/restore' : '/window/maximize';
  await fetch(endpoint, { method: 'POST' });
  updateWindowModeLabel(!maximized);
}

function updateWindowModeLabel(isMaximized) {
  const btn = document.getElementById('btnWindowMode');
  if (!btn) return;
  btn.querySelector('.mm-label').textContent =
    isMaximized ? 'Fullscreen' : 'Windowed Mode';
  btn.querySelector('.mm-icon').textContent = isMaximized ? '⛶' : '⊡';
}
```

**More menu button label:**
- When maximised: `⊡  Windowed Mode` (sub-label: "Access desktop")
- When windowed: `⛶  Fullscreen` (sub-label: "Return to helm display")

This button occupies position 9 in the More menu 3×3 grid (bottom right).
It replaces the old "Exit to Desktop" entry from the previous spec.

---

#### 19.8 Voice Language — `UI_LANG` in vessel.env

Add `UI_LANG` to `config/vessel.env`:

```bash
VESSEL_NAME=MV SERENITY
HOME_PORT=Kingston
UI_LANG=en-GB
```

`UI_LANG` must be a valid BCP 47 locale tag (same format as Web Speech API `lang`).

Examples:
| Language | UI_LANG value |
|---|---|
| English (UK) | `en-GB` |
| English (US) | `en-US` |
| German | `de-DE` |
| Arabic | `ar-SA` |
| Japanese | `ja-JP` |
| Ukrainian | `uk-UA` |

Flask passes `UI_LANG` to the Jinja2 template as `{{ ui_lang }}`.

In `helm.js`, set recognition language on initialisation:
```javascript
recognition.lang = '{{ ui_lang }}';  // Injected by Flask
```

If `UI_LANG` is missing from `vessel.env`, default to `'en-GB'`.

---

## ADDENDUM SECTION D — UPDATED FILE STRUCTURE (APPENDS SPEC SECTION 24)

Add the `scripts/` directory to the file structure:

```
/home/boatiq/Helm-OS/deployment/d3kOS/
├── scripts/
│   └── launch-d3kos.sh        ← Chromium launch script (chmod +x)
```

Add `UI_LANG` to the vessel.env documentation:

```
config/vessel.env contents:
  VESSEL_NAME=   (vessel name)
  HOME_PORT=     (home port)
  UI_LANG=       (BCP 47 locale tag, e.g. en-GB, de-DE, ja-JP)
```

---

## ADDENDUM SECTION E — SESSION 1 BUILD ORDER CHANGE

In the FINDINGS document Session 1 build plan, insert the following as step 0
(before all other steps):

**Step 0 — System prerequisites (run once on Pi, not in every session)**

```bash
# Install required packages
sudo apt install squeekboard wlrctl unclutter-xfixes

# Configure labwc rc.xml window rules (see Addendum Section C 19.4)
# Configure labwc autostart (see Addendum Section C 19.5)
# Reload labwc
labwc --reconfigure

# Verify Squeekboard appears when tapping an input field in any app
# Verify wlrctl can communicate with compositor
wlrctl toplevel list
```

After step 0, all other Session 1 steps proceed unchanged.

---

## ADDENDUM SECTION F — DEPENDENCY MANIFEST UPDATE

Add the following to the deployment dependency list:

| Package | Install | Purpose |
|---|---|---|
| `squeekboard` | `sudo apt install squeekboard` | On-screen keyboard for all 18 languages |
| `wlrctl` | `sudo apt install wlrctl` | Wayland window state control (maximize/restore) |
| `unclutter-xfixes` | `sudo apt install unclutter-xfixes` | Hide cursor on touchscreen |

All three are Trixie packages. No PPAs, no third-party sources, no pip installs.

---

## SUMMARY OF ALL SPEC CHANGES

| What changed | Where | Action for Claude Code |
|---|---|---|
| `--kiosk` → `--app --start-maximized` | Section 2, Section 19 | Use new launch command only |
| Hard rule against `--kiosk` | Section 4 | Never use `--kiosk` or `--start-fullscreen` |
| labwc rc.xml window rules | Section 19.4 | Add rules before Session 1 (preserve ILITEK touch rule) |
| labwc autostart | Section 19.5 | Configure before Session 1 |
| Squeekboard replaces custom keyboard | Section 19.6 | Install, no app code needed |
| wlrctl windowed toggle (keyboard-api.py) | Section 19.7 | Add to keyboard-api.py + More menu button |
| `UI_LANG` in vessel.env | Section 19.8 | Add to vessel.env, wire to helm.js |
| `scripts/launch-d3kos.sh` new file | Section 24 | Create and chmod +x |
| Step 0 system prerequisites | Session 1 | Run once before Session 1 begins |

---

*Addendum version 1.0.0 — 2026-03-13*
*Deployed to: `/home/boatiq/Helm-OS/deployment/d3kOS/docs/D3KOS_UI_SPEC_ADDENDUM_01.md`*
*Owner: Skipper Don / AtMyBoat.com*
*Read alongside: `D3KOS_UI_SPEC.md`, `D3KOS_V12_FINDINGS.md`*
