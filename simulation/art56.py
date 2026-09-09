"""The wrist: a bevel differential that resolves two motors into two joints.

Two bevel pinions face each other on the wrist axis and both mesh the crown
plate that carries the gripper. Turn them the same way and the whole wrist
housing rolls; turn them opposite ways and the crown — and the tool with
it — rolls instead. That is why the forearm's two motors both turn for
either joint, and it is the one thing about Thor a maker cannot read off
the drawings.

Measured on the design's own parts: the bevel pinions have fifteen teeth
and the crown thirty, so a pinion turns twice for one turn of the crown.
Both pinions sit on the wrist axis at x = ±39.4 in this frame, the crown
sits on it at z = 21.5, and the two GT2 40-tooth pulleys the forearm belts
drive share the pinions' shafts at x = ±18.

Sign conventions, all about this frame's own +X (the wrist axis) and +Z
(the tool axis):

- `art5` turns the whole housing about +X: the `wrist` joint below, stated
  in the forearm's frame, where the same line is its +Y.
- `tool` turns the crown, and the gripper on it, about +Z relative to the
  housing: the `WristOutput.tool` joint.
- each pinion, and the pulley on its shaft, spins `CROWN_RATIO * tool`
  about the wrist axis relative to the housing, the two in opposite senses.
"""

from solid_node.motion.joints import Revolute
from solid_node.node import AssemblyNode

from simulation import fasteners, layout, parts, placing
from simulation.gripper import Gripper
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyArt56'

#: Teeth on the crown plate and on each bevel pinion, counted from the
#: parts' own geometry (see docs/measurements.md).
CROWN_TEETH = 30
BEVEL_TEETH = 15

#: How far a pinion turns for one turn of the crown.
CROWN_RATIO = CROWN_TEETH / BEVEL_TEETH

#: The wrist axis, in this frame.
WRIST_AXIS = (1.0, 0.0, 0.0)

#: The same axis in the forearm's frame, where the fork's two bearings and
#: the 102 mm axle share it 111.5 above the forearm's origin, and how far
#: this frame is turned about Z inside that one. Stated here because this
#: is the body that rolls; the forearm reads them back to place it.
WRIST_AXIS_IN_FOREARM = (0.0, 1.0, 0.0)
WRIST_HEIGHT = 111.5
WRIST_TURN = 90.0

HOUSING_PLACEMENT = {
    'Art56MotorCoverRing_Art56MotorCoverRing': 'art56_motor_cover_ring',
    'CommonBearingFixThrough_CommonBearingFixThrough':
        'common_bearing_fix_through',
    'Art56SmallGear_Art56SmallGear': 'art56_small_gear_1',
    'Art56SmallGear_Art56SmallGear001': 'art56_small_gear_2',
    'Bearing_625ZZ001': 'bearing_625zz_1',
    'Bearing_625ZZ002': 'bearing_625zz_2',
    'Collar5mm001': 'collar_5mm_1',
    'Collar5mm002': 'collar_5mm_2',
    'GT2x40PulleyM005': 'gt2x40_pulley_1',
    'GT2x40PulleyM006': 'gt2x40_pulley_2',
}

OUTPUT_PLACEMENT = {
    'Art56GearPlate_Art56GearPlate': 'art56_gear_plate',
}

#: Where the gears are put on their shafts, about their own Z: the centre
#: of the window in which each shares least with its mate, measured by
#: `simulation.tools.geometry.mesh_window` and recorded with the rest of
#: the machine's gear pairs in `simulation.layout.MESH`.
PHASES = {
    label: mesh.phase for label, mesh in layout.MESH.items()
    if label in HOUSING_PLACEMENT
}



def _sign(label):
    """Which way a placed part's own +Z runs against the wrist axis."""
    return placing.axis_sign(layout.link(GROUP, label), WRIST_AXIS)


class WristOutput(AssemblyNode):
    """What the tool roll turns: the crown plate and the gripper on it.

    The crown's own axis is the housing frame's +Z through the origin,
    which is this node's own origin too, so the joint is one rotation.
    """

    tool = Revolute(axis=(0.0, 0.0, 1.0), unit='deg')

    art56_gear_plate = parts.Art56GearPlate()
    gripper = Gripper()

    def render(self):
        placing.place_from_design(self, GROUP, OUTPUT_PLACEMENT)


class Art56(AssemblyNode):
    """The wrist housing, its differential, and the gripper it carries."""

    #: The whole housing rolls about the fork's axis, in the forearm's
    #: frame.
    wrist = Revolute(axis=WRIST_AXIS_IN_FOREARM,
                     at=(0.0, 0.0, WRIST_HEIGHT), unit='deg')

    art56_motor_cover_ring = parts.Art56MotorCoverRing()
    common_bearing_fix_through = parts.CommonBearingFixThrough()
    art56_small_gear_1 = parts.Art56SmallGear()
    art56_small_gear_2 = parts.Art56SmallGear()
    bearing_625zz_1 = CATALOGUE['Bearing_625ZZ']()
    bearing_625zz_2 = CATALOGUE['Bearing_625ZZ']()
    collar_5mm_1 = CATALOGUE['Collar5mm']()
    collar_5mm_2 = CATALOGUE['Collar5mm']()
    gt2x40_pulley_1 = CATALOGUE['GT2x40PulleyM4']()
    gt2x40_pulley_2 = CATALOGUE['GT2x40PulleyM4']()

    output = WristOutput()

    #: Every screw and nut the parts' own holes imply, derived rather than
    #: invented; see `simulation.fasteners`.
    screws = fasteners.declare_screws(GROUP)
    nuts = fasteners.declare_nuts(GROUP)

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, HOUSING_PLACEMENT,
                                  phases=PHASES)

    def simulate(self):
        # Each pinion, and the belt pulley sharing its shaft, spins about
        # the wrist axis. The two pinions face each other, so one turns
        # one way about that axis and the other the opposite way; the
        # pulleys follow the pinions they share a shaft with. All four
        # are parts the design places, turning on their own bearings; see
        # README, "What still turns by hand".
        spin = CROWN_RATIO * placing.bound(self.output.tool)
        for label, attribute, about_axis in (
                ('Art56SmallGear_Art56SmallGear', 'art56_small_gear_1', spin),
                ('Art56SmallGear_Art56SmallGear001', 'art56_small_gear_2',
                 -spin),
                ('GT2x40PulleyM005', 'gt2x40_pulley_1', spin),
                ('GT2x40PulleyM006', 'gt2x40_pulley_2', -spin)):
            getattr(self, attribute).rotate(_sign(label) * about_axis,
                                            [0.0, 0.0, 1.0])
