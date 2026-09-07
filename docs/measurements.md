# What the model measured

Every number the simulation layer stands on was read out of this
repository's own files. Nothing here is a catalogue value taken on trust,
a dimension scaled off a drawing, or a figure chosen to make something fit.
The tools that read them live in `simulation/tools/` and can be re-run:

    python -m simulation.tools.emit_layout      # the placement tables
    python -m simulation.tools.emit_fasteners   # the fastener table

`simulation/test_layout.py` and `simulation/test_fasteners.py` re-run those
readings and fail if the transcription and the design have drifted apart.

## Where the numbers come from

| file | what it is the source of |
| --- | --- |
| `freecad-src/Assembly*.FCStd` | every part's placement. FreeCAD's Assembly4 solves the assembly and stores each link's resulting global placement in the document, so these are the design's own answer, not a reconstruction. |
| `step/*.step` | every printed part's geometry, exact. One product per file, named after the file. |
| `doc/ThorDimensions.png` | the author's own axis measures: 202.00, 160.00, 195.00, 67.15 mm. |
| `stl/*.stl` | used only for cheap measurement — tooth counts, radii — never for the model, which reads the STEP. |

## The joint axes

Measured from the assembly's own solved placements, in the machine frame
(Z up, origin on `BaseBot`'s mounting face).

| joint | axis | through | span from the one below |
| --- | --- | --- | --- |
| `art1` base yaw | +Z | (0, 0) | — |
| `art2` shoulder roll | +Y | z = 202.0 | 202.0 |
| `art3` elbow roll | +Y | z = 362.0 | 160.0 |
| `art4` forearm yaw | forearm axis | — | — |
| `art5` wrist roll | +Y | z = 556.0 | 194.0 |
| `art6` tool roll | wrist output | — | — |

The elbow axis is `Art3Pulley`'s own axis carried through the Art3 link:
443.5 − 81.5 = 362.0. The wrist axis is the Art56 link's own origin.

**Against the author's drawing.** 202.0 and 160.0 agree exactly. The
drawing's 195.00 mm from elbow to wrist is 194.0 in the assembly — one
millimetre short.

## The sub-assemblies, each inside its parent

| link | inside | translate | rotate |
| --- | --- | --- | --- |
| `AssemblyBase` | the machine | (0, 0, 0) | — |
| `AssemblyArt1` | the machine | (0, 0, 79.0) | — |
| `AssemblyArt2` | Art1 | (0, −68.0, 123.0) | 180° about (0, .7071, .7071) |
| `AssemblyArt3` | Art2 | (0, 241.5, 68.0) | 90° about X |
| `AssemblyArt4` | Art3 | (0, 0, −1.0) | 180° about Y |
| `AssemblyArt56` | Art4 | (0, 0, 111.5) | 90° about Z |

## The bought components' own frames

Read off the `App::Part` groups the FreeCAD documents carry for each
component, so a placement transcribed from the assembly lands a Python
drawing of the same component without any correction.

| component | frame | size |
| --- | --- | --- |
| `Stepper_Nema17x34` | back face at z=0, shaft along +Z | 42.30 square, corners cut to a 53.84 diagonal; body to 34.0, Ø22 boss 2.0, Ø5 shaft to 54.0 |
| `Stepper_Nema17x40` | as above | body to 40.0, shaft to 60.1 |
| `Nema17_GearBox` | as above | body 33.0, plate 7.0 at 41.5 square, Ø36 barrel 20.3, Ø6 shaft to 78.3 |
| `Bearing_625ZZ` | bore centred, one face at z=0 | Ø16 × 5.0, bore Ø5 |
| `Bearing_MF84ZZ` | as above, flange at z=0 | Ø9.2 flange, Ø8 × 3.0, bore Ø4 |
| `Bearing_16014zz` | as above | Ø110 × 13.0, bore Ø70 |
| `Pulley_GT2x20` | one flange face at z=0 | Ø18 flange, tips at r 6.07, land 1.0–10.0, hub to 14.6 |
| `GT2x40PulleyM4` | as above | Ø28 flange, tips at r 12.49, land 1.0–8.5, hub to 17.0 |
| `Collar5mm` | centred on z=0 | Ø10 × 5.0, bore Ø5, clamp boss to y 5.87 |
| `Magnet` | one face at z=0 | Ø8 × 1.0 |
| `Fan_40x40` / `Fan_50x50` | centred, one face at z=0 | 40 × 40 × 10 / 50 × 50 × 11 |
| `ServomotorWheelHorn` | hub face at z=0 | Ø21 disc 2.3, Ø8.86 hub to 5.5 |
| `Servomotor` | the **horn's** axis, not the body's | body y −21.0 to −61.6, tabs to −68.6, envelope 19.8 × 54.6 × 44.5 |
| `OpticSensor` | board face at z=0 | 35.0 × 11.0 × 2.2 board, 20.5 × 10.2 fork 9.3 tall |
| `MicroEndstop` | body's near bottom corner | 12.6 × 5.8 × 9.4 plus lever |
| `ArduinoMega` | 58.07 from the near end | 108.8 × 53.2, −1.63 to 13.18 |
| `OnOffButton` | bezel face at z=0 | Ø17.8 bezel, body to −36.0 |
| `ResetButton` | bezel at y=+2.0, body along −Y | Ø18.9 bezel, body to −38.6 |
| `JackDC`, `NutButton`, `M8Connector` | as the design draws them | (−5.5, −22.0, −6.35)–(5.5, −3.8, 6.35); Ø21.94 × 3.0 across 19.0 flats; 21.0 long, Ø11.52 flatted to 10.0 |
| `BearingBalls` | the forearm's yaw axis | 36 balls of Ø6 on a 35.0 pitch radius |
| shafts `4×14`, `5×14.5`, `5×32`, `5×102`, `5×128` | one end at z=0 | Ø4 or Ø5 by their names |

## The gear trains

Tooth counts and radii read from each part's own geometry.

| pair | teeth | tip radius | measured centres | nominal |
| --- | --- | --- | --- | --- |
| base pinion in `Art1Bot`'s ring | 10 in 50 | 12.00 / 47.45 in | 40.0 | 39.5 |
| shoulder pinions in `Art2BodyA`'s ring | 10 in 60 | 12.00 / 47.66 in | 48.34 | ≈49.5 |
| forearm pinion on the column's gear | 10 on 20 | 10.80 / 19.80 | 27.85 | 27.0 |
| wrist bevels on the crown | 15 on 30 | — | on the wrist axis | — |
| elbow belt pulleys | 20 and 117 | 6.11 / 37.00 | 160.0 | — |
| wrist belt pulleys | 20 and 40 | 6.11 / 12.49 | 81.51 | — |

`Art2BodyA`'s internal ring was fitted to its own section: root circle
r 61.825, tip circle r 57.659, both centred within 0.003 of the part's
origin. `Art3Pulley`'s 117 teeth follow from its 37.000 tip radius through
GT2's own geometry (`teeth = π × (tip + 0.254)` gives 117.04); a Fourier
count on the same section reads 126 and is wrong, because the section
samples only a sixth of the circle.

### Where each gear goes on its shaft

The design's assembly leaves every gear pair interpenetrating: it never put
a pinion on at an angle that meshes. Each phase below is the centre of the
window in which the pair shares least, swept one degree at a time through a
full tooth pitch on the exact kernel.

| pair | phase | window | least shared |
| --- | --- | --- | --- |
| base pinion | 23.40° | 0.05° | 0.1965 mm³ |
| shoulder pinion, −x | 31.5° | 5.0° | 0 |
| shoulder pinion, +x | 19.5° | 5.0° | 0 |
| forearm pinion | 31.0° | 4.0° | 24.2991 mm³ |
| wrist bevel, −x | 0.4° | 0.4° | 0 |
| wrist bevel, +x | 23.4° | 0.4° | 0 |

Two of the six never reach zero, and what fouls is not a tooth:

- the **base pinion** stands 2 mm taller than the ring gear it drives, and
  its top rim cuts the rim above the teeth by 0.20 mm³ at every phase;
- the **forearm pinion**'s lower flange, which is 1.2 mm larger in radius
  than its teeth, fouls the unrelieved ring at the foot of the column's
  gear by 24.30 mm³ at every phase.

Both are recorded in `simulation/seats.py` and neither is fixed upstream.

## The gripper linkage

Read from the parts' own pivot bores, in the machine frame at rest.

| pin | right (+y) | left (−y) |
| --- | --- | --- |
| arm pivot in the body | 14.52, 645.00 | −14.50, 645.00 |
| arm pin in the jaw | 49.51, 645.17 | −49.50, 645.15 |
| link pivot in the body | 6.00, 663.50 | −6.00, 663.50 |
| link pin in the jaw | 41.00, 663.50 | −41.00, 663.50 |

Both cranks are 35.00 mm between pins and the arm-to-link offset is the
same on the body (−8.52, +18.50) as on the jaw (−8.51, +18.33): a
parallelogram to within the 0.17 mm the design's own pin positions carry.
The jaw is therefore in pure circular translation, and its gripping face is
a flat plane 34.97 from the centre over its whole height — a 69.94 mm clear
opening, closing to zero at an 89.7° crank swing.

## The belts

| belt | pulleys | taut loop | teeth | the design's own part |
| --- | --- | --- | --- | --- |
| elbow | 20T at the shoulder axis, 117T at the elbow, two Ø12 idlers at (±14.5, 99.85) | 397.64 mm | 199 | `GT2_Belt_Art3`, placed clear of both pulleys |
| wrist ×2 | 20T at (±24, ·, 33.6), 40T on the fork axis, 81.51 mm apart | 221.53 mm | 111 | `Belt_GT2-208mm`, placed lying flat |

Wrap angles on the elbow belt: 163.1° on the drive pulley, 52.4° on each
idler, 92.2° on the elbow pulley. On a wrist belt: 189.0° and 171.0°.

Two findings fall out of this table. The forearm belts are named for
208 mm and their pulleys need 221.5; the design's own belt solid measures
about 220 mm, so the name is what is wrong. And the elbow belt's two
pulleys do not share a plane: the drive pulley's belt land is centred
17.15 along the shoulder axis in the upper arm's frame and the elbow
pulley's 25.0, **7.85 mm apart**, which no 6 mm belt can bridge. The model
draws that belt in the drive pulley's plane and records the offset rather
than quietly splitting the difference.

## The fasteners

The design models no fastener at all. Every screw and nut in the model is
derived from the printed parts' own geometry, one link at a time in that
link's own frame, because a screw holds one rigid link together.

Signatures found across the machine:

| feature | measurement | count |
| --- | --- | --- |
| M3 clearance hole | cylindrical face, r 1.70 | 400 faces |
| M4 clearance hole | r 2.10 | 4 faces |
| socket-head counterbore | r 2.95 | 192 faces |
| M3 hex nut pocket | six planes at 2.90 from the axis — 5.80 across flats, a 5.5 nut with 0.3 mm of print clearance | — |

Clustering those onto shared axes and splitting each axis into contiguous
stacks at a 1.0 mm gap gives:

| link | stacks | fasteners fitted | with a nut | unclassified |
| --- | --- | --- | --- | --- |
| Base | 49 | 37 | 6 | 12 |
| Art1 | 65 | 64 | 45 | 1 |
| Art2 | 60 | 37 | 22 | 23 |
| Art3 | 33 | 20 | 8 | 13 |
| Art4 | 54 | 44 | 24 | 10 |
| Art56 | 26 | 14 | 6 | 12 |
| **total** | **287** | **216** | **111** | **71** |

Lengths chosen, all M3 unless noted: 89 × 6, 55 × 8, 20 × 10, 6 × 12,
26 × 16, 8 × 20, 7 × 25, 5 × 35, and 4 × M4 8.

**The 71 unclassified stacks** are a hole through one part with neither a
counterbore nor a nut pocket, and nothing in the geometry says whether they
take a screw: many will be the M3s that hold a motor to its printed holder,
where the thread is in the motor's own casting and the model has no
geometry for it, and some will be cable passes. The model fits no fastener
to them rather than guessing, and they are listed here as a group rather
than silently absorbed. Five further stacks carry neither a counterbore nor
a pocket at either end and are marked `undecided`: the model puts their
heads at the low end of the stack, which is a convention, not a reading.

## The published parts' own defects

Four of the 46 printed parts are not one positive solid as published:

| part | what the file holds | what the model does |
| --- | --- | --- |
| `Art2MotorGear` | one solid, inside out, −8435.0 mm³ | reverses it |
| `Art4BodyBot` | one solid, inside out, −113674.9 mm³ | reverses it |
| `GripperActiveArm` | two solids: a 2479.9 mm³ arm and a 45.4 mm³ Ø3.4 × 5.0 pin standing in its outer pivot hole | takes the arm, and the pin as a part of its own |
| `GripperPassiveArm` | two solids: a 3421.4 mm³ arm and the same pin | as above |

Seven printed parts tessellate to a mesh that is not closed at the default
0.1 mm deflection — `Art1Body`, `Art1Top`, `Art1GearMotor`, `Art2BodyB`,
`Art2MotorGear`, `Art3Body`, `Art4BodyBot`. Their exact geometry is sound;
only the triangulation has seams. Every contract in this project is
therefore decided on solids rather than on triangles.

`Art1OptoFix`, `Art4BearingPlug` and `Art56Interface` are drawn, exported
to `step/` and `stl/`, and placed in no assembly document.
