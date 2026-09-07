## ADDED Requirements

### Requirement: The servo opens and closes the fingers together
The gripper SHALL be driven by the single servo the design places on the
gripper base, through its horn, the active arm, the passive arm and the two
link arms, so that both fingers move together and symmetrically.

#### Scenario: The fingers are symmetric at every opening
- **WHEN** `grip` is set to any value in its range
- **THEN** the two finger faces are equidistant from the gripper's centre
  plane within 0.05 mm

#### Scenario: The driver measures the clear opening
- **WHEN** `grip` is set to a value
- **THEN** the clear distance between the two finger gripping faces equals
  that value within 0.1 mm

#### Scenario: The servo horn drives the linkage
- **WHEN** `grip` changes
- **THEN** the servo horn rotates, the active and passive arms swing, and
  the servo body does not move relative to the gripper base

### Requirement: The linkage closes without fouling itself
No two parts of the gripper SHALL share volume at any opening, beyond the
overlaps the design's own geometry already carries.

#### Scenario: The gripper is clear through its whole travel
- **WHEN** `grip` is swept from fully closed to fully open
- **THEN** at every sampled value the set of gripper part pairs sharing
  volume is exactly the set the seats inventory records

#### Scenario: Fully closed is closed
- **WHEN** `grip` is at its minimum
- **THEN** the two finger faces are within 0.1 mm of touching and do not
  share volume
