# Session D: Quick Fixes & UI Polish

**Estimated Time:** 2-4 hours
**Domain:** UI/Frontend (Domain 1)
**Priority:** Medium
**Status:** Ready to start

---

## Overview

Fix 5 known UI issues to improve user experience and system polish:
1. Charts page - Install o-charts addon
2. Boatlog export button - Fix crash
3. Network status labels - Change to white color
4. NMEA2000 simulator - Disable/remove
5. Dashboard live data - Connect to Signal K

---

## Task 1: Fix Charts Page (1 hour)

**Problem:** Charts page missing o-charts addon for OpenCPN integration

**Current State:**
- Page exists at `/var/www/html/charts.html`
- OpenCPN installed (Tier 2 trigger)
- No o-charts integration

**Solution:**

### Step 1: Check if o-charts plugin exists
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "ls /usr/share/opencpn/plugins/ | grep -i chart"
```

### Step 2: Install o-charts plugin (if not present)
```bash
# Check available packages
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "apt search opencpn-plugin"

# Install o-charts plugin
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo apt-get install -y opencpn-plugin-oesenc"
```

### Step 3: Update charts.html to integrate with OpenCPN
```html
<!-- Add iframe to OpenCPN charts interface -->
<iframe src="http://localhost:8080/opencpn" 
        width="100%" 
        height="100%" 
        frameborder="0">
</iframe>
```

**Alternative:** If OpenCPN doesn't have web interface, add instructions for desktop app launch.

**Testing:**
- Navigate to http://192.168.1.237/charts.html
- Verify charts display or instructions show

---

## Task 2: Fix Boatlog Export Button (30 minutes)

**Problem:** Export button crashes when clicked

**Current State:**
- Boatlog page at `/var/www/html/boatlog.html`
- Export button exists but causes JavaScript error

**Solution:**

### Step 1: Read current boatlog.html
```bash
grep -A 10 "export" /var/www/html/boatlog.html
```

### Step 2: Identify the crash
Common causes:
- Missing export function
- Incorrect API endpoint
- Tier check failing

### Step 3: Fix export functionality
```javascript
// Add export function if missing
async function exportBoatlog() {
    try {
        // Check tier first
        const tierResp = await fetch('/tier/status');
        const tierData = await tierResp.json();
        
        if (tierData.tier === 0) {
            alert('Export requires Tier 1 or higher');
            return;
        }
        
        // Trigger export
        const resp = await fetch('/export/generate', {method: 'POST'});
        const data = await resp.json();
        
        if (data.success) {
            alert('Export complete! File: ' + data.export_id);
        } else {
            alert('Export failed: ' + data.error);
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('Export failed: ' + error.message);
    }
}
```

**Testing:**
- Click export button
- Verify no crash
- Check export created in `/opt/d3kos/data/exports/`

---

## Task 3: Network Status Labels White (15 minutes)

**Problem:** Network status labels hard to read (black text on dark background)

**File:** `/var/www/html/index.html` (main dashboard)

**Solution:**

### Step 1: Find network status section
```bash
grep -n "network" /var/www/html/index.html
```

### Step 2: Change text color to white
```css
/* Add to style section or inline */
.network-status-label {
    color: #FFFFFF !important;
}
```

Or inline:
```html
<span style="color: #FFFFFF;">Network Status</span>
```

**Testing:**
- Open main dashboard
- Verify white text is visible

---

## Task 4: Disable NMEA2000 Simulator (30 minutes)

**Problem:** Simulator still enabled, not needed anymore

**Current State:**
- Service: `d3kos-simulator.service`
- Script: `/opt/d3kos/simulator/nmea2000-simulator.sh`
- Dashboard toggle exists

**Solution:**

### Step 1: Stop and disable service
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo systemctl stop d3kos-simulator"
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo systemctl disable d3kos-simulator"
```

### Step 2: Remove dashboard toggle button
Edit Node-RED dashboard or `/var/www/html/index.html` to remove simulator button.

### Step 3: (Optional) Remove service file
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo rm /etc/systemd/system/d3kos-simulator.service"
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo systemctl daemon-reload"
```

**Testing:**
- Verify simulator not running: `systemctl status d3kos-simulator`
- Expected: "Unit d3kos-simulator.service could not be found" or "inactive"

---

## Task 5: Dashboard Live Data (1-2 hours)

**Problem:** Dashboard shows static data instead of live Signal K data

**File:** `/var/www/html/dashboard.html`

**Current State:**
- Dashboard exists with 4 rows (Engine, Tanks, System, Network)
- Data is hardcoded/static

**Solution:**

### Step 1: Add Signal K WebSocket connection
```javascript
// Connect to Signal K
const ws = new WebSocket('ws://' + window.location.hostname + '/signalk/v1/stream?subscribe=all');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.updates) {
        data.updates.forEach(update => {
            update.values.forEach(value => {
                updateDashboard(value.path, value.value);
            });
        });
    }
};
```

### Step 2: Update dashboard elements
```javascript
function updateDashboard(path, value) {
    // Engine metrics
    if (path === 'propulsion.port.revolutions') {
        document.getElementById('rpm').textContent = Math.round(value * 60);
    }
    else if (path === 'propulsion.port.oilPressure') {
        document.getElementById('oil-pressure').textContent = Math.round(value / 1000);
    }
    // ... add all other paths
}
```

### Step 3: Add auto-refresh fallback
```javascript
// Fallback if WebSocket disconnects
setInterval(async () => {
    if (ws.readyState !== WebSocket.OPEN) {
        // Fetch via HTTP API
        const resp = await fetch('/signalk/v1/api/vessels/self');
        const data = await resp.json();
        // Update dashboard from API
    }
}, 5000);
```

**Signal K Paths to Monitor:**
- `propulsion.port.revolutions` → RPM
- `propulsion.port.oilPressure` → Oil Pressure
- `propulsion.port.temperature` → Engine Temp
- `tanks.fuel.0.currentLevel` → Fuel Level
- `tanks.freshWater.0.currentLevel` → Water Level
- `electrical.batteries.house.voltage` → Battery
- `navigation.speedOverGround` → Speed
- `navigation.courseOverGroundTrue` → Heading

**Testing:**
- Start engine (or use simulator)
- Open dashboard
- Verify values update in real-time

---

## Files to Modify

1. `/var/www/html/charts.html` - Add o-charts integration
2. `/var/www/html/boatlog.html` - Fix export button
3. `/var/www/html/index.html` - White network labels
4. `/var/www/html/dashboard.html` - Live Signal K data
5. (Optional) Remove `/etc/systemd/system/d3kos-simulator.service`

---

## Backups

Create backups before modifying:
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo cp /var/www/html/charts.html /var/www/html/charts.html.bak.sessionD"
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo cp /var/www/html/boatlog.html /var/www/html/boatlog.html.bak.sessionD"
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo cp /var/www/html/index.html /var/www/html/index.html.bak.sessionD"
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "sudo cp /var/www/html/dashboard.html /var/www/html/dashboard.html.bak.sessionD"
```

---

## Testing Checklist

- [ ] Charts page loads without errors
- [ ] Boatlog export button works (or shows tier error)
- [ ] Network status labels are white and visible
- [ ] Simulator service is stopped/disabled
- [ ] Dashboard shows live data from Signal K

---

## Success Criteria

✅ All 5 UI issues fixed
✅ No new bugs introduced
✅ System remains stable
✅ Better user experience

---

**Estimated Time Breakdown:**
- Charts: 1 hour
- Boatlog export: 30 min
- Network labels: 15 min
- Simulator: 30 min
- Dashboard live data: 1-2 hours
**Total: 2-4 hours**

**Ready to start Session D!**
