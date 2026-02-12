# Engine Dashboard Implementation

**Date:** 2026-02-09
**Status:** ✅ Deployed and Working
**File:** `/var/www/html/dashboard.html`

## Overview

This document details the implementation of the d3kOS Engine Dashboard, a standalone HTML page that provides real-time monitoring of engine metrics, tank levels, system status, and network connectivity per MASTER_SYSTEM_SPEC.md Section 4.3.1.

## Problem Statement

From previous session, two main issues were identified:

1. **Dashboard Navigation Issue**: The Dashboard button in the main menu was pointing to an incomplete Node-RED Dashboard 2.0 page that only contained Signal K control buttons, not the comprehensive engine gauges specified in MASTER_SYSTEM_SPEC.md
2. **Onboarding Keyboard Access**: Engine wizard needed to exit fullscreen mode so the on-screen keyboard would be accessible

## Solution Approach

### Initial Approach: Node-RED Dashboard 2.0 (Abandoned)

**What we tried:**
- Built comprehensive Dashboard 2.0 with all 4 rows per MASTER_SYSTEM_SPEC.md
- Created Engine Gauges page with 17 widgets across 4 groups
- Configured WebSocket nodes for real-time Signal K data

**Problems encountered:**
1. White flash during page transitions
2. Fonts were too small (16px default vs 22-24px needed)
3. No top navigation bar like other pages
4. Design system mismatch with standalone HTML pages (boatlog.html, navigation.html, helm.html)
5. Toggle button functionality broken
6. Duplicate page errors in FlowFuse

**User decision:** After reviewing both approaches, user chose "yeah the boatlog style" - meaning standalone HTML instead of Node-RED Dashboard 2.0.

### Final Solution: Standalone HTML Dashboard

**Rationale:**
- Matches existing design system from boatlog.html, navigation.html, helm.html
- Consistent 22-24px fonts for readability
- Top navigation bar with "← Main Menu" button
- Black (#000000) background with green (#00CC00) accents
- Full control over styling and layout
- No framework limitations

## Technical Implementation

### File Structure

**Location:** `/var/www/html/dashboard.html` (21KB)

**Key Components:**

#### 1. Top Navigation Bar
```html
<nav class="top-nav">
  <button class="nav-button" onclick="goBack()">← Main Menu</button>
  <span class="status-text">d3kOS v2.0 | Engine Dashboard</span>
  <button class="nav-button" onclick="window.location.reload()">↻ Refresh</button>
</nav>
```

#### 2. Four Dashboard Rows (per MASTER_SYSTEM_SPEC.md Section 4.3.1)

**Row 1: Engine Metrics** (5 gauges)
- Tachometer (RPM) - `propulsion.*.revolutions`
- Tilt/Trim (%) - `propulsion.*.tiltTrim`
- Coolant Temp (°F) - `propulsion.*.temperature`
- Voltage (V) - `electrical.batteries.*.voltage`
- Oil Pressure (PSI) - `propulsion.*.oilPressure`

**Row 2: Tank Levels** (4 gauges)
- Fresh Water (%) - `tanks.freshWater.*.currentLevel`
- Black Water (%) - `tanks.blackWater.*.currentLevel`
- Fuel (%) - `tanks.fuel.*.currentLevel`
- Battery (%) - `electrical.batteries.*.capacity.stateOfCharge`

**Row 3: System Status** (4 indicators)
- CPU Usage (%) - `environment.rpi.cpu`
- Memory Usage (%) - `environment.rpi.memory`
- Storage Usage (%) - `environment.rpi.storage`
- GPU Temp (°F) - `environment.rpi.gpu.temperature`

**Row 4: Network Status** (4 indicators)
- WiFi Connection - `environment.rpi.network.wifi`
- Ethernet Connection - `environment.rpi.network.eth0`
- NMEA2000 Status - `environment.rpi.network.can0`
- Internet Connectivity - External ping test

### Signal K Integration

**WebSocket Connection:**
```javascript
function connectSignalK() {
  ws = new WebSocket('ws://localhost:3000/signalk/v1/stream?subscribe=none');

  ws.onopen = () => {
    console.log('Connected to Signal K');
    updateConnectionStatus(true);

    // Subscribe to all required paths
    const subscription = {
      context: 'vessels.self',
      subscribe: [
        { path: 'propulsion.*.revolutions' },
        { path: 'propulsion.*.temperature' },
        { path: 'propulsion.*.tiltTrim' },
        { path: 'propulsion.*.oilPressure' },
        { path: 'electrical.batteries.*.voltage' },
        { path: 'electrical.batteries.*.capacity.stateOfCharge' },
        { path: 'tanks.*.*.currentLevel' },
        { path: 'environment.rpi.*' }
      ]
    };
    ws.send(JSON.stringify(subscription));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.updates) {
      data.updates.forEach(update => {
        update.values.forEach(pathValue => {
          updateGauge(pathValue.path, pathValue.value);
        });
      });
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    updateConnectionStatus(false);
  };

  ws.onclose = () => {
    console.log('Disconnected from Signal K');
    updateConnectionStatus(false);
    // Reconnect after 5 seconds
    setTimeout(connectSignalK, 5000);
  };
}
```

**Data Update Handler:**
```javascript
function updateGauge(path, value) {
  // Map Signal K paths to gauge IDs
  const pathMapping = {
    'propulsion.main.revolutions': 'rpm-value',
    'propulsion.main.tiltTrim': 'trim-value',
    'propulsion.main.temperature': 'temp-value',
    'electrical.batteries.house.voltage': 'voltage-value',
    'propulsion.main.oilPressure': 'pressure-value',
    'tanks.freshWater.0.currentLevel': 'fresh-value',
    'tanks.blackWater.0.currentLevel': 'black-value',
    'tanks.fuel.0.currentLevel': 'fuel-value',
    'electrical.batteries.house.capacity.stateOfCharge': 'battery-value',
    'environment.rpi.cpu': 'cpu-value',
    'environment.rpi.memory': 'memory-value',
    'environment.rpi.storage': 'storage-value',
    'environment.rpi.gpu.temperature': 'gpu-value'
  };

  const elementId = pathMapping[path];
  if (elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      // Convert and format value based on gauge type
      const formattedValue = formatValue(path, value);
      element.textContent = formattedValue;

      // Update status color based on value
      updateGaugeColor(elementId, value, path);
    }
  }
}
```

### Design System

**CSS Variables:**
```css
:root {
  --color-bg: #000000;
  --color-text: #FFFFFF;
  --color-accent: #00CC00;
  --color-warning: #FFA500;
  --color-critical: #FF0000;
  --color-disabled: #333333;
  --font-family: "Roboto", "Arial", sans-serif;
  --font-base: 22px;
  --font-heading: 24px;
}
```

**Typography:**
- Base text: 22px
- Section headings: 24px
- Gauge values: 48px (bold, white)
- Gauge labels: 18px

**Layout:**
- Top navigation: Fixed at top, 60px height
- Dashboard sections: Flexbox grid
- Gauge cards: 2-5 per row depending on content
- Touch-friendly: 60px minimum button height
- Custom scrollbars: 20px width with green accents

**Color Coding:**
- Normal: Green (#00CC00)
- Warning: Orange (#FFA500)
- Critical: Red (#FF0000)
- Disabled/Offline: Dark Gray (#333333)

### Navigation Integration

**Main Menu Update:**

Modified `/var/www/html/index.html` to point Dashboard button to standalone HTML:

```javascript
case 'dashboard':
  window.location.href = '/dashboard.html';
  break;
```

**Previous (Node-RED Dashboard 2.0):**
```javascript
case 'dashboard':
  window.location.href = 'http://192.168.1.237:1880/dashboard';
  break;
```

### Onboarding Keyboard Fix

Modified navigation for Onboarding/Engine Setup to toggle out of fullscreen before opening:

```javascript
case 'onboarding':
  // Toggle out of fullscreen first so keyboard is accessible
  fetch('http://localhost:1880/toggle-fullscreen', {
    method: 'POST',
    mode: 'no-cors'
  }).then(() => {
    setTimeout(() => {
      window.location.href = '/onboarding.html';
    }, 500);
  }).catch(() => {
    // If toggle fails, still navigate to onboarding
    window.location.href = '/onboarding.html';
  });
  break;
```

## Deployment Process

### 1. File Preparation

Created `dashboard.html` on Ubuntu workstation:
```bash
cd /home/boatiq/Helm-OS/
# Created dashboard.html matching boatlog.html design
```

### 2. Transfer to Pi

```bash
# Copy dashboard.html to Pi
scp -i ~/.ssh/d3kos_key /home/boatiq/Helm-OS/dashboard.html d3kos@192.168.1.237:/tmp/

# Install to web root
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 \
  "sudo cp /tmp/dashboard.html /var/www/html/ && \
   sudo chown www-data:www-data /var/www/html/dashboard.html"
```

### 3. Update Main Menu

```bash
# Update index.html navigation
scp -i ~/.ssh/d3kos_key /home/boatiq/Helm-OS/index.html d3kos@192.168.1.237:/tmp/

# Install updated menu
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 \
  "sudo cp /tmp/index.html /var/www/html/ && \
   sudo chown www-data:www-data /var/www/html/index.html"
```

### 4. Verification

```bash
# Check files deployed correctly
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "ls -lh /var/www/html/*.html"

# Test HTTP access
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "curl -s http://localhost/dashboard.html | head -30"
```

## Troubleshooting

### Issue: Browser Cache Showing Old Dashboard

**Symptom:** After deployment, user sees old Node-RED Dashboard 2.0 instead of new standalone HTML page.

**Cause:** Browser cached the previous dashboard page and menu navigation.

**Solution:**

1. **Hard Refresh (Recommended):**
   - Press `Ctrl + Shift + R` or `Ctrl + F5` on the main menu page
   - Then click Dashboard button

2. **Clear Browser Cache:**
   - Press `Ctrl + Shift + Delete`
   - Select "Cached images and files"
   - Click "Clear data"
   - Reload page

3. **Direct URL Access:**
   - Navigate directly to: `http://192.168.1.237/dashboard.html`
   - Press `Ctrl + Shift + R` to force fresh load

**Verification:**
- New dashboard shows top navigation bar with "← Main Menu" button
- Large readable fonts (22-24px)
- Black background with green accents
- 4 distinct sections with clear headings

## Testing Results

### ✅ Functional Tests Passed

1. **Navigation:**
   - Main menu → Dashboard: ✅ Works
   - Dashboard → Main menu: ✅ Works
   - Refresh button: ✅ Works

2. **Display:**
   - All 4 rows visible: ✅ Works
   - Engine Metrics (5 gauges): ✅ Displayed
   - Tank Levels (4 gauges): ✅ Displayed
   - System Status (4 indicators): ✅ Displayed
   - Network Status (4 indicators): ✅ Displayed

3. **Signal K Connection:**
   - WebSocket connects: ✅ Works
   - Subscriptions sent: ✅ Works
   - Data updates received: ✅ Works (live NMEA2000 data)
   - Auto-reconnect on disconnect: ✅ Works

4. **Design Consistency:**
   - Matches boatlog.html style: ✅ Confirmed
   - 22-24px fonts: ✅ Confirmed
   - Top navigation bar: ✅ Confirmed
   - Black/green theme: ✅ Confirmed
   - Touch-friendly buttons: ✅ Confirmed

5. **Onboarding Keyboard Access:**
   - Fullscreen toggle before opening: ✅ Works
   - On-screen keyboard accessible: ✅ Confirmed

## Files Modified

### Created Files
- `/var/www/html/dashboard.html` (21KB) - New standalone engine dashboard

### Modified Files
- `/var/www/html/index.html` (31KB) - Updated dashboard navigation + onboarding fullscreen toggle
- `/home/boatiq/.claude/projects/-home-boatiq/memory/MEMORY.md` - Documented deployment and design system

### Abandoned Files (not used)
- `~/.node-red/flows.json` - Node-RED Dashboard 2.0 engine gauges (superseded by standalone HTML)
- `/tmp/fix_dashboard_ux.py` - Script to fix Dashboard 2.0 fonts/navigation (not needed)
- `/tmp/flows_ux_fix.json` - Modified flows with UX improvements (not used)

## Architecture Decisions

### Why Standalone HTML vs Node-RED Dashboard 2.0?

**Node-RED Dashboard 2.0 (Initially attempted):**
- ❌ Framework imposes its own styling limitations
- ❌ Difficult to match exact font sizes and spacing
- ❌ No easy way to add top navigation bar
- ❌ White background flash during transitions
- ❌ Complex configuration with ui-base, ui-theme, ui-page, ui-group requirements
- ✅ Good for rapid prototyping
- ✅ Built-in widgets

**Standalone HTML (Final choice):**
- ✅ Complete control over styling and layout
- ✅ Matches existing design system perfectly
- ✅ Direct Signal K WebSocket access (same as navigation.html)
- ✅ Consistent with boatlog.html, navigation.html, helm.html
- ✅ No framework dependencies
- ✅ Easier to maintain and modify
- ✅ Better touch optimization
- ❌ Requires manual WebSocket management
- ❌ No built-in widgets (must create gauges manually)

**Decision:** Use standalone HTML for all main UI pages, reserve Node-RED Dashboard 2.0 for backend controls only (Signal K restart/stop buttons).

## Design System Standards

Based on this implementation, the following standards are established for all d3kOS UI pages:

### Layout
- **Top Navigation Bar:** Required on all pages (except main menu)
  - Left: "← Main Menu" button
  - Center: Page title with d3kOS version
  - Right: Action button (Refresh, Settings, etc.)
  - Height: 60px minimum
  - Border: 2px solid green (#00CC00)

### Typography
- **Base Font:** 22px
- **Headings:** 24px
- **Gauge Values:** 48px bold
- **Labels:** 18px
- **Font Family:** Roboto, Arial, sans-serif

### Colors
- **Background:** Black (#000000)
- **Text:** White (#FFFFFF)
- **Accent/Normal:** Green (#00CC00)
- **Warning:** Orange (#FFA500)
- **Critical:** Red (#FF0000)
- **Disabled:** Dark Gray (#333333)

### Touch Optimization
- **Button Height:** 60px minimum
- **Button Padding:** 14px vertical, 28px horizontal
- **Scrollbar Width:** 20px
- **Touch Action:** manipulation (prevents double-tap zoom)

### Signal K Integration
- **WebSocket URL:** `ws://localhost:3000/signalk/v1/stream`
- **Auto-reconnect:** 5 second delay on disconnect
- **Subscription:** Use context 'vessels.self' with specific path patterns
- **Error Handling:** Display offline status, retry connection

## References

- MASTER_SYSTEM_SPEC.md Section 4.3.1 - Dashboard Layout specification
- MASTER_SYSTEM_SPEC.md Section 5.1 - Web UI architecture
- boatlog.html - Design system reference
- navigation.html - Signal K WebSocket pattern reference
- SIGNALK_CONFIGURATION.md - Signal K setup and paths

## Lessons Learned

1. **Framework Choice Matters:** For UI consistency, standalone HTML provided better control than Node-RED Dashboard 2.0
2. **Browser Cache:** Always instruct users to hard refresh after HTML deployments
3. **Design System First:** Establishing design standards early (from boatlog.html) made later pages easier to build
4. **Fullscreen Mode:** Toggle out of fullscreen before showing keyboard-heavy screens
5. **WebSocket Reliability:** Implement auto-reconnect for marine environments with spotty connectivity

## Future Enhancements

Potential improvements for future iterations:

1. **Historical Data:** Add graphs showing engine RPM, temperature trends over time
2. **Alerts:** Visual/audio alerts when values exceed thresholds
3. **Data Logging:** Log all gauge values to database for maintenance tracking
4. **Customization:** Allow user to configure alert thresholds
5. **Mobile Responsive:** Optimize layout for different screen sizes
6. **Offline Mode:** Cache last known values when Signal K disconnects
7. **Multi-Engine Support:** Extend to handle twin-engine configurations

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Claude (d3kOS Development)
