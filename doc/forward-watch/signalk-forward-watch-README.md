# Forward Watch

**Camera-Based Collision Avoidance System for Marine Vessels**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Signal K Plugin](https://img.shields.io/badge/Signal%20K-Plugin-00A0E0.svg)](https://signalk.org/)
[![npm version](https://badge.fury.io/js/signalk-forward-watch.svg)](https://www.npmjs.com/package/signalk-forward-watch)

> **AI-powered object detection that displays marine hazards on your chartplotter in real-time.**

Like having Tesla Vision for your boat - detects people, vessels, debris, and displays them on your existing chartplotter.

---

## ✨ Features

- 🎯 **Real-Time Detection** - Identifies 7 types of marine hazards at 10 FPS
- 📍 **GPS Coordinate Mapping** - Converts camera detections to chartplotter targets
- 🔌 **Universal Compatibility** - Works with all NMEA2000 chartplotters (Garmin, Raymarine, Simrad, etc.)
- 🌐 **Open Source** - Apache 2.0 license, community-driven
- 🛠️ **Easy Installation** - Signal K plugin, one-click install
- 🌙 **Night Vision Support** - Works with IR cameras in darkness

---

## 🚢 What Does It Detect?

| Object | Description | Safety Priority |
|--------|-------------|-----------------|
| 👤 **People** | Swimmers, man overboard, paddleboarders | Critical |
| ⛵ **Boats** | Vessels, ships, sailboats | High |
| 🛶 **Kayaks** | Small watercraft, canoes | High |
| 🟡 **Buoys** | Navigation markers, mooring buoys | Medium |
| 🪵 **Logs** | Large floating timber, debris | High |
| 🗑️ **Trash** | Floating containers, wreckage | Medium |
| 🏗️ **Docks** | Piers, marinas, fixed structures | Medium |

---

## 🎬 How It Works

```
┌──────────────┐
│    Camera    │ → Forward-facing marine camera (RTSP/HTTP)
└──────┬───────┘
       ↓
┌──────────────┐
│  AI Detection│ → YOLOv8 identifies objects
└──────┬───────┘
       ↓
┌──────────────┐
│   Distance   │ → MiDaS estimates depth (meters)
└──────┬───────┘
       ↓
┌──────────────┐
│ GPS Mapping  │ → Converts to latitude/longitude
└──────┬───────┘
       ↓
┌──────────────┐
│  Signal K    │ → Outputs NMEA2000 targets
└──────┬───────┘
       ↓
┌──────────────┐
│ Chartplotter │ → Displays as AIS-like overlay
└──────────────┘
```

**Detection → Display in <200ms**

---

## 📦 Installation

### Prerequisites

- Signal K Server (Node.js 18+)
- Marine camera with RTSP or HTTP stream
- Raspberry Pi 4B (4GB+ RAM) or similar
- NMEA2000 network (for chartplotter integration)

### Install via Signal K AppStore (Recommended)

1. Open Signal K web interface: `http://localhost:3000`
2. Navigate to **Appstore** → **Available**
3. Search for **"forward-watch"**
4. Click **Install**
5. Restart Signal K server
6. Configure in **Server** → **Plugin Config** → **Forward Watch**

### Install via npm

```bash
cd ~/.signalk
npm install signalk-forward-watch
sudo systemctl restart signalk
```

### Manual Installation (Development)

```bash
git clone https://github.com/d3kOS/signalk-forward-watch.git
cd signalk-forward-watch
npm install
npm link
cd ~/.signalk
npm link signalk-forward-watch
sudo systemctl restart signalk
```

---

## ⚙️ Configuration

### Basic Setup

1. **Camera URL:**
   ```
   rtsp://username:password@camera-ip:554/stream
   ```
   Example: `rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_main`

2. **Enable Object Classes:**
   - ✅ People
   - ✅ Boats
   - ✅ Kayaks
   - ✅ Buoys
   - ✅ Logs
   - ✅ Debris
   - ⬜ Docks (optional)

3. **Detection Settings:**
   - Confidence threshold: `0.5` (50%)
   - Max detection range: `200` meters
   - Update rate: `1.0` Hz

### Calibration

Required for accurate distance measurement:

```json
{
  "calibration": {
    "cameraHeight": 2.5,        // meters above waterline
    "cameraTilt": -5,           // degrees (negative = pointing down)
    "fieldOfView": 107,         // degrees horizontal
    "depthScaleFactor": 1.0     // adjust after testing
  }
}
```

**Calibration Steps:**
1. Measure camera height above waterline
2. Measure camera tilt angle with level/inclinometer
3. Place test object at known distance (e.g., 25m, 50m)
4. Run detection and compare estimated vs actual distance
5. Adjust `depthScaleFactor` if needed (e.g., 1.2 if distances are 20% short)

---

## 🎯 Supported Chartplotters

| Brand | Models | Compatibility | Display Type |
|-------|--------|---------------|--------------|
| **Garmin** | GPSMAP, Echomap, Quatix | ✅ Full | AIS-like targets |
| **Raymarine** | Axiom, Element, Dragonfly | ✅ Full | AIS-like targets |
| **Simrad** | NSS evo3, GO, Cruise | ✅ Full | AIS-like targets |
| **Lowrance** | HDS Live, Elite FS | ✅ Full | AIS-like targets |
| **Furuno** | NavNet TZtouch, GP | ✅ Full | AIS-like targets |
| **OpenCPN** | All versions | ✅ Native | Signal K direct |
| **B&G** | Vulcan, Zeus | ✅ Full | AIS-like targets |

**How it appears:** Targets show as AIS vessels with custom names like `FWD-PERSON-42m` (Forward Watch detected person at 42 meters).

---

## 📊 Performance

| Metric | Specification |
|--------|--------------|
| **Detection Rate** | 10 FPS (frames per second) |
| **Detection Range** | 10-200 meters (object size dependent) |
| **Distance Accuracy** | ±20% @ 10-50m, ±40% @ 50-100m |
| **GPS Accuracy** | ±10-30 meters (combined error) |
| **Update Rate** | 1-2 Hz to chartplotter |
| **Latency** | <200ms (camera → chartplotter) |
| **CPU Usage** | <60% (Raspberry Pi 4B) |
| **Memory Usage** | <2GB |
| **Power** | ~10W (camera + processing) |

---

## 🧠 AI Models

### YOLOv8-Marine (Object Detection)

**Model:** YOLOv8n (Nano)
**Size:** 6MB (base) / 25MB (marine-trained)
**Format:** ONNX
**Classes:** 7 (people, boats, kayaks, buoys, logs, debris, docks)
**Inference:** 10+ FPS on Raspberry Pi 4B

**Training (Optional):**
- Use pre-trained base model (works immediately)
- Or train custom model for better accuracy:
  - Dataset: [SeaShips](https://github.com/jiaming-wang/SeaShips) (31,455 images)
  - Training time: 12-16 hours on RTX 3060 Ti
  - Export to ONNX format

### MiDaS v3.0 (Depth Estimation)

**Model:** MiDaS v3.0 (Intel)
**Size:** 100MB
**Format:** ONNX
**Purpose:** Monocular depth estimation (single camera distance)
**Inference:** 5+ FPS on Raspberry Pi 4B
**Accuracy:** ±20% @ 50m range

**No training required** - pre-trained model works out of the box.

---

## 📸 Recommended Cameras

### **Reolink RLC-810A** (Recommended)

- **Resolution:** 4K (3840×2160)
- **Night Vision:** IR LEDs, 30m range
- **Waterproof:** IP67 rated (marine environment)
- **Field of View:** 107° horizontal
- **RTSP:** Yes (no subscription required)
- **Price:** ~$90 USD
- **Mount:** Standard 1/4"-20 thread

### **Alternative Options:**

- **Hikvision DS-2CD2xxx** - ONVIF/RTSP support
- **Axis M10xx Series** - Professional quality
- **Generic IP Cameras** - Any with RTSP/HTTP stream

**Requirements:**
- Minimum 1080p resolution
- RTSP or HTTP stream (no cloud-only cameras)
- Outdoor/weatherproof rating recommended
- Fixed focus lens (not PTZ) for Forward Watch

---

## 🛠️ Troubleshooting

### No objects detected
- ✅ Check camera stream is accessible (test with VLC)
- ✅ Verify camera URL and credentials correct
- ✅ Lower confidence threshold to 0.3
- ✅ Ensure objects are within 10-200m range

### Inaccurate distances
- ✅ Calibrate camera height and tilt angle
- ✅ Adjust depth scale factor (test with known distances)
- ✅ Verify camera is level and forward-facing

### No chartplotter display
- ✅ Check NMEA2000 network connected
- ✅ Enable Signal K NMEA2000 plugin
- ✅ Verify chartplotter supports AIS targets
- ✅ Try waypoint output mode instead

### Low FPS / Performance issues
- ✅ Reduce camera resolution (4K → 1080p)
- ✅ Lower detection rate (10 FPS → 5 FPS)
- ✅ Disable unused object classes
- ✅ Check CPU usage: `htop`

**Debug Logs:**
```bash
tail -f ~/.signalk/logs/signalk.log | grep forward-watch
```

---

## 📚 Documentation

- **[Technical Specification](doc/FORWARD_WATCH_SPECIFICATION.md)** - Detailed architecture and implementation
- **[One-Page Overview](doc/FORWARD_WATCH_ONEPAGER.md)** - Quick introduction for users
- **[Training Guide](doc/FORWARD_WATCH_TRAINING.md)** - How to train custom AI models
- **[API Reference](doc/API.md)** - Signal K delta message format
- **[Calibration Guide](doc/CALIBRATION.md)** - Distance accuracy optimization

---

## 🤝 Contributing

We welcome contributions from the community!

**Ways to contribute:**
- 🐛 Report bugs via [GitHub Issues](https://github.com/d3kOS/signalk-forward-watch/issues)
- 💡 Suggest features or improvements
- 🔧 Submit pull requests
- 📝 Improve documentation
- 🎓 Share trained models or datasets
- 💬 Help others in Signal K Slack #forward-watch

**Development Setup:**
```bash
git clone https://github.com/d3kOS/signalk-forward-watch.git
cd signalk-forward-watch
npm install
npm test
npm link
```

**Code Style:** JavaScript Standard Style
**Testing:** Jest (run `npm test`)
**Commit Format:** Conventional Commits

---

## 📄 License

**Apache License 2.0**

Copyright 2026 d3kOS Development Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## 🙏 Acknowledgments

**Datasets:**
- [SeaShips Dataset](https://github.com/jiaming-wang/SeaShips) by Wuhan University
- [Marine Surveillance Dataset](https://universe.roboflow.com/marine-cv6x4/seaships-zhqhn) by Roboflow
- [Floating Debris Dataset](https://www.nature.com/articles/s41597-025-04594-9)

**Libraries:**
- [YOLOv8](https://github.com/ultralytics/ultralytics) by Ultralytics
- [MiDaS](https://github.com/isl-org/MiDaS) by Intel ISL
- [Geodesy](https://www.npmjs.com/package/geodesy) by Chris Veness
- [ONNX Runtime](https://onnxruntime.ai/) by Microsoft

**Research:**
- [Marine Vessel Tracking](https://www.scitepress.org/PublishedPapers/2021/105160/105160.pdf) (Tobias Jacob, 2021)
- [Distance Estimation for Maritime Traffic](https://www.mdpi.com/2077-1312/12/1/78) (2024)

**Platforms:**
- [Signal K](https://signalk.org/) - Marine data standard
- [d3kOS](https://github.com/d3kOS/d3kOS) - Marine operating system

---

## 📞 Support

**GitHub Issues:** https://github.com/d3kOS/signalk-forward-watch/issues

**Signal K Slack:** #forward-watch channel

**Email:** support@d3kos.org

**Website:** https://d3kos.org/forward-watch

---

## 🗺️ Roadmap

### Version 1.1 (Q2 2026)
- [ ] Object tracking with persistent IDs
- [ ] Collision prediction (ETA to intercept)
- [ ] Audible proximity alerts
- [ ] Web UI dashboard with live view

### Version 2.0 (Q3 2026)
- [ ] Multi-camera support (360° coverage)
- [ ] Vessel type classification
- [ ] AIS data fusion
- [ ] Hardware acceleration (Coral TPU, Intel NCS2)

### Future
- [ ] Stereo camera support (accurate depth)
- [ ] Wake detection
- [ ] Replay mode
- [ ] Mobile app integration

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=d3kOS/signalk-forward-watch&type=Date)](https://star-history.com/#d3kOS/signalk-forward-watch&Date)

---

**Made with ❤️ by the d3kOS Team**

*Navigate safer - Forward Watch sees what you can't.*
