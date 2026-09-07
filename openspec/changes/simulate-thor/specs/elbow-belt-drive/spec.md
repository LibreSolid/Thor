## ADDED Requirements

### Requirement: A GT2 belt carries the elbow from the shoulder axis
The elbow SHALL be driven by the belt the design runs from the pulley on
the shoulder axis to the pulley on the elbow axis, 160.0 mm apart.

#### Scenario: The belt reaches both pulleys at rest
- **WHEN** every driver is at rest
- **THEN** the belt path is tangent to both pulleys' pitch circles and its
  free spans lie on the outer common tangents

#### Scenario: The belt follows the joints
- **WHEN** `art2` or `art3` moves
- **THEN** the belt is redrawn so that it remains tangent to both pulleys
  and its total length is unchanged within 0.5 mm

#### Scenario: The belt wraps the arc the geometry gives it
- **WHEN** the belt path is measured at rest
- **THEN** the wrap arc on each pulley equals the arc the two pitch radii
  and the 160.0 mm centre distance imply, within 0.5°

### Requirement: The elbow's driver is its absolute angle
Because the belt's driving pulley is carried by `Art1` and is coaxial with
the shoulder axis, the belt holds the elbow at a constant orientation in
the machine frame while the shoulder swings. The `art3` driver SHALL
therefore measure the forearm's angle in the machine frame, not its angle
relative to the upper arm.

#### Scenario: Moving the shoulder alone does not turn the forearm
- **WHEN** `art2` changes and `art3` is unchanged
- **THEN** the forearm's direction in the machine frame is unchanged, and
  its angle relative to the upper arm has changed by the same amount `art2`
  did

#### Scenario: Moving the elbow alone turns the forearm
- **WHEN** `art3` changes and `art2` is unchanged
- **THEN** the forearm's direction in the machine frame changes by that
  amount and the upper arm does not move
