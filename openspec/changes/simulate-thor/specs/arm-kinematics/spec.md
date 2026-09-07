## ADDED Requirements

### Requirement: The machine stands where the design says it stands
The model SHALL reproduce the pose the design's own FreeCAD assembly
records, in the assembly's own frame: Z up, origin on the mounting face of
`BaseBot`, every printed part at the placement that assembly solved.

#### Scenario: The home pose is the design's home pose
- **WHEN** every driver is at its rest value
- **THEN** each printed part's world placement equals the placement its
  FreeCAD link records, within 0.01 mm and 0.01°

#### Scenario: The transcribed layout has not drifted from the design
- **WHEN** the layout constants are compared against the placements read
  back out of `freecad-src/Assembly*.FCStd`
- **THEN** every translation agrees within 0.001 mm and every rotation
  within 0.001°, and no instance is present in one and absent in the other

### Requirement: Six joints, each about the axis the design puts it on
The model SHALL expose six rotational joints. Each SHALL turn about the
axis and through the point the design's assembly places it on, and each
driver SHALL measure that joint's own rotation from the home pose in
degrees, positive by the right-hand rule.

#### Scenario: The base yaws about Z
- **WHEN** `art1` is 30°
- **THEN** everything above the slewing bearing has rotated 30° about the
  Z axis through (0, 0) and the base has not moved

#### Scenario: The shoulder rolls about Y at 202 mm
- **WHEN** `art2` is 20°
- **THEN** the upper arm and everything above it has rotated 20° about the
  Y axis through z = 202.0, and the elbow axis has moved to the circle of
  radius 160.0 about that axis

#### Scenario: The elbow rolls about Y at 362 mm
- **WHEN** `art3` is 45° and every other driver is at rest
- **THEN** the forearm and everything above it has rotated 45° about the Y
  axis through z = 362.0

#### Scenario: The forearm yaws about its own Z
- **WHEN** `art4` is 90°
- **THEN** the wrist assembly has rotated 90° about the forearm's own
  longitudinal axis and the elbow has not moved

#### Scenario: The wrist rolls about Y at 556 mm
- **WHEN** `art5` is 40° and every other driver is at rest
- **THEN** the wrist housing and the gripper have rotated 40° about the Y
  axis through z = 556.0

#### Scenario: The tool yaws about the wrist's own axis
- **WHEN** `art6` is 60° and every other driver is at rest
- **THEN** the gripper has rotated 60° about the wrist output axis and the
  wrist housing has not moved

### Requirement: The reach is the reach the design's drawing states
The model's axis spacings SHALL match `doc/ThorDimensions.png` where the
assembly agrees with it, and the model SHALL record the one span where they
disagree rather than adopting either silently.

#### Scenario: Base to shoulder and shoulder to elbow
- **WHEN** the joint axes are measured at the home pose
- **THEN** the base-to-shoulder span is 202.0 mm and the shoulder-to-elbow
  span is 160.0 mm, each within 0.01 mm of the drawing

#### Scenario: Elbow to wrist disagrees with the drawing
- **WHEN** the elbow-to-wrist span is measured at the home pose
- **THEN** it is 194.0 mm, one millimetre short of the drawing's 195.00 mm,
  and that difference is stated as a finding

### Requirement: Each joint's motion is one rigid motion
A joint SHALL move every part above it and no part below it, and no part
SHALL move relative to another part of the same link at any driver value.

#### Scenario: A link is rigid through its whole travel
- **WHEN** any single driver is swept through its declared range
- **THEN** the distance between any two parts of one link is unchanged
  within 0.01 mm at every sampled value
