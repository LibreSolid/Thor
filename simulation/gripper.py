"""The gripper: one servo, two meshed sector gears, two parallel jaws.

The design drives both jaws from a single servo whose horn is coaxial with
the active arm. The active and passive arms carry meshing sector gears at
their pivots, so the passive side follows the active one exactly and the
jaws stay symmetric. Each jaw hangs on a parallelogram — the arm below and
a link above, both 35.00 mm between pins — so it translates on a circle
without turning: the two gripping faces stay flat and parallel at every
opening.

Measured from the parts' own pivot bores, in the machine frame at rest:

===========================  ==============  ==============
pin                          right (+y)      left (-y)
===========================  ==============  ==============
arm pivot in the body        14.52, 645.00   -14.50, 645.00
arm pin in the jaw           49.51, 645.17   -49.50, 645.15
link pivot in the body        6.00, 663.50    -6.00, 663.50
link pin in the jaw          41.00, 663.50   -41.00, 663.50
===========================  ==============  ==============

Both cranks are 35.00 mm, and the arm-to-link offset is the same on the
body (-8.52, +18.50) as on the jaw (-8.51, +18.33): a parallelogram to
within the 0.17 mm the design's own pin positions carry.
"""

from solid_node.math import acos, cos, sin
from solid_node.node import AssemblyNode, TranslationalPort

from simulation import layout, parts, placing
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyArt56'

#: Distance between an arm's two pins, mm. Measured on both arms and both
#: links; all four agree to 0.01.
CRANK = 35.00

#: The crank's angle above the opening direction at rest, degrees. The
#: design's arm pin sits 0.17 mm high over its 34.99 mm reach.
REST_CRANK_ANGLE = 0.278

#: Half the clear opening at rest, mm: the jaw's gripping face is a flat
#: plane at this distance from the gripper's centre, over its whole height.
REST_HALF_OPENING = 34.97

#: The clear opening between the two gripping faces at rest, mm.
OPEN = 2 * REST_HALF_OPENING

#: Where the arm pivots sit, in the Art56 frame, mm.
ARM_PIVOT_X = 14.5216
ARM_PIVOT_Z = 89.0
LINK_PIVOT_X = 6.0072
LINK_PIVOT_Z = 107.5

PLACEMENT = {
    'GripperBot_GripperBot': 'gripper_bot',
    'Unnamed_GripperTop': 'gripper_top',
    'Servomotor002': 'servomotor',
    'ServomotorWheelHorn001': 'servomotor_wheel_horn',
    'GripperActiveArm_GripperActiveArm': 'gripper_active_arm',
    'Unnamed3_GripperPassiveArm': 'gripper_passive_arm',
    'Unnamed2_GripperArm': 'gripper_arm_1',
    'Unnamed2_GripperArm001': 'gripper_arm_2',
    'Unnamed1_GripperFinger': 'gripper_finger',
    'GripperFinger_sym001': 'gripper_finger_sym',
}


#: The jaw pivot pins the design ships inside their arms' own files, and
#: the arm each one belongs to.
PINS = {
    'gripper_active_pin': 'GripperActiveArm_GripperActiveArm',
    'gripper_passive_pin': 'Unnamed3_GripperPassiveArm',
}


def crank_angle(opening):
    """The arm's angle from its rest position for a given clear opening.

    The jaw is in pure circular translation, so its inward travel is
    `CRANK * (cos(phi) - cos(phi_rest))` and both jaws move together.
    """
    cosine = cos(REST_CRANK_ANGLE) + (opening - OPEN) / (2 * CRANK)
    return acos(cosine) - REST_CRANK_ANGLE


def jaw_offset(opening):
    """How far a jaw has travelled from rest, as (dy, dz) in the Art56 frame."""
    angle = crank_angle(opening) + REST_CRANK_ANGLE
    return (CRANK * (cos(angle) - cos(REST_CRANK_ANGLE)),
            CRANK * (sin(angle) - sin(REST_CRANK_ANGLE)))


class Gripper(AssemblyNode):
    """The end effector, at rest in the wrist output's own frame.

    `grip` is the clear opening between the two gripping faces, in
    millimetres: `OPEN` is fully open, zero is closed.
    """

    grip = TranslationalPort(unit='mm')

    gripper_bot = parts.GripperBot()
    gripper_top = parts.GripperTop()
    servomotor = CATALOGUE['Servomotor']()
    servomotor_wheel_horn = CATALOGUE['ServomotorWheelHorn']()
    gripper_active_arm = parts.GripperActiveArm()
    gripper_active_pin = parts.GripperActiveArmPin()
    gripper_passive_arm = parts.GripperPassiveArm()
    gripper_passive_pin = parts.GripperPassiveArmPin()
    gripper_arm_1 = parts.GripperArm()
    gripper_arm_2 = parts.GripperArm()
    gripper_finger = parts.GripperFinger()
    gripper_finger_sym = parts.GripperFingerMirrored()

    def render(self):
        placing.place_from_design(self, GROUP, PLACEMENT)
        # Each jaw pivot pin is exported inside its arm's own file, so it
        # takes that arm's placement unchanged and travels with it.
        for pin, label in PINS.items():
            placed = layout.link(GROUP, label)
            child = getattr(self, pin)
            child.rotate(placed.angle, list(placed.axis))
            child.translate(list(placed.translate))

    def simulate(self):
        opening = self.grip.value
        if opening is None:
            return
        angle = crank_angle(opening)
        offset = jaw_offset(opening)
        # The pivots run along the Art56 frame's own Y; turning about it by
        # +angle closes the +x jaw and -angle closes the -x one.
        for label, sign, pivot_x, pivot_z in (
                ('GripperActiveArm_GripperActiveArm', 1.0,
                 ARM_PIVOT_X, ARM_PIVOT_Z),
                ('ServomotorWheelHorn001', 1.0, ARM_PIVOT_X, ARM_PIVOT_Z),
                ('Unnamed3_GripperPassiveArm', -1.0,
                 -ARM_PIVOT_X, ARM_PIVOT_Z),
                ('Unnamed2_GripperArm001', 1.0, LINK_PIVOT_X, LINK_PIVOT_Z),
                ('Unnamed2_GripperArm', -1.0, -LINK_PIVOT_X, LINK_PIVOT_Z)):
            placed = layout.link(GROUP, label)
            child = getattr(self, PLACEMENT[label])
            placing.turn_about(child, placed, sign * angle,
                               [0.0, -1.0, 0.0], [pivot_x, 0.0, pivot_z])
        for pin, label in PINS.items():
            placed = layout.link(GROUP, label)
            sign = 1.0 if pin == 'gripper_active_pin' else -1.0
            pivot_x = ARM_PIVOT_X if sign > 0 else -ARM_PIVOT_X
            placing.turn_about(getattr(self, pin), placed, sign * angle,
                               [0.0, -1.0, 0.0], [pivot_x, 0.0, ARM_PIVOT_Z])
        # Each jaw is the coupler of a parallelogram: it translates and
        # never turns. The travel is stated in the Art56 frame, so it is
        # carried into each jaw's own frame before it is applied.
        for label, sign in (('Unnamed1_GripperFinger', 1.0),
                            ('GripperFinger_sym001', -1.0)):
            placed = layout.link(GROUP, label)
            child = getattr(self, PLACEMENT[label])
            child.translate(placing.into_local(
                placed, direction=[sign * offset[0], 0.0, offset[1]]))
