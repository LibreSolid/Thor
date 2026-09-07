"""The shoulder housing: three geared motors and the arm they swing.

`Art1` is what the base's yaw turns. It carries three geared NEMA 17s: two
whose ten-tooth pinions run inside the sixty-tooth internal ring cut into
the upper arm's shoulder plate, and one on the shoulder axis itself whose
twenty-tooth GT2 pulley drives the elbow through a belt the length of the
upper arm.

That third motor is why the elbow's driver is an absolute angle. Its pulley
is coaxial with the shoulder joint but carried by this housing, not by the
arm: swing the shoulder and the belt holds the forearm's direction in the
machine frame while its angle relative to the upper arm changes by exactly
as much as the shoulder moved.
"""

from solid_node.node import AssemblyNode, RotationalPort, TranslationalPort

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

#: Which motor turns with which pinion.
SHOULDER_DRIVE = (('Art2MotorGear_Art2MotorGear', 'Nema17_GearBox002'),
                  ('Art2MotorGear_Art2MotorGear001', 'Nema17_GearBox001'))


class Art1(AssemblyNode):
    """The shoulder housing and the arm above it."""

    #: The shoulder's angle in the machine frame, degrees.
    shoulder = RotationalPort(unit='deg')
    #: The forearm's absolute angle in the machine frame, degrees.
    elbow = RotationalPort(unit='deg')
    #: The forearm's yaw about its own axis, degrees.
    yaw = RotationalPort(unit='deg')
    #: The wrist's roll, degrees.
    wrist = RotationalPort(unit='deg')
    #: The tool's roll, degrees.
    tool = RotationalPort(unit='deg')
    #: The gripper's clear opening, mm.
    grip = TranslationalPort(unit='mm')

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

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, PLACEMENT, phases=PHASES)
        self.art2.rotate(ARM_TURN, list(ARM_TURN_AXIS))
        self.art2.translate(list(ARM_ORIGIN))

    def simulate(self):
        shoulder = placing.bound(self.shoulder)
        elbow = placing.bound(self.elbow)
        self.art2.shoulder = self.shoulder
        self.art2.elbow = self.elbow
        self.art2.yaw = self.yaw
        self.art2.wrist = self.wrist
        self.art2.tool = self.tool
        self.art2.grip = self.grip
        # The arm's own frame sits on the shoulder axis and its own +Z runs
        # along it, so the swing is a turn about its own Z.
        self.art2.rotate(shoulder, [0.0, 0.0, 1.0])
        # An internal pair turns the same way, and the pinion turns as many
        # times as the ring has teeth over its own.
        for pinion_label, motor_label in SHOULDER_DRIVE:
            turn = SHOULDER_RATIO * shoulder
            sign = placing.axis_sign(layout.link(GROUP, pinion_label),
                                     SHOULDER_AXIS)
            getattr(self, PLACEMENT[pinion_label]).rotate(
                sign * turn, [0.0, 0.0, 1.0])
            motor_sign = placing.axis_sign(layout.link(GROUP, motor_label),
                                           SHOULDER_AXIS)
            getattr(self, PLACEMENT[motor_label]).spin = motor_sign * turn
        # The elbow belt's driving pulley is on the shoulder axis but is
        # carried here, so it turns by the elbow's absolute angle at the
        # belt's own ratio, whatever the shoulder is doing.
        drive = ELBOW_RATIO * elbow
        pulley_sign = placing.axis_sign(
            layout.link(GROUP, 'Pulley_GT2x20_Modified001'), SHOULDER_AXIS)
        self.elbow_drive_pulley.rotate(pulley_sign * drive, [0.0, 0.0, 1.0])
        disk_sign = placing.axis_sign(
            layout.link(GROUP, 'Art23Optodisk_Art23Optodisk'), SHOULDER_AXIS)
        self.art23_optodisk.rotate(disk_sign * drive, [0.0, 0.0, 1.0])
        motor_sign = placing.axis_sign(
            layout.link(GROUP, 'Nema17_GearBox003'), SHOULDER_AXIS)
        self.elbow_motor.spin = motor_sign * drive
