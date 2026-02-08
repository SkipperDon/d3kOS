# HELM-OS HARDWARE SPECIFICATION

**Version**: 2.0
**Date**: February 6, 2026
**Based on**: MASTER_SYSTEM_SPEC.md v2.0

---

## TABLE OF CONTENTS

1. [Hardware Overview](#hardware-overview)
2. [Core Components](#core-components)
3. [Optional Hardware](#optional-hardware)
4. [Hardware Interfaces](#hardware-interfaces)
5. [Environmental Specifications](#environmental-specifications)
6. [Power Requirements](#power-requirements)
7. [Physical Mounting](#physical-mounting)
8. [Bill of Materials](#bill-of-materials)
9. [Assembly Guide](#assembly-guide)
10. [Hardware Troubleshooting](#hardware-troubleshooting)

---

## 1. HARDWARE OVERVIEW

d3kOS is built on the Raspberry Pi 4 platform, designed to provide a complete marine electronics solution with engine monitoring, navigation, and voice control capabilities.

### 1.1 System Block Diagram

```
                    ┌─────────────────────┐
                    │   Raspberry Pi 4    │
                    │   Model B (4/8GB)   │
                    │   Quad-core ARM     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼────────┐ ┌────▼────┐  ┌───────▼────────┐
     │   PiCAN-M HAT   │ │ USB Hub │  │  10.1" Touch   │
     │   (NMEA2000)    │ │         │  │  1920×1200     │
     │   Micro-fit     │ │  4-Port │  │  1000 nit      │
     └────────┬────────┘ └────┬────┘  └────────────────┘
              │               │
              │     ┌─────────┼──────────────┐
              │     │         │              │
         ┌────▼────┐│  ┌──────▼──┐  ┌───────▼────────┐
         │ N2K Bus ││  │ GPS USB │  │   AIS USB      │
         │ (CAN0)  ││  │ VK-162  │  │   dAISy        │
         │ 250kbps ││  │         │  │                │
         └─────────┘│  └─────────┘  └────────────────┘
                    │
              ┌─────▼──────┐
              │ Anker S330 │
              │Speakerphone│
              │ USB Audio  │
              └────────────┘
                    │
              ┌─────▼──────┐
              │  Reolink   │
              │ RLC-810A   │
              │ IP Camera  │
              │ (Optional) │
              └────────────┘
```

### 1.2 Key Features

- **Processing**: Raspberry Pi 4 (ARM Cortex-A72, 1.5GHz quad-core)
- **Memory**: 4GB (minimum) or 8GB (recommended)
- **Storage**: 64GB microSD (minimum), 128GB recommended
- **Display**: 10.1" capacitive touchscreen (1920×1200, 1000 nit)
- **Marine Interface**: PiCAN-M HAT with micro-fit NMEA2000 connector
- **Connectivity**: USB GPS, USB AIS, WiFi, Ethernet
- **Voice**: USB speakerphone with echo cancellation
- **Camera**: IP camera support via RTSP

---

## 2. CORE COMPONENTS

### 2.1 Raspberry Pi 4 Model B

**Specifications**:
- **Processor**: Broadcom BCM2711, Quad-core Cortex-A72 (ARM v8) 64-bit SoC @ 1.5GHz
- **RAM**: 4GB LPDDR4-3200 SDRAM (minimum) or 8GB (recommended for voice features)
- **GPU**: VideoCore VI, OpenGL ES 3.0, Hardware H.264 decode
- **Storage**: MicroSD card slot (supports SDXC up to 2TB)
- **USB**: 2× USB 3.0, 2× USB 2.0
- **Network**: Gigabit Ethernet, 2.4/5.0 GHz WiFi 802.11ac, Bluetooth 5.0
- **Video**: 2× micro-HDMI ports (up to 4K 60Hz)
- **GPIO**: 40-pin header for HAT connectivity
- **Power**: 5V DC via USB-C (3A required)
- **Dimensions**: 85mm × 56mm × 17mm

**Why Pi 4?**:
- Sufficient processing power for real-time marine data
- GPU acceleration for camera streams
- USB 3.0 for high-speed peripherals
- Adequate RAM for AI voice models (Phi-2 2.7B)
- Active community and extensive software support

**Part Number**: RPI4-MODBP-4GB or RPI4-MODBP-8GB
**Manufacturer**: Raspberry Pi Foundation
**Estimated Cost**: $55 (4GB), $75 (8GB)

### 2.2 PiCAN-M HAT

**Specifications**:
- **CAN Controller**: MCP2515 (SPI interface)
- **CAN Transceiver**: MCP2551 (high-speed CAN)
- **Connector**: Micro-fit 4-pin (power + CAN H/L)
- **Bitrate**: Up to 1 Mbps (250 kbps for NMEA2000)
- **Termination**: Optional 120Ω termination resistor
- **LEDs**: Power, CAN TX/RX indicators
- **Dimensions**: Raspberry Pi HAT form factor
- **Mounting**: Uses Pi GPIO header (no soldering)

**Pinout**:
```
Micro-fit 4-pin Connector:
Pin 1: 12V+ (red)    - From boat power
Pin 2: GND (black)   - Ground
Pin 3: CAN-H (white) - NMEA2000 high
Pin 4: CAN-L (blue)  - NMEA2000 low
```

**Features**:
- Compatible with NMEA2000 marine networks
- Galvanic isolation (protects Pi from electrical noise)
- Easy plug-and-play installation
- Linux SocketCAN support
- Real-time clock (RTC) with battery backup

**Part Number**: PICAN-M
**Manufacturer**: SKPANG Electronics
**Estimated Cost**: $60

### 2.3 Touchscreen Display

**Specifications**:
- **Size**: 10.1 inches (diagonal)
- **Resolution**: 1920 × 1200 pixels (WUXGA)
- **Aspect Ratio**: 16:10
- **Brightness**: 1000 nits (sunlight readable)
- **Touch Technology**: Capacitive multi-touch (10 points)
- **Viewing Angle**: 178° (H) / 178° (V)
- **Contrast Ratio**: 1000:1
- **Response Time**: 25ms
- **Interface**: HDMI (video), USB (touch)
- **Backlight**: LED
- **Operating Temp**: 0°C to 50°C
- **Dimensions**: 230mm × 150mm × 10mm
- **Weight**: 350g

**Why 1000 nit?**:
- Essential for outdoor marine use in direct sunlight
- Standard laptop screens (300 nit) are unreadable in sun
- Comparable to dedicated marine chartplotters

**Recommended Models**:
- Waveshare 10.1" HDMI LCD (H) with 1000 nit option
- Generic 10.1" 1920×1200 IPS sunlight-readable display

**Estimated Cost**: $120-$150

### 2.4 USB GPS Receiver

**Specifications**:
- **Chipset**: u-blox 7 or 8 series
- **Channels**: 50+ concurrent
- **Update Rate**: 1 Hz (10 Hz capable)
- **Sensitivity**: -165 dBm
- **Accuracy**: 2.5m CEP (with WAAS/EGNOS)
- **Cold Start**: < 30 seconds
- **Hot Start**: < 1 second
- **Interface**: USB 2.0
- **Protocol**: NMEA 0183, UBX
- **Power**: 5V via USB (< 100mA)
- **Antenna**: Built-in patch antenna
- **Cable Length**: 1.5m (USB extension recommended)

**Recommended Model**: VK-162 G-Mouse USB GPS
**Alternative**: GlobalSat BU-353S4
**Part Number**: VK-162
**Estimated Cost**: $15-$20

**Features**:
- Plug-and-play (gpsd compatible)
- Magnetic mount for easy installation
- SMA connector for external antenna (optional)

### 2.5 USB AIS Receiver

**Specifications**:
- **Channels**: Dual-channel AIS (161.975 MHz, 162.025 MHz)
- **Sensitivity**: -112 dBm
- **Interface**: USB 2.0
- **Protocol**: NMEA 0183 (sentences: !AIVDM, !AIVDO)
- **Baud Rate**: 38400 bps
- **Power**: 5V via USB (< 500mA)
- **Antenna**: SMA connector (external marine antenna required)
- **Range**: Up to 40 nautical miles (with proper antenna)
- **LED Indicators**: Power, Message reception

**Recommended Model**: dAISy AIS Receiver
**Alternative**: Comar AIS-2-USB
**Part Number**: dAISy2+
**Estimated Cost**: $80-$100

**Important**:
- Requires external VHF marine antenna (not included)
- Best mounted high on vessel for maximum range
- Must be connected to dedicated AIS antenna (not shared with VHF radio)

### 2.6 Anker PowerConf S330 Speakerphone

**Specifications**:
- **Type**: USB speakerphone with 4-microphone array
- **Microphones**: 4× omnidirectional MEMS
- **Pickup Range**: 360° coverage, 3-meter radius
- **Speaker**: 5W full-range driver
- **Frequency Response**: 150Hz - 20kHz
- **Echo Cancellation**: Hardware acoustic echo cancellation (AEC)
- **Noise Reduction**: Hardware noise suppression
- **Interface**: USB-C (includes USB-A adapter)
- **Power**: USB bus-powered (no external power needed)
- **Compatibility**: Linux (ALSA), Windows, macOS
- **Dimensions**: 124mm diameter × 28mm height
- **Weight**: 340g

**Why This Speakerphone?**:
- Excellent echo cancellation (critical for voice assistant)
- Wide pickup pattern (hands-free from helm)
- Marine-grade audio processing
- USB-powered (no extra cables)
- Linux-compatible (plug-and-play)

**Part Number**: A3302
**Manufacturer**: Anker
**Estimated Cost**: $130

**Alternative**: Jabra Speak 510 ($120)

### 2.7 MicroSD Card

**Specifications**:
- **Capacity**: 64GB (minimum), 128GB (recommended)
- **Class**: UHS-I U3, A2 Application Performance Class
- **Read Speed**: 100 MB/s (minimum)
- **Write Speed**: 60 MB/s (minimum)
- **Endurance**: High-endurance rated for continuous write
- **Warranty**: Lifetime (for quality brands)

**Why A2 Class?**:
- Optimized for random read/write (app performance)
- Faster boot times
- Better database performance
- Reduced wear on flash memory

**Recommended**: SanDisk Extreme or Samsung EVO Plus
**Part Number**: SDSQXA1-128G-GN6MA (SanDisk 128GB)
**Estimated Cost**: $12-$20

---

## 3. OPTIONAL HARDWARE

### 3.1 Reolink RLC-810A IP Camera

**Specifications**:
- **Resolution**: 4K (3840 × 2160) @ 30fps
- **Sensor**: 1/2.8" 8MP progressive CMOS
- **Lens**: 4mm fixed (87° field of view)
- **Night Vision**: IR LEDs (100ft range)
- **Protocols**: RTSP, RTMP, ONVIF
- **Network**: 10/100 Mbps Ethernet (PoE supported)
- **Encoding**: H.264, H.265
- **Storage**: MicroSD card slot (up to 256GB)
- **Audio**: Built-in microphone
- **IP Rating**: IP66 (weatherproof)
- **Power**: 12V DC or PoE (802.3af)
- **Dimensions**: 194mm × 86mm × 86mm

**RTSP URL Format**:
```
rtsp://admin:password@192.168.1.100:554/h264Preview_01_main
```

**Part Number**: RLC-810A
**Manufacturer**: Reolink
**Estimated Cost**: $80-$100

**Installation Notes**:
- Requires PoE injector or 12V power supply
- Mount on mast or cabin for best coverage
- Configure static IP address
- Enable RTSP in camera settings

### 3.2 DC-DC Power Converter

**Specifications**:
- **Input**: 12V DC (9-17V range)
- **Output**: 5V DC, 3A (15W)
- **Efficiency**: > 90%
- **Isolation**: Galvanic isolation (protects from noise)
- **Protection**: Overload, short-circuit, over-temperature
- **Ripple**: < 50mV
- **Operating Temp**: -40°C to +55°C
- **Dimensions**: 63mm × 43mm × 24mm
- **Mounting**: DIN rail or screw mount

**Recommended**: Victron Energy Orion-Tr 12/12-9A
**Alternative**: DROK LM2596 (budget option, no isolation)
**Part Number**: ORI121209020
**Estimated Cost**: $35 (Victron), $8 (DROK)

**Why Galvanic Isolation?**:
- Protects Raspberry Pi from electrical noise
- Prevents ground loops
- Essential for reliable NMEA2000 operation

### 3.3 Enclosure

**Specifications**:
- **Material**: Aluminum or 3D-printed ABS/PETG
- **Dimensions**: 250mm × 180mm × 80mm (internal)
- **Ventilation**: Passive (no fans for reliability)
- **Mounting**: VESA 75mm or custom bracket
- **IP Rating**: IP20 (indoor), IP65 (outdoor with gaskets)
- **Access**: Removable front panel for touchscreen
- **Cable Entry**: PG9 cable glands (4-6 required)

**Options**:
1. **Custom 3D-Printed**: STL files provided in repository
2. **Aluminum Hammond**: 1455N2201 (IP65 rated)
3. **Pelican Case**: Pelican 1200 with custom cutouts

**Estimated Cost**: $20 (3D print), $50 (Hammond), $40 (Pelican)

### 3.4 Cooling

**Passive Cooling** (Recommended):
- **Heatsink**: Aluminum case acts as giant heatsink
- **Thermal Pads**: 15mm × 15mm × 1mm for CPU/GPU
- **Airflow**: Ventilation holes top/bottom (convection)

**Active Cooling** (Not Recommended):
- Fans introduce failure points in marine environment
- Use only if CPU temp consistently > 75°C
- Noctua NF-A4×10 (5V, quiet) if required

**Part Number**: Thermal pads included with most Pi 4 cases
**Estimated Cost**: $5-$10

---

## 4. HARDWARE INTERFACES

### 4.1 Interface Summary

| Interface | Protocol | Device | Speed | Purpose |
|-----------|----------|--------|-------|---------|
| **GPIO (HAT)** | SPI/CAN | PiCAN-M | 10 Mbps (SPI) | NMEA2000 bus |
| **USB 3.0** | Serial | GPS Receiver | 115.2 kbps | Position data |
| **USB 3.0** | Serial | AIS Receiver | 38.4 kbps | Vessel tracking |
| **USB 2.0** | Audio | Speakerphone | 48 kHz, 16-bit | Voice I/O |
| **HDMI** | Display | Touchscreen | 1080p @ 60Hz | Video output |
| **USB** | HID | Touchscreen | 125 Hz | Touch input |
| **Ethernet** | TCP/IP | IP Camera | 100 Mbps | RTSP stream |
| **WiFi** | 802.11ac | Client devices | 300 Mbps | Dashboard access |

### 4.2 GPIO Pinout (PiCAN-M)

The PiCAN-M HAT uses the following Raspberry Pi GPIO pins:

| Pin # | BCM # | Function | PiCAN-M Use |
|-------|-------|----------|-------------|
| 19 | GPIO10 | SPI0 MOSI | MCP2515 data out |
| 21 | GPIO9 | SPI0 MISO | MCP2515 data in |
| 23 | GPIO11 | SPI0 SCLK | MCP2515 clock |
| 24 | GPIO8 | SPI0 CE0 | MCP2515 chip select |
| 22 | GPIO25 | GPIO | MCP2515 interrupt |
| - | - | - | RTC battery backup |

**Important**: The PiCAN-M HAT reserves these pins. Do not use them for other purposes.

### 4.3 CAN Bus Configuration

**NMEA2000 Physical Layer**:
- **Bitrate**: 250 kbps (standard NMEA2000 speed)
- **Bus Topology**: Linear (trunk + drops)
- **Termination**: 120Ω at each end of bus
- **Max Cable Length**: 200 meters (backbone)
- **Max Drop Length**: 6 meters per device
- **Max Devices**: 50 (practical limit: 30)

**CAN0 Interface Setup** (`/etc/network/interfaces.d/can0`):
```bash
auto can0
iface can0 inet manual
    pre-up /sbin/ip link set can0 type can bitrate 250000
    up /sbin/ifconfig can0 up
    down /sbin/ifconfig can0 down
```

**Testing CAN Bus**:
```bash
# Check interface
ifconfig can0

# Monitor CAN traffic
candump can0

# Send test frame
cansend can0 1FFFFFFF#0011223344556677
```

### 4.4 USB Device Mapping

**Consistent Device Naming** (udev rules):

Create `/etc/udev/rules.d/99-d3kos.rules`:
```bash
# GPS Receiver
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", SYMLINK+="gps0"

# AIS Receiver
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="ais0"

# Speakerphone
SUBSYSTEM=="sound", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="000a", TAG+="systemd", ENV{PULSE_NAME}="helm-mic"
```

**Benefits**:
- Devices always appear at same location
- Scripts don't break if USB ports change
- Easier troubleshooting

---

## 5. ENVIRONMENTAL SPECIFICATIONS

### 5.1 Operating Conditions

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| **Operating Temperature** | 0°C to 50°C (32°F to 122°F) | Raspberry Pi limit |
| **Storage Temperature** | -20°C to 60°C (-4°F to 140°F) | Unpowered storage |
| **Humidity** | 5% to 95% non-condensing | Avoid condensation |
| **Ingress Protection** | IP20 (enclosure required) | Not waterproof bare |
| **Vibration** | Tested to marine standards | Secure mounting required |
| **Shock** | 50G (11ms half-sine) | Typical marine shock |
| **Altitude** | 0 to 2000m | Sea level operation |

### 5.2 Marine Environment Considerations

**Thermal Management**:
- **Issue**: Raspberry Pi can reach 80°C+ in direct sun
- **Solution**:
  - Mount in shaded location (not on console)
  - Use aluminum enclosure as heatsink
  - Ensure ventilation (convection cooling)
  - Monitor CPU temp (d3kos-health.service)

**Moisture Protection**:
- **Issue**: Condensation can damage electronics
- **Solution**:
  - IP65-rated enclosure with gaskets
  - Silica gel packets inside enclosure
  - Conformal coating on PCBs (optional)
  - Keep enclosure above bilge

**Vibration Isolation**:
- **Issue**: Engine vibration can loosen connections
- **Solution**:
  - Secure mounting with vibration-damping pads
  - Cable strain relief at all connections
  - Locking USB connectors (screw-type)
  - Threadlocker on mounting screws

**Salt Air Corrosion**:
- **Issue**: Salt accelerates corrosion of contacts
- **Solution**:
  - Gold-plated connectors where possible
  - Marine-grade tinned copper wiring
  - Dielectric grease on connections
  - Regular inspection and cleaning

### 5.3 Temperature Monitoring

d3kOS monitors CPU temperature and throttles if needed:

```javascript
// CPU Temperature Thresholds
const tempThresholds = {
  normal: 60,      // °C - Normal operation
  warning: 70,     // °C - Visual warning
  critical: 80,    // °C - Reduce load, voice alert
  throttle: 82     // °C - Hardware throttling begins
};
```

**Thermal Protection**:
- Software monitoring every 10 seconds
- Automatic service reduction at 80°C
- User alert at 70°C
- Hardware thermal throttling at 82°C (Pi built-in)

---

## 6. POWER REQUIREMENTS

### 6.1 Power Budget

| Component | Voltage | Current (Typ) | Current (Max) | Power (W) |
|-----------|---------|---------------|---------------|-----------|
| Raspberry Pi 4 | 5V | 1.2A | 3.0A | 15W |
| PiCAN-M HAT | 5V | 0.1A | 0.2A | 1W |
| Touchscreen | 5V | 0.5A | 0.8A | 4W |
| GPS Receiver | 5V | 0.08A | 0.1A | 0.5W |
| AIS Receiver | 5V | 0.3A | 0.5A | 2.5W |
| Speakerphone | 5V | 0.2A | 0.5A | 2.5W |
| **Total** | **5V** | **2.4A** | **5.1A** | **25.5W** |

**Recommended Power Supply**: 5V @ 5A (25W minimum, 30W for headroom)

### 6.2 Boat Power Integration

**From 12V Boat Battery**:

```
┌─────────────────┐
│  12V Battery    │  Boat house battery (12V nominal)
│  (11V - 14.5V)  │  Typical: 12.6V resting, 14.2V charging
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Fuse/Breaker  │  5A fuse (boat side protection)
│      5A         │  Protects wiring to converter
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DC-DC Conv     │  Victron Orion-Tr 12/12-9A
│  12V → 5V, 5A   │  Isolated, filtered, regulated
└────────┬────────┘
         │ 5V @ 5A
         ▼
┌─────────────────┐
│  Raspberry Pi   │  USB-C input
│  + Peripherals  │  Official Pi PSU cable recommended
└─────────────────┘
```

### 6.3 Power Quality

**Critical Requirements**:
- **Voltage Regulation**: ±5% (4.75V - 5.25V)
- **Ripple**: < 50mV peak-to-peak
- **Transient Protection**: Survive 24V transients (alternator spikes)
- **Reverse Polarity**: Protection required (diode or MOSFET)
- **Brownout**: Clean shutdown if voltage < 4.5V

**Why Galvanic Isolation?**:
- Prevents ground loops with NMEA2000 bus
- Filters alternator and ignition noise
- Protects Pi from boat electrical faults
- Required for reliable operation

### 6.4 Power Consumption Profiles

**Idle** (Dashboard only, no camera/voice):
- Power: ~10W
- Current: ~2A @ 5V
- Runtime on 100Ah battery: ~600 hours (theoretical)

**Typical Use** (Dashboard + voice standby):
- Power: ~15W
- Current: ~3A @ 5V
- Runtime on 100Ah battery: ~400 hours

**Peak Use** (Dashboard + voice active + camera recording):
- Power: ~25W
- Current: ~5A @ 5V
- Runtime on 100Ah battery: ~240 hours

**Startup Surge**:
- Peak: 3.0A for <1 second during boot
- Ensure power supply can handle 3A inrush

---

## 7. PHYSICAL MOUNTING

### 7.1 Mounting Options

**Option 1: Panel Mount** (Recommended)
```
┌─────────────────────────────────────┐
│          Navigation Console         │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │    d3kOS Touchscreen      │   │
│  │        (Flush Mount)        │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Chartplotter] [VHF Radio] [GPS]  │
└─────────────────────────────────────┘
```

**Option 2: RAM Mount** (Portable)
- Use RAM X-Grip for 10" tablets
- Suction cup or permanent mount base
- Adjustable for sun glare
- Easy removal for storage

**Option 3: Bulkhead Mount**
- VESA 75mm bracket
- Wall-mounted in pilothouse
- Viewing angle adjustable
- Cable management through bulkhead

### 7.2 Mounting Considerations

**Viewing Angle**:
- Optimal: 15-30° tilt from vertical
- Minimize glare from sun/water
- Comfortable viewing from helm position

**Accessibility**:
- Within arm's reach of helm
- Touch-friendly (no over-reach)
- Clear line of sight
- Not blocking critical instruments

**Cable Routing**:
- Strain relief at enclosure
- Secure along bulkhead/console
- Avoid pinch points
- Keep away from moving parts
- Bundle with cable ties

**Ventilation**:
- Do not mount in sealed space
- Ensure air circulation (passive convection)
- Avoid direct sun exposure
- Keep away from heat sources (engine exhaust)

### 7.3 Installation Diagram

```
Side View:
                Touchscreen
                     │
         ┌───────────┴───────────┐
         │   Aluminum Enclosure  │
         │  ┌─────────────────┐  │
         │  │ Raspberry Pi 4  │  │
         │  │   + PiCAN-M     │  │
         │  └─────────────────┘  │
         │                       │
         │  Ventilation Holes    │
         └──────────┬────────────┘
                    │
            Mounting Bracket
                    │
         ┌──────────▼──────────┐
         │   Navigation Console│
         │   or Bulkhead       │
         └─────────────────────┘

Cable Routing:
- 12V power (red/black) → DC-DC converter → USB-C
- NMEA2000 (white/blue) → Micro-fit 4-pin → PiCAN-M
- GPS/AIS (USB) → USB 3.0 ports
- Speakerphone (USB) → USB 2.0 port
- Camera (Ethernet) → RJ45 port
```

---

## 8. BILL OF MATERIALS

### 8.1 Core System (Required)

| Item | Description | Part Number | Qty | Unit Cost | Total |
|------|-------------|-------------|-----|-----------|-------|
| Raspberry Pi 4 | Model B, 4GB RAM | RPI4-MODBP-4GB | 1 | $55.00 | $55.00 |
| PiCAN-M HAT | NMEA2000 interface | PICAN-M | 1 | $60.00 | $60.00 |
| Touchscreen | 10.1" 1920×1200, 1000 nit | Generic | 1 | $120.00 | $120.00 |
| MicroSD Card | 128GB, A2, U3 | SDSQXA1-128G | 1 | $20.00 | $20.00 |
| DC-DC Converter | 12V→5V, 5A, isolated | ORI121209020 | 1 | $35.00 | $35.00 |
| USB GPS | VK-162 G-Mouse | VK-162 | 1 | $15.00 | $15.00 |
| USB AIS | dAISy receiver | dAISy2+ | 1 | $80.00 | $80.00 |
| Enclosure | Aluminum case | Hammond 1455N | 1 | $50.00 | $50.00 |
| Cables | HDMI, USB, power | Assorted | 1 | $20.00 | $20.00 |
| Mounting | VESA bracket + hardware | Generic | 1 | $15.00 | $15.00 |
| **Subtotal** | | | | | **$470.00** |

### 8.2 Voice Features (Tier 2)

| Item | Description | Part Number | Qty | Unit Cost | Total |
|------|-------------|-------------|-----|-----------|-------|
| Raspberry Pi 4 | Upgrade to 8GB RAM | RPI4-MODBP-8GB | 1 | $75.00 | $75.00 |
| Speakerphone | Anker PowerConf S330 | A3302 | 1 | $130.00 | $130.00 |
| MicroSD Card | Upgrade to 256GB | SDSQXA1-256G | 1 | $35.00 | $35.00 |
| **Subtotal** | (Additional cost for voice) | | | | **$240.00** |

### 8.3 Camera Integration (Tier 2)

| Item | Description | Part Number | Qty | Unit Cost | Total |
|------|-------------|-------------|-----|-----------|-------|
| IP Camera | Reolink RLC-810A | RLC-810A | 1 | $90.00 | $90.00 |
| PoE Injector | 802.3af, 15W | Generic | 1 | $12.00 | $12.00 |
| Ethernet Cable | Cat5e, 50ft outdoor | Generic | 1 | $15.00 | $15.00 |
| Camera Mount | Adjustable pole mount | Generic | 1 | $10.00 | $10.00 |
| **Subtotal** | (Additional cost for camera) | | | | **$127.00** |

### 8.4 Consumables & Tools

| Item | Description | Qty | Unit Cost | Total |
|------|-------------|-----|-----------|-------|
| Cable Ties | Assorted sizes, marine-grade | 50 | $0.10 | $5.00 |
| Heat Shrink Tubing | Assorted sizes | 1 pack | $8.00 | $8.00 |
| Dielectric Grease | Marine-grade, 4oz tube | 1 | $10.00 | $10.00 |
| Silica Gel Packets | Desiccant, 10g | 5 | $1.00 | $5.00 |
| Threadlocker | Blue (removable) | 1 | $6.00 | $6.00 |
| Fuse Holder | Blade fuse, 5A | 1 | $3.00 | $3.00 |
| **Subtotal** | | | | **$37.00** |

### 8.5 Total Cost Summary

| Configuration | Components | Total Cost |
|---------------|-----------|------------|
| **Tier 0 (Core)** | Basic system without voice/camera | **$470** |
| **Tier 2 (Voice)** | Core + 8GB Pi + Speakerphone | **$710** |
| **Tier 2 (Voice + Camera)** | Core + Voice + IP Camera | **$837** |
| **With Consumables** | Any configuration + tools/supplies | **+$37** |

**Note**: Costs are estimates (USD, 2026). Actual prices vary by supplier and location.

---

## 9. ASSEMBLY GUIDE

### 9.1 Pre-Assembly Checklist

Before starting, gather:
- [ ] All components (see BOM)
- [ ] Tools: Screwdrivers (Phillips, flathead), wire cutters, crimpers
- [ ] Multimeter (for testing voltages)
- [ ] Computer with microSD card reader
- [ ] d3kOS image file downloaded
- [ ] Raspberry Pi Imager software

### 9.2 Assembly Steps

**Step 1: Flash MicroSD Card**
1. Download d3kOS image from GitHub releases
2. Verify checksum: `sha256sum d3kos-vX.X.X.img.gz`
3. Launch Raspberry Pi Imager
4. Choose OS → Use custom → Select .img.gz file
5. Choose storage → Select your microSD card
6. Write (takes 5-10 minutes)
7. Safely eject card

**Step 2: Attach PiCAN-M HAT**
1. Place Raspberry Pi on anti-static surface
2. Align PiCAN-M GPIO pins with Pi header
3. Press firmly until fully seated (no gap)
4. Secure with included standoffs (finger tight)
5. **Do NOT power on yet**

**Step 3: Install Cooling**
1. Apply thermal pad to CPU (large chip)
2. Apply thermal pad to GPU (near CPU)
3. Apply thermal pad to RAM (near CPU)
4. If using heatsink case, attach now

**Step 4: Prepare Enclosure**
1. Drill cable entry holes (use PG9 cable glands)
2. Mount touchscreen in front panel
3. Create ventilation holes (top/bottom)
4. Test-fit Raspberry Pi (don't secure yet)

**Step 5: Wire DC-DC Converter**
1. Connect 12V+ (red) to boat fuse block (5A fuse)
2. Connect GND (black) to boat ground
3. Test output voltage: **Must be 5.0V ±0.25V**
4. Connect USB-C cable to converter output
5. Secure converter with mounting screws

**Step 6: Connect Peripherals**
1. Insert microSD card into Pi (contacts facing up)
2. Connect HDMI cable (Pi → Touchscreen)
3. Connect USB cable (Touchscreen touch → Pi USB 2.0)
4. Connect GPS (USB 3.0 port, blue)
5. Connect AIS (USB 3.0 port, blue)
6. Connect Speakerphone (USB 2.0 port, black)
7. Connect Ethernet cable (if camera used)

**Step 7: Connect NMEA2000**
1. Locate micro-fit 4-pin connector on PiCAN-M
2. Connect NMEA2000 drop cable:
   - Pin 1 (red): 12V+
   - Pin 2 (black): GND
   - Pin 3 (white): CAN-H
   - Pin 4 (blue): CAN-L
3. Verify connections with multimeter:
   - 12V between red and black: ~12V
   - Resistance between white and blue: ~60Ω (with termination)

**Step 8: Cable Management**
1. Route all cables through glands
2. Apply strain relief at entry points
3. Bundle cables with cable ties
4. Leave 6" service loop inside enclosure
5. Apply dielectric grease to all connectors

**Step 9: First Power-On**
1. **Double-check all connections**
2. Connect USB-C power to Raspberry Pi
3. Watch for:
   - Green LED (activity) flashing
   - Display shows boot messages
   - Boot time: ~60 seconds
4. If no activity after 30 seconds, disconnect power and check connections

**Step 10: Initial Configuration**
1. Touchscreen should show Chromium (maximized)
2. Look for WiFi network: "d3kOS"
3. Connect from phone/tablet (password: `d3kos-2026`)
4. Navigate to: `http://10.42.0.1`
5. Complete onboarding wizard (13 questions)

### 9.3 Post-Installation Testing

**Test 1: Touchscreen Calibration**
- Tap each corner of screen
- Verify cursor follows touch
- Test on-screen keyboard

**Test 2: NMEA2000 Data**
```bash
# From SSH or console
candump can0 | grep -E '127488|127489|127505'
```
- Should see PGNs scrolling
- If nothing, check CAN-H/CAN-L connections

**Test 3: GPS Lock**
```bash
cgps -s
```
- Wait for satellites (2-5 minutes)
- Verify latitude/longitude correct

**Test 4: AIS Reception**
```bash
cat /dev/ttyUSB1
```
- Should see !AIVDM sentences
- If nothing, check antenna connection

**Test 5: Voice (Tier 2)**
- Say: "Helm"
- Wait for beep (~500ms)
- Say: "What's the engine status?"
- Should hear response within 2 seconds

**Test 6: Camera (if installed)**
- Navigate to Main Menu → Camera
- Should see live RTSP stream
- Verify night vision (cover lens)

---

## 10. HARDWARE TROUBLESHOOTING

### 10.1 Power Issues

**Problem**: Raspberry Pi won't power on (no LED)

**Possible Causes & Solutions**:
1. **Insufficient power supply**
   - Test: Measure voltage at USB-C: must be 5.0V ±0.25V
   - Fix: Use official Pi power supply or upgrade converter

2. **Bad USB-C cable**
   - Test: Try different cable
   - Fix: Use high-quality cable (24AWG power wires)

3. **Polarity reversed**
   - Test: Check 12V input with multimeter
   - Fix: Correct wiring (red=+, black=-)

4. **Blown fuse**
   - Test: Check continuity across fuse
   - Fix: Replace 5A fuse, investigate short

**Problem**: Random reboots

**Possible Causes & Solutions**:
1. **Undervoltage** (check `/var/log/syslog` for "Under-voltage detected")
   - Test: Measure voltage under load: must stay > 4.75V
   - Fix: Larger gauge power wires, better converter

2. **Overheating** (check `vcgencmd measure_temp`)
   - Test: Monitor CPU temp: should be < 80°C
   - Fix: Improve ventilation, add heatsink, move to cooler location

3. **SD card corruption**
   - Test: Run `fsck` on SD card
   - Fix: Reflash SD card, use high-quality card

### 10.2 NMEA2000 Issues

**Problem**: No NMEA2000 data (candump shows nothing)

**Troubleshooting Steps**:
1. Check CAN interface exists:
   ```bash
   ifconfig can0
   ```
   - If not found: PiCAN-M not detected (reseat HAT)

2. Check bus voltage:
   - Measure 12V between red and black wires at micro-fit
   - Should read ~12V
   - If 0V: NMEA2000 bus not powered

3. Check termination:
   - Measure resistance between CAN-H and CAN-L
   - Should read ~60Ω (two 120Ω resistors in parallel)
   - If open circuit: Missing termination resistors
   - If ~120Ω: Only one terminator (need two)
   - If < 50Ω: Too many terminators

4. Check wiring:
   - Swap CAN-H and CAN-L (common mistake)
   - Verify white=CAN-H, blue=CAN-L

5. Test with known-good device:
   - Connect laptop with NMEA2000 interface
   - Verify bus has traffic

**Problem**: Intermittent NMEA2000 data

**Possible Causes**:
- Loose connections (vibration)
- Bad crimp on micro-fit pins
- Corroded contacts (salt water intrusion)
- Electromagnetic interference (ignition noise)

**Fix**:
- Apply dielectric grease to contacts
- Use shielded NMEA2000 cable
- Route cable away from engine/alternator
- Check ground connections

### 10.3 Display Issues

**Problem**: No display output

**Troubleshooting**:
1. Check HDMI connection (reseat both ends)
2. Try different HDMI cable
3. Verify touchscreen power LED is on
4. Check Pi green LED is flashing (SD card activity)
5. Try external HDMI monitor to isolate issue

**Problem**: Display too dim (can't see in sunlight)

**Solutions**:
- Verify 1000 nit display (not 300 nit)
- Check brightness setting (often accessible via touchscreen button)
- Adjust mounting angle to reduce glare
- Add polarizing filter (reduces brightness but improves contrast)

**Problem**: Touchscreen not responding

**Troubleshooting**:
1. Check USB touch cable connected
2. Verify in `lsusb` output:
   ```bash
   lsusb | grep -i touch
   ```
3. Test with mouse to verify OS is running
4. Recalibrate touch: `xinput-calibrator`

### 10.4 GPS/AIS Issues

**Problem**: No GPS fix

**Troubleshooting**:
1. Check GPS LED (should blink when acquiring satellites)
2. Verify USB connection: `lsusb | grep -i prolific`
3. Check gpsd status: `systemctl status gpsd`
4. View GPS data: `cgps -s`
5. Ensure antenna has clear view of sky (not inside metal cabin)
6. Wait 5 minutes (cold start can be slow)

**Problem**: No AIS data

**Troubleshooting**:
1. Verify AIS LED flashing (indicates messages received)
2. Check USB connection: `lsusb | grep -i ftdi`
3. Monitor serial port: `cat /dev/ttyUSB1`
4. Verify antenna connected (SMA connector)
5. Check antenna location (high = better range)
6. Test with known AIS traffic nearby (VesselFinder app)

### 10.5 Performance Issues

**Problem**: Slow dashboard updates

**Troubleshooting**:
1. Check CPU usage: `top`
   - If > 90%: Too many services running
   - Fix: Disable camera or voice temporarily

2. Check memory: `free -h`
   - If < 500MB free: Memory pressure
   - Fix: Restart services, upgrade to 8GB Pi

3. Check SD card speed: `dd if=/dev/zero of=/tmp/test bs=1M count=100`
   - Should be > 50 MB/s write
   - If slow: Replace with A2-rated card

**Problem**: Voice assistant not responding

**Tier 2+ Only**

**Troubleshooting**:
1. Check service status: `systemctl status helm-voice`
2. Check microphone: `arecord -l`
3. Test wake word: Say "Helm" (check `/var/log/helm-voice.log`)
4. Verify Phi-2 model loaded (check RAM usage: should be +3GB)
5. Check CPU temp (throttling slows inference)

---

## APPENDIX A: CONNECTOR PINOUTS

### A.1 PiCAN-M Micro-Fit 4-Pin

```
View: Looking at connector (tab on bottom)

  ┌───────────────┐
  │  ⚫  ⚫  ⚫  ⚫ │
  │  1   2   3   4│
  └───────┬───────┘
          │ (tab)

Pin 1: 12V+ (RED)    - Boat power +
Pin 2: GND (BLACK)   - Boat ground
Pin 3: CAN-H (WHITE) - NMEA2000 high
Pin 4: CAN-L (BLUE)  - NMEA2000 low
```

### A.2 NMEA2000 DeviceNet Micro-C

Standard NMEA2000 cables use DeviceNet Micro-C connectors:

```
Male (Tee or Backbone):
Pin 1: Shield
Pin 2: NET-S (power -)
Pin 3: NET-C (CAN-H)
Pin 4: NET-S (power +)
Pin 5: NET-C (CAN-L)

Female (Device Drop):
Same pinout (mirrors male)
```

**Adapter Required**: DeviceNet Micro-C Female → Micro-Fit 4-pin Male

---

## APPENDIX B: RECOMMENDED SUPPLIERS

| Component | Supplier | Part Number | URL |
|-----------|----------|-------------|-----|
| Raspberry Pi 4 | Adafruit | RPI4-MODBP-4GB | adafruit.com |
| PiCAN-M | SKPANG | PICAN-M | skpang.co.uk |
| GPS VK-162 | Amazon | VK-162 | amazon.com |
| AIS dAISy | Amazon | dAISy2+ | amazon.com |
| Anker S330 | Amazon | A3302 | amazon.com |
| Reolink Camera | Reolink | RLC-810A | reolink.com |
| Victron Converter | Victron | ORI121209020 | victronenergy.com |
| Marine Supplies | West Marine | Various | westmarine.com |

---

## APPENDIX C: REVISION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-04 | Initial hardware specification |
| 2.0 | 2026-02-06 | Added detailed assembly guide, troubleshooting, BOM costs |

---

**END OF HARDWARE SPECIFICATION**
