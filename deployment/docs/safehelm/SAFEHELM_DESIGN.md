# SafeHelm: Production-Ready Maritime Collision Avoidance System

## d3kOS Module — Technical Design v1.0

**Date:** 2026-05-11  
**Author:** d3kOS / AtMyBoat.com  
**Target Platform:** Raspberry Pi 5, d3kOS v0.9.9+  
**Integration:** Signal K → AvNav → pypilot  
**Status:** Design Phase — Pre-Implementation  
**GitHub Target:** `github.com/SkipperDon/d3kOS/services/safehelm/`


## 1. Why This Document Exists

The academic research on maritime collision avoidance describes the problem well. It does not describe a deployable solution. Papers published through 2026 share a common failure: they model the ocean as a clean simulation with perfect sensors, cooperative vessels, and unlimited compute. None of these assumptions hold at sea.

This document provides what the research does not: a complete technical design for a production-ready, COLREGs-aware collision avoidance system that runs on a Raspberry Pi 5, integrates with Signal K and AvNav, and operates safely in the real world — including when sensors fail, vessels do not cooperate, and the captain is asleep.

**This system is different from the research in six critical ways:**

| Research Gap | SafeHelm Solution |
| - | - |
| Assumes sensors always work | Sensor Reliability Layer with confidence scoring and graceful degradation |
| No real-time guarantees | Deterministic 100ms execution loop with watchdog timers |
| Treats boats as point masses | Vessel Dynamics Model using real turn/stop physics |
| Ignores human factors | Human-in-the-Loop design with alarm fatigue prevention |
| No multi-vessel logic | Conflict Graph with priority assignment and deadlock resolution |
| No safety envelope | Control Barrier Functions with hard constraint enforcement |



## 2. What the Research Got Right

Before stating what is missing, credit what holds:

- **CPA/TCPA as the core risk metric** — mathematically sound. Distance alone is meaningless. Geometry and time are everything.

- **COLREGs Rules 13–17** as the decision framework — these are correct. The head-on, crossing, and overtaking classifications are the right starting point.

- **Velocity Obstacle (VO)** as the path planning model — computationally feasible on a Pi 5 and geometrically correct for the problem.

- **AIS as the primary data source** — correct. Any system that ignores AIS is not serious.

- **Ship Domain modelling** — correct framing. The safety bubble is not a circle; it is an asymmetric zone shaped by the vessel's dynamics.

The problem is not the theory. The problem is the assumption that theory is sufficient for deployment.


## 3. The SafeHelm Architecture: 7-Layer Stack

```
┌─────────────────────────────────────────────────────────────────┐  
│  LAYER 7: SAFETY ENVELOPE                                        │  
│  Control Barrier Functions — hard constraints — never violated   │  
├─────────────────────────────────────────────────────────────────┤  
│  LAYER 6: HUMAN INTERFACE                                        │  
│  AvNav widget — voice alerts — one-tap confirm — alarm budget    │  
├─────────────────────────────────────────────────────────────────┤  
│  LAYER 5: MULTI-VESSEL CONFLICT SOLVER                           │  
│  Priority graph — deadlock resolver — cooperative/adversarial    │  
├─────────────────────────────────────────────────────────────────┤  
│  LAYER 4: COLREGs DECISION ENGINE                                │  
│  Situation classifier — give-way/stand-on — maneuver selector    │  
├─────────────────────────────────────────────────────────────────┤  
│  LAYER 3: VESSEL DYNAMICS MODEL                                  │  
│  Turn radius — stopping distance — drift — rudder saturation     │  
├─────────────────────────────────────────────────────────────────┤  
│  LAYER 2: REAL-TIME EXECUTION CORE                               │  
│  100ms deterministic loop — thread isolation — watchdog          │  
├─────────────────────────────────────────────────────────────────┤  
│  LAYER 1: SENSOR FUSION & RELIABILITY                            │  
│  AIS + Camera + GPS + IMU — confidence scoring — degraded modes  │  
└─────────────────────────────────────────────────────────────────┘  
         ↑                                        ↓  
   Signal K (input)                    pypilot (output)  
   Forward Watch (input)               AvNav widget (output)  
   GPS/IMU (input)                     Voice/speaker (output)
```

Data flows upward (raw sensor → decision), commands flow downward (decision → actuator). Each layer has exactly one job. No layer reaches past its neighbour.


## 4. Layer 1: Sensor Fusion and Reliability Engine

### 4.1 The Problem the Research Ignores

Every sensor fails. Cameras wash out in glare. AIS updates stall. GPS drifts near bridges. IMUs develop bias in cold weather. The research assumes clean data. Real deployments do not get clean data.

**A collision avoidance system that fails silently when a sensor degrades is dangerous. It is worse than no system at all.**

### 4.2 Sensor Confidence Scoring

Every data input receives a continuous confidence score (0.0 to 1.0) that decays when data is stale or contradictory and recovers when fresh data arrives.

```
import time  
from dataclasses import dataclass, field  
from typing import Optional  
  
@dataclass  
class SensorReading:  
    value: dict  
    timestamp: float  
    source: str  
    confidence: float = 1.0  
  
class SensorConfidenceTracker:  
    """  
    Tracks confidence for each sensor. Confidence decays over time.  
    Recovery is faster than decay (bias toward trusting fresh data).  
    """  
    DECAY\_RATES = \{  
        'ais':     0.05,   \# per second — AIS updates ~every 10s at close range  
        'camera':  0.20,   \# per second — camera must be near-real-time  
        'gps':     0.02,   \# per second — GPS is usually reliable  
        'imu':     0.10,   \# per second — IMU drift is slow but real  
    \}  
    MINIMUM\_CONFIDENCE = 0.0  
    STALE\_THRESHOLD = 0.3  \# below this = sensor is considered unreliable  
  
    def \_\_init\_\_(self):  
        self.\_scores: dict\[str, float\] = \{\}  
        self.\_last\_update: dict\[str, float\] = \{\}  
  
    def update(self, source: str, timestamp: float) -\> None:  
        now = time.monotonic()  
        self.\_scores\[source\] = 1.0  
        self.\_last\_update\[source\] = now  
  
    def get\_confidence(self, source: str) -\> float:  
        if source not in self.\_scores:  
            return 0.0  
        now = time.monotonic()  
        elapsed = now - self.\_last\_update.get(source, now)  
        decay = self.DECAY\_RATES.get(source, 0.1)  
        score = self.\_scores\[source\] \* (1.0 - decay \* elapsed)  
        return max(self.MINIMUM\_CONFIDENCE, score)  
  
    def is\_reliable(self, source: str) -\> bool:  
        return self.get\_confidence(source) \>= self.STALE\_THRESHOLD
```

### 4.3 Degraded Operation Modes

The system must define explicit operating modes. It must never silently degrade.

| Mode | Active Sensors | Capability | Operator Alert |
| - | - | - | - |
| FULL | AIS + Camera + GPS + IMU | All targets visible | None |
| AIS\_ONLY | AIS + GPS | AIS targets only — "dark" vessels invisible | Yellow banner |
| CAMERA\_ONLY | Camera + GPS | Visual targets only — no MMSI, estimated range | Yellow banner |
| GPS\_ONLY | GPS | Own position only — no target tracking | Red banner + audio |
| DEGRADED | Partial GPS | Limited accuracy — advisory only | Red banner + audio |
| BLIND | None reliable | Safety envelope: emergency stop autopilot | Critical alarm |


```
class OperatingMode:  
    FULL = "FULL"  
    AIS\_ONLY = "AIS\_ONLY"  
    CAMERA\_ONLY = "CAMERA\_ONLY"  
    GPS\_ONLY = "GPS\_ONLY"  
    DEGRADED = "DEGRADED"  
    BLIND = "BLIND"  
  
def determine\_mode(tracker: SensorConfidenceTracker) -\> str:  
    has\_gps = tracker.is\_reliable('gps')  
    has\_ais = tracker.is\_reliable('ais')  
    has\_camera = tracker.is\_reliable('camera')  
    has\_imu = tracker.is\_reliable('imu')  
  
    if not has\_gps:  
        return OperatingMode.BLIND if not has\_ais else OperatingMode.DEGRADED  
    if has\_ais and has\_camera:  
        return OperatingMode.FULL  
    if has\_ais:  
        return OperatingMode.AIS\_ONLY  
    if has\_camera:  
        return OperatingMode.CAMERA\_ONLY  
    return OperatingMode.GPS\_ONLY
```

### 4.4 Camera-to-World Coordinate Transform

The Forward Watch camera sees pixels. The collision avoidance engine needs geographic coordinates. This transform is the bridge. It requires:

- Camera field of view (horizontal and vertical, in degrees)

- Camera mounting angle (pan, tilt relative to bow)

- Own vessel position (lat/lon)

- Own vessel heading (true, from compass)

- Target pixel coordinates from the vision model

- Estimated range (from stereo or monocular depth estimation)

```
import math  
  
def pixel\_to\_bearing(  
    pixel\_x: int,  
    pixel\_y: int,  
    frame\_width: int,  
    frame\_height: int,  
    hfov\_deg: float,  
    camera\_pan\_deg: float,  
    own\_heading\_deg: float  
) -\> float:  
    """  
    Convert pixel position to true bearing from own vessel.  
    pixel\_x: horizontal pixel, 0=left edge  
    hfov\_deg: camera horizontal field of view  
    camera\_pan\_deg: camera offset from bow (positive = starboard)  
    own\_heading\_deg: vessel true heading  
    Returns: true bearing to target (0-360)  
    """  
    pixels\_from\_center = pixel\_x - (frame\_width / 2)  
    angle\_from\_camera\_center = (pixels\_from\_center / frame\_width) \* hfov\_deg  
    relative\_bearing = camera\_pan\_deg + angle\_from\_camera\_center  
    true\_bearing = (own\_heading\_deg + relative\_bearing) % 360  
    return true\_bearing  
  
def bearing\_distance\_to\_latlon(  
    own\_lat: float,  
    own\_lon: float,  
    bearing\_deg: float,  
    distance\_nm: float  
) -\> tuple\[float, float\]:  
    """  
    Project a bearing and distance from own position to lat/lon.  
    Uses spherical earth approximation (accurate enough for \<10NM).  
    """  
    R = 3440.065  \# Earth radius in nautical miles  
    bearing\_rad = math.radians(bearing\_deg)  
    lat1 = math.radians(own\_lat)  
    lon1 = math.radians(own\_lon)  
    d\_r = distance\_nm / R  
    lat2 = math.asin(  
        math.sin(lat1) \* math.cos(d\_r) +  
        math.cos(lat1) \* math.sin(d\_r) \* math.cos(bearing\_rad)  
    )  
    lon2 = lon1 + math.atan2(  
        math.sin(bearing\_rad) \* math.sin(d\_r) \* math.cos(lat1),  
        math.cos(d\_r) - math.sin(lat1) \* math.sin(lat2)  
    )  
    return math.degrees(lat2), math.degrees(lon2)
```


## 5. Layer 2: Real-Time Execution Core

### 5.1 The Problem the Research Ignores

The research presents algorithms. It does not discuss when they run or what happens when they run late. A collision avoidance decision that arrives 500ms late is a failed decision. On a boat closing at 20 knots combined speed, 500ms is 5 meters.

**The execution timing is not an implementation detail. It is a safety property.**

### 5.2 The 100ms Deterministic Loop

SafeHelm runs a fixed-frequency update loop at 10Hz (100ms period). Every cycle must complete within budget. The watchdog kills and restarts any cycle that overruns.

```
Each 100ms cycle:  
  T+0ms:   Read all sensor queues (non-blocking, take latest)  
  T+5ms:   Update confidence scores  
  T+10ms:  Fuse AIS + Camera targets into unified target list  
  T+15ms:  Run CPA/TCPA for all targets  
  T+30ms:  Run COLREGs classifier for all risk targets  
  T+45ms:  Run Conflict Graph solver if \>1 risk target  
  T+60ms:  Evaluate Safety Envelope constraints  
  T+70ms:  Determine action (None / Advisory / Autopilot command)  
  T+80ms:  Push to output queues (AvNav, voice, pypilot)  
  T+100ms: Cycle complete — sleep until next tick

import threading  
import time  
import logging  
  
class SafeHelmCore(threading.Thread):  
    LOOP\_PERIOD\_S = 0.100  \# 100ms  
    WATCHDOG\_LIMIT\_S = 0.090  \# kill cycle if it runs past 90ms  
  
    def \_\_init\_\_(self, sensor\_hub, decision\_engine, output\_bus):  
        super().\_\_init\_\_(daemon=True, name="SafeHelmCore")  
        self.\_sensor\_hub = sensor\_hub  
        self.\_decision\_engine = decision\_engine  
        self.\_output\_bus = output\_bus  
        self.\_running = False  
        self.\_cycle\_count = 0  
        self.\_overruns = 0  
  
    def run(self):  
        self.\_running = True  
        next\_tick = time.monotonic()  
        while self.\_running:  
            cycle\_start = time.monotonic()  
            try:  
                self.\_execute\_cycle()  
            except Exception as e:  
                logging.error(f"SafeHelm cycle \{self.\_cycle\_count\} failed: \{e\}")  
                self.\_output\_bus.send\_fault("CYCLE\_ERROR", str(e))  
  
            elapsed = time.monotonic() - cycle\_start  
            if elapsed \> self.WATCHDOG\_LIMIT\_S:  
                self.\_overruns += 1  
                logging.warning(  
                    f"Cycle \{self.\_cycle\_count\} overran: \{elapsed\*1000:.1f\}ms"  
                )  
  
            self.\_cycle\_count += 1  
            next\_tick += self.LOOP\_PERIOD\_S  
            sleep\_time = next\_tick - time.monotonic()  
            if sleep\_time \> 0:  
                time.sleep(sleep\_time)  
  
    def \_execute\_cycle(self):  
        sensor\_data = self.\_sensor\_hub.read\_latest()  
        targets = self.\_decision\_engine.fuse\_and\_evaluate(sensor\_data)  
        action = self.\_decision\_engine.determine\_action(targets)  
        self.\_output\_bus.dispatch(action)  
  
    def stop(self):  
        self.\_running = False
```

### 5.3 Thread Architecture

Four isolated threads. They communicate only through thread-safe queues. No shared mutable state.

| Thread | Job | Period |
| - | - | - |
| `SafeHelmCore` | Main decision loop | 100ms |
| `AISReader` | Reads Signal K websocket, pushes to queue | Event-driven |
| `CameraFeeder` | Reads Forward Watch output, pushes to queue | 200ms (5Hz) |
| `OutputBus` | Reads action queue, dispatches to AvNav/pypilot/voice | Event-driven |



## 6. Layer 3: Vessel Dynamics Model

### 6.1 The Problem the Research Ignores

Academic systems treat vessels as points that can turn instantaneously. A sailing vessel is not a point. It has:

- A turning circle (typically 2–3 boat lengths at cruising speed)

- A stopping distance (typically 5–8 boat lengths)

- Windage (the hull acts as a sail in crosswinds)

- Current drift (the ocean moves)

- Propeller walk (single-screw boats turn better one direction)

**A collision avoidance maneuver that is geometrically correct but physically impossible is useless.**

### 6.2 Vessel Dynamics Parameters

These are configured once per vessel in `safehelm-config.json`. The defaults are for a 35–40 foot sailing vessel with a single inboard diesel.

```
@dataclass  
class VesselDynamics:  
    """Physical constraints of own vessel. Configured once per installation."""  
    loa\_meters: float = 11.0          \# Length Overall  
    beam\_meters: float = 3.7          \# Beam  
    max\_speed\_kts: float = 8.0        \# Hull speed  
    cruise\_speed\_kts: float = 6.0     \# Typical cruising speed  
    min\_turn\_radius\_nm: float = 0.05  \# At full rudder, full speed  
    stopping\_dist\_nm: float = 0.08    \# Crash stop distance  
    max\_turn\_rate\_deg\_s: float = 3.0  \# Maximum degrees per second  
    prop\_walk\_dir: int = -1           \# -1 = port, +1 = starboard (single screw)  
    windage\_factor: float = 0.15      \# Leeway fraction of wind speed  
  
    def time\_to\_turn\_deg(self, angle\_deg: float, current\_speed\_kts: float) -\> float:  
        """Seconds required to turn by angle\_deg at current speed."""  
        effective\_rate = self.max\_turn\_rate\_deg\_s \* (current\_speed\_kts / self.cruise\_speed\_kts)  
        effective\_rate = max(effective\_rate, 0.5)  
        return abs(angle\_deg) / effective\_rate  
  
    def achievable\_new\_heading(  
        self, current\_heading: float, target\_heading: float,  
        tcpa\_seconds: float, current\_speed\_kts: float  
    ) -\> bool:  
        """True if vessel can physically reach target\_heading before TCPA."""  
        angle\_needed = abs((target\_heading - current\_heading + 180) % 360 - 180)  
        time\_needed = self.time\_to\_turn\_deg(angle\_needed, current\_speed\_kts)  
        return time\_needed \< (tcpa\_seconds \* 0.7)  \# 30% margin
```

### 6.3 Drift and Current Compensation

Own vessel position is not just GPS. It is GPS corrected for current set and drift. A vessel tracking 270° at 6 knots in a 2-knot current flowing north is actually making good a ground track of approximately 252°.

```
def apply\_current\_correction(  
    cog\_deg: float, sog\_kts: float,  
    current\_set\_deg: float, current\_speed\_kts: float  
) -\> tuple\[float, float\]:  
    """  
    Returns corrected Course Over Ground and Speed Over Ground  
    accounting for tidal current or river flow.  
    """  
    import cmath  
    vessel = cmath.rect(sog\_kts, math.radians(90 - cog\_deg))  
    current = cmath.rect(current\_speed\_kts, math.radians(90 - current\_set\_deg))  
    resultant = vessel + current  
    corrected\_sog = abs(resultant)  
    corrected\_cog = (90 - math.degrees(cmath.phase(resultant))) % 360  
    return corrected\_cog, corrected\_sog
```


## 7. Layer 4: COLREGs Decision Engine

### 7.1 CPA and TCPA — The Core Risk Calculation

All targets, regardless of source (AIS or camera), are evaluated on CPA and TCPA. These two numbers answer the only question that matters: *Will we collide, and when?*

```
import math  
from dataclasses import dataclass  
  
@dataclass  
class Target:  
    id: str  
    lat: float  
    lon: float  
    sog\_kts: float  
    cog\_deg: float  
    source: str  \# 'ais' | 'camera' | 'virtual'  
    confidence: float  
  
@dataclass  
class OwnVessel:  
    lat: float  
    lon: float  
    sog\_kts: float  
    cog\_deg: float  
    heading\_deg: float  
  
@dataclass  
class RiskAssessment:  
    target\_id: str  
    cpa\_nm: float  
    tcpa\_sec: float  
    encounter\_type: str  
    role: str  \# 'GIVE\_WAY' | 'STAND\_ON' | 'BOTH\_TURN' | 'UNDEFINED'  
    risk\_level: str  \# 'CLEAR' | 'MONITOR' | 'WARNING' | 'CRITICAL'  
    recommended\_heading: float | None  
  
KTS\_TO\_NM\_PER\_S = 1.0 / 3600.0  
  
def latlon\_to\_xy\_nm(lat1, lon1, lat2, lon2) -\> tuple\[float, float\]:  
    """Convert two lat/lon pairs to relative x/y in nautical miles."""  
    dlat = (lat2 - lat1) \* 60.0  
    dlon = (lon2 - lon1) \* 60.0 \* math.cos(math.radians((lat1 + lat2) / 2))  
    return dlon, dlat  \# x=east, y=north  
  
def calculate\_cpa\_tcpa(own: OwnVessel, target: Target) -\> tuple\[float, float\]:  
    """  
    Calculate CPA (nm) and TCPA (seconds) using relative motion vectors.  
    Negative TCPA means the CPA has already been passed.  
    """  
    px, py = latlon\_to\_xy\_nm(own.lat, own.lon, target.lat, target.lon)  
  
    own\_vx = own.sog\_kts \* math.sin(math.radians(own.cog\_deg)) \* KTS\_TO\_NM\_PER\_S  
    own\_vy = own.sog\_kts \* math.cos(math.radians(own.cog\_deg)) \* KTS\_TO\_NM\_PER\_S  
    tgt\_vx = target.sog\_kts \* math.sin(math.radians(target.cog\_deg)) \* KTS\_TO\_NM\_PER\_S  
    tgt\_vy = target.sog\_kts \* math.cos(math.radians(target.cog\_deg)) \* KTS\_TO\_NM\_PER\_S  
  
    dvx = tgt\_vx - own\_vx  
    dvy = tgt\_vy - own\_vy  
    v\_rel\_sq = dvx \* dvx + dvy \* dvy  
  
    if v\_rel\_sq \< 1e-12:  \# stationary relative to each other  
        cpa = math.sqrt(px \* px + py \* py)  
        return cpa, float('inf')  
  
    tcpa\_s = -(px \* dvx + py \* dvy) / v\_rel\_sq  
    cx = px + dvx \* tcpa\_s  
    cy = py + dvy \* tcpa\_s  
    cpa = math.sqrt(cx \* cx + cy \* cy)  
  
    return cpa, tcpa\_s
```

### 7.2 COLREGs Situation Classifier

```
def classify\_encounter(  
    own: OwnVessel,  
    target: Target,  
    own\_true\_bearing\_to\_target: float  
) -\> tuple\[str, str\]:  
    """  
    Returns (encounter\_type, own\_role).  
    encounter\_type: HEAD\_ON | CROSSING | OVERTAKING | BEING\_OVERTAKEN  
    own\_role: GIVE\_WAY | STAND\_ON | BOTH\_TURN | UNDEFINED  
    """  
    rel\_bearing = (own\_true\_bearing\_to\_target - own.heading\_deg + 360) % 360  
    target\_rel\_hdg = (target.cog\_deg - own.cog\_deg + 360) % 360  
  
    \# Rule 13: Overtaking (target approaching from more than 22.5° abaft beam)  
    if 112.5 \<= rel\_bearing \<= 247.5:  
        return "OVERTAKING", "GIVE\_WAY"  
  
    \# Rule 14: Head-on (target dead ahead ±15°, coming toward us ±15°)  
    if rel\_bearing \<= 15 or rel\_bearing \>= 345:  
        if 165 \<= target\_rel\_hdg \<= 195:  
            return "HEAD\_ON", "BOTH\_TURN"  
  
    \# Rule 15: Crossing — target on starboard bow  
    if 5 \<= rel\_bearing \<= 112.5:  
        return "CROSSING", "GIVE\_WAY"  
  
    \# Rule 15: Crossing — target on port bow (we are stand-on)  
    if 247.5 \<= rel\_bearing \<= 355:  
        return "CROSSING", "STAND\_ON"  
  
    return "UNDEFINED", "UNDEFINED"
```

### 7.3 Risk Level Assignment

```
SHIP\_DOMAIN\_NM = 0.25       \# Safety bubble radius (default)  
CRITICAL\_TCPA\_SEC = 300     \# 5 minutes  
WARNING\_TCPA\_SEC = 600      \# 10 minutes  
  
def assign\_risk\_level(cpa\_nm: float, tcpa\_sec: float) -\> str:  
    if tcpa\_sec \< 0:  
        return "CLEAR"  \# CPA already passed  
    if cpa\_nm \< SHIP\_DOMAIN\_NM:  
        if tcpa\_sec \< CRITICAL\_TCPA\_SEC:  
            return "CRITICAL"  
        if tcpa\_sec \< WARNING\_TCPA\_SEC:  
            return "WARNING"  
        return "MONITOR"  
    return "CLEAR"
```

### 7.4 Recommended Heading Calculator

When SafeHelm recommends a course change, it must provide a specific heading — not "turn right." The heading must:

1. Clear all threats (CPA \> ship domain)

2. Comply with COLREGs (preferentially Starboard)

3. Be achievable given vessel dynamics

4. Return to original track after clearing

```
def find\_escape\_heading(  
    own: OwnVessel,  
    threats: list\[tuple\[Target, RiskAssessment\]\],  
    dynamics: VesselDynamics,  
    prefer\_starboard: bool = True  
) -\> float | None:  
    """  
    Sweep headings in 5-degree steps (Starboard preference) to find  
    the nearest COLREGs-compliant course that clears all threats.  
    Returns None if no escape exists (rare — usually means stop).  
    """  
    search\_order = list(range(0, 180, 5)) + list(range(355, 180, -5))  
    if not prefer\_starboard:  
        search\_order = list(range(355, 180, -5)) + list(range(0, 180, 5))  
  
    for delta in search\_order:  
        candidate\_hdg = (own.heading\_deg + delta) % 360  
        candidate\_own = OwnVessel(  
            lat=own.lat, lon=own.lon,  
            sog\_kts=own.sog\_kts,  
            cog\_deg=candidate\_hdg,  
            heading\_deg=candidate\_hdg  
        )  
        all\_clear = all(  
            calculate\_cpa\_tcpa(candidate\_own, t)\[0\] \>= SHIP\_DOMAIN\_NM  
            for t, \_ in threats  
        )  
        if all\_clear:  
            min\_tcpa = min(calculate\_cpa\_tcpa(own, t)\[1\] for t, \_ in threats)  
            if dynamics.achievable\_new\_heading(  
                own.heading\_deg, candidate\_hdg, min\_tcpa, own.sog\_kts  
            ):  
                return candidate\_hdg  
  
    return None
```


## 8. Layer 5: Multi-Vessel Conflict Solver

### 8.1 The Problem the Research Ignores

Most research addresses one vessel at a time. Harbors do not cooperate. A SafeHelm decision for three simultaneous threats may be individually correct but collectively deadlocked — each vessel's "escape" heading crosses another vessel's path.

### 8.2 Conflict Graph Architecture

```
from dataclasses import dataclass, field  
import itertools  
  
@dataclass  
class ConflictNode:  
    target: Target  
    assessment: RiskAssessment  
    priority: int  \# lower number = higher priority  
  
@dataclass  
class ConflictGraph:  
    nodes: list\[ConflictNode\] = field(default\_factory=list)  
  
    def assign\_priorities(self) -\> None:  
        """  
        Priority assignment rules (lower number = act first):  
        1. CRITICAL risk before WARNING  
        2. Give-way vessel obligation before stand-on  
        3. Closest TCPA breaks ties  
        4. Vessels on port bow (Starboard rule) get higher priority attention  
        """  
        for i, node in enumerate(  
            sorted(self.nodes, key=lambda n: (  
                0 if n.assessment.risk\_level == "CRITICAL" else 1,  
                0 if n.assessment.role == "GIVE\_WAY" else 1,  
                n.assessment.tcpa\_sec  
            ))  
        ):  
            node.priority = i  
  
    def detect\_deadlock(self, proposed\_headings: dict\[str, float\]) -\> bool:  
        """  
        Check if proposed escape headings create crossing conflicts.  
        Returns True if deadlock detected.  
        """  
        for n1, n2 in itertools.combinations(self.nodes, 2):  
            h1 = proposed\_headings.get(n1.target.id)  
            h2 = proposed\_headings.get(n2.target.id)  
            if h1 is None or h2 is None:  
                continue  
            delta = abs((h1 - h2 + 180) % 360 - 180)  
            if delta \< 30:  
                return True  
        return False  
  
    def resolve(self, own: OwnVessel, dynamics: VesselDynamics) -\> float | None:  
        """  
        Iteratively find an escape heading that clears all threats  
        without creating new ones. Returns None if no solution found  
        (triggers emergency stop advisory).  
        """  
        self.assign\_priorities()  
        threats\_by\_priority = \[(n.target, n.assessment) for n in self.nodes\]  
        return find\_escape\_heading(own, threats\_by\_priority, dynamics)
```

### 8.3 Deadlock Resolution: The Emergency Slow-Down

When no heading solves all conflicts simultaneously, reducing speed is often the correct COLREGs answer. A vessel that slows from 6 knots to 2 knots gains time for other vessels to pass.

If no escape heading and no speed reduction resolves the conflict within the safety margin, the system escalates to CRITICAL alert and disengages autopilot, returning full control to the captain.


## 9. Layer 6: Human-in-the-Loop Interface

### 9.1 The Problem the Research Ignores

An alarm that fires too often is turned off. A system that annoys the captain becomes a liability. **Alarm fatigue is not a UX problem. It is a safety problem.**

### 9.2 Alarm Budget System

```
@dataclass  
class AlarmBudget:  
    """  
    Limits how often SafeHelm can alarm the operator.  
    Prevents alarm fatigue while ensuring critical events are never suppressed.  
    """  
    max\_warnings\_per\_hour: int = 6  
    max\_advisories\_per\_hour: int = 20  
    \_warning\_times: list\[float\] = field(default\_factory=list)  
    \_advisory\_times: list\[float\] = field(default\_factory=list)  
  
    def can\_alarm(self, level: str) -\> bool:  
        now = time.monotonic()  
        one\_hour\_ago = now - 3600  
        if level == "CRITICAL":  
            return True  \# Critical alarms are NEVER suppressed  
        if level == "WARNING":  
            self.\_warning\_times = \[t for t in self.\_warning\_times if t \> one\_hour\_ago\]  
            return len(self.\_warning\_times) \< self.max\_warnings\_per\_hour  
        self.\_advisory\_times = \[t for t in self.\_advisory\_times if t \> one\_hour\_ago\]  
        return len(self.\_advisory\_times) \< self.max\_advisories\_per\_hour  
  
    def record\_alarm(self, level: str) -\> None:  
        now = time.monotonic()  
        if level == "WARNING":  
            self.\_warning\_times.append(now)  
        elif level != "CRITICAL":  
            self.\_advisory\_times.append(now)
```

### 9.3 Voice Alert Script Templates

Voice alerts must be unambiguous and actionable. They follow a strict format:

```
\[Direction\] vessel \[bearing\]. \[Role\]. \[Action\]. \[Heading if known\].
```

Examples:

- "Starboard vessel, bearing zero four five. We are give-way. Recommend turn to two seven zero."

- "Head-on. Both vessels must turn starboard. Recommend zero nine zero."

- "Port vessel approaching. We hold right of way. Maintain course."

- "CRITICAL. Collision course. No clear heading found. Manual override required."

```
def generate\_voice\_alert(assessment: RiskAssessment, bearing\_deg: float) -\> str:  
    if bearing\_deg \< 45 or bearing\_deg \> 315:  
        direction = "Ahead"  
    elif bearing\_deg \< 135:  
        direction = "Starboard"  
    elif bearing\_deg \< 225:  
        direction = "Astern"  
    else:  
        direction = "Port"  
  
    role\_phrase = \{  
        "GIVE\_WAY": "We are give-way.",  
        "STAND\_ON": "We hold right of way.",  
        "BOTH\_TURN": "Head-on. Both turn starboard.",  
        "UNDEFINED": "Situation unclear.",  
    \}.get(assessment.role, "")  
  
    if assessment.recommended\_heading is not None:  
        heading\_phrase = f"Recommend turn to \{int(assessment.recommended\_heading):03d\}."  
    else:  
        heading\_phrase = "No clear heading. Manual override required."  
  
    bearing\_phrase = f"bearing \{int(bearing\_deg):03d\}"  
    return f"\{direction\} vessel, \{bearing\_phrase\}. \{role\_phrase\} \{heading\_phrase\}"
```

### 9.4 AvNav Widget Specification

The SafeHelm AvNav widget displays in the corner of the chart. It has three states:

**State: CLEAR** — Small green dot. No text.

**State: WARNING** — Yellow banner at bottom of chart:

```
⚠ Vessel SW 225° — Give-way — Suggest 090°   \[ACK\] \[EXECUTE\]
```

**State: CRITICAL** — Full-width red banner, pulsing:

```
🚨 COLLISION RISK — Bearing 045° — TCPA 4min — Suggest 090°   \[EXECUTE NOW\] \[TAKE HELM\]
```

The `\[EXECUTE\]` button sends the recommended heading to pypilot. The `\[TAKE HELM\]` button disengages SafeHelm autopilot control and silences the alarm for 2 minutes.

**A 2-minute silence window is the maximum. After 2 minutes, if the threat is still active, the alarm re-fires.**


## 10. Layer 7: Safety Envelope

### 10.1 The Missing Piece in All the Research

Every autonomous system needs a safety layer that is mathematically separate from the planning layer. The planner proposes actions. The safety layer vetoes unsafe ones. These two components must never be merged.

**The safety layer says "you may not do that" even if the planner says "do it."**

### 10.2 Hard Constraints

These constraints are never violated regardless of what the planner recommends:

```
@dataclass  
class SafetyEnvelope:  
    """  
    Hard constraints that cannot be overridden by the planner.  
    If the planner produces an action violating these, it is rejected.  
    """  
    min\_speed\_response\_kts: float = 1.0   \# Never command \< 1kt except full stop  
    max\_rudder\_rate\_pct: float = 50.0     \# Never slam rudder past 50%/s  
    shallow\_water\_depth\_m: float = 3.0    \# Never maneuver if depth \< 3m  
    no\_go\_zone\_deg: float = 40.0          \# For sail — keep out of irons  
    max\_heel\_deg: float = 30.0            \# Never command course that increases heel past 30°  
  
    def validate\_heading\_command(  
        self,  
        proposed\_heading: float,  
        current\_depth\_m: float,  
        current\_heel\_deg: float,  
        wind\_angle\_deg: float,  
        vessel\_type: str  
    ) -\> tuple\[bool, str\]:  
        """  
        Returns (approved, reason).  
        If not approved, reason explains what constraint was violated.  
        """  
        if current\_depth\_m \< self.shallow\_water\_depth\_m:  
            return False, f"SHALLOW\_WATER: depth \{current\_depth\_m:.1f\}m \< \{self.shallow\_water\_depth\_m\}m minimum"  
  
        if vessel\_type == "sailing":  
            apparent\_wind\_on\_new\_hdg = abs(wind\_angle\_deg)  
            if apparent\_wind\_on\_new\_hdg \< self.no\_go\_zone\_deg:  
                return False, f"NO\_GO\_ZONE: heading places vessel in irons (\{apparent\_wind\_on\_new\_hdg:.0f\}° apparent)"  
  
        if current\_heel\_deg \> self.max\_heel\_deg \* 0.8:  
            return False, f"HEEL\_LIMIT: current heel \{current\_heel\_deg:.0f\}° approaching limit"  
  
        return True, "APPROVED"
```

### 10.3 Control Barrier Function (Simplified)

A Control Barrier Function (CBF) defines a "safe set" — positions from which safety can be maintained. If the system is outside the safe set, it must return to it before doing anything else.

For our purposes, the CBF is a simple invariant: **the CPA to any threat must never decrease faster than our turning capability allows us to correct.**

```
def barrier\_function(  
    cpa\_nm: float,  
    tcpa\_sec: float,  
    dynamics: VesselDynamics,  
    own\_speed\_kts: float  
) -\> float:  
    """  
    Returns h(x) where h(x) \>= 0 means we are in the safe set.  
    h(x) \< 0 means safety is violated — emergency action required.  
  
    The barrier: we must have enough time to turn to an escape heading  
    before the threat arrives. If we can't turn fast enough, we are unsafe.  
    """  
    if tcpa\_sec \<= 0:  
        return 1.0  \# Already past — safe  
  
    max\_turn\_180 = dynamics.time\_to\_turn\_deg(180, own\_speed\_kts)  
    safety\_margin\_s = 60  \# We want at least 60s of buffer after turning  
    h = tcpa\_sec - max\_turn\_180 - safety\_margin\_s  
    return h
```

If `barrier\_function()` returns negative, the system enters **Emergency Mode**:

1. If autopilot engaged: immediately command full starboard rudder (COLREGs preference)

2. Simultaneously broadcast critical voice alert

3. Log the event with full sensor snapshot for post-incident review

4. Never re-engage autonomous control until captain acknowledges


## 11. Non-Compliant Vessel Handling

### 11.1 The Hardest Unsolved Problem

The research mentions this but does not solve it. In practice, this is the most common real-world scenario:

- Jet skis and PWCs ignore all rules

- Small fishing boats drift without power

- Ferries and car carriers assume everyone will yield

- Vessels under poor watchkeeping do not react as expected

**A system that assumes all vessels are cooperative is only safe in simulation.**

### 11.2 Compliance Detection

```
@dataclass  
class ComplianceTracker:  
    """  
    Track whether a vessel is responding to the situation as COLREGs requires.  
    A give-way vessel should be altering course. If it is not, it is non-compliant.  
    """  
    target\_id: str  
    expected\_role: str  \# 'GIVE\_WAY' — they should be turning  
    history: list\[tuple\[float, float\]\] = field(default\_factory=list)  \# (timestamp, cog)  
  
    def record\_cog(self, timestamp: float, cog: float) -\> None:  
        self.history.append((timestamp, cog))  
        if len(self.history) \> 20:  
            self.history.pop(0)  
  
    def is\_compliant(self, tcpa\_sec: float) -\> bool:  
        """  
        If TCPA \< 5 minutes and vessel is give-way, they should be turning.  
        Compliance = COG changed by \>10° in last 60 seconds.  
        """  
        if self.expected\_role != "GIVE\_WAY" or tcpa\_sec \> 300:  
            return True  
        if len(self.history) \< 2:  
            return True  \# Insufficient data — assume compliant  
  
        recent = \[h for h in self.history if time.monotonic() - h\[0\] \< 60\]  
        if len(recent) \< 2:  
            return True  
  
        cog\_change = abs(recent\[-1\]\[1\] - recent\[0\]\[1\])  
        cog\_change = min(cog\_change, 360 - cog\_change)  
        return cog\_change \> 10.0
```

### 11.3 Defensive Navigation Mode

When a vessel is detected as non-compliant, SafeHelm switches to **Defensive Mode**:

1. **Stand-on vessel duty suspended**: Even as a stand-on vessel, we begin planning our own escape rather than waiting for the give-way vessel to act (Rule 17(a)(ii) — action by stand-on vessel).

2. **Ship domain expands**: Safety bubble grows from 0.25NM to 0.50NM for that target.

3. **Alarm threshold tightens**: CRITICAL fires at TCPA \< 8 minutes instead of 5.

4. **Audit log flagged**: The non-compliance event is recorded with full sensor snapshot.

```
def handle\_non\_compliant(  
    own: OwnVessel,  
    target: Target,  
    assessment: RiskAssessment,  
    dynamics: VesselDynamics  
) -\> RiskAssessment:  
    """Recompute assessment for a non-compliant give-way vessel."""  
    expanded\_domain = SHIP\_DOMAIN\_NM \* 2.0  
    new\_risk = assign\_risk\_level\_with\_domain(  
        assessment.cpa\_nm, assessment.tcpa\_sec, expanded\_domain  
    )  
    new\_heading = find\_escape\_heading(  
        own, \[(target, assessment)\], dynamics, prefer\_starboard=True  
    )  
    return RiskAssessment(  
        target\_id=target.id,  
        cpa\_nm=assessment.cpa\_nm,  
        tcpa\_sec=assessment.tcpa\_sec,  
        encounter\_type=assessment.encounter\_type,  
        role="GIVE\_WAY",  \# We assume give-way even if we were stand-on  
        risk\_level=new\_risk,  
        recommended\_heading=new\_heading  
    )
```


## 12. Signal K, AvNav, and pypilot Integration

### 12.1 Signal K Integration (Data In)

SafeHelm reads from Signal K via WebSocket subscription. One subscription covers all needed data.

```
import asyncio  
import websockets  
import json  
  
SIGNALK\_WS = "ws://localhost:3000/signalk/v1/stream"  
  
SUBSCRIBE\_MSG = \{  
    "context": "vessels.\*",  
    "subscribe": \[  
        \{"path": "navigation.position"\},  
        \{"path": "navigation.speedOverGround"\},  
        \{"path": "navigation.courseOverGroundTrue"\},  
        \{"path": "navigation.headingTrue"\},  
        \{"path": "sensors.ais.class"\},  
    \]  
\}  
  
async def stream\_signalk(queue: asyncio.Queue):  
    async with websockets.connect(SIGNALK\_WS) as ws:  
        await ws.send(json.dumps(SUBSCRIBE\_MSG))  
        async for message in ws:  
            data = json.loads(message)  
            await queue.put(data)
```

### 12.2 Virtual AIS Injection (Targets Out to AvNav)

Camera-detected targets are injected as Signal K vessels. AvNav then renders them as AIS symbols automatically.

```
import requests  
  
SIGNALK\_API = "http://localhost:3000/signalk/v1/api"  
  
def inject\_virtual\_target(  
    target\_id: str,  
    lat: float,  
    lon: float,  
    sog\_kts: float,  
    cog\_deg: float,  
    confidence: float  
) -\> None:  
    """  
    Inject a camera-detected vessel into Signal K as a virtual AIS target.  
    AvNav will render it as a standard vessel triangle on the chart.  
    """  
    vessel\_path = f"vessels/urn:mrn:d3k:visual:\{target\_id\}"  
    updates = \[  
        \{"path": "navigation.position",  
         "value": \{"latitude": lat, "longitude": lon\}\},  
        \{"path": "navigation.speedOverGround",  
         "value": sog\_kts \* 0.514444\},  \# kts to m/s  
        \{"path": "navigation.courseOverGroundTrue",  
         "value": math.radians(cog\_deg)\},  
        \{"path": "sensors.safehelm.confidence",  
         "value": confidence\},  
    \]  
    payload = \{  
        "context": vessel\_path,  
        "updates": \[\{"values": updates, "source": \{"label": "safehelm-cv"\}\}\]  
    \}  
    try:  
        requests.put(f"\{SIGNALK\_API\}/\{vessel\_path\}", json=payload, timeout=0.05)  
    except Exception:  
        pass  \# Never block the main loop on network I/O
```

### 12.3 pypilot Integration (Autopilot Commands Out)

pypilot accepts heading commands via its own TCP protocol or via Signal K autopilot API.

```
import socket  
import json  
  
PYPILOT\_HOST = "localhost"  
PYPILOT\_PORT = 23322  \# pypilot default control port  
  
def send\_heading\_to\_pypilot(target\_heading\_deg: float) -\> bool:  
    """  
    Send a heading command to pypilot.  
    Returns True if command was accepted.  
    Only called after Safety Envelope validation passes.  
    """  
    try:  
        with socket.create\_connection(  
            (PYPILOT\_HOST, PYPILOT\_PORT), timeout=0.08  
        ) as sock:  
            command = json.dumps(\{  
                "ap.heading\_command": math.radians(target\_heading\_deg)  
            \}) + "\\n"  
            sock.send(command.encode())  
        return True  
    except Exception as e:  
        logging.error(f"pypilot command failed: \{e\}")  
        return False  
  
def engage\_pypilot\_compass\_mode() -\> bool:  
    """Set pypilot to compass mode before sending heading commands."""  
    try:  
        with socket.create\_connection(  
            (PYPILOT\_HOST, PYPILOT\_PORT), timeout=0.08  
        ) as sock:  
            command = json.dumps(\{"ap.mode": "compass"\}) + "\\n"  
            sock.send(command.encode())  
        return True  
    except Exception:  
        return False  
  
def disengage\_pypilot() -\> bool:  
    """Disengage autopilot — return full control to helm."""  
    try:  
        with socket.create\_connection(  
            (PYPILOT\_HOST, PYPILOT\_PORT), timeout=0.08  
        ) as sock:  
            command = json.dumps(\{"ap.enabled": False\}) + "\\n"  
            sock.send(command.encode())  
        return True  
    except Exception:  
        return False
```

### 12.4 AvNav Plugin (JavaScript Widget)

```
// safehelm-widget.js — Drop into AvNav plugins directory  
// Displays collision risk status in a corner overlay on the chart  
  
(function() \{  
    const SAFEHELM\_API = '/safehelm/status';  
    const POLL\_INTERVAL\_MS = 500;  
  
    let container;  
  
    function init() \{  
        container = document.createElement('div');  
        container.id = 'safehelm-overlay';  
        container.style.cssText = \`  
            position: fixed;  
            bottom: 80px;  
            right: 20px;  
            z-index: 9000;  
            font-family: monospace;  
            font-size: 18px;  
            min-width: 240px;  
        \`;  
        document.body.appendChild(container);  
        poll();  
    \}  
  
    function poll() \{  
        fetch(SAFEHELM\_API)  
            .then(r =\> r.json())  
            .then(render)  
            .catch(() =\> renderOffline())  
            .finally(() =\> setTimeout(poll, POLL\_INTERVAL\_MS));  
    \}  
  
    function render(data) \{  
        const colors = \{  
            CLEAR: '\#00aa00',  
            MONITOR: '\#888800',  
            WARNING: '\#ff8800',  
            CRITICAL: '\#ff0000'  
        \};  
        const level = data.highest\_risk || 'CLEAR';  
        const color = colors\[level\] || '\#888888';  
  
        if (level === 'CLEAR') \{  
            container.innerHTML = \`\<div style="color:$\{color\};padding:4px"\>✔ SafeHelm CLEAR\</div\>\`;  
            return;  
        \}  
  
        const t = data.primary\_threat;  
        container.innerHTML = \`  
            \<div style="background:$\{color\};color:white;padding:12px;border-radius:6px;line-height:1.6"\>  
                \<strong\>$\{level\} — $\{t.encounter\_type\}\</strong\>\<br\>  
                Bearing $\{t.bearing\_deg.toFixed(0)\}° | TCPA $\{(t.tcpa\_sec/60).toFixed(1)\} min\<br\>  
                $\{t.role\} | Suggest $\{t.recommended\_heading ? t.recommended\_heading.toFixed(0)+'°' : 'STOP'\}\<br\>  
                \<button onclick="executeManeuver($\{t.recommended\_heading\})"  
                    style="margin-top:8px;padding:8px 16px;font-size:18px;  
                           background:white;color:$\{color\};border:none;  
                           border-radius:4px;cursor:pointer;width:100%"\>  
                    EXECUTE MANEUVER  
                \</button\>  
                \<button onclick="silenceAlarm()"  
                    style="margin-top:4px;padding:8px 16px;font-size:18px;  
                           background:transparent;color:white;border:2px solid white;  
                           border-radius:4px;cursor:pointer;width:100%"\>  
                    TAKE HELM (2 min silence)  
                \</button\>  
            \</div\>\`;  
    \}  
  
    function executeManeuver(heading) \{  
        fetch('/safehelm/execute', \{  
            method: 'POST',  
            headers: \{'Content-Type': 'application/json'\},  
            body: JSON.stringify(\{heading: heading\})  
        \});  
    \}  
  
    function silenceAlarm() \{  
        fetch('/safehelm/silence', \{method: 'POST'\});  
    \}  
  
    function renderOffline() \{  
        container.innerHTML = '\<div style="color:\#888;padding:4px"\>SafeHelm offline\</div\>';  
    \}  
  
    document.addEventListener('DOMContentLoaded', init);  
\})();
```


## 13. Python Module File Structure

```
d3kOS/services/safehelm/  
├── safehelm.py              — Main entry point, initialises all layers  
├── core/  
│   ├── loop.py              — SafeHelmCore real-time execution thread  
│   ├── sensor\_hub.py        — SensorConfidenceTracker, input queues  
│   ├── dynamics.py          — VesselDynamics model  
│   └── envelope.py          — SafetyEnvelope, barrier function  
├── engine/  
│   ├── cpa.py               — CPA/TCPA calculations  
│   ├── colregs.py           — COLREGs classifier  
│   ├── conflict.py          — ConflictGraph, multi-vessel solver  
│   └── compliance.py        — Non-compliant vessel detection  
├── interface/  
│   ├── signalk\_reader.py    — Signal K WebSocket subscriber  
│   ├── virtual\_ais.py       — Inject camera targets into Signal K  
│   ├── pypilot\_client.py    — pypilot TCP command interface  
│   └── voice.py             — Text-to-speech alert generation  
├── ui/  
│   └── safehelm-widget.js   — AvNav overlay widget  
├── safehelm-config.json     — Vessel dynamics, thresholds, preferences  
└── safehelm.service         — systemd unit for Pi autostart
```


## 14. safehelm.service (systemd)

```
\[Unit\]  
Description=d3kOS SafeHelm Collision Avoidance Service  
After=network.target d3kos-signalk.service  
Requires=d3kos-signalk.service  
  
\[Service\]  
Type=simple  
User=d3kos  
WorkingDirectory=/opt/d3kos/services/safehelm  
ExecStart=/opt/d3kos/venv/bin/python safehelm.py  
Restart=on-failure  
RestartSec=5  
KillMode=process  
  
\[Install\]  
WantedBy=multi-user.target
```


## 15. Testing Strategy

### 15.1 Unit Tests (Pure Python, No Hardware)

Each module is independently testable with synthetic data:

```
def test\_cpa\_head\_on():  
    own = OwnVessel(lat=0.0, lon=0.0, sog\_kts=6.0, cog\_deg=0.0, heading\_deg=0.0)  
    target = Target(id="T1", lat=0.1, lon=0.0, sog\_kts=6.0, cog\_deg=180.0,  
                    source="ais", confidence=1.0)  
    cpa, tcpa = calculate\_cpa\_tcpa(own, target)  
    assert cpa \< 0.01, "Head-on CPA should be near zero"  
    assert 0 \< tcpa \< 600, "TCPA should be positive and \< 10 min"  
  
def test\_escape\_heading\_starboard\_preference():  
    \# Give-way vessel in crossing situation should get Starboard recommendation  
    own = OwnVessel(lat=0.0, lon=0.0, sog\_kts=6.0, cog\_deg=0.0, heading\_deg=0.0)  
    target = Target(id="T1", lat=0.05, lon=0.05, sog\_kts=6.0, cog\_deg=270.0,  
                    source="ais", confidence=1.0)  
    threats = \[(target, RiskAssessment(  
        target\_id="T1", cpa\_nm=0.1, tcpa\_sec=300,  
        encounter\_type="CROSSING", role="GIVE\_WAY",  
        risk\_level="WARNING", recommended\_heading=None  
    ))\]  
    dynamics = VesselDynamics()  
    result = find\_escape\_heading(own, threats, dynamics, prefer\_starboard=True)  
    assert result is not None  
    delta = (result - 0.0 + 360) % 360  
    assert 0 \< delta \< 180, f"Expected Starboard turn but got delta=\{delta\}"
```

### 15.2 Scenario Simulation Tests

A replay engine feeds recorded AIS/GPS data through the full stack and verifies:

- No false positives in open water

- Correct encounter classification for each COLREGs scenario

- Escape heading always achievable given vessel dynamics

- Alarm budget respected across a 4-hour voyage

### 15.3 Hardware-in-the-Loop (Pi)

Run against live Signal K data on the Pi with pypilot in "simulate" mode. Verify:

- 100ms loop completes within 90ms under full load (all 4 threads active)

- Virtual AIS targets appear in AvNav within 500ms of camera detection

- Voice alerts fire within 200ms of risk threshold crossing

- pypilot command round-trip \< 150ms


## 16. Development Roadmap for GitHub

### Phase 1 — Shadow Mode (4 weeks)

- [ ] Implement Layers 1–4 (Sensor, Loop, Dynamics, COLREGs)

- [ ] Run in log-only mode — no alarms, no autopilot commands

- [ ] Replay tool: feed in AIS capture files, verify classifications

- [ ] Unit test coverage \> 80%

### Phase 2 — Advisory Mode (4 weeks)

- [ ] Implement Layer 6 (Human Interface — voice + AvNav widget)

- [ ] Virtual AIS injection working in AvNav

- [ ] Alarm budget system preventing fatigue

- [ ] Sea trial: one 4-hour passage, verify advisory quality

### Phase 3 — Conflict Solver (3 weeks)

- [ ] Implement Layer 5 (Multi-Vessel Conflict Graph)

- [ ] Non-compliant vessel detection and defensive mode

- [ ] Test against harbour simulation with 10+ simultaneous targets

### Phase 4 — Autopilot Integration (4 weeks)

- [ ] Implement Safety Envelope (Layer 7)

- [ ] pypilot command interface

- [ ] \[EXECUTE MANEUVER\] button live

- [ ] Deadman switch testing — confirm human override always wins

- [ ] Sea trial: autopilot nudge test in controlled open water

### Phase 5 — Open Source Release

- [ ] README with clear install instructions

- [ ] Example `safehelm-config.json` for common vessel types

- [ ] Signal K plugin manifest

- [ ] OpenPlotter compatibility verification


## 17. Why This Is Better Than the Research

| Dimension | Research Papers | SafeHelm Design |
| - | - | - |
| **Sensor failure** | Ignored | Explicit degraded modes, confidence decay |
| **Real-time budget** | Unaddressed | 100ms deterministic loop, watchdog |
| **Vessel physics** | Point masses | Turn radius, stopping dist, prop walk |
| **Human factors** | Absent | Alarm budget, one-tap, 2-min silence |
| **Multi-vessel** | One target | Conflict graph, deadlock resolution |
| **Non-compliant** | Assumed compliant | Compliance tracker, defensive mode |
| **Safety layer** | None | CBF barrier function, hard constraints |
| **Deployment** | Server/simulation | Pi 5, Signal K, AvNav, pypilot |
| **Cost** | $0 documented | Pi 5 + camera = ~$150 total |
| **Explainability** | Black box | Named COLREGs rule cited per decision |


**The research describes what to build. This document describes how to build it and what happens when the real world fails to cooperate.**


*d3kOS SafeHelm — Technical Design v1.0 — 2026-05-11*  
*github.com/SkipperDon/d3kOS*

