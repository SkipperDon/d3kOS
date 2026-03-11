# OpenCPN Flatpak + O-Charts Plugin — Setup Guide

**Source:** `/home/boatiq/1 openCPN using flatback.odt` (Don's reference document)
**Applies to:** d3kOS Pi (Debian Trixie, Flatpak OpenCPN 5.12.4)
**Status:** OpenCPN Flatpak installed and running. O-Charts plugin installed. Chart activation: Don's manual task.

---

## Why Flatpak (not native Debian package)

Debian Trixie does not provide native OpenCPN plugins, including the O-Charts plugin. The Flatpak version of OpenCPN includes its own runtime and plugin ecosystem, which allows the O-Charts plugin to install and function normally.

This is why d3kOS uses Flatpak OpenCPN — it is the only reliable path to get the O-Charts plugin working on Debian.

---

## Current State on d3kOS Pi

Already done (do not repeat):
- Flatpak installed system-wide
- `flatpak remote-add flathub` configured
- `flatpak install flathub org.opencpn.OpenCPN` — version 5.12.4
- `sudo flatpak override --device=input --device=dri` — touchscreen + display access
- Launcher: `/home/d3kos/install-opencpn.sh` → `flatpak run org.opencpn.OpenCPN`
- Plugin catalog updated, O-Charts plugin installed and enabled

---

## O-Charts Chart Activation — Don's Manual Steps

Two methods (either works):

### Method 1 — Direct login in plugin (simplest)
1. Open OpenCPN via the Charts button on the d3kOS main menu
2. Go to **Options → Plugins → O-Charts → Preferences**
3. Click **Log in** and enter your o-charts.org account credentials
4. Your licensed charts will appear — download them
5. Charts store inside the Flatpak sandbox automatically

### Method 2 — Device fingerprint registration
1. Go to o-charts.org → My Charts → Assign Device
2. Upload fingerprint file: `oc03L_1772818229.fpr` (already copied to `C:\Users\donmo\Downloads\`)
3. Download the chart files
4. Copy charts to: `~/.var/app/org.opencpn.OpenCPN/data/opencpn/charts/`

Method 1 is simpler. Use it unless there is a reason to use the fingerprint method.

---

## Flatpak Notes

- The Flatpak version is sandboxed — file dialogs may open in sandboxed locations
- Chart files are stored inside the Flatpak sandbox by default
- Additional directory access can be granted via `flatpak override --filesystem=<path>` if needed
- Plugin config location: `~/.var/app/org.opencpn.OpenCPN/config/opencpn/`
- Chart data location: `~/.var/app/org.opencpn.OpenCPN/data/opencpn/charts/`

---

## AIS Pipeline (reminder)

OpenCPN receives AIS data via TCP from Signal K:
- Signal K → signalk-to-nmea0183 plugin → TCP port 10110 → OpenCPN
- In OpenCPN: add TCP connection to `localhost:10110` with AIVDM filter enabled

See also: `deployment/docs/SIGNALK_UPGRADE.md`, `deployment/docs/OPENCPN_PINCH_ZOOM.md`
