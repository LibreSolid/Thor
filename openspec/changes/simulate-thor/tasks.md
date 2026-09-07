Ground-up order: the manifest first so the pilot can watch, then the machine
from the mounting face upward. Every group is "contracts red" then "parts,
contracts green", on `solid test --faceted`. The exact run happens once, in
group 13.

## 1. Project skeleton and the model the pilot can watch

- [ ] 1.1 Add `pyproject.toml` with `[tool.solid-node] model =
      "simulation.thor:Thor"` and `[tool.libresolid-studio] profile =
      "builder"`; add `_build/`, `*.png` and `.env` to `.gitignore`.
- [ ] 1.2 Create `simulation/__init__.py` (empty), `simulation/materials.py`
      (one colour per material and per printed-part family) and
      `simulation/layout.py` with `SEAT_GAP = 0.05` and the six
      sub-assembly placements.
- [ ] 1.3 Move the FreeCAD/STEP measurement probe into
      `simulation/tools/probe.py`: read `.FCStd` documents without FreeCAD,
      resolve link placements, read `.brp` shapes, find cylindrical holes,
      hex pockets, gear tooth counts and mesh windows. It is a tool, not a
      node, and nothing in the model imports it at build time.
- [ ] 1.4 Write `docs/measurements.md` with what the probe read: bought-part
      frames, hole and pocket signatures, gear counts and radii, mesh
      windows, and the home-pose overlap inventory.
- [ ] 1.5 `simulation/parts.py`: one `StepNode` per printed part, reading
      `step/<Name>.step`, with the part's material colour. Contract: every
      class builds and is one connected body.
- [ ] 1.6 `simulation/thor.py` with a `Thor` root that renders the base
      alone, so `solid build` publishes something from the first commit.

## 2. Layout fidelity

- [ ] 2.1 Red: `simulation/test_layout.py` re-reads every
      `freecad-src/Assembly*.FCStd`, resolves each link's placement, and
      compares it against `layout.py` — translations to 0.001 mm, rotations
      to 0.001°, and the instance sets equal in both directions.
- [ ] 2.2 Transcribe all six sub-assemblies' instance placements into
      `layout.py` until the drift test is green.
- [ ] 2.3 Mutation check: change one translation in `layout.py` by 0.01 mm;
      confirm the drift test fails naming that instance; revert.

## 3. The base

- [ ] 3.1 Red: `simulation/test_base.py` — `BaseBot` on the floor, the
      16014ZZ slewing bearing seated in `BaseBearingFix` at the seat gap,
      `BaseTop` and `BaseBoxCover` on their faces, the base stepper's
      flange on `BaseBot` with its shaft through the bore, `Art1GearMotor`
      on that shaft, the two fans and the board inside the box.
- [ ] 3.2 `simulation/hardware.py`: `Nema17x40`, `Bearing` (parameterised by
      bore, outer diameter, width, flange), `Fan`, `ArduinoMega`,
      `OnOffButton`, `ResetButton`, `JackDC`, `OpticSensor`, `Washer` — each
      in the frame `docs/measurements.md` records.
- [ ] 3.3 `simulation/base.py`: the `Base` assembly, parts placed from
      `layout.py`, ports for nothing (it does not move).
- [ ] 3.4 Green, then mutation check: flip the slewing bearing's axial
      placement by 2 mm and confirm the seat contract fails.

## 4. Art1 — the base yaw

- [ ] 4.1 Red: `simulation/test_art1.py` — `Art1Bot`'s internal ring
      concentric with the slewing bearing, the base pinion meshed into it
      (blocked past its measured backlash, free within it), the three geared
      motors on their faces, the three optical discs on their shafts,
      `Art1Top`, `Art1Body` and the two fan holders on their seats.
- [ ] 4.2 Measure the base pinion's clear window against `Art1Bot`'s ring
      with the probe; record it in `layout.py` and `docs/measurements.md`.
- [ ] 4.3 `hardware.py`: `Nema17GearBox`, `PulleyGT2` (parameterised by
      teeth), `Shaft` (diameter, length).
- [ ] 4.4 `simulation/art1.py`: the `Art1` assembly with an `art1` rotational
      port and a `pinion` port; `render()` places, `simulate()` turns the
      pinion at the ring ratio.
- [ ] 4.5 Wire `Art1` into `Thor` under an `art1` driver; green; mutation
      check: drop the ring ratio from the pinion's angle and confirm the
      mesh contract fails mid-sweep.

## 5. Art2 — the shoulder

- [ ] 5.1 Red: `simulation/test_art2.py` — the fork's two plates 136 mm
      apart, the four `CommonBearingFix` and their 625ZZ bearings on the
      shoulder and elbow axes, the 5×128 shaft through the elbow, the two
      belt tensioners with their MF84ZZ bearings and 4×14 shafts, the twelve
      magnets in their pockets, the two optical sensors on their brackets.
- [ ] 5.2 Measure both shoulder pinions' clear windows against `Art2BodyA`'s
      ring at 1° resolution; record centres and widths.
- [ ] 5.3 `simulation/art2.py`: the `Art2` assembly with `art2` and `art3`
      ports; the shoulder pinions live in `Art1` and are fed from here.
- [ ] 5.4 Red then green: both pinions in mesh at rest and through the
      shoulder's whole travel at one tooth pitch per step.
- [ ] 5.5 Mutation check: give both pinions the same phase and confirm the
      right-hand pinion's mesh contract fails.

## 6. Art3 — the elbow, and the belt that drives it

- [ ] 6.1 Red: `simulation/test_art3.py` — `Art3Body` on the elbow axis, the
      elbow pulley and optical disc on their bearings, the forearm motor on
      `Art4MotorFix`, `Art4BearingRing` and its balls on the slewing seat.
- [ ] 6.2 Measure `Art3Pulley`'s tooth count and pitch radius, and the
      shoulder pulley's, from their own geometry; record both. If the count
      is not a GT2-consistent integer, record it as a finding.
- [ ] 6.3 `simulation/flexibles.py`: `ElbowBelt`, a `MolejoNode` whose path
      is the two pitch circles and their outer common tangents, with ports
      for both pulley angles.
- [ ] 6.4 Red then green: the belt is tangent to both pulleys at rest, wraps
      the arc the geometry implies within 0.5°, and keeps its length within
      0.5 mm through a sweep of `art2` and `art3`.
- [ ] 6.5 Red then green: `art3` is the forearm's absolute angle — moving
      `art2` alone leaves the forearm's machine-frame direction unchanged.
- [ ] 6.6 `simulation/art3.py`; wire into `Thor` under `art2` and `art3`;
      mutation check: make `art3` relative instead of absolute and confirm
      the absolute-angle contract fails.

## 7. Art4 — the forearm yaw

- [ ] 7.1 Red: `simulation/test_art4.py` — the transmission column's
      twenty-tooth gear meshed with the forearm pinion at 27.85 mm centres,
      the column on the slewing ring, `Art4BodyBot` and `Art4Body` on the
      column, the two wrist motors on their holders, the two wrist bearings
      on the 5×102 shaft, the endstop and the M8 connector on their faces.
- [ ] 7.2 Measure the forearm pinion's clear window against the column gear;
      record it.
- [ ] 7.3 `simulation/art4.py` with `art4`, `art5`, `art6` ports; the column
      gear turns at the two-to-one ratio the tooth counts give.
- [ ] 7.4 Green; mutation check: shift the column 1 mm off axis and confirm
      the mesh contract fails.

## 8. The wrist differential

- [ ] 8.1 Red: `simulation/test_art56.py` — both bevel pinions meshed into
      the crown plate (blocked past backlash, free within it), the crown on
      its 625ZZ, the two collars and two GT2×40 pulleys on the wrist shaft.
- [ ] 8.2 Measure each bevel's clear window against the crown; measure the
      bevel and crown tooth counts; record the ratio.
- [ ] 8.3 `flexibles.py`: the two 208 mm forearm belts, 98 mm centres, ports
      for their pulley angles.
- [ ] 8.4 `simulation/art56.py`: the `Art56` assembly resolving `art5` and
      `art6` into the two bevel angles and back out to the two forearm
      motors and their belts.
- [ ] 8.5 Red then green: equal input rolls the wrist and not the tool;
      opposite input rolls the tool and not the wrist; both motors turn for
      either.
- [ ] 8.6 Mutation check: swap the sign of one bevel's contribution and
      confirm the wrist-only and tool-only contracts fail.

## 9. The gripper

- [ ] 9.1 Red: `simulation/test_gripper.py` — fingers symmetric about the
      centre plane at every opening, `grip` equal to the measured clear
      opening, the servo body fixed to the base, the horn turning with the
      active arm, closed means within 0.1 mm of touching and not
      overlapping.
- [ ] 9.2 Solve the four-bar from the design's own pivot positions; record
      the solved link lengths and the opening range in
      `docs/measurements.md`.
- [ ] 9.3 `hardware.py`: `Servomotor`, `ServoHorn`. `parts.py`: the mirrored
      `GripperFingerMirrored`, an `StepNode` subclass whose `adjust()`
      mirrors the exported finger, with the mirror stated in its docstring
      and recorded as a finding.
- [ ] 9.4 `simulation/gripper.py` with a `grip` port; green.
- [ ] 9.5 Mutation check: drive one finger and not the other; confirm the
      symmetry contract fails.

## 10. Fasteners

- [ ] 10.1 Extend `simulation/tools/probe.py` to emit the fastener table:
      cluster hole faces into axes, split each axis into contiguous stacks
      at a 1 mm gap, detect hex pockets and head counterbores, choose the
      shortest standard M3 length that spans each stack, and report any
      stack it cannot classify.
- [ ] 10.2 Run it, read every unclassified stack by hand, and write the
      result and the leftovers into `docs/measurements.md`.
- [ ] 10.3 Transcribe the table into `simulation/fasteners.py` as data, with
      a test that re-runs the probe and compares the table entry for entry.
- [ ] 10.4 `hardware.py`: `SocketHeadScrewM3` (length parameterised, real
      thread only where something hangs on it — nowhere here, so a plain
      shank), `HexNutM3`, `WasherM3`.
- [ ] 10.5 Red then green: every screw's shank inside its stack's clearance
      holes and sharing volume with none of them; every screw spanning its
      stack; every head bearing on its counterbore or outer face at the seat
      gap; every nut inside its pocket, blocked past two degrees, engaged on
      its screw with 0.5 mm to one nut thickness of protrusion; no nut on an
      axis without a pocket.
- [ ] 10.6 Compare the derived totals per length against the published Bill
      of Materials and record both columns in `docs/measurements.md`.
- [ ] 10.7 Mutation check: shorten one screw by one standard step and
      confirm the span contract fails; move one nut out of its pocket and
      confirm the seat contract fails.

## 11. The root: drivers, instructions, integrity

- [ ] 11.1 `simulation/thor.py`: seven drivers (`art1`…`art6`, `grip`) with
      the ranges and units the design's own travel gives them; bind every
      sub-assembly port, the moving ones and the ones held at zero alike.
- [ ] 11.2 Instructions `Home`, `Ready`, `Reach`, `Pick`, `Place`, `Park`,
      each with a duration no shorter than its largest joint travel divided
      by that joint's rated rate.
- [ ] 11.3 `simulation/seats.py`: the measured overlap inventory, and the
      root contract that the set of overlapping printed-solid pairs is
      exactly that set, each within ten per cent of its recorded volume.
- [ ] 11.4 `simulation/test_thor.py`: `test_solid_integrity`
      (`assertNoDisconnectedSolids`), `test_assembly_integrity` (the seats
      inventory, swept over the animation), the reach contracts, and the
      per-joint rigid-link contract.
- [ ] 11.5 A `ScenarioTest` that triggers every instruction in turn and
      checks the inventory on a cadence no coarser than a tenth of each
      ramp, plus one run that must fail (a pose routed straight through a
      collision) to prove the scenario can see one.
- [ ] 11.6 Mutation check per sub-assembly, recorded here: which contract
      catches a wrong pulley height, a flipped bevel sign, a tilted idler, a
      pinion phase, a mis-sized screw.

## 12. Build, look, and write it down

- [ ] 12.1 `solid build`; read `_build/viewer.json`: walk `root` to each
      sub-assembly, confirm the operations carry the qualified driver ids,
      every rigid leaf's `model` file exists, and the `drivers` table lists
      all seven.
- [ ] 12.2 `solid snapshot` at rest and at one posed instant, isometric and
      along each joint axis; look at every image before calling it done.
- [ ] 12.3 README section: how to run it, what each driver means in the
      builder's terms, the instructions, the ground-up sequence of models to
      look at, and what the model found in the design.
- [ ] 12.4 Fold every finding into `design.md`'s Findings, the README's
      bullets, and the docstring of the node that lives with it.

## 13. Certify and close

- [ ] 13.1 Full regression on the faceted kernel: `solid test --faceted` for
      every node file including the root.
- [ ] 13.2 The exact run, once: `solid test --exact` for every node file
      including the root. Record the wall clock. Where the two kernels
      disagree, fix the model or the contract and never reach for an epsilon.
- [ ] 13.3 Report any framework friction to the shop's `docs/warts.md` under
      a Thor heading, with the workaround and the file that carries it; offer
      `file-a-wart` and do not file it.
- [ ] 13.4 Commit the implementation, fill `Purpose` in every spec, sync the
      specs and archive the change.
