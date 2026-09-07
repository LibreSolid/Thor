## ADDED Requirements

### Requirement: Two motors resolve into wrist roll and tool roll
The wrist SHALL be driven by the two motors the design places in the
forearm, each reaching, through its own GT2 belt and pulley, one of the two
bevel pinions that face each other on the wrist axis and mesh the crown
plate. Turning both pinions the same way SHALL roll the wrist; turning them
opposite ways SHALL roll the tool.

#### Scenario: Equal input rolls the wrist
- **WHEN** both bevel pinions turn by the same angle in the same sense
- **THEN** `art5` changes and `art6` does not

#### Scenario: Opposite input rolls the tool
- **WHEN** both bevel pinions turn by the same angle in opposite senses
- **THEN** `art6` changes and `art5` does not

#### Scenario: Wrist motion shows in both motors
- **WHEN** `art5` moves alone
- **THEN** both forearm motors turn, in the same sense, and their belts are
  redrawn to follow

#### Scenario: Tool motion shows in both motors
- **WHEN** `art6` moves alone
- **THEN** both forearm motors turn, in opposite senses, and their belts
  are redrawn to follow

### Requirement: The bevel pair stays meshed
Each bevel pinion SHALL be phased into the crown plate and SHALL stay in
mesh through the wrist's and the tool's whole travel.

#### Scenario: The bevels are in mesh at rest
- **WHEN** every driver is at rest
- **THEN** neither bevel pinion shares volume with the crown plate, and
  each is blocked against it just past its measured backlash in both
  directions

#### Scenario: The bevels stay meshed through travel
- **WHEN** `art5` and `art6` are each swept through their range at a step
  no coarser than one tooth pitch
- **THEN** at every sampled value neither bevel shares volume with the
  crown plate
