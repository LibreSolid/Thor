"""The forearm's root: the elbow pulley, the yaw motor and the slewing race.

`Art3` is the link between the elbow and the forearm's own yaw. Its own
parts do not move relative to each other; what it carries does. The
117-tooth pulley on its elbow axis is what the shoulder's belt drives, and
its 34 mm stepper drives the forearm's yaw through a ten-tooth pinion into
the twenty-tooth gear at the foot of the transmission column.

The forearm turns on a printed slewing race: thirty-six Ø6 balls on a
35 mm pitch circle running between `Art4BearingRing` and the seat in
`Art3Body`. A ball cage between one turning race and one still one runs at
half the speed, and the balls are shown turning at that rate.
"""

from solid_node.motion.joints import Revolute
from solid_node.node import AssemblyNode

from simulation import fasteners, layout, parts, placing
from simulation.art4 import (FOREARM_ORIGIN, FOREARM_TURN,
                             FOREARM_TURN_AXIS, YAW_AXIS_IN_LINK, Art4)
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyArt3'

#: Where the elbow axis runs in the upper arm's frame: the design puts the
#: two plates' elbow bearings 160.0 from the shoulder along the arm and
#: 68.0 out of the plate's own plane. The forearm's own origin sits a
#: further 81.5 along the arm, which is why turning it about its own
#: origin would be wrong and the joint states the line instead.
ELBOW_ALONG_ARM = 160.0
ELBOW_ACROSS_ARM = 68.0
ELBOW_ACROSS_FOREARM = 81.5

#: Teeth on the transmission column's gear and on the pinion that drives it.
COLUMN_TEETH = 20
PINION_TEETH = 10

#: How far the pinion turns for one turn of the forearm.
COLUMN_RATIO = COLUMN_TEETH / PINION_TEETH

#: Teeth on the elbow pulley the shoulder's belt drives, from its own
#: 37.000 mm tip radius: a GT2 pulley's tip radius is its pitch radius less
#: 0.254, so the pitch circle is 37.254 and pi times its diameter divided
#: by the 2 mm pitch is 117.04. Counting the section's teeth directly gave
#: 126, because the section a plane takes through this pulley catches only
#: about a sixth of the circle; see docs/measurements.md.
ELBOW_PULLEY_TEETH = 117

#: The forearm's yaw axis, in this frame: this frame's own -Z, because the
#: whole Art3 document is turned end for end inside the upper arm. Stated
#: by `simulation.art4`, the body that turns on it.
YAW_AXIS = YAW_AXIS_IN_LINK

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


def _sign(label):
    """Which way a placed part's own +Z runs against the yaw axis."""
    return placing.axis_sign(layout.link(GROUP, label), YAW_AXIS)


class Art3(AssemblyNode):
    """The elbow's output link and the forearm it turns."""

    #: The elbow, stated in the upper arm's frame: this node's angle
    #: RELATIVE to that arm. The machine-frame angle the maker drives is
    #: the shoulder's swing plus this one; `simulation.art1` states that
    #: sum and lets the solver work backwards to here.
    elbow = Revolute(axis=(0.0, 0.0, 1.0),
                     at=(0.0, ELBOW_ALONG_ARM, ELBOW_ACROSS_ARM),
                     unit='deg')

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

    # An external pair turns the other way, and the pinion turns as many
    # times as the column's gear has teeth over its own.
    art4.yaw.drives(yaw_motor.spin,
                    ratio=-COLUMN_RATIO * _sign('Stepper_Nema17x34001'))

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, PLACEMENT, phases=PHASES)
        # The forearm hangs one millimetre below this frame's origin, turned
        # end for end: its own +Z is this frame's -Z.
        self.art4.rotate(FOREARM_TURN, list(FOREARM_TURN_AXIS))
        self.art4.translate(list(FOREARM_ORIGIN))

    def simulate(self):
        # Two parts the design places, turning on their own bearings; see
        # README, "What still turns by hand".
        yaw = placing.bound(self.art4.yaw)
        self.art4_motor_gear.rotate(
            _sign('Art4MotorGear_Art4MotorGear') * -COLUMN_RATIO * yaw,
            [0.0, 0.0, 1.0])
        # A ball cage between a turning race and a still one runs at half
        # the turning race's speed.
        self.bearing_balls.rotate(
            _sign('BearingBalls001') * yaw / 2.0, [0.0, 0.0, 1.0])
