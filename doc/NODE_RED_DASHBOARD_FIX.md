# Node-RED Dashboard 2.0 Configuration Fix

**Date:** 2026-02-09
**Issue:** Persistent validation errors on Dashboard 2.0 nodes (red warning triangles)
**Status:** RESOLVED

## Problem Summary

When importing Node-RED Dashboard 2.0 flows, all nodes showed validation errors with red warning triangles in the editor. The errors persisted across multiple fix attempts, including:
- Property corrections
- Removing duplicate nodes
- Complete rebuilds with new IDs
- Minimal clean configurations

Even brand new configurations created from scratch showed the same validation errors.

## Root Causes Identified

After examining Node-RED logs and Dashboard 2.0 source code, the issues were:

### 1. Missing ui-theme Node
Dashboard 2.0 pages require a `ui-theme` node to be created and referenced. Without it, the theme property defaults to 'undefined' or empty string, causing warnings:
```
[warn] [ui-base:d3kOS Dashboard] Theme 'undefined' specified in page 'page-system' does not exist
```

### 2. ui-page Missing Required Properties
**Missing:** `theme` property (type: 'ui-theme')

**Correct ui-page structure:**
```json
{
  "id": "page-system",
  "type": "ui-page",
  "name": "System",
  "ui": "ui-base-new",
  "path": "/system",
  "icon": "home",
  "layout": "grid",
  "theme": "default-theme",  ← REQUIRED: must reference a ui-theme node
  "order": 1
}
```

### 3. ui-group Missing Required Properties
**Missing:** `showTitle`, `className`, `visible`, `disabled`, `groupType`

**Correct ui-group structure:**
```json
{
  "id": "group-signalk",
  "type": "ui-group",
  "name": "Signal K Control",
  "page": "page-system",
  "width": 6,
  "height": 1,
  "order": 1,
  "showTitle": true,      ← REQUIRED
  "className": "",        ← REQUIRED (can be empty string)
  "visible": true,        ← REQUIRED (default: true)
  "disabled": false,      ← REQUIRED (default: false)
  "groupType": "default"  ← REQUIRED (default: "default")
}
```

**Note:** Old flows may use `disp` property instead of `showTitle`. Dashboard 2.0 has backwards compatibility (`if (this.disp) { this.showTitle = this.disp }`), but `showTitle` is the correct property.

## Solution Applied

### Step 1: Create ui-theme Node
```json
{
  "id": "default-theme",
  "type": "ui-theme",
  "name": "Default Theme",
  "colors": {
    "surface": "#ffffff",
    "primary": "#0094CE",
    "bgPage": "#eeeeee",
    "groupBg": "#ffffff",
    "groupOutline": "#cccccc"
  },
  "sizes": {
    "density": "default",
    "pagePadding": "12px",
    "groupGap": "12px",
    "groupBorderRadius": "4px",
    "widgetGap": "12px"
  }
}
```

### Step 2: Reference Theme in ui-page
Added `"theme": "default-theme"` to all ui-page nodes.

### Step 3: Add All Required Properties to ui-group
Added `showTitle`, `className`, `visible`, `disabled`, `groupType` to all ui-group nodes.

### Step 4: Stop and Restart Node-RED
```bash
sudo systemctl stop nodered
# Update flows.json
sudo systemctl start nodered
```

## Verification

After applying the fix, Node-RED logs showed:
```
[info] [ui-base:d3kOS Dashboard] Node-RED Dashboard 2.0 (v1.30.2) started at /dashboard
[info] [ui-base:d3kOS Dashboard] Created socket.io server bound to Node-RED port at path /dashboard/socket.io
[info] Started flows
```

**No theme warnings or validation errors!**

## Dashboard 2.0 Required Properties Reference

### ui-base (Dashboard Configuration)
```json
{
  "type": "ui-base",
  "name": "Dashboard Name",
  "path": "/dashboard",
  "includeClientData": true,
  "acceptsClientConfig": ["ui-notification", "ui-control"]
}
```

### ui-theme (Theme Configuration)
```json
{
  "type": "ui-theme",
  "name": "Theme Name",
  "colors": {
    "surface": "#ffffff",
    "primary": "#0094CE",
    "bgPage": "#eeeeee",
    "groupBg": "#ffffff",
    "groupOutline": "#cccccc"
  },
  "sizes": {
    "density": "default",
    "pagePadding": "12px",
    "groupGap": "12px",
    "groupBorderRadius": "4px",
    "widgetGap": "12px"
  }
}
```

### ui-page (Page Configuration)
```json
{
  "type": "ui-page",
  "name": "Page Name",
  "ui": "<ui-base-id>",
  "path": "/page-path",
  "icon": "home",
  "layout": "grid",
  "theme": "<ui-theme-id>",  ← Reference to ui-theme node
  "order": 1
}
```

### ui-group (Group/Card Configuration)
```json
{
  "type": "ui-group",
  "name": "Group Name",
  "page": "<ui-page-id>",
  "width": 6,
  "height": 1,
  "order": 1,
  "showTitle": true,
  "className": "",
  "visible": true,
  "disabled": false,
  "groupType": "default"
}
```

### ui-button (Button Widget)
```json
{
  "type": "ui-button",
  "z": "<tab-id>",
  "group": "<ui-group-id>",
  "name": "Button Name",
  "label": "Button Label",
  "order": 1,
  "width": 3,
  "height": 1,
  "tooltip": "Tooltip text",
  "color": "",
  "bgcolor": "#0094CE",
  "className": "",
  "icon": "refresh",
  "payload": "",
  "payloadType": "str",
  "topic": "topic",
  "topicType": "msg",
  "wires": [["<target-node-id>"]]
}
```

### ui-text (Text Display Widget)
```json
{
  "type": "ui-text",
  "z": "<tab-id>",
  "group": "<ui-group-id>",
  "order": 1,
  "width": 6,
  "height": 1,
  "name": "Text Name",
  "label": "Label:",
  "format": "{{msg.payload}}",
  "layout": "row-left",
  "style": false,
  "font": "",
  "fontSize": 14,
  "color": "#717171",
  "className": "",
  "wires": []
}
```

## Lessons Learned

1. **Always create a ui-theme node first** when setting up Dashboard 2.0
2. **Check Dashboard 2.0 source code** (`~/.node-red/node_modules/@flowfuse/node-red-dashboard/nodes/config/*.html`) for required properties
3. **Monitor Node-RED logs** (`journalctl -u nodered -f`) to identify specific validation warnings
4. **Browser caching is persistent** - always close and reopen browser (not just refresh) after fixing configuration errors
5. **Dashboard 2.0 is stricter than Dashboard 1.0** - all properties must be explicitly defined, even if they're default values

## Files Modified

- `~/.node-red/flows.json` - Complete rebuild with all required properties
- `/home/boatiq/Helm-OS/signalk-control-dashboard.json` - Original (incorrect) configuration
- `/tmp/signalk-control-dashboard-fixed.json` - Corrected configuration for reference

## Signal K Control Dashboard

The corrected Signal K dashboard includes:

**Controls:**
- **Restart Signal K** button (orange) - Executes `sudo systemctl restart signalk`
- **Stop Signal K** button (red) - Executes `sudo systemctl stop signalk`
- **Start Signal K** button (green) - Executes `sudo systemctl start signalk`

**Status Display:**
- **Status:** Shows command output from systemctl operations
- **Current Status:** Shows real-time status with color-coded indicators:
  - 🟢 **RUNNING** (green) - Service is active
  - 🔴 **STOPPED** (red) - Service is inactive
  - 🔴 **FAILED** (red) - Service failed to start
  - 🟠 **UNKNOWN** (orange) - Status cannot be determined

**Automatic Status Checking:**
- Status is automatically checked every 10 seconds via inject node
- Uses `systemctl is-active signalk 2>&1` to check service status
- Function node parses output and formats HTML display with colored indicators

## Dashboard Access

- **Node-RED Editor:** http://192.168.1.237:1880
- **Dashboard UI:** http://192.168.1.237:1880/dashboard
- **System Page:** http://192.168.1.237:1880/dashboard/system

## Next Steps

1. Build onboarding wizard flow (15-question engine configuration)
2. Test Signal K integration with actual NMEA2000 data
3. Add additional system monitoring pages (CPU, memory, disk, temperature)
4. Create backup/restore functionality for flows

## References

- Node-RED Dashboard 2.0: https://dashboard.flowfuse.com/
- Node-RED Documentation: https://nodered.org/docs/
- Signal K Documentation: https://signalk.org/
- Package: `@flowfuse/node-red-dashboard` v1.30.2
- Node-RED: v4.1.4
- Node.js: v20.20.0
