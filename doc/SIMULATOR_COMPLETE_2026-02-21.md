## NMEA2000 Simulator (2026-02-21 UPDATED)

**Status:** ✅ PRODUCTION READY - Full UI and API implemented

**Purpose:** Generate realistic NMEA2000 engine data for testing without real engine

---

### Implementation

**Core Components:**
- Virtual CAN interface: `vcan0` (created via `modprobe vcan`)
- Simulator script: `/opt/d3kos/simulator/nmea2000-simulator.sh`
- Systemd service: `d3kos-simulator.service` (disabled by default, manual enable only)
- **NEW:** Flask API service: `d3kos-simulator-api.service` (port 8096)
- **NEW:** Web UI: `/var/www/html/settings-simulator.html`
- **NEW:** Dashboard banner: Auto-warning on `dashboard.html` and `helm.html`

**Data Generated:**
- **PGN:** 127488 (Engine Parameters Rapid Update)
- **RPM:** Cycles 800-2400 RPM (increases 50 RPM/sec, then decreases)
- **Boost Pressure:** 150,000 Pa (1.5 bar / 21.8 PSI) - constant
- **Trim:** 0% (neutral) - constant
- **Update rate:** 1 Hz (every second)
- **Interface:** vcan0 (Virtual CAN)
- **Source:** 64 (0x40)
- **Engine Instance:** 0 (Port engine)

---

### API Endpoints

**Base URL:** `http://192.168.1.237/simulator/` (nginx proxy to localhost:8096)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulator/status` | GET | Get simulator running status |
| `/simulator/toggle` | POST | Toggle simulator ON/OFF |
| `/simulator/values` | GET | Get current simulated values (real-time) |
| `/simulator/info` | GET | Get simulator configuration info |
| `/health` | GET | Health check |

**Example Response (`/simulator/values`):**
```json
{
    "success": true,
    "timestamp": 1771688004.0643206,
    "values": {
        "rpm": 850,
        "boost_pa": 150000,
        "boost_bar": 1.5,
        "boost_psi": 21.8,
        "trim": 0,
        "pgn": 127488,
        "interface": "vcan0",
        "source": 64,
        "engine_instance": 0,
        "update_rate_hz": 1
    }
}
```

---

### Web UI

**Access:** Settings → NMEA2000 Simulator (Testing)
**URL:** http://192.168.1.237/settings-simulator.html

**Features:**
- ✅ Toggle switch (ON/OFF with visual feedback)
- ✅ Live RPM value display (updates every second when ON)
- ✅ Simulated parameters grid (RPM, Boost, Trim, Update Rate)
- ✅ Warning banner when simulator active
- ✅ Risk warning section (critical alerts)
- ✅ Usage guidelines ("When to Use")
- ✅ Safety features documentation
- ✅ Touch-optimized, d3kOS theme (black/green/orange)

**Dashboard Banner:**
- **Auto-detection:** Checks simulator status every 5 seconds
- **Display:** Fixed orange banner at top when simulator ON
- **Message:** "🟠 SIMULATOR MODE ACTIVE - Simulated data is being broadcast - Real engine data ignored"
- **Animation:** Subtle pulse effect
- **Pages:** Shown on `dashboard.html` and `helm.html`

---

### Signal K Configuration

**Provider:** `vcan0-simulator`
**Location:** `~/.signalk/settings.json` → `pipedProviders`
**Default State:** Disabled
**Auto-Enable:** API automatically enables when simulator toggled ON
**Auto-Disable:** API automatically disables when simulator toggled OFF

**Signal K will automatically restart when provider state changes**

---

### Control Methods

1. **Web UI (Recommended):**
   - Navigate to Settings → NMEA2000 Simulator
   - Use toggle switch
   - View live values

2. **API (Programmatic):**
   ```bash
   # Get status
   curl http://192.168.1.237/simulator/status
   
   # Toggle ON/OFF
   curl -X POST http://192.168.1.237/simulator/toggle
   
   # Get live values
   curl http://192.168.1.237/simulator/values
   ```

3. **Systemd (Advanced):**
   ```bash
   sudo systemctl start d3kos-simulator
   sudo systemctl stop d3kos-simulator
   ```

---

### Safety Features

1. **Auto-Disable on Boot:** Simulator is OFF by default, requires manual enable each session
2. **Dashboard Banner:** Orange warning banner on all pages when active
3. **Visual Indicators:** Simulated values displayed in orange (not green)
4. **Manual Enable Required:** Cannot auto-start, user must toggle ON
5. **Confirmation Messages:** API returns clear success/failure messages
6. **Real-time Monitoring:** Status checked every 5 seconds on web pages

---

### Risks of Leaving Simulator ON

**🔴 Critical Risks:**

1. **Real Engine Data Ignored**
   - If CX5106 is connected, actual RPM, boost, trim overridden by fake data
   - Won't see real engine conditions
   - **Risk:** Miss engine problems (overheating, low oil, etc.)

2. **False/Missing Alarms**
   - Simulated values always "normal"
   - Real engine problems won't trigger alerts
   - **Risk:** Safety hazard - operate boat with faulty engine

3. **User Confusion**
   - Easy to forget simulator is active
   - Make operational decisions based on fake data
   - **Risk:** Incorrect throttle settings, wrong diagnostics

4. **Troubleshooting Complexity**
   - Hard to diagnose real problems with simulated data
   - Wastes time chasing phantom issues
   - **Risk:** Delayed repairs, frustration

5. **Network Pollution**
   - Simulated data broadcast on NMEA2000 network
   - Could confuse chartplotters, autopilots, other displays
   - **Risk:** Incorrect navigation, instrument errors

---

### When to Use Simulator

**✅ Good Use Cases:**

- **Indoor Development:** Test system without running engine
- **UI Testing:** Verify dashboard displays, gauges, alarms
- **Demos:** Show system capabilities to potential customers
- **Training:** Learn system without burning fuel or being on water
- **Edge Case Testing:** Simulate high RPM, failures, edge conditions
- **Integration Testing:** Test data flow from NMEA2000 → Signal K → Dashboard

**❌ Bad Use Cases:**

- **Real boat operation:** NEVER use with real engine running
- **Long-term:** Don't leave ON for extended periods
- **Production:** Not for actual boating, only development/testing
- **With CX5106 connected:** Conflicting data sources

---

### Benefits of Keeping Simulator (vs Removing)

**Why Keep:**
1. ✅ Test UI without engine
2. ✅ Indoor development (winter, off-season)
3. ✅ Demo system to others
4. ✅ Train new users
5. ✅ Edge case testing (high RPM, failures)
6. ✅ Rapid development iteration

**Why NOT Remove:**
- Simulator doesn't interfere when OFF (disabled by default)
- Useful tool for ongoing development
- No performance impact when disabled
- Easy to enable/disable via UI
- Safety features prevent accidental use

---

### Files & Services

**Settings Page:**
- `/var/www/html/settings-simulator.html` (15 KB)

**API Service:**
- `/opt/d3kos/services/simulator/simulator-api.py` (Python/Flask)
- `/etc/systemd/system/d3kos-simulator-api.service`
- Port: 8096 (localhost only, proxied via nginx)
- Status: `systemctl status d3kos-simulator-api`

**Simulator Service:**
- `/opt/d3kos/simulator/nmea2000-simulator.sh` (Bash script)
- `/etc/systemd/system/d3kos-simulator.service.disabled`
- Enabled dynamically by API when toggled ON

**Modified Pages:**
- `/var/www/html/dashboard.html` - Added banner
- `/var/www/html/helm.html` - Added banner
- `/var/www/html/settings.html` - Added simulator link

**Nginx Configuration:**
- `/etc/nginx/sites-enabled/default` - Added `/simulator/` proxy

---

### Testing Results

**Date:** 2026-02-21
**Status:** ✅ ALL TESTS PASSED (9/9)

**See:** `/home/boatiq/Helm-OS/doc/SIMULATOR_TEST_RESULTS.md`

**Summary:**
- API endpoints: All working
- Service control: ✅ ON/OFF functioning
- Signal K integration: ✅ Auto-enable/disable working
- Live values: ✅ Cycling 800-2400 RPM as expected
- Dashboard banner: ✅ Appears/disappears correctly
- Auto-disable on boot: ✅ Verified disabled by default

---

### User Instructions

**To Enable Simulator:**
1. Navigate to **Settings**
2. Click **"🔧 NMEA2000 Simulator (Testing)"** button
3. Toggle switch to **ON**
4. Verify orange banner appears: "🟠 SIMULATOR MODE ACTIVE"
5. Watch live RPM values cycle 800-2400

**To Disable Simulator:**
1. Return to Settings → Simulator
2. Toggle switch to **OFF**
3. Verify banner disappears
4. Confirm status shows "⭕ Simulator is STOPPED"

**Safety Reminder:**
- ⚠️ **NEVER** use simulator with real engine running
- ⚠️ Real CX5106 data ignored when simulator active
- ⚠️ Remember to turn OFF after testing
- ⚠️ Dashboard banner will remind you when active

---

**Documentation Updated:** 2026-02-21
**Implementation Complete:** ✅
**Production Ready:** ✅
