# SIMULATOR REMOVAL — Claude Code Instructions
**Task:** Remove NMEA2000 Simulator from d3kOS completely and safely
**Date Issued:** 2026-03-12
**Authority:** Don / Skipper — Safety & Liability Risk
**AAO Risk Level:** MEDIUM — modifies production web pages and systemd services

---

## STOP BEFORE STARTING

Read this entire document before executing any command.
Confirm each phase is complete before moving to the next.
If any step fails, STOP and report — do not continue.

---

## PHASE 0 — ARCHIVE (do this first, no exceptions)

Create the archive directory and copy all simulator files before touching anything else.

```bash
mkdir -p /home/boatiq/archive/simulator-2026-02-21
```

Copy these files to the archive:
```bash
cp /home/boatiq/Helm-OS/doc/SIMULATOR_COMPLETE_2026-02-21.md /home/boatiq/archive/simulator-2026-02-21/
cp /home/boatiq/Helm-OS/doc/SIMULATOR_USER_GUIDE.md /home/boatiq/archive/simulator-2026-02-21/
cp /home/boatiq/Helm-OS/doc/SIMULATOR_TEST_RESULTS.md /home/boatiq/archive/simulator-2026-02-21/
cp /opt/d3kos/simulator/nmea2000-simulator.sh /home/boatiq/archive/simulator-2026-02-21/
cp /opt/d3kos/services/simulator/simulator-api.py /home/boatiq/archive/simulator-2026-02-21/
cp /etc/systemd/system/d3kos-simulator-api.service /home/boatiq/archive/simulator-2026-02-21/
cp /etc/systemd/system/d3kos-simulator.service.disabled /home/boatiq/archive/simulator-2026-02-21/
```

Verify archive contents before continuing:
```bash
ls -la /home/boatiq/archive/simulator-2026-02-21/
```

**Expected:** 7 or more files listed. If archive is empty or incomplete, STOP.

---

## PHASE 1 — STOP AND DISABLE SERVICES

```bash
sudo systemctl stop d3kos-simulator-api
sudo systemctl stop d3kos-simulator
sudo systemctl disable d3kos-simulator-api
sudo systemctl disable d3kos-simulator
```

Verify both are stopped:
```bash
sudo systemctl is-active d3kos-simulator-api
sudo systemctl is-active d3kos-simulator
```

**Expected output:** `inactive` or `failed` for both. If either shows `active`, STOP and report.

---

## PHASE 2 — REMOVE SERVICE FILES

```bash
sudo rm /etc/systemd/system/d3kos-simulator-api.service
sudo rm /etc/systemd/system/d3kos-simulator.service.disabled
sudo systemctl daemon-reload
```

Verify removed:
```bash
ls /etc/systemd/system/d3kos-simulator* 2>&1
```

**Expected:** `No such file or directory`

---

## PHASE 3 — REMOVE SIMULATOR SCRIPTS AND API

```bash
sudo rm -rf /opt/d3kos/simulator/
sudo rm -rf /opt/d3kos/services/simulator/
```

Verify removed:
```bash
ls /opt/d3kos/simulator/ 2>&1
ls /opt/d3kos/services/simulator/ 2>&1
```

**Expected:** `No such file or directory` for both.

---

## PHASE 4 — REMOVE WEB UI PAGE

```bash
sudo rm /var/www/html/settings-simulator.html
```

Verify removed:
```bash
ls /var/www/html/settings-simulator.html 2>&1
```

**Expected:** `No such file or directory`

---

## PHASE 5 — REMOVE SIMULATOR LINK FROM SETTINGS PAGE

Edit `/var/www/html/settings.html`.

Find and remove the simulator menu item. It will look similar to one of these patterns:
```html
<a href="settings-simulator.html">🔧 NMEA2000 Simulator (Testing)</a>
```
or as a button/list item referencing `settings-simulator.html` or containing the word `simulator`.

Remove the entire element (the `<a>`, `<li>`, `<button>`, or `<div>` block — whatever wraps it).

After editing, verify no simulator references remain in settings.html:
```bash
grep -i "simulat" /var/www/html/settings.html
```

**Expected:** No output. If any lines are returned, remove them and re-check.

---

## PHASE 6 — REMOVE DASHBOARD BANNER FROM dashboard.html AND helm.html

### dashboard.html

Edit `/var/www/html/dashboard.html`.

Find and remove ALL of the following:
1. The orange simulator banner HTML block (contains "SIMULATOR MODE ACTIVE")
2. The JavaScript that polls `/simulator/status` every 5 seconds
3. Any `<script>` block or inline code that references `simulator`
4. Any CSS styles specific to the simulator banner (orange gradient, pulse animation)

After editing, verify:
```bash
grep -i "simulat" /var/www/html/dashboard.html
```

**Expected:** No output.

### helm.html

Repeat the same removal for `/var/www/html/helm.html`:

```bash
grep -i "simulat" /var/www/html/helm.html
```

**Expected:** No output.

---

## PHASE 7 — REMOVE NGINX PROXY BLOCK

Edit `/etc/nginx/sites-enabled/default`.

Find and remove the `/simulator/` location block. It will look like:
```nginx
location /simulator/ {
    proxy_pass http://localhost:8096/;
    ...
}
```

Remove the entire block.

Verify nginx config is still valid:
```bash
sudo nginx -t
```

**Expected:** `syntax is ok` and `test is successful`

If test fails, STOP — do not reload nginx. Report the error.

If test passes, reload nginx:
```bash
sudo systemctl reload nginx
```

---

## PHASE 8 — REMOVE SIGNAL K PROVIDER

Edit `~/.signalk/settings.json`.

Find the `vcan0-simulator` entry in the `pipedProviders` array. It will look like:
```json
{
    "id": "vcan0-simulator",
    ...
}
```

Remove the entire object from the array. Ensure the JSON remains valid (no trailing commas, array brackets intact).

Verify the provider is gone:
```bash
grep -i "vcan0-simulator" ~/.signalk/settings.json
grep -i "simulat" ~/.signalk/settings.json
```

**Expected:** No output.

Restart Signal K to apply the change:
```bash
sudo systemctl restart signalk
```

Wait 10 seconds, then verify Signal K is running:
```bash
sudo systemctl is-active signalk
```

**Expected:** `active`

---

## PHASE 9 — SCAN FOR ANY REMAINING SIMULATOR REFERENCES

Run a full scan across the entire d3kOS web and config area:
```bash
grep -ri "simulat" /var/www/html/
grep -ri "simulat" /opt/d3kos/ 2>/dev/null
grep -ri "vcan0-simulator" ~/.signalk/
grep -ri "8096" /etc/nginx/
```

**Expected:** All commands return no output.

If any references are found, remove them before continuing to Phase 10.

---

## PHASE 10 — NETWORK TRAFFIC VERIFICATION

Check that the virtual CAN interface `vcan0` is no longer active:
```bash
ip link show vcan0 2>&1
```

**Expected:** `Device "vcan0" does not exist` or interface shows as DOWN.

If `vcan0` is UP, bring it down:
```bash
sudo ip link set vcan0 down
sudo modprobe -r vcan
```

Verify no simulator traffic on the real CAN interface:
```bash
timeout 5 candump can0 2>/dev/null | head -20
```

Review output — confirm there are no PGN 127488 frames from source address 0x40 (64) in the candump output. Real engine data from CX5106 will have a different source address.

---

## PHASE 11 — DASHBOARD VERIFICATION

Open these pages in a browser and verify:

### dashboard.html — `http://192.168.1.237/dashboard.html`
- [ ] No orange banner visible anywhere on the page
- [ ] No "SIMULATOR MODE ACTIVE" text
- [ ] All gauge values show real data or zero/dashes (not cycling 800–2400 RPM)
- [ ] RPM gauge is NOT cycling — it should be static at 0 or showing real engine value
- [ ] Boost pressure is NOT showing constant 1.5 bar (150,000 Pa) unless real engine is running
- [ ] No JavaScript console errors related to `/simulator/status` (check browser dev tools)

### helm.html — `http://192.168.1.237/helm.html`
- [ ] No orange banner visible
- [ ] No simulator-related JavaScript errors in console

### settings.html — `http://192.168.1.237/settings.html`
- [ ] No "🔧 NMEA2000 Simulator (Testing)" button or link visible
- [ ] Tapping all menu items confirms no link to `settings-simulator.html`

### settings-simulator.html — `http://192.168.1.237/settings-simulator.html`
- [ ] Page returns 404 Not Found
- [ ] If not 404, report immediately — the file was not removed

---

## PHASE 12 — SIGNAL K NAVIGATION DATA VERIFICATION

Open Signal K admin at `http://192.168.1.237:3000`.

Navigate to **Data Browser** and check the following paths:

| Signal K Path | Expected with Engine OFF |
|---------------|--------------------------|
| `propulsion.0.revs` | `null` or `0` — NOT cycling |
| `propulsion.0.boostPressure` | `null` or `0` — NOT constant 150000 |
| `propulsion.0.trim` | `null` or `0` |

Verify:
- [ ] No values are updating at 1Hz when engine is off
- [ ] No `vcan0-simulator` source listed in any data path
- [ ] Data sources for propulsion show only `CX5106` or `null` — not `vcan0-simulator`

If ANY path shows data from `vcan0-simulator` source, Signal K did not fully reload the config. Run:
```bash
sudo systemctl restart signalk
sleep 15
```

Then re-check the Data Browser.

---

## PHASE 13 — GIT COMMIT

```bash
cd /home/boatiq/Helm-OS
git add -A
git status
```

Review the status output — confirm only simulator-related files appear as deleted or modified. No other files should be changed.

If status looks correct:
```bash
git commit -m "remove: NMEA2000 simulator — safety and liability risk

Removed all simulator components from d3kOS:
- Stopped and removed d3kos-simulator-api.service
- Removed d3kos-simulator.service.disabled
- Deleted /opt/d3kos/simulator/ and /opt/d3kos/services/simulator/
- Deleted /var/www/html/settings-simulator.html
- Removed simulator link from settings.html
- Removed simulator banner and polling JS from dashboard.html and helm.html
- Removed nginx /simulator/ proxy block
- Removed vcan0-simulator provider from Signal K settings.json

Archive preserved at: /home/boatiq/archive/simulator-2026-02-21/

Reason: Simulator running on production system creates liability risk.
Replacement: Use tkurki/signalk-simulator plugin (standalone, no d3kOS impact)."
```

**DO NOT git push — local commit only per git policy.**

---

## PHASE 14 — UPDATE GOVERNANCE DOCUMENTS

Update the following files to record this removal:

### SESSION_LOG.md
Add a new entry with:
- Date: 2026-03-12
- Goal: Remove NMEA2000 simulator from d3kOS
- Completed: All 13 phases above
- Decision: Simulator removed due to safety/liability risk. Archive at `/home/boatiq/archive/simulator-2026-02-21/`
- Pending: Consider tkurki/signalk-simulator as standalone replacement

### PROJECT_CHECKLIST.md
- Mark simulator removal as DONE
- Add new task: "Evaluate tkurki/signalk-simulator as standalone Signal K plugin for bench testing"

### DEPLOYMENT_INDEX.md
- Mark all simulator files as REMOVED with date 2026-03-12
- Note archive location

---

## COMPLETION REPORT

When all phases are done, report the following in chat:

1. Confirmation each phase passed
2. Any steps that had unexpected output
3. Current `systemctl is-active` status for signalk, nginx
4. Result of the Signal K Data Browser check for `propulsion.0.revs`
5. Git commit hash
6. Governance files updated

---

## IF SOMETHING GOES WRONG

**Service won't stop:** `sudo systemctl kill d3kos-simulator-api` then retry stop.

**nginx -t fails after editing:** Restore from backup — `sudo cp /etc/nginx/sites-enabled/default.bak /etc/nginx/sites-enabled/default` (create .bak before editing).

**Signal K won't restart after settings.json edit:** JSON is likely malformed. Restore from git: `cd ~/.signalk && git checkout settings.json` (if Signal K uses git) or manually fix the JSON syntax error. Use `python3 -m json.tool ~/.signalk/settings.json` to validate JSON before restarting.

**Dashboard shows 404 for all pages:** nginx config is broken. Do not reload nginx until `nginx -t` passes clean.

---

*Issued by: Don / Skipper — AtMyBoat.com / d3kOS*
*Archive location: /home/boatiq/archive/simulator-2026-02-21/*
*DO NOT regenerate this task — archive contains original simulator code if needed later*
