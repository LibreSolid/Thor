## Why

ADR-097 (`joint-frame-follows-declarer`, solid-node main 91c0b2a) changes
which frame a class-body joint's `axis`/`at`/`carries` are read in: the
declaring body's OWN rest frame, not the parent's. Thor is the ADR's
originating sighting -- its thirteen hand-turned catalogue parts and its
`Art2.shoulder`/`Art3.elbow`/`Art4.yaw`/`Art56.wrist` axes under rotation
are the concrete evidence the design cites -- and the previous migration
(`move-thor-onto-joints`) was written against the superseded parent-frame
rule, so five of Thor's six declared joints now read wrong wherever their
parent rotates or translates them, and the thirteen hand-turned parts are
newly declarable at all. Until this is fixed the project is broken on
solid-node main.

## What Changes

- `Art1.yaw`: `at=YAW_ANCHOR` deleted (RESTATES -- the root places `Art1`
  with no rotation, so the anchor was always this body's own origin).
  `YAW_ANCHOR` itself is deleted, now unread anywhere.
- `Art2.shoulder`: `at=ARM_ORIGIN` deleted (RESTATES). Axis rewritten
  `(0, 1, 0)` -> `(0, 0, 1)`: `Art1.render()` turns this body 180 degrees
  about `(0, 1/sqrt2, 1/sqrt2)` before placing it, and a 180-degree turn
  is its own inverse, so the housing's shoulder axis maps onto this
  frame's own Z exactly. `SHOULDER_AXIS`, `ARM_ORIGIN`, `ARM_TURN`,
  `ARM_TURN_AXIS` (art2.py's own copies, never read elsewhere) are
  deleted as dead.
- `Art3.elbow`: `at=(0, ELBOW_ALONG_ARM, ELBOW_ACROSS_ARM)` (a genuine
  `PARENT-FRAME-OFFSET`, not a restatement) rewritten to
  `at=(0, 0, ELBOW_ACROSS_FOREARM)`, axis `(0, 0, 1)` -> `(0, 1, 0)`:
  `Art2.render()` turns this body 90 degrees about `(1, 0, 0)` before
  translating it by `(0, 241.5, 68)`, and carrying the old anchor and
  axis back through that turn gives exactly these numbers -- the same
  `ELBOW_ACROSS_FOREARM = 81.5` the project already names.
- `Art4.yaw`: `at=FOREARM_ORIGIN` deleted (RESTATES). Axis rewritten
  `YAW_AXIS_IN_LINK (0, 0, -1)` -> `(0, 0, 1)`: `Art3.render()` turns
  this body 180 degrees about `(0, 1, 0)` before placing it, its own
  inverse, so Art3's yaw axis maps onto this frame's own Z.
  `YAW_AXIS_IN_LINK` stays (still read by `art3.py`'s own `_sign`, a
  different frame's use of the same physical line); `FOREARM_ORIGIN`
  stays (still used by `Art3.render()`'s placement).
- `Art56.wrist`: `at=(0, 0, WRIST_HEIGHT)` deleted (RESTATES). Axis
  rewritten `WRIST_AXIS_IN_FOREARM (0, 1, 0)` -> `WRIST_AXIS (1, 0, 0)`
  (this module's own constant): `Art4.render()` turns this body 90
  degrees about `(0, 0, 1)` before placing it, carrying the forearm's
  wrist axis back through that turn onto this frame's own X.
  `WRIST_HEIGHT` stays (still used by `Art4.render()`'s placement).
- `WristOutput.tool`: unchanged (`OWN-ORIGIN-ALREADY` -- the parent
  applies no placement to this body at all).
- **The thirteen hand-turned catalogue parts become declared joints.**
  Every one turns about its own placed origin on its own local Z,
  confirmed from the design's own `placing.axis_sign` calls, so each
  becomes `turn = Revolute(axis=(0.0, 0.0, 1.0), unit='deg')` on the
  class: `parts.Art1GearMotor`, `parts.Art2MotorGear` (two instances),
  `hardware.PulleyGT2` (five instances across three assemblies),
  `parts.Art23Optodisk`, `parts.Art4MotorGear`, `hardware.BearingBalls`
  (an `AssemblyNode`, whose joint rotates the whole 36-ball array as one
  rigid body on top of its own static layout), `parts.Art56SmallGear`
  (two instances). Each hand `part.rotate(sign * angle, [0, 0, 1])` in a
  `simulate()` method is replaced by a class-level `.drives(part.turn,
  ratio=sign * gear_ratio)` relation from the coordinate that already
  drove it (a joint, a derived coordinate, or a root port), with the
  sign read once, at class-definition time, from the same
  `placing.axis_sign` call the hand-written code already made --
  unaffected by the frame rule, a property of the design's static
  mounting.
- **Five `simulate()` methods -- `Base.simulate`, `Art1.simulate`,
  `Art3.simulate`, `Art4.simulate`, `Art56.simulate` -- are deleted
  entirely.** Each contained only the hand-turned rotations above; with
  every one now a relation, nothing is left. `Gripper.simulate` is
  unchanged (its jaws are the couplers of a parallelogram, not a lower
  pair -- out of scope for this ADR).
- `SHOULDER_DRIVE` (art1.py) and `MOTOR_DRIVES` (art4.py), module-level
  lookups whose only reader was the deleted `simulate()` loop, are
  deleted as dead.

## What does not change

Every leaf's composed world matrix, at every pose `capture_poses.py`
samples (19 poses: defaults, each of the seven drivers at 40%/100% of its
range, all seven together at 63%, and three time fractions), is
bit-identical to the model before this change -- maximum deviation
0.000e+00, reusing the campaign's own BEFORE capture
(`before2/Thor-Thor-before.json`) taken from the unmodified source on the
pre-ADR-097 framework. Root drivers, instructions, every design
placement, every fastener, every belt, the gripper's own kinematics and
every test contract are unchanged.

## Known gaps

None found. All six declared joints and all thirteen hand-turned parts
are stated as literals in their own frame with no callable needed: every
placement Thor applies to a joint-bearing body is either a pure
translation (RESTATES/OWN-ORIGIN-ALREADY) or a rotation whose axis
carries to a clean own-frame literal (the four `PARENT-FRAME-OFFSET`/
axis-under-rotation cases), and every hand-turned part spins about a line
through its own placed origin on its own local Z regardless of mounting,
so none of the five `PARENT-KNOWLEDGE-IN-SUBSTANCE` or
axis-unstateable-as-a-literal shapes ADR-097 names occurs here. This
matches the framework's own read-only survey of the project
(`solid-node/openspec/changes/archive/2026-09-10-joint-frame-follows-declarer/evidence/survey.md`,
rows tagged `Robotic-Arms/Thor`).

## Pre-existing state

The repository was clean at `4e6f134` when this change started; nothing
was stashed or committed before the refactor's own commit.

## Tests

`solid test --exact simulation/thor.py` is the project's declared suite
(the faceted kernel cannot build seven of Thor's parts; see README). Its
baseline result and this change's result are both recorded in
`tasks.md`; no test is edited by this change -- if the suite's failing
set changes shape (not just count) from the true pre-edit baseline, that
is investigated before commit, not worked around.
