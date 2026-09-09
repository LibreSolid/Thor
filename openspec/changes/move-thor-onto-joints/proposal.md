## Why

The model was written before solid-node had a motion layer, so it carried
the layer itself: `simulation/placing.py` inverted rest placements by hand
to turn the forearm about an axis 81.5 mm from its own origin, five levels
of sub-assembly each declared six ports whose only job was to hand a value
to the level below, and every one of them applied its motion in a
`simulate()` method that had to know which way each part was placed.

solid-node now states those things itself: a `Revolute` joint declared on
the body that moves, in the frame its parent places it in; a relation from
a root driver to a coordinate anywhere below it by path; a derived
coordinate for a linear formula over coordinates; and `ratio=` for gearing.

## What Changes

- Every freedom of the machine becomes a joint on the body that has it:
  `Art1.yaw` (base), `Art2.shoulder`, `Art3.elbow`, `Art4.yaw`,
  `Art56.wrist`, `WristOutput.tool`. The gripper's opening stays a port.
- The twenty forwarded `RotationalPort`/`TranslationalPort` declarations
  are deleted. The root's seven drivers reach their joints by path.
- `Art1.elbow_absolute = art2.shoulder + art2.art3.elbow` states the
  elbow's absolute angle once; the root drives it and the solver works
  backwards to the elbow joint. `Art4.left`/`Art4.right` state the wrist
  differential's two pinion turns the same way.
- Motors, and both toothed belts, are driven by relations with a `ratio`:
  the gear ratio, or the pulley's pitch arc per degree.
- `placing.rotate_about` is no longer used by the arm; it and
  `into_local`/`turn_about` remain only for the gripper's parallelogram.
- The root's `Driver` declarations, `instructions`, every design placement,
  every fastener, every belt and every test contract are unchanged.

## What does not change

Every leaf's composed world matrix, at every instruction pose and at an
intermediate pose, is bit-identical to the model before the change (441
leaves × 7 poses, maximum deviation 0).

## Known gap

A joint's axis and anchor are resolved in the node's constructor, before
its parent's `render()` places it, so a part placed by
`placing.place_from_design` cannot declare a joint anchored at its own
placed origin. The thirteen printed gears, pulleys, optical discs and the
ball cage that spin on their own bearings therefore keep a hand-written
`rotate` in their parent's `simulate()`, with the sign read off the
placement by `placing.axis_sign`. Filed against the framework.
