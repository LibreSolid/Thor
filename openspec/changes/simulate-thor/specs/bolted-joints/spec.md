## ADDED Requirements

### Requirement: Screws and nuts stand where the parts' own holes put them
Every fastener the model places SHALL sit on an axis derived from
cylindrical holes measured in the printed parts' own geometry, never from a
number chosen by hand.

#### Scenario: Every fastener is on a measured hole axis
- **WHEN** the fastener table is compared against the holes the probe reads
  out of the STEP solids
- **THEN** every fastener's axis matches a measured hole cluster within
  0.05 mm and 0.05°, and no fastener stands on an axis the probe did not
  find

#### Scenario: A screw passes through its stack without touching it
- **WHEN** any screw is examined
- **THEN** its shank lies inside the clearance holes of every part in its
  stack, sharing volume with none of them

#### Scenario: A screw spans the stack it fastens
- **WHEN** any screw is examined
- **THEN** its shank reaches from under its head through the far face of
  the last part in its stack, and its length is the shortest standard M3
  length that does so

#### Scenario: A screw head lands on a face
- **WHEN** any screw is examined
- **THEN** its head bears on the counterbore the design cut for it, or on
  the outer face of the first part in the stack where there is none, at the
  seat gap and no closer

### Requirement: Nuts sit in the pockets the design cut for them
A fastener SHALL carry a nut where and only where the design cut a hex
pocket on that axis, measured as six planes 2.90 mm from the axis.

#### Scenario: A nut is seated in its pocket
- **WHEN** a fastener whose axis carries a hex pocket is examined
- **THEN** its nut lies inside that pocket, sharing volume with no part,
  and is blocked against rotation past two degrees in both directions

#### Scenario: A nut is engaged on its screw
- **WHEN** a fastener carries a nut
- **THEN** the screw's shank passes through the nut and protrudes beyond it
  by at least half a millimetre and at most one nut thickness

#### Scenario: No nut is invented
- **WHEN** a fastener whose axis carries no hex pocket is examined
- **THEN** the model places no nut on it and records it as a screw into the
  print

### Requirement: No fastener fouls a moving part
Fasteners SHALL clear every part they do not fasten, at every pose the
machine can take.

#### Scenario: Fasteners are clear through the animation
- **WHEN** the machine is swept through its instructions
- **THEN** no fastener shares volume with any part outside its own stack at
  any sampled instant
