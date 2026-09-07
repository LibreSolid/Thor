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

- `art5` turns the whole housing about +X. The parent applies it; nothing
  in here reads it.
- `tool` turns the crown, and the gripper on it, about +Z relative to the
  housing.
- each pinion, and the pulley on its shaft, spins `CROWN_RATIO * tool`
  about the wrist axis relative to the housing, the two in opposite senses.
"""

from solid_node.node import AssemblyNode, RotationalPort, TranslationalPort

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



class WristOutput(AssemblyNode):
    """What the tool roll turns: the crown plate and the gripper on it.

    The crown's own axis is this frame's +Z through the origin, so the
    parent turns this node about that line and everything in it follows.
    """

    grip = TranslationalPort(unit='mm')

    art56_gear_plate = parts.Art56GearPlate()
    gripper = Gripper()

    def render(self):
        placing.place_from_design(self, GROUP, OUTPUT_PLACEMENT)

    def simulate(self):
        self.gripper.grip = self.grip


class Art56(AssemblyNode):
    """The wrist housing, its differential, and the gripper it carries."""

    #: The tool's roll about the wrist output axis, degrees.
    tool = RotationalPort(unit='deg')
    #: The gripper's clear opening, mm.
    grip = TranslationalPort(unit='mm')

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

    def pinion_spin(self, tool):
        """How far each pinion turns about the wrist axis for a tool roll.

        Positive is the sense of this frame's +X. The pinion on -X turns
        one way and the pinion on +X the other; that is what makes the
        pair a differential rather than a shaft.
        """
        return CROWN_RATIO * tool

    def simulate(self):
        tool = placing.bound(self.tool)
        self.output.grip = self.grip
        # The crown turns about this frame's own +Z through the origin,
        # which is the output node's own origin too.
        self.output.rotate(tool, [0.0, 0.0, 1.0])
        # Each pinion, and the belt pulley sharing its shaft, spins about
        # the wrist axis. The two pinions face each other, so one turns
        # one way about that axis and the other the opposite way; the
        # pulleys follow the pinions they share a shaft with. The design
        # places these four parts facing four different ways, so each
        # part's sign is read off its own placement rather than typed.
        spin = CROWN_RATIO * tool
        for label, attribute, about_axis in (
                ('Art56SmallGear_Art56SmallGear', 'art56_small_gear_1', spin),
                ('Art56SmallGear_Art56SmallGear001', 'art56_small_gear_2',
                 -spin),
                ('GT2x40PulleyM005', 'gt2x40_pulley_1', spin),
                ('GT2x40PulleyM006', 'gt2x40_pulley_2', -spin)):
            placed = layout.link(GROUP, label)
            sign = placing.axis_sign(placed, WRIST_AXIS)
            getattr(self, attribute).rotate(sign * about_axis,
                                            [0.0, 0.0, 1.0])
