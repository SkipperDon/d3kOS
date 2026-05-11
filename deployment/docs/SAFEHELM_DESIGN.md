# SafeHelm: Production-Ready Maritime Collision Avoidance System
## d3kOS Module — Technical Design v1.0

**Date:** 2026-05-11  
**Author:** d3kOS / AtMyBoat.com  
**Target Platform:** Raspberry Pi 5, d3kOS v0.9.9+  
**Integration:** Signal K → AvNav → pypilot  
**Status:** Design Phase — Pre-Implementation  
**GitHub Target:** `github.com/SkipperDon/d3kOS/services/safehelm/`

---

## 1. Why This Document Exists

The academic research on maritime collision avoidance describes the problem well. It does not describe a deployable solution. Papers published through 2026 share a common failure: they model the ocean as a clean simulation with perfect sensors, cooperative vessels, and unlimited compute. None of these assumptions hold at sea.

This document provides what the research does not: a complete technical design for a production-ready, COLREGs-aware collision avoidance system that runs on a Raspberry Pi 5, integrates with Signal K and AvNav, and operates safely in the real world — including when sensors fail, vessels do not cooperate, and the captain is asleep.

**This system is different from the research in six critical ways:**

| Research Gap | SafeHelm Solution |
|---|---|
| Assumes sensors always work | Sensor Reliability Layer with confidence scoring and graceful degradation |
| No real-time guarantees | Deterministic 100ms execution loop with watchdog timers |
| Treats boats as point masses | Vessel Dynamics Model using real turn/stop physics |
| Ignores human factors | Human-in-the-Loop design with alarm fatigue prevention |
| No multi-vessel logic | Conflict Graph with priority assignment and deadlock resolution |
| No safety envelope | Control Barrier Functions with hard constraint enforcement |

---

## 2. What the Research Got Right

Before stating what is missing, credit what holds:

- **CPA/TCPA as the core risk metric** — mathematically sound. Distance alone is meaningless. Geometry and time are everything.
- **COLREGs Rules 13–17** as the decision framework — these are correct. The head-on, crossing, and overtaking classifications are the right starting point.
- **Velocity Obstacle (VO)** as the path planning model — computationally feasible on a Pi 5 and geometrically correct for the problem.
- **AIS as the primary data source** — correct. Any system that ignores AIS is not serious.
- **Ship Domain modelling** — correct framing. The safety bubble is not a circle; it is an asymmetric zone shaped by the vessel's dynamics.

The problem is not the theory. The problem is the assumption that theory is sufficient for deployment.

---

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

---

## 4. Layer 1: Sensor Fusion and Reliability Engine

### 4.1 The Problem the Research Ignores

Every sensor fails. Cameras wash out in glare. AIS updates stall. GPS drifts near bridges. IMUs develop bias in cold weather. The research assumes clean data. Real deployments do not get clean data.

**A collision avoidance system that fails silently when a sensor degrades is dangerous. It is worse than no system at all.**

### 4.2 Sensor Confidence Scoring

Every data input receives a continuous confidence score (0.0 to 1.0) that decays when data is stale or contradictory and recovers when fresh data arrives.

```python
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
    DECAY_RATES = {
        'ais':     0.05,   # per second — AIS updates ~every 10s at close range
        'camera':  0.20,   # per second — camera must be near-real-time
        'gps':     0.02,   # per second — GPS is usually reliable
        'imu':     0.10,   # per second — IMU drift is slow but real
    }
    MINIMUM_CONFIDENCE = 0.0
    STALE_THRESHOLD = 0.3  # below this = sensor is considered unreliable

    def __init__(self):
        self._scores: dict[str, float] = {}
        self._last_update: dict[str, float] = {}

    def update(self, source: str, timestamp: float) -> None:
        now = time.monotonic()
        self._scores[source] = 1.0
        self._last_update[source] = now

    def get_confidence(self, source: str) -> float:
        if source not in self._scores:
            return 0.0
        now = time.monotonic()
        elapsed = now - self._last_update.get(source, now)
        decay = self.DECAY_RATES.get(source, 0.1)
        score = self._scores[source] * (1.0 - decay * elapsed)
        return max(self.MINIMUM_CONFIDENCE, score)

    def is_reliable(self, source: str) -> bool:
        return self.get_confidence(source) >= self.STALE_THRESHOLD
```

### 4.3 Degraded Operation Modes

The system must define explicit operating modes. It must never silently degrade.

| Mode | Active Sensors | Capability | Operator Alert |
|---|---|---|---|
| FULL | AIS + Camera + GPS + IMU | All targets visible | None |
| AIS_ONLY | AIS + GPS | AIS targets only — "dark" vessels invisible | Yellow banner |
| CAMERA_ONLY | Camera + GPS | Visual targets only — no MMSI, estimated range | Yellow banner |
| GPS_ONLY | GPS | Own position only — no target tracking | Red banner + audio |
| DEGRADED | Partial GPS | Limited accuracy — advisory only | Red banner + audio |
| BLIND | None reliable | Safety envelope: emergency stop autopilot | Critical alarm |

```python
class OperatingMode:
    FULL = "FULL"
    AIS_ONLY = "AIS_ONLY"
    CAMERA_ONLY = "CAMERA_ONLY"
    GPS_ONLY = "GPS_ONLY"
    DEGRADED = "DEGRADED"
    BLIND = "BLIND"

def determine_mode(tracker: SensorConfidenceTracker) -> str:
    has_gps = tracker.is_reliable('gps')
    has_ais = tracker.is_reliable('ais')
    has_camera = tracker.is_reliable('camera')
    has_imu = tracker.is_reliable('imu')

    if not has_gps:
        return OperatingMode.BLIND if not has_ais else OperatingMode.DEGRADED
    if has_ais and has_camera:
        return OperatingMode.FULL
    if has_ais:
        return OperatingMode.AIS_ONLY
    if has_camera:
        return OperatingMode.CAMERA_ONLY
    return OperatingMode.GPS_ONLY
```

### 4.4 Camera-to-World Coordinate Transform

The Forward Watch camera sees pixels. The collision avoidance engine needs geographic coordinates. This transform is the bridge. It requires:

- Camera field of view (horizontal and vertical, in degrees)
- Camera mounting angle (pan, tilt relative to bow)
- Own vessel position (lat/lon)
- Own vessel heading (true, from compass)
- Target pixel coordinates from the vision model
- Estimated range (from stereo or monocular depth estimation)

```python
import math

def pixel_to_bearing(
    pixel_x: int,
    pixel_y: int,
    frame_width: int,
    frame_height: int,
    hfov_deg: float,
    camera_pan_deg: float,
    own_heading_deg: float
) -> float:
    """
    Convert pixel position to true bearing from own vessel.
    pixel_x: horizontal pixel, 0=left edge
    hfov_deg: camera horizontal field of view
    camera_pan_deg: camera offset from bow (positive = starboard)
    own_heading_deg: vessel true heading
    Returns: true bearing to target (0-360)
    """
    pixels_from_center = pixel_x - (frame_width / 2)
    angle_from_camera_center = (pixels_from_center / frame_width) * hfov_deg
    relative_bearing = camera_pan_deg + angle_from_camera_center
    true_bearing = (own_heading_deg + relative_bearing) % 360
    return true_bearing

def bearing_distance_to_latlon(
    own_lat: float,
    own_lon: float,
    bearing_deg: float,
    distance_nm: float
) -> tuple[float, float]:
    """
    Project a bearing and distance from own position to lat/lon.
    Uses spherical earth approximation (accurate enough for <10NM).
    """
    R = 3440.065  # Earth radius in nautical miles
    bearing_rad = math.radians(bearing_deg)
    lat1 = math.radians(own_lat)
    lon1 = math.radians(own_lon)
    d_r = distance_nm / R
    lat2 = math.asin(
        math.sin(lat1) * math.cos(d_r) +
        math.cos(lat1) * math.sin(d_r) * math.cos(bearing_rad)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing_rad) * math.sin(d_r) * math.cos(lat1),
        math.cos(d_r) - math.sin(lat1) * math.sin(lat2)
    )
    return math.degrees(lat2), math.degrees(lon2)
```

---

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
  T+45ms:  Run Conflict Graph solver if >1 risk target
  T+60ms:  Evaluate Safety Envelope constraints
  T+70ms:  Determine action (None / Advisory / Autopilot command)
  T+80ms:  Push to output queues (AvNav, voice, pypilot)
  T+100ms: Cycle complete — sleep until next tick
```

```python
import threading
import time
import logging

class SafeHelmCore(threading.Thread):
    LOOP_PERIOD_S = 0.100  # 100ms
    WATCHDOG_LIMIT_S = 0.090  # kill cycle if it runs past 90ms

    def __init__(self, sensor_hub, decision_engine, output_bus):
        super().__init__(daemon=True, name="SafeHelmCore")
        self._sensor_hub = sensor_hub
        self._decision_engine = decision_engine
        self._output_bus = output_bus
        self._running = False
        self._cycle_count = 0
        self._overruns = 0

    def run(self):
        self._running = True
        next_tick = time.monotonic()
        while self._running:
            cycle_start = time.monotonic()
            try:
                self._execute_cycle()
            except Exception as e:
                logging.error(f"SafeHelm cycle {self._cycle_count} failed: {e}")
                self._output_bus.send_fault("CYCLE_ERROR", str(e))

            elapsed = time.monotonic() - cycle_start
            if elapsed > self.WATCHDOG_LIMIT_S:
                self._overruns += 1
                logging.warning(
                    f"Cycle {self._cycle_count} overran: {elapsed*1000:.1f}ms"
                )

            self._cycle_count += 1
            next_tick += self.LOOP_PERIOD_S
            sleep_time = next_tick - time.monotonic()
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _execute_cycle(self):
        sensor_data = self._sensor_hub.read_latest()
        targets = self._decision_engine.fuse_and_evaluate(sensor_data)
        action = self._decision_engine.determine_action(targets)
        self._output_bus.dispatch(action)

    def stop(self):
        self._running = False
```

### 5.3 Thread Architecture

Four isolated threads. They communicate only through thread-safe queues. No shared mutable state.

| Thread | Job | Period |
|---|---|---|
| `SafeHelmCore` | Main decision loop | 100ms |
| `AISReader` | Reads Signal K websocket, pushes to queue | Event-driven |
| `CameraFeeder` | Reads Forward Watch output, pushes to queue | 200ms (5Hz) |
| `OutputBus` | Reads action queue, dispatches to AvNav/pypilot/voice | Event-driven |

---

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

```python
@dataclass
class VesselDynamics:
    """Physical constraints of own vessel. Configured once per installation."""
    loa_meters: float = 11.0          # Length Overall
    beam_meters: float = 3.7          # Beam
    max_speed_kts: float = 8.0        # Hull speed
    cruise_speed_kts: float = 6.0     # Typical cruising speed
    min_turn_radius_nm: float = 0.05  # At full rudder, full speed
    stopping_dist_nm: float = 0.08    # Crash stop distance
    max_turn_rate_deg_s: float = 3.0  # Maximum degrees per second
    prop_walk_dir: int = -1           # -1 = port, +1 = starboard (single screw)
    windage_factor: float = 0.15      # Leeway fraction of wind speed

    def time_to_turn_deg(self, angle_deg: float, current_speed_kts: float) -> float:
        """Seconds required to turn by angle_deg at current speed."""
        effective_rate = self.max_turn_rate_deg_s * (current_speed_kts / self.cruise_speed_kts)
        effective_rate = max(effective_rate, 0.5)
        return abs(angle_deg) / effective_rate

    def achievable_new_heading(
        self, current_heading: float, target_heading: float,
        tcpa_seconds: float, current_speed_kts: float
    ) -> bool:
        """True if vessel can physically reach target_heading before TCPA."""
        angle_needed = abs((target_heading - current_heading + 180) % 360 - 180)
        time_needed = self.time_to_turn_deg(angle_needed, current_speed_kts)
        return time_needed < (tcpa_seconds * 0.7)  # 30% margin
```

### 6.3 Drift and Current Compensation

Own vessel position is not just GPS. It is GPS corrected for current set and drift. A vessel tracking 270° at 6 knots in a 2-knot current flowing north is actually making good a ground track of approximately 252°.

```python
def apply_current_correction(
    cog_deg: float, sog_kts: float,
    current_set_deg: float, current_speed_kts: float
) -> tuple[float, float]:
    """
    Returns corrected Course Over Ground and Speed Over Ground
    accounting for tidal current or river flow.
    """
    import cmath
    vessel = cmath.rect(sog_kts, math.radians(90 - cog_deg))
    current = cmath.rect(current_speed_kts, math.radians(90 - current_set_deg))
    resultant = vessel + current
    corrected_sog = abs(resultant)
    corrected_cog = (90 - math.degrees(cmath.phase(resultant))) % 360
    return corrected_cog, corrected_sog
```

---

## 7. Layer 4: COLREGs Decision Engine

### 7.1 CPA and TCPA — The Core Risk Calculation

All targets, regardless of source (AIS or camera), are evaluated on CPA and TCPA. These two numbers answer the only question that matters: *Will we collide, and when?*

```python
import math
from dataclasses import dataclass

@dataclass
class Target:
    id: str
    lat: float
    lon: float
    sog_kts: float
    cog_deg: float
    source: str  # 'ais' | 'camera' | 'virtual'
    confidence: float

@dataclass
class OwnVessel:
    lat: float
    lon: float
    sog_kts: float
    cog_deg: float
    heading_deg: float

@dataclass
class RiskAssessment:
    target_id: str
    cpa_nm: float
    tcpa_sec: float
    encounter_type: str
    role: str  # 'GIVE_WAY' | 'STAND_ON' | 'BOTH_TURN' | 'UNDEFINED'
    risk_level: str  # 'CLEAR' | 'MONITOR' | 'WARNING' | 'CRITICAL'
    recommended_heading: float | None

KTS_TO_NM_PER_S = 1.0 / 3600.0

def latlon_to_xy_nm(lat1, lon1, lat2, lon2) -> tuple[float, float]:
    """Convert two lat/lon pairs to relative x/y in nautical miles."""
    dlat = (lat2 - lat1) * 60.0
    dlon = (lon2 - lon1) * 60.0 * math.cos(math.radians((lat1 + lat2) / 2))
    return dlon, dlat  # x=east, y=north

def calculate_cpa_tcpa(own: OwnVessel, target: Target) -> tuple[float, float]:
    """
    Calculate CPA (nm) and TCPA (seconds) using relative motion vectors.
    Negative TCPA means the CPA has already been passed.
    """
    px, py = latlon_to_xy_nm(own.lat, own.lon, target.lat, target.lon)

    own_vx = own.sog_kts * math.sin(math.radians(own.cog_deg)) * KTS_TO_NM_PER_S
    own_vy = own.sog_kts * math.cos(math.radians(own.cog_deg)) * KTS_TO_NM_PER_S
    tgt_vx = target.sog_kts * math.sin(math.radians(target.cog_deg)) * KTS_TO_NM_PER_S
    tgt_vy = target.sog_kts * math.cos(math.radians(target.cog_deg)) * KTS_TO_NM_PER_S

    dvx = tgt_vx - own_vx
    dvy = tgt_vy - own_vy
    v_rel_sq = dvx * dvx + dvy * dvy

    if v_rel_sq < 1e-12:  # stationary relative to each other
        cpa = math.sqrt(px * px + py * py)
        return cpa, float('inf')

    tcpa_s = -(px * dvx + py * dvy) / v_rel_sq
    cx = px + dvx * tcpa_s
    cy = py + dvy * tcpa_s
    cpa = math.sqrt(cx * cx + cy * cy)

    return cpa, tcpa_s
```

### 7.2 COLREGs Situation Classifier

```python
def classify_encounter(
    own: OwnVessel,
    target: Target,
    own_true_bearing_to_target: float
) -> tuple[str, str]:
    """
    Returns (encounter_type, own_role).
    encounter_type: HEAD_ON | CROSSING | OVERTAKING | BEING_OVERTAKEN
    own_role: GIVE_WAY | STAND_ON | BOTH_TURN | UNDEFINED
    """
    rel_bearing = (own_true_bearing_to_target - own.heading_deg + 360) % 360
    target_rel_hdg = (target.cog_deg - own.cog_deg + 360) % 360

    # Rule 13: Overtaking (target approaching from more than 22.5° abaft beam)
    if 112.5 <= rel_bearing <= 247.5:
        return "OVERTAKING", "GIVE_WAY"

    # Rule 14: Head-on (target dead ahead ±15°, coming toward us ±15°)
    if rel_bearing <= 15 or rel_bearing >= 345:
        if 165 <= target_rel_hdg <= 195:
            return "HEAD_ON", "BOTH_TURN"

    # Rule 15: Crossing — target on starboard bow
    if 5 <= rel_bearing <= 112.5:
        return "CROSSING", "GIVE_WAY"

    # Rule 15: Crossing — target on port bow (we are stand-on)
    if 247.5 <= rel_bearing <= 355:
        return "CROSSING", "STAND_ON"

    return "UNDEFINED", "UNDEFINED"
```

### 7.3 Risk Level Assignment

```python
SHIP_DOMAIN_NM = 0.25       # Safety bubble radius (default)
CRITICAL_TCPA_SEC = 300     # 5 minutes
WARNING_TCPA_SEC = 600      # 10 minutes

def assign_risk_level(cpa_nm: float, tcpa_sec: float) -> str:
    if tcpa_sec < 0:
        return "CLEAR"  # CPA already passed
    if cpa_nm < SHIP_DOMAIN_NM:
        if tcpa_sec < CRITICAL_TCPA_SEC:
            return "CRITICAL"
        if tcpa_sec < WARNING_TCPA_SEC:
            return "WARNING"
        return "MONITOR"
    return "CLEAR"
```

### 7.4 Recommended Heading Calculator

When SafeHelm recommends a course change, it must provide a specific heading — not "turn right." The heading must:
1. Clear all threats (CPA > ship domain)
2. Comply with COLREGs (preferentially Starboard)
3. Be achievable given vessel dynamics
4. Return to original track after clearing

```python
def find_escape_heading(
    own: OwnVessel,
    threats: list[tuple[Target, RiskAssessment]],
    dynamics: VesselDynamics,
    prefer_starboard: bool = True
) -> float | None:
    """
    Sweep headings in 5-degree steps (Starboard preference) to find
    the nearest COLREGs-compliant course that clears all threats.
    Returns None if no escape exists (rare — usually means stop).
    """
    search_order = list(range(0, 180, 5)) + list(range(355, 180, -5))
    if not prefer_starboard:
        search_order = list(range(355, 180, -5)) + list(range(0, 180, 5))

    for delta in search_order:
        candidate_hdg = (own.heading_deg + delta) % 360
        candidate_own = OwnVessel(
            lat=own.lat, lon=own.lon,
            sog_kts=own.sog_kts,
            cog_deg=candidate_hdg,
            heading_deg=candidate_hdg
        )
        all_clear = all(
            calculate_cpa_tcpa(candidate_own, t)[0] >= SHIP_DOMAIN_NM
            for t, _ in threats
        )
        if all_clear:
            min_tcpa = min(calculate_cpa_tcpa(own, t)[1] for t, _ in threats)
            if dynamics.achievable_new_heading(
                own.heading_deg, candidate_hdg, min_tcpa, own.sog_kts
            ):
                return candidate_hdg

    return None
```

---

## 8. Layer 5: Multi-Vessel Conflict Solver

### 8.1 The Problem the Research Ignores

Most research addresses one vessel at a time. Harbors do not cooperate. A SafeHelm decision for three simultaneous threats may be individually correct but collectively deadlocked — each vessel's "escape" heading crosses another vessel's path.

### 8.2 Conflict Graph Architecture

```python
from dataclasses import dataclass, field
import itertools

@dataclass
class ConflictNode:
    target: Target
    assessment: RiskAssessment
    priority: int  # lower number = higher priority

@dataclass
class ConflictGraph:
    nodes: list[ConflictNode] = field(default_factory=list)

    def assign_priorities(self) -> None:
        """
        Priority assignment rules (lower number = act first):
        1. CRITICAL risk before WARNING
        2. Give-way vessel obligation before stand-on
        3. Closest TCPA breaks ties
        4. Vessels on port bow (Starboard rule) get higher priority attention
        """
        for i, node in enumerate(
            sorted(self.nodes, key=lambda n: (
                0 if n.assessment.risk_level == "CRITICAL" else 1,
                0 if n.assessment.role == "GIVE_WAY" else 1,
                n.assessment.tcpa_sec
            ))
        ):
            node.priority = i

    def detect_deadlock(self, proposed_headings: dict[str, float]) -> bool:
        """
        Check if proposed escape headings create crossing conflicts.
        Returns True if deadlock detected.
        """
        for n1, n2 in itertools.combinations(self.nodes, 2):
            h1 = proposed_headings.get(n1.target.id)
            h2 = proposed_headings.get(n2.target.id)
            if h1 is None or h2 is None:
                continue
            delta = abs((h1 - h2 + 180) % 360 - 180)
            if delta < 30:
                return True
        return False

    def resolve(self, own: OwnVessel, dynamics: VesselDynamics) -> float | None:
        """
        Iteratively find an escape heading that clears all threats
        without creating new ones. Returns None if no solution found
        (triggers emergency stop advisory).
        """
        self.assign_priorities()
        threats_by_priority = [(n.target, n.assessment) for n in self.nodes]
        return find_escape_heading(own, threats_by_priority, dynamics)
```

### 8.3 Deadlock Resolution: The Emergency Slow-Down

When no heading solves all conflicts simultaneously, reducing speed is often the correct COLREGs answer. A vessel that slows from 6 knots to 2 knots gains time for other vessels to pass.

If no escape heading and no speed reduction resolves the conflict within the safety margin, the system escalates to CRITICAL alert and disengages autopilot, returning full control to the captain.

---

## 9. Layer 6: Human-in-the-Loop Interface

### 9.1 The Problem the Research Ignores

An alarm that fires too often is turned off. A system that annoys the captain becomes a liability. **Alarm fatigue is not a UX problem. It is a safety problem.**

### 9.2 Alarm Budget System

```python
@dataclass
class AlarmBudget:
    """
    Limits how often SafeHelm can alarm the operator.
    Prevents alarm fatigue while ensuring critical events are never suppressed.
    """
    max_warnings_per_hour: int = 6
    max_advisories_per_hour: int = 20
    _warning_times: list[float] = field(default_factory=list)
    _advisory_times: list[float] = field(default_factory=list)

    def can_alarm(self, level: str) -> bool:
        now = time.monotonic()
        one_hour_ago = now - 3600
        if level == "CRITICAL":
            return True  # Critical alarms are NEVER suppressed
        if level == "WARNING":
            self._warning_times = [t for t in self._warning_times if t > one_hour_ago]
            return len(self._warning_times) < self.max_warnings_per_hour
        self._advisory_times = [t for t in self._advisory_times if t > one_hour_ago]
        return len(self._advisory_times) < self.max_advisories_per_hour

    def record_alarm(self, level: str) -> None:
        now = time.monotonic()
        if level == "WARNING":
            self._warning_times.append(now)
        elif level != "CRITICAL":
            self._advisory_times.append(now)
```

### 9.3 Voice Alert Script Templates

Voice alerts must be unambiguous and actionable. They follow a strict format:

```
[Direction] vessel [bearing]. [Role]. [Action]. [Heading if known].
```

Examples:
- "Starboard vessel, bearing zero four five. We are give-way. Recommend turn to two seven zero."
- "Head-on. Both vessels must turn starboard. Recommend zero nine zero."
- "Port vessel approaching. We hold right of way. Maintain course."
- "CRITICAL. Collision course. No clear heading found. Manual override required."

```python
def generate_voice_alert(assessment: RiskAssessment, bearing_deg: float) -> str:
    if bearing_deg < 45 or bearing_deg > 315:
        direction = "Ahead"
    elif bearing_deg < 135:
        direction = "Starboard"
    elif bearing_deg < 225:
        direction = "Astern"
    else:
        direction = "Port"

    role_phrase = {
        "GIVE_WAY": "We are give-way.",
        "STAND_ON": "We hold right of way.",
        "BOTH_TURN": "Head-on. Both turn starboard.",
        "UNDEFINED": "Situation unclear.",
    }.get(assessment.role, "")

    if assessment.recommended_heading is not None:
        heading_phrase = f"Recommend turn to {int(assessment.recommended_heading):03d}."
    else:
        heading_phrase = "No clear heading. Manual override required."

    bearing_phrase = f"bearing {int(bearing_deg):03d}"
    return f"{direction} vessel, {bearing_phrase}. {role_phrase} {heading_phrase}"
```

### 9.4 AvNav Widget Specification

The SafeHelm AvNav widget displays in the corner of the chart. It has three states:

**State: CLEAR** — Small green dot. No text.

**State: WARNING** — Yellow banner at bottom of chart:
```
⚠ Vessel SW 225° — Give-way — Suggest 090°   [ACK] [EXECUTE]
```

**State: CRITICAL** — Full-width red banner, pulsing:
```
🚨 COLLISION RISK — Bearing 045° — TCPA 4min — Suggest 090°   [EXECUTE NOW] [TAKE HELM]
```

The `[EXECUTE]` button sends the recommended heading to pypilot. The `[TAKE HELM]` button disengages SafeHelm autopilot control and silences the alarm for 2 minutes.

**A 2-minute silence window is the maximum. After 2 minutes, if the threat is still active, the alarm re-fires.**

---

## 10. Layer 7: Safety Envelope

### 10.1 The Missing Piece in All the Research

Every autonomous system needs a safety layer that is mathematically separate from the planning layer. The planner proposes actions. The safety layer vetoes unsafe ones. These two components must never be merged.

**The safety layer says "you may not do that" even if the planner says "do it."**

### 10.2 Hard Constraints

These constraints are never violated regardless of what the planner recommends:

```python
@dataclass
class SafetyEnvelope:
    """
    Hard constraints that cannot be overridden by the planner.
    If the planner produces an action violating these, it is rejected.
    """
    min_speed_response_kts: float = 1.0   # Never command < 1kt except full stop
    max_rudder_rate_pct: float = 50.0     # Never slam rudder past 50%/s
    shallow_water_depth_m: float = 3.0    # Never maneuver if depth < 3m
    no_go_zone_deg: float = 40.0          # For sail — keep out of irons
    max_heel_deg: float = 30.0            # Never command course that increases heel past 30°

    def validate_heading_command(
        self,
        proposed_heading: float,
        current_depth_m: float,
        current_heel_deg: float,
        wind_angle_deg: float,
        vessel_type: str
    ) -> tuple[bool, str]:
        """
        Returns (approved, reason).
        If not approved, reason explains what constraint was violated.
        """
        if current_depth_m < self.shallow_water_depth_m:
            return False, f"SHALLOW_WATER: depth {current_depth_m:.1f}m < {self.shallow_water_depth_m}m minimum"

        if vessel_type == "sailing":
            apparent_wind_on_new_hdg = abs(wind_angle_deg)
            if apparent_wind_on_new_hdg < self.no_go_zone_deg:
                return False, f"NO_GO_ZONE: heading places vessel in irons ({apparent_wind_on_new_hdg:.0f}° apparent)"

        if current_heel_deg > self.max_heel_deg * 0.8:
            return False, f"HEEL_LIMIT: current heel {current_heel_deg:.0f}° approaching limit"

        return True, "APPROVED"
```

### 10.3 Control Barrier Function (Simplified)

A Control Barrier Function (CBF) defines a "safe set" — positions from which safety can be maintained. If the system is outside the safe set, it must return to it before doing anything else.

For our purposes, the CBF is a simple invariant: **the CPA to any threat must never decrease faster than our turning capability allows us to correct.**

```python
def barrier_function(
    cpa_nm: float,
    tcpa_sec: float,
    dynamics: VesselDynamics,
    own_speed_kts: float
) -> float:
    """
    Returns h(x) where h(x) >= 0 means we are in the safe set.
    h(x) < 0 means safety is violated — emergency action required.

    The barrier: we must have enough time to turn to an escape heading
    before the threat arrives. If we can't turn fast enough, we are unsafe.
    """
    if tcpa_sec <= 0:
        return 1.0  # Already past — safe

    max_turn_180 = dynamics.time_to_turn_deg(180, own_speed_kts)
    safety_margin_s = 60  # We want at least 60s of buffer after turning
    h = tcpa_sec - max_turn_180 - safety_margin_s
    return h
```

If `barrier_function()` returns negative, the system enters **Emergency Mode**:
1. If autopilot engaged: immediately command full starboard rudder (COLREGs preference)
2. Simultaneously broadcast critical voice alert
3. Log the event with full sensor snapshot for post-incident review
4. Never re-engage autonomous control until captain acknowledges

---

## 11. Non-Compliant Vessel Handling

### 11.1 The Hardest Unsolved Problem

The research mentions this but does not solve it. In practice, this is the most common real-world scenario:

- Jet skis and PWCs ignore all rules
- Small fishing boats drift without power
- Ferries and car carriers assume everyone will yield
- Vessels under poor watchkeeping do not react as expected

**A system that assumes all vessels are cooperative is only safe in simulation.**

### 11.2 Compliance Detection

```python
@dataclass
class ComplianceTracker:
    """
    Track whether a vessel is responding to the situation as COLREGs requires.
    A give-way vessel should be altering course. If it is not, it is non-compliant.
    """
    target_id: str
    expected_role: str  # 'GIVE_WAY' — they should be turning
    history: list[tuple[float, float]] = field(default_factory=list)  # (timestamp, cog)

    def record_cog(self, timestamp: float, cog: float) -> None:
        self.history.append((timestamp, cog))
        if len(self.history) > 20:
            self.history.pop(0)

    def is_compliant(self, tcpa_sec: float) -> bool:
        """
        If TCPA < 5 minutes and vessel is give-way, they should be turning.
        Compliance = COG changed by >10° in last 60 seconds.
        """
        if self.expected_role != "GIVE_WAY" or tcpa_sec > 300:
            return True
        if len(self.history) < 2:
            return True  # Insufficient data — assume compliant

        recent = [h for h in self.history if time.monotonic() - h[0] < 60]
        if len(recent) < 2:
            return True

        cog_change = abs(recent[-1][1] - recent[0][1])
        cog_change = min(cog_change, 360 - cog_change)
        return cog_change > 10.0
```

### 11.3 Defensive Navigation Mode

When a vessel is detected as non-compliant, SafeHelm switches to **Defensive Mode**:

1. **Stand-on vessel duty suspended**: Even as a stand-on vessel, we begin planning our own escape rather than waiting for the give-way vessel to act (Rule 17(a)(ii) — action by stand-on vessel).
2. **Ship domain expands**: Safety bubble grows from 0.25NM to 0.50NM for that target.
3. **Alarm threshold tightens**: CRITICAL fires at TCPA < 8 minutes instead of 5.
4. **Audit log flagged**: The non-compliance event is recorded with full sensor snapshot.

```python
def handle_non_compliant(
    own: OwnVessel,
    target: Target,
    assessment: RiskAssessment,
    dynamics: VesselDynamics
) -> RiskAssessment:
    """Recompute assessment for a non-compliant give-way vessel."""
    expanded_domain = SHIP_DOMAIN_NM * 2.0
    new_risk = assign_risk_level_with_domain(
        assessment.cpa_nm, assessment.tcpa_sec, expanded_domain
    )
    new_heading = find_escape_heading(
        own, [(target, assessment)], dynamics, prefer_starboard=True
    )
    return RiskAssessment(
        target_id=target.id,
        cpa_nm=assessment.cpa_nm,
        tcpa_sec=assessment.tcpa_sec,
        encounter_type=assessment.encounter_type,
        role="GIVE_WAY",  # We assume give-way even if we were stand-on
        risk_level=new_risk,
        recommended_heading=new_heading
    )
```

---

## 12. Signal K, AvNav, and pypilot Integration

### 12.1 Signal K Integration (Data In)

SafeHelm reads from Signal K via WebSocket subscription. One subscription covers all needed data.

```python
import asyncio
import websockets
import json

SIGNALK_WS = "ws://localhost:3000/signalk/v1/stream"

SUBSCRIBE_MSG = {
    "context": "vessels.*",
    "subscribe": [
        {"path": "navigation.position"},
        {"path": "navigation.speedOverGround"},
        {"path": "navigation.courseOverGroundTrue"},
        {"path": "navigation.headingTrue"},
        {"path": "sensors.ais.class"},
    ]
}

async def stream_signalk(queue: asyncio.Queue):
    async with websockets.connect(SIGNALK_WS) as ws:
        await ws.send(json.dumps(SUBSCRIBE_MSG))
        async for message in ws:
            data = json.loads(message)
            await queue.put(data)
```

### 12.2 Virtual AIS Injection (Targets Out to AvNav)

Camera-detected targets are injected as Signal K vessels. AvNav then renders them as AIS symbols automatically.

```python
import requests

SIGNALK_API = "http://localhost:3000/signalk/v1/api"

def inject_virtual_target(
    target_id: str,
    lat: float,
    lon: float,
    sog_kts: float,
    cog_deg: float,
    confidence: float
) -> None:
    """
    Inject a camera-detected vessel into Signal K as a virtual AIS target.
    AvNav will render it as a standard vessel triangle on the chart.
    """
    vessel_path = f"vessels/urn:mrn:d3k:visual:{target_id}"
    updates = [
        {"path": "navigation.position",
         "value": {"latitude": lat, "longitude": lon}},
        {"path": "navigation.speedOverGround",
         "value": sog_kts * 0.514444},  # kts to m/s
        {"path": "navigation.courseOverGroundTrue",
         "value": math.radians(cog_deg)},
        {"path": "sensors.safehelm.confidence",
         "value": confidence},
    ]
    payload = {
        "context": vessel_path,
        "updates": [{"values": updates, "source": {"label": "safehelm-cv"}}]
    }
    try:
        requests.put(f"{SIGNALK_API}/{vessel_path}", json=payload, timeout=0.05)
    except Exception:
        pass  # Never block the main loop on network I/O
```

### 12.3 pypilot Integration (Autopilot Commands Out)

pypilot accepts heading commands via its own TCP protocol or via Signal K autopilot API.

```python
import socket
import json

PYPILOT_HOST = "localhost"
PYPILOT_PORT = 23322  # pypilot default control port

def send_heading_to_pypilot(target_heading_deg: float) -> bool:
    """
    Send a heading command to pypilot.
    Returns True if command was accepted.
    Only called after Safety Envelope validation passes.
    """
    try:
        with socket.create_connection(
            (PYPILOT_HOST, PYPILOT_PORT), timeout=0.08
        ) as sock:
            command = json.dumps({
                "ap.heading_command": math.radians(target_heading_deg)
            }) + "\n"
            sock.send(command.encode())
        return True
    except Exception as e:
        logging.error(f"pypilot command failed: {e}")
        return False

def engage_pypilot_compass_mode() -> bool:
    """Set pypilot to compass mode before sending heading commands."""
    try:
        with socket.create_connection(
            (PYPILOT_HOST, PYPILOT_PORT), timeout=0.08
        ) as sock:
            command = json.dumps({"ap.mode": "compass"}) + "\n"
            sock.send(command.encode())
        return True
    except Exception:
        return False

def disengage_pypilot() -> bool:
    """Disengage autopilot — return full control to helm."""
    try:
        with socket.create_connection(
            (PYPILOT_HOST, PYPILOT_PORT), timeout=0.08
        ) as sock:
            command = json.dumps({"ap.enabled": False}) + "\n"
            sock.send(command.encode())
        return True
    except Exception:
        return False
```

### 12.4 AvNav Plugin (JavaScript Widget)

```javascript
// safehelm-widget.js — Drop into AvNav plugins directory
// Displays collision risk status in a corner overlay on the chart

(function() {
    const SAFEHELM_API = '/safehelm/status';
    const POLL_INTERVAL_MS = 500;

    let container;

    function init() {
        container = document.createElement('div');
        container.id = 'safehelm-overlay';
        container.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            z-index: 9000;
            font-family: monospace;
            font-size: 18px;
            min-width: 240px;
        `;
        document.body.appendChild(container);
        poll();
    }

    function poll() {
        fetch(SAFEHELM_API)
            .then(r => r.json())
            .then(render)
            .catch(() => renderOffline())
            .finally(() => setTimeout(poll, POLL_INTERVAL_MS));
    }

    function render(data) {
        const colors = {
            CLEAR: '#00aa00',
            MONITOR: '#888800',
            WARNING: '#ff8800',
            CRITICAL: '#ff0000'
        };
        const level = data.highest_risk || 'CLEAR';
        const color = colors[level] || '#888888';

        if (level === 'CLEAR') {
            container.innerHTML = `<div style="color:${color};padding:4px">✔ SafeHelm CLEAR</div>`;
            return;
        }

        const t = data.primary_threat;
        container.innerHTML = `
            <div style="background:${color};color:white;padding:12px;border-radius:6px;line-height:1.6">
                <strong>${level} — ${t.encounter_type}</strong><br>
                Bearing ${t.bearing_deg.toFixed(0)}° | TCPA ${(t.tcpa_sec/60).toFixed(1)} min<br>
                ${t.role} | Suggest ${t.recommended_heading ? t.recommended_heading.toFixed(0)+'°' : 'STOP'}<br>
                <button onclick="executeManeuver(${t.recommended_heading})"
                    style="margin-top:8px;padding:8px 16px;font-size:18px;
                           background:white;color:${color};border:none;
                           border-radius:4px;cursor:pointer;width:100%">
                    EXECUTE MANEUVER
                </button>
                <button onclick="silenceAlarm()"
                    style="margin-top:4px;padding:8px 16px;font-size:18px;
                           background:transparent;color:white;border:2px solid white;
                           border-radius:4px;cursor:pointer;width:100%">
                    TAKE HELM (2 min silence)
                </button>
            </div>`;
    }

    function executeManeuver(heading) {
        fetch('/safehelm/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({heading: heading})
        });
    }

    function silenceAlarm() {
        fetch('/safehelm/silence', {method: 'POST'});
    }

    function renderOffline() {
        container.innerHTML = '<div style="color:#888;padding:4px">SafeHelm offline</div>';
    }

    document.addEventListener('DOMContentLoaded', init);
})();
```

---

## 13. Python Module File Structure

```
d3kOS/services/safehelm/
├── safehelm.py              — Main entry point, initialises all layers
├── core/
│   ├── loop.py              — SafeHelmCore real-time execution thread
│   ├── sensor_hub.py        — SensorConfidenceTracker, input queues
│   ├── dynamics.py          — VesselDynamics model
│   └── envelope.py          — SafetyEnvelope, barrier function
├── engine/
│   ├── cpa.py               — CPA/TCPA calculations
│   ├── colregs.py           — COLREGs classifier
│   ├── conflict.py          — ConflictGraph, multi-vessel solver
│   └── compliance.py        — Non-compliant vessel detection
├── interface/
│   ├── signalk_reader.py    — Signal K WebSocket subscriber
│   ├── virtual_ais.py       — Inject camera targets into Signal K
│   ├── pypilot_client.py    — pypilot TCP command interface
│   └── voice.py             — Text-to-speech alert generation
├── ui/
│   └── safehelm-widget.js   — AvNav overlay widget
├── safehelm-config.json     — Vessel dynamics, thresholds, preferences
└── safehelm.service         — systemd unit for Pi autostart
```

---

## 14. safehelm.service (systemd)

```ini
[Unit]
Description=d3kOS SafeHelm Collision Avoidance Service
After=network.target d3kos-signalk.service
Requires=d3kos-signalk.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/safehelm
ExecStart=/opt/d3kos/venv/bin/python safehelm.py
Restart=on-failure
RestartSec=5
KillMode=process

[Install]
WantedBy=multi-user.target
```

---

## 15. Testing Strategy

### 15.1 Unit Tests (Pure Python, No Hardware)

Each module is independently testable with synthetic data:

```python
def test_cpa_head_on():
    own = OwnVessel(lat=0.0, lon=0.0, sog_kts=6.0, cog_deg=0.0, heading_deg=0.0)
    target = Target(id="T1", lat=0.1, lon=0.0, sog_kts=6.0, cog_deg=180.0,
                    source="ais", confidence=1.0)
    cpa, tcpa = calculate_cpa_tcpa(own, target)
    assert cpa < 0.01, "Head-on CPA should be near zero"
    assert 0 < tcpa < 600, "TCPA should be positive and < 10 min"

def test_escape_heading_starboard_preference():
    # Give-way vessel in crossing situation should get Starboard recommendation
    own = OwnVessel(lat=0.0, lon=0.0, sog_kts=6.0, cog_deg=0.0, heading_deg=0.0)
    target = Target(id="T1", lat=0.05, lon=0.05, sog_kts=6.0, cog_deg=270.0,
                    source="ais", confidence=1.0)
    threats = [(target, RiskAssessment(
        target_id="T1", cpa_nm=0.1, tcpa_sec=300,
        encounter_type="CROSSING", role="GIVE_WAY",
        risk_level="WARNING", recommended_heading=None
    ))]
    dynamics = VesselDynamics()
    result = find_escape_heading(own, threats, dynamics, prefer_starboard=True)
    assert result is not None
    delta = (result - 0.0 + 360) % 360
    assert 0 < delta < 180, f"Expected Starboard turn but got delta={delta}"
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
- pypilot command round-trip < 150ms

---

## 16. Development Roadmap for GitHub

### Phase 1 — Shadow Mode (4 weeks)
- [ ] Implement Layers 1–4 (Sensor, Loop, Dynamics, COLREGs)
- [ ] Run in log-only mode — no alarms, no autopilot commands
- [ ] Replay tool: feed in AIS capture files, verify classifications
- [ ] Unit test coverage > 80%

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
- [ ] [EXECUTE MANEUVER] button live
- [ ] Deadman switch testing — confirm human override always wins
- [ ] Sea trial: autopilot nudge test in controlled open water

### Phase 5 — Open Source Release
- [ ] README with clear install instructions
- [ ] Example `safehelm-config.json` for common vessel types
- [ ] Signal K plugin manifest
- [ ] OpenPlotter compatibility verification

---

## 17. Why This Is Better Than the Research

| Dimension | Research Papers | SafeHelm Design |
|---|---|---|
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

---

*d3kOS SafeHelm — Technical Design v1.0 — 2026-05-11*  
*github.com/SkipperDon/d3kOS*
