# d3kOS — AvNav o-charts Installation Guide
**Version:** 1.0.0 | **Phase:** 4 | **Updated:** 2026-03-13
**Applies to:** Raspberry Pi 4B, Debian Trixie, AvNav installed via OpenPlotter

---

## Overview

o-charts provides commercial licensed charts for AvNav. This guide covers:
1. Installing the ochartsng plugin into AvNav
2. Creating an account and activating your licence on this Pi
3. Downloading CHS (Canada), and other chart regions

**Prerequisites:**
- AvNav installed and running at `http://localhost:8080` (Phase 5 pre-requirement)
- Internet access on the Pi for initial download and licence activation
- Pi IP address: `192.168.1.237`

---

## Step 1 — Install the ochartsng Plugin

1. Open AvNav in the browser: `http://localhost:8080`
2. Navigate to **Plugin Manager** → **Available Plugins**
3. Find **ochartsng** and click **Install**
4. Wait for download and installation to complete
5. Restart AvNav: `sudo systemctl restart avnav`
6. Verify the plugin is listed as **Active** in Plugin Manager

---

## Step 2 — Create o-charts Account

1. Open `https://o-charts.org` in a browser
2. Create a free account (email required)
3. After login, go to **My Charts** → **My Systems**
4. Click **Add new system** — this generates a system fingerprint token

---

## Step 3 — Activate Your Licence on the Pi

### Method A — Direct Login (Recommended)

1. In AvNav at `http://localhost:8080`, open the **ochartsng** plugin settings
2. Enter your o-charts account email and password
3. The plugin registers this Pi automatically
4. Your purchased charts will appear in **My Charts**

### Method B — Fingerprint Method

1. In AvNav ochartsng plugin, click **Download Fingerprint**
2. A file named `oc03L_*.fpr` is saved to `~/Downloads`
3. Upload the `.fpr` file at `https://o-charts.org` → My Systems
4. o-charts generates a licence file (`.zip`)
5. In AvNav, click **Install Licence** → select the `.zip`

---

## Step 4 — Download Charts

### Canada CHS Charts

1. In AvNav ochartsng plugin, go to **Download Charts**
2. Select **CHS — Canada** → choose your region (Great Lakes, East Coast, etc.)
3. Click **Download** — files are large (300–800 MB per region); allow 20–60 minutes
4. After download, click **Install** → charts appear in AvNav chart list

### UK / Europe / US Charts

- **UK Admiralty:** Select **UKHO — Leisure** in the chart list
- **US NOAA:** Free — see *Free Chart Sources* section in d3kOS Settings
- **Other regions:** Available in the ochartsng plugin regional chart list

---

## Step 5 — Verify Charts Load

1. Open AvNav at `http://localhost:8080`
2. Click **Charts** (top menu) → your purchased chart regions should appear
3. Zoom to a known area and verify chart tiles render
4. Check the chart date in the AvNav chart info panel (current vs. outdated)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ochartsng plugin not visible | Restart AvNav: `sudo systemctl restart avnav` |
| Licence activation fails | Verify Pi clock is correct: `date` — wrong time breaks SSL |
| Charts download stalls | Check disk space: `df -h /` — need 5+ GB free per chart region |
| Charts show but tiles missing | Clear AvNav cache: AvNav → Settings → Cache → Clear |
| "System not found" on o-charts | Re-generate fingerprint — Pi reinstall resets fingerprint |

---

## File Locations (Pi)

| File | Location |
|------|----------|
| Chart files | `/home/d3kos/.avnav/charts/` (or AvNav data root) |
| ochartsng licence | `/home/d3kos/.avnav/ochartsng/` |
| Plugin files | AvNav plugin directory (set during install) |
| Fingerprint file | `~/Downloads/oc03L_*.fpr` |

---

## Port Reference

| Service | URL |
|---------|-----|
| AvNav | `http://localhost:8080` |
| AvNav o-charts plugin UI | `http://localhost:8082` (auto-started by ochartsng) |
| Signal K (chart data) | `http://localhost:8099` |

---

*d3kOS v2.0 — deployment/d3kOS/docs/AVNAV_OCHARTS_INSTALL.md*
