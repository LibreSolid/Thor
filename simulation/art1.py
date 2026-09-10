"""The shoulder housing: three geared motors and the arm they swing.

`Art1` is what the base's yaw turns. It carries three geared NEMA 17s: two
whose ten-tooth pinions run inside the sixty-tooth internal ring cut into
the upper arm's shoulder plate, and one on the shoulder axis itself whose
twenty-tooth GT2 pulley drives the elbow through a belt the length of the
upper arm.

That third motor is why the shoulder and the elbow are coupled. Its pulley
is coaxial with the shoulder joint but carried by this housing, not by the
arm, so what the belt sees is that pulley's turn RELATIVE TO THE ARM: hold
the motor still, swing the shoulder by theta, and the 117-tooth elbow
pulley turns against the arm by -20 theta / 117 -- not by -theta. Only
equal pulleys would hold the forearm's direction in the machine frame, and
reading it that way was this model's mistake.

The machine is modelled the way a controller drives it instead: `art3` is
the elbow's own angle, and this housing works out what its motor must turn
to deliver it, `shoulder + (117/20) * elbow`.
"""

from solid_node.motion.joints import Revolute
from solid_node.node import AssemblyNode

from simulation import fasteners, layout, parts, placing
from simulation.art2 import Art2
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyArt1'

#: Teeth on the shoulder's internal ring and on each pinion in it.
SHOULDER_RING_TEETH = 60
SHOULDER_PINION_TEETH = 10

#: How far a shoulder pinion turns for one degree of shoulder movement.
SHOULDER_RATIO = SHOULDER_RING_TEETH / SHOULDER_PINION_TEETH

#: Teeth on the elbow belt's driving pulley and on the pulley it drives.
#: The driven count is read off the elbow pulley's own 37.000 mm tip
#: radius rather than counted on a section, which catches only a sixth of
#: that pulley's circle and answers 126; see docs/measurements.md and
#: `simulation.art3.ELBOW_PULLEY_TEETH`.
ELBOW_DRIVE_TEETH = 20
ELBOW_PULLEY_TEETH = 117

#: How far the elbow's driving pulley turns for one degree of elbow travel.
ELBOW_RATIO = ELBOW_PULLEY_TEETH / ELBOW_DRIVE_TEETH

#: The shoulder axis, in this frame.
SHOULDER_AXIS = (0.0, 1.0, 0.0)

#: Where the upper arm's own frame sits in this one.
ARM_ORIGIN = (0.0, -68.0, 123.0)
ARM_TURN = 180.0
ARM_TURN_AXIS = (0.0, 0.7071067811865476, 0.7071067811865476)

#: The base's yaw axis, in this housing's own frame -- the root places
#: this node with no rotation, so it is also the machine frame's.
YAW_AXIS = (0.0, 0.0, 1.0)

PLACEMENT = {
    'Art1Bot_Art1Bot': 'art1_bot',
    'Art1Top_Art1Top': 'art1_top',
    'Art1FanHolder_Art1FanHolder': 'art1_fan_holder_1',
    'Art1FanHolder_Art1FanHolder001': 'art1_fan_holder_2',
    'Art1Body_Art1Body': 'art1_body',
    'Art23Optodisk_Art23Optodisk': 'art23_optodisk',
    'Bearing_625ZZ001': 'bearing_625zz',
    'CommonBearingFixThrough_CommonBearingFixThrough':
        'common_bearing_fix_through',
    'Nema17_GearBox001': 'shoulder_motor_1',
    'Nema17_GearBox002': 'shoulder_motor_2',
    'Nema17_GearBox003': 'elbow_motor',
    'Art2MotorGear_Art2MotorGear': 'shoulder_pinion_1',
    'Art2MotorGear_Art2MotorGear001': 'shoulder_pinion_2',
    'Fan_40x40001': 'fan_40x40_1',
    'Fan_40x40002': 'fan_40x40_2',
    'Art2BodyACover1_Art2BodyACover1': 'art2_body_a_cover1',
    'Pulley_GT2x20_Modified001': 'elbow_drive_pulley',
    '5x14.5mm001': 'shaft_5x14_5',
    '5x32mm001': 'shaft_5x32',
}

PHASES = {
    label: mesh.phase for label, mesh in layout.MESH.items()
    if label in PLACEMENT
}

def _sign(label):
    """Which way a placed part's own +Z runs against the shoulder axis."""
    return placing.axis_sign(layout.link(GROUP, label), SHOULDER_AXIS)


class Art1(AssemblyNode):
    """The shoulder housing and the arm above it."""

    #: The whole housing yaws about its own Z, through its own origin --
    #: the root places it with no rotation, so this is also the base's
    #: own yaw axis.
    yaw = Revolute(axis=YAW_AXIS, unit='deg')

    art1_bot = parts.Art1Bot()
    art1_top = parts.Art1Top()
    art1_fan_holder_1 = parts.Art1FanHolder()
    art1_fan_holder_2 = parts.Art1FanHolder()
    art1_body = parts.Art1Body()
    art23_optodisk = parts.Art23Optodisk()
    bearing_625zz = CATALOGUE['Bearing_625ZZ']()
    common_bearing_fix_through = parts.CommonBearingFixThrough()
    shoulder_motor_1 = CATALOGUE['Nema17_GearBox']()
    shoulder_motor_2 = CATALOGUE['Nema17_GearBox']()
    elbow_motor = CATALOGUE['Nema17_GearBox']()
    shoulder_pinion_1 = parts.Art2MotorGear()
    shoulder_pinion_2 = parts.Art2MotorGear()
    fan_40x40_1 = CATALOGUE['Fan_40x40']()
    fan_40x40_2 = CATALOGUE['Fan_40x40']()
    art2_body_a_cover1 = parts.Art2BodyACover1()
    elbow_drive_pulley = CATALOGUE['Pulley_GT2x20_Modified']()
    shaft_5x14_5 = CATALOGUE['5x14.5mm']()
    shaft_5x32 = CATALOGUE['5x32mm']()

    art2 = Art2()

    #: Every screw and nut the parts' own holes imply, derived
    #: rather than invented; see `simulation.fasteners`.
    screws = fasteners.declare_screws(GROUP)
    nuts = fasteners.declare_nuts(GROUP)

    #: How far the elbow's drive train -- its pulley, its optical disc and
    #: its motor -- turns about the shoulder axis relative to THIS housing.
    #: The belt sees the drive pulley only against the arm, so the pulley
    #: turns `drive - shoulder` there; the belt carries that onto the
    #: 117-tooth elbow pulley at 20/117, giving
    #: `(20/117)(drive - shoulder)`, and setting that equal to the elbow's
    #: own angle leaves `drive = shoulder + (117/20) * elbow`. The
    #: shoulder term is the compensation a controller has to make, stated
    #: once, here, beside the motor that makes it.
    drive = art2.shoulder + ELBOW_RATIO * art2.art3.elbow

    # Each shoulder motor drives its pinion inside the ring, so it turns
    # as many times as the ring has teeth over the pinion's own.
    art2.shoulder.drives(shoulder_motor_2.spin,
                         ratio=SHOULDER_RATIO * _sign('Nema17_GearBox002'))
    art2.shoulder.drives(shoulder_motor_1.spin,
                         ratio=SHOULDER_RATIO * _sign('Nema17_GearBox001'))

    # The motor is on the drive pulley's own shaft, so it turns with it.
    drive.drives(elbow_motor.spin, ratio=_sign('Nema17_GearBox003'))

    # The two shoulder pinions are printed parts turning on their own
    # bearings inside the ring, at the same ratio as the motors above.
    art2.shoulder.drives(shoulder_pinion_1.turn,
                         ratio=SHOULDER_RATIO
                         * _sign('Art2MotorGear_Art2MotorGear'))
    art2.shoulder.drives(shoulder_pinion_2.turn,
                         ratio=SHOULDER_RATIO
                         * _sign('Art2MotorGear_Art2MotorGear001'))

    # The elbow drive pulley and its optical disc are printed parts
    # turning on the shoulder axis, carried by this housing; `drive` is
    # the same sum the elbow motor above turns with.
    drive.drives(elbow_drive_pulley.turn,
                ratio=_sign('Pulley_GT2x20_Modified001'))
    drive.drives(art23_optodisk.turn,
                ratio=_sign('Art23Optodisk_Art23Optodisk'))

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, PLACEMENT, phases=PHASES)
        self.art2.rotate(ARM_TURN, list(ARM_TURN_AXIS))
        self.art2.translate(list(ARM_ORIGIN))
