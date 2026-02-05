# CX5106 Engine Gateway - Configuration Guide

## Overview

The CX5106 is an analog-to-NMEA2000 engine gateway that converts analog engine signals into NMEA2000 PGNs for display on marine chartplotters and multi-function displays.

**Hardware:**
- Raspberry Pi 4B
- PiCAN-M HAT
- CX5106 Engine Gateway
- NMEA2000 backbone

---

## Part 1: DIP Switch Configuration Logic

The CX5106 has **8 DIP switches** that control how it operates and what PGNs it outputs.

### DIP Switch Functions

Based on the CX5106 manual analysis:

#### **Switches 1-2: Engine Instance Selection**
Controls which engine instance number is assigned on the NMEA2000 network.

| SW1 | SW2 | Engine Instance |
|-----|-----|-----------------|
| OFF | OFF | Instance 0 (Primary/Single Engine) |
| ON  | OFF | Instance 1 (Port Engine) |
| OFF | ON  | Instance 2 (Starboard Engine) |
| ON  | ON  | Instance 3 (Center/Auxiliary) |

**Purpose**: Prevents instance conflicts when multiple engines are on the same NMEA2000 network.

---

#### **Switches 3-4: RPM Source Configuration**
Selects the type of signal input for RPM measurement.

| SW3 | SW4 | RPM Source Type | Description |
|-----|-----|-----------------|-------------|
| OFF | OFF | Alternator W-Terminal | AC signal from alternator W terminal |
| ON  | OFF | Ignition Coil | Gasoline engine ignition pulse |
| OFF | ON  | Magnetic Pickup | Diesel flywheel sensor |
| ON  | ON  | ECU Digital Output | Direct from engine ECU |

**Purpose**: Matches the CX5106 input configuration to the actual engine signal type.

---

#### **Switches 5-6: Number of Cylinders**
Sets cylinder count for accurate RPM calculation.

| SW5 | SW6 | Cylinders |
|-----|-----|-----------|
| OFF | OFF | 4 cylinders |
| ON  | OFF | 6 cylinders |
| OFF | ON  | 8 cylinders |
| ON  | ON  | 3 cylinders |

**Purpose**: The CX5106 uses cylinder count to calculate RPM from the incoming pulse frequency.

---

#### **Switch 7: Engine Stroke Type**
Selects between 2-stroke and 4-stroke engine timing.

| SW7 | Engine Type |
|-----|-------------|
| OFF | 4-Stroke |
| ON  | 2-Stroke |

**Purpose**: 2-stroke engines fire once per revolution, 4-stroke engines fire once every two revolutions.

---

#### **Switch 8: Gear Ratio**
Adjusts RPM calculation for geared engines.

| SW8 | Gear Ratio |
|-----|------------|
| OFF | 1:1 (Direct Drive) |
| ON  | 2:1 (Reduction Gear) |

**Purpose**: If the RPM sensor reads propeller shaft speed instead of engine crankshaft, this corrects the displayed RPM.

**Note**: Some engines use 2.5:1 or other ratios - in these cases, use OFF and note that displayed RPM will need manual interpretation.

---

## Part 2: Required Wizard Questions

To automatically configure the CX5106 DIP switches, the helm-OS wizard must ask these questions:

### **Question 1: Number of Engines**
**Question**: "How many engines does your vessel have?"

**Options**:
- Single engine
- Twin engines (port/starboard)
- Triple engines
- Quad engines

**Maps to**: DIP Switches 1-2 (Engine Instance)

**Logic**:
```
Single engine → SW1: OFF, SW2: OFF (Instance 0)
Twin engines → First engine: OFF/OFF, Second engine: ON/OFF
```

---

### **Question 2: Engine Position** (if multiple engines)
**Question**: "Which engine is this CX5106 connected to?"

**Options**:
- Primary/Single
- Port (left)
- Starboard (right)
- Center/Auxiliary

**Maps to**: DIP Switches 1-2 (Engine Instance)

---

### **Question 3: RPM Signal Source**
**Question**: "What type of RPM signal does your engine provide?"

**Options**:
- Alternator W-Terminal (most common on older engines)
- Ignition Coil (gasoline engines)
- Magnetic Pickup on Flywheel (diesel engines)
- ECU Digital Output (modern engines)
- I don't know

**Maps to**: DIP Switches 3-4 (RPM Source)

**Help Text**:
- **Alternator W-Terminal**: Look for a single wire terminal on the alternator labeled "W" or "~"
- **Ignition Coil**: Gasoline engines - signal from coil negative terminal
- **Magnetic Pickup**: Diesel engines - sensor mounted near flywheel
- **ECU**: Modern engines with digital engine management

**If "I don't know"**:
- AI suggests based on engine make/model/year
- Default: Alternator W-Terminal (most common)

---

### **Question 4: Number of Cylinders**
**Question**: "How many cylinders does your engine have?"

**Options**:
- 3 cylinders
- 4 cylinders
- 6 cylinders
- 8 cylinders

**Maps to**: DIP Switches 5-6 (Cylinders)

**Validation**: Cross-check with engine make/model if known

---

### **Question 5: Engine Stroke Type**
**Question**: "Is your engine a 2-stroke or 4-stroke?"

**Options**:
- 4-Stroke (most common - diesel and modern gasoline)
- 2-Stroke (older outboards, some small engines)

**Maps to**: DIP Switch 7 (Stroke)

**Help Text**: 
- **4-Stroke**: Most modern marine engines (diesel, inboard gasoline)
- **2-Stroke**: Older outboards, some small displacement engines

---

### **Question 6: Gear Ratio**
**Question**: "What is your engine's gear ratio?"

**Options**:
- 1:1 (Direct Drive - no reduction gear)
- 2:1 (2:1 Reduction Gear)
- Other ratio (manual entry)

**Maps to**: DIP Switch 8 (Gear Ratio)

**Help Text**:
- **1:1**: Engine shaft directly connected to propeller shaft
- **2:1**: Common on sailboats and displacement hulls
- **Other**: If your ratio is 2.5:1, 3:1, etc., select "1:1" and note RPM will display 2x actual

**Advanced**: Store actual ratio in config for future RPM correction

---

## Part 3: Wizard Flow Integration

### Step-by-Step Configuration

**Step 1: Engine Count Detection**
```
Question: "How many engines?"
User Answer: "Twin engines"
System Action: Prepare for 2 CX5106 configurations
```

**Step 2: Per-Engine Configuration Loop**
For each engine:

```
Wizard: "Configuring Engine 1 (Port)"

Q1: Engine position? → Port
    Maps to: SW1=ON, SW2=OFF (Instance 1)

Q2: RPM signal source? → Alternator W-Terminal
    Maps to: SW3=OFF, SW4=OFF

Q3: Number of cylinders? → 4
    Maps to: SW5=OFF, SW6=OFF

Q4: Stroke type? → 4-Stroke
    Maps to: SW7=OFF

Q5: Gear ratio? → 2:1
    Maps to: SW8=ON

System: Generates DIP switch diagram:
┌─┬─┬─┬─┬─┬─┬─┬─┐
│1│2│3│4│5│6│7│8│
├─┼─┼─┼─┼─┼─┼─┼─┤
│↑│↓│↓│↓│↓│↓│↓│↑│
└─┴─┴─┴─┴─┴─┴─┴─┘
```

**Step 3: Visual Confirmation**
Display clear diagram showing:
- Which switches to set UP (ON)
- Which switches to set DOWN (OFF)
- Physical location on CX5106 unit
- Photo/diagram of actual hardware

**Step 4: Verification Prompt**
```
"Please set the DIP switches as shown above, then press Next.

⚠️ Important: Power cycle the CX5106 after changing DIP switches.
Turn off power, wait 10 seconds, turn back on.
```

---

## Part 4: AI-Assisted Configuration

### When User Selects "I Don't Know"

**If user doesn't know RPM signal source:**

AI inference based on:
- Engine make/model/year
- Fuel type (diesel vs gasoline)
- Engine age

Example:
```
Engine: Yanmar 3YM30, 2015, Diesel
AI Inference: "Magnetic Pickup on Flywheel"
Reasoning: "Modern diesel engines typically use magnetic pickups"
Confidence: High
```

**If user doesn't know stroke type:**

AI inference based on:
- Engine make/model
- Fuel type
- Displacement

Example:
```
Engine: Mercury 90HP Outboard, 2008
AI Inference: "2-Stroke"
Reasoning: "Mercury outboards before 2010 were predominantly 2-stroke"
Confidence: Medium
User Prompt: "Please verify in your engine manual"
```

---

## Part 5: JSON Configuration Storage

### config/boat-active.json

```json
{
  "engine": {
    "manufacturer": "Yanmar",
    "model": "3YM30",
    "cylinders": 3,
    "stroke": "4-stroke",
    "fuel_type": "diesel",
    "gear_ratio": "2:1"
  },
  "gateway": {
    "model": "CX5106",
    "switches": {
      "sw1": "ON",   // Engine instance 1 (port)
      "sw2": "OFF",
      "sw3": "OFF",  // Magnetic pickup
      "sw4": "ON",
      "sw5": "ON",   // 3 cylinders
      "sw6": "ON",
      "sw7": "OFF",  // 4-stroke
      "sw8": "ON"    // 2:1 gear ratio
    },
    "instance": 1,
    "rpm_source": "magnetic_pickup",
    "notes": "Port engine - Yanmar 3YM30 diesel with 2:1 reduction gear"
  }
}
```

---

## Part 6: Common Configurations

### Configuration Presets

#### **Single Yanmar 3YM30 Diesel**
```
SW1: OFF    (Instance 0)
SW2: OFF
SW3: OFF    (Magnetic pickup)
SW4: ON
SW5: ON     (3 cylinders)
SW6: ON
SW7: OFF    (4-stroke)
SW8: ON     (2:1 gear)
```

#### **Twin Volvo Penta D4 Diesel (Port Engine)**
```
SW1: ON     (Instance 1 - Port)
SW2: OFF
SW3: OFF    (Alternator W-terminal)
SW4: OFF
SW5: OFF    (4 cylinders)
SW6: OFF
SW7: OFF    (4-stroke)
SW8: OFF    (1:1 direct drive)
```

#### **Single Mercruiser 5.7L Gasoline V8**
```
SW1: OFF    (Instance 0)
SW2: OFF
SW3: ON     (Ignition coil)
SW4: OFF
SW5: OFF    (8 cylinders)
SW6: ON
SW7: OFF    (4-stroke)
SW8: OFF    (1:1 direct)
```

---

## Part 7: Troubleshooting

### RPM Reading is Double Actual
**Cause**: Wrong gear ratio setting
**Fix**: Change SW8 from OFF to ON (or vice versa)

### RPM Reading is Zero
**Possible Causes**:
1. Wrong RPM source (SW3/SW4)
2. Wrong cylinder count (SW5/SW6)
3. Wrong stroke type (SW7)
4. Physical wiring issue

**Debug Steps**:
1. Verify signal wire connected to correct engine terminal
2. Check DIP switches match wizard configuration
3. Power cycle CX5106
4. Check NMEA2000 backbone termination

### RPM Fluctuates Wildly
**Cause**: Usually wrong cylinder count
**Fix**: Verify actual cylinder count and set SW5/SW6 correctly

---

## Summary

### 6 Critical Questions for CX5106 Configuration:

1. **Number of engines** → SW1/SW2 (Instance)
2. **Engine position** (if multiple) → SW1/SW2 (Instance)
3. **RPM signal source** → SW3/SW4 (Signal Type)
4. **Number of cylinders** → SW5/SW6 (Cylinder Count)
5. **Engine stroke type** → SW7 (2-stroke/4-stroke)
6. **Gear ratio** → SW8 (1:1 or 2:1)

### Output:
- Visual DIP switch diagram
- JSON configuration
- Setup instructions
- Verification steps

This ensures the CX5106 correctly converts analog engine signals to NMEA2000 PGNs that chartplotters can display.
