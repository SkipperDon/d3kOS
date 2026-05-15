# WiBoat — Bill of Materials & Assembly Instructions

## Version 2.0 — 4-Antenna Phase 1 Baseline

**Document:** `WiBoat\_BOM\_v2.md` **Version:** 2.0 **Date:** 2026-05-15 **Supersedes:** `WiBoat\_BOM\_Assembly\_Instructions.docx` v1.0 **Status:** Engineering Baseline — 4-Antenna Configuration


## Revision History

| Version | Date | Summary |
| - | - | - |
| 1.0 | 2026-05-15 | Initial BOM — 2-antenna Phase 1, 4-antenna Phase 3 upgrade path |
| 2.0 | 2026-05-15 | **4-antenna array from Phase 1.** SP4T RF switch added for 4-channel CSI. Both ALFA TX injectors from Phase 1. All upgrade paths removed — full configuration deployed from day one. |



## Critical Architecture Note

The **Raspberry Pi 4B internal BCM43455 WiFi chip** does ALL CSI (Channel State Information) receiving. It has one RF receive chain. The ALFA USB adapters transmit probe packets; the BCM43455 receives reflections.

To get four independent antenna positions for bearing estimation (MUSIC algorithm), a **GPIO-controlled SP4T RF switch** cycles the BCM43455 receive input through four antenna ports sequentially. At 100 packets/second, each antenna is sampled at 25 packets/second (40 ms interval). At marine target speeds (≤20 kts / 10 m/s), this introduces ≤0.4 m displacement between antenna samples — well within the ±15° bearing accuracy budget at ranges ≥30 m.

**This is the standard approach for single-chip 4-element CSI arrays in maritime research. No second Raspberry Pi is required.**


## Section 1 — Phase 1 Complete Bill of Materials

All items below are deployed in Phase 1. There are no "Phase 2" or "Phase 3" hardware upgrades for the antenna array — the full 4-antenna configuration is built from the start.

### 1.1 Core Processing Hardware

| Item | Part / Model | Qty | Unit Cost (CAD) | Total (CAD) | Notes |
| - | - | - | - | - | - |
| Raspberry Pi 4B — WiBoat processor | RPi 4B, 4GB RAM | 1 | $85–$105 | $85–$105 | Kernel 5.10 LOCKED (Bullseye 32-bit). NEVER run `apt upgrade` after nexmon\_csi install. |
| MicroSD card | SanDisk Endurance 32GB | 1 | $12–$18 | $12–$18 | Industrial endurance preferred — continuous write workload |
| USB-C power supply | Official RPi PSU 5V/3A | 1 | $15–$20 | $15–$20 | Stable power critical — RF switch + 4 antennas draw current |
| Gigabit Ethernet cable | Cat6 1m | 1 | $5–$8 | $5–$8 | WiBoat RPi 4B ↔ boat router |


**Core hardware subtotal: $117–$151 CAD**


### 1.2 CSI Receive — 4-Antenna Array

The BCM43455 internal chip performs all CSI reception. The SP4T switch multiplexes 4 antenna inputs to the BCM43455.

| Item | Part / Model | Qty | Unit Cost (CAD) | Total (CAD) | Notes |
| - | - | - | - | - | - |
| 12 dBi outdoor omni antenna | Tupavco TP551 2.4 GHz 12dBi N-Female OR equivalent (e.g., TP-Link TL-ANT2412D, Alpha AOA-2409TF) | **4** | $35–$55 | **$140–$220** | All 4 installed Phase 1. Fibreglass radome. UV/salt resistant. N-Female connector. |
| SP4T RF switch — GPIO-controlled | Mini-Circuits MSW-2-20+ or equivalent SP4T 2.4 GHz RF switch; 50Ω; TTL/GPIO control | 1 | $18–$35 | $18–$35 | Single-Pole 4-Throw switch. Connects all 4 antennas to BCM43455 RX input. GPIO pins on RPi 4B control antenna selection. SMA connectors preferred. Breakout board available from RF parts suppliers. |
| SMA adapter — N-Female to SMA-Male | N-Female to SMA-Male | 4 | $4–$7 | $16–$28 | Adapts antenna N-Female connectors to switch SMA ports |
| SMA adapter — SMA-Female to U.FL/IPEX | SMA to IPEX/U.FL pigtail, 100mm | 1 | $5–$8 | $5–$8 | Connects switch output to RPi 4B BCM43455 internal antenna connector (replaces stock antenna) |
| LMR-400 coax — antenna runs | LMR-400 with N-Male connectors, custom length | 4 | $15–$25/m | $60–$100 per antenna run (4m each) | Low-loss coax for mast/arch runs. 4 runs × ~4m each = 16m total. Source: Times Microwave or equivalent. Have professionally terminated or use crimping tool. |


**4-antenna array subtotal: $239–$391 CAD**

> **SP4T switch wiring:** The 4 antenna coax lines connect to the 4 switch input ports. The switch output (common port) connects via short SMA-to-IPEX pigtail to the BCM43455 internal antenna connector. 3 GPIO pins (binary) control which antenna is selected: 00=ant1, 01=ant2, 10=ant3, 11=ant4. The nexmon\_csi service software cycles these pins at the packet rate to distribute CSI observations across all 4 antenna positions.


### 1.3 TX Injection — Both ALFA Adapters from Phase 1

The ALFA adapters **transmit** the 2.4 GHz probe frames whose reflections the BCM43455 receives. With 4 receive antennas covering 360°, two TX adapters are needed from Phase 1 for full azimuthal probe coverage.

| Item | Part / Model | Qty | Unit Cost (CAD) | Total (CAD) | Notes |
| - | - | - | - | - | - |
| USB WiFi adapter — TX injector | ALFA AWUS036NH (AR9271, 2.4 GHz, 2W) | **2** | $38–$50 | **$76–$100** | TX probe injection only — does NOT perform CSI extraction (no nexmon support on Atheros). High TX power (2W) maximises reflection distance to ~250m. |
| USB extension / powered hub | Short USB cable or powered USB3 hub | 1 | $10–$20 | $10–$20 | Isolates ALFA USB power draw from RPi 4B USB bus |


**TX injection subtotal: $86–$120 CAD**


### 1.4 LoRa / Meshtastic Radio

| Item | Part / Model | Qty | Unit Cost (CAD) | Total (CAD) | Notes |
| - | - | - | - | - | - |
| LoRa node | Heltec WiFi LoRa 32 V3 (SX1262, 915 MHz — Canadian frequency) | 1 | $22–$30 | $22–$30 | Flash with Meshtastic firmware. USB serial to RPi 4B. 5–15 km range for cooperative hazard sharing. |
| LoRa antenna | 915 MHz 3 dBi rubber duck (included with Heltec V3) | 1 | Included | $0 | Supplied with board. Mount externally for best range if possible. |


**LoRa subtotal: $22–$30 CAD**


### 1.5 Weatherproofing and Mounting

| Item | Part / Model | Qty | Unit Cost (CAD) | Total (CAD) | Notes |
| - | - | - | - | - | - |
| IP65 weatherproof enclosure | Hammond 1554D or equivalent plastic IP65 box, ~200×160×90mm | 1 | $28–$45 | $28–$45 | Houses RPi 4B, SP4T switch board, USB hub. Mount below-deck or in cockpit locker. |
| Cable entry glands | PG7 glands for coax (×4) + USB power entry (×2) | 6 | $2–$4 each | $12–$24 | Waterproof cable entry. |
| DIN rail or mounting tray | 3D-printable bracket or aluminium tray | 1 | $5–$15 | $5–$15 | Internal mounting for RPi + switch board |
| Self-amalgamating tape | For exposed antenna connector joints | 1 roll | $8–$12 | $8–$12 | Apply over N-Male connections at mast/arch where weather exposure exists |
| Stainless steel antenna mounting | Ratchet/rail mount for mast or radar arch | 4 | $12–$20 each | $48–$80 | One per antenna. Position for 90° spacing on Uniform Circular Array. |


**Mounting subtotal: $101–$176 CAD**


### 1.6 Phase 3 Hardware (deferred — budget for later)

These items are NOT required for Phase 1 or Phase 2. They are listed for Phase 3 budget planning only.

| Item | Phase | Estimated Cost (CAD) | Purpose |
| - | - | - | - |
| 5 GHz USB WiFi adapter (ALFA AWUS036AC or similar) | P3 | $45–$65 | batman-adv cooperative mesh with other WiBoat vessels at ≤500 m |
| RF power amplifier (2.4 GHz, ≤800 mW) | P3 | $35–$60 | Extended TX range. EIRP must be recalculated before deployment; must not exceed 4W (36 dBm) under ISED RSS-210 |



## Section 2 — Phase 1 Cost Summary

| Category | Low (CAD) | High (CAD) |
| - | - | - |
| Core processing hardware | $117 | $151 |
| 4-antenna receive array + SP4T switch | $239 | $391 |
| TX injection (2x ALFA) | $86 | $120 |
| LoRa / Meshtastic | $22 | $30 |
| Weatherproofing and mounting | $101 | $176 |
| **Phase 1 Total** | **$565** | **$868** |


> **Note on antenna cost variance:** The main cost driver is LMR-400 coax length and termination. Pre-terminated LMR-400 assemblies cost more per metre than bulk cable + field termination. Buying bulk cable and having a marine electronics shop terminate the N-connectors typically saves $30–$60.


## Section 3 — Antenna Array Layout

### 3.1 Uniform Circular Array (UCA) Configuration

Four antennas arranged in a circle at 90° intervals. This configuration enables Unitary Root MUSIC to compute unambiguous bearing from all four quadrants.

```
        ANT-1 (12 o'clock — forward)  
             |  
ANT-4 ------+------ ANT-2  
(9 o'clock) | (3 o'clock)  
             |  
        ANT-3 (6 o'clock — aft)
```

**Array diameter (d):** The physical spacing between opposite antennas should be approximately **λ/2 to 2λ** at 2.4 GHz, where λ = 125 mm.

- Minimum spacing: 62.5 mm (λ/2) — required for MUSIC phase disambiguation

- Optimal spacing: 125–250 mm (λ to 2λ) — maximises angular resolution

- **Recommended array diameter: 200–300 mm** (antenna centres)

### 3.2 Mounting on Mast or Radar Arch

For a radar arch or mast, mount the 4 antennas at compass points (N/S/E/W relative to boat centreline) at the same height. Ensure no metallic obstruction within 300 mm of any antenna element.

- Keep all 4 LMR-400 coax runs **equal length** (within 10%) to maintain phase coherence

- Coax runs connect to SP4T switch in weatherproof enclosure below deck

- SP4T switch output connects to BCM43455 internal antenna connector

### 3.3 Antenna Position in wiboat-config.json

```
\{  
  "antenna\_array": \{  
    "type": "UCA",  
    "element\_count": 4,  
    "diameter\_mm": 250,  
    "spacing\_mm": 177,  
    "switch\_gpio\_pins": \[17, 27, 22\],  
    "antenna\_positions\_deg": \[0, 90, 180, 270\]  
  \},  
  "network": \{  
    "on\_boat": \{  
      "wiboat\_ip": "10.42.0.2",  
      "d3kos\_ip": "10.42.0.1",  
      "subnet": "10.0.0.0/24"  
    \},  
    "lan\_dev": \{  
      "wiboat\_ip": "DHCP",  
      "d3kos\_ip": "192.168.1.237",  
      "subnet": "192.168.1.0/24"  
    \}  
  \}  
\}
```


## Section 4 — SP4T RF Switch Wiring Guide

### 4.1 What is the SP4T Switch?

A Single-Pole 4-Throw (SP4T) RF switch is a small electronic component (typically a chip on a PCB breakout) that connects ONE of four inputs to a single output, controlled by digital signals from the Raspberry Pi GPIO pins.

In this application:

- **4 inputs** → connected to the 4 antenna coax lines

- **1 output** → connected to the BCM43455 antenna input (via SMA-to-IPEX pigtail)

- **Control** → 2–3 GPIO pins on RPi 4B (binary selection)

### 4.2 Wiring Diagram

```
Antenna 1 (0°)  ──────┐  
Antenna 2 (90°) ──────┤  SP4T RF    ──── SMA-to-IPEX ──── BCM43455  
Antenna 3 (180°)──────┤  Switch         pigtail (100mm)    RX input  
Antenna 4 (270°)──────┘  
                       ↑  
                  GPIO 17,27,22  
                  from RPi 4B
```

### 4.3 GPIO Pin Assignment (default — configurable)

| GPIO | Binary bit | State |
| - | - | - |
| GPIO 17 | Bit 0 (LSB) | Antenna select |
| GPIO 27 | Bit 1 | Antenna select |
| GPIO 22 | Bit 2 (MSB) | Enable (HIGH = switch enabled) |


| GPIO 22 | GPIO 27 | GPIO 17 | Selected antenna |
| - | - | - | - |
| 1 | 0 | 0 | Antenna 1 (0°) |
| 1 | 0 | 1 | Antenna 2 (90°) |
| 1 | 1 | 0 | Antenna 3 (180°) |
| 1 | 1 | 1 | Antenna 4 (270°) |


### 4.4 Recommended SP4T Parts

| Part | Supplier | Cost (CAD) | Notes |
| - | - | - | - |
| Mini-Circuits MSW-2-20+ | Mini-Circuits direct / Digi-Key | $25–$40 | Breakout available. 50Ω. DC–20 GHz. TTL control. SMA connectors. Best option. |
| PE42440 (pSemi / Peregrine) | Mouser / Digi-Key | $18–$28 | SMD chip — needs PCB or breakout. Low insertion loss at 2.4 GHz. |
| HMC252 (Analog Devices) | Mouser | $20–$30 | SMD chip — alternative. Well-documented. |


> **Easiest option for builders:** Order a pre-assembled SP4T switch module with SMA connectors from AliExpress or RF Parts (search "SP4T RF switch SMA 2.4GHz GPIO"). These typically cost $15–$25 CAD including connectors and a small PCB with header pins — no soldering required.


## Section 5 — Software Configuration

### 5.1 nexmon\_csi Configuration

nexmon\_csi is installed on the WiBoat RPi 4B and configured to receive on 2.4 GHz channel 6 in monitor mode. The wiboat-processor service cycles the SP4T switch GPIO pins between CSI packet receptions.

**Required kernel:** Raspberry Pi OS Bullseye 32-bit, kernel 5.10. After nexmon\_csi installation, NEVER run `apt upgrade`. The kernel is permanently locked to 5.10.

**CSI extraction is performed by BCM43455 only.** The ALFA adapters are configured in master mode to inject 802.11 probe request frames continuously. The BCM43455 receives the reflected frames and extracts per-subcarrier amplitude and phase data.

### 5.2 Network Configuration

**On-boat deployment:**

```
\# /etc/dhcpcd.conf — static IP on WiBoat RPi 4B  
interface eth0  
static ip\_address=10.42.0.2/24  
static routers=10.42.0.1  
static domain\_name\_servers=10.42.0.1
```

**wiboat-config.json (on-boat):**

```
\{  
  "network": \{  
    "wiboat\_ip": "10.42.0.2",  
    "listen\_port": 8766,  
    "health\_port": 8767,  
    "meshtastic\_port": 8768  
  \},  
  "signalk": \{  
    "host": "10.42.0.1",  
    "port": 3000  
  \}  
\}
```

**Environment override for LAN/dev:**

```
export WIBOAT\_HOST=192.168.1.237   \# D3kOS RPi 5 LAN address  
export WIBOAT\_SELF=192.168.1.xx    \# WiBoat dev address (DHCP)
```


## Section 6 — Pre-Build Checklist

Before purchasing any hardware, verify:

- [ ] Raspberry Pi 4B in stock — confirm 4GB model for TFLite headroom

- [ ] Confirm local frequency regulations: 915 MHz LoRa is the Canadian ISED frequency. Verify if outside Canada.

- [ ] Measure mast or radar arch: confirm 200–300 mm diameter mounting ring is feasible for 4-antenna UCA placement

- [ ] Measure coax run lengths from antenna mounting to enclosure — order LMR-400 with 10% excess

- [ ] Confirm boat router can assign static IP `10.42.0.2` before Phase 1 code is written


## Section 7 — Assembly Sequence

### Phase 1 Assembly Order

1. **Flash SD card** — Raspberry Pi OS Bullseye 32-bit. Set hostname `wiboat`. Assign static IP `10.42.0.2` in `/etc/dhcpcd.conf`. Enable SSH.

2. **Install nexmon\_csi** — Follow nexmon\_csi RPi 4B Bullseye guide. After installation, lock kernel: `apt-mark hold raspberrypi-kernel raspberrypi-kernel-headers`.

3. **Wire SP4T switch** — Connect SMA-to-IPEX pigtail from switch common output to BCM43455 internal antenna connector. Connect GPIO pins 17, 27, 22 to switch control lines. Connect 3.3V and GND.

4. **Connect 4 antenna coax lines** — Connect LMR-400 runs (equal length) from 4 antenna positions to SP4T switch input ports. Use N-to-SMA adapters at antenna connectors.

5. **Connect ALFA adapters** — Both ALFA AWUS036NH connected to RPi 4B USB ports (or powered hub). Configure in master mode for probe injection.

6. **Connect Heltec V3 LoRa** — USB serial to RPi 4B. Flash Meshtastic firmware on Heltec before connecting.

7. **Mount antennas** — Install 4 antennas at 90° intervals on mast or radar arch. Apply self-amalgamating tape over all exposed N-Male connections. Run coax to enclosure.

8. **Enclosure** — Mount RPi 4B, SP4T switch, and USB hub inside IP65 enclosure. Use cable glands for all coax and power entries. Seal.

9. **Power test** — Apply power. Confirm SSH access at `10.42.0.2`. Confirm nexmon\_csi daemon running: `sudo systemctl status nexmon\_csi.service`.

10. **CSI validation** — Run range calibration test against 1 m² aluminium reflector at 10 m, 25 m, and 50 m. Confirm ±5 m accuracy at 50 m (Phase 1 acceptance criterion).


## Section 8 — Safety and Regulatory Notes

### EIRP Limit (ISED RSS-210, Canada)

Maximum EIRP: **4W = 36 dBm**

Phase 1 TX budget:

- ALFA AWUS036NH output: 30 dBm (1W)

- LMR-400 cable loss (4m at 2.4 GHz): −1.5 dB

- Antenna gain: +12 dBi

- **EIRP: 30 − 1.5 + 12 = 40.5 dBm → EXCEEDS LIMIT**

> **IMPORTANT:** Running the ALFA at full 2W (30 dBm) with a 12 dBi antenna exceeds the Canadian ISED limit. The ALFA TX power must be reduced to approximately **21 dBm (125 mW)** to stay within the 36 dBm EIRP limit with a 12 dBi antenna and 1.5 dB cable loss: 21 − 1.5 + 12 = 31.5 dBm ≈ 1.4W EIRP (within limit). Use `iwconfig wlan1 txpower 21` to set TX power. Document this setting in the system installation guide.

### Air-Gapped Operation

WiBoat operates without internet connectivity. All AI inference (TFLite Phase 2+) runs locally on-device. No raw CSI data, contact data, or position data leaves the boat LAN.


*WiBoat Bill of Materials and Assembly Instructions v2.0* *2026-05-15 | Skipper Don | AtMyBoat.com* *4-antenna Phase 1 baseline — SP4T RF switch architecture — dual-network config* *Supersedes: WiBoat\_BOM\_Assembly\_Instructions.docx v1.0*


# Where to buy at the lowest price May 15, 2026 Canada

**The lowest verified retail pricing and corresponding purchase locations for your Phase 1 Bill of Materials in Canada are detailed below:**

## **1.1 Core Processing Hardware**

- **Raspberry Pi 4 Model B (4GB RAM)**: Available for **$144.47 CAD** from [DigiKey Canada](https://www.digikey.ca/fr/products/detail/mini-circuits/MSW-2-20-/13927100). Alternatively, the base unit is in production via specialized distributors like [PiShop.ca](https://www.pishop.ca/product/raspberry-pi-4-model-b-4gb/).

- **MicroSD Card (SanDisk High Endurance 32GB)**: Sourced for **$39.95 CAD** at PiShop.ca. Designed specifically to sustain continuous file overwrite workloads.

- **Official USB-C Power Supply (5.1V 3A)**: Can be ordered for **$11.56 CAD** through DigiKey Canada or for **$11.95 CAD** via [PiShop.ca](https://www.pishop.ca/product/raspberry-pi-15w-power-supply-us-white/).

- **Gigabit Ethernet Cable (Cat6 1m)**: Generic Cat6 cables from local industrial/electronic retailers are recommended to keep deployment within the estimated $5–$8 CAD boundary. \[1\] 

## **1.2 CSI Receive — 4-Antenna Array**

- **12 dBi Outdoor Omni Antenna**: The Tupavco TP551 2.4 GHz model can be searched directly through the [Amazon Canada Tupavco Store](https://www.amazon.ca/Wireless-Connector-Amplifier-Tupavco-TP551/dp/B07YGPDPW8).

- **SP4T RF Switch IC (Mini-Circuits MSW-2-20+)**: The bare surface-mount switch component is listed at **$29.11 CAD** on [DigiKey Canada](https://www.digikey.ca/fr/products/detail/mini-circuits/MSW-2-20-/13927100) and via [Mouser Canada](https://www.mouser.ca/ProductDetail/Mini-Circuits/MSW-2-20+?qs=xZ%2FP%252Ba9zWqbkBcBeVIejhQ%3D%3D&mgh=1). *(Note: For deployment, ensure you acquire this pre-soldered onto an SMA breakout panel through RF prototyping suppliers).*

- **Coaxial Infrastructure (RF Adapters & LMR-400 Cable)**: Standard N-Female to SMA-Male adapters, U.FL pigtails, and custom LMR-400 cables are best procured through regional automation and component hubs like DigiKey Canada to ensure low signal attenuation. \[2, 3\] 

## **1.3 TX Injection**

- **USB WiFi Adapter (ALFA AWUS036NH)**: The legacy Atheros AR9271 variant is available for **$27.99 CAD** via AliExpress. *(Note: Because the AWUS036NH model is formally End-of-Life, you can verify stock or view current high-power alternatives on the [Amazon CA ALFA Network Hub](https://www.amazon.ca/AWUS036NH-Network-Drive-Free-Wireless-Penetration/dp/B09G8CZBX1)).*

- **Powered USB Hub**: A standard USB 3.0 powered hub can be sourced from local electronics storefronts to ensure stable current flow. \[4\] 

## **1.4 LoRa / Meshtastic Radio**

- **LoRa Node (Heltec WiFi LoRa 32 V3 - 915 MHz)**: Can be ordered for **$32.57 CAD** on Amazon Canada or via [Newegg Canada](https://www.newegg.ca/p/3C6-02X3-00CT0). Ensure the chosen option explicitly states 902–928 MHz compatibility for use with Canadian frequencies. \[5\] 

## **1.5 Weatherproofing and Mounting**

- **IP65 Weatherproof Enclosure**: The Hammond 1554 series is manufactured in Canada and can be filtered by specific layout dimension bounds directly via [DigiKey Canada's Hammond Portal](https://www.digikey.ca/en/product-highlight/h/hammond/1554-1555-series) or through regional wholesale supply channels like [Electro Sonic Canada](https://www.e-sonic.com/en/suppliers/hammond-canada-1698/). \[6, 7\] 

**Would you like help mapping out alternative dual-band WiFi hardware if any of these processing units or adapters go out of stock?**


\[1\] [https://www.pishop.ca](https://www.pishop.ca/product/raspberry-pi-4-model-b-4gb/)

\[2\] [https://www.amazon.ca](https://www.amazon.ca/Wireless-Connector-Amplifier-Tupavco-TP551/dp/B07YGPDPW8)

\[3\] [https://www.mouser.ca](https://www.mouser.ca/ProductDetail/Mini-Circuits/MSW-2-20%2B?qs=xZ%2FP%252Ba9zWqbkBcBeVIejhQ%3D%3D)

\[4\] [https://www.amazon.ca](https://www.amazon.ca/AWUS036NH-Network-Drive-Free-Wireless-Penetration/dp/B09G8CZBX1)

\[5\] [https://www.newegg.ca](https://www.newegg.ca/p/3C6-02X3-00CT0)

\[6\] [https://www.digikey.ca](https://www.digikey.ca/en/product-highlight/h/hammond/1554-1555-series)

\[7\] [https://www.e-sonic.com](https://www.e-sonic.com/en/suppliers/hammond-canada-1698/)

