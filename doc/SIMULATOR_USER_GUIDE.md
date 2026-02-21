# d3kOS NMEA2000 Simulator - User Guide
**Quick Start Guide for Testing Mode**

---

## What is the Simulator?

The NMEA2000 Simulator generates **fake engine data** for testing d3kOS without running your real boat engine. It's perfect for:

- ✅ Testing the system indoors (winter, off-season)
- ✅ Learning how d3kOS works without burning fuel
- ✅ Showing the system to others (demos)
- ✅ Verifying dashboard displays and gauges

⚠️ **NEVER use the simulator while your real engine is running!** It will override real data with fake data.

---

## How to Turn ON the Simulator

1. From the main menu, tap **Settings**
2. Scroll down and tap **"🔧 NMEA2000 Simulator (Testing)"**
3. Tap the **toggle switch** to turn it **ON**
4. You should see:
   - Orange banner at the top: **"🟠 SIMULATOR MODE ACTIVE"**
   - Live RPM values cycling from 800 to 2400

5. Go back to the Dashboard - the orange warning banner should appear at the top

**That's it!** Your system is now receiving simulated engine data.

---

## What Data is Being Simulated?

When the simulator is ON, you'll see fake data for:

| Parameter | What You'll See |
|-----------|-----------------|
| **RPM** | Cycles up and down between 800-2400 RPM |
| **Boost Pressure** | Always shows 150,000 Pa (1.5 bar / 22 PSI) |
| **Trim** | Always shows 0% (neutral position) |

**Update Rate:** Values update every second

---

## How to Turn OFF the Simulator

**IMPORTANT:** Always turn OFF the simulator when you're done testing!

1. Tap **Settings**
2. Tap **"🔧 NMEA2000 Simulator (Testing)"**
3. Tap the **toggle switch** to turn it **OFF**
4. The orange banner should disappear from all pages

---

## Safety Warnings

### 🔴 CRITICAL: DO NOT Use Simulator With Real Engine

**What happens if you forget to turn it OFF:**

- ❌ **Real engine RPM will be ignored** - you'll see fake RPM (800-2400) instead of actual RPM
- ❌ **Real boost pressure will be ignored** - you'll see constant 1.5 bar instead of actual boost
- ❌ **Engine problems won't show up** - overheating, low oil, etc. won't trigger alarms
- ❌ **You could damage your engine** - operating blindly with fake data

**The orange banner is your reminder!** If you see it on the dashboard while boating, **immediately turn OFF the simulator.**

---

## When Should I Use the Simulator?

### ✅ **GOOD Times to Use:**
- Testing the system indoors (not on the water)
- Learning how the dashboard works (winter months)
- Showing d3kOS to friends or family
- Verifying gauge displays after system updates
- Indoor development work

### ❌ **BAD Times to Use:**
- **NEVER** while the real engine is running
- **NEVER** while actually boating
- **NEVER** for extended periods (easy to forget it's ON)
- **NEVER** when troubleshooting real engine problems

---

## Troubleshooting

### The toggle switch won't turn ON
- Check that you're connected to the d3kOS network
- Refresh the settings page and try again
- Check that the d3kOS system is running (reboot if needed)

### The orange banner doesn't appear on the dashboard
- Wait 5 seconds (it auto-checks every 5 seconds)
- Refresh the dashboard page
- Make sure the simulator is actually ON (check Settings → Simulator page)

### I forgot to turn it OFF and my engine data is wrong
1. **Immediately** go to Settings → Simulator
2. Toggle switch to **OFF**
3. Verify orange banner disappears
4. Wait 10 seconds for system to stabilize
5. Check dashboard - real engine data should now be displayed

### How do I know the simulator is OFF after a reboot?
- The simulator is **always OFF by default** after reboot
- You must manually turn it ON each session
- This prevents accidental use while boating

---

## FAQ

**Q: Will the simulator run my battery down?**
A: No, it uses minimal CPU/power. But always turn it OFF when not testing.

**Q: Can I change the simulated RPM range?**
A: Not through the UI. The simulator script can be edited by advanced users, but the default 800-2400 range is appropriate for most engines.

**Q: Will the simulator affect my chartplotter or other NMEA2000 devices?**
A: Only if they're connected to the same NMEA2000 network. The simulator broadcasts on the `vcan0` virtual interface, which is separate from the real `can0` interface used by your CX5106 gateway.

**Q: Can I use the simulator to test alarms?**
A: Not directly - the simulated values are always "normal" (no overheating, no low oil, etc.). Alarm testing requires modifying the simulator script (advanced).

**Q: What if I lose internet and can't access the settings page?**
A: The simulator settings page works offline (no internet needed). Just connect to the d3kOS WiFi and access the settings.

---

## Quick Reference

| Action | Steps |
|--------|-------|
| **Turn ON** | Settings → Simulator → Toggle ON |
| **Turn OFF** | Settings → Simulator → Toggle OFF |
| **Check Status** | Look for orange banner on dashboard |
| **View Live Values** | Settings → Simulator (when ON) |

---

**Remember:** The simulator is a **testing tool only**. Always turn it OFF before using your boat!

**Need Help?** See the complete documentation at `/home/boatiq/Helm-OS/doc/SIMULATOR_COMPLETE_2026-02-21.md`

---

**Last Updated:** 2026-02-21
**d3kOS Version:** 1.0.3+
