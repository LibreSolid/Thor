Behaviour-preserving throughout: the acceptance is that every leaf's world
matrix is unchanged at every pose, so evidence is captured before the first
edit and compared after the last. `git rev-parse --show-toplevel` confirmed
this project's own repository before every write and commit.

## 1. Evidence (before)

- [x] 1.1 BEFORE poses reused from the framework's own cycle-2 capture
      against the unmodified source on the pre-ADR-097 framework:
      `Thor-Thor-before.json`, 19 poses (defaults; each of art1..art6 and
      grip at 40%/100% of range; all seven at 63%; time at 0.25/0.5/0.75),
      441 leaves.
- [x] 1.2 True baseline suite, `solid test --exact simulation/thor.py`, on
      the unmodified source (commit 4e6f134) against solid-node main
      91c0b2a (ADR-097 integrated, `Joint._carry` already deleted):
      **33 tests, 27 passed, 6 failed.** Four of the six are the frame
      breakage this change fixes -- `Art2.shoulder`/`Art3.elbow`/
      `Art4.yaw`/`Art56.wrist` reading their old parent-frame `at`/`axis`
      as if it were already own-frame, doubling or misdirecting the
      offset: `test_swinging_the_shoulder_swings_the_forearm_with_the_arm`,
      `test_the_pinions_stay_in_mesh_through_the_shoulder_s_travel`,
      `test_turning_the_elbow_turns_only_the_forearm`,
      `test_turning_the_elbow_turns_the_forearm`. The other two are
      unrelated and pre-date this cycle: `test_assembly_integrity` and
      `test_the_demo_never_drives_a_part_through_another`, both failing
      the same `seats.assert_inventory` check the project's own history
      already records as red (`move-thor-onto-joints/tasks.md` 3.2: "the
      same two `seats.assert_inventory` failures the unmodified model
      produces"). This baseline was captured cleanly: the working tree
      was stashed back to `4e6f134` for the run and the stage-B edits
      re-applied afterward, after an earlier attempt run concurrently
      with drafting the edits was discarded as contaminated (see the
      framework's own evidence.md 0.4 for the same caution).

## 2. Joints

- [x] 2.1 Rewrite the five affected joints' `axis`/`at` into their own
      declaring body's rest frame:
      - `Art1.yaw` (`art1.py`): `at=YAW_ANCHOR` deleted (RESTATES).
        `YAW_ANCHOR` deleted, now unread anywhere.
      - `Art2.shoulder` (`art2.py`): `at=ARM_ORIGIN` deleted (RESTATES).
        `axis=SHOULDER_AXIS` (0, 1, 0) rewritten to the literal
        `(0.0, 0.0, 1.0)`: `Art1.render()` turns this body 180 degrees
        about `(0, 1/sqrt2, 1/sqrt2)` before placing it, its own inverse,
        carrying the housing's shoulder axis onto this frame's own Z.
        Art2's own dead copies of `SHOULDER_AXIS`, `ARM_ORIGIN`,
        `ARM_TURN`, `ARM_TURN_AXIS` deleted (never read elsewhere; Art1
        keeps its own, still needed by `render()` and `_sign()`).
      - `Art3.elbow` (`art3.py`): a genuine `PARENT-FRAME-OFFSET`, not a
        restatement. `at=(0, ELBOW_ALONG_ARM, ELBOW_ACROSS_ARM)`
        rewritten to `at=(0.0, 0.0, ELBOW_ACROSS_FOREARM)`, axis
        `(0, 0, 1)` rewritten to `(0.0, 1.0, 0.0)`: `Art2.render()` turns
        this body 90 degrees about `(1, 0, 0)` then translates it by
        `(0, 241.5, 68)`; carrying the old anchor and axis back through
        that turn gives exactly these numbers, matching the project's
        own `ELBOW_ACROSS_FOREARM = 81.5`.
      - `Art4.yaw` (`art4.py`): `at=FOREARM_ORIGIN` deleted (RESTATES).
        `axis=YAW_AXIS_IN_LINK` (0, 0, -1) rewritten to the literal
        `(0.0, 0.0, 1.0)`: `Art3.render()` turns this body 180 degrees
        about `(0, 1, 0)`, its own inverse. `YAW_AXIS_IN_LINK` and
        `FOREARM_ORIGIN` both stay -- still read by `art3.py`'s own
        `_sign()` and `render()` respectively.
      - `Art56.wrist` (`art56.py`): `at=(0, 0, WRIST_HEIGHT)` deleted
        (RESTATES). `axis=WRIST_AXIS_IN_FOREARM` (0, 1, 0) rewritten to
        this module's own `WRIST_AXIS` constant, `(1.0, 0.0, 0.0)`:
        `Art4.render()` turns this body 90 degrees about `(0, 0, 1)`,
        carrying the forearm's wrist axis onto this frame's own X.
        `WRIST_HEIGHT` stays -- still read by `Art4.render()`.
      - `WristOutput.tool` (`art56.py`): unchanged, `OWN-ORIGIN-ALREADY`.
- [x] 2.2 Declare `turn = Revolute(axis=(0.0, 0.0, 1.0), unit='deg')` on
      the seven classes behind Thor's thirteen hand-turned catalogue
      parts: `parts.Art1GearMotor` (1 instance), `parts.Art2MotorGear`
      (2), `hardware.PulleyGT2` (5, across `art1.elbow_drive_pulley`,
      `art4.motor_pulley_1/2`, `art56.gt2x40_pulley_1/2`),
      `parts.Art23Optodisk` (1), `parts.Art4MotorGear` (1),
      `hardware.BearingBalls` (1, an `AssemblyNode` -- the joint turns
      the whole 36-ball array as one rigid body on top of its own static
      `render()`), `parts.Art56SmallGear` (2). 1+2+5+1+1+1+2 = 13.
- [x] 2.3 Replace each hand-written `part.rotate(...)` with a class-level
      `.drives(part.turn, ratio=...)` relation from the coordinate that
      already drove it, the sign folded in at class-definition time from
      the same `placing.axis_sign(...)` call the hand-written code used
      (values independently re-verified against source: base +1.0;
      shoulder pinions -1.0/-1.0; elbow_drive_pulley +1.0; optodisk
      +1.0; art4_motor_gear +1.0; bearing_balls +1.0; motor_pulley_1/2
      +1.0/-1.0; small_gear_1/2 +1.0/-1.0; gt2x40_pulley_1/2 -1.0/+1.0).
      `Base.simulate`, `Art1.simulate`, `Art3.simulate`, `Art4.simulate`
      and `Art56.simulate` deleted entirely -- each held only these hand
      rotations, so nothing is left. `Gripper.simulate` (the
      parallelogram jaw linkage) is untouched: out of scope for this
      ADR. The now-dead `SHOULDER_DRIVE` (art1.py) and `MOTOR_DRIVES`
      (art4.py) lookups, whose only reader was the deleted loop, are
      deleted. README's "What still turns by hand" section updated to
      say so.

## 3. Evidence (after)

- [x] 3.1 Sanity check before the heavy suite: constructed `Thor()`,
      posed it (`art1=0, art2=30, art3=-40`, rest at default), and read
      all thirteen `.turn.value`s directly -- e.g. `shoulder_pinion_1`
      and `shoulder_pinion_2` both `-180.0` (30 x SHOULDER_RATIO(6) x
      -1), `elbow_drive_pulley`/`art23_optodisk` both `-204.0`
      (`drive = 30 + (117/20)*(-40) = -204`, sign +1) -- matching hand
      arithmetic before running the slow suite.
- [x] 3.2 Re-captured AFTER poses on the edited source (same 19 poses,
      441 leaves) and compared against the reused BEFORE:
      **max deviation 0.000e+00 over 19 poses.**
- [x] 3.3 Fast plain-pytest tests unaffected by the joint change,
      `simulation/test_layout.py simulation/test_fasteners.py`: 9/9
      passed, same as baseline.
- [x] 3.4 Re-ran `solid test --exact simulation/thor.py`: **33 tests, 31
      passed, 2 failed.** The four frame-breakage failures from 1.2 are
      now green; the same two pre-existing `seats.assert_inventory`
      failures (`test_assembly_integrity`,
      `test_the_demo_never_drives_a_part_through_another`) remain red,
      unchanged in name and cause -- no test newly red, no test edited.
- [x] 3.5 Commit in this repository only, naming ADR-097 and this
      evidence.
