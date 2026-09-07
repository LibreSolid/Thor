"""The forearm's root: the elbow pulley, the yaw motor and the slewing race.

`Art3` is the link between the elbow and the forearm's own yaw. Its own
parts do not move relative to each other; what it carries does. The
126-tooth pulley on its elbow axis is what the shoulder's belt drives, and
its 34 mm stepper drives the forearm's yaw through a ten-tooth pinion into
the twenty-tooth gear at the foot of the transmission column.

The forearm turns on a printed slewing race: thirty-six Ø6 balls on a
35 mm pitch circle running between `Art4BearingRing` and the seat in
`Art3Body`. A ball cage between one turning race and one still one runs at
half the speed, and the balls are shown turning at that rate.
"""

from solid_node.node import AssemblyNode, RotationalPort, TranslationalPort

from simulation import fasteners, layout, parts, placing
from simulation.art4 import Art4
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyArt3'

#: Teeth on the transmission column's gear and on the pinion that drives it.
COLUMN_TEETH = 20
PINION_TEETH = 10

#: How far the pinion turns for one turn of the forearm.
COLUMN_RATIO = COLUMN_TEETH / PINION_TEETH

#: Teeth on the elbow pulley the shoulder's belt drives.
ELBOW_PULLEY_TEETH = 126

#: The forearm's yaw axis, in this frame: this frame's own -Z, because the
#: whole Art3 document is turned end for end inside the upper arm.
YAW_AXIS = (0.0, 0.0, -1.0)

PLACEMENT = {
    'Art3Body_Art3Body': 'art3_body',
    'Art23Optodisk_Art23Optodisk': 'art23_optodisk',
    'Art3Pulley_Art3Pulley': 'art3_pulley',
    'Art4MotorFix_Art4MotorFix': 'art4_motor_fix',
    'Stepper_Nema17x34001': 'yaw_motor',
    'Art4MotorGear_Art4MotorGear': 'art4_motor_gear',
    'Fan_40x40001': 'fan_40x40',
    'Bearing_625ZZ001': 'bearing_625zz_1',
    'Bearing_625ZZ002': 'bearing_625zz_2',
    'CommonBearingFixThrough_CommonBearingFixThrough':
        'common_bearing_fix_through_1',
    'CommonBearingFixThrough_CommonBearingFixThrough001':
        'common_bearing_fix_through_2',
    'OpticSensor001': 'optic_sensor',
    'Art4BearingRing_Art4BearingRing': 'art4_bearing_ring',
    'BearingBalls001': 'bearing_balls',
}

PHASES = {
    label: mesh.phase for label, mesh in layout.MESH.items()
    if label in PLACEMENT
}


class Art3(AssemblyNode):
    """The elbow's output link and the forearm it turns."""

    #: The forearm's yaw about its own axis, degrees.
    yaw = RotationalPort(unit='deg')
    #: The wrist's roll, degrees.
    wrist = RotationalPort(unit='deg')
    #: The tool's roll, degrees.
    tool = RotationalPort(unit='deg')
    #: The gripper's clear opening, mm.
    grip = TranslationalPort(unit='mm')

    art3_body = parts.Art3Body()
    art23_optodisk = parts.Art23Optodisk()
    art3_pulley = parts.Art3Pulley()
    art4_motor_fix = parts.Art4MotorFix()
    yaw_motor = CATALOGUE['Stepper_Nema17x34']()
    art4_motor_gear = parts.Art4MotorGear()
    fan_40x40 = CATALOGUE['Fan_40x40']()
    bearing_625zz_1 = CATALOGUE['Bearing_625ZZ']()
    bearing_625zz_2 = CATALOGUE['Bearing_625ZZ']()
    common_bearing_fix_through_1 = parts.CommonBearingFixThrough()
    common_bearing_fix_through_2 = parts.CommonBearingFixThrough()
    optic_sensor = CATALOGUE['OpticSensor']()
    art4_bearing_ring = parts.Art4BearingRing()
    bearing_balls = CATALOGUE['BearingBalls']()

    art4 = Art4()

    #: Every screw and nut the parts' own holes imply, derived
    #: rather than invented; see `simulation.fasteners`.
    screws = fasteners.declare_screws(GROUP)
    nuts = fasteners.declare_nuts(GROUP)

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, PLACEMENT, phases=PHASES)
        # The forearm hangs one millimetre below this frame's origin, turned
        # end for end: its own +Z is this frame's -Z.
        self.art4.rotate(180.0, [0.0, 1.0, 0.0])
        self.art4.translate([0.0, 0.0, -1.0])

    def simulate(self):
        yaw = placing.bound(self.yaw)
        self.art4.wrist = self.wrist
        self.art4.tool = self.tool
        self.art4.grip = self.grip
        # The forearm's own +Z is the yaw axis and its origin is on it.
        self.art4.rotate(yaw, [0.0, 0.0, 1.0])
        # An external pair turns the other way, and the pinion turns as
        # many times as the column's gear has teeth over its own.
        pinion = -COLUMN_RATIO * yaw
        sign = placing.axis_sign(
            layout.link(GROUP, 'Art4MotorGear_Art4MotorGear'), YAW_AXIS)
        self.art4_motor_gear.rotate(sign * pinion, [0.0, 0.0, 1.0])
        motor_sign = placing.axis_sign(
            layout.link(GROUP, 'Stepper_Nema17x34001'), YAW_AXIS)
        self.yaw_motor.spin = motor_sign * pinion
        # A ball cage between a turning race and a still one runs at half
        # the turning race's speed.
        cage_sign = placing.axis_sign(
            layout.link(GROUP, 'BearingBalls001'), YAW_AXIS)
        self.bearing_balls.rotate(cage_sign * yaw / 2.0, [0.0, 0.0, 1.0])
