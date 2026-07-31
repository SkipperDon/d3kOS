#!/usr/bin/env python3
"""
LAB-SIM — Signal K scenario injector for d3kOS lab validation.

Purpose
-------
The lab Pi has no NMEA 2000 devices, no depth sounder, no GPS and no AIS dongle.
That made every gauge/alarm/depth/AIS fix untestable in the lab, which pushed all
validation onto boat trips, where the boat's own hardware was also broken. Nothing
could ever be proven. See V09994_FIX_PLAN.md section 5.1.

LAB-SIM injects synthetic Signal K deltas so the dashboard cannot tell the lab Pi
from the real boat. Everything downstream of Signal K becomes desk-testable.

Design constraints (deliberate)
-------------------------------
1. NEVER installed on the Pi. This file lives in the repo on the workstation and
   is streamed into the Pi's python3 over SSH stdin. Nothing is written to the
   Pi's disk, so it can never clone onto the boat card. A simulator that could
   start accidentally on a live vessel is a safety hazard.
2. Every injected value carries $source = "LAB-SIM". Simulated data is therefore
   always distinguishable from real sensor data in Signal K.
3. Standard library + websocket-client only. websocket-client is already present
   on the Pi; nothing is installed.

Usage (from the workstation)
----------------------------
    ssh -i ~/.ssh/id_d3kos d3kos@192.168.1.237 python3 - <scenario> < labsim.py
    ssh -i ~/.ssh/id_d3kos d3kos@192.168.1.237 python3 - list < labsim.py

Or use run.sh, which wraps the above.
"""

import json
import math
import sys
import time

WS_URL = "ws://localhost:8099/signalk/v1/stream?subscribe=none"
SOURCE = "LAB-SIM"

# ---------------------------------------------------------------------------
# Unit helpers — Signal K is strictly SI. Getting these wrong is the single
# easiest way to produce a test that "passes" against the wrong number.
# ---------------------------------------------------------------------------

def psi(v):
    """pounds per square inch -> pascals"""
    return v * 6894.757


def degf(v):
    """degrees Fahrenheit -> kelvin"""
    return (v - 32.0) * 5.0 / 9.0 + 273.15


def rpm(v):
    """revolutions per minute -> hertz (SK stores engine revs in Hz)"""
    return v / 60.0


def knots(v):
    """knots -> metres per second"""
    return v * 0.514444


def feet(v):
    """feet -> metres"""
    return v * 0.3048


def deg(v):
    """degrees -> radians"""
    return v * math.pi / 180.0


# ---------------------------------------------------------------------------
# Reference values — Monterey 265 / MerCruiser 454 MAG MPI.
# Sourced from MERCRUISER_454_MAG_MPI_SM_AI.md and the d3kOS diag thresholds.
# ---------------------------------------------------------------------------

OIL_NORMAL_PSI = 42.0     # healthy cruising oil pressure
OIL_CRIT_PSI = 3.0        # below the d3kOS crit threshold of 4 psi
COOLANT_NORMAL_F = 165.0  # thermostat is 160 F
COOLANT_HOT_F = 220.0
IDLE_RPM = 650.0
CRUISE_RPM = 2400.0

# Every Signal K path the d3kOS dashboard actually subscribes to.
# Read from the deployed instruments.js on 2026-07-31 — do not edit from memory.
# The dashboard reads BOTH propulsion.0.* and propulsion.port.* (the BUG-29
# alias fix), so scenarios publish port.* and the alias layer handles the rest.
DASHBOARD_PATHS = [
    "propulsion.port.revolutions",
    "propulsion.port.oilPressure",
    "propulsion.port.coolantTemperature",
    "propulsion.port.temperature",
    "propulsion.port.drive.trimState",
    "propulsion.port.trimTabPosition",
    "tanks.fuel.0.currentLevel",
    "electrical.batteries.0.voltage",
    "environment.depth.belowTransducer",
    "environment.depth.belowKeel",
    "navigation.position",
    "navigation.speedOverGround",
    "navigation.courseOverGroundTrue",
]


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------

class Injector:
    """Holds one websocket to Signal K and pushes deltas down it."""

    def __init__(self, url=WS_URL):
        import websocket  # already present on the Pi
        self.ws = websocket.create_connection(url, timeout=10)
        self.url = url

    def send(self, values):
        """values: dict of {signalk_path: value}"""
        delta = {
            "updates": [{
                "$source": SOURCE,
                "values": [{"path": p, "value": v} for p, v in values.items()],
            }]
        }
        self.ws.send(json.dumps(delta))

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def run_steps(steps, hold=0.0):
    """
    Execute a scenario.

    steps: list of (delay_before_seconds, description, values_dict)
    hold:  seconds to keep republishing the final frame, so the value does not
           go stale in Signal K while a human inspects the dashboard.
    """
    inj = Injector()
    last = {}
    try:
        for delay, desc, values in steps:
            if delay:
                time.sleep(delay)
            if values:
                inj.send(values)
                last = values
            stamp = time.strftime("%H:%M:%S")
            print(f"[{stamp}] {desc}", flush=True)

        if hold and last:
            print(f"--- holding final state for {hold:.0f}s "
                  f"(republishing every 2s so it does not go stale) ---",
                  flush=True)
            end = time.time() + hold
            while time.time() < end:
                inj.send(last)
                time.sleep(2)
    finally:
        inj.close()
    print("--- scenario complete ---", flush=True)


# ---------------------------------------------------------------------------
# Scenarios — one per bug or bug cluster
# ---------------------------------------------------------------------------

def engine_running(oil_psi=OIL_NORMAL_PSI, r=CRUISE_RPM, cool_f=COOLANT_NORMAL_F,
                   fuel=0.62, volts=13.8):
    """A healthy running-engine frame."""
    return {
        "propulsion.port.revolutions": rpm(r),
        "propulsion.port.oilPressure": psi(oil_psi),
        # NB: the dashboard has NO handler for propulsion.port.coolantTemperature.
        # instruments.js aliases only revolutions/oilPressure/temperature/trimState.
        # Publish BOTH: .temperature is what the dashboard reads today, and
        # .coolantTemperature is what Signal K produces from N2K PGN 127489.
        "propulsion.port.temperature": degf(cool_f),
        "propulsion.port.coolantTemperature": degf(cool_f),
        "propulsion.port.drive.trimState": 0.15,
        "tanks.fuel.0.currentLevel": fuel,
        "electrical.batteries.0.voltage": volts,
    }


def sc_boot_engine_off():
    """
    BUG-45 — false critical alerts on Pi boot with the engine off.

    The Pangoo reports 0 psi / 0 rpm when the engine is not running. Before the
    fix, that tripped an immediate CRITICAL overlay on every boot. The fix is a
    30 s debounce from Signal K first connect.
    """
    frame = {
        "propulsion.port.revolutions": 0.0,
        "propulsion.port.oilPressure": 0.0,
        "propulsion.port.temperature": degf(68.0),
        "propulsion.port.coolantTemperature": degf(68.0),
        "tanks.fuel.0.currentLevel": 0.55,
        "electrical.batteries.0.voltage": 12.5,
    }
    return [
        (0, "ENGINE OFF — oil 0 psi, rpm 0. Reload the dashboard NOW.", frame),
        (10, "t+10s  (inside 30s debounce) — expect NO critical overlay", frame),
        (10, "t+20s  (inside 30s debounce) — expect NO critical overlay", frame),
        (15, "t+35s  (debounce expired)", frame),
    ], 30.0


def sc_oil_critical():
    """
    BUG-42 (acknowledge latch) and BUG-44 (voice alarm).

    Runs the engine healthy, drops oil pressure below the 4 psi crit threshold
    and holds it there. The operator must be able to press ACKNOWLEDGE once and
    have the overlay stay dismissed, and the alert must SPEAK.
    """
    ok = engine_running()
    bad = engine_running(oil_psi=OIL_CRIT_PSI)
    return [
        (0, "Engine healthy — oil 42 psi, 2400 rpm. Let gauges settle.", ok),
        (5, "still healthy", ok),
        (5, f"*** OIL PRESSURE -> {OIL_CRIT_PSI} psi (CRITICAL) ***", bad),
        (3, "WATCH: overlay appears AND espeak speaks (BUG-44)", bad),
        (5, "NOW PRESS 'ACKNOWLEDGE' — it must STAY dismissed (BUG-42)", bad),
        (10, "still critical — overlay must NOT have re-appeared", bad),
        (10, "still critical — overlay must NOT have re-appeared", bad),
    ], 40.0


def sc_oil_recover():
    """
    BUG-42 re-arm. After acknowledging, oil pressure recovers above threshold.
    The latch must reset so a SUBSEQUENT drop alarms again.
    """
    bad = engine_running(oil_psi=OIL_CRIT_PSI)
    ok = engine_running()
    return [
        (0, "Oil CRITICAL — acknowledge the overlay when it appears", bad),
        (12, "OIL RECOVERING -> 42 psi. Latch must reset.", ok),
        (8, "healthy", ok),
        (5, "*** SECOND DROP -> critical. Overlay MUST fire again. ***", bad),
        (10, "if no overlay appeared, the ack latch never reset — FAIL", bad),
    ], 25.0


def sc_depth_sweep():
    """
    BUG-30 — dashboard read belowKeel, Signal K publishes belowTransducer.
    Replays the depths actually recorded during the S112 cruise.
    """
    seq = [3.80, 1.79, 1.08, 1.04, 0.90, 2.40, 3.80]
    steps = [(0, "Depth sweep — replaying S112 cruise depths", None)]
    for d in seq:
        steps.append((4, f"depth {d:.2f} m  ({d / 0.3048:.1f} ft)",
                      {"environment.depth.belowTransducer": d}))
    return steps, 20.0


def sc_throttle_step():
    """
    BUG-13 — speed gauge flickers between steady-state and live value during
    throttle transitions. Steps SOG hard, which is what triggered it on the boat.
    """
    seq = [0.0, 3.11, 3.17, 1.19, 4.28, 2.39, 0.0]
    steps = [(0, "Throttle steps — watch the speed tile for flicker", None)]
    for kt in seq:
        steps.append((5, f"SOG {kt:.2f} kt",
                      {"navigation.speedOverGround": knots(kt),
                       "propulsion.port.revolutions": rpm(600 + kt * 700)}))
    return steps, 15.0


def sc_stationary_cog():
    """
    BUG-15 — course heading flashes different directions while stationary.
    At near-zero speed COG is mathematically meaningless and jitters wildly.
    """
    steps = [(0, "Stationary, noisy COG — watch the heading tile", None)]
    headings = [12, 187, 45, 302, 96, 271, 5, 154, 220, 88]
    for h in headings:
        steps.append((3, f"COG {h}deg at 0.04 kt",
                      {"navigation.courseOverGroundTrue": deg(h),
                       "navigation.speedOverGround": knots(0.04),
                       "navigation.position": {"latitude": 42.8947,
                                               "longitude": -79.6222}}))
    return steps, 15.0


def sc_units():
    """
    BUG-43 — Imperial/Metric selection has no effect on gauges.
    Publishes values with easy round numbers in BOTH systems so a wrong unit is
    obvious at a glance. Operator preference is Imperial.
    """
    frame = engine_running(cool_f=212.0)          # 212 F = 100 C exactly
    frame["environment.depth.belowTransducer"] = feet(10.0)  # 10.0 ft = 3.048 m
    return [
        (0, "Coolant 212F / 100C, depth 10.0ft / 3.05m", frame),
        (0, "IMPERIAL expected: 212 F and 10.0 ft", frame),
        (0, "If it shows 100 / 3.0 the unit setting is being ignored (BUG-43)",
         frame),
    ], 60.0


def sc_cruise():
    """
    Full healthy cruise — everything live at once. General smoke test that the
    whole gauge cluster renders. Use this first to confirm the rig works.
    """
    steps = [(0, "Full cruise — all gauges should come alive", None)]
    for i in range(24):
        t = i / 23.0
        steps.append((3, f"cruise t={i * 3}s", {
            "propulsion.port.revolutions": rpm(1800 + 700 * math.sin(t * 6)),
            "propulsion.port.oilPressure": psi(38 + 6 * math.sin(t * 4)),
            "propulsion.port.coolantTemperature": degf(160 + 8 * math.sin(t * 2)),
            "propulsion.port.temperature": degf(160 + 8 * math.sin(t * 2)),
            "tanks.fuel.0.currentLevel": 0.70 - 0.10 * t,
            "electrical.batteries.0.voltage": 13.9 + 0.3 * math.sin(t * 8),
            "environment.depth.belowTransducer": 2.5 + 1.5 * math.sin(t * 3),
            "navigation.speedOverGround": knots(3.0 + 1.2 * math.sin(t * 5)),
            "navigation.courseOverGroundTrue": deg((t * 360) % 360),
            "navigation.position": {"latitude": 42.8947 + t * 0.004,
                                    "longitude": -79.6222 + t * 0.006},
        }))
    return steps, 20.0


def sc_clear():
    """Push a healthy neutral state. Use after testing to quiet any alarms."""
    return [(0, "Clearing to healthy neutral state", engine_running())], 5.0


SCENARIOS = {
    "cruise":        (sc_cruise,         "Full healthy cruise — smoke test the rig"),
    "boot-engine-off": (sc_boot_engine_off, "BUG-45 — no false crit alarm on boot"),
    "oil-critical":  (sc_oil_critical,   "BUG-42/44 — ack latch + voice alarm"),
    "oil-recover":   (sc_oil_recover,    "BUG-42 — ack latch resets on recovery"),
    "depth-sweep":   (sc_depth_sweep,    "BUG-30 — belowTransducer tracking"),
    "throttle-step": (sc_throttle_step,  "BUG-13 — speed gauge flicker"),
    "stationary-cog": (sc_stationary_cog, "BUG-15 — COG flashing while stopped"),
    "units":         (sc_units,          "BUG-43 — Imperial/Metric selection"),
    "clear":         (sc_clear,          "Reset to healthy neutral state"),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("list", "-h", "--help"):
        print("LAB-SIM — Signal K scenario injector\n")
        print(f"{'scenario':<18} {'bug(s)':<12} description")
        print("-" * 74)
        for name, (_, desc) in SCENARIOS.items():
            bug = desc.split(" — ")[0] if " — " in desc else ""
            tail = desc.split(" — ", 1)[1] if " — " in desc else desc
            print(f"{name:<18} {bug:<12} {tail}")
        print("\nAll injected values carry $source = LAB-SIM.")
        return 0

    name = sys.argv[1]
    if name not in SCENARIOS:
        print(f"unknown scenario: {name}", file=sys.stderr)
        print(f"known: {', '.join(SCENARIOS)}", file=sys.stderr)
        return 2

    fn, desc = SCENARIOS[name]
    print(f"=== LAB-SIM: {name} ===")
    print(f"{desc}\n")
    steps, hold = fn()
    run_steps(steps, hold)
    return 0


if __name__ == "__main__":
    sys.exit(main())
