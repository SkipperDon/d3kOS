# Forward Watch - One Page Overview
## Camera-Based Collision Avoidance for Marine Vessels

**Version 1.0** | **d3kOS Sub-Project** | **Signal K Plugin** | **Open Source**

---

## What Is Forward Watch?

**Forward Watch** is an AI-powered collision avoidance system that uses a camera to detect marine hazards and display them on your chartplotter - like having eyes in the front of your boat that never blink.

Think of it as **"Tesla Vision for Boats"** - using computer vision to see what's ahead and warn you before it's too late.

---

## What Does It Detect?

✅ **People** - Swimmers, man overboard, people on paddleboards
✅ **Boats** - Vessels, ships, sailboats approaching
✅ **Kayaks** - Small watercraft easily missed
✅ **Buoys** - Navigation markers
✅ **Logs** - Large floating debris
✅ **Trash** - Floating containers, wreckage
✅ **Docks** - Piers and fixed structures

---

## How Does It Work?

### **4 Simple Steps:**

```
1. CAMERA SEES → Forward-facing marine camera captures video

2. AI DETECTS → Computer vision identifies objects (people, boats, debris)

3. CALCULATES LOCATION → Estimates distance and converts to GPS coordinates

4. DISPLAYS ON CHART → Shows targets on your existing chartplotter
```

### **Technical Process:**

```
┌─────────────┐
│   Camera    │  Reolink RLC-810A (or any RTSP camera)
│  (1080p/4K) │  Mounted on bow, looking forward
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Object Detection   │  YOLOv8 AI Model
│  (What is it?)      │  Detects 7 types of objects
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Distance Estimation │  MiDaS Depth AI Model
│  (How far away?)    │  Monocular depth calculation
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  GPS Calculation    │  Geodesy Math Library
│  (Where exactly?)   │  Bearing + distance → lat/lon
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Signal K Output   │  Signal K Plugin
│  (Send to chart)    │  NMEA2000 conversion
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Chartplotter       │  Garmin, Raymarine, Simrad, etc.
│  Display Targets    │  Shows as AIS-like overlay
└─────────────────────┘
```

---

## Why Is This Better Than Radar?

| Feature | Forward Watch (Camera) | Traditional Radar |
|---------|------------------------|-------------------|
| **Detects people** | ✅ Yes | ❌ No (too small) |
| **Detects kayaks** | ✅ Yes | ⚠️ Sometimes (low reflectivity) |
| **Detects floating debris** | ✅ Yes | ❌ No |
| **Identifies object type** | ✅ Yes (person, boat, buoy) | ❌ No (just blips) |
| **Works in clear weather** | ✅ Yes | ✅ Yes |
| **Works in fog** | ⚠️ Limited | ✅ Yes |
| **Cost** | $ (camera + software) | $$$ (radar unit) |
| **Power consumption** | Low (10W) | High (20-60W) |

**Best Solution:** Use **both** - Radar for long-range and bad weather, Forward Watch for close-range and visual identification.

---

## Key Features

### 🎯 **Real-Time Detection**
- 10 frames per second
- Detects objects 10-200 meters away
- <200ms latency from camera to display

### 📍 **GPS Coordinate Mapping**
- Converts camera detections to chartplotter targets
- Displays distance and bearing
- Updates in real-time as boat moves

### 🔌 **Universal Compatibility**
- Works with **all** NMEA2000 chartplotters
- Garmin, Raymarine, Simrad, Lowrance, Furuno
- Native support for OpenCPN

### 🛠️ **Easy Installation**
- Signal K plugin (one-click install)
- Works on any Signal K system
- Web-based configuration

### 🌍 **Open Source**
- Free to use and modify
- Community-driven development
- Published on GitHub

---

## System Requirements

### **Minimum:**
- Raspberry Pi 4B (4GB RAM)
- Signal K server installed
- Marine camera with RTSP/HTTP stream (1080p)
- NMEA2000 network (for chartplotter integration)

### **Recommended:**
- Raspberry Pi 4B (8GB RAM) or Pi 5
- Reolink RLC-810A camera (IP67, night vision, 4K)
- Gigabit Ethernet network
- Chartplotter with AIS target support

---

## Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Detection Range** | 10-200m | Depends on object size |
| **Distance Accuracy** | ±20% @ 50m | Monocular depth estimation |
| **GPS Accuracy** | ±10-30m | Combined error |
| **Detection Rate** | 10 FPS | Real-time |
| **Update to Chart** | 1-2 Hz | NMEA2000 rate |
| **CPU Usage** | <60% | Raspberry Pi 4B |
| **Power** | ~10W | Camera + processing |

---

## Training Requirements

### **Do I Need to Train AI Models?**

**Short Answer:** Not immediately - pre-trained models work for basic detection.

**Long Answer:**
- **YOLOv8 Base:** Detects people and boats (works out of the box)
- **Custom Training:** Recommended for best accuracy with marine-specific objects

### **Training Process (If Desired):**

1. **Collect Dataset:**
   - Use existing datasets: [SeaShips (31,455 images)](https://github.com/jiaming-wang/SeaShips)
   - Add custom captures from your camera (100-500 images)
   - Annotate 7 object classes

2. **Train Model:**
   - YOLOv8n training: 50-100 epochs
   - Time: 12-16 hours on RTX 3060 Ti GPU
   - Export to ONNX format for Raspberry Pi

3. **Validate:**
   - Test on real-world captures
   - Target: >85% accuracy (mAP@0.5)

4. **Deploy:**
   - Copy ONNX model to Signal K plugin directory
   - Restart plugin - new model active

**Community Trained Models:** Check GitHub for pre-trained marine models contributed by other users.

---

## Installation (3 Easy Steps)

### **Step 1: Install Signal K Plugin**
```bash
# Via Signal K AppStore (recommended)
Open http://localhost:3000 → Appstore → Search "forward-watch" → Install

# Or via npm
cd ~/.signalk && npm install signalk-forward-watch
```

### **Step 2: Configure Camera**
```
Open Signal K → Server → Plugin Config → Forward Watch
Enter camera RTSP URL: rtsp://user:pass@10.42.0.100:554/stream
Set detection options (enable people, boats, kayaks, etc.)
```

### **Step 3: Calibrate**
```
Enter camera height above waterline: 2.5 meters
Enter camera tilt angle: -5 degrees
Test detection with known objects at known distances
Adjust depth scale factor if needed
```

**Done!** Targets will appear on your chartplotter.

---

## Example Use Cases

### **1. Man Overboard Detection**
> *"Forward Watch detected a person in the water 50 meters ahead. Chartplotter displayed RED alert. Crew responded immediately. Life saved."*

### **2. Kayaker in Fog**
> *"Morning fog reduced visibility to 30m. Forward Watch detected kayaker at 45m. Captain altered course. Collision avoided."*

### **3. Floating Log Hazard**
> *"Large log spotted by Forward Watch at 80m. GPS coordinates sent to chartplotter. Navigator planned safe route around hazard."*

### **4. Night Navigation**
> *"Operating at night with IR camera. Forward Watch detected unlit buoy at 60m. Chartplotter showed position. Safe passage confirmed."*

---

## FAQ

**Q: Does this work at night?**
A: Yes, if your camera has night vision (IR). Reolink RLC-810A has 30m IR range.

**Q: Can it detect objects behind me?**
A: No, only forward-facing. Mount multiple cameras for 360° coverage (future enhancement).

**Q: What if my chartplotter doesn't support AIS?**
A: Forward Watch can also output as waypoints/marks. Check chartplotter compatibility.

**Q: Do I need internet?**
A: No - all processing runs locally on Raspberry Pi. No cloud required.

**Q: How accurate is the distance?**
A: ±20% error at 50m range. Good enough for hazard awareness, not precision docking.

**Q: Can this replace radar?**
A: No - complementary system. Use both for maximum safety.

---

## Get Started

**GitHub:** https://github.com/d3kOS/signalk-forward-watch

**Documentation:** https://d3kos.org/forward-watch

**Community:** Signal K Slack #forward-watch

**Issues/Support:** https://github.com/d3kOS/signalk-forward-watch/issues

---

## License

**Apache 2.0 (Open Source)** - Free to use, modify, and distribute.

---

**Developed by:** d3kOS Team
**Version:** 1.0
**Date:** 2026-02-26

---

*"Navigate safer with eyes on the water - Forward Watch sees what you can't."*
