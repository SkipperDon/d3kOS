# WiFi Marine Proximity Radar — R&D Framework
### Project: WiBoat Sensor — WiFi CSI Sensing → SignalK/AvNav Overlay
**Version 0.1 | May 2026 | Status: Research & Feasibility**

---

## 1. Project Vision

Build an open-source, boat-mounted WiFi sensing system that detects nearby vessels and
objects using reflected 2.4 GHz WiFi signals (Channel State Information — CSI), processes
them into range/bearing contact data, and injects those contacts as synthetic targets into
**SignalK** (and optionally **AvNav**) for display as a proximity radar overlay.

**Goal:** Short-range collision avoidance awareness out to ~150–250 m, particularly useful
in fog, darkness, or congested anchorages where non-AIS vessels (dinghies, kayaks, unlicensed
powerboats) are invisible to chart plotters.

---

## 2. Open Source Building Blocks Found

### 2.1 CSI Extraction Layer

| Project | Hardware | Notes | Link |
|---|---|---|---|
| **nexmon_csi** (seemoo-lab) | Raspberry Pi 3B+, 4B | Gold standard. Patches Broadcom WiFi firmware to expose raw CSI per frame. Outputs UDP packets. | github.com/seemoo-lab/nexmon_csi |
| **nexmonster/nexmon_csi** | RPi 3B+, 4B | Easier install wrapper with pre-compiled binaries. RSSI + Frame Control included. | github.com/nexmonster/nexmon_csi |
| **picsi** | RPi | Python tool — one-command install of nexmon_csi. Manages profiles, forwards CSI over UDP to external machine. | github.com/nexmonster/picsi |
| **WirelessEye** | RPi 4B (kernel 5.10) | Qt GUI for real-time CSI display + TCP server. Good for bench testing your signal pipeline. | github.com/pkindt/WirelessEye |
| **esp-csi** (Espressif official) | ESP32 all variants | Official Espressif CSI SDK. Cheaper than RPi. ESP32-S3 recommended. Built-in human/motion detection demos. | github.com/espressif/esp-csi |
| **wifi-3d-fusion** | ESP32/Nexmon | Deep learning pose from CSI. Shows the signal processing pipeline clearly — useful reference. | github.com/MaliosDark/wifi-3d-fusion |

### 2.2 SignalK Integration Layer

| Project | Function | Notes | Link |
|---|---|---|---|
| **signalk-server** | Core hub | Node.js server. Multiplexes NMEA0183, NMEA2000, custom plugins. Runs on RPi. WebSocket + REST API. | github.com/SignalK/signalk-server |
| **signalk-radar** (wdantuma) | Radar server | Golang radar server implementing JSON REST + protobuf WebSocket API. SignalK plugin proxies the radar API. **This is the key integration point.** | github.com/wdantuma/signalk-radar |
| **freeboard-sk** | Chart plotter UI | Has **initial RADAR API support** already built in. Can display radar sweep overlays from signalk-radar. | github.com/SignalK/freeboard-sk |
| **KIP** | Instrument panel | Includes an **AIS Radar widget** with range rings and target details. Could be adapted for WiFi contacts. | github.com/mxtommy/Kip |

### 2.3 AvNav Integration Layer

AvNav (wellenvogel/avnav) supports Python + JavaScript plugins via a clean API:
- **`avnav_api.py`** — plugin can write arbitrary key/value data into AvNav's store
- Plugins can emit synthetic NMEA sentences (including `!AIVDM` AIS sentences)
- JavaScript overlay layer can draw custom symbols on the chart
- **Easiest path:** Plugin emits fake AIS NMEA sentences → AvNav treats contacts as AIS targets

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HARDWARE (Mast/Flybridge Mount)              │
│                                                                 │
│  [ANT-1]──┐                          ┌──[ANT-3]                │
│  Omni     │   ┌──────────────────┐   │  Omni                  │
│  2.4GHz   ├──▶│  ALFA AWUS036NH  │◀──┤  2.4GHz               │
│           │   │  (TX/RX #1)      │   │                        │
│  [ANT-2]──┘   └────────┬─────────┘   └──[ANT-4]               │
│  Omni (90°            │              Omni (90°                 │
│  offset)              │              offset)                   │
│                        │  USB 3.0                              │
│               ┌────────▼─────────┐                             │
│               │  WiFi Amplifier  │  ALFA 800mW amp             │
│               │  TX boost stage  │  +27dBm output              │
│               └────────┬─────────┘                             │
│                        │                                       │
│               ┌────────▼─────────────────────────────────┐    │
│               │         Raspberry Pi 4B (4GB)            │    │
│               │  ┌────────────────────────────────────┐  │    │
│               │  │  nexmon_csi firmware patch         │  │    │
│               │  │  CSI packets → UDP port 5500       │  │    │
│               │  └───────────────┬────────────────────┘  │    │
│               │                  │                        │    │
│               │  ┌───────────────▼────────────────────┐  │    │
│               │  │  wiboat-csi-processor (Python)     │  │    │
│               │  │  • MUSIC/ESPRIT AoA algorithm      │  │    │
│               │  │  • ToF range estimation            │  │    │
│               │  │  • Clutter filter (wave rejection) │  │    │
│               │  │  • Contact tracker (Kalman)        │  │    │
│               │  └───────────────┬────────────────────┘  │    │
│               │                  │                        │    │
│               │  ┌───────────────▼────────────────────┐  │    │
│               │  │  SignalK Server + signalk-radar     │  │    │
│               │  │  plugin                             │  │    │
│               │  │  → freeboard-sk radar overlay      │  │    │
│               │  │  → AvNav AIS injection (NMEA)      │  │    │
│               │  └────────────────────────────────────┘  │    │
│               └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Hardware Bill of Materials

### 4.1 Core Compute

| Component | Recommended Model | Notes | Est. Cost |
|---|---|---|---|
| Single Board Computer | **Raspberry Pi 4B — 4GB** | Runs nexmon_csi, SignalK, and signal processing simultaneously. Use kernel 5.10 for nexmon compatibility. | ~$55 |
| Storage | 32GB A2-class microSD | Samsung Pro Endurance recommended for continuous write workloads | ~$12 |
| Power Supply | 12V→5V 3A DC-DC (marine rated) | Feed from boat's 12V bus. Use fused spur. | ~$15 |

### 4.2 WiFi Adapters (CSI-capable)

| Adapter | Chip | TX Power | CSI Support | Notes |
|---|---|---|---|---|
| **ALFA AWUS036NH** | Ralink RT3070 | 2000mW (2W) | Via nexmon on RPi internal | High power. Good outdoor range. RP-SMA connector for external antenna. Best starting point. |
| **ALFA AWUS036ACH** | RTL8812AU | 1900mW | Limited — use RPi internal BCM chip for CSI | Good as secondary TX injector |
| **RPi 4B internal WiFi** | BCM43455 | ~100mW | **Yes — nexmon_csi primary target** | This is what nexmon patches. External adapters handle power, internal chip does CSI extraction. |

> **Architecture note:** Use the RPi's **internal BCM43455** for CSI extraction (nexmon patches
> this chip). Use the **ALFA AWUS036NH** as the high-power frame injector/transmitter. The
> internal chip receives the reflected frames and extracts CSI. This is the standard bistatic
> WiFi radar configuration.

### 4.3 RF Amplification

| Component | Model | Spec | Notes |
|---|---|---|---|
| TX Amplifier | **ALFA WiFi Amplifier** | 800mW input → 2.5W EIRP with 5dBi antenna | Inline amplifier. USB powered. Fits between adapter and antenna. ~$40 |
| Alternative | **TP-LINK CPE210 outdoor AP** | 100mW with 9dBi integrated antenna | If you want a self-contained TX node rather than discrete components. Outdoor weatherproof. |

> **Regulatory note (Canada — ISED):** Maximum EIRP for 2.4 GHz (ISM band) is **4W (36 dBm)**
> under RSS-210. Your 2.5W EIRP target is within limits. Do not exceed 36 dBm EIRP.
> No licence required for 2.4 GHz ISM band operation at these power levels.

### 4.4 Antenna Configuration — Recommended Setup

**Minimum viable (Phase 1): 2-antenna array**

```
        BOW
         │
   [ANT-A]  [ANT-B]
    omni    omni
   ├──────────────┤
     baseline: 0.6m
```

| Antenna | Model | Gain | Mount |
|---|---|---|---|
| ANT-A & ANT-B | **Tupavco TP551 or equivalent** | 12 dBi | Fibreglass weatherproof omni. N-female. Mount at masthead or radar arch. Vertical polarisation. |
| Alternative (budget) | ALFA AOA-2409TF | 9 dBi | Fibreglass omni. Good marine option. |

**Expanded array (Phase 2): 4-antenna MIMO**

Add two more antennas at 90° offsets for full 360° bearing coverage and reduced ambiguity.
Baseline: 0.5–0.6m between adjacent antennas (half-wavelength at 2.4 GHz ≈ 6.25 cm for
grating lobe avoidance, but wider baselines improve resolution at cost of ambiguity).

**Practical marine baseline recommendation: 30–60 cm** — balances resolution against
installation on a typical radar arch.

### 4.5 Cabling

| Item | Spec |
|---|---|
| Antenna cable | LMR-400 or equivalent low-loss coax. Minimise run length. Every metre of RG-58 costs ~0.5 dB. |
| Connectors | N-male to RP-SMA adapters. Self-amalgamating tape all outdoor joints. |
| USB extension | USB 3.0 active extension if RPi is below deck — max 5m passive, 15m active. |

---

## 5. Software Stack

### 5.1 Layer 1 — CSI Extraction (on RPi)

```bash
# Install nexmon_csi via picsi (easiest path)
pip3 install picsi
picsi install          # downloads pre-compiled firmware for your kernel
picsi enable
picsi up 6/20          # channel 6, 20MHz bandwidth for 2.4GHz

# CSI packets arrive as UDP on port 5500
# Capture: tcpdump -i wlan0 dst port 5500 -w csi_capture.pcap
```

**Key parameters to tune:**
- Channel: 1, 6, or 11 (non-overlapping 2.4 GHz channels)
- Bandwidth: 20 MHz for Phase 1 (finer ToF resolution with 40 MHz later)
- MAC filter: set to broadcast to capture all frames

### 5.2 Layer 2 — Signal Processing (Python)

**Core algorithms needed:**

```
CSI Packet (UDP)
    │
    ▼
csiread library          # Parse nexmon CSI binary format
    │                    # pip install csiread
    ▼
Phase/Amplitude Extract  # Per-subcarrier complex values
    │                    # 52 subcarriers @ 20MHz
    ▼
Sanitisation             # Remove phase jumps, interpolate missing subcarriers
    │
    ▼
┌───────────────────────────────────┐
│  Range Estimation                 │
│  Method: IFFT on subcarrier phase │
│  ToF = phase_slope / (2π·Δf)     │
│  Range = ToF × c / 2             │
└───────────────┬───────────────────┘
                │
┌───────────────▼───────────────────┐
│  Bearing Estimation               │
│  Method: MUSIC algorithm on       │
│  phase difference between ANT-A   │
│  and ANT-B                        │
│  AoA = arcsin(Δφ·λ / 2π·d)       │
└───────────────┬───────────────────┘
                │
┌───────────────▼───────────────────┐
│  Clutter Rejection                │
│  • Static background subtraction │
│  • Wave motion frequency filter  │
│    (waves: 0.1–0.5 Hz)           │
│  • Doppler shift detection       │
└───────────────┬───────────────────┘
                │
┌───────────────▼───────────────────┐
│  Contact Tracker                  │
│  Kalman filter per detected       │
│  contact. Output: (range, bearing,│
│  Δrange, confidence_score)        │
└───────────────┬───────────────────┘
                │
                ▼
        Contact List JSON
```

**Key Python libraries:**
- `csiread` — parse nexmon CSI packets
- `numpy`, `scipy.signal` — FFT, MUSIC algorithm
- `filterpy` — Kalman filter tracker
- `socket` / `asyncio` — UDP receive loop

### 5.3 Layer 3 — Navigation Integration

#### Path A: SignalK (Recommended primary path)

The **signalk-radar** project (wdantuma) already implements the Radar API that **freeboard-sk**
supports. The integration approach:

1. **Write a SignalK plugin** (Node.js) that:
   - Subscribes to your Python processor's output (via local WebSocket or named pipe)
   - Publishes contacts to SignalK's vessels path as synthetic radar returns
   - Implements the signalk-radar JSON REST API so freeboard-sk can render the radar sweep

2. **freeboard-sk** already has initial RADAR API support — contacts will appear as a
   radar overlay on the chart.

```javascript
// SignalK plugin skeleton — wiboat-signalk-plugin/index.js
module.exports = function(app) {
  const plugin = {}
  plugin.id = 'wiboat-radar'
  plugin.name = 'WiBoat WiFi Radar'

  plugin.start = function(options) {
    // Connect to Python processor output
    const ws = new WebSocket('ws://localhost:8765')
    ws.on('message', (data) => {
      const contacts = JSON.parse(data)
      contacts.forEach(contact => {
        app.handleMessage(plugin.id, {
          updates: [{
            values: [{
              path: `environment.wiboat.contacts.${contact.id}`,
              value: {
                range: contact.range_m,
                bearing: contact.bearing_deg,
                confidence: contact.confidence
              }
            }]
          }]
        })
      })
    })
  }
  return plugin
}
```

#### Path B: AvNav (Parallel integration)

AvNav's Python plugin API allows injection of NMEA sentences. Synthetic AIS targets
are the simplest approach — AvNav already knows how to display AIS symbols.

```python
# avnav plugin: wiboat_plugin/plugin.py
import math, socket, json

class Plugin:
    CONFIG = []

    def __init__(self, api):
        self.api = api
        self.seq = 0

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', 9876))  # receive from Python processor
        while True:
            data, _ = sock.recvfrom(4096)
            contacts = json.loads(data)
            for c in contacts:
                nmea = self._make_fake_ais(c)
                self.api.addNMEA(nmea, addChecksum=True)

    def _make_fake_ais(self, contact):
        # Synthesise !AIVDM sentence from range/bearing + own position
        # Use MMSI range 970000000-979999999 (SAR transponder range — won't conflict)
        # This gives you a dot on the chart at the computed position
        ...
```

---

## 6. R&D Phases

### Phase 1 — Bench Proof of Concept (Months 1–2)

**Goal:** Prove CSI extraction works and range estimation is feasible.

- [ ] Set up RPi 4B with nexmon_csi via picsi
- [ ] Capture CSI packets with a known reflector (metal sheet) at 10 m, 25 m, 50 m
- [ ] Write Python IFFT range estimator, validate against tape measure
- [ ] Visualise with WirelessEye for real-time sanity checking
- [ ] Document: minimum detectable range, maximum reliable range, noise floor

**Success criterion:** Reliably detect a 1m² metal reflector at 50m range ± 5m accuracy.

### Phase 2 — Direction Finding (Months 2–3)

**Goal:** Add bearing estimation with 2-antenna array.

- [ ] Mount two ALFA AWUS036NH adapters with 12dBi omni antennas, 60cm baseline
- [ ] Implement MUSIC algorithm for AoA from phase difference
- [ ] Validate bearing accuracy against GPS-tracked tender at known positions
- [ ] Add basic Kalman tracker for contact persistence

**Success criterion:** Bearing accuracy ±20° at 100m range.

### Phase 3 — Marine Environment Testing (Months 3–5)

**Goal:** Validate in real marine clutter (waves, spray, wind).

- [ ] Deploy on anchored boat in protected water
- [ ] Test detection of: fibreglass hull, aluminium tender, kayak, buoy
- [ ] Tune clutter rejection filter for wave motion frequency
- [ ] Assess rain/spray degradation
- [ ] Compare detections to visual sightings and AIS targets

**Success criterion:** Detect a fibreglass vessel >7m at 100m range with <30% false positive rate.

### Phase 4 — Navigation Integration (Months 5–7)

**Goal:** Contacts appear on SignalK/AvNav display.

- [ ] Write SignalK plugin consuming Python processor output
- [ ] Validate contacts appear on freeboard-sk radar overlay
- [ ] Write AvNav plugin for parallel display
- [ ] Build simple web dashboard for system status monitoring
- [ ] Package as installable SignalK plugin (npm)

**Success criterion:** End-to-end demo — detected boat appears as symbol on chart plotter.

### Phase 5 — Extended Range (Months 7–12)

**Goal:** Push reliable range toward 200m+ with amplification.

- [ ] Add ALFA 800mW inline amplifier to TX chain
- [ ] Upgrade to 15 dBi outdoor omni antennas
- [ ] Experiment with 4-antenna array for reduced ambiguity + improved bearing
- [ ] Evaluate 5 GHz band for higher bandwidth (better ToF resolution) vs range trade-off
- [ ] Consider SDR (Software Defined Radio) as alternative TX platform for finer control

---

## 7. Realistic Range Expectations

| Configuration | Expected Range (large steel vessel) | Expected Range (fibreglass <10m) |
|---|---|---|
| RPi internal BCM, stock antenna | 20–40 m | 10–20 m |
| + ALFA AWUS036NH, 9dBi omni | 60–100 m | 30–60 m |
| + Inline amplifier, 12dBi omni | 100–180 m | 50–100 m |
| + 15dBi omni, 4-antenna array | 150–250 m | 80–150 m |

*All estimates for open water, LOS conditions. Rain and spray will reduce range 20–40%.*

---

## 8. Key Technical Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Wave clutter masks targets | High | Frequency-domain filtering (waves: 0.1–0.5 Hz, vessels: detectable Doppler shift) |
| Non-metallic hulls (fibreglass) low reflectivity | Medium | Higher TX power + sensitive RX. Accept reduced range for non-metallic targets. |
| Multipath from boat structure | Medium | Antenna placement away from superstructure. MUSIC algorithm handles multipath better than IFFT alone. |
| Regulatory limits cap TX power | Low | 2.5W EIRP well within ISED RSS-210 limits. Document compliance. |
| nexmon_csi kernel compatibility | Medium | Lock kernel version. Don't `apt upgrade` blindly. Use dedicated RPi image. |
| Bearing ambiguity (2-antenna) | Medium | Third antenna resolves left/right ambiguity in Phase 5. |

---

## 9. Useful Reference Repositories

```
Core CSI:
  github.com/seemoo-lab/nexmon_csi         — original nexmon CSI
  github.com/nexmonster/nexmon_csi         — easy install wrapper
  github.com/nexmonster/picsi              — Python installer/manager
  github.com/pkindt/WirelessEye            — real-time CSI visualiser
  github.com/espressif/esp-csi             — ESP32 CSI (cheap TX node option)

Signal Processing:
  github.com/MaliosDark/wifi-3d-fusion     — CSI processing pipeline reference
  github.com/zeroby0/csi-explorer          — CSI plotting tool

Navigation Integration:
  github.com/SignalK/signalk-server        — SignalK hub
  github.com/wdantuma/signalk-radar        — Radar API for SignalK ← KEY
  github.com/SignalK/freeboard-sk          — Chart plotter with radar support
  github.com/mxtommy/Kip                   — Instrument panel with AIS radar widget
  github.com/wellenvogel/avnav             — AvNav (your existing nav software)

Hardware:
  ALFA AWUS036NH — high power WiFi adapter (2W TX)
  Tupavco TP551 / ALFA AOA-2409TF — outdoor weatherproof omni antennas
  ALFA WiFi Amplifier — inline 800mW amplifier
```

---

## 10. Suggested First Steps This Week

1. **Order hardware:** RPi 4B 4GB + 2× ALFA AWUS036NH + 2× 9dBi outdoor omni + LMR-400 cable
2. **Flash RPi** with Raspberry Pi OS (Bullseye, 32-bit) — **do not upgrade kernel** after flash
3. **Run `picsi install`** and confirm you can capture CSI packets with `tcpdump`
4. **Download WirelessEye** and visualise live CSI amplitude on a laptop
5. **Set a fixed reflector** (piece of aluminium sheet) at 10m and prove you see it change when it's moved

> "The best radar is the one actually mounted on your boat."
> Start small. Prove range estimation. Then add bearing. Then integrate. Then amplify.

---

*Document Status: Living R&D framework — update as phases complete.*
*Author: Skipper Don | WiBoat Project | Toronto, ON*
