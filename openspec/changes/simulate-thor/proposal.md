## Why

Thor is published as fifty printed parts, a FreeCAD assembly and an assembly
video. Nothing in the repository is the robot: no file answers whether the
long GT2 belt still reaches its pulleys when the shoulder swings, whether the
wrist differential's two bevel pinions actually mesh the crown plate, whether
the gripper linkage closes without the arms passing through each other, or
which M3 screw length a given hole stack actually needs. The FreeCAD assembly
holds the answer for exactly one pose — the fully extended home pose — and it
holds no fasteners at all.

A simulation layer turns the parts into the machine: six joints a maker can
drive in a browser, every bought component in its seat, every bolt and nut
placed where the parts' own holes put them, and contracts that fail when an
interface stops holding.

## What Changes

- A new `simulation/` package inside this repository. Nothing under
  `stl/`, `step/`, `freecad-src/`, `mods/` or `doc/` is edited, moved or
  regenerated.
- Printed parts enter as `StepNode` leaves reading `step/*.step` directly —
  exact geometry, one class per printed part, no geometry restated.
- Placements are transcribed from the design's own FreeCAD Assembly4
  documents into `simulation/layout.py` in millimetres and degrees, with a
  test that re-reads the `.FCStd` files and compares every value.
- Bought parts the design places but does not draw as printable parts —
  NEMA 17 steppers (34 mm, 40 mm, and the geared shoulder motors), 625ZZ /
  MF84ZZ / 16014ZZ bearings, GT2 20T and 40T pulleys, 5 mm shafts, shaft
  collars, magnets, 40 and 50 mm fans, opto sensors, a micro endstop, the
  gripper servo and its horn, the control board and its panel furniture —
  are drawn in Python from catalogue dimensions in `simulation/hardware.py`,
  in the frames the design's own assembly uses.
- **Bolts and nuts, which the design does not model at all**, are derived
  from the printed parts' own geometry: Ø3.4 mm clearance holes, Ø5.9 mm
  socket-head counterbores and 5.8 mm across-flats hex pockets are found in
  the STEP solids, clustered into contiguous world-space stacks, and each
  stack is fitted with the shortest standard M3 screw that spans it, plus a
  nut where the design cut a pocket for one. The probe that measures them is
  kept as `simulation/tools/probe.py` and its readings in
  `docs/measurements.md`.
- Belts become molejo flexible parts driven from their pulley centres, so
  the shoulder-to-elbow belt is redrawn as the arm moves rather than frozen.
- Six joint drivers plus a gripper opening, in the builder's own terms
  (`art1` … `art6`, `grip`), and a small set of instructions that pose the
  robot.
- Contracts for every interface the drawings leave open, an interference
  sweep over the animation, a scenario over the instructions, and the
  framework's two integrity contracts.
- A README section describing how to run it, what the drivers mean and what
  the model found in the design.

## Capabilities

### New Capabilities

- `arm-kinematics`: the six joint axes, where each sits, what each driver
  measures, and the reach the design's own dimension drawing states.
- `shoulder-gear-drive`: the twin geared shoulder motors and their pinions
  meshing the shoulder gear.
- `elbow-belt-drive`: the long GT2 belt from the shoulder pulley to the
  elbow pulley, and how elbow orientation is coupled to shoulder motion.
- `wrist-differential`: the two Art4 motors, their GT2 belts and pinions,
  and the crown plate that resolves them into wrist roll and tool roll.
- `gripper-linkage`: the servo, horn, active and passive arms and the two
  fingers, and the parallel motion they produce.
- `bolted-joints`: M3 screws and nuts placed on the stacks the printed
  parts' own holes and pockets define.
- `seated-hardware`: bearings, shafts, pulleys, collars, motors and magnets
  on the seats the design cut for them.
- `robot-poses`: the instructions the model offers and where each lands.

### Modified Capabilities

None. This repository has no prior OpenSpec record.

## Impact

- New: `simulation/` package, `simulation/tools/probe.py`,
  `docs/measurements.md`, an OpenSpec record under `openspec/`, and two
  sections added to `pyproject.toml` (`[tool.solid-node]` and
  `[tool.libresolid-studio]`); the repository has no `pyproject.toml` today,
  so one is created.
- Modified: `README.md` gains a simulation section; `.gitignore` gains the
  build directory and rendered images.
- Untouched: every upstream source — `freecad-src/`, `step/`, `stl/`,
  `mods/`, `doc/`, `LICENSE`.
- Dependencies: `solid-node` with its `viewer` extra, and `molejo` for the
  belts. Both are read through the workspace environment; this repository
  pins no version.
- Out of scope, and why: the control electronics' internal geometry (the
  board is a bought part, drawn as its envelope); wiring and cable routing
  (no evidence in the design for any route); the ROS2 and Asgard control
  stacks (separate repositories, and the model's drivers are joint angles,
  not their transports); print-time supports and tolerances (a printer
  property, not a design one); and the `mods/` variants (a second
  configuration of the same machine, and the pilot asked for the build the
  design ships).
