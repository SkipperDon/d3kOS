# d3kOS Changelog

All notable changes to d3kOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v0.9.9.5.1] — Pi Health RSS Alerting · CAN Auto-Detect · issues.db Retention — 2026-10-24

Patch release extending the D27-RSS notification system and adding automatic CAN adapter detection. Delivered as a signed OTA package from GitHub; verified on Pi 4, Pi 5 and the test Pi on 2026-10-24.

### Fixed

- **BUG-293: Pi health pill button** — Replaced static non-clickable dot (5-min poll, often stale) with a self-injecting clickable pill button on all 5 dashboard pages (index, engine-monitor, anchor-watch, marine-vision). Pill shows Pi: OK / Pi: WARN / Pi: CRITICAL in green / amber / red. Click opens a detail modal listing every agent's current status and last-updated time. Poll interval reduced from 300 s to 60 s.
- **BUG-273: CAN adapter auto-detection** — `hardware-probe.sh` now detects PiCAN-M (can0 + mcp251x driver) and USB-CAN-A (USB ID 1a86:7523) automatically. Switches the correct Signal K provider on/off, enables/disables can0-check timer and usbcan bridge service, and restarts Signal K only when configuration changes. Self-installs systemd units and udev rule from `/opt/d3kos/system/` (OTA-deliverable). udev hot-plug trigger re-runs the probe on USB adapter insert/remove. Every cloned Pi now configures itself correctly without manual intervention.
- **BUG-306: Helm voice restored** — v0.9.9.5 shipped an untested rewrite of `voice-assistant-hybrid.py` that never answered a question that never answered a question on the test Pi. Restored the last working version. Verified on the test Pi: wake word "Helm" → question heard → answer spoken, including after a reboot.
- **BUG-307: Helm faster time answers + no mid-answer restarts** — the voice watchdog now waits 45 s and rechecks before restarting Helm (Helm pauses its wake-word listener while answering, which the watchdog mistook for a fault). Bare "time" added to Helm's quick-answer list, so "time is it" (Vosk often drops "what") no longer loads the 12 s manual-search engine — measured 0.4 s vs 12.1 s on the test Pi.
- **BUG-308: SafeHelm speaks in Helm's voice** — ai-bridge (SafeHelm and other alerts) used robotic espeak-ng. `_piper()` in `ai-bridge/utils/tts.py` now plays with `aplay` (its old sounddevice player was silent under systemd), and OTA migration `0006-tts-piper.sh` switches ai-bridge to Piper when Piper and its voice model are installed. Ear-tested on the test Pi.
- **BUG-309: Helm no longer wakes itself on SafeHelm alerts** — now that SafeHelm speaks in Helm's clear voice, "SafeHelm …" could trigger Helm's wake word. Helm ignores its wake word while ai-bridge is speaking and for 3 s after (stale speaking flag ignored after 60 s).
- **BUG-310: Helm answers no longer lost; SafeHelm always has the speaker first** — Helm, SafeHelm and other ai-bridge alerts each grabbed the S330 speaker directly, so an answer could be silently dropped ("Device or resource busy"). ai-bridge (`utils/tts.py`) now owns the speaker through one priority queue: urgent alerts (SafeHelm, anchor drag) say "Captain, standby.", pause 4 s, then speak, and Helm gets "Captain, ask the question again. We were interrupted." if it was cut off; busy speaker is retried and never silently dropped. Helm (`voice-assistant-hybrid.py`) speaks through the queue (`POST :3002/speak`), waiting up to 30 s for ai-bridge at boot. Helm no longer hears its own speaker (mic audio discarded while ai-bridge speaks — monotonic flag, immune to the boot clock jump), no longer wakes on talk or steady noise (`wake_word_vosk.py`: `[unk]` + wake word must be ≤ 1.5 s), and the voice watchdog uses a Helm heartbeat (`/dev/shm/d3kos-helm-heartbeat.json`) instead of thread counting, so it no longer restarts Helm mid-answer (supersedes the BUG-307 45 s recheck). Verified by ear test on the test Pi.
- **BUG-311: OTA refuses downgrades** — the installer now rejects any release whose version is older than the installed one (result "not_newer"); re-applying the same release stays harmless.
- **BUG-300/301: SafeHelm widget restored; stray battery cell removed** — main dashboard layout regression fixed.
- **Dashboard: 3D button removed** — the 3D row button is removed from the main dashboard row selector; the old "Pi: OK" text indicator is replaced by the BUG-293 health pill on the main page.

### Added

- **RSS health alerting** — `GET /rss` (port 3000) now includes Pi health events when overall agent status is warning or critical. Description lists every non-green agent with its message. Stable guid (`pi-health-yellow` / `pi-health-red`) prevents d3kTV duplicate ticker entries for ongoing conditions.
- **"All systems OK" RSS item** — When no active alerts exist, the feed emits a single `INFO: d3kOS — All systems OK` item so d3kTV always has content to display.
- **1-hour issues.db auto-prune** — `alert_watcher` now deletes issues.db records older than 1 hour at each 30-second poll cycle. Prevents simulator data and resolved alerts from accumulating in the RSS feed.


## [v0.9.9.5] — OTA Self-Update · Helm Voice AI · SafeHelm · USB-CAN-A — 2026-10-09

The most significant d3kOS release since v0.9.9.4. Five headline capabilities: automated over-the-air updates (Pi now keeps itself current without operator intervention), the Helm Voice AI assistant, SafeHelm collision avoidance advisory, USB-CAN-A NMEA 2000 adapter support, and a fully redesigned AIS subsystem. Dozens of stability, first-boot, and wizard reliability fixes included. Lab-validated on Raspberry Pi 3B+, Pi 4, and Pi 5.

### Headline Capabilities

- **Over-the-Air Update (OTA)** — d3kOS now self-updates from the cloud. When an update is queued via the AtMyBoat.com admin panel the dashboard shows an amber "Update Available" pill. Two taps install the update in the background; the Pi restarts services automatically. Full-state signed packages cover every file in `/opt/d3kos`. ECDSA signature verification, SHA-256 integrity check, automatic rollback on failure, and numbered migration scripts guarantee clean installs. No SD card swap, no SSH session required.

- **Helm Voice AI (D-VA-01)** — Always-on in-browser voice assistant. Say the wake word "Helm", ask a question, hear the answer spoken back. Vosk speech-to-text on-Pi; Piper TTS; Gemini language model via ai_bridge with RAG from your boat and engine manuals. Works offline (answers from general knowledge when internet or API key unavailable). Configure Gemini API key from the Settings page. No browser extension — pure WebRTC microphone.

- **SafeHelm Collision Avoidance Advisory (D02)** — Background service monitors AIS targets and computes CPA/TCPA using COLREGs Rules 13, 14, 15, and 18. Advisory-only (no false alarms while moored or at low speed). Three-tier alert gate: critical / warning / advisory. Stand-on escalation follows Rule 17. Alerts appear as status-bar pills on every dashboard page; spoken alerts use the voice arbiter with a 15-second inter-announcement gap.

- **USB-CAN-A NMEA 2000 Support** — CAN adapter auto-detection on boot. `can-autodetect.sh` identifies whether a PiCAN-M (SPI) or USB-CAN-A (USB) adapter is connected and brings up `can0` at 250 kbps automatically. No manual configuration required. Signal K receives engine, GPS, and AIS data from whichever adapter is present.

- **AIS Redesign** — `ais-catcher` replaces `rtl_ais`. UDP delivery to Signal K (no TCP server dependency), community telemetry disabled by default (`-X off`), udev hotplug rule for RTL-SDR dongle. AIS works reliably from first boot. Targets appear on AvNav chart overlay.

- **AtMyBoat.com Integration** — Complete device registration and account-pairing flow. Scan QR code in the wizard → visit `atmyboat.com/register/?rt=TOKEN` → account created and Pi paired in one atomic operation. Per-device Ed25519 authentication. Device approval email sent to owner on admin approval. Settings page shows device token and pairing status.

### New Features

- **Signal K Forward Watch v0.2.5 (signalk-forward-watch)** — Alarms persist across 3 consecutive detection cycles (or immediately when target is ≤75 m); auto-clear when target no longer detected; alerts suppressed below 1.0 kn (moored). Sea trial validation: moored false alarms 97→0, approaching vessels correctly detected. LatLon geodesy replaced with spherical formula (ESM compatibility fix).

- **D16 Marine Vision 3D Surround View** — Row-ribbon button added to Marine Vision panel. Validated on Pi 4: CPU < 3.0 load average, 30 FPS stable.

- **Marine Vision View Mode Bar** — View mode selector in the Marine Vision panel header for quick switching between live, playback, and detection modes.

- **SafeHelm Global Persistent Widget** — `safehelm-global.js` self-injecting widget on all 6 operational dashboard pages. Always-on SSE to port 8096; pill dismisses on tap, reappears on next alert. AODA 18 px / 48 px compliant.

- **Boot Disclaimer Gate (D19)** — Legal disclaimer shown on every new session; user must tap "I Agree" before reaching the dashboard. Sanitize script removes the session flag so every fresh image shows the gate on first boot.

- **Vessel Setup Wizard (HCD-8)** — Full 9-step onboarding: vessel name, propulsion type, vessel length class, GPS provider, AIS provider, NMEA 2000 adapter, Signal K host, AtMyBoat.com registration, summary. Runs only on new or wiped installs. Preceded by a mandatory password-change step.

- **Boat Log Auto-Capture** — `boatlog_capture.py` + `d3kos-boatlog-capture.service`. Engine data captured server-side without requiring the Boat Log page to be open.

- **Timezone Auto-Detection** — `detect-timezone.sh` sets correct local timezone on first boot from ip-api.com; falls back to worldtimeapi.org → ipapi.co.

- **Signal K Source Priorities** — SOG/COG now use a single authoritative source; dashboard no longer alternates between GPS and N2K values.

- **Anchor Watch Restored** — Anchor watch endpoint corrected to point at ai_bridge (`localhost:3002`). "Set Anchor" button now arms reliably.

- **AI Self-Tuning** — Gemini API key saved in Settings persists across reboots. RAG layer uses boat and engine manual excerpts for context-aware answers. Offline fallback uses general knowledge automatically.

### Removed

- **CX5106 N2K Engine Bridge** — Removed. Engine data is now delivered exclusively via NMEA 2000 CAN bus (USB-CAN-A or PiCAN-M) and Signal K. The CX5106 serial protocol was unreliable on real hardware; the bridge has been dropped. "NMEA 2000" label replaces the former OEM name in the wizard.

### First-Boot Reliability

Complete overhaul of the first-boot experience for new installs and cloned images:

- Clone identity regeneration on every first boot (new `device-token.json`, SSH host keys, `installation_id`)
- Change-password step precedes wizard — wizard cannot run on factory credentials
- Five OTA migrations shipped with the base image, applied on first OTA update
- nginx `/network/` proxy corrected — all password-change and onboarding API routes reachable from kiosk browser
- Chromium auto-launches in kiosk mode with correct Wayland environment variables
- Plymouth boot splash displays correctly at Tier 0
- SSH host keys regenerate before sshd starts
- `fake-hwclock` masked (no RTC hardware on Pi 4 / Pi 5)
- Sanitize script removes `vessel.env`, sessions, logs, and WiFi profiles before imaging

### Bug Fixes

**Dashboard and UI:**
- **BUG-26** — Anchor watch "Set Anchor" endpoint pointed at wrong service; now arms correctly
- **BUG-27** — Status bar font sizes below AODA 18 px minimum; `.sb-vessel` and `#clk` corrected
- **BUG-41** — `/settings` HTTP 500 on load (`tier_num`/`device_token` template variables missing)
- **BUG-50** — System Status page reported GPS/AIS/AvNav healthy when services were not running
- **BUG-82** — Boat Log UI now fetches and merges server-side log entries on page load
- **BUG-151** — AODA font size violations in `hardware.html`, `cameras.js`, `remote-access.html`
- **BUG-172** — Chromium 107% CPU / system load 3.89+ on idle dashboard; resolved

**Services and Stability:**
- **BUG-108** — `api-keys.json` had no creation mechanism; first-boot generation added
- **BUG-132** — `camera_stream_manager.py` RTSP init was synchronous in main thread; now non-blocking (commit `0faf9fc4`)
- **BUG-134** — `d3kos-camera-stream.service` ExecCondition failed-closed on network issues; now fail-open (commit `c6abd40c`)
- **BUG-136** — `d3kos-fish-detector.service` same fail-closed ExecCondition; same fail-open fix (commit `fd4e2fd8`)
- **BUG-137** — `d3kos-go2rtc.service` permission denied on config file at boot (commit `354c00fa`)
- **BUG-141** — `d3kos-live` crash-loop: log file owned by root; ownership corrected
- **BUG-142** — `d3kos-fish-detector` crash-loop: ONNX model absent from image
- **BUG-143** — `d3kos-voice` crash-loop: Vosk and Piper models absent
- **BUG-144** — `d3kos-voice-watchdog` fails: watchdog script missing
- **BUG-145** — `d3kos-export-daily` fails: export script missing; restored
- **BUG-148** — `d3kos-fleet-push` crash-loop: missing env file
- **BUG-149** — `d3kos-fish-detector.service` `StartLimitIntervalSec` in wrong unit file section
- **BUG-150** — `d3kos-boatlog-api.service` deprecated `MemoryLimit=` directive
- **BUG-163** — `fake-hwclock-load.service` fails on Pi without RTC hardware; masked
- **BUG-170** — Watchdog CRITICAL_PATHS stale entry generated 1,152 false CRITICAL log entries per day
- **BUG-171** — Watchdog false "services tree corrupt" alert every 5 minutes
- **BUG-270** — Export scripts missing from image; restored
- **BUG-281** — OTA packages installed scripts without executable bit; build script now chmod 755 all shebangs

**Voice / Helm AI:**
- **BUG-174** — D-VA-01 UtteranceGate truthiness bug caused missed responses
- **BUG-175** — D-VA-01 TURN config test failure
- **BUG-177** — Helm Voice required device pairing; blocked Tier 0 users; gate removed
- **BUG-199** — Helm Voice "I didn't understand": RAG disabled, no manual content loaded; RAG re-enabled
- **BUG-200** — Gemini API key save in Settings was a non-functional stub; now saves and persists
- **BUG-201** — Onboarding wizard Gemini key field name mismatch; corrected
- **BUG-202** — `POST /gemini/config` echoed full API key in JSON response; masked value returned

**OTA System:**
- **BUG-223** — Update pill never appeared on :80 kiosk (cross-origin :3000); same-origin URLs enforced
- **BUG-260** — OTA could only update `/opt/d3kos` files; full-state signed packages introduced
- **BUG-261** — OTA never updated `version.txt`; migration 0001 now updates installed version
- **BUG-273** — CAN adapters not auto-detected on boot; `can-autodetect.sh` + service added (OTA migration 0002)
- **BUG-277** — Update pill continued to offer "Update Available" during active install
- **BUG-278** — New agent/pill code did not take effect after OTA update
- **BUG-279** — Settings offered rollback from stale pre-release backup; removed

**AIS and Signal K:**
- **BUG-19/20** — `fetchAis="true"` and `aisQueryPeriod="5"` added to `avnav_server.xml`; AIS targets appear on chart overlay
- **BUG-32** — `rtl_ais` port conflict with Signal K TCP 10110; directed to dedicated port 10108
- **BUG-100** — AvNav apt GPG key missing from image; key `06B67AB0E988310475E75A2746E95F3C8A61623B` installed to keyring
- **BUG-125** — `rtl-ais.service` looped forever when no SDR dongle attached
- **BUG-126** — Signal K GPS and AIS providers not pre-configured; now included in base image
- **BUG-159** — Pangoo src 64 injected false engine data with engine off; `signalk-suppress-pangoo` installed
- **BUG-248** — `ais-catcher` replaces `rtl_ais`: more reliable decode, UDP delivery, no community telemetry
- **BUG-250** — ais-catcher shared data with aiscatcher.org by default; disabled with `-X off`
- **BUG-251** — ais-catcher restarted immediately after `systemctl stop`

**AtMyBoat.com / Registration:**
- **BUG-111** — Registration created unlinked accounts; now creates account + links Pi atomically
- **BUG-112** — Wizard QR encoded `d3kos://register` (unresolvable deep link); corrected to `atmyboat.com/register/?rt=TOKEN`
- **BUG-113** — qrcodejs loaded from CDN only; vendored locally for offline use
- **BUG-114** — Token displayed with `R-` prefix rejected by validators; prefix stripped before display
- **BUG-115** — PWA login screen had no registration link; "Create one" added
- **BUG-116** — Settings page missing AtMyBoat.com section and QR display; full panel added
- **BUG-117** — Registration token remained valid after use; now marked `used_at` on redemption
- **BUG-118** — `amboat_reg_tokens` table missing `pi_id` and `device_token` columns; schema corrected
- **BUG-119** — Logged-in users visiting registration URL saw form again; now auto-links and redirects
- **BUG-120** — Admin approval sent no email to device owner; `wp_mail()` to contact_email added
- **BUG-121** — No way to skip AtMyBoat.com registration section; "Skip" button added
- **BUG-146** — `d3kos-auto-enrol` HTTP 400: `public_key` format rejected by server; corrected
- **BUG-155** — `ota-queue.php` tier gate returned HTTP 403 for all devices; fixed

**First Boot and Image:**
- **BUG-152** — OTA rsync failed on root-owned Plymouth splash file
- **BUG-153** — OTA deleted rollback directory on success; "Revert" option never appeared
- **BUG-154** — Flask rollback thread died when service stopped itself
- **BUG-157** — `first-boot-setup.sh` missing execute permission
- **BUG-263** — Cloned devices shared one device identity; unique identity regenerated per-device on first boot
- **BUG-276** — Hard-coded factory password in camera credentials; moved to config file
- **BUG-283** — SSH host keys regenerated after sshd started, causing boot failure; ordering fixed
- **BUG-285** — Sanitize script did not remove `vessel.env`; device shipped with stale owner data
- **BUG-287** — nginx stripped `/network` prefix; all onboarding API routes returned 404 from kiosk
- **BUG-288** — Change-password flow unreachable from kiosk at first boot
- **BUG-289** — "CX5106 DIP Switch Setup" wizard step label still shown after CX5106 removal
- **BUG-290** — "Garmin NMEA 2000" OEM label in wizard; replaced with "NMEA 2000"

**Setup Wizard:**
- **BUG-291** — `POST /setup` rejected empty `vessel_name`; LAUNCH button silently reloaded wizard with no error shown; fallback `'My Vessel'` added to `app.py`
- **BUG-292** — Chromium HTML5 constraint validation blocked LAUNCH button: `required` attribute on hidden step 2 radio inputs silently prevented form submission when navigating past step 2; `required` removed from `propulsion_type` and `vessel_length_class` inputs

### Security

- **BUG-59** — Pre-commit credential scanning hook added to both repos; blocks commits containing live API key patterns
- **BUG-62** — HTTP Auth layer added over `/wp-admin/` on HostPapa
- **BUG-68** — `offline-check.php` token delivery moved to POST body; `AMBOAT_API_KEY` rotated
- **BUG-87** — My Account delete action unthrottled; rate limit and confirmation re-prompt added
- **BUG-91** — Entitlement authority failed open to Tier 1 on error; hardened to fail-closed

---

## [v0.9.9.4-post] — 2026-09-04 — Device-Gated Registration Live

### Added
- **Device-gated registration (Option B)** — Pi-generated one-time short code replaces UUID copy-paste. Pi dashboard → Settings → "Get Registration Code" displays a 7-character code + QR code. User scans or clicks, lands on `/register/` with a green "d3kOS Pi verified" badge. Token is single-use, 30-minute expiry. No copying between applications required.
- **`amboat_reg_tokens` table** — production database schema updated; stores token, pi_id, device_token, expiry, and used_at.
- **User manual Section 17.4** — "Creating Your AtMyBoat.com Account (Device-Gated Registration)" with 4-step walkthrough and troubleshooting table. v2.4.1.

### Fixed
- **BUG-60 CLOSED** — WordPress comment settings confirmed: manual approval required, open commenting permitted (no login gate required).

### Security
- Deleted 50 MB SQL database dump (`atmyb197_wp59874-2026-08-18-6ed06e9.sql`) that was sitting in the web root and publicly accessible.

