## ADDED Requirements

### Requirement: Every bought component the design places is present
The model SHALL carry every component the design's assembly places but does
not draw as a printed part: the stepper motors and their gearboxes, the
ball bearings, the GT2 pulleys, the shafts and collars, the magnets, the
fans, the optical sensors, the endstop, the servo and its horn, the control
board and its panel furniture.

#### Scenario: The component inventory matches the design's
- **WHEN** the model's bought components are listed by kind and counted
- **THEN** the list equals the one the FreeCAD assembly documents place,
  with the same count of each kind

#### Scenario: Each component stands where the design places it
- **WHEN** each bought component is compared against its FreeCAD link
- **THEN** its origin and its axis agree within 0.01 mm and 0.01°

### Requirement: Bearings sit on their shafts and in their seats
Each ball bearing SHALL have its bore on the shaft or boss the design gives
it and its outer race in the pocket that holds it, at the seat gap.

#### Scenario: A bearing is on its shaft
- **WHEN** a bearing carrying a shaft is examined
- **THEN** the shaft passes through its bore, they share no volume, and the
  bearing is blocked against radial displacement past the seat gap in every
  direction

#### Scenario: A bearing is in its seat
- **WHEN** a bearing seated in a printed part is examined
- **THEN** the part's bore surrounds its outer race, they share no volume,
  and the bearing is blocked against axial displacement past the seat gap
  toward its seat

### Requirement: Motors are held by their holders
Each motor SHALL be bolted to the printed holder the design gives it, with
its flange on that holder's face and its shaft through that holder's bore.

#### Scenario: A motor is on its holder's face
- **WHEN** a motor is examined
- **THEN** its mounting flange stands at the seat gap from the holder's
  face and its shaft passes through the holder's bore without sharing
  volume with it

#### Scenario: A motor turns nothing it is not connected to
- **WHEN** any driver moves
- **THEN** each motor body moves only with the link that holds it, and only
  its output shaft turns relative to that link

### Requirement: Pulleys and collars are fixed to their shafts
Each pulley and collar SHALL be on the shaft the design gives it and SHALL
turn with it.

#### Scenario: A pulley is on its shaft
- **WHEN** a pulley is examined
- **THEN** its bore surrounds its shaft, they share no volume, and it is
  blocked against radial displacement past the seat gap

#### Scenario: A pulley turns with its shaft
- **WHEN** the shaft a pulley is fixed to turns
- **THEN** the pulley turns by the same angle about the same axis

### Requirement: The design's own overlaps are an inventory, not an epsilon
The design's home pose has printed parts that share volume. The model SHALL
record exactly which pairs and by how much, and SHALL fail when the set of
overlapping pairs is not exactly that set.

#### Scenario: The recorded overlaps are the only overlaps
- **WHEN** every pair of printed solids is compared at rest
- **THEN** the pairs that share positive volume are exactly the pairs the
  inventory names, each within ten per cent of its recorded volume

#### Scenario: A new overlap fails
- **WHEN** a part is moved so that it shares volume with a part the
  inventory does not pair it with
- **THEN** the contract fails and names both parts

#### Scenario: A healed overlap fails
- **WHEN** a pair the inventory names stops sharing volume
- **THEN** the contract fails and names that pair

### Requirement: Every printed part is one connected body
Each printed solid SHALL be exactly one connected body.

#### Scenario: No printed part is in pieces
- **WHEN** every printed solid below the root is examined
- **THEN** each is exactly one connected body
