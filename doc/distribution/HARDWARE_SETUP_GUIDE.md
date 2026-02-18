# d3kOS Hardware Setup Guide

**Version**: 1.0.3
**Last Updated**: February 18, 2026

---

## 📋 Table of Contents

1. [Bill of Materials](#bill-of-materials)
2. [PiCAN-M HAT Installation](#pican-m-hat-installation)
3. [NMEA2000 Wiring](#nmea2000-wiring)
4. [CX5106 Engine Gateway Setup](#cx5106-engine-gateway-setup)
5. [Power Supply](#power-supply)
6. [Touchscreen Assembly](#touchscreen-assembly)
7. [GPS & AIS Receivers](#gps--ais-receivers)
8. [Camera Installation](#camera-installation)
9. [Enclosure & Mounting](#enclosure--mounting)
10. [Wiring Diagrams](#wiring-diagrams)

---

## 1. Bill of Materials

### Core Components

| Item | Part Number | Qty | Est. Cost (USD) | Supplier | Notes |
|------|-------------|-----|-----------------|----------|-------|
| **Raspberry Pi 4 Model B (4GB)** | RPI4-MODBP-4GB | 1 | $55 | raspberrypi.com | 8GB model also supported |
| **PiCAN-M HAT** | PICAN-M | 1 | $60 | skpang.co.uk | NMEA2000 interface |
| **10.1" Touchscreen (1920×1200)** | Generic | 1 | $120 | Amazon/AliExpress | IPS panel recommended |
| **MicroSD Card (128GB Class 10 A2)** | SanDisk Extreme | 1 | $18 | Amazon | 32GB minimum |
| **USB GPS Receiver** | VK-162 | 1 | $15 | Amazon | USB-A, compatible with gpsd |
| **Anker PowerConf S330** | A3302 | 1 | $130 | Amazon | USB speaker + mic (Tier 2+) |
| **12V to 5V DC Converter** | Victron Orion-Tr 12/12-9 | 1 | $35 | victronenergy.com | 3A minimum output |
| **CX5106 Engine Gateway** | CX5106 | 1 | $250 | actisense.com | Analog to NMEA2000 |
| **DB9 Male Connector** | Molex 43025-0900 | 1 | $3 | mouser.com | NMEA2000 backbone connection |
| **NMEA2000 Backbone Cable (2m)** | Generic | 1 | $15 | Amazon | T-connector included |
| **Heat Sinks for Pi** | Generic Aluminum | 3 | $5 | Amazon | Thermal adhesive included |
| **USB-C Power Cable (Angled)** | Generic | 1 | $8 | Amazon | Right-angle for space savings |
| **HDMI to Micro-HDMI Cable (1m)** | Generic | 1 | $7 | Amazon | For touchscreen connection |
| | | | | | |
| **TOTAL** | | | **$721** | | |

### Optional Components

| Item | Part Number | Qty | Est. Cost (USD) | Supplier | Notes |
|------|-------------|-----|-----------------|----------|-------|
| **Reolink RLC-810A Camera** | RLC-810A | 1 | $110 | reolink.com | 4K/1080p, IP67, night vision (Tier 2+) |
| **USB AIS Receiver** | dAISy | 1 | $80 | tindie.com | Vessel tracking |
| **360° Motorized Searchlight** | Golight Stryker | 1 | $350 | golight.com | Camera mounting platform |
| **Waterproof Enclosure** | Bud Industries NBF-32244 | 1 | $45 | mouser.com | NEMA 4X rated |
| **3D-Printed Enclosure** | Custom STL | 1 | $20 | Local 3D print | Files available on GitHub |
| **USB Extension Cable (3m)** | Generic | 2 | $10 | Amazon | For GPS/AIS relocation |
| **Cable Glands (PG9)** | Generic | 5 | $8 | Amazon | Waterproof cable entry |
| **Desiccant Packs** | Generic Silica Gel | 3 | $5 | Amazon | Moisture control |
| | | | | | |
| **OPTIONAL TOTAL** | | | **$628** | | |

### Tools Required

- Small Phillips screwdriver
- Wire strippers (14-22 AWG)
- Crimping tool (NMEA2000 connectors)
- Multimeter (voltage and continuity testing)
- Soldering iron (for DB9 connector)
- Heat gun or lighter (heat-shrink tubing)
- Drill with step bits (enclosure mounting)
- Marine adhesive or 3M VHB tape (mounting)

---

## 2. PiCAN-M HAT Installation

### Step 2.1: Inspect GPIO Pins

**Before Installation**:
1. Power off Raspberry Pi
2. Inspect 40-pin GPIO header on Raspberry Pi
3. Ensure no bent or missing pins
4. Inspect PiCAN-M GPIO socket (female connector)
5. Ensure all 40 holes are clear

### Step 2.2: Align HAT

1. Hold PiCAN-M HAT above Raspberry Pi
2. Orient DB9 connector (NMEA2000) toward edge of Pi
3. Align GPIO pins with PiCAN-M socket
4. Ensure all 40 pins will insert into socket

**Alignment Check**:
```
PiCAN-M HAT (top view)
┌─────────────────────────────┐
│  [DB9 NMEA2000]             │
│                             │
│   ○ GPIO Pin 1 (3.3V)       │
│   ○ ○ ○ ○ ○ ○ ... (40 pins)│
│                             │
└─────────────────────────────┘

Raspberry Pi 4 (top view)
┌─────────────────────────────┐
│  [Ethernet] [USB x4]        │
│                             │
│   ○ GPIO Pin 1 (3.3V)       │
│   ○ ○ ○ ○ ○ ○ ... (40 pins)│
│  [HDMI0] [HDMI1] [USB-C]    │
└─────────────────────────────┘
```

### Step 2.3: Install HAT

1. **Press down evenly** on both sides of HAT
2. **Apply firm pressure** until HAT seats completely
3. **Check alignment** - HAT should be parallel to Pi board
4. **Verify** - No GPIO pins visible above HAT socket

**Common Mistake**: Offset by 1-2 pins - HAT won't seat properly. Double-check alignment!

### Step 2.4: Verify Installation

**Visual Check**:
- ✅ HAT sits flush on Pi (no gap)
- ✅ DB9 connector accessible
- ✅ Screw holes aligned (if using standoffs)
- ✅ No bent GPIO pins

**Electrical Check** (Advanced):
- Use multimeter to verify 3.3V on GPIO Pin 1 (after power on)
- Use multimeter to verify 5V on GPIO Pin 2

---

## 3. NMEA2000 Wiring

### Step 3.1: NMEA2000 Backbone Overview

**Standard NMEA2000 Network**:
```
 [12V Power] ──┬── T-Connector ── T-Connector ── T-Connector ── [120Ω Terminator]
               │         │               │               │
               │    [Chartplotter]   [CX5106]        [Pi + PiCAN-M]
               │
         [120Ω Terminator]
```

**Requirements**:
- **Power**: 9-16V DC from boat battery (NMEA2000 red wire)
- **Ground**: Boat ground (NMEA2000 black wire)
- **Termination**: 120Ω resistors at both ends of backbone
- **Cable**: NMEA2000 certified cable (twisted pair CAN-H/CAN-L)

### Step 3.2: DB9 Pin Assignment (PiCAN-M to NMEA2000)

**NMEA2000 Micro-C to DB9 Adapter**:

| DB9 Pin | NMEA2000 Wire | Signal | Function |
|---------|---------------|--------|----------|
| **1** | Shield | Shield | Ground/Shield |
| **2** | Red | NET-S | 12V Power (not used by PiCAN-M) |
| **3** | Black | NET-C | Ground |
| **4** | White | CAN-H | CAN High |
| **5** | Blue | CAN-L | CAN Low |
| **6** | - | - | Not connected |
| **7** | - | - | Not connected |
| **8** | - | - | Not connected |
| **9** | - | - | Not connected |

**PiCAN-M DB9 Socket Pinout** (Same as above):
- Pin 1: Shield
- Pin 3: Ground
- Pin 4: CAN-H (white wire)
- Pin 5: CAN-L (blue wire)

**Note**: PiCAN-M is powered by Raspberry Pi (5V via GPIO), not NMEA2000 backbone (12V).

### Step 3.3: NMEA2000 T-Connector Installation

**Adding PiCAN-M to Existing Backbone**:
1. Locate NMEA2000 backbone near helm
2. Disconnect one existing T-connector
3. Insert new T-connector into gap
4. Connect PiCAN-M DB9 cable to T-connector drop cable
5. Verify backbone continuity (both terminators installed)

**Wiring Check**:
```bash
# After power on, verify CAN interface
ifconfig can0

# Should show:
can0: flags=193<UP,RUNNING,NOARP>  mtu 16
```

### Step 3.4: Termination Resistors

**CRITICAL**: NMEA2000 backbone must have exactly **2 terminators** (120Ω each):
- One at beginning of backbone
- One at end of backbone

**Testing Termination** (Multimeter):
1. Disconnect backbone from power
2. Measure resistance between CAN-H and CAN-L at any T-connector
3. Expected: 60Ω (two 120Ω resistors in parallel)

**If Resistance Wrong**:
- Too high (>60Ω): Missing terminator
- Too low (<60Ω): Too many terminators
- Open circuit (OL): Broken wire or no terminators

---

## 4. CX5106 Engine Gateway Setup

### Step 4.1: CX5106 Overview

**Purpose**: Converts analog engine sensors (oil pressure, temperature, tachometer) to NMEA2000 PGN messages.

**Inputs** (Analog Sensors):
1. **Tachometer** - Engine RPM signal (W terminal on alternator or negative coil)
2. **Oil Pressure** - 0-80 PSI sender (variable resistance)
3. **Coolant Temperature** - 100-250°F sender (variable resistance)
4. **Fuel Level** - 0-100% sender (variable resistance, optional)

**Output**: NMEA2000 PGN messages (127488, 127489, 127505, 127508) to backbone

### Step 4.2: Sensor Wiring

**CX5106 Wire Colors and Connections**:

| CX5106 Wire | Sensor Connection | Notes |
|-------------|-------------------|-------|
| **Black** | Engine ground | Connect to engine block or battery negative |
| **Red** | +12V Boat power | Fused 5A, same as NMEA2000 backbone power |
| **Yellow** | Tachometer signal | Alternator W terminal or coil negative |
| **Blue** | Oil pressure sender | Single wire sender (ground through sender) |
| **Green** | Coolant temp sender | Single wire sender (ground through sender) |
| **Brown** | Fuel level sender (optional) | Single wire sender (ground through sender) |
| **White** | Ignition switch | +12V when ignition on (CX5106 auto-power) |

**Sensor Specifications**:
- **Oil Pressure Sender**: 10-180Ω (0-80 PSI) - SAE standard
- **Temperature Sender**: 1000-50Ω (100-250°F) - SAE standard
- **Tachometer Signal**: 0-12V AC/DC pulses (cylinders/2 pulses per revolution)

### Step 4.3: DIP Switch Configuration

**CX5106 has 8 DIP switches** - configured based on Initial Setup wizard (Step 18).

**Example Configuration** (from wizard):
```
Switch 1 [ON ] - Engine Type: Gasoline (Fuel Injection)
Switch 2 [OFF] - Number of Cylinders: 8
Switch 3 [OFF] - Oil Pressure Sender Type: SAE Standard
Switch 4 [ON ] - Idle RPM: 650
Switch 5 [ON ] - Max RPM: 4800
Switch 6 [OFF] - Compression Ratio: 9.4:1
Switch 7 [OFF] - Reserved
Switch 8 [OFF] - Reserved
```

**Visual Diagram**:
```
[█][░][░][█][█][░][░][░]
 1  2  3  4  5  6  7  8

█ = ON (up position)
░ = OFF (down position)
```

**See**: CX5106_CONFIGURATION_GUIDE.md for full DIP switch reference

### Step 4.4: Mounting CX5106

1. Mount CX5106 near engine (within 2m of sensors)
2. Keep away from exhaust manifold (heat)
3. Secure with marine-grade zip ties or screws
4. Orient with wire connectors facing downward (water drainage)
5. Label wires for future maintenance

### Step 4.5: Testing CX5106

**Before Engine Start**:
1. Verify 12V power on CX5106 red wire
2. Check ground continuity (black wire to engine block)
3. Verify NMEA2000 connection (T-connector)

**After Engine Start**:
1. Navigate to d3kOS Dashboard
2. Verify RPM displays (should match dash tachometer)
3. Verify oil pressure displays (30-60 PSI at idle)
4. Verify temperature displays (160-200°F when warmed up)

**Troubleshooting**: See TROUBLESHOOTING_GUIDE.md Section 3

---

## 5. Power Supply

### Step 5.1: Victron Orion-Tr DC-DC Converter

**Model**: Orion-Tr 12/12-9 (12V input, 12V/5V USB output, 9A max)

**Specifications**:
- **Input**: 9-18V DC (boat battery)
- **Output 1**: 12V @ 9A (not used by d3kOS)
- **Output 2**: USB-A 5V @ 3A (Raspberry Pi power)
- **Efficiency**: 95%
- **Isolation**: Non-isolated
- **Protection**: Over-current, over-temperature, reverse polarity

**Wiring**:
```
Boat Battery (+12V) ──┬── [5A Fuse] ── Orion-Tr Input (+)
                      │
Boat Battery (Ground) ── Orion-Tr Input (-)

Orion-Tr USB Output ── USB-C Cable ── Raspberry Pi
```

### Step 5.2: Alternative Power Supply (DIY)

**If Victron not available**, use generic 12V to 5V buck converter:

**Requirements**:
- **Input**: 9-16V DC
- **Output**: 5V @ 3A minimum (5A recommended)
- **Regulation**: <±5% ripple
- **Protection**: Over-current, short circuit

**Recommended Models**:
- Pololu D24V25F5 (2.5A)
- DROK LM2596 (3A adjustable)
- Mean Well SD-15B-5 (3A industrial)

**Wiring Example** (DROK LM2596):
```
IN+ ── [5A Fuse] ── Boat +12V
IN- ── Boat Ground

OUT+ ── USB-C Breakout Board (+5V)
OUT- ── USB-C Breakout Board (GND)
```

**Voltage Adjustment** (DROK LM2596):
1. Connect input power (no load)
2. Measure output voltage with multimeter
3. Adjust potentiometer to 5.0-5.2V DC
4. Connect Raspberry Pi and verify voltage under load

### Step 5.3: Fusing and Protection

**CRITICAL**: Always use inline fuse on 12V power line.

**Fuse Specifications**:
- **Rating**: 5A blade fuse
- **Type**: ATO/ATC standard automotive fuse
- **Location**: Within 18" of battery connection
- **Holder**: Waterproof inline fuse holder

**Protection Checklist**:
- ✅ 5A fuse on 12V+ line
- ✅ Reverse polarity protection (diode or DC converter built-in)
- ✅ Over-current protection (DC converter built-in)
- ✅ Surge protection (optional TVS diode)

### Step 5.4: Power Consumption

**d3kOS Power Draw** (5V measured):

| Mode | Current (A) | Power (W) | Notes |
|------|-------------|-----------|-------|
| **Idle** (no services) | 0.8A | 4W | Pi only, minimal load |
| **Normal** (dashboard) | 1.2A | 6W | Signal K, Node-RED, web |
| **Active** (camera + AI) | 2.5A | 12.5W | Camera stream, AI processing |
| **Peak** (boot + camera record) | 3.5A | 17.5W | First 30 seconds of boot |

**12V Power Draw** (boat battery, 95% converter efficiency):
- Idle: ~0.4A @ 12V (~5W)
- Normal: ~0.6A @ 12V (~7W)
- Active: ~1.3A @ 12V (~16W)
- Peak: ~1.8A @ 12V (~22W)

**Daily Power Consumption** (24 hours):
- Idle: 5W × 24h = 120 Wh (10 Ah @ 12V)
- Normal: 7W × 24h = 168 Wh (14 Ah @ 12V)

**Battery Sizing**:
- **100 Ah battery**: ~7 days runtime (normal load)
- **200 Ah battery**: ~14 days runtime (normal load)
- Recommend dedicated "house" battery for electronics

---

## 6. Touchscreen Assembly

### Step 6.1: Touchscreen Selection

**Recommended Specifications**:
- **Size**: 10.1" diagonal
- **Resolution**: 1920×1200 (WUXGA) or 1280×800 (WXGA)
- **Panel Type**: IPS (wide viewing angle)
- **Interface**: HDMI + USB (2 cable connection)
- **Brightness**: 300-400 cd/m² (readable in sunlight)
- **Power**: 12V DC input (avoid USB-powered - insufficient current)

**Suppliers**:
- Amazon: Search "10.1 inch HDMI touchscreen 1920x1200"
- AliExpress: Generic IPS touchscreen monitors
- Waveshare: 10.1" HDMI LCD (1024×600, lower resolution)

### Step 6.2: HDMI Connection

**Raspberry Pi 4 has 2 micro-HDMI ports**:
- **HDMI0** (primary) - Use this for touchscreen
- **HDMI1** (secondary) - For external monitor (optional)

**Cable**:
- Micro-HDMI (male) to HDMI (male) - 1m length
- Or micro-HDMI to HDMI adapter + standard HDMI cable

**Connection**:
1. Plug micro-HDMI into **HDMI0** port on Pi (closest to USB-C power)
2. Plug HDMI into touchscreen HDMI input
3. Power on touchscreen
4. Display should show d3kOS after boot (~60 seconds)

### Step 6.3: USB Touch Connection

**Cable**: USB-A to USB-B (included with most touchscreens)

**Connection**:
1. Plug USB-A into Raspberry Pi **USB 3.0 port** (blue)
2. Plug USB-B into touchscreen USB port (labeled "Touch" or "USB")
3. Touch should work immediately (no drivers needed on Linux)

**Verification**:
```bash
# Check touch device detected
lsusb | grep -i ilitek

# Expected output:
Bus 001 Device 003: ID 222a:0001 ILITEK ILITEK-TP
```

### Step 6.4: Brightness and Orientation

**Brightness Adjustment**:
- Use touchscreen physical buttons (usually on back or side)
- Increase brightness for outdoor use (sunlight)
- Decrease brightness for night use (battery savings)

**Orientation** (if needed):
- d3kOS defaults to landscape (1920×1200 horizontal)
- If touchscreen mounts vertically, rotate via SSH:
  ```bash
  # Rotate display 90° clockwise
  echo "display_rotate=1" | sudo tee -a /boot/firmware/config.txt
  sudo reboot
  ```

---

## 7. GPS & AIS Receivers

### Step 7.1: USB GPS Receiver (VK-162)

**Specifications**:
- **Chipset**: u-blox 7th generation
- **Interface**: USB-A (plug and play)
- **Channels**: 56 channels
- **Sensitivity**: -161 dBm
- **Update Rate**: 1-10 Hz (default 1 Hz)
- **Accuracy**: 2.5m CEP (outdoor)

**Installation**:
1. Plug VK-162 USB into Raspberry Pi
2. Position GPS antenna near window or outside
3. Allow 2-5 minutes for initial GPS fix (cold start)

**LED Indicator**:
- **Blinking red** - Searching for satellites
- **Solid red** - GPS fix acquired (3+ satellites)

**Testing**:
```bash
# Check GPS device detected
ls /dev/ttyACM*
# Expected: /dev/ttyACM0

# Monitor GPS data
cat /dev/ttyACM0
# Should show NMEA sentences ($GPGGA, $GPRMC, etc.)
```

**Antenna Positioning**:
- **Best**: Roof-mounted external antenna (clear sky view)
- **Good**: Near window on boat deck
- **Poor**: Inside cabin (may not acquire fix)

### Step 7.2: USB AIS Receiver (Optional)

**Model**: dAISy (USB AIS receiver)

**Specifications**:
- **Interface**: USB-A (FTDI serial)
- **Channels**: 2 (AIS A + AIS B)
- **Frequency**: 161.975 MHz, 162.025 MHz
- **Antenna**: External VHF antenna (SO-239 connector)

**Installation**:
1. Connect dAISy USB to Raspberry Pi
2. Connect dAISy RF input to VHF antenna (via splitter if sharing)
3. Configure Signal K for AIS source (auto-detected as /dev/ttyUSB0)

**See**: Signal K documentation for AIS configuration

---

## 8. Camera Installation (Tier 2+)

### Step 8.1: Reolink RLC-810A Specifications

**Camera Specs**:
- **Resolution**: 4K (3840×2160) @ 25fps or 1080p @ 30fps
- **Sensor**: 1/2.5" CMOS
- **Lens**: 4mm (107° horizontal FOV)
- **Night Vision**: IR LEDs, 30m range
- **IP Rating**: IP67 (marine waterproof)
- **Power**: PoE (802.3af) or 12V DC @ 1A
- **RTSP**: Yes (h264Preview_01_main, h264Preview_01_sub)

### Step 8.2: Camera Mounting

**Option 1: 360° Motorized Searchlight** (Golight Stryker)
- Mount camera on searchlight platform
- Use searchlight rotation for pan/tilt
- Control searchlight via separate remote (not integrated with d3kOS)

**Option 2: Fixed Marine Mount**
- Standard marine camera mount
- Stainless steel hardware (corrosion resistance)
- Vibration dampening rubber washers

**Option 3: T-top or Hardtop Mount**
- Mount to boat structure (T-top, hardtop, arch)
- Downward angle for deck monitoring (fish capture)
- Forward angle for navigation (forward watch)

### Step 8.3: Camera Network Configuration

**Static IP Assignment** (DHCP reservation):
1. Connect camera to d3kOS network (10.42.0.0/24)
2. Find camera IP via Reolink app or network scanner
3. Configure DHCP reservation on Pi:
   ```bash
   # Add to /etc/NetworkManager/dnsmasq-shared.d/camera-reservation.conf
   dhcp-host=ec:71:db:f9:7c:7c,10.42.0.100,infinite
   ```
4. Restart NetworkManager:
   ```bash
   sudo systemctl restart NetworkManager
   ```

**Camera IP**: 10.42.0.100
**RTSP URL** (sub-stream): rtsp://admin:password@10.42.0.100:554/h264Preview_01_sub

### Step 8.4: Camera Power

**Option 1: PoE (Power over Ethernet)**
- Use PoE injector or PoE switch
- Single cable for power + data
- Recommended for permanent installation

**Option 2: 12V DC Power**
- Use boat 12V power (same as NMEA2000)
- Fused 2A on 12V+ line
- Separate Ethernet cable for data

---

## 9. Enclosure & Mounting

### Step 9.1: Waterproof Enclosure

**Commercial Enclosure** (Bud Industries NBF-32244):
- **Material**: Polycarbonate (UV resistant)
- **Size**: 11.8" × 7.9" × 5.9"
- **Rating**: NEMA 4X (waterproof, corrosion resistant)
- **Mounting**: Flange holes (4 corner screws)
- **Cable Entry**: 5× PG9 cable glands

**3D-Printed Enclosure** (Custom):
- **Material**: PETG or ASA filament (UV resistant, waterproof)
- **Design**: Available on GitHub (STL files)
- **Printing**: 0.3mm layer height, 30% infill
- **Waterproofing**: Seal with silicone sealant after assembly

### Step 9.2: Mounting Location

**Helm Station Requirements**:
- ✅ Within arm's reach of operator
- ✅ Eye-level or slightly below (touchscreen visibility)
- ✅ Protected from direct rain/spray
- ✅ Away from compass (Pi has magnets)
- ✅ Ventilated (heat dissipation)

**Mounting Options**:
1. **Dashboard Panel** - Flush mount cutout
2. **Swing Arm** - Adjustable positioning
3. **Pedestal** - Free-standing on console
4. **Overhead** - T-top or hardtop underside

### Step 9.3: Cable Management

**Cable Entry**:
- Use PG9 cable glands for waterproof entry
- Route cables downward (water drainage)
- Seal around glands with silicone

**Internal Routing**:
- Use cable ties to organize wiring
- Label cables for future maintenance
- Leave service loops (12" extra length)

**External Routing**:
- Use split loom tubing for protection
- Secure to boat structure every 12" (zip ties)
- Protect from chafing (rubber grommets at holes)

---

## 10. Wiring Diagrams

### Diagram 1: Complete System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       d3kOS System Wiring                       │
└─────────────────────────────────────────────────────────────────┘

Boat 12V Battery
     │
     ├─── [5A Fuse] ─── Victron Orion-Tr 12/12-9 ─── USB-C ─── Raspberry Pi 4
     │                                                              │
     │                                                              ├─── HDMI ─── Touchscreen
     │                                                              │
     │                                                              ├─── USB ─── Touchscreen (Touch)
     │                                                              │
     │                                                              ├─── USB ─── GPS (VK-162)
     │                                                              │
     │                                                              ├─── USB ─── Speaker (Anker S330)
     │                                                              │
     │                                                              └─── GPIO ─── PiCAN-M HAT
     │                                                                              │
     ├─── NMEA2000 Backbone (12V) ──┬── T-Conn ── CX5106              DB9 ────────┘
     │                               │               │
     │                               │               ├─── Yellow ─── Tachometer Signal
     │                               │               ├─── Blue ───── Oil Pressure Sender
     │                               │               ├─── Green ──── Temp Sender
     │                               │               └─── Black ──── Engine Ground
     │                               │
     │                               ├── T-Conn ── Chartplotter (optional)
     │                               │
     │                               └── [120Ω Term] ──────────── [120Ω Term]
     │
     └─── Camera Power (12V @ 1A) ─── Reolink RLC-810A
                                           │
                                           └─── Ethernet ─── Raspberry Pi eth0
```

### Diagram 2: NMEA2000 Backbone Detail

```
[120Ω Terminator] ─── Backbone ─┬─ T-Connector ─┬─ Drop Cable (2m) ─── CX5106
                                 │                └─ Backbone
                                 │
                                 ├─ T-Connector ─┬─ Drop Cable (2m) ─── PiCAN-M (Pi)
                                 │                └─ Backbone
                                 │
                                 ├─ T-Connector ─┬─ Drop Cable (2m) ─── Chartplotter
                                 │                └─ Backbone
                                 │
                                 └─ Backbone ──── [120Ω Terminator]

Backbone Power: Red wire (+12V), Black wire (Ground)
Data Wires: White (CAN-H), Blue (CAN-L), Shield
```

### Diagram 3: CX5106 Sensor Wiring

```
CX5106 Engine Gateway
┌─────────────────────┐
│  [DIP Switches]     │
│  [█][░][░][█][█]... │
│                     │
│  Wire Terminals:    │
│  ┌──────────────┐   │
│  │ Black        │───┼─── Engine Ground (block or battery -)
│  │ Red          │───┼─── +12V Boat Power (fused 5A)
│  │ White        │───┼─── Ignition +12V (optional auto-power)
│  │ Yellow       │───┼─── Tachometer Signal (alternator W terminal)
│  │ Blue         │───┼─── Oil Pressure Sender (single wire)
│  │ Green        │───┼─── Coolant Temp Sender (single wire)
│  │ Brown        │───┼─── Fuel Level Sender (optional)
│  └──────────────┘   │
│                     │
│  [NMEA2000 Out] ────┼─── T-Connector (backbone)
└─────────────────────┘

Sender Notes:
- Oil pressure sender: 10-180Ω (0-80 PSI), grounded through sender body
- Temp sender: 1000-50Ω (100-250°F), grounded through sender body
- Tachometer: 0-12V pulses, (cylinders/2) pulses per revolution
```

### Diagram 4: Power Supply Detail

```
Victron Orion-Tr 12/12-9
┌─────────────────────┐
│  Input:             │
│  ┌──────────────┐   │
│  │ IN+          │───┼─── [5A Fuse] ─── Boat +12V Battery
│  │ IN-          │───┼─── Boat Ground
│  └──────────────┘   │
│                     │
│  Output:            │
│  ┌──────────────┐   │
│  │ USB-A (5V 3A)│───┼─── USB-C Cable ─── Raspberry Pi USB-C Power
│  │ 12V @ 9A     │   │    (not used)
│  └──────────────┘   │
│                     │
│  Status LED: Green  │
└─────────────────────┘

Voltage Verification:
- Measure IN+/IN- with multimeter: 12-14V DC (engine running)
- Measure USB-A output: 5.0-5.2V DC (no load)
- Measure USB-A output: 4.8-5.2V DC (Raspberry Pi connected, idle)
```

---

## ✅ Assembly Checklist

**Before First Power-On**:
- [ ] PiCAN-M HAT seated properly (all 40 GPIO pins)
- [ ] Heat sinks installed on Raspberry Pi
- [ ] SD card inserted and locked
- [ ] HDMI cable connected (HDMI0 port)
- [ ] USB touch cable connected (blue USB 3.0 port)
- [ ] GPS receiver plugged in (USB)
- [ ] Speaker plugged in (USB, Tier 2+)
- [ ] NMEA2000 DB9 cable connected to PiCAN-M
- [ ] NMEA2000 backbone powered (9-16V DC)
- [ ] NMEA2000 terminators installed (both ends)
- [ ] CX5106 sensors wired (tach, oil, temp)
- [ ] CX5106 DIP switches configured (per wizard)
- [ ] DC converter output verified (5.0-5.2V)
- [ ] Fuse installed on 12V+ line (5A)
- [ ] All connections tight (no loose wires)
- [ ] Enclosure sealed (cable glands installed)

**After Power-On**:
- [ ] Red LED on Raspberry Pi (power)
- [ ] Green LED flashing (booting)
- [ ] Touchscreen shows d3kOS splash (60-90 seconds)
- [ ] WiFi AP visible (SSID: d3kOS)
- [ ] Web interface loads (http://d3kos.local)
- [ ] Initial Setup wizard appears
- [ ] Complete wizard (20 steps)
- [ ] Dashboard shows engine data (after engine start)

---

**Document Version**: 1.0.3
**Last Updated**: February 18, 2026
**Maintainer**: SkipperDon (https://atmyboat.com)
