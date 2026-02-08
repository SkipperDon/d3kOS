# HELM-OS ONBOARDING GUIDE

**Version**: 2.0
**Last Updated**: February 6, 2026

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Onboarding Wizard Flow](#onboarding-wizard-flow)
3. [Question Details](#question-details)
4. [CX5106 DIP Switch Configuration](#cx5106-dip-switch-configuration)
5. [QR Code Generation](#qr-code-generation)
6. [Reset Counter](#reset-counter)
7. [Onboarding Best Practices](#onboarding-best-practices)
8. [Troubleshooting Onboarding](#troubleshooting-onboarding)

---

## OVERVIEW

The d3kOS onboarding wizard is a 13-question process that collects critical information about your marine engine. This data is used to:

- Configure the CX5106 NMEA2000 gateway DIP switches
- Establish engine performance baselines
- Enable accurate anomaly detection
- Optimize threshold settings for alerts

### Time Required

- **Typical completion**: 10-15 minutes
- **With AI assistance**: 5-10 minutes (if you know your engine specs)
- **Research required**: 20-30 minutes (if you need to look up specifications)

### When to Run Onboarding

- **First boot** (automatically launched)
- **Engine replacement** (reset and reconfigure)
- **Incorrect configuration** (reset and try again)

### Onboarding Limits

- **Tier 0 (Free)**: 10 resets maximum
- **Tier 2+ (Paid)**: Unlimited resets

---

## ONBOARDING WIZARD FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                    ONBOARDING WIZARD                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Welcome Screen                                     │
│  - Introduction to onboarding process                       │
│  - Estimated time: 10-15 minutes                            │
│  - Have engine manual ready                                 │
│  - [Start] button                                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Steps 2-16: Configuration Questions (Q1-Q15)              │
│  - Q1-Q13: Engine specifications                            │
│  - Q14: Tank sensor standard (regional)                     │
│  - Q15: Engine position (if multi-engine)                   │
│  - Each question on separate page                           │
│  - Progress indicator: "Step X of 15"                       │
│  - [Back] [Next] [Save & Exit] buttons                      │
│  - Auto-save progress                                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 15: CX5106 DIP Switch Configuration                  │
│  - Visual diagram of DIP switches                           │
│  - Detailed explanation of each switch                      │
│  - Why these settings for your engine                       │
│  - [Print] [Save PDF] [Next] buttons                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 16: QR Code Generation                               │
│  - Installation ID generated                                │
│  - QR code displayed                                        │
│  - Instructions for mobile app pairing                      │
│  - [Regenerate] [Complete] buttons                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 17: Completion                                        │
│  - Summary of configuration                                 │
│  - Next steps: Run engine baseline                          │
│  - [Go to Main Menu] button                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## QUESTION DETAILS

### Question 1: Engine Manufacturer

**Purpose**: Identify engine manufacturer for AI-assisted data population

**Input Type**: Autocomplete dropdown

**Example Manufacturers**:
- Mercury Marine
- Yamaha
- Honda
- Suzuki
- Volvo Penta
- Yanmar
- Cummins
- Caterpillar
- John Deere

**How to Answer**:
1. Start typing manufacturer name
2. Select from dropdown suggestions
3. If not found, type full name manually

**AI Assistance**:
- Suggests popular marine engine manufacturers as you type
- Filters list based on input
- Offers "Other" option for unlisted manufacturers

**Validation**:
- Required field
- Minimum 2 characters

**Example**:
```
Manufacturer: [Mercury Marine▼]
              [Mercury Marine     ]
              [Mercruiser         ]
              [Mermaid Marine     ]
```

---

### Question 2: Engine Model

**Purpose**: Identify specific engine model for baseline data

**Input Type**: Autocomplete dropdown (filtered by manufacturer)

**How to Answer**:
1. Model list is filtered based on Q1 manufacturer
2. Start typing model number
3. Select from suggestions
4. If not found, enter manually

**AI Assistance**:
- Pre-populated with known models for selected manufacturer
- Suggests similar models
- Auto-fills known specifications if model is in database

**Validation**:
- Required field
- Minimum 2 characters

**Example**:
```
Model: [5.0L MPI Alpha▼]
       [5.0L MPI Alpha            ]
       [5.0L MPI Bravo            ]
       [5.7L MPI Alpha            ]
```

---

### Question 3: Engine Year

**Purpose**: Identify engine generation for specification lookup

**Input Type**: Number input (1950-2026)

**How to Answer**:
1. Enter 4-digit year (e.g., 2018)
2. Use on-screen keyboard or physical keyboard

**AI Assistance**:
- Suggests likely year range based on model
- Warns if year seems inconsistent with model

**Validation**:
- Must be between 1950 and current year (2026)
- Must be 4-digit number

**Default**: 2010

**Example**:
```
Year: [2018____]
      Use keyboard to enter year
```

---

### Question 4: Number of Cylinders

**Purpose**: Calculate RPM sensor configuration

**Input Type**: Dropdown selection

**Options**:
- 1 cylinder
- 2 cylinders
- 3 cylinders
- 4 cylinders
- 6 cylinders
- 8 cylinders
- 12 cylinders

**How to Answer**:
1. Select from dropdown
2. Common: 4 (outboards), 6 (sterndrives), 8 (V8 inboards)

**AI Assistance**:
- Auto-populated from model database if available
- Suggests typical configuration for engine type

**Validation**:
- Required field

**Default**: 4 cylinders

**CX5106 Impact**: Determines ignition pulse multiplication factor

**Example**:
```
Cylinders: [4▼]
           [1 cylinder  ]
           [2 cylinders ]
           [3 cylinders ]
           [4 cylinders ✓]
           [6 cylinders ]
           [8 cylinders ]
```

---

### Question 5: Engine Displacement

**Purpose**: Calculate power output and fuel consumption baselines

**Input Type**: Dual number input (Liters OR Cubic Inches)

**How to Answer**:
1. Enter displacement in either liters or cubic inches
2. Conversion happens automatically in real-time
3. Both values update as you type

**Conversion**: 1 Liter = 61.024 Cubic Inches

**AI Assistance**:
- Auto-calculated from cylinders + stroke if Q7 is answered first
- Suggests typical displacement for engine type

**Validation**:
- Range: 0.5 L to 15 L (30 to 916 CID)
- Must be positive number

**Default**: 5.0 L (305 CID)

**Example**:
```
Displacement:
  Liters:       [5.0___] L
  Cubic Inches: [305.1_] CID

(Enter either value, the other updates automatically)
```

---

### Question 6: Compression Ratio

**Purpose**: Determine fuel type and performance characteristics

**Input Type**: Number input (format: X.X:1)

**How to Answer**:
1. Enter compression ratio (e.g., 9.5)
2. System displays as "9.5:1"

**Typical Ranges**:
- **Gasoline**: 8:1 to 11:1
- **Diesel**: 15:1 to 22:1

**AI Assistance**:
- Suggests typical range based on engine type
- Warns if value seems incorrect for fuel type

**Validation**:
- Range: 7:1 to 22:1
- Must be positive decimal

**Default**: 9.5:1 (gasoline)

**Example**:
```
Compression Ratio: [9.5___]:1

Typical ranges:
- Gasoline: 8-11:1
- Diesel: 15-22:1
```

---

### Question 7: Stroke Length

**Purpose**: Calculate displacement and RPM characteristics

**Input Type**: Dual number input (mm OR inches)

**How to Answer**:
1. Enter stroke in millimeters or inches
2. Conversion happens automatically

**Conversion**: 1 inch = 25.4 mm

**AI Assistance**:
- Auto-calculated from displacement + cylinders
- Formula: `Stroke = (Displacement / Cylinders) / Bore`

**Validation**:
- Range: 50mm to 200mm (2" to 8")
- Must be positive number

**Default**: 90mm (3.54")

**Example**:
```
Stroke Length:
  Millimeters: [90.0__] mm
  Inches:      [3.54__] in

(Enter either value, the other updates automatically)
```

---

### Question 8: Induction Type

**Purpose**: Determine boost pressure monitoring and fuel requirements

**Input Type**: Radio buttons

**Options**:
- Naturally Aspirated
- Turbocharged
- Supercharged

**How to Answer**:
1. Select appropriate option
2. Most marine engines are naturally aspirated

**AI Assistance**:
- Infers from model name (e.g., "Turbo" in name → Turbocharged)
- Suggests based on displacement and power output

**Validation**:
- Required field

**Default**: Naturally Aspirated

**CX5106 Impact**: Affects boost pressure monitoring configuration

**Example**:
```
Induction Type:
○ Naturally Aspirated
○ Turbocharged
○ Supercharged
```

---

### Question 9: Rated Horsepower

**Purpose**: Establish power output baselines

**Input Type**: Number input with unit toggle (HP or kW)

**How to Answer**:
1. Enter rated horsepower
2. Toggle between HP and kW if needed

**Conversion**: 1 HP = 0.746 kW

**AI Assistance**:
- Suggests manufacturer rating from model database
- Calculates expected HP from displacement

**Validation**:
- Range: 10 HP to 1000 HP (7.5 kW to 746 kW)
- Must be positive number

**Default**: 200 HP (149 kW)

**Example**:
```
Rated Power:
  Horsepower: [220___] HP
  Kilowatts:  [164.1_] kW

(Enter either value, the other updates automatically)
```

---

### Question 10: Idle RPM Specification

**Purpose**: Set idle speed monitoring thresholds

**Input Type**: Number input

**How to Answer**:
1. Enter manufacturer specified idle RPM
2. Check engine manual or service data

**Typical Ranges**:
- **Gasoline**: 600-800 RPM
- **Diesel**: 500-700 RPM

**AI Assistance**:
- Suggests 700 RPM for gasoline
- Suggests 650 RPM for diesel

**Validation**:
- Range: 400 RPM to 1200 RPM
- Must be positive integer

**Default**: 700 RPM

**Example**:
```
Idle RPM Specification: [700___] RPM

Typical ranges:
- Gasoline: 600-800 RPM
- Diesel: 500-700 RPM
```

---

### Question 11: WOT RPM Range

**Purpose**: Set wide-open-throttle monitoring thresholds

**Input Type**: Two number inputs (Min, Max)

**How to Answer**:
1. Enter minimum WOT RPM (lower end of range)
2. Enter maximum WOT RPM (upper end of range)
3. Check propeller manual or engine specifications

**How to Find**:
- Check engine manual "WOT RPM" specification
- Check propeller documentation
- Typical range is ±200-300 RPM

**AI Assistance**:
- Calculates from manufacturer specs if available
- Suggests 4800-5200 RPM as typical range

**Validation**:
- Max must be greater than Min
- Range: 2000 RPM to 7000 RPM
- Typical spread: 200-500 RPM

**Default**: 4800-5200 RPM

**Example**:
```
WOT RPM Range:
  Minimum: [4800__] RPM
  Maximum: [5200__] RPM

Acceptable range at wide-open-throttle.
Check your propeller manual.
```

---

### Question 12: Maximum Coolant Temperature

**Purpose**: Set overheat warning thresholds

**Input Type**: Number input with unit toggle (°F or °C)

**How to Answer**:
1. Enter maximum safe coolant temperature
2. Toggle between Fahrenheit and Celsius

**Conversion**: °F = (°C × 9/5) + 32

**Typical Values**:
- **Freshwater cooling**: 180-190°F (82-88°C)
- **Raw water cooling**: 140-160°F (60-71°C)
- **Closed cooling**: 180-200°F (82-93°C)

**AI Assistance**:
- Suggests 180°F for freshwater systems
- Suggests 160°F for raw water systems

**Validation**:
- Range: 120°F to 220°F (49°C to 104°C)
- Must be positive number

**Default**: 180°F (82°C)

**Example**:
```
Maximum Coolant Temperature:
  Fahrenheit: [180___] °F
  Celsius:    [82.2__] °C

Typical values:
- Freshwater: 180-190°F
- Raw water: 140-160°F
```

---

### Question 13: Minimum Oil Pressure

**Purpose**: Set low oil pressure warning thresholds

**Input Type**: Two number inputs (Idle PSI, Cruise PSI)

**How to Answer**:
1. Enter minimum acceptable oil pressure at idle
2. Enter minimum acceptable oil pressure at cruise (2500+ RPM)
3. Check engine manual for specifications

**Typical Values**:
- **Idle**: 10-15 PSI
- **Cruise**: 40-60 PSI

**AI Assistance**:
- Suggests 10 PSI @ idle
- Suggests 40 PSI @ cruise

**Validation**:
- Cruise must be greater than Idle
- Idle range: 5-20 PSI
- Cruise range: 30-80 PSI

**Default**: 10 PSI idle, 40 PSI cruise

**Example**:
```
Minimum Oil Pressure:
  At Idle:  [10___] PSI
  At Cruise: [40___] PSI

Check your engine manual for specifications.
Cruise = 2500+ RPM
```

---

### Question 14: Tank Sensor Standard (Regional Setting)

**Purpose**: Configure CX5106 for correct tank level sensor readings

**Input Type**: Radio buttons

**How to Answer**:
Select your boat's region or tank sensor type

**Options**:
- North America / United States / Canada (240-33Ω senders)
- Europe / International (0-190Ω senders)
- I don't know (AI will suggest based on boat origin)

**Maps to**: CX5106 Second Row Switch "1"

**Why This Matters**:
- Tank level sensors use different resistance standards by region
- North American boats: 240-33Ω (full tank) to 33Ω (empty)
- European boats: 0-190Ω range
- Wrong setting = inverted or incorrect fuel/water/waste tank readings

**AI Assistance**:
- If engine manufacturer is American (Mercury, Crusader, etc.) → Suggests American
- If engine manufacturer is European (Volvo, Yanmar, etc.) → May suggest European
- If boat registered in US/Canada → Suggests American
- If boat registered in Europe → Suggests European

**Validation**:
- Cross-check with boat documentation
- If tank readings seem inverted after installation, this setting should be toggled

**Default**: North America (240-33Ω) for US/Canadian boats

**Example**:
```
Tank Sensor Standard:
○ North America (240-33Ω) - Most US/Canadian boats
● Europe (0-190Ω) - European boats
○ I don't know - Let AI suggest

Affects: Fuel level, fresh water, waste water readings
```

---

### Question 15: Engine Designation (For Multi-Engine Configuration)

**Purpose**: Identify which physical engine this CX5106 is monitoring

**Input Type**: Radio buttons (conditionally shown)

**Conditional Logic**:
- If single engine (detected from earlier questions) → **Auto-set to "Primary/Port" and skip this question**
- If multiple engines → Show this question

**How to Answer**:
Select which engine this specific CX5106 unit is connected to

**Options**:
- Primary / Single Engine (default)
- Port Engine (left side)
- Starboard Engine (right side)

**Maps to**: CX5106 Second Row Switch "2"

**Why This Matters**:
- Helps identify which CX5106 unit corresponds to which physical engine
- Different from NMEA2000 instance (First Row SW1-2)
- Used for internal organization and troubleshooting

**Auto-populate**:
- If Question 1-2 already determined engine count and position, auto-fill
- Single engine → Automatically set to "Primary/Port" (OFF)
- Twin engines → Ask user to confirm port vs starboard for this unit

**Default**: Primary/Port (for single engine boats)

**Example**:
```
Engine Designation:
● Primary / Single Engine
○ Port Engine (Left)
○ Starboard Engine (Right)

Note: This is for organizing your CX5106 units.
Already set by earlier questions about engine count.
```

---

## CX5106 DIP SWITCH CONFIGURATION

After completing all 15 questions, d3kOS generates **complete** CX5106 DIP switch configuration for **both rows**.

### What is CX5106?

The CX5106 is a NMEA2000 engine gateway that converts analog engine sensors (RPM, temperature, pressure) to NMEA2000 PGNs (digital messages).

### DIP Switch Overview

The CX5106 has **TWO ROWS** of DIP switches:

**FIRST ROW (8 switches)** - Engine Configuration:
- Engine instance (NMEA2000 network identification)
- Cylinder count
- RPM sensor type
- Engine stroke type (2-stroke vs 4-stroke)
- Gear ratio

**SECOND ROW (2 switches)** - Regional & Position Settings:
- Tank sensor resistance standard (American vs European)
- Engine position designation (Port vs Starboard)

### Example Configuration Display

```
┌──────────────────────────────────────────────────────────────┐
│          CX5106 COMPLETE DIP SWITCH CONFIGURATION            │
│         For: Mercury 5.0L MPI Alpha (2018)                   │
│         Region: North America                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   FIRST ROW (Engine Configuration):                         │
│   ┌─┬─┬─┬─┬─┬─┬─┬─┐                                        │
│   │1│2│3│4│5│6│7│8│                                        │
│   ├─┼─┼─┼─┼─┼─┼─┼─┤                                        │
│   │░│░│░│░│░│█│░│░│   █ = ON   ░ = OFF                    │
│   └─┴─┴─┴─┴─┴─┴─┴─┘                                        │
│                                                              │
│   SW1: OFF - Single engine (Instance 0)                     │
│   SW2: OFF                                                   │
│   SW3: OFF - Alternator W-terminal                          │
│   SW4: OFF                                                   │
│   SW5: OFF - 8 cylinders                                    │
│   SW6: ON                                                    │
│   SW7: OFF - 4-stroke engine                                │
│   SW8: OFF - 1:1 direct drive                               │
│                                                              │
│   SECOND ROW (Regional & Position):                         │
│   ┌───┬───┐                                                 │
│   │"1"│"2"│                                                 │
│   ├───┼───┤                                                 │
│   │ █ │ ░ │   █ = ON   ░ = OFF                             │
│   └───┴───┘                                                 │
│                                                              │
│   "1": ON  - American tank senders (240-33Ω)                │
│   "2": OFF - Single/Port engine designation                 │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                WHY THESE SETTINGS?                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ FIRST ROW:                                                   │
│ • SW1-2 OFF/OFF: Single engine (NMEA2000 Instance 0)        │
│ • SW3-4 OFF/OFF: Alternator W-terminal for RPM              │
│ • SW5-6 OFF/ON: 8 cylinder V8 configuration                 │
│ • SW7 OFF: 4-stroke engine                                  │
│ • SW8 OFF: 1:1 gear ratio (direct drive)                    │
│                                                              │
│ SECOND ROW:                                                  │
│ • "1" ON: North American boat with 240-33Ω tank senders     │
│   (Ensures correct fuel, water, waste tank level readings)  │
│ • "2" OFF: Single engine / Port designation                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘

[Print to PDF] [Save Configuration] [Next]
```

### Installation Instructions

1. **Locate DIP Switches**: On side of CX5106 module
2. **Power Off**: Disconnect power before changing switches
3. **Set Switches**: Use small screwdriver or pen
4. **Verify**: Double-check against diagram
5. **Power On**: Reconnect power
6. **Test**: Verify data appears in Signal K

### Common DIP Switch Patterns

**Single 4-Cylinder Outboard** (North American):
```
FIRST ROW:
Switch: 1   2   3   4   5   6   7   8
        OFF OFF OFF OFF OFF OFF OFF OFF

SECOND ROW:
Switch: "1" "2"
        ON  OFF  (American senders, Single engine)
```

**Single 6-Cylinder Sterndrive** (North American):
```
FIRST ROW:
Switch: 1   2   3   4   5   6   7   8
        OFF OFF OFF OFF ON  OFF OFF OFF

SECOND ROW:
Switch: "1" "2"
        ON  OFF  (American senders, Single engine)
```

**Port Engine (Twin 8-Cylinder)** (North American):
```
FIRST ROW:
Switch: 1   2   3   4   5   6   7   8
        ON  OFF OFF OFF OFF ON  OFF OFF  (Instance 1, 8-cyl, 4-stroke)

SECOND ROW:
Switch: "1" "2"
        ON  OFF  (American senders, Port engine)
```

**Starboard Engine (Twin 8-Cylinder)** (North American):
```
FIRST ROW:
Switch: 1   2   3   4   5   6   7   8
        OFF ON  OFF OFF OFF ON  OFF OFF  (Instance 2, 8-cyl, 4-stroke)

SECOND ROW:
Switch: "1" "2"
        ON  ON   (American senders, Starboard engine)
```

---

## QR CODE GENERATION

### Purpose

The QR code uniquely identifies your d3kOS installation and allows:
- Mobile app pairing
- Remote monitoring (Tier 3)
- Configuration backup

### Installation ID Format

```
Format: 16-character hexadecimal
Example: a3f7c91e8d2b4f60
```

Generated from:
- MAC address of Raspberry Pi
- Installation timestamp
- Random salt

### QR Code Content

```
d3kos://pair?id=a3f7c91e8d2b4f60&version=2.0.0&tier=0&boat=MyBoat
```

Parameters:
- `id`: Installation ID
- `version`: d3kOS version
- `tier`: License tier (0, 2, or 3)
- `boat`: Boat name (optional, from Q1 if entered)

### Display

```
┌─────────────────────────────────────────┐
│    INSTALLATION COMPLETE                │
│                                         │
│    ████████████████████████████         │
│    ██ ▄▄▄▄▄ █▀▄▄  █ ▄▄▄▄▄ ██         │
│    ██ █   █ █▀ █▀▀█ █   █ ██         │
│    ██ █▄▄▄█ ██▄▀  █ █▄▄▄█ ██         │
│    ██▄▄▄▄▄▄▄█▀█ ▀ █▄▄▄▄▄▄▄██         │
│    ██▄  ▀▄▀▄▄▀▀▀▄ ▄  █▄▀ ▄██         │
│    ████████████████████████████         │
│                                         │
│    Installation ID:                     │
│    a3f7c91e8d2b4f60                    │
│                                         │
│    Scan with d3kOS mobile app         │
│    to pair your device                  │
│                                         │
│    [Regenerate QR Code]                 │
│    [Go to Main Menu]                    │
│                                         │
└─────────────────────────────────────────┘
```

### When to Regenerate

- If QR code is lost
- If pairing with new mobile device
- If security compromise suspected

### How to Access Later

From main menu:
1. Tap "QR Code" button
2. QR code displays with current installation ID
3. Scan with mobile app

---

## RESET COUNTER

### Purpose

Tracks number of onboarding resets to prevent abuse of free tier.

### Reset Limits

| Tier | Reset Limit | Action After Limit |
|------|-------------|-------------------|
| Tier 0 (Free) | 10 resets | Must download fresh image or upgrade |
| Tier 2+ (Paid) | Unlimited | No limit |

### Counter Display

Appears in footer of every onboarding page:

```
┌─────────────────────────────────────────┐
│                                         │
│  [Onboarding question content here]     │
│                                         │
│  [Back]              [Next]             │
│                                         │
├─────────────────────────────────────────┤
│ Resets used: 7/10 (Tier 0)              │
└─────────────────────────────────────────┘
```

### Warning Messages

**Reset 8**:
```
⚠️ Warning: Only 2 resets remaining.

Consider upgrading to Tier 2 for unlimited resets by installing OpenCPN or another compatible app.

[Continue] [Cancel]
```

**Reset 9**:
```
⚠️ Warning: This is your last reset.

After this reset, you will need to download a fresh d3kOS image or upgrade to Tier 2+ for unlimited resets.

[Continue] [Cancel]
```

**Reset 10**:
```
❌ Maximum resets reached (10/10).

Options:
1. Download fresh d3kOS image from GitHub
2. Upgrade to Tier 2+ by installing OpenCPN

[Download Image] [View Upgrade Options] [Cancel]
```

### How to Reset Onboarding

From main menu:
1. Tap "Onboarding" button
2. Tap "Reset Wizard"
3. Confirm reset (counter increments)
4. Wizard restarts from Question 1

### Counter Storage

Location: `/opt/d3kos/state/onboarding-reset-count.json`

```json
{
  "reset_count": 7,
  "max_resets": 10,
  "last_reset": "2026-02-06T10:30:00Z",
  "warnings_shown": [8, 9],
  "tier": 0
}
```

---

## ONBOARDING BEST PRACTICES

### Before You Start

1. **Have engine documentation ready**:
   - Owner's manual
   - Service manual
   - Propeller specifications
   - Previous service records

2. **Know your engine**:
   - Manufacturer and model
   - Year of manufacture
   - Recent service history

3. **Set aside time**:
   - Allow 15-20 minutes uninterrupted
   - Don't rush through questions
   - Accuracy is critical for monitoring

### During Onboarding

1. **Double-check entries**:
   - Use [Back] button to review
   - Verify units (PSI vs kPa, °F vs °C)
   - Confirm decimal places

2. **Use AI assistance**:
   - Let system suggest values
   - Verify suggestions against manual
   - Override if needed

3. **Save progress**:
   - Tap "Save & Exit" if interrupted
   - Progress auto-saves every 30 seconds
   - Resume later from main menu

### After Onboarding

1. **Print DIP switch configuration**:
   - Keep for reference
   - Take photo with phone
   - Store in engine documentation

2. **Configure CX5106**:
   - Set DIP switches as shown
   - Verify NMEA2000 data flows
   - Check Signal K for engine data

3. **Run engine baseline**:
   - Essential for anomaly detection
   - Should be done within first week
   - Takes 30 minutes of engine runtime

4. **Save QR code**:
   - Screenshot for backup
   - Scan with mobile app
   - Keep installation ID safe

---

## TROUBLESHOOTING ONBOARDING

### Issue: Can't Find Engine Model

**Problem**: Your engine model is not in the dropdown list

**Solution**:
1. Type model number manually
2. Use closest similar model
3. Continue with manual entry
4. AI assistance will still work

### Issue: Not Sure About Specification

**Problem**: Don't know compression ratio, stroke length, etc.

**Solutions**:
1. Check engine owner's manual
2. Search online: "[Manufacturer] [Model] specifications"
3. Use AI suggested value (usually accurate)
4. Contact manufacturer support

### Issue: Made Mistake on Previous Question

**Problem**: Realized error after clicking Next

**Solutions**:
1. Use [Back] button to return
2. Correct the answer
3. Click [Next] to continue
4. All data is saved automatically

### Issue: Want to Start Over

**Problem**: Made multiple errors, want fresh start

**Solutions**:
1. Click "Save & Exit"
2. Return to main menu
3. Tap "Onboarding" → "Reset Wizard"
4. Confirm reset (uses one reset from counter)

### Issue: DIP Switch Configuration Doesn't Match

**Problem**: Generated DIP switches don't match CX5106 documentation

**Solutions**:
1. Verify all onboarding answers are correct
2. Check CX5106 model number (different models vary)
3. Follow d3kOS configuration (optimized for your engine)
4. Contact support if data still incorrect

### Issue: Hit Reset Limit (Tier 0)

**Problem**: Used all 10 resets, can't reset again

**Solutions**:
1. **Option 1**: Upgrade to Tier 2
   - Install OpenCPN (free, unlocks Tier 2)
   - From main menu: "OpenCPN Management" → "Install"
   - Get unlimited resets

2. **Option 2**: Fresh image
   - Download new d3kOS image from GitHub
   - Flash to SD card
   - Lose current configuration
   - Get fresh 10 resets

### Issue: Onboarding Won't Complete

**Problem**: Stuck on "Saving configuration..." screen

**Solutions**:
1. Wait 30 seconds (slow SD card)
2. Check disk space: Must have >2GB free
3. Check logs: `sudo journalctl -u d3kos-onboarding`
4. Restart service: `sudo systemctl restart d3kos-onboarding`

### Issue: QR Code Won't Generate

**Problem**: Blank QR code or error message

**Solutions**:
1. Check network interface: `ifconfig`
2. Verify installation ID exists: `cat /opt/d3kos/config/license.json`
3. Regenerate from main menu: "QR Code" button
4. Check logs: `/opt/d3kos/logs/onboarding.log`

---

## NEXT STEPS AFTER ONBOARDING

1. **Configure CX5106 DIP switches** using generated configuration
2. **Verify NMEA2000 data** flowing in Signal K
3. **Run engine baseline** for 30 minutes (see MASTER_SYSTEM_SPEC.md section 6.1)
4. **Test dashboard gauges** to ensure all metrics display
5. **Install OpenCPN** (optional, unlocks Tier 2 features)

For detailed operational instructions, see:
- [INSTALLATION.md](INSTALLATION.md) - Complete setup guide
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

---

**Onboarding Complete!** Your d3kOS is configured and ready to monitor your engine.
