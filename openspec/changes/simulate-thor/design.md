## Context

Thor is a 625 mm, six-degree-of-freedom, 3D-printed robot arm published by
Ángel L.M. under CC-BY-SA-4.0. Its configuration is yaw-roll-roll-yaw-roll-yaw
and it carries 750 g. The repository ships four things, and each answers a
different question:

- `step/*.step` — fifty printed parts, one product per file, product name
  equal to the file basename, exact B-rep. **The source of truth for
  printed geometry.**
- `stl/*.stl` — the same parts tessellated for printing. Redundant with the
  STEP for our purpose, and less precise; used only for cheap measurement.
- `freecad-src/Assembly*.FCStd` — a FreeCAD Assembly4 model: one top
  document linking six sub-assembly documents, each linking its parts.
  Assembly4 **stores every link's solved placement**, so these files carry
  the complete world pose of the machine at the home pose. **The source of
  truth for placement.**
- `doc/ThorDimensions.png` — the author's own axis-measure drawing:
  202.00 mm base to shoulder, 160.00 mm shoulder to elbow, 195.00 mm elbow
  to wrist, 67.15 mm wrist to tool. **The source of truth for reach.**

`mods/` holds user contributions (split parts, alternative electronics,
end effectors); the pilot asked for the build the design ships, so `mods/`
is out.

The FreeCAD documents also place every bought part — steppers, bearings,
pulleys, belts, shafts, fans, magnets, sensors, the servo, the control
board — as internal `App::Part` groups with their own geometry. Those
groups are read for their **frames**, and the parts themselves are drawn in
Python from catalogue dimensions, because the design does not ship them as
printable parts and a simulation should not embed someone else's component
library.

The design ships **no fasteners at all**. The pilot asked for a full build
with bolts and nuts, so they are derived from the printed parts' own
geometry.

There is no `pyproject.toml`, no Python, no test suite and no OpenSpec
record in the repository today.

## Coordinates

The machine frame is the FreeCAD assembly's own frame, unchanged: **Z up,
origin on the mounting face of `BaseBot`**, X toward the electronics box's
open side, Y completing the right-handed set. At the home pose the arm
stands fully extended along +Z and the tool points up. Every number below is
in that frame, in millimetres and degrees.

The six joints, measured from the assembly's own solved placements:

| driver | joint | axis | through | at rest |
| --- | --- | --- | --- | --- |
| `art1` | base yaw | +Z | (0, 0, ·) | 0° |
| `art2` | shoulder roll | +Y | (0, ·, 202.0) | 0° |
| `art3` | elbow roll | +Y | (0, ·, 362.0) | 0° |
| `art4` | forearm yaw | +Z | (0, 0, ·) | 0° |
| `art5` | wrist roll | +Y | (0, ·, 556.0) | 0° |
| `art6` | tool yaw | +Z of the wrist | wrist centre | 0° |
| `grip` | finger opening | — | — | open |

Each driver measures the joint's own rotation from the home pose the
FreeCAD assembly records, in degrees, positive by the right-hand rule about
the stated axis. `grip` is the clear opening between the two finger faces in
millimetres. Nothing is measured in motor steps: the maker drives joints,
the model turns the motors.

Cross-check against the author's drawing: 202.0 base-to-shoulder matches
exactly; 362.0 − 202.0 = 160.0 shoulder-to-elbow matches exactly;
556.0 − 362.0 = **194.0** against the drawing's 195.00 (see Finding 1).

## Goals / Non-Goals

**Goals**

- The complete machine the repository ships: every printed part in the
  FreeCAD assembly, every bought component it places, and the fasteners its
  holes imply.
- Six joints plus a gripper, drivable in the browser, each in the builder's
  own terms.
- Transmissions that actually transmit: the shoulder's twin pinions in the
  internal ring gear, the elbow belt, the forearm pinion on its column
  gear, the wrist differential, the gripper linkage — each phased so it
  meshes, each provable by a contract.
- Fasteners placed from the parts' own holes, with the screw length each
  stack actually needs, not a guess.
- An honest interference record: the design's own home pose has fifteen
  overlapping part pairs, and the model says exactly which.

**Non-Goals**

- Editing, repairing or regenerating any upstream file.
- Electronics internals, wiring, cable routing (no evidence in the design).
- Motor step counts, firmware, G-code, ROS2 or Asgard (other repositories;
  our drivers are joint angles).
- Print supports, shrinkage or tolerance compensation (printer properties).
- The `mods/` variants and the alternative end effectors.
- Dynamics, payload deflection, torque. Kinematics only.

## Decisions

**D1 — Printed parts are `StepNode`, one class per part, reading
`step/*.step` in place.** Alternatives: `StlNode` on `stl/*.stl` (faceted,
loses the exact kernel, and the contracts here need exact answers about
gear meshes measured in fractions of a millimetre), or re-drawing parts
(forbidden). Each file holds exactly one product named after the file, so
no `part=` is needed. Measured cost: the fifty files load in about 15 s
total, the heaviest (`Art56GearPlate`, 13 MB) in 1.2 s, and each
tessellates in under 0.7 s at the default 0.1 mm — cheap enough to keep
exact geometry throughout.

**D2 — Placement comes from the FreeCAD assembly, transcribed into
`simulation/layout.py`, and a test re-reads the `.FCStd` files and compares
every value.** Assembly4 writes each link's solved global placement into the
document, so the numbers are the design's own, not a reconstruction. The
build's static import walk cannot see a zip file read at runtime, so the
layout must be transcribed rather than parsed at build time; the drift test
is what keeps the transcription honest. Verified before writing any node:
all 64 printed instances placed by these numbers reproduce the machine, and
the assembled bounding box is 219.4 × 200.0 × 701.0 mm.

**D3 — Bought parts are drawn in Python in `simulation/hardware.py`, in the
frames the FreeCAD internal parts use.** Measured from those parts' own
`.brp` shapes, so a catalogue part drops into the design's placement
unchanged:

| component | local frame | size |
| --- | --- | --- |
| `Stepper_Nema17x34` | flange face at z=0, shaft +Z | 42.3 sq, body+shaft to z=54 |
| `Stepper_Nema17x40` | as above | to z=60.1 |
| `Nema17_GearBox` | as above | 42.3 sq, to z=78.3 |
| `Bearing_625ZZ` | bore centred, one face z=0 | Ø16 × 5, bore Ø5 |
| `Bearing_MF84ZZ` | as above | Ø9.2 flange, Ø8 × 3, bore Ø4 |
| `Bearing_16014zz` | as above | Ø110 × 13, bore Ø70 |
| `Pulley_GT2x20` | bore centred, base z=0 | Ø18 × 22.9 |
| `GT2x40PulleyM4` | as above | Ø28 × 17 |
| shafts `4×14`, `5×14.5`, `5×32`, `5×102`, `5×128` | one end at z=0, +Z | Ø4 or Ø5 |
| `Collar5mm` | centred z=0 | Ø10 × 5, bore Ø5 |
| `Magnet` | face z=0 | Ø8 × 1 |
| `Fan_40x40` / `Fan_50x50` | centred, face z=0 | 40×40×10 / 50×50×11 |
| `Servomotor` + horn | horn hub at z=0 | horn Ø21 × 5.5 |
| `OpticSensor`, `MicroEndstop`, `ArduinoMega`, buttons, jack, M8 connector | as measured | envelopes |

Alternative considered: extracting the `.brp` shapes from the FreeCAD
documents into STEP and importing them. Rejected — it would copy a
component library the design does not own into this repository, and the
catalogue dimensions are public and simple.

**D4 — Fasteners are derived from the printed parts' own geometry, not
invented.** The probe reads every cylindrical face of each STEP solid,
transforms it to world coordinates, and keeps three signatures measured
across the whole machine:

- **Ø3.4 mm** (radius 1.70) — M3 clearance hole. 400 faces found.
- **Ø5.9 mm** (radius 2.95) — M3 socket-head counterbore. 192 faces.
- **Ø4.2 mm** (radius 2.10) — M4 clearance. 4 faces, in the belt tensioners.
- **5.8 mm across flats** (six planes at 2.90 from the axis) — M3 hex nut
  pocket, i.e. a 5.5 mm nut with 0.3 mm print clearance.

Coaxial faces are clustered (axis directions parallel to 1e-4, axis lines
within 0.15 mm), giving 168 fastener axes. Each axis's per-part axial
intervals are merged with a 1.0 mm gap tolerance into **contiguous stacks**;
a cluster that spans a joint gap is two fasteners, not one long screw. Each
stack gets the shortest standard M3 length (6, 8, 10, 12, 16, 20, 25, 30,
35, 40, 45, 50 …) that spans it plus the nut where the design cut a pocket,
head on the counterbored end, or on the outer end where there is none.
The probe stays as `simulation/tools/probe.py`; its readings go to
`docs/measurements.md`; the resulting table is transcribed into
`simulation/fasteners.py` so the build's source tracking can see it.

Alternative considered: transcribing the published Bill of Materials. It
gives counts and lengths but no positions, so it cannot place a single
screw; it is used only to sanity-check the derived totals.

**D5 — Gear phase is an assembly act, not a design value, so the model
phases each pair to mesh.** The design's own home pose has every gear pair
interpenetrating: measured 46.2 and 3.2 mm³ at the two shoulder pinions,
34.8 mm³ at the forearm pinion, 23.6 mm³ at the base pinion, 0.5 and
0.2 mm³ at the wrist bevels. A builder puts a printed pinion on its shaft at
whatever angle drops into mesh; the FreeCAD assembly simply never bothered.
Each pair's phase is therefore **measured** — the pinion is swept through
one tooth pitch against its mate on the exact kernel and the centre of the
window in which the pair shares least is taken — and recorded in
`layout.MESH` with the window width, which is the pair's backlash and the
bound the engagement contracts use. Sweeping the whole of a crown plate
that is thirteen megabytes of STEP costs minutes per phase, so the mate is
trimmed once to the box the pinion sweeps through and the sweep then runs
on a solid the size of the pinion.

| pair | phase | window | least shared |
| --- | --- | --- | --- |
| base pinion | 23.40° | 0.05° | 0.1965 mm³ |
| shoulder pinion, −x | 31.5° | 5.0° | 0 |
| shoulder pinion, +x | 19.5° | 5.0° | 0 |
| forearm pinion | 31.0° | 4.0° | 24.2991 mm³ |
| wrist bevel, −x | 0.4° | 0.4° | 0 |
| wrist bevel, +x | 23.4° | 0.4° | 0 |

Two pairs never reach zero however they are phased, and what fouls is not a
tooth: those floors are findings, recorded in `simulation/seats.py`.

Alternative considered: keeping the design's phase and admitting the
overlaps into the seats inventory. Rejected: gears that overlap at rest
sweep straight through each other when driven, which is precisely the thing
the model exists to disprove.

**D6 — Where the design's own parts overlap for reasons phase cannot fix,
`simulation/seats.py` is an inventory, and the contract is that the found
set is exactly that set.** No epsilon anywhere. Measured at the home pose
over all 64 printed instances (142 bounding-box-overlapping pairs, exact
booleans):

| mm³ | pair |
| --- | --- |
| 3248.867 | `Art56GearPlate` × `GripperBot` |
| 24.074 | `Art3Body` × `Art4Optodisk` |
| 0.202 | `Art2BodyA` × `Art2BodyACover2` |
| 0.020 | `GripperBot` × `GripperTop` |
| 0.004 | `GripperBot` × `GripperPassiveArm` |
| 0.003 | `GripperBot` × `GripperArm001` |
| 0.002 | `GripperBot` × `GripperArm` |
| 0.001 | `Art1Top` × `Art1FanHolder001` |
| 0.000 | `GripperArm001` × `GripperFinger` |

plus the five gear pairs D5 removes. The 3248.9 mm³ gripper-to-gear-plate
overlap is a mounting boss the design sinks straight into the plate rather
than rebating; it is a finding, not an error we may quietly fix.

**D7 — Every seated part stands 0.05 mm off its seat** (`SEAT_GAP`), because
two coincident faces cannot be asked whether they touch. The gap is applied
along the seat normal in `render()` and named in each node's docstring.

**D8 — Belts are molejo flexible parts driven from their pulley centres.**
Three belt runs: the long GT2 from the shoulder-axis pulley to the elbow
pulley (160 mm centres), and the two 208 mm GT2 loops in the forearm driving
the wrist differential (98 mm centres). Each is a `MolejoNode` whose path
parameters are ports fed from the pulley angles, so a belt is redrawn as the
joint moves rather than frozen at the home pose. Alternative: importing the
design's own belt solids from the FreeCAD documents — rejected, they are
frozen at one pose and cannot move.

**D9 — The elbow belt's driving pulley is coaxial with the shoulder axis,
and the model says so.** `Nema17_GearBox003` sits at the shoulder axis in
the `Art1` frame (0, 29.05, 123) driving `Pulley_GT2x20_Modified` at
(0, −56.35, 123), which is on the art2 axis; the driven `Art3Pulley` is on
the art3 axis. Because the driver is carried by `Art1` and not by the upper
arm, the belt holds the elbow at a constant **absolute** orientation while
the shoulder swings: moving `art2` alone changes the elbow's angle relative
to the upper arm without any elbow motor turning. `art3` is declared as the
elbow's absolute angle, which is what the belt actually controls, and the
relative angle follows.

**D10 — The wrist is a differential and is driven by intent.** Two
`Nema17x34` motors in the forearm drive, through the two 208 mm belts and
their GT2 pulleys, the two `Art56SmallGear` bevel pinions facing each other
on the wrist axis; both mesh the `Art56GearPlate` crown. Sum turns the wrist
(`art5`), difference turns the tool (`art6`). The maker gets `art5` and
`art6`; the pinion angles, belt runs and motor shafts are solved inside and
bound through ports, so the two motors visibly turn together for a wrist
roll and against each other for a tool roll.

**D11 — The control surface is six joint drivers plus `grip`.** Seven
sliders, at the top of what the craft skill tolerates, and every one of them
is a thing a maker can predict before moving it: this is a six-axis arm and
its axes are its meaning. Grouping them would hide the machine. The motors,
pinions, belts, optical discs and the differential are all solved from these
seven and exposed as ports on the sub-assemblies, so nothing is
unreachable later.

**D12 — Sub-assemblies mirror the design's own six documents**, one module
each: `base.py`, `art1.py`, `art2.py`, `art3.py`, `art4.py`, `art56.py`,
plus `gripper.py` split out of `art56` because it is a mechanism of its own.
Each owns its parts and declares ports for what its parent must tell it.
`thor.py` is the root: it declares the seven drivers and the instructions,
binds every port including the ones it holds at zero, and is the manifest's
model. The ground-up classes (`Base`, `Art1`, … ) exist so the README can
name a build sequence and `solid build simulation/art4.py:Art4` works.

**D13 — Layout numbers live in `simulation/layout.py`, a module defining no
node**, imported by every sub-assembly from that module directly and never
through the package `__init__.py`, so the framework's import walk
invalidates exactly the nodes that read an edited number.

## Findings

Recorded as measured; none is fixed upstream, and telling the author is the
pilot's decision.

1. **The author's dimension drawing says 195.00 mm from the elbow axis to
   the wrist axis; the FreeCAD assembly puts them 194.00 mm apart**
   (elbow at z=362.0 from `Art3Pulley` on the `Art3` origin, wrist at
   z=556.0 from the `Art56` link placement). The other two spans on the
   same drawing, 202.00 and 160.00, match the assembly exactly.
2. **No gear pair in the assembly is phased to mesh.** All five printed
   gear pairs interpenetrate at the home pose, by 0.2 to 46.2 mm³. Fixed in
   the model by measuring each pair's clear window (D5).
3. **The two shoulder pinions need different phases** — about 32.5° and
   20.5° about their own axes — even though the design places them
   symmetrically at x = ±21.5. They are mirrored instances of one part, so
   their local frames differ by the mirror.
4. **The shoulder's internal ring gear runs about 1.2 mm closer to its
   pinions than a standard profile would put them.** The ring has 60 teeth
   with a fitted root radius of 61.83 and tip radius 57.66 about a centre
   at (0.001, 0.003) of `Art2BodyA`'s own frame, giving a pitch radius near
   59.5; the pinions have 10 teeth with a tip radius of 12.00 and a root
   radius of 7.34, pitch radius near 10. The nominal internal centre
   distance is therefore about 49.5, and the assembly places the pinions at
   48.34. The pair still has a clear mesh window, so the model runs them
   where the design puts them.
5. **`GripperBot` is sunk 3248.9 mm³ into `Art56GearPlate`.** The gripper
   base's mounting boss occupies the same space as the plate it bolts to;
   nothing in either part rebates for the other.
6. **`Art4Optodisk` passes 24.1 mm³ through `Art3Body`'s wall.** The
   optical disc's rim overlaps the body rather than running in a slot cut
   for it.
7. **Three parts are drawn and exported but never placed.**
   `Art56Interface`, `Art1OptoFix` and `Art4BearingPlug` are in `step/`,
   `stl/` and `freecad-src/` and appear in no assembly document; the
   gripper mounts directly to the gear plate.
8. **`GripperFinger` is used mirrored.** The design places one
   `GripperFinger` and one `Part::Mirroring` of it; only the unmirrored
   part is exported to `step/` and `stl/`, so a builder printing from the
   published files gets two identical fingers, not a handed pair.
9. **The design models no fastener.** Every joint's screws and nuts are
   implied by holes and pockets and stated nowhere in the repository. The
   model derives 181 of them, 77 with nuts, and leaves 85 further hole
   stacks unclassified because nothing in the geometry says whether they
   take a screw.
10. **The base pinion has no interference-free phase.** It stands 2 mm
    taller than `Art1Bot`'s fifty-tooth ring, and its top rim cuts the rim
    above the teeth by 0.1965 mm³ at every phase.
11. **The forearm pinion's lower flange fouls the transmission column.**
    The flange is 12.0 in radius against the teeth's 10.8, and the ring at
    the foot of the column's twenty-tooth gear is not relieved for it:
    24.2991 mm³ at every phase.
12. **The arm's two belt pulleys share only 3.65 mm of land for a 6 mm
    belt.** Their running surfaces, along the shoulder axis in the upper
    arm's frame, are 12.650–21.651 on the drive pulley and 18.000–33.000
    on the elbow pulley. The model centres the belt at 19.825, in the
    middle of what the two do share, and records the shortfall. The
    forearm's pulleys, by contrast, share their whole 7.5 mm land, which
    is what makes this a finding about the arm and not about the model.
13. **The forearm belts are named for 208 mm and their pulleys need
    223.5.** The design's own belt solid measures about 220 mm, so the
    name is what is wrong; a builder buying by it gets a belt that cannot
    close.
13a. **The arm's two sprung tensioners do not reach its belt.** They run
    on Ø12 surfaces at (±14.5, 99.85) and the taut run passes 11.41 mm
    from their centres — 5.41 mm clear of the rims. They are solved
    retracted, so the belt is a two-pulley loop of 462.98 mm (231.49
    teeth) and the tensioners are what take up the difference between that
    and a belt made in whole teeth.
14. **All three belt solids are placed where their pulleys are not.** Both
    forearm belts lie flat in a plane perpendicular to their pulleys' axes,
    and the arm's belt is placed clear of both of its pulleys.
15. **Two published parts are exported inside out**, `Art2MotorGear` at
    −8435.0 mm³ and `Art4BodyBot` at −113674.9 mm³.
16. **`GripperActiveArm` and `GripperPassiveArm` each hold two solids**:
    the arm, and a loose Ø3.4 × 5.0 pin of 45.4 mm³ standing in its outer
    pivot hole with 0.3 mm of clearance. A builder slicing those files
    gets a plug printed inside the hole.
17. **Seven printed parts tessellate to a mesh that is not closed** at the
    default 0.1 mm deflection, although their exact geometry is sound:
    `Art1Body`, `Art1Top`, `Art1GearMotor`, `Art2BodyB`, `Art2MotorGear`,
    `Art3Body` and `Art4BodyBot`. Every contract here is therefore decided
    on solids.
18. **`Art3Pulley` has 117 teeth**, not the 126 a Fourier count of its own
    section suggests: its 37.000 tip radius gives 117.04 through GT2's own
    geometry, and the section samples too little of the circle to count.
19. **`Art1Top` is one solid that tessellates into five bodies**: the
    part, three two-triangle patches of zero volume 5.0 × 23.4 in extent,
    and a detached 3220.9 mm³ lug. Its exact geometry is a single solid of
    530398.4 mm³. This is finding 17 seen from the other side, and it is
    why solid connectivity is asked of the B-rep here rather than of the
    mesh.

### Findings for the framework

Recorded in the shop's `docs/warts.md` under Thor, not fixed here:

- `assertNoDisconnectedSolids` answers on the STL even when the node is
  exact, so `Art1Top` fails as five bodies while its solid is one.
- The faceted kernel cannot run this machine at all: seven of its parts
  tessellate non-manifold and every faceted comparison touching one of
  them raises rather than answering, which leaves an exact run — about an
  hour for the whole-model interference scan — as the only kernel.
- There is no public way to ask which pairs of an assembly interfere and
  by how much: `assertNoSolidInterference` raises on the first pair. A
  machine whose own design overlaps must reach for
  `_placed_assembly_solids`, `_bounds_candidates` and
  `_candidate_intersection`, which `simulation/seats.py` does.
- A flexible leaf's snapshot STL is imported by bare filename, so an
  assembly in a different Python package from the leaf renders it as
  nothing at all, silently. `simulation/beltview.py` sits beside the model
  rather than under `simulation/tools/` for that reason alone.

## Risks / Trade-offs

- **Exact interference over ~290 solids is slow.** The 64 printed parts
  alone took 100 s for one instant. → Build and iterate on
  `solid test --faceted`; sweep the animation there; run the exact kernel
  once at the end, and report the wall clock honestly rather than thinning
  the contract.
- **The derived fastener table could be wrong about a stack.** A hole
  cluster is geometry, but "this stack takes a 16 mm screw and that one a
  nut" is an inference. → Every fastener is checked by contract (the screw
  spans its stack, the nut sits in its pocket, no fastener fouls a moving
  part), the totals are compared against the published Bill of Materials,
  and any stack the probe cannot classify is listed in
  `docs/measurements.md` rather than silently given a default.
- **Joint travel limits are not published in this repository.** → Driver
  `range` is declared from the mechanism's own measured travel where the
  geometry bounds it (the base's slewing ring, the wrist's differential)
  and otherwise as the full circle, with the assumption named in the README
  and the spec. Ranges are presentation metadata and never clamp, so a
  wrong range cannot make the model lie about geometry.
- **The elbow belt's coupling (D9) will surprise a maker** who expects
  `art3` to be the elbow's angle relative to the upper arm. → The spec
  states the absolute convention, the README says it in the driver table,
  and an instruction demonstrates it.
- **A `MolejoNode` belt is a flexible part and can never be proved not to
  interfere the way a rigid one can.** → Belt contracts assert path
  geometry (the run reaches both pulleys, wraps the measured arc, keeps its
  measured length) rather than volume.

## Open Questions

- The `Art3Pulley` tooth count is measured at build time from its own
  geometry; if it does not come out an integer multiple consistent with a
  GT2 profile, the belt ratio is a finding rather than a value.
- Whether any fastener stack the probe classifies as "screw into plastic"
  is in fact a heat-set insert. The design shows no insert bore, so the
  model assumes self-tapping into the print; this is recorded, not hidden.
