# Hardware Capability Detection — Requirements Specification
**Document:** HCD-REQ-001  
**Version:** 1.0  
**Date:** 2026-09-10  
**Author:** Donald Moskaluk / SkipperDon  
**Status:** DRAFT — awaiting operator approval  

---

## 1. Purpose and Scope

d3kOS must operate correctly across multiple hardware generations (RPi 4B, RPi 5, and beyond) and optional accelerator HATs. Features that require hardware not present on a given installation must be automatically disabled, clearly communicated to the operator, and automatically re-enabled when qualifying hardware is detected — without requiring manual configuration.

**In scope:**
- Raspberry Pi model and generation detection
- RAM capacity detection
- HAT detection (EEPROM-compliant HAT+ standard)
- Accelerator detection — PCIe-attached (Hailo) and USB-attached (Coral) devices
- Dynamic re-detection on hardware change events
- Feature gate enforcement across all services
- Setup description — hardware-aware capability summary for wizard and dashboard

**Out of scope:**
- Network hardware detection (NIC, WiFi chipset)
- NMEA2000 HAT detection (handled separately in SK/AvNav configuration)
- Cloud/remote capability assessment
- Windows or non-Linux platforms

---

## 2. Hardware Detection Requirements

### 2.1 — Platform Detection (REQ-HCD-001 through REQ-HCD-004)

| ID | Requirement |
|---|---|
| REQ-HCD-001 | The system SHALL detect the Raspberry Pi model string from `/proc/device-tree/model` |
| REQ-HCD-002 | The system SHALL extract the Pi generation as an integer (4, 5, etc.) from the model string |
| REQ-HCD-003 | The system SHALL detect total installed RAM in GB from `/proc/meminfo` (rounded down to nearest integer GB) |
| REQ-HCD-004 | If `/proc/device-tree/model` is absent or unreadable, the system SHALL record `pi_gen: 0` and `pi_model: "unknown"` and log a warning — it SHALL NOT fail silently |

### 2.2 — HAT Detection (REQ-HCD-005 through REQ-HCD-009)

| ID | Requirement |
|---|---|
| REQ-HCD-005 | The system SHALL detect HAT presence by reading `/proc/device-tree/hat/` directory |
| REQ-HCD-006 | If a HAT is present, the system SHALL record: `product`, `vendor`, `product_id`, `product_ver` from the device tree HAT node |
| REQ-HCD-007 | The system SHALL record a normalised `hat_class` value from a lookup table (see Appendix A) to identify known HAT types without requiring consumers to parse raw product strings |
| REQ-HCD-008 | If no HAT EEPROM is detected, `hat.present` SHALL be `false` and all HAT fields SHALL be `null` |
| REQ-HCD-009 | HAT detection runs on every boot probe and on every scheduled re-probe. HATs are NOT monitored for hot-plug (physical HAT changes require reboot by design) |

### 2.3 — Accelerator Detection (REQ-HCD-010 through REQ-HCD-016)

| ID | Requirement |
|---|---|
| REQ-HCD-010 | The system SHALL detect Hailo-8L presence by checking for `/dev/hailo0` device node |
| REQ-HCD-011 | The system SHALL detect Google Coral USB presence by checking `lsusb` output for USB vendor/product ID `18d1:9302` (Coral USB Accelerator) |
| REQ-HCD-012 | The system SHALL detect Google Coral USB Mini presence by checking `lsusb` for `18d1:9303` |
| REQ-HCD-013 | The system SHALL detect Hailo-8 (full) via PCIe device enumeration (`/sys/bus/pci/devices/` scan for Hailo vendor ID `1e60`) |
| REQ-HCD-014 | The system SHALL record a normalised `accelerator_class` list containing zero or more values from: `["hailo-8", "hailo-8l", "coral-usb", "coral-usb-mini"]` |
| REQ-HCD-015 | Unknown USB devices that match no known accelerator profile SHALL be ignored — detection MUST NOT produce false positives |
| REQ-HCD-016 | If no accelerator is detected, `accelerator.present` SHALL be `false` and `accelerator_class` SHALL be an empty list `[]` |

---

## 3. Dynamic Detection Requirements

### 3.1 — Hot-Plug Detection (REQ-HCD-020 through REQ-HCD-025)

| ID | Requirement |
|---|---|
| REQ-HCD-020 | The system SHALL use udev rules to detect USB accelerator attach and detach events in real time, without polling |
| REQ-HCD-021 | On a USB accelerator attach event: the system SHALL trigger a re-probe within 5 seconds, update `hardware-profile.json`, and notify all registered consumers |
| REQ-HCD-022 | On a USB accelerator detach event: the system SHALL trigger a re-probe within 5 seconds, update `hardware-profile.json`, and notify all registered consumers |
| REQ-HCD-023 | udev rules SHALL match on known accelerator USB vendor/product IDs only (see REQ-HCD-011, REQ-HCD-012). Rules SHALL NOT fire on generic USB storage, hubs, or unknown devices |
| REQ-HCD-024 | If a re-probe is already in progress when a udev event fires, the second event SHALL be queued and the re-probe run again after the first completes — events SHALL NOT be dropped |
| REQ-HCD-025 | HAT changes (PCIe/I2C hardware) are NOT monitored via udev. A HAT change requires a reboot; the boot-time probe covers it |

### 3.2 — Scheduled Re-Probe (REQ-HCD-026 through REQ-HCD-028)

| ID | Requirement |
|---|---|
| REQ-HCD-026 | The system SHALL run a full hardware probe at every boot (via systemd service, before d3kOS dashboard starts) |
| REQ-HCD-027 | The system SHALL run a scheduled re-probe every 15 minutes while the system is running, as a belt-and-suspenders backup to udev |
| REQ-HCD-028 | An operator-triggered re-probe SHALL be available via: (a) a button in the dashboard Hardware page, and (b) a CLI command `d3kos-probe` |

### 3.3 — Change Notification (REQ-HCD-030 through REQ-HCD-034)

| ID | Requirement |
|---|---|
| REQ-HCD-030 | When `hardware-profile.json` changes after a re-probe, the system SHALL notify all registered consumers via an HTTP POST to a local webhook endpoint on the dashboard Flask service (`POST /api/hardware/profile-updated`) |
| REQ-HCD-031 | The dashboard SHALL, upon receiving a profile-update notification, re-evaluate all feature gates and update the UI state without requiring a page reload |
| REQ-HCD-032 | Each d3kOS systemd service that is feature-gated SHALL watch `hardware-profile.json` for changes (via `inotifywait` or equivalent) and re-evaluate its enabled state on change |
| REQ-HCD-033 | If a previously unavailable feature becomes available after a hardware change, the dashboard SHALL display a toast notification: `"New hardware detected: [device name]. [Feature Name] is now available."` with an Enable button |
| REQ-HCD-034 | If a running feature's hardware is removed (e.g. USB accelerator unplugged mid-session), the dashboard SHALL display a warning toast and gracefully stop the affected service — it SHALL NOT crash |

---

## 4. Hardware Profile Requirements

### 4.1 — Profile File (REQ-HCD-040 through REQ-HCD-044)

| ID | Requirement |
|---|---|
| REQ-HCD-040 | The hardware profile SHALL be stored at `config/hardware-profile.json` within the d3kOS config directory |
| REQ-HCD-041 | The profile SHALL be human-readable JSON, indented 2 spaces |
| REQ-HCD-042 | The profile SHALL be written atomically (write to `.tmp`, then rename) to prevent consumers reading a partial file |
| REQ-HCD-043 | The profile SHALL include an `probed_at` ISO 8601 timestamp and a `probe_version` integer (incremented on every write) for change detection |
| REQ-HCD-044 | The profile file SHALL be readable by all d3kOS services (permissions: `644`) |

### 4.2 — Profile Schema

```json
{
  "probe_version": 7,
  "probed_at": "2026-09-10T14:30:00Z",
  "platform": {
    "pi_model": "Raspberry Pi 4 Model B Rev 1.4",
    "pi_gen": 4,
    "ram_gb": 8
  },
  "hat": {
    "present": false,
    "product": null,
    "vendor": null,
    "product_id": null,
    "product_ver": null,
    "hat_class": null
  },
  "accelerator": {
    "present": false,
    "accelerator_class": [],
    "devices": []
  }
}
```

**Populated example (Pi 5 + Hailo-8L):**
```json
{
  "probe_version": 12,
  "probed_at": "2026-09-10T15:00:00Z",
  "platform": {
    "pi_model": "Raspberry Pi 5 Model B Rev 1.0",
    "pi_gen": 5,
    "ram_gb": 8
  },
  "hat": {
    "present": true,
    "product": "Raspberry Pi AI HAT+",
    "vendor": "Raspberry Pi Ltd",
    "product_id": "0x0031",
    "product_ver": "0x0001",
    "hat_class": "hailo-ai-hat"
  },
  "accelerator": {
    "present": true,
    "accelerator_class": ["hailo-8l"],
    "devices": [
      { "type": "hailo-8l", "node": "/dev/hailo0", "bus": "pcie" }
    ]
  }
}
```

---

## 5. Capabilities Manifest Requirements

### 5.1 — Manifest File (REQ-HCD-050 through REQ-HCD-053)

| ID | Requirement |
|---|---|
| REQ-HCD-050 | A capabilities manifest SHALL be shipped with d3kOS at `config/capabilities-manifest.json`. It defines every optional feature, its hardware requirements, and its fallback |
| REQ-HCD-051 | The manifest SHALL be updated whenever a new feature is added to d3kOS — the feature MUST be declared before it can be gated |
| REQ-HCD-052 | The manifest SHALL be human-readable and operator-editable to allow overrides (e.g. force-enable a feature for testing) |
| REQ-HCD-053 | A manifest entry MAY include an `operator_override` flag. If `true`, the feature gate is bypassed regardless of hardware. Default: `false`. This is an advanced/diagnostic option |

### 5.2 — Manifest Schema

```json
{
  "manifest_version": "1.0",
  "features": {
    "ollama_local": {
      "display_name": "Local AI (Ollama)",
      "description": "Runs the Ollama LLM engine locally on the Pi for offline AI assistance.",
      "requires": {
        "pi_gen_min": 5,
        "ram_gb_min": 8,
        "accelerator_any": true,
        "accelerator_class_any": ["hailo-8l", "hailo-8", "coral-usb"]
      },
      "fallback_feature": "ollama_remote",
      "service": "d3kos-ollama.service",
      "operator_override": false
    },
    "vision_ai_d11": {
      "display_name": "Vision AI (D11)",
      "description": "Camera-based computer vision for object detection and situational awareness.",
      "requires": {
        "pi_gen_min": 5,
        "ram_gb_min": 4,
        "accelerator_any": false
      },
      "fallback_feature": null,
      "service": "d3kos-vision.service",
      "operator_override": false
    },
    "surround_view_d16": {
      "display_name": "3D Surround View (D16)",
      "description": "360-degree surround view from four USB cameras stitched in real time.",
      "requires": {
        "pi_gen_min": 4,
        "ram_gb_min": 4,
        "accelerator_any": false
      },
      "fallback_feature": null,
      "service": "d3kos-go2rtc.service",
      "operator_override": false
    },
    "safehelm_d02": {
      "display_name": "SafeHelm (D02)",
      "description": "Automated watchkeeping alerts and heading deviation detection.",
      "requires": {
        "pi_gen_min": 4,
        "ram_gb_min": 2,
        "accelerator_any": false
      },
      "fallback_feature": null,
      "service": "d3kos-safehelm.service",
      "operator_override": false
    },
    "vhf_suite_d13": {
      "display_name": "VHF DSC Suite (D13)",
      "description": "VHF radio DSC decode, DSC distress relay, and MMSI tracking.",
      "requires": {
        "pi_gen_min": 5,
        "ram_gb_min": 4,
        "accelerator_any": false
      },
      "fallback_feature": null,
      "service": "d3kos-vhf.service",
      "operator_override": false
    },
    "ollama_remote": {
      "display_name": "Remote AI (Gemini API)",
      "description": "AI assistance via Gemini API — requires internet connection. Active when local AI is unavailable.",
      "requires": {
        "pi_gen_min": 4,
        "ram_gb_min": 1,
        "accelerator_any": false
      },
      "fallback_feature": null,
      "service": "d3kos-gemini-proxy.service",
      "operator_override": false
    }
  }
}
```

---

## 6. Feature Gate Requirements

### 6.1 — Gate Logic (REQ-HCD-060 through REQ-HCD-065)

| ID | Requirement |
|---|---|
| REQ-HCD-060 | A `feature_available(feature_key)` function SHALL be provided as a shared Python library (`d3kos_feature_gate.py`) importable by any d3kOS service |
| REQ-HCD-061 | The gate SHALL return `True` only if ALL conditions in the feature's `requires` block are satisfied by the current hardware profile |
| REQ-HCD-062 | If `operator_override` is `true` in the manifest, the gate SHALL return `True` regardless of hardware — and SHALL log a warning that override is active |
| REQ-HCD-063 | A `feature_reason(feature_key)` function SHALL return a human-readable string explaining why a feature is locked, for display in the wizard and dashboard |
| REQ-HCD-064 | A `feature_upgrade_path(feature_key)` function SHALL return a list of hardware items the operator would need to add to unlock the feature |
| REQ-HCD-065 | The gate library SHALL cache the profile in memory and invalidate the cache when `probe_version` changes — it SHALL NOT read the JSON file on every call |

---

## 7. Setup Description Requirements

### 7.1 — What It Is (REQ-HCD-070 through REQ-HCD-074)

The **Setup Description** is a hardware-aware capability summary generated from the profile and manifest. It is shown in three places:

| ID | Requirement |
|---|---|
| REQ-HCD-070 | The Setup Description SHALL be displayed at the end of the first-boot wizard, as the final confirmation screen before the operator completes setup |
| REQ-HCD-071 | The Setup Description SHALL be available at any time from the dashboard's **Hardware** page (a dedicated page, not a modal) |
| REQ-HCD-072 | The Setup Description SHALL be re-generated and re-displayed automatically whenever `hardware-profile.json` changes |
| REQ-HCD-073 | A plain-text version of the Setup Description SHALL be available via CLI: `d3kos-probe --describe` |
| REQ-HCD-074 | The Setup Description SHALL use plain language — no technical identifiers (no `pi_gen`, no `product_id`) — it is written for the operator, not a developer |

### 7.2 — Setup Description Format

The description has four sections, always in this order:

```
d3kOS Hardware Profile
════════════════════════════════════════════════════
Platform   : Raspberry Pi 4 Model B  ·  8 GB RAM
HAT        : None detected
Accelerator: None detected
════════════════════════════════════════════════════

ENABLED ON THIS HARDWARE
  ✓  d3kOS Dashboard                    — always on
  ✓  Remote AI (Gemini API)             — internet required
  ✓  SafeHelm (D02)                     — watchkeeping alerts
  ✓  3D Surround View (D16)             — requires 4 USB cameras
  ✓  signalk-forward-watch              — always on

AVAILABLE WITH OPTIONAL HARDWARE
  ✗  Local AI (Ollama)        — add a Pi 5 + Hailo-8L AI HAT+
  ✗  Vision AI (D11)          — add a Pi 5 (8 GB RAM)
  ✗  VHF DSC Suite (D13)      — add a Pi 5 (4 GB RAM min)

HOW TO UNLOCK MORE FEATURES
  Upgrade to Raspberry Pi 5 to unlock Vision AI and VHF Suite.
  Add the Raspberry Pi AI HAT+ (Hailo-8L) to unlock Local AI.
  Plug in a Google Coral USB Accelerator to unlock Local AI
  on any Pi 5.

════════════════════════════════════════════════════
Last probed: 2026-09-10 14:30 UTC  ·  [Re-probe now]
════════════════════════════════════════════════════
```

### 7.3 — Section Rules (REQ-HCD-075 through REQ-HCD-079)

| ID | Requirement |
|---|---|
| REQ-HCD-075 | "ENABLED ON THIS HARDWARE" SHALL list every feature whose gate returns `True` for the current profile, including always-on features |
| REQ-HCD-076 | "AVAILABLE WITH OPTIONAL HARDWARE" SHALL list every feature whose gate returns `False`, with a plain-language reason derived from `feature_upgrade_path()` |
| REQ-HCD-077 | "HOW TO UNLOCK MORE FEATURES" section SHALL be omitted entirely if all features are enabled (no locked features) |
| REQ-HCD-078 | The "Last probed" timestamp and "Re-probe now" button SHALL always appear at the bottom |
| REQ-HCD-079 | When displayed in the wizard, the "Re-probe now" button SHALL re-run the probe and refresh the screen in place — the operator can plug in hardware and re-probe without restarting the wizard |

---

## 8. Default Configuration Scenarios

These are the expected Setup Descriptions for the hardware combinations planned for d3kOS releases.

### Scenario A — v0.9.9.4 / v0.9.9.5 Base Unit (Current)
**Hardware:** RPi 4 Model B · 8 GB RAM · No HAT · No accelerator

```
ENABLED ON THIS HARDWARE
  ✓  d3kOS Dashboard
  ✓  Remote AI (Gemini API)
  ✓  SafeHelm (D02)
  ✓  3D Surround View (D16)      — requires 4 USB cameras
  ✓  signalk-forward-watch

AVAILABLE WITH OPTIONAL HARDWARE
  ✗  Local AI (Ollama)           — add Pi 5 + Hailo-8L AI HAT+
  ✗  Vision AI (D11)             — add Pi 5 (8 GB RAM)
  ✗  VHF DSC Suite (D13)         — add Pi 5 (4 GB RAM min)
```

### Scenario B — RPi 5 Base (No accelerator)
**Hardware:** RPi 5 Model B · 8 GB RAM · No HAT · No accelerator

```
ENABLED ON THIS HARDWARE
  ✓  d3kOS Dashboard
  ✓  Remote AI (Gemini API)
  ✓  SafeHelm (D02)
  ✓  3D Surround View (D16)      — requires 4 USB cameras
  ✓  signalk-forward-watch
  ✓  Vision AI (D11)             — camera required
  ✓  VHF DSC Suite (D13)         — VHF receiver required

AVAILABLE WITH OPTIONAL HARDWARE
  ✗  Local AI (Ollama)           — add Hailo-8L AI HAT+ or Coral USB
```

### Scenario C — RPi 5 + Hailo-8L AI HAT+ (Full stack)
**Hardware:** RPi 5 Model B · 8 GB RAM · Raspberry Pi AI HAT+ · Hailo-8L

```
ENABLED ON THIS HARDWARE
  ✓  d3kOS Dashboard
  ✓  Remote AI (Gemini API)
  ✓  SafeHelm (D02)
  ✓  3D Surround View (D16)      — requires 4 USB cameras
  ✓  signalk-forward-watch
  ✓  Vision AI (D11)             — camera required
  ✓  VHF DSC Suite (D13)         — VHF receiver required
  ✓  Local AI (Ollama)           — AI HAT+ detected · offline capable

AVAILABLE WITH OPTIONAL HARDWARE
  (none — all features enabled on this hardware)

HOW TO UNLOCK MORE FEATURES
  (section omitted — all features unlocked)
```

### Scenario D — RPi 5 + Coral USB (Partial accelerator)
**Hardware:** RPi 5 Model B · 8 GB RAM · No HAT · Coral USB Accelerator

```
ENABLED ON THIS HARDWARE
  ✓  d3kOS Dashboard
  ✓  Remote AI (Gemini API)
  ✓  SafeHelm (D02)
  ✓  3D Surround View (D16)      — requires 4 USB cameras
  ✓  signalk-forward-watch
  ✓  Vision AI (D11)             — camera required
  ✓  VHF DSC Suite (D13)         — VHF receiver required
  ✓  Local AI (Ollama)           — Coral USB detected · offline capable

AVAILABLE WITH OPTIONAL HARDWARE
  (none — all features enabled on this hardware)
```

### Scenario E — RPi 4 + Coral USB (Accelerator, wrong platform)
**Hardware:** RPi 4 Model B · 8 GB RAM · No HAT · Coral USB Accelerator

```
ENABLED ON THIS HARDWARE
  ✓  d3kOS Dashboard
  ✓  Remote AI (Gemini API)
  ✓  SafeHelm (D02)
  ✓  3D Surround View (D16)      — requires 4 USB cameras
  ✓  signalk-forward-watch

AVAILABLE WITH OPTIONAL HARDWARE
  ✗  Local AI (Ollama)           — requires Pi 5 (accelerator detected
                                    but Pi 4 CPU insufficient)
  ✗  Vision AI (D11)             — add Pi 5 (8 GB RAM)
  ✗  VHF DSC Suite (D13)         — add Pi 5 (4 GB RAM min)
```
> Note: Scenario E demonstrates that the gate is multi-condition. An accelerator alone is not sufficient — the Pi generation gate also applies. The description communicates this clearly to the operator without exposing the underlying logic.

---

## 9. Non-Functional Requirements

| ID | Requirement |
|---|---|
| REQ-HCD-090 | The full hardware probe SHALL complete in under 10 seconds on a RPi 4B |
| REQ-HCD-091 | The probe SHALL run without internet access — all detection is local |
| REQ-HCD-092 | The probe SHALL produce no output to stdout during normal operation — log to journald only |
| REQ-HCD-093 | The udev rules SHALL NOT introduce any boot-time delay — they fire on events only |
| REQ-HCD-094 | The feature gate library SHALL add no more than 5 ms overhead per call (cached profile read) |
| REQ-HCD-095 | All components SHALL work correctly with Python 3.9+ (current Pi OS baseline) |
| REQ-HCD-096 | The hardware-profile.json SHALL survive a d3kOS software update — it is operator data, not application data, and SHALL NOT be overwritten by an update |
| REQ-HCD-097 | A probe failure (e.g. missing `/proc/device-tree`) SHALL produce a valid `hardware-profile.json` with all unknown fields set to safe defaults — it SHALL NOT leave the profile file absent or corrupt |

---

## Appendix A — Known HAT Classes

| `hat_class` value | Product | Vendor |
|---|---|---|
| `hailo-ai-hat` | Raspberry Pi AI HAT+ | Raspberry Pi Ltd |
| `pican-m` | PiCAN-M NMEA 2000 HAT | Copperhill Technologies |
| `pican2` | PiCAN2 CAN Bus HAT | Copperhill Technologies |
| `waveshare-can` | Waveshare RS485 CAN HAT | Waveshare |
| `unknown-hat` | HAT EEPROM present but product not in lookup table | — |

> Appendix A is a living list. Add entries as new HATs are validated.

---

## Appendix B — Known Accelerator Device IDs

| `accelerator_class` | Detection method | Vendor:Product ID / Node |
|---|---|---|
| `hailo-8l` | Device node | `/dev/hailo0` |
| `hailo-8` | PCIe scan | Vendor ID `0x1e60` |
| `coral-usb` | USB ID | `18d1:9302` |
| `coral-usb-mini` | USB ID | `18d1:9303` |

> Appendix B is a living list. Add entries as new accelerators are validated.

---

*End of HCD-REQ-001 v1.0*
