## ADDED Requirements

### Requirement: The model offers a small set of poses
The root SHALL declare instructions that pose the whole machine, each
landing exactly on its stated driver targets and each showing something a
maker would not see by dragging one slider.

#### Scenario: Home returns the design's own pose
- **WHEN** `Home` is triggered and its ramp completes
- **THEN** every joint driver is 0° and the machine stands in the pose the
  FreeCAD assembly records

#### Scenario: Ready folds the arm to a working stance
- **WHEN** `Ready` is triggered and its ramp completes
- **THEN** every driver is exactly on its target and the tool points
  forward and down

#### Scenario: Reach extends the arm without moving the base
- **WHEN** `Reach` is triggered from `Ready`
- **THEN** `art1` is unchanged and the tool centre has moved outward in the
  arm's own plane

#### Scenario: Pick closes the gripper on the target opening
- **WHEN** `Pick` is triggered
- **THEN** the arm arrives at its pose and `grip` lands on its target
  opening

#### Scenario: Place returns the load and opens the gripper
- **WHEN** `Place` is triggered from `Pick`
- **THEN** the base has yawed to the place station and `grip` is at its
  open target

#### Scenario: Park folds the arm to a stable resting stance
- **WHEN** `Park` is triggered
- **THEN** every driver is exactly on its target and the machine's centre
  of mass is over the base

### Requirement: The machine does not collide while it moves
Running the instructions SHALL not bring any two parts into a shared volume
beyond the inventory's own.

#### Scenario: The demo runs clean
- **WHEN** every instruction is triggered in turn and the machine is
  sampled at intervals no coarser than a tenth of each ramp's duration
- **THEN** at every sample the set of printed-solid pairs sharing volume is
  exactly the set the inventory records

#### Scenario: A route that would collide is routed through a safe pose
- **WHEN** a direct ramp between two declared poses would drive parts
  through each other
- **THEN** the instruction routes through an intermediate pose, and that
  routing is stated as a finding about the machine

### Requirement: Moves take the time the mechanism takes
Each instruction's duration SHALL be at least the time the slowest joint in
it needs at the rate its motor and gearing allow.

#### Scenario: A duration is not faster than the mechanism
- **WHEN** an instruction's duration is compared against the largest joint
  travel it commands divided by that joint's rated rate
- **THEN** the duration is not shorter
