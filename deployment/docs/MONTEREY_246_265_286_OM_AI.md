---
title: Monterey 246 / 265 / 286 Cruiser — Owner's Manual (AI-Friendly Edition)
source_document: Monterey_246_265_286_Cruiser_OM.pdf (126 pages, 9 chapters)
source_copyright: © Monterey Boats. Diagram credits: Ken Cook Co. (KC-#### tags)
owner_vessel: Monterey 265 (this edition tags 265-relevant content)
edition: AI-friendly conversion — faithful facts + diagrams-as-text + query structure
status: COMPLETE — all chapters + every diagram described (Ch1–2, Ch3, Ch4, Ch5–6, Ch7/Ship Systems, trailering, gas/fire, all 4 wiring diagrams + detailed M-16 schematic)
converted: 2026-07-24 S106
consumer: d3kOS RAG (ChromaDB via helm_os_ingest.py)
---

# Monterey 246 / 265 / 286 Cruiser — Owner's Manual (AI-Friendly Edition)

## About this edition (read me first — for the AI and the reader)

This is a faithful, restructured conversion of the Monterey Cruiser Owner's Manual,
optimized so an AI assistant can retrieve and reason over it. It is **not** a verbatim
reprint. Conversion rules applied throughout:

1. **Facts are exact.** Every specification, gauge scale, unit, capacity, range, and
   safety signal word is reproduced precisely from the source. Where the source gives a
   number, this edition gives the same number.
2. **Diagrams are described in text.** Each illustration (identified by its `KC-####`
   art tag) is removed and replaced by a `DIAGRAM` block describing what it shows,
   including every callout label.
3. **Prose is faithfully restructured, not padded.** Descriptive text is condensed and
   reorganized for retrieval; meaning is preserved.
4. **Safety notices are preserved with their signal word** (`WARNING`, `CAUTION`,
   `NOTE`) exactly as the source classifies them.

### Model-applicability tags

| Tag | Meaning |
|-----|---------|
| `[ALL]` | Applies to 246, 265, and 286 |
| `[265]` | Confirmed relevant to the Monterey 265 |
| `[TWIN]` | Twin-engine equipped boats only |
| `[SINGLE]` | Single-engine equipped boats only |
| `[OPTION]` | Optional equipment — may not be fitted to a given hull |

> **Configuration note:** The source manual covers several models and states that controls
> and instruments "may be optional or slightly different" per boat. Engine count
> (single vs. twin) is a per-hull option. Confirm your 265's actual engine configuration
> before treating `[TWIN]`/`[SINGLE]` items as present. `[UNVERIFIED — confirm on boat]`

### Safety signal words (as defined by the source, Chapter 1)

- **WARNING** — potentially hazardous situation which, if not avoided, COULD result in
  death or serious injury.
- **CAUTION** — potentially hazardous situation which, if not avoided, MAY result in minor
  or moderate injury; may also flag unsafe practices.
- **NOTE / property-damage signal** — a situation which, if not avoided, may result in
  product or property damage.

### How to query this document (AI guidance)

- Each control, gauge, or switch is its own `###` subsection with a stable heading — use
  the heading as the retrieval anchor.
- Gauge subsections carry a structured fact block (`Measures / Units-scale / Normal range /
  Source of truth`). When asked "what is the normal range for X," return the
  `Normal range` field; if it says "not in this manual," direct to the engine manual.
- Diagram content is inside `DIAGRAM (KC-####):` blocks.

---

# Spatial Reference Frame (for "where is X?" queries)

Derived from the Boating Terminology diagram (KC-0033, page i-1). Use this vocabulary to
answer location questions about any component described in this document.

- **Fore/aft axis:** BOW (front) → BOW PULPIT (platform projecting forward of the bow) →
  FORWARD → HELM (steering station) → AFT → STERN (rear) → TRANSOM (flat rear wall of the
  hull) → WATERLINE / DRAFT (below water).
- **Athwartships axis:** PORT SIDE (left, facing forward) · centerline · STARBOARD SIDE
  (right, facing forward).
- **Other reference terms:** BEAM (max width), GUNWALE (top edge of the hull side),
  FREEBOARD (hull height above waterline), RADAR ARCH (overhead structure aft of the helm),
  LOA (length overall).
- **HIN location (fact):** the Hull Identification Number is on the **transom, upper
  starboard side, above the waterline**.

---

# Chapter 1 — Boating Safety

**Source pages:** 1-1 to 1-14 (PDF pages 5–18) · **Applicability:** `[ALL]`

This chapter covers general boating safety, required equipment, emergencies, and hazardous
conditions. Most illustrations here are **reference icons** (they show *what* equipment is,
not *where* it sits on the boat); location-relevant items are flagged.

## 1.1 Required Safety Equipment

**Owner responsibility:** the boat ships with most federally required safety equipment, but
obtaining USCG-approved equipment is the owner's responsibility.

**DIAGRAM (KC-0081) — "Minimum Required Safety Equipment" (table):** columns by boat class —
**Class 1** (16 to <26 ft / 4.9 to <7.9 m), **Class 2** (26 to <40 ft / 7.9 to <12.2 m),
**Class 3** (40 to ≤65 ft / 12.2 to ≤19.8 m). Rows:
- **PFDs:** one approved Type I/II/III per person aboard or towed, plus one throwable Type IV.
- **Fire extinguisher (must say "Coast Guard Approved"):** Class 1 = at least one B-I hand
  portable; Class 2 = at least two B-I OR one B-II; Class 3 = at least three B-I OR one B-I
  plus one B-II.
- **Visual distress signals:** required (coastal waters); day + night approved.
- **Bell/whistle:** <12 m must carry an efficient sound-producing device; 12–20 m must carry
  a whistle audible ½ nautical mile and a bell ≥200 mm (7.87 in) mouth diameter.

**DIAGRAM (KC-0041/0051/0061/0071) — PFD types (four line drawings, one per type):**
- **Type I — Life Preservers:** bulky vest/yoke; offshore/rough water; turns an unconscious
  person face-up.
- **Type II — Buoyant Vests:** near-shore/inland; turns most unconscious people face-up.
- **Type III — Flotation Aids:** vest style; calm inland waters/water sports; does NOT turn a
  person face-up.
- **Type IV — Throwable Devices:** ring buoy and square cushion; thrown to a person in the
  water; cushions must never be worn on the back.

> **CAUTION:** Many states require minors to wear a PFD at all times — consult local authorities.

**Stowage (location facts):** remove PFDs from packaging and stow for quick access; **do not
stow near grease or oil**; do not use a PFD as a fender.

## 1.2 Fire Extinguishers

**DIAGRAM (KC-0083) — extinguisher pressure gauge:** close-up of a fire-extinguisher head and
its round pressure gauge; the dial is marked with an **OVERCHARGED** zone (top) and a
**RECHARGE** zone (bottom), with the normal band between them. Check the gauge regularly.

> **Location guidance (fact):** mount extinguishers in **readily accessible areas, away from
> the engine compartment and alcohol stove**; all passengers should know each one's location
> and operation. Must be classified for type B fires (gasoline, oil, grease).

## 1.3 Visual Distress Signals

**DIAGRAM (KC-0082) — distress-signal chart (six cells):**
- **Orange flag** (black square + disc on orange) — USE DAY ONLY.
- **Red distress flare (hand)** — USE DAY AND NIGHT.
- **Arms signals** (person on a boat raising/lowering both arms, use bright cloth) — USE DAY ONLY.
- **Orange smoke signal (hand)** — USE DAY ONLY.
- **Red meteor flare** (fired arcing upward) — USE DAY AND NIGHT.
- **Electric distress light** (flashlight flashing "SOS") — USE NIGHT ONLY.
- **Dye marker** (dark stain spreading on water) — USE DAY ONLY.

> **WARNING:** Pyrotechnic signaling devices can cause injury and property damage if mishandled.
> Follow the manufacturer's directions and stow them inaccessible to children.

## 1.4 Recommended Equipment

**DIAGRAM (KC-0090) — recommended-gear illustration:** a grouped drawing of suggested extra
gear — bucket/bailer, anchor with line, combination oar/boat hook, first-aid kit, hand pump,
flashlight, compass/chart, spare propeller, tools (wrench/pliers), coiled tow line, lubricant,
and a portable AM/FM weather radio. (Full recommended list is text; the drawing depicts the
main items.)

## 1.5 Emergencies

**Reporting:** the operator must file a report for accidents involving loss of life, injury,
or damage over **$200**.

**Fires:** most fires occur just after refueling. Aim the extinguisher at the **base of the
flames** with a sweeping motion. If not extinguished, get out and swim **at least 25 yards
upwind**.

**DIAGRAM (KC-0164) — fire emergency:** side view of a cruiser with flames rising from the
cabin/helm area and a person in the water swimming away from the boat.

**DIAGRAM (KC-0170) — capsizing:** a person standing on the overturned hull of a capsized boat
in the water. Guidance: turn the engine OFF, account for others, **stay with the boat (it
floats)** and climb onto the hull, and do not try to swim to shore.

## 1.6 Hazardous Conditions (Weather)

> **WARNING:** Gasoline floats on water and can burn. If the boat is abandoned, swim upwind far
> enough to avoid spreading fuel.

**Storms:** wear PFDs; stow gear below and lash deck equipment; reduce speed and head for the
nearest refuge; if power is lost, keep the bow into the waves with a sea anchor off the bow.
**Fog:** avoid operating; take bearings, log courses/speeds; sound a **five-second horn/whistle
blast every minute**; passengers wear PFDs and watch for oncoming vessels.

**DIAGRAM (KC-0371, page 1-9) — weather warning signals (chart, 3 columns: Daytime pennant /
Description / Nighttime light):**
| Warning | Daytime signal | Nighttime lights | Condition |
|---------|----------------|------------------|-----------|
| Small Craft Advisory | one pennant | top red, bottom white | winds >18 kn sustained 2+ hr, or hazardous waves |
| Gale Warning | two pennants | top white, bottom red | sustained winds 34–47 kn (2+ hr) |
| Storm Warning | one square flag (black square on red) | two red lights (vertical) | sustained winds ≥48 kn |
| Hurricane Warning | two square flags (black squares on red) | red-white-red (vertical) | forecast winds ≥64 kn |
(Diagram note: the shaded pennants/flags are "actual signal in red.")

*(Remaining Chapter 1 text — Operation by Minors, Passenger Safety, Water Sports, General &
Special Gas Precautions, pages 1-11 to 1-14 — is text-only with no further diagrams; it will
be folded into the complete pass.)*

---

# Chapter 2 — Basic Rules of the Road

**Source pages:** 2-1 to 2-8 (PDF pages 19–26) · **Applicability:** `[ALL]`

Covers aids to navigation (the "signposts of the waterway") and right-of-way rules. **These
diagrams describe external navigation markers and vessel-encounter geometry — they are not
on-boat component locations.** Two U.S. marking systems: USWMS (inland, state-maintained) and
FWMS (coastal/rivers, USCG-maintained).

## 2.1 Aids to Navigation

**DIAGRAM (KC-0411, page 2-3) — Uniform State Waterway Marking System (USWMS):** buoy icons;
shaded areas represent the marker's actual color (orange/red).
- **Regulatory markers (white buoy with an orange symbol):** circle = **CONTROLLED AREA**;
  open diamond = **DANGER**; diamond with cross = **BOATS KEEP OUT**; square = **INFORMATION**.
- **Lateral / cardinal markers:** black-and-white **vertical** stripes = *do not pass between
  the buoy and shore*; red-and-white **horizontal** bands = **SPECIAL PURPOSE**; all-black
  can = *navigate to starboard facing upstream*; solid-color triangle = *navigate to port
  facing upstream*; color-topped-over-white = *navigate to south or west*; black-topped-over-
  white = *navigate to north or east*; black vertical stripes = **MID-CHANNEL**.

**DIAGRAM (KC-0441, page 2-4) — Federal Waterways Marking System (FWMS), lateral aids "as seen
entering from seaward"** (each row shows lighted buoy / unlighted buoy / daymark):
- **Port side — GREEN, odd numbers:** green-light lighted buoy (#3), flat-top **can buoy**
  (#5), **square** daymark (#1).
- **Starboard side — RED, even numbers:** red-light lighted buoy (#2), cone-top **nun buoy**
  (#4), **triangle** daymark (#6).
- **Safe-water / mid-channel aids (red, lettered):** white-light lighted buoy (G), **spherical
  buoy** (E), round daymark (C).
- **Preferred-channel aids (green + red, lettered):** to **starboard** — green-light buoy (L),
  can buoy (B), square daymark (C); to **port** — red-light buoy (H), nun buoy (D), triangle
  daymark (A).

> **Rule of thumb (fact):** RED, triangular daymarks with EVEN numbers mark the **starboard**
> side of the channel; GREEN, square daymarks with ODD numbers mark the **port** side (entering
> from seaward). ("Red-Right-Returning.")

## 2.2 Light Structures

**DIAGRAM (KC-0442, page 2-5) — Range Lights:** a boat approaching a channel with a **FRONT
MARKER** (lower, nearer) and a **REAR MARKER** (higher, farther) ashore. Three sub-panels show
the markers' apparent alignment: **LEFT OF RANGE LINE** (markers offset left), **ON RANGE
LINE** (markers stacked vertically — correct course), **RIGHT OF RANGE LINE** (offset right).
Keep the two markers in a vertical line to stay in the channel.

**DIAGRAM (KC-0443, page 2-5) — Lighthouses:** two tall tower structures with distinctive
paint schemes (one horizontally banded, one spiral-striped); unique patterns/flash
characteristics aid identification at harbor entrances, headlands, and danger areas.

## 2.3 Right-of-Way

**Terminology:** the **stand-on** (privileged) boat holds course and speed; the **give-way**
(burdened) boat keeps clear and passes to the stand-on boat's stern. Less-maneuverable and
larger vessels generally have right-of-way.

**Whistle signals (facts):** one short blast = intend to pass on *my* port; two short = pass on
*my* starboard; one long blast = warning (e.g., leaving a slip); **five or more short rapid
blasts = danger signal** (intent unclear).

**DIAGRAM (KC-0475, page 2-7) — meeting/passing (three columns of two boats each, blue arrows =
travel direction, "HONK" bubbles = whistle blasts):**
- **PASSING PORT TO PORT** — boats meeting pass left-to-left (no signal shown).
- **MEETING HEAD TO HEAD** — both turn right and pass port-to-port; one **HONK** each.
- **PASSING STARBOARD TO STARBOARD** — used when both are on the left of a channel; two blasts
  (**HONK HONK**) each.

**Crossing situation (fact):** the boat on your starboard side (roughly the 12-to-4-o'clock
arc) is the stand-on boat; hold clear and pass astern of it. Up/down-river traffic has
privilege over boats crossing the river.

**DIAGRAM (KC-0476, page 2-8) — overtaking / prudential / night running (illustrations):**
overtaking boat is the give-way boat and must keep clear of the boat ahead (stand-on holds
course/speed); if collision is unavoidable neither boat has right-of-way and both must act to
avoid it; between sunset and sunrise all boats must show navigation lights and should slow and
keep clear regardless of privilege.

---

# Chapter 3 — Controls and Indicators

**Source pages:** 3-1 to 3-10 (PDF pages 27–36) · **Applicability:** `[ALL]`

Knowing the controls and indicators is essential for safe operation. Those shown may be
optional or slightly different from the ones on a given boat.

---

## 3.1 Shift / Throttle Control

The shift/throttle control differs by model and engine. The description below is typical of
most remote controls; consult the engine and remote-control manual for differences.

> **CAUTION:** Do not shift too quickly from forward to reverse. Stay in neutral or idle
> until the boat has lost most of its headway before completing the shift to reverse, or
> engine damage may occur.

### Single-Engine Control `[SINGLE]`
A single lever acts as both gear shifter and throttle. The lever is detented in neutral for
starting. Shifting happens within the first **15°** of travel — push forward for forward,
pull back for reverse. Beyond 15° the lever moves from the shifting range into the throttle
range. **Never attempt to shift without the engine running.**

### Twin-Engine Control `[TWIN]`
Independent levers control shift and throttle for each engine; basic operation matches the
single-engine control. Increasing throttle (forward) increases speed; the shift control
selects forward or reverse. Some boats have separate individual controls for shift and
throttle — if so equipped (dual-lever), the throttle lever must be in the **idle** position
before making a shift.

> **NOTE:** Refer to the engine and remote-control operator's manuals for detailed operation
> in conjunction with the engine.

**DIAGRAM (KC-0651):** Line drawing of a twin-engine dual control head — two curved,
side-by-side control levers rising from a single pedestal base. The left lever is labeled
**PORT CONTROL LEVER**, the right **STARBOARD CONTROL LEVER**.

**DIAGRAM (KC-0653) — "TYPICAL DUAL-LEVER CONTROL":** A binnacle-mounted control shown from
the side, with two levers and leader lines to five labeled positions:
- **SHIFT LEVER IN FORWARD POSITION** (shift lever tilted forward),
- **SHIFT LEVER IN NEUTRAL POSITION** (shift lever upright/centered),
- **SHIFT LEVER IN REVERSE POSITION** (shift lever tilted aft),
- **THROTTLE LEVER IN FULL THROTTLE POSITION** (throttle lever full forward),
- **THROTTLE LEVER IN IDLE POSITION** (throttle lever back/idle).

---

## 3.2 Instruments (Gauges)

All instruments are illuminated for night operation. Their type, number, and location vary;
some may not appear on a given model. On twin-engine boats there may be two sets of some
instruments — one per engine — with port-engine instruments typically on the port side of
the helm panel and starboard-engine instruments on the starboard side. `[TWIN]`

> **CAUTION:** If an instrument reading is outside normal or recommended ranges, investigate
> the cause immediately or see your dealer. Consult the engine operator's manual for the
> normal recommended ranges.

> **BUG-16 / tolerance note:** For most gauges below, this boat manual does **not** state the
> numeric normal range — it defers to the engine (MerCruiser) manual. The only explicit
> range here is the voltmeter (12+ V). To power a "compare live value to normal range"
> feature, source the engine manual's ranges.

### Tachometer
- **Measures:** engine speed in revolutions per minute (RPM).
- **Units / scale:** `RPM ×100`, dial marked 0,5,10,15,20,25,30,35,40 (i.e., 0–4000 RPM).
- **Normal range:** not in this manual — consult the engine manual for the proper RPM
  operating range.
- **Use:** keep the engine within its proper operating range.
- **DIAGRAM (KC-0700):** Round analog gauge, needle sweep 0→40, label **RPM · x 100**.

### Speedometer
- **Measures:** forward boat speed relative to the water.
- **Units / scale:** dual scale — **MPH** (marked 15,20,25,30,35,40,45,50) and **KPH**
  (marked 20,30,40,50,60,70,80).
- **Accuracy:** approximate — most marine speedometers are water-pressure operated.
- **Use:** monitor fuel consumption and propeller performance.
- **DIAGRAM (KC-0710):** Round analog gauge with two concentric scales, outer **MPH**, inner
  **KPH**.

### Fuel Gauge
- **Measures:** approximate fuel level in the gas tank(s).
- **Units / scale:** **E** (empty) – **½** – **F** (full).
- **Accuracy:** varies with boat attitude (trim and list); the pick-up tube cannot withdraw
  all fuel. Observe the **One Third Rule** — ⅓ of fuel out, ⅓ back, ⅓ reserve.
- **DIAGRAM (KC-0700 face):** Round gauge labeled **FUEL**, scale **E — ½ — F**.

### Engine Sync Gauge `[TWIN]`
- **Measures:** synchronization of the two engines' speeds.
- **Reading:** adjust throttles so the needle is **centered**; the dial spans **PORT** (left)
  to **STBD** (right).
- **Why:** excessive noise and vibration occur if engines are not synchronized.
- **DIAGRAM (KC-0702):** Round gauge labeled **ENGINE SYNC**, needle centered between
  **PORT** and **STBD**.

### Voltmeter
- **Measures:** condition of the main / cranking battery, in volts DC.
- **Units / scale:** **VOLTS**, dial marked ~10,13,16 with **–** and **+** ends.
- **Normal range:** **12+ volts** (the one explicit range in this manual).
- **DIAGRAM (KC-0740):** Round gauge labeled **VOLTS**, scale 10–16, minus on the left, plus
  on the right.

### Ammeter
- **Measures:** charging current in the electrical system.
- **Units / scale:** **AMP**, dial marked **–50 … 0 … +50**.
- **Normal range:** not in this manual — consult the engine manual.
- **DIAGRAM (KC-0750):** Round gauge labeled **AMP**, center-zero scale –50 to +50.

### Engine Trim Gauge
- **Measures:** position of the outdrive unit — relative bow position from horizontal.
- **Units / scale:** **TRIM**, marked **DN** (down) to **UP**.
- **Use:** monitor boat trim.
- **DIAGRAM (KC-0760):** Round gauge labeled **TRIM**, scale from **DN** to **UP**.

### Water Pressure Gauge
- **Measures:** cooling water circulated by the water pump, in PSI.
- **Units / scale:** **WATER PRESS**, marked 5,10,15,20,25,30 (PSI).
- **Normal range:** not in this manual — consult the engine manual for the normal PSI range.
- **Use:** confirm the engine cooling system is operating properly.
- **DIAGRAM (KC-0730):** Round gauge labeled **WATER PRESS**, scale 5–30 PSI.

### Engine Oil Pressure Gauge
- **Measures:** pressure of the lubricating oil inside the engine.
- **Units / scale:** dual — **PSI** (outer, marked 0,40,80) and **kPa ×100** (inner, marked
  1,2,3,4).
- **Normal range:** not in this manual — consult the engine manual.
- **DIAGRAM (KC-0780):** Round black-faced gauge, label **OIL**, oil-can symbol, outer scale
  **PSI 0–80**, inner scale **kPa ×100 (0–4)**. *(Visually verified from rendered page.)*

### Engine Water Temperature Gauge
- **Measures:** engine water/coolant temperature inside the engine.
- **Units / scale:** dual — **°F ×10** (outer, marked 10,15,24 → 100–240 °F) and **°C ×10**
  (inner).
- **Normal range:** not in this manual — consult the engine manual.
- **DIAGRAM (KC-0770):** Round black-faced gauge, label **TEMP**, outer scale **°F ×10**,
  inner scale **°C ×10**. *(Visually verified from rendered page.)*

### Engine Hourmeter
- **Measures:** accumulated engine operating time.
- **Behavior:** activated whenever the ignition switch is **ON** — **logs time even when the
  engine is not running.**
- **Use:** keep accurate logs for scheduled maintenance.
- **DIAGRAM (KC-0782):** Round gauge labeled **ENGINE HOURS** with a digital odometer-style
  counter window. *(Visually verified from rendered page.)*

---

## 3.3 Switches

Each electrical circuit has a control switch; some have an LED ON/OFF indicator, and most
have an adjacent fuse holder or circuit breaker.

### Master Power Switch
Disconnects the boat electrical systems from the batteries. Keep OFF when not using the boat.

### Battery Switch
Connects the battery(ies) to the electrical system. Provides isolation and positive
disconnect to protect against tampering, electrical fire hazards, and battery run-down.
Rotate to OFF when the boat is not in use.

> **WARNING:** Never turn the switch to the OFF position while the engine(s) is running, or
> serious alternator / electrical system damage could occur.

**DIAGRAM (KC-0704) — "TYPICAL BATTERY SWITCH":** Round rotary switch, **ON** at top, **OFF**
at bottom, with three mounting-screw holes around the rim. *(Visually verified.)*

### Battery Selector Switch `[OPTION]`
Operates as a battery switch and can connect two batteries in **parallel** for starting if
one battery is low; allows emergency starting of either engine from the opposite battery.
May be used with an isolator and a third battery (see Ship Systems).

**DIAGRAM (KC-0705) — "TYPICAL BATTERY SELECTOR SWITCH":** Rotary switch with positions
**OFF**, **1**, **2**, and **BOTH**.

### Windshield Wiper Switch `[OPTION]`
Controls operation of the windshield wipers.

### Compass
Indicates where NORTH is; aids navigation. Must be compensated (corrected) for deflections
from nearby magnets and wiring. After all optional helm equipment is installed, have the
compass compensated by a qualified compass adjuster, who provides a deviation card/chart.
Keep electrical or metal items **three or more feet** from the compass. Readjust if any
compensated influencing item is removed, relocated, or added nearby. Watch for sluggish or
erratic behavior — signs of alien magnetism or a damaged compass.

### Fuel Gauge Switch
Lets you check tank fuel level when the navigation lights are OFF or the ignition is OFF.

### Boarding and Courtesy Lights
Controlled by selector switches. The main DC breaker (**Master Power**) switch must be ON to
activate lighting.

### Navigation Lights Switch
- **NAV** position: red and green bow lights, white stern light, and gauge illumination ON.
- **ANC** (anchor) position: only the white stern light ON, for night anchoring.

> **WARNING:** Never operate the boat between sunset and sunrise with the switch in the anchor
> position. Running lights are required to indicate direction and right-of-way at night.

### Blower Switch
Activates the engine-box ventilation blower to remove explosive fumes from the box and bilge.

> **WARNING:** Operate the blower a minimum of **five minutes** before each engine start, and
> continuously at idle or slow-speed running. Failure to operate the blower can create
> conditions favorable for an explosion, with severe personal injury or death.

### Bilge Switch
Activates the bilge pump to remove excess water. Some models have an **AUTO** setting — switch
to AUTO while underway to pump water as it enters.

> **CAUTION:** Switch the bilge OFF when the boat is not in use — wave action or trailer travel
> can run the pump and drain the battery.

### Ignition Switch
Starts and stops the engine. Consult the engine operator's manual.

### Depth Sounder `[OPTION]`
Indicates the distance between the bottom of the boat and the surface directly below the
transducer.

> **Operational note:** To avoid running aground in shallow water, **always add extra distance
> to the meter reading.** Consult the depth sounder operator's manual.

> **d3kOS cross-reference:** On this vessel, depth is sourced from the **Garmin unit via NMEA
> 2000** (operator-confirmed, S106) — see BUG-18.

### Gas Fume Detector
Alarm sounds when gas fumes are detected; the sensor is mounted in the bilge where fumes
collect. Test before each cruise.

> **WARNING:** If the gas fume detector indicates a dangerous condition:
> - DO NOT operate electrical equipment.
> - Extinguish open flames and smoking materials immediately.
> - Turn engine(s) OFF.
> - Wait **5 minutes** before opening the engine compartment to investigate.
> - Determine the cause and correct it before resuming operation.

### Engine Alarm System
Sounds an alarm if engine temperature exceeds a set limit or oil pressure drops below a set
range. If it sounds during operation, **immediately shut down engines and determine the
cause.** Consult the engine operator's manual.

### Battery Charger `[OPTION]`
Operates from shore power or generator; converts 110 V AC to 12 V DC to charge batteries.
Delivers full output to a discharged battery or a trickle charge to a nearly-full one.

### Battery Isolator `[OPTION]`
Allows charging multiple batteries; automatically apportions charge, prevents overcharging,
and stops a higher-charged battery from discharging into a lower-charged one.

### Horn Button
Push and hold to sound the horn.

### Trim / Tilt Switch
Activates the engine power trim and tilt. Push and hold until the drive is at the desired
angle. Use with the trim gauge to maximize performance; the tilt function raises the drive
for trailering.

**DIAGRAM (KC-0931) — "TYPICAL TRIM SWITCH":** Rocker switch marked **UP** and **DN**.

### Trim Tab Switches `[OPTION]`
Rocker switches controlling the port and starboard transom trim tabs. Adjusting them improves
ride and corrects side-to-side listing from varying weight. See the RUNNING chapter for
trimming procedures.

**DIAGRAM (KC-0932) — "TRIM TAB SWITCHES":** Two rockers, each marked **BOW UP / BOW DOWN**,
labeled **PORT** and **STBD**.

### Engine Stop Switch and Lanyard
Stops the engine when engaged. Attach the lanyard to the operator whenever the engine is
running; if the operator is thrown from the seat or moves too far from the helm, the lanyard
engages the switch and shuts off the engine. To attach: hold out the button head, slide the
fork beneath the safety switch, and clip the hook on the opposite end to a strong piece of
the operator's clothing (e.g., a belt loop).

> **WARNING:** Attach the lanyard to the operator before starting the engine — this prevents a
> runaway boat if you are thrown out. The switch is only effective in good working condition:
> - Never remove or modify the switch and/or lanyard.
> - Keep the lanyard free from obstructions.
> - **Once a month:** with the engine running, pull the lanyard; if the engine does not stop,
>   see your dealer for switch replacement.

**DIAGRAM (KC-0950):** The engine stop switch with lanyard, callouts: **SAFETY SWITCH**,
**BUTTON HEAD**, **FORK**, **LANYARD**, **HOOK**.

### Hydraulic Steering System `[OPTION]`
The manual hydraulic steering does **not** behave like automotive power steering — effort to
turn the wheel increases as more force is demanded. Turning the wheel drives pistons in the
manual pump, forcing hydraulic fluid to the cylinder, which turns the boat; the reservoir
holds extra fluid and maintains a pressure head that keeps air out of the system.

**DIAGRAM (KC-1882):** Schematic of the hydraulic steering loop, callouts: **MANUAL PUMP**,
**RESERVOIR**, **HYDRAULIC CYLINDER**.

### Fuel Feed Valves `[OPTION]`
Models with two or more fuel tanks use manual valves to control fuel flow to the engines;
boat trim can be adjusted with proper use of these valves (see Ship Systems).

**DIAGRAM (KC-1002) — "FUEL FEED VALVES":** Three valves shown with **ON/OFF** positions,
labeled **PORT VALVE**, **CROSSOVER VALVE**, **STBD VALVE**.

---

# Chapter 4 — Operation

**Source pages:** 4-1 to 4-11 (PDF pages 37–47) · **Applicability:** `[ALL]`

Covers fueling, starting, shifting/running, the warning alarm, steering, stopping, docking,
and boat trim.

## 4.1 Fueling
Key facts: know your tank capacity; **do not fill to capacity** (allow for fuel expansion);
before fueling close all hatches/windows, extinguish flames, turn all power off, operate no
electrical switches; keep the fill nozzle **in contact with / grounded to the fill opening**
to reduce static spark; check oil level; inspect fuel lines for leaks each fill. Federal law
prohibits discharging oil/oily waste (fine up to $5,000).

## 4.2 Starting

**DIAGRAM (KC-1002) — Fuel Feed Valves:** (same control as Chapter 3) three inline valves on
the fuel supply, labeled **STBD VALVE**, **CROSSOVER VALVE**, **PORT VALVE**, with **ON/OFF**
positions. Open the fuel feed valve(s) before starting.

**DIAGRAM (KC-2165) — "Typical Seacock and Strainer":** a raw-water cooling intake shown in
cross-section. From the bottom up: the hull with **INCOMING RAW WATER** entering through a
below-waterline through-hull fitting; the **SEACOCK** (shut-off valve, with **OPEN** and
**CLOSED** lever positions); and above it the **STRAINER** (sediment/debris filter) before the
water continues to the engine.
- **LOCATION:** below the waterline, in the **bilge / engine compartment** — the engine
  cooling-water intake. Open the engine-cooling seacock before starting; seacocks for
  washdowns, heads, and A/C are opened as needed.

**Start sequence (facts):** battery switch(es) ON → open engine hatch → open fuel feed
valve(s) → run bilge blower **≥5 min** → clear bilge water with manual bilge pump → sniff test
→ open cooling seacock → close hatch → drive(s) full **IN** → trim tabs full **DOWN** → shift
lever(s) NEUTRAL → cycle throttle then return to idle → slightly advance throttle.

## 4.3 Docking

**DIAGRAM (KC-1125) — dock approach:** plan view of a boat approaching a dock with **WIND or
CURRENT** direction arrows. Approach pointed into the wind if possible; if wind/current pushes
you off the dock use a sharper angle; if it pushes you on, use a slow speed and shallow angle;
with no wind/current approach at a **10–20° angle**.
- **Tie-up facts:** use fenders; tie only to lifting / tie-down eyes — **never handrails or
  windshield frames**; use double-braided nylon line with chafing protectors; leave slack for
  wave/tidal movement.

## 4.4 Boat Trim

> **CAUTION:** Do not trim the engine out too far or the boat may "porpoise" (bounce),
> reducing control and visibility. Improper trim-tab use at high speed can cause an accident.

**DIAGRAM (KC-1157) — power trim positions (three drive profiles):** **IN TOO FAR** (drive
tucked under, bow digs in), **CORRECT** (prop path parallel to water), **OUT TOO FAR** (drive
kicked out, bow high / porpoising). Each shows a **UP / TRIM / DN** rocker. Start trimmed IN;
increase angle out as the boat planes.

**DIAGRAM (KC-1154) — trim-tab action (side view + inset):** a cruiser at speed with **STERN
RISES** (arrow up at transom) and **BOW LOWERS** (arrow down at bow); label **WATER IS
REDIRECTED CREATING UPWARD FORCE AT STERN**. Inset labeled **HULL** shows a trim tab hinged at
the transom deflecting water flow (blue arrows) downward/aft, producing upward force.

**DIAGRAM (KC-1155) — trim-tab cross effect (top-down hull):** **PORT TAB LOWERED → port stern
rises, starboard bow lowers**; **STARBOARD TAB LOWERED → starboard stern rises, port bow
lowers.** (Lowering one tab raises that side's stern and lowers the opposite bow.)

**DIAGRAM (KC-1153) — trim-tab tuning:** an **UNTRIMMED** hull vs. a **PLANING ATTITUDE** hull,
with the note **PROP PARALLEL TO WATER FLOW**. Procedure: set tabs for planing → use power trim
to set prop path parallel to water flow → fine-tune with tabs → don't overtrim (bow digs in and
the boat veers) → don't move one tab much further down than the other while underway (causes
listing).

---

# Chapter 5 — Getting Underway

**Source pages:** 5-1 to 5-4 (PDF pages 48–52) · **Applicability:** `[ALL]`

Covers the pre-departure safety checklist, safety equipment, boarding, and capacity.

## 5.1 Safety Checklist
> Perform these in the same order every time. **Do NOT launch if any problem is found** —
> have it fixed first.

**Pre-Operation:**
- Check weather report, wind, and water conditions.
- Confirm required safety equipment is aboard; fire extinguisher fully charged.
- Confirm the bilge drain plug is installed properly.
- Check that no fuel/oil/water is leaking (or has leaked) into the bilge.
- Check all hoses and connections for leakage/damage.
- Check engine and stern-drive oil levels.
- Check stern-drive pump and trim-tab pump fluid levels.
- Check hydraulic steering fluid level.
- Ensure the raw-water intake strainer is clean.
- Confirm raw-water inlet **seacocks are open**.
- Inspect exhaust connections for water leaks / gas stains; tighten loose connections.
- Check the propeller for damage.
- Check the engine cooling-water pick-up for blockage.
- Check battery terminals are clean and tight.
- Test electrical circuits (lights, pumps, horn, etc.).
- Confirm throttle/shift control is in **neutral**.
- Confirm the steering system operates properly.
- Confirm all required maintenance is done.

**During Operation:** check gauges frequently for abnormal behavior; confirm controls operate
smoothly; watch for excessive vibration.

**After Operation:** fill the fuel tank (prevents condensation moisture); check for fuel/oil/
water leakage; check the propeller for damage; complete the End-of-Day Shutdown checks.

## 5.2 Boarding & Loading (facts)
- Board one person at a time — **step in, do not jump**; avoid slippery surfaces; set gear on
  the dock first, then board and pick it up.
- Distribute weight side-to-side and fore-and-aft to maintain trim; avoid excess weight in the
  bow or stern.
- Passengers must not ride on the bow, bow pulpit, deck, gunwale, or rear sun deck while
  underway, nor dangle feet over the side.
- Stow gear securely; never on top of safety equipment (it must stay quickly accessible).
- In adverse weather, reduce load (capacity ratings assume normal conditions).
- Never use the engine/drive as a boarding ramp; engine OFF when swimmers/divers/skiers board.

**DIAGRAM (KC-1445, page 5-4) — USCG "Maximum Capacities" certification plate:** a rectangular
data plate reading **MAXIMUM CAPACITIES / U.S. COAST GUARD**, with example values *"11 PERSONS
OR 1620 LBS."* and *"1620 POUNDS, PERSONS, GEAR,"* plus compliance text (load capacity,
compartment ventilation, steering/fuel/electrical systems).
- **LOCATION:** the certification plate is affixed to the boat (typically at the helm station).
- **`[UNVERIFIED — confirm on boat]`** The 11-persons / 1620-lb figures are the *illustration's*
  example values, not necessarily your 265's rating — read your boat's own plate for the
  actual certified capacity. Do not exceed it.

# Chapter 6 — Running

**Source pages:** 6-1 to 6-8 (PDF pages 53–61) · **Applicability:** `[ALL]`

Covers maneuvering, salt water, freezing temperatures, towing, anchoring, and propellers.

## 6.1 Maneuvering

**DIAGRAM (KC-1474, page 6-1) — turning circles:** a top-down boat in a turn showing two
concentric arcs — an outer **STERN CIRCLE** (larger) and an inner **BOW CIRCLE** (smaller).
Because thrust and steering are both at the stern, **the stern swings away from the direction
of the turn** and the bow follows the tighter circle. Steering response depends on engine
position, motion, and throttle.

**DIAGRAM (KC-1074 / KC-2340, page 6-2) — propeller torque / counter-rotation:** illustrates
that a single **clockwise** propeller makes the boat drift to **starboard going forward** and
to **port going backward** (strongest at slow speed / backing). Twin **counter-rotating**
engines (one CW, one CCW) cancel this torque steer and hold an even keel.

**DIAGRAM (KC-1521, page 6-3) — twin-throttle pivot:** using one engine forward and the other
in reverse to pivot the boat (e.g., port forward + starboard reverse pivots into a starboard
turn). Practice with quick throttle "bursts" in open water.

## 6.2 Towing

**DIAGRAM (KC-2115, page 6-4) — towing procedure:** one boat towing another; pass a light
weighted throwing line first with the heavier tow line secured to it; match tow-line length to
wave action (both boats on crests or in troughs together); shorten in calm water; tow at
moderate speed.
> **Facts:** tow line must be rated **≥4× the gross weight** of the towed boat; never tow a
> much larger or grounded vessel.

## 6.3 Anchoring

> **CAUTION:** Always anchor from the **bow**; NEVER from the stern. Current can make a
> stern-anchored boat unsteady and can pull it under.

**DIAGRAM (KC-1535, page 6-5) — anchor scope:** side view of an anchored boat with the rode
running from the bow down to the anchor on the bottom; label **LINE 6 TO 7 TIMES DEPTH OF
WATER.** Example: in 10 ft of water, let out 60–70 ft of line. Tie the rode to the anchor and
to the **forward cleat / bow eye**; head into the wind/current over the drop spot; back up
slowly keeping tension; check for drag against the shoreline and reset if dragging.

## 6.4 Propellers

**DIAGRAM (KC-1580 / KC-1581, page 6-7) — propeller geometry:** illustrations of propeller
**diameter** (blade-tip circle) and **pitch** (theoretical forward travel per revolution). The
propeller converts engine power to thrust; correct diameter/pitch keeps the engine within its
full-throttle RPM range (see the engine manual for that range).

**Performance-boating facts:** raise trim tabs above the boat bottom; trim engines out as the
boat rises and accelerates; **watch the tachometer to keep engines within the full-throttle
range**; keep one hand on the wheel and one on the throttles.

---

# Chapter 7 / Ship Systems — Electrical

**Source pages:** 7-1 to 7-5 + Ship Systems 11-x (PDF pages 60–98) · **Applicability:** `[ALL]`

> **DC system fundamentals (facts):** the boat has a **12-volt negative-ground DC system** —
> the positive wire is hot (feeds 12 V loads), the negative wire is ground. Many boats have
> **three batteries**: two **cranking** batteries (start engines only) and one **auxiliary**
> battery feeding all other DC circuits via the master battery switch. Engines charge all
> batteries via the **alternator(s)**, rate controlled by an internal **voltage regulator**.
> Grounding path: cranking batteries → engine(s); auxiliary battery → cranking batteries;
> engine(s) → a **bonding strip located in the engine compartment**. An **electronic solid-
> state isolator** separates the auxiliary from the cranking batteries so accessory loads don't
> drain cranking batteries when ignition is OFF. `[d3kOS cross-ref: BUG-17 battery voltage]`

## 7.1 Battery Service

**DIAGRAM (KC-1620, page 7-2) — battery servicing:** a marine battery with vent caps; guidance
shows checking terminals for corrosion (clean with baking-soda/water and a wire brush, vent
wells corked first) and checking cell fluid **¼–½ inch above the plates** (top up with
distilled water; do not overfill; some batteries are sealed).
> **CAUTION:** Batteries contain sulfuric acid (severe burns) — wear protection. Turn OFF the
> battery charger and battery switch before servicing.

## 7.2 Fuses and Breakers

**DIAGRAM (KC-1630, page 7-3) — "Typical Fuse Block":** a rectangular multi-circuit fuse block;
wires enter from the top and bottom, with a column of fuse elements down the middle and screw
terminals around the edges. Some models instead use a **circuit breaker next to each switch**
(reset: switch the circuit OFF, wait ~1 minute, push the breaker button fully in, switch ON).

**DIAGRAM (KC-1640, page 7-3) — "Typical In-Line Fuse Holder":** a cylindrical barrel spliced
into a wire, marked **"TWIST AND PULL TO OPEN."** Some accessories (e.g., stereo) have an
extra in-line fuse in the positive lead; **some in-line fuse holders are located near the
battery.**
> **CAUTION:** Never exceed recommended fuse sizes or bypass the fuse safeguard; install the
> correct type/rating. Repeated failures indicate a severe problem.

## 7.3 DC Master Panel

**DIAGRAM (KC-1633, page 11-2) — "Typical DC Control Panel":** a horizontal panel titled **DC
CONTROL**. Left to right the panel carries, as labeled:
1. **DC VOLTS** — analog voltmeter (far left).
2. **BATTERY TEST (CRANK)** — rotary test switch.
3. **MASTER BREAKER** — with **OFF** position.
4. A row of toggle **circuit breakers**, labeled in order:
   **AUTO BILGE PUMP · IGNITION (single) · FWD · AFT · STBD · PORT · HEAD · FRESH WATER PUMP ·
   REFRIG · CABIN LIGHTS FWD · CABIN LIGHTS AFT · BILGE LIGHTS · COCKPIT LIGHTS · ACC · ACC ·
   ACC · CARBON MONOXIDE DETECTOR** (far right).
- **LOCATION / use:** the DC control panel is at the **helm / electrical panel area**. To read
  batteries: master breaker OFF, turn the battery-test switch, then flip individual breakers ON
  as required. `[UNVERIFIED — confirm on boat]` This is the *typical* panel layout; your 265's
  exact breaker set and order may differ — confirm against the actual panel.

# Ship Systems — Fresh Water

**DIAGRAM (KC-2040, page 11-9) — "Typical Complex Freshwater System":** a top-down hull plan of
the potable-water plumbing. Line key: **solid line = COLD**, **dotted line = HOT**.
- **Inlets (forward/top of diagram):** **CITY WATER INLET** and **TANK FILLER** (dock-side
  fill), and a **COCKPIT WASHDOWN** tap.
- **Port side run:** **HOT WATER HEATER** (with **FROM ENGINE / TO ENGINE** loop for engine-heat
  water heating) and a **COCKPIT SHOWER**.
- **Center (heart of the system):** **FRESH WATER TANK** → **FILTER** → **PUMP** →
  **ACCUMULATOR** (pressure tank) — this cluster pressurizes potable water.
- **Starboard side loads:** **SHOWER**, **HEAD VANITY** (sink), **ICEMAKER**, and **GALLEY**
  (sink).
- **LOCATION answers this supports:** fresh-water tank/pump/filter/accumulator are grouped
  centrally in the bilge/cabin sole; hot-water heater is on the port side tied to the engine;
  city-water and tank-fill connections are forward.

### Fresh-Water Deck Fill

**DIAGRAM (KC-2047, page 11-10) — "Typical Deck Plate Key":** a special T-handled key supplied
with the boat, used to unlock the deck-plate fill caps. Insert the key into the cap slot and
turn **counterclockwise** to unlock.
- **Facts:** the fresh-water deck fill is marked **"WATER"**; the tank is vented through the
  hull (tank is full when water comes out of the vent); fill only with potable water via a
  blue sanitary drinking-water hose. The **pump is located to port and below the engine hatch**.

# Ship Systems — AC Electrical

**DIAGRAM (KC-1634, page 11-4) — "Typical AC Control Panel"** (two-panel unit):
- **AC CONTROL (left panel):** a **REVERSED POLARITY** warning light, a **POWER AVAILABLE**
  light, an **AC VOLTS** meter, and toggle breakers labeled **STOVE, MICRO(wave), BATT CHRG,
  SPARE** (left column) and **WATER HEATER, OUT(let)S, REFRIG, SPARE** (right column). A
  **SLIDE PROTECTOR** covers the meter opening.
- **GENERATOR CONTROL (right panel):** a warning label (gasoline-vapor / blower start caution),
  generator controls **BLOWER, STOP, START, PREHEAT**, indicator lights **GENERATOR RUNNING,
  REVERSED POLARITY, SHOREPOWER**, and a **GENERATOR / SHOREPOWER** source selector.
- **Facts:** the **Power Available** light must be lit before switching the main AC breaker ON.
  Reversed-polarity light watches the **shoreside** source only (not boat wiring).

> **WARNING:** If a reversed-polarity warning shows, DO NOT use the power source — turn it off
> and disconnect the shore cord. Reversed polarity can cause shock, electrocution, or death.

**DIAGRAM (KC-2053, page 11-6) — "Typical Boat-Side Shore Power Connection":** an exploded view
of the shore-power inlet — the **SHORE POWER CORD** plugs into the **BOAT RECEPTACLE** and is
secured by a **THREADED LOCKING COLLAR** (locks the connection and improves water resistance).
- **Facts:** 125 V receptacles rated **15 A, 30 A, 50 A (125 V), or 50 A (125/250 V)**; 30 A and
  50 A systems have an AC control panel; a 15 A system usually feeds one device (e.g., a battery
  charger) with no panel.

# Ship Systems — Head & Waste

**DIAGRAM (KC-2044, page 11-16) — "Typical Dock Pumpout System":** the head/waste plumbing.
- **HEAD** (marine toilet, center) with a **MANUAL HAND PUMP**; waste line runs to the
  **HOLDING TANK** (starboard/aft block); a **VENT** keeps the tank at atmospheric pressure; a
  **SEACOCK** (below waterline) supplies raw flush water to the head; a **WASTE DOCKSIDE
  PUMPOUT FITTING** (deck plate marked **"WASTE"**) empties the tank via a ¾″ sanitary hose.
> **CAUTION:** Do not flush into a full holding tank — it could damage the waste system.

**DIAGRAM (KC-2045, page 11-17) — "Typical Overboard Discharge System":** adds a **"Y" VALVE**
between the head and the holding tank; the Y valve directs waste either to the holding tank or
to an **OUTLET SEACOCK** for overboard discharge. Operate overboard only in approved areas —
Y-valve in the overboard position and the outlet seacock open; close the seacock when not in use.

**DIAGRAM (KC-2046, page 11-17) — "Typical Macerator System":** a **MACERATOR PUMP** with a
**"Y" VALVE** and a **DISCHARGE SEACOCK**. The Y valve sits between the pumpout plate and the
macerator discharge seacock; it lets you either dockside-pump-out or run the macerator to pump
the holding tank overboard.
- **LOCATION note:** head/vanity is a cabin fixture; the holding tank, seacocks, macerator, and
  Y-valve are in the **bilge / below-sole**, aft toward the transom.

# Trailering, Slinging & Lifting

**Source pages:** sections 10-x (PDF pages 81–88) · **Applicability:** `[ALL]`

**DIAGRAM (KC-1866, page 10-8) — "Slinging/Lifting":** shows two lift methods — **LIFT RINGS**
with a **SPREADER BAR** (and **USE CHAFE PROTECTION**), and **SLINGS** with a **SPREADER BAR**
under the hull — plus bow/stern cross-section views of correct sling placement.
> **Facts:** attach lifting cables only to the **lifting eyes in the transom and bow** — never
> to cleats, ski-tow eyes, or handrails; cover cables to protect the finish; use spreader bars
> to keep lift pressure vertical; keep the **bow slightly higher than the stern** to prevent
> engine damage. (Trailering pages also cover hitch/safety-chains, backing, launching, loading.)

## Trailering Checklist (page 10-4)
**DIAGRAM (KC-1711) — trailer tie-down:** shows a **BOW TIE-DOWN** to the **WINCH STAND**, the
**WINCH LINE** to the bow eye, and the trailer **FRAME CROSSMEMBER**.
- Consult state laws for brake/axle-load requirements; check brakes and fluid before each trip.
- Check springs and undercarriage for loose parts.
- Check tire inflation (under-inflated tires overheat and fail).
- Check wheel bearings and lug nuts before each trip.
- Secure the boat with a line from the **bow eye to the winch line PLUS a bow tie-down** to the
  winch stand/tongue; tie the **stern down from the stern eyes**.
- Verify taillights and turn signals work before towing.
- Take down convertible top, side curtains, and back cover before highway towing.
- Carry a spare tire for trailer **and** tow vehicle, plus tools to change them.
- On extended trips carry spare wheel bearings, seals, and races.
- Check wheel hubs at every stop — if a hub is abnormally hot, inspect the bearing before continuing.
- Consult the engine operator's manual for engine-related trailering precautions.

# Special Gas Precautions & Fire System

**Source pages:** sections M-x (PDF pages 110–111) · **Applicability:** `[ALL]`

**DIAGRAM (CC-10, page M-2) — carbon-monoxide hazard:** a boat moored against a seawall with
engine/generator exhaust drifting along the seawall and up into a building's windows/hatches;
caption: **"Carbon monoxide from engines or generator can travel along a seawall and enter
windows or hatches."**
> **WARNING (facts):** CO is odorless, colorless, lethal — sources include engine/generator
> exhaust, ranges, heaters. Symptoms: flushed appearance, throbbing temples, inattentiveness,
> ringing ears, headaches, drowsiness, nausea, dizziness, fatigue, vomiting, collapse,
> convulsions — get the person to fresh air and medical help immediately. Holding-tank methane
> is also lethal in enclosed spaces: ventilate and don't smoke before working on it.

**DIAGRAM (KC-0084, page M-3) — "Automatic Halon Fire Extinguishing System":** the Halon
cylinder shown in two gauge states — **SYSTEM CHARGED** (needle in the charged band) and
**SYSTEM DISCHARGED** (needle low).
- **LOCATION / operation:** mounted in the **engine compartment**; auto-actuates at a preset
  temperature. On discharge you may hear a pop then rushing air — **shut down all electrical and
  mechanical systems**, and **do NOT open the engine hatch** (oxygen feeds the fire → flashback);
  let the agent soak **≥15 minutes**.
> **WARNING:** Halon and fire-byproduct fumes are toxic — do not breathe them. **CAUTION:**
> Halon cylinders must be weighed periodically to confirm they are adequately charged.

# Chapter 8 — Troubleshooting

**Source pages:** 8-1 to 8-3 (PDF pages 73–75) · **Applicability:** `[ALL]`
For engine-specific problems consult the engine owner's manual; some problems need a dealer.

## 8.1 Trouble Check Chart (Symptom → Possible Cause)

| Symptom | Possible causes |
|---|---|
| Engine will not crank | Emergency safety switch not connected; faulty ignition switch; throttle/shift control in gear; main circuit breaker open; battery terminals corroded; weak battery; battery switch OFF; engine problem |
| Engine cranks but will not start | No fuel in tank; fuel filter clogged; flame arrestor dirty; fuel valves closed; contaminated fuel; faulty fuel pump; bad spark plugs; engine problem |
| Poor boat performance | Excessive water in bilge; uneven load distribution; engine trim wrong; damaged/obstructed propeller; improper propeller selection; contaminated fuel; engine problem |
| Poor gas mileage | Engine trim wrong; marine growth on hull; plugged flame arrestor; faulty fuel pump; engine problem |
| Throttle/shifting problems | Corroded cable; kink in cable; engine problem |
| Excessive vibration | Propeller damaged or fouled; engine problem |
| Electrical problems | Blown fuse or open circuit; loose wiring connections; defective switch or gauge; weak battery |
| No power to AC outlets | Ground-fault circuit interrupter tripped; loose shore power cord; AC breaker |
| Sink/shower does not operate | Fresh-water pump breaker off; fresh-water tank empty; fresh-water pump defective |
| Head will not flush | Head circuit breaker off; weak/discharged battery; head seacock closed |
| Head will not empty | Discharge valve closed; line to holding tank blocked |

## 8.2 Detailed Troubleshooting — Engine & Power Train (M-4/M-5)

> **WARNING:** Disconnect battery cables before making checks or adjustments around engine and
> electrical components — injury or boat damage may occur.

| Problem | Possible cause | Solution |
|---|---|---|
| Engine will not start | Fuel valves closed / tank empty | Check valves or fill tank |
| | Contaminated fuel | Check for contaminants/water; if contaminated, drain tank & lines, flush with clean fuel, replace fuel filters; see dealer |
| | Loose wiring or bad key switch | Look for loose connections; technician replaces switch if needed |
| | DC main and/or ignition breakers OFF | Turn all breakers ON |
| | Weak or bad battery | Have battery tested or charged |
| | Corroded battery terminals | Clean terminals |
| Low starter speed | Loose wiring connections | Clean and tighten all connections |
| | Weak or discharged battery | Charge battery |
| Starter will not turn crankshaft | Defective starting switch | Dealer replaces switch |
| Lack of power | Throttle not fully open | Dealer adjusts throttle linkage |
| | Contaminated fuel | Drain, flush, replace filters; see dealer |
| Erratic engine speed | Pinched/clogged fuel lines or tank vent | Replace line or remove obstruction; see dealer |
| | Contaminated fuel | Drain, flush, replace filters; see dealer |
| Engine overheats | Cooling-water seacock closed or pick-up blocked | Open seacock or remove obstruction |
| | Leaking or pinched water lines | Repair/replace water lines; see dealer |
| Excessive vibration (some is normal) | Objects obstructing propeller | Reverse prop or cut/pull obstruction free |
| | Bent propeller | Replace as necessary |
| | Engine touching a brace/hull | Check mounts/alignment; see dealer |
| | Engine not timed / misfiring | Have engine tuned by dealer |
| Poor performance | Overloaded / weight badly distributed | Reduce/redistribute load; trim helps |
| | Material wrapped around propeller | Run prop in reverse or cut/pull material |
| | Damaged / wrong propeller | Inspect; replace as necessary |
| | Marine growth or hull damage | Clean or repair hull |
| | Excessive bilge water | Pump out; inspect hull for leaks |

## 8.3 Detailed Troubleshooting — Electrical (M-6)

> **CAUTION:** Never reset an automatically-tripped breaker without first locating and
> correcting the problem. Only certified electrical professionals should work on the system.

| Problem | Possible cause | Solution |
|---|---|---|
| Electrical component will not function | Breaker tripped/OFF | If tripped, correct problem & reset; otherwise turn breaker ON |
| | Weak/discharged battery | Charge battery |
| | Loose/broken wire connection | Connect/repair wire; install plug in outlet |
| Lights do not come on / are dim | Breaker tripped/OFF | Correct & reset, or turn ON |
| | Weak/discharged battery | Charge battery |
| | Loose/broken wire connection | Connect/repair wire |
| | Light bulb burned out | Replace bulb |
| Generator will not start | DC main breaker OFF | Turn breaker ON |
| No power at AC outlets | GFCI tripped | Reset outlet button & test; if it won't reset, DO NOT use outlets — have circuit checked by a qualified technician |

## 8.4 Detailed Troubleshooting — Plumbing (M-7/M-8)

| Problem | Possible cause | Solution |
|---|---|---|
| No water from cockpit washdown | Washdown-pump breaker tripped/OFF | Correct & reset, or turn ON |
| | Washdown switch OFF | Flip switch ON |
| | Strainer / hull inlet plugged | Clean strainer or clear inlet |
| | Seacock closed | Open washdown seacock |
| | Pump auto shut-off defective | Dealer checks pump |
| No water at showers/sinks | Fresh-water-pump breaker tripped/off | Correct & reset, or turn ON |
| | Fresh-water tank empty | Fill tank |
| | Pump defective | Dealer services pump |
| Low water pressure at all outlets | Water system lost its charge | Check for leaks / air leaks in accumulator; see dealer |
| | Weak/worn pump | Dealer services pump |
| Low pressure at only one outlet | Restriction/obstruction in line | Clean, repair, or clear the line |
| Shower sump overflows | Sump-pump breaker tripped/OFF | Correct & reset, or turn ON |
| | Discharge lines blocked/pinched | Remove obstruction or straighten line |
| | Pump / auto switch defective | Dealer services |
| Head will not flush | Head (FWD) breaker tripped/OFF | Correct & reset, or turn ON |
| | Low battery charge | Charge batteries |
| | Flush-water seacock not open | Open seacock |
| | Inlet pedal valve not working | Dealer services head |
| Head will not empty | Y-valve not open / line to holding tank blocked | Open Y-valve or remove obstruction |

## 8.5 Generator Set — Prestart (M-8) `[OPTION]`
1. Air cleaner clean and properly installed.
2. Battery connections and electrolyte level checked (if battery has filler caps).
3. Fuel tanks full and fuel system primed.
4. Oil level at or near the FULL mark.
(Read the generator's own owner's manual before operating.)

# Chapter 9 — Storage (Winter Lay-Up & Reactivation)

**Source pages:** 9-1 to 9-3 (PDF pages 77–79) · **Applicability:** `[ALL]`
> Improper storage damage is **not** covered by warranty. Perform annual maintenance at lay-up.

## 9.1 While the boat is still in the water
1. Fill fuel tank; add fuel stabilizer/conditioner per manufacturer.
2. Run the boat ≥15 minutes so treated fuel reaches the engine.
- **Note:** if storing >5 months, in high humidity, temperature extremes, or outdoors — "fog"
  the engine with rust-preventative fogging oil per the manufacturer; see dealer.

## 9.2 When the boat is removed from the water
- **Immediately remove the bilge drain plug;** raise the bow high to drain.
- Flush the engine cooling system with clean water — **do not exceed 1500 rpm.**
- Perform scheduled maintenance (stern drives: engine tune, oil & fuel-filter changes).
- Clean hull/deck/interior while growth is still wet; allow a couple days to air-dry (prevents mildew).
- Wax all surfaces; apply rust inhibitor to metal parts.
- Clean dirt/oil/grease from engine and bilge; touch up bare engine paint.
- Prepare the engine per the engine owner's manual.
- Store the bilge drain plug in a bag taped to the throttle lever (easy to find).
- Remove batteries; clean, fully charge, store above freezing, away from heat/spark/flame.
- Open all faucets; run the fresh-water pump to empty the tank and lines, then run it dry 1–2 min.
- Open all drains (including the water heater, if equipped).
- Empty and flush the holding tank.
- **Winterize the head:** close the inlet seacock, remove the inlet hose from the pump, attach a
  short hose, pour 1 quart of nontoxic antifreeze into a container, and pump until the colored
  fluid runs down the bowl rim.
- Close the outlet seacock.
- Remove strainer and seacock drain plugs (prevents freeze damage); close all seacocks.
- Support the hull properly to prevent damage.

## 9.3 If stored on a trailer
- Repack wheel bearings with water-resistant grease (or use bearing protectors + grease gun).
- Park in a protected area; a cradle is best; if outside, use a cover.
- Loosen tie-downs and winch line, but keep the boat resting properly on hull supports.
- Jack up the trailer and block the frame to relieve weight on tires/springs.
- Refer to engine and accessory manuals for further instructions.

## 9.4 Reactivating the boat after storage
- Charge and install batteries.
- Check engine/bilge for nesting animals; clean as needed.
- Inspect the engine for cracks/leaks from freeze damage.
- Check hose condition and clamp tightness.
- Install the bilge drain plug.
- Open/close all seacocks to verify operation; install all strainer/seacock drain plugs.
- Open faucets; fill the fresh-water tank (~20 gal), run the pump through the faucets, then fill full.
- Perform daily maintenance (and annual maintenance if not done at lay-up).
- If equipped with optional fresh-water cooling (stern drive) and it was drained, refill with coolant.
- Check and lubricate the steering system.
- Remove blocks from under the trailer frame; tighten tie-downs and winch line.
- Check trailer tire pressure and lug nuts.
- Launch and start (may need a minute of cranking to prime — allow 1 min cool-down per 15 sec of
  cranking); watch gauges, check for leaks/abnormal noise; keep speed low for the first 15 minutes.
- Refer to engine and accessory manuals for further reactivation steps.

# Appendix — Sample Float Plan (page 11-20)

A copy-and-fill template. Fill it out and **leave the copy with a reliable person** who can
notify the Coast Guard/rescue if you don't return as scheduled — **do NOT file it with the
Coast Guard.** Fields:
- **Operator:** Name; Telephone.
- **Boat description:** Type; Color; Trim; Registration Number; Length; Name; Make; Other Info.
- **Persons aboard:** Name; Age; Address & Telephone (multiple rows).
- **Engine:** Type; HP; No. of Engines; Fuel Capacity.
- **Survival equipment:** PFDs; Flares; Mirror; Smoke Signals; Flashlight; Food; Paddles; Water;
  Anchor; Raft or Dinghy; EPIRB.
- **Radio:** Yes/No; Type; Frequency.
- **Voyage:** Destination; Est. Time of Arrival; Expect to Return By.
- **Vehicle:** Auto Type; License No.; Parked (where).
- **If not returned by [time], call the Coast Guard or [Local Authority]** — record both phone numbers.

# Appendix (detailed) — AC/DC Panel Wiring Schematic (M-16)

**DIAGRAM (MONTEREY-9, page M-16) — detailed panel wiring schematic.** Unlike the M-13/14/15
topology diagrams, this page gives **breaker ratings, wire numbers, wire colors, and connector
pin assignments** for the distribution panels. It covers the **house AC/DC panel harness — NOT
the engine sender/tachometer harness** (those remain in the MerCruiser manual; see BUG-14).

**265 / 286 AC-DC Panel — DC side** `[265]` (40 A DC main, fed by "4 RED"):
| DC breaker | Rating | Wire | Term |
|---|---|---|---|
| Cabin Lights | 10 A | 14 BLU | 1 |
| Refrigerator | 5 A | 14 RED | 2 |
| Water Pump | 10 A | 16 BRN/GRN | 3 |
| Stereo | 10 A | 16 RED | 4 |
| Sump Pump | 5 A | 14 BRN/BLU | 5 |
| Macerator | 20 A | 8 BRN/WHT | 6 |
| Television | 15 A | 12 RED | 7 |
| Accessory | 10 A | (open) | — |

**265 / 286 AC-DC Panel — AC side** `[265]` (30 A / 30 A / 65 V mains; 125 V indicator light;
0–150 V AC voltmeter):
| AC breaker | Rating | Wire |
|---|---|---|
| Television | 15 A | 16 BLK |
| Refrigerator | 5 A | 14 BLK |
| Stove | 15 A | 14 ORG |
| Water Heater | 15 A | 14 BLK (#22) |
| Battery Charger | 15 A | 14 GRN (#20) |
| Microwave | 15 A | 14 RED (#18) |
| Outlet | 15 A | 14 BLU |
| Air Conditioner | 20 A | 14 BLK (#4) |
| Coffee Maker | 15 A | 14 BRN (#17) |
| Accessory | 15 A (×2) | — |

**Connector housings (265/286):** three **9-position, 25-amp socket housings** (Housing #1/#2/#3)
carrying circuits **AIR, TR(im?), STOVE, OUTLET, FRIDGE, MICRO, WATER HEATER, BATT CHRG, COFFEE**
with **14 WHT / 14 GRN / 14 BLK** conductors. Assembly notes on the drawing: *"all wires run with
4 RED," "all housings hang 18″ off of panel," "ty-wrap wires together then over with DC ground."*

**246 AC-DC Panel** (bottom of sheet): DC main 30 A; DC breakers **Fridge 5, Sump Pump 6, Cabin
Lts 7, Water Press 6, Accy 15, Accy 10** (wire colors incl. 10 BLK, 10 RED, 14 RED, 14 BRN/BLU,
16 BLU, 14 BRN/GRN, 14 BRN/WHT). AC breakers **Outlets 18, Fridge 7, Wtr Htr 15, Stove 15, Batt
Chrgr 11, Access 10** (14 BLK, 12 BLU, etc.). Housing pin groups: **1-4-7 STOVE, 2-5-8 STOVE,
3-6-9 FRIDGE, 10-11-12 BATT CHRGR, 13-14-15 WTR HTR, ACC-MICROWAVE (16/17/18)**.

---

# Appendix — Wiring Diagrams (M-13 / M-14 / M-15)

**Source pages:** PDF 121–123 · **Applicability:** one diagram per model (246 / 265 / 286)

> **What these diagrams are — and are NOT.** Each is a **component-location / topology
> diagram**: a top-down (plan) view of the hull with every electrical device drawn at its
> approximate physical position and lines showing the power runs back to the distribution
> panel and batteries. They **do NOT** show wire colors, gauge/sender pin assignments, or the
> engine harness. For engine sender, gauge, and tachometer wire identification (e.g., the
> CX5106 / BUG-14 work) the source of truth is the **MerCruiser engine manual** plus on-boat
> multimeter identification — not this diagram. `[d3kOS cross-ref: BUG-14, BUG-17]`

## 265 Wiring Diagram (M-14, art "MONTEREY-7") `[265]`

**DIAGRAM — full description:** A top-down outline of the 265 hull, bow at top, stern at
bottom. Electrical components are placed at their physical locations and joined by lines
representing wiring runs. **Line styles:** heavy solid lines = main DC/AC power runs routed
along the port and starboard sides; dashed lines = overhead / masthead runs.

**Power source and distribution (stern, starboard side):**
- Two batteries, each labeled **BATT**, at the stern-starboard.
- **BATTERY SWITCHES** on the starboard side, fed from the batteries.
- Main power runs route forward from the battery switches along both sides of the hull to the
  **AC-DC PANEL** and **STEREO PANEL** (port side, amidships), which distribute to the loads.

**Loads by zone (bow → stern), as drawn:**
- **Bow / forward cabin:** PORT FWD SPEAKER and STBD FWD SPEAKER (either side of the bow), a
  120-volt outlet, and several cabin **LIGHT**s down both sides. **MASTHEAD LIGHT** is reached
  by a dashed (overhead) run.
- **Galley (port, mid-forward):** STOVE, COFFEE MAKER, MICROWAVE, and FRIDGE clustered
  together, with a nearby LIGHT.
- **Midships:** AC-DC PANEL and STEREO PANEL (port); SUMP PUMP; **120 VOLT CABIN OUTLET** and a
  second **120 VOLT OUTLET**; the **HELM** on the starboard side; additional LIGHTs.
- **Cockpit / aft:** PORT AFT SPEAKER and STBD AFT SPEAKER, plus cockpit LIGHTs across the beam.
- **Tankage (drawn as blocks across the beam, ahead of the stern cluster):** FRESH WATER,
  FUEL TANK, HOLDING TANK.
- **Stern / bilge cluster:** WATER HEATER, BATTERY CHARGER, HALON (fire suppression),
  FLOAT SWITCH, BILGE PUMPS, WATER PRESSURE (pump), MACERATOR, BLOWERS, TRIM TAB, a
  **TO ENGINE** connection point, DRIVE TRIM, and **STERN LIGHT** at the transom.

**Key takeaways for querying:**
- Batteries → battery switches → panel → loads is the DC topology.
- The single **TO ENGINE** connection is the only engine tie-point shown; the engine's internal
  wiring and senders are covered by the engine manufacturer's manual, not here.
- AC (120 V) loads (outlets, water heater, battery charger, galley appliances) are fed via the
  AC-DC panel from shore power / charger, not the DC battery bus.

## 246 Wiring Diagram (M-13, art "MONTEREY-8")
Same top-down hull-topology format as the 265. Component placement, bow → stern:
- **Bow tip:** NAVIGATION LIGHT. **Forward cabin:** cabin LIGHTs both sides; PORT FWD /
  STBD FWD SPEAKER; 120 VOLT OUTLET; OVERHEAD LIGHT; STOVE and FRIDGE (galley, port).
- **Midships:** AC-DC PANEL + STEREO PANEL (port); SUMP PUMP; HELM (starboard); 120 VOLT CABIN
  OUTLET; FUEL TANK (center, dashed outline); PORT AFT / STBD AFT SPEAKER.
- **Stern cluster:** WATER HEATER, BATTERY CHARGER, LIGHT, WATER PRESSURE PUMP, MACERATOR,
  HOLDING TANK, PUMP FLOAT SWITCH, BILGE PUMPS, **MAIN GROUND**, TO ENGINE, DRIVE TRIM (one),
  TRIM TABS, HALON, BLOWERS, MASTHEAD LIGHT, BATTERY SWITCHES, two **BATT**.
- **Differences vs 265:** simpler galley (no microwave / coffee maker); explicit **MAIN GROUND**
  node; labeled **NAVIGATION LIGHT** and **OVERHEAD LIGHT**; single **DRIVE TRIM**.

## 286 Wiring Diagram (M-15, art "MONTEREY-6")
Same format; the largest load set of the three. Component placement, bow → stern:
- **Bow / forward cabin:** PORT FWD / STBD FWD SPEAKER; cabin LIGHTs both sides; a 120 VOLT
  OUTLET; **TELEVISION CABLE**; galley cluster COFFEE MAKER, FRIDGE, STOVE, **GALLEY LIGHT**,
  MICROWAVE; MASTHEAD LIGHT; **NAV LIGHT on both sides**.
- **Midships:** AC-DC PANEL + STEREO PANEL (port); SUMP PUMP; another 120 VOLT OUTLET; HELM
  (starboard); 120 VOLT CABIN OUTLET; several more cabin/cockpit LIGHTs.
- **Aft:** FUEL TANK and HOLDING TANK (center-aft blocks); PORT AFT / STBD AFT SPEAKER.
- **Stern cluster:** BATTERY CHARGER, HALON, WATER PRESSURE PUMP, MACERATOR, **TRIM TAB PUMP**,
  WATER HEATER, PUMP FLOAT SWITCH, BILGE PUMPS, TO ENGINE, BLOWERS, **two DRIVE TRIM**,
  BATTERY SWITCHES, two **BATT**; NAVIGATION LIGHT at the transom.
- **Differences vs 265:** adds TELEVISION CABLE, extra 120 V outlets, GALLEY LIGHT, dual NAV
  lights, a TRIM TAB PUMP, and **two DRIVE TRIM** units (twin-drive configuration).

---

<!-- DOCUMENT COMPLETE (S106 2026-07-24). Every diagram in the 126-page source has been rendered
     from the PDF and described in text, organized for AI retrieval with a spatial locator frame
     for "where is X?" queries. Coverage: Ch1 Boating Safety, Ch2 Rules of the Road, Ch3 Controls
     & Indicators, Ch4 Operation, Ch5–6 Getting Underway/Running, Ch7/Ship Systems (DC + AC
     electrical, fresh water, head & waste, overboard/macerator), Trailering & Slinging, Special
     Gas & Fire systems, all four hull wiring diagrams (246/265/286 + M-16 detailed AC/DC panel
     schematic with wire colors). Text-only pages with no diagrams (portions of Ch1 minors/gas,
     Ch3 switch prose, trailering procedure text, Ch8–9 troubleshooting/storage charts) are
     summarized in their sections. NOTE: engine sender/gauge/tachometer wire colors are NOT in
     this boat manual — see the MerCruiser engine manual (BUG-14). -->

# Appendix — Text-Only Sections (no diagrams)

For completeness, these source sections carry no substantive illustrations (only chapter-header
icons) and are captured as facts in their chapters or summarized here:
- **Ch1 (1-11 to 1-14):** Operation by Minors, Passenger Safety, Water Sports, General
  Precautions (no alcohol/drugs while operating), Special Gas Precautions intro.
- **Ch2 (2-1, 2-2):** hazard prose — dam spillways, shallow-water operation, sand bars, warning
  markers.
- **Ch7 / Ship Systems prose:** salt-water care, freezing-temperature layup, corrosion
  protection / bonding narrative, steering-system service.
- **Ch8 Troubleshooting & Ch9 Storage:** now fully transcribed above as tables/lists (Trouble
  Check Chart, detailed Engine/Electrical/Plumbing charts, generator prestart, winter lay-up and
  reactivation procedures). The Safety Checklist (Ch5), Trailering Checklist (Ch10), and Sample
  Float Plan are also transcribed. **Nothing is omitted.**
