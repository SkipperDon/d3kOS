# CX5106 Engine Gateway Configuration Manual
## Standalone Setup Guide - No Wizard Required

---

## Table of Contents
1. [Introduction](#introduction)
2. [What You Need](#what-you-need)
3. [Understanding DIP Switches](#understanding-dip-switches)
4. [Step-by-Step Configuration](#step-by-step-configuration)
5. [DIP Switch Reference Tables](#dip-switch-reference-tables)
6. [Common Engine Configurations](#common-engine-configurations)
7. [Troubleshooting](#troubleshooting)
8. [Validation & Testing](#validation--testing)

---

## Introduction

The CX5106 Engine Gateway converts analog engine signals (like alternator pulses, ignition signals, or magnetic pickups) into NMEA2000 digital data that your chartplotter or multi-function display can understand.

This manual will help you configure the 8 DIP switches on your CX5106 so it correctly reads your engine and sends accurate RPM, temperature, and other data to your NMEA2000 network.

**Important**: Incorrect DIP switch settings will cause wrong RPM readings, erratic data, or no data at all.

---

## What You Need

Before you begin, gather this information about your engine:

### Required Information Checklist

□ **Number of engines on your boat** (1, 2, 3, or 4)  
□ **Which engine this CX5106 connects to** (Primary, Port, Starboard, Center)  
□ **Type of RPM signal** (see "Identifying Your RPM Signal" below)  
□ **Number of cylinders** (3, 4, 6, or 8)  
□ **Engine stroke type** (2-stroke or 4-stroke)  
□ **Gear ratio** (1:1 direct drive or 2:1 reduction gear)

### Tools Needed

- Small flathead screwdriver or pen (to flip DIP switches)
- Your engine owner's manual (helpful but not required)
- Multimeter (optional - for advanced troubleshooting)

---

## Understanding DIP Switches

### What is a DIP Switch?

A DIP switch is a small physical switch that can be set to ON (up) or OFF (down). The CX5106 has 8 switches arranged in a row.

```
┌─┬─┬─┬─┬─┬─┬─┬─┐
│1│2│3│4│5│6│7│8│  ← Switch numbers
├─┼─┼─┼─┼─┼─┼─┼─┤
│↑│↓│↑│↓│↑│↓│↑│↓│  ← UP = ON, DOWN = OFF
└─┴─┴─┴─┴─┴─┴─┴─┘
```

### Location on CX5106

The DIP switches are located on the side of the CX5106 unit. They are clearly labeled 1-8 from left to right.

**Visual Reference:**

![CX5106 DIP Switches](../../assets/images/cx5106_10125.png)

*Photo showing the actual CX5106 DIP switch locations*

**IMPORTANT**:
- Always power OFF the CX5106 before changing switches
- After setting switches, power cycle (turn off, wait 10 seconds, turn on)
- Changes do NOT take effect until after power cycle

---

## Step-by-Step Configuration

### STEP 1: Determine Engine Instance (Switches 1 & 2)

**Question**: How many engines does your boat have, and which one is this?

#### If you have ONE engine:
Set both switches to **OFF (down)**

```
SW1: ↓ OFF
SW2: ↓ OFF
```

#### If you have TWO engines:
**First CX5106 (Port/Left Engine):**
```
SW1: ↑ ON
SW2: ↓ OFF
```

**Second CX5106 (Starboard/Right Engine):**
```
SW1: ↓ OFF
SW2: ↑ ON
```

#### If you have THREE engines:
**First CX5106 (Port):**
```
SW1: ↑ ON
SW2: ↓ OFF
```

**Second CX5106 (Center):**
```
SW1: ↓ OFF
SW2: ↓ OFF
```

**Third CX5106 (Starboard):**
```
SW1: ↓ OFF
SW2: ↑ ON
```

#### Reference Table: Engine Instance

| SW1 | SW2 | Instance | Typical Use |
|-----|-----|----------|-------------|
| OFF | OFF | Instance 0 | Single engine OR center engine |
| ON  | OFF | Instance 1 | Port (left) engine |
| OFF | ON  | Instance 2 | Starboard (right) engine |
| ON  | ON  | Instance 3 | Auxiliary/Generator |

---

### STEP 2: Identify Your RPM Signal Source (Switches 3 & 4)

This is the most critical setting. You need to know where the CX5106 gets its RPM signal from.

#### Identifying Your RPM Signal

**ALTERNATOR W-TERMINAL** (Most Common)
- Look at your alternator (the belt-driven component that charges your battery)
- Find a small terminal labeled "W", "~", or "AC"
- Usually a single thin wire coming from this terminal
- **Common on**: Older engines, diesel engines, inboard gas engines

**IGNITION COIL** (Gasoline Engines)
- For gasoline engines with traditional distributor or coil packs
- Signal comes from the negative (-) side of the ignition coil
- **Common on**: Older gasoline inboard engines, some I/O drives

**MAGNETIC PICKUP** (Diesel Engines)
- A sensor mounted near the flywheel or harmonic balancer
- Detects metal teeth passing by
- Usually has 2 wires (signal and ground)
- **Common on**: Modern diesel engines (Yanmar, Volvo, Cummins)

**ECU DIGITAL OUTPUT** (Modern Engines)
- Direct digital signal from Engine Control Unit
- **Common on**: Newer engines (2010+) with advanced ECUs

---

#### How to Set Switches 3 & 4

**If you have ALTERNATOR W-TERMINAL:**
```
SW3: ↓ OFF
SW4: ↓ OFF
```

**If you have IGNITION COIL:**
```
SW3: ↑ ON
SW4: ↓ OFF
```

**If you have MAGNETIC PICKUP:**
```
SW3: ↓ OFF
SW4: ↑ ON
```

**If you have ECU DIGITAL OUTPUT:**
```
SW3: ↑ ON
SW4: ↑ ON
```

#### Reference Table: RPM Signal Source

| SW3 | SW4 | Signal Type | When to Use |
|-----|-----|-------------|-------------|
| OFF | OFF | Alternator W-Terminal | Most older engines, simple setups |
| ON  | OFF | Ignition Coil | Gasoline engines, spark ignition |
| OFF | ON  | Magnetic Pickup | Diesel engines, flywheel sensor |
| ON  | ON  | ECU Digital | Modern engines with ECU output |

---

### STEP 3: Set Number of Cylinders (Switches 5 & 6)

**Question**: How many cylinders does your engine have?

You can usually find this in:
- Engine model number (e.g., "4JH" = 4 cylinder, "6LPA" = 6 cylinder)
- Owner's manual
- Stamped on engine block
- Online search of engine make/model

#### How to Set Switches 5 & 6

**If you have 3 CYLINDERS:**
```
SW5: ↑ ON
SW6: ↑ ON
```

**If you have 4 CYLINDERS:**
```
SW5: ↓ OFF
SW6: ↓ OFF
```

**If you have 6 CYLINDERS:**
```
SW5: ↑ ON
SW6: ↓ OFF
```

**If you have 8 CYLINDERS:**
```
SW5: ↓ OFF
SW6: ↑ ON
```

#### Reference Table: Number of Cylinders

| SW5 | SW6 | Cylinders | Common Engines |
|-----|-----|-----------|----------------|
| OFF | OFF | 4 cylinders | Most inboard diesels, 4-cyl gas |
| ON  | OFF | 6 cylinders | V6 gas, inline-6 diesel |
| OFF | ON  | 8 cylinders | V8 gas (Mercruiser, Crusader) |
| ON  | ON  | 3 cylinders | Small diesels (Yanmar 3YM30) |

---

### STEP 4: Set Engine Stroke Type (Switch 7)

**Question**: Is your engine a 2-stroke or 4-stroke?

**How to tell:**
- **4-Stroke** = Most modern engines (all diesels, most inboard gas)
- **2-Stroke** = Older outboards, some small displacement engines
- If you have oil in your crankcase (dipstick) = 4-stroke
- If you mix oil with fuel = 2-stroke

#### How to Set Switch 7

**If you have a 4-STROKE engine:**
```
SW7: ↓ OFF
```

**If you have a 2-STROKE engine:**
```
SW7: ↑ ON
```

#### Reference Table: Stroke Type

| SW7 | Engine Type | Common Examples |
|-----|-------------|-----------------|
| OFF | 4-Stroke | All diesels, modern inboards, new outboards |
| ON  | 2-Stroke | Older outboards (pre-2000), some small engines |

**When in doubt**: Almost all marine engines today are 4-stroke. Select OFF.

---

### STEP 5: Set Gear Ratio (Switch 8)

**Question**: Does your engine have a reduction gear, or is it direct drive?

**How to tell:**
- **Direct Drive (1:1)**: Engine shaft directly connected to prop shaft, no gearbox
- **Reduction Gear (2:1)**: Engine shaft goes through a reduction gear before prop shaft
  - Common on sailboats and displacement hulls
  - Allows engine to run at higher RPM while prop turns slower

**Finding your gear ratio:**
- Check engine manual or transmission spec sheet
- Look for numbers like "1:1", "2:1", "2.5:1"
- Common sailboat ratios: 2:1, 2.5:1, 3:1

#### How to Set Switch 8

**If you have DIRECT DRIVE (1:1 ratio):**
```
SW8: ↓ OFF
```

**If you have 2:1 REDUCTION GEAR:**
```
SW8: ↑ ON
```

**If you have OTHER RATIOS (2.5:1, 3:1, etc.):**
```
SW8: ↓ OFF  (Set to direct drive)
Note: Displayed RPM will need manual correction
```

#### Reference Table: Gear Ratio

| SW8 | Ratio | When to Use |
|-----|-------|-------------|
| OFF | 1:1 Direct Drive | No reduction gear, V-drives, straight shaft |
| ON  | 2:1 Reduction | Reduction gear box, some sailboats |

**IMPORTANT**: If your ratio is NOT exactly 1:1 or 2:1 (e.g., 1.5:1, 2.5:1), see the troubleshooting section for RPM correction factors.

---

## DIP Switch Reference Tables

### Complete Configuration Matrix

| Function | Switches | Setting Options |
|----------|----------|-----------------|
| **Engine Instance** | SW1, SW2 | 0 (single), 1 (port), 2 (starboard), 3 (aux) |
| **RPM Source** | SW3, SW4 | Alternator, Ignition, Magnetic, ECU |
| **Cylinders** | SW5, SW6 | 3, 4, 6, or 8 |
| **Stroke Type** | SW7 | 2-stroke or 4-stroke |
| **Gear Ratio** | SW8 | 1:1 or 2:1 |

---

## Common Engine Configurations

These are pre-configured settings for popular marine engines. Find yours and copy the DIP switch positions exactly.

---

### **Yanmar 3YM30 Diesel (Sailboat)**

**Engine Specs:**
- 3 cylinders, 4-stroke diesel
- Magnetic pickup sensor
- 2:1 reduction gear (common on sailboats)

**DIP Switch Settings:**
```
SW1: ↓ OFF  (Single engine)
SW2: ↓ OFF
SW3: ↓ OFF  (Magnetic pickup)
SW4: ↑ ON
SW5: ↑ ON   (3 cylinders)
SW6: ↑ ON
SW7: ↓ OFF  (4-stroke)
SW8: ↑ ON   (2:1 gear ratio)
```

---

### **Mercruiser 7.4L V8 (1994 - Bravo II Drive)**

**Engine Specs:**
- 8 cylinders, 4-stroke gasoline
- Alternator W-terminal
- 1.5:1 gear ratio (use 1:1 setting, see note)

**DIP Switch Settings:**
```
SW1: ↓ OFF  (Single engine)
SW2: ↓ OFF
SW3: ↓ OFF  (Alternator W-terminal)
SW4: ↓ OFF
SW5: ↓ OFF  (8 cylinders)
SW6: ↑ ON
SW7: ↓ OFF  (4-stroke)
SW8: ↓ OFF  (1:1 - see note below)
```

**NOTE**: Bravo II has 1.5:1 ratio, not supported by CX5106. Set to 1:1 (OFF). Displayed RPM will be 1.5x actual. Divide displayed RPM by 1.5 for true engine RPM.

---

### **Volvo Penta D4-260 Diesel (Twin Engine - Port)**

**Engine Specs:**
- 4 cylinders, 4-stroke diesel
- Alternator W-terminal
- Direct drive (1:1)

**DIP Switch Settings:**
```
SW1: ↑ ON   (Port engine = Instance 1)
SW2: ↓ OFF
SW3: ↓ OFF  (Alternator W-terminal)
SW4: ↓ OFF
SW5: ↓ OFF  (4 cylinders)
SW6: ↓ OFF
SW7: ↓ OFF  (4-stroke)
SW8: ↓ OFF  (1:1 direct drive)
```

**For Starboard Engine**: Same settings except SW1=OFF, SW2=ON

---

### **Yanmar 6LPA-STP2 Diesel (6-cylinder)**

**Engine Specs:**
- 6 cylinders, 4-stroke diesel
- Magnetic pickup
- Direct drive (1:1)

**DIP Switch Settings:**
```
SW1: ↓ OFF  (Single engine)
SW2: ↓ OFF
SW3: ↓ OFF  (Magnetic pickup)
SW4: ↑ ON
SW5: ↑ ON   (6 cylinders)
SW6: ↓ OFF
SW7: ↓ OFF  (4-stroke)
SW8: ↓ OFF  (1:1 direct drive)
```

---

### **Mercury 90HP Outboard (2-Stroke)**

**Engine Specs:**
- 4 cylinders, 2-stroke
- Ignition coil signal
- Direct drive

**DIP Switch Settings:**
```
SW1: ↓ OFF  (Single engine)
SW2: ↓ OFF
SW3: ↑ ON   (Ignition coil)
SW4: ↓ OFF
SW5: ↓ OFF  (4 cylinders)
SW6: ↓ OFF
SW7: ↑ ON   (2-stroke)
SW8: ↓ OFF  (Direct drive)
```

---

### **Cummins QSB 5.9L Diesel**

**Engine Specs:**
- 6 cylinders, 4-stroke diesel
- ECU digital output
- Direct drive

**DIP Switch Settings:**
```
SW1: ↓ OFF  (Single engine)
SW2: ↓ OFF
SW3: ↑ ON   (ECU digital)
SW4: ↑ ON
SW5: ↑ ON   (6 cylinders)
SW6: ↓ OFF
SW7: ↓ OFF  (4-stroke)
SW8: ↓ OFF  (Direct drive)
```

---

## Troubleshooting

### Problem: RPM Shows Zero

**Possible Causes:**

1. **Wrong RPM source selected (SW3/SW4)**
   - **Solution**: Verify your RPM signal type and set SW3/SW4 correctly
   - Use a multimeter to confirm signal is present at CX5106 input

2. **Wrong cylinder count (SW5/SW6)**
   - **Solution**: Double-check your engine specs and set correctly

3. **Physical wiring problem**
   - **Solution**: Check wire connections between engine and CX5106
   - Verify wire is connected to correct terminal (W-terminal, coil, sensor)

4. **Did not power cycle after setting switches**
   - **Solution**: Turn CX5106 off, wait 10 seconds, turn back on

---

### Problem: RPM is Double (or Half) Actual RPM

**Cause**: Wrong gear ratio setting (SW8)

**Solution**:
- If RPM shows **double** actual: Change SW8 from OFF to ON
- If RPM shows **half** actual: Change SW8 from ON to OFF
- Power cycle after changing

---

### Problem: RPM Fluctuates Wildly

**Cause**: Usually wrong cylinder count (SW5/SW6)

**Solution**:
1. Verify actual number of cylinders on your engine
2. Set SW5/SW6 to match cylinder count exactly
3. Power cycle CX5106

**Less Common Causes:**
- Wrong stroke type (SW7) - verify 2-stroke vs 4-stroke
- Loose or corroded wire connection - clean and tighten connections

---

### Problem: RPM Shows 1.5x Actual (or Other Odd Multiplier)

**Cause**: Your gear ratio is not exactly 1:1 or 2:1

**Common Non-Standard Ratios:**
- 1.5:1 (Mercruiser Bravo II)
- 2.5:1 (common sailboat ratio)
- 3:1 (heavy displacement hulls)

**Solution**:

Set SW8 to OFF (1:1 mode), then calculate correction factor:

```
True Engine RPM = Displayed RPM ÷ Gear Ratio

Examples:
- 1.5:1 ratio → Divide displayed RPM by 1.5
  (Display shows 3000 → Actual is 2000)
  
- 2.5:1 ratio → Divide displayed RPM by 2.5
  (Display shows 5000 → Actual is 2000)
```

**Make a label for your helm:**
```
┌────────────────────────────────┐
│  RPM CORRECTION NEEDED         │
│  Gear Ratio: 1.5:1             │
│  Divide displayed RPM by 1.5   │
│                                │
│  Display → Actual              │
│  3000   →  2000                │
│  4500   →  3000                │
└────────────────────────────────┘
```

---

### Problem: No Data on Chartplotter

**Checklist:**

□ CX5106 has power (LED is on)  
□ CX5106 is connected to NMEA2000 backbone  
□ NMEA2000 backbone has termination resistors at both ends  
□ NMEA2000 backbone has 12V power  
□ Chartplotter is configured to display engine data  
□ Correct engine instance is selected on chartplotter  

**Solutions:**
1. Check NMEA2000 physical connections
2. Verify backbone power (should be 12V DC)
3. Check chartplotter settings for engine data pages
4. Try different engine instance on chartplotter display

---

## Validation & Testing

### Initial Testing Procedure

After setting DIP switches:

**1. Power Cycle CX5106**
- Turn off power to CX5106
- Wait 10 seconds
- Turn power back on

**2. Start Engine (at dock, in neutral)**
- Let engine idle for 1 minute
- Note RPM on chartplotter

**3. Verify RPM Reading**
- Compare chartplotter RPM to:
  - Engine tachometer (if equipped)
  - Published idle RPM for your engine
  - Typical idle range (600-800 RPM for most engines)

**4. Test at Higher RPM**
- Increase throttle to ~1500 RPM (in neutral, at dock)
- Verify RPM changes smoothly on chartplotter
- Check for fluctuations or erratic readings

**5. On-Water Testing**
- Take boat out (calm conditions)
- Run at cruise RPM
- Verify RPM reads correctly under load
- Note any differences between no-load and under-load readings

---

### Expected RPM Ranges (for validation)

| Engine Type | Idle RPM | Cruise RPM | Max RPM (WOT) |
|-------------|----------|------------|---------------|
| Small Diesel (3-4 cyl) | 600-800 | 2000-2400 | 3000-3600 |
| Large Diesel (6-8 cyl) | 600-750 | 1800-2200 | 2400-2800 |
| Gas Inboard (V8) | 700-900 | 3000-3500 | 4200-4800 |
| Gas Outboard | 600-800 | 4000-5000 | 5500-6500 |

**If your readings are far outside these ranges**, recheck your DIP switch settings.

---

### Configuration Record

**Fill this out and keep with your boat documentation:**

```
CX5106 CONFIGURATION RECORD
═══════════════════════════════════

Boat: _________________________________
Engine Make: __________________________
Engine Model: _________________________
Year: _________________________________

DIP SWITCH SETTINGS:
┌─┬─┬─┬─┬─┬─┬─┬─┐
│1│2│3│4│5│6│7│8│
├─┼─┼─┼─┼─┼─┼─┼─┤
│ │ │ │ │ │ │ │ │  ← Mark each switch ↑ or ↓
└─┴─┴─┴─┴─┴─┴─┴─┘

Configuration Details:
Engine Instance: _______________
RPM Source: ____________________
Cylinders: _____________________
Stroke Type: ___________________
Gear Ratio: ____________________

RPM Correction Factor (if needed): _______

Configured by: _____________________
Date: ______________________________

Notes:
_____________________________________
_____________________________________
_____________________________________
```

---

## Quick Reference Card

**Print and laminate this for your boat:**

```
╔════════════════════════════════════════╗
║   CX5106 DIP SWITCH QUICK REFERENCE    ║
╠════════════════════════════════════════╣
║                                        ║
║  SW1-2: ENGINE INSTANCE                ║
║    OFF/OFF = Single/Primary            ║
║    ON/OFF  = Port (left)               ║
║    OFF/ON  = Starboard (right)         ║
║                                        ║
║  SW3-4: RPM SOURCE                     ║
║    OFF/OFF = Alternator W-term         ║
║    ON/OFF  = Ignition coil             ║
║    OFF/ON  = Magnetic pickup           ║
║    ON/ON   = ECU digital               ║
║                                        ║
║  SW5-6: CYLINDERS                      ║
║    OFF/OFF = 4 cyl                     ║
║    ON/OFF  = 6 cyl                     ║
║    OFF/ON  = 8 cyl                     ║
║    ON/ON   = 3 cyl                     ║
║                                        ║
║  SW7: STROKE                           ║
║    OFF = 4-stroke                      ║
║    ON  = 2-stroke                      ║
║                                        ║
║  SW8: GEAR RATIO                       ║
║    OFF = 1:1 direct                    ║
║    ON  = 2:1 reduction                 ║
║                                        ║
║  ⚠️ ALWAYS POWER CYCLE AFTER CHANGES   ║
╚════════════════════════════════════════╝
```

---

## Additional Resources

### Finding Your Engine Information

**If you don't have your engine manual:**

1. **Engine Model Number**: Usually stamped on engine block or valve cover
2. **Online Search**: "[Make] [Model] specifications" (e.g., "Yanmar 3YM30 specifications")
3. **Manufacturer Website**: Most have spec sheets available
4. **Marine Forums**: Sites like The Hull Truth, Cruisers Forum have knowledgeable users
5. **Your Marina**: Service technicians can usually identify engine details

### Need More Help?

If you're still having trouble:
- Post on marine electronics forums with photos of your engine
- Contact CX5106 manufacturer support
- Consult a marine electronics installer
- Check helm-OS community forums (if available)

---

## Safety Notes

⚠️ **Before Making Changes:**
- Always turn off power to CX5106
- Work in a well-ventilated area
- Keep tools and materials away from fuel and electrical systems
- If uncertain, consult a professional marine technician

⚠️ **While Testing:**
- Test at dock first before going on water
- Have someone monitor the engine while you check displays
- Never exceed safe RPM ranges during testing
- Ensure proper ventilation when running engine

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Compatible with:** CX5106 Engine Gateway (all versions)

---

*This manual is provided as a guide. Always refer to your engine and equipment manufacturer's documentation for authoritative specifications and safety information.*
