# BUG-129 — Camera Discovery: No Credential Guidance · Atomic Spec

**Document:** V09995-BUG129-001 · **Version:** 1.0 · **Date:** 2026-09-15 (S164)
**Author:** Tier 2 (Sonnet) · **Implementer:** Tier 3 (qwen2.5-coder:7b)
**Bug severity:** Medium — users cannot complete camera setup without knowing RTSP URL format or credentials
**Root cause confirmed:** S164 — template list read; setup.html and settings.html confirmed present

---

## 1. Root Cause

Camera setup UI (wizard and settings page) allows users to enter camera RTSP URLs and
credentials but provides zero guidance on:
- What format an RTSP URL takes (e.g. `rtsp://admin:pass@192.168.1.x:554/stream`)
- Default credentials for common IP cameras
- How to find the camera's IP address
- What port to use (554 is standard, but some cameras differ)

Result: operators are left to guess. Discovery fails silently. Marine Vision never works.

---

## 2. Files Changed

| # | File | Op | Description |
|---|------|----|-------------|
| 1 | `deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/setup.html` | modify | Add camera credential help text to wizard camera step |
| 2 | `deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/settings.html` | modify | Add camera credential help panel to settings camera section |
| 3 | `deployment/v0.9.9.4/opt/d3kos/config/cameras-config.json` | create | Template config with commented format examples |

Fix goes in v0.9.9.4 tree (bug fix, not new feature). Both templates confirmed present.

---

## 3. Guidance Content — Exact Text

The same content block goes into both setup.html and settings.html.
Use a `<div class="camera-help">` wrapper for CSS targeting.

```html
<div class="camera-help" style="background:#f4f8ff;border-left:4px solid #2c7be5;padding:12px 16px;margin:12px 0;border-radius:4px;">
  <p style="font-size:18px;font-weight:600;margin:0 0 8px 0;">Camera RTSP URL Format</p>
  <p style="font-size:18px;margin:0 0 6px 0;">Most IP cameras use this format:</p>
  <code style="font-size:18px;display:block;background:#e8f0ff;padding:8px;border-radius:3px;margin-bottom:8px;">rtsp://admin:password@192.168.1.x:554/stream</code>
  <p style="font-size:18px;margin:0 0 4px 0;"><strong>Common defaults:</strong></p>
  <ul style="font-size:18px;margin:0 0 8px 0;padding-left:20px;">
    <li>Hikvision: <code>rtsp://admin:admin@[IP]:554/Streaming/Channels/101</code></li>
    <li>Dahua: <code>rtsp://admin:admin@[IP]:554/cam/realmonitor?channel=1&amp;subtype=0</code></li>
    <li>Generic IP cam: <code>rtsp://admin:12345@[IP]:554/stream1</code></li>
    <li>Reolink: <code>rtsp://admin:[pass]@[IP]:554/h264Preview_01_main</code></li>
  </ul>
  <p style="font-size:18px;margin:0;color:#555;">To find your camera's IP: check your router's connected devices list. Port 554 is standard. Default username is usually <code>admin</code>.</p>
</div>
```

**AODA requirement:** all font sizes ≥18px. The inline styles above enforce this.
Do NOT use a smaller font for the code examples.

---

## 4. cameras-config.json Template

Create at `deployment/v0.9.9.4/opt/d3kos/config/cameras-config.json`:

```json
{
  "_comment": "d3kOS camera configuration. Add cameras below. Remove this comment in production.",
  "_format": "rtsp://username:password@ip_address:port/stream_path",
  "cameras": []
}
```

This file serves as the empty-state template. When Marine Vision discovers a camera,
it populates the `cameras` array. The template ensures the file exists so Marine Vision
doesn't fail with a missing-file error on first boot.

---

## 5. Guard Test

File: `tests/test_bug129_camera_guidance.py`

```
test_setup_page_contains_rtsp_help:
  - Flask test client: GET /setup
  - Assert response body contains "camera-help"
  - Assert response body contains "rtsp://"
  - Assert response body contains "554"

test_settings_page_contains_rtsp_help:
  - Flask test client: GET /settings (with vessel.env present to pass wizard gate)
  - Assert response body contains "camera-help"
  - Assert response body contains "rtsp://"

test_cameras_config_json_valid:
  - Read deployment/v0.9.9.4/opt/d3kos/config/cameras-config.json
  - Assert json.loads() succeeds without error
  - Assert "cameras" key exists and is a list
```

Minimum bar: all 3 pass before BUG-129 is marked done.

---

## 6. Dispatch Block for Tier 3

```
TASK: BUG-129 — Camera Credential Guidance
IMPLEMENTER: Tier 3 (qwen2.5-coder:7b)

DELIVERABLES:

1. Modify deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/setup.html
   - Find the camera setup step/section (search for "camera" or "rtsp" in the file)
   - Insert the guidance block from spec §3 VERBATIM immediately before the RTSP URL input field
   - If no camera section exists in setup.html, insert before the final "Next" button
     of the wizard and note this deviation in your preflight report

2. Modify deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/settings.html
   - Find the camera settings section (search for "camera" or "rtsp" in the file)
   - Insert the guidance block from spec §3 VERBATIM immediately before the first
     camera URL input field in that section
   - If no camera section exists, insert at the end of the page before </main> or </body>
     and note the deviation in your preflight report

3. Create deployment/v0.9.9.4/opt/d3kos/config/cameras-config.json
   - Content verbatim from spec §4

4. Create tests/test_bug129_camera_guidance.py
   - Three test functions from spec §5
   - Flask test client needs vessel.env present in tmpdir for /settings test
   - All three must pass

PRE-FLIGHT: Before writing, search both template files for "camera" and "rtsp" (case-insensitive).
Report what you find and where you will insert the guidance block. Do not insert until confirmed.

CONSTRAINTS:
- Font size minimum 18px everywhere — AODA requirement, zero exceptions
- Do NOT modify app.py or any Python files
- Do NOT add any new routes or endpoints
- Inline styles are acceptable for the guidance div (avoid CSS class conflicts)
- The &amp; entities in the Dahua URL must stay as HTML entities in the template

VERIFICATION:
[ ] Guidance block appears in setup.html before/near the RTSP URL field
[ ] Guidance block appears in settings.html before/near the camera settings
[ ] cameras-config.json is valid JSON with "cameras": []
[ ] All font sizes in the guidance block >= 18px
[ ] All 3 tests pass
```
