"""What each part is made of, as the colour it is shown in.

The design's own STEP files carry FreeCAD's default greys, which say
nothing about the machine. The author's published photographs
(``doc/main.jpg``, ``doc/banner.png``) show Thor printed in red with a dark
end effector, and that is the scheme the model follows: printed structure
red, the gripper's own printed parts dark, and every bought component the
colour of what it is actually made of.
"""

#: Printed structure — the arm's own shells, bodies, covers and holders.
PRINTED = '#d8352a'
#: Printed transmission — gears, pulleys and optical discs, darkened so a
#: maker can pick the drive train out of the shell that carries it.
PRINTED_DRIVE = '#9c241c'
#: The gripper's own printed parts, dark as the author prints them.
PRINTED_GRIPPER = '#4a2440'

#: Bearing races, shafts, screws, nuts and washers.
STEEL = '#b8bcc0'
#: Ball-bearing balls and anything bright-turned.
BRIGHT_STEEL = '#dde1e5'
#: Stepper and servo bodies.
MOTOR_BODY = '#2b2f33'
#: Aluminium pulleys and collars.
ALUMINIUM = '#a9adb2'
#: Rubber toothed belts.
BELT = '#1c1c1e'
#: Neodymium magnets.
MAGNET = '#8d9296'
#: Fan housings.
FAN = '#3a3d40'
#: Printed-circuit boards.
PCB = '#1f6b3a'
#: Moulded connector and switch bodies.
PLASTIC_BLACK = '#232426'

#: Printed parts whose colour is the gripper's rather than the arm's.
GRIPPER_PARTS = frozenset({
    'GripperActiveArm', 'GripperArm', 'GripperBot', 'GripperFinger',
    'GripperPassiveArm', 'GripperTop',
})

#: Printed parts that are transmission members rather than structure.
DRIVE_PARTS = frozenset({
    'Art1GearMotor', 'Art2MotorGear', 'Art4MotorGear', 'Art3Pulley',
    'Art56GearPlate', 'Art56SmallGear', 'Art4TransmissionColumn',
    'Art23Optodisk', 'Art4Optodisk', 'Art3TensionerPulley',
    'Art4BearingRing',
})


def printed_colour(part_name):
    """The colour a published printed part is shown in."""
    if part_name in GRIPPER_PARTS:
        return PRINTED_GRIPPER
    if part_name in DRIVE_PARTS:
        return PRINTED_DRIVE
    return PRINTED
