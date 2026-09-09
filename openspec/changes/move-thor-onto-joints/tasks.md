Behaviour-preserving throughout: the acceptance is that every leaf's world
matrix is unchanged at every pose, so evidence is captured before the first
edit and compared after the last.

## 1. Evidence

- [x] 1.1 Capture every leaf's composed world matrix, and every bound port,
      at `Home`, `Ready`, `Reach`, `Pick`, `Place`, `Park` and one
      intermediate pose, on the model as it stands.

## 2. Joints

- [x] 2.1 Declare the six freedoms as `Revolute` joints on the bodies that
      move, each stating its axis and anchor in its parent's frame; move
      the constants that describe a placement to the module of the body
      that is placed (`art2` owns the shoulder axis, `art3` the elbow,
      `art4` the forearm's yaw, `art56` the wrist).
- [x] 2.2 Delete the forwarded port declarations and the root's
      `simulate()`; state the seven drivers' relations by path.
- [x] 2.3 State `elbow_absolute` on `Art1` and `left`/`right` on `Art4` as
      derived coordinates, and drive the motors and belts from them with
      `ratio=`.
- [x] 2.4 Shrink the sub-assembly `simulate()` methods to the design-placed
      parts that spin on their own bearings; delete `Art2`'s, `Thor`'s and
      `WristOutput`'s entirely.

## 3. Evidence again

- [x] 3.1 Re-capture and compare every leaf's world matrix at every pose:
      maximum deviation 0 over 441 leaves and 7 poses.
- [x] 3.2 `solid test --exact simulation/thor.py`: 31 tests, 29 passed,
      2 failed — the same two `seats.assert_inventory` failures the
      unmodified model produces against the same framework build.
- [x] 3.3 Record how the model moves in `README.md`, including what still
      turns by hand and why.
