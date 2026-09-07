## ADDED Requirements

### Requirement: Two pinions drive the shoulder's internal ring gear
The shoulder SHALL be driven by the two geared motors the design places in
`Art1`, each carrying a ten-tooth pinion that runs inside the sixty-tooth
internal ring gear cut into the shoulder plate.

#### Scenario: The pinions are in mesh at rest
- **WHEN** every driver is at rest
- **THEN** each pinion shares no volume with the ring gear, and each is
  blocked against the ring within one degree past its measured backlash
  window in both directions

#### Scenario: The pinions stay in mesh through the shoulder's travel
- **WHEN** `art2` is swept through its range at a step no coarser than one
  tooth pitch
- **THEN** at every sampled value each pinion shares no volume with the
  ring gear and remains blocked against it past its backlash

#### Scenario: The pinions turn at the ring's ratio
- **WHEN** `art2` changes by an angle
- **THEN** each pinion turns, relative to the arm that carries it, by six
  times that angle, the ratio of sixty ring teeth to ten pinion teeth

#### Scenario: The motors turn with their pinions
- **WHEN** `art2` moves
- **THEN** each geared motor's output shaft turns with its pinion and the
  motor bodies do not move relative to `Art1`

### Requirement: The two pinions carry different phases
The design places the two pinions as mirrored instances at x = ±21.5, so
their local frames differ. Each pinion's phase SHALL be the centre of its
own measured interference-free window, and the two SHALL NOT be assumed
equal.

#### Scenario: Each pinion is phased on its own measurement
- **WHEN** each pinion is swept through one tooth pitch against the ring
- **THEN** each has a contiguous window in which it shares no volume with
  the ring, the two windows differ, and each pinion is placed at the centre
  of its own
