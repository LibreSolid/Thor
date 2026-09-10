"""The upper arm: a fork of two plates, and the belt run inside it.

`Art2` is the 160 mm link between the shoulder and the elbow, built as two
plates 136 mm apart with a union piece between them. Its shoulder end
carries the sixty-tooth internal ring the two shoulder pinions run in; its
elbow end carries the bearings the forearm turns on.

The elbow's belt runs the length of this fork, from a pulley on the
shoulder axis to the pulley on the elbow axis, clear of the two sprung
tensioners the arm carries for it. The driving pulley is carried by `Art1`,
not by this arm, so what the belt sees at that end is the drive pulley's
turn **relative to this arm** — and at twenty teeth against the elbow
pulley's hundred and seventeen it carries only 20/117 of it across. A
shoulder swing with the motor still therefore does not hold the forearm's
direction in the machine frame; the model once said it did, and it was
wrong. The elbow joint on `Art3` is the forearm's angle relative to this
arm, the maker drives that joint, and the housing's own motor makes up the
shoulder term.
"""

import math

from solid_node.motion.joints import Revolute
from solid_node.node import AssemblyNode

from simulation import fasteners, flexibles, layout, parts, placing
from simulation.art3 import (ELBOW_ACROSS_ARM, ELBOW_ALONG_ARM,
                             ELBOW_ACROSS_FOREARM, Art3)
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyArt2'

#: Teeth on the internal ring cut into the shoulder plate.
SHOULDER_RING_TEETH = 60

#: The elbow axis in this frame.
ELBOW_AXIS = (0.0, 0.0, 1.0)

#: The design places its belt loop flat, in a plane the pulleys are not in;
#: the model draws the belt from its pulleys instead. See
#: `simulation.flexibles` and design.md, Findings.
BELTS = ('GT2_Belt_Art3001',)

#: The belt runs in this frame's own XY plane: its drive pulley is on the
#: shoulder axis at the origin and the elbow pulley 160.0 along +Y. What
#: is left is how far up the shoulder axis the plane sits, and the two
#: pulleys leave only 3.65 mm of shared land for a 6 mm belt; the model
#: centres it in what they share and records the shortfall.
BELT_PLANE_Z = flexibles.ARM_BELT_PLANE

PLACEMENT = {
    'Art2BodyA_Art2BodyA': 'art2_body_a',
    'Art2BodyAWindow_Art2BodyAWindow': 'art2_body_a_window',
    'Art2BodyACover2_Art2BodyACover2': 'art2_body_a_cover2',
    'Art2BodyUnion_Art2BodyUnion': 'art2_body_union',
    'Art2BodyBCover_Art2BodyBCover': 'art2_body_b_cover',
    'Art2BodyB_Art2BodyB': 'art2_body_b',
    'CommonBearingFix_CommonBearingFix': 'common_bearing_fix_1',
    'CommonBearingFix_CommonBearingFix001': 'common_bearing_fix_2',
    'CommonBearingFix_CommonBearingFix002': 'common_bearing_fix_3',
    'CommonBearingFix_CommonBearingFix003': 'common_bearing_fix_4',
    'Art2SideCover_Art2SideCover': 'art2_side_cover_1',
    'Art2SideCover_Art2SideCover001': 'art2_side_cover_2',
    'Art3TensionerBody_Art3TensionerBody': 'tensioner_body_1',
    'Art3TensionerBody_Art3TensionerBody001': 'tensioner_body_2',
    'Art3TensionerPulley_Art3TensionerPulley': 'tensioner_pulley_1',
    'Art3TensionerPulley_Art3TensionerPulley001': 'tensioner_pulley_2',
    'Bearing_625ZZ001': 'bearing_625zz_1',
    'Bearing_625ZZ002': 'bearing_625zz_2',
    'Bearing_625ZZ003': 'bearing_625zz_3',
    'Bearing_625ZZ004': 'bearing_625zz_4',
    'OpticSensor001': 'optic_sensor_1',
    'OpticSensor002': 'optic_sensor_2',
    '4x14mm001': 'tensioner_shaft_1',
    '4x14mm002': 'tensioner_shaft_2',
    'Bearing_MF84ZZ001': 'bearing_mf84zz_1',
    'Bearing_MF84ZZ002': 'bearing_mf84zz_2',
    'Magnet001': 'magnet_1',
    'Magnet002': 'magnet_2',
    'Magnet003': 'magnet_3',
    'Magnet004': 'magnet_4',
    'Magnet005': 'magnet_5',
    'Magnet006': 'magnet_6',
    'Magnet007': 'magnet_7',
    'Magnet008': 'magnet_8',
    'Magnet009': 'magnet_9',
    'Magnet010': 'magnet_10',
    'Magnet011': 'magnet_11',
    'Magnet012': 'magnet_12',
    '5x128mm001': 'elbow_axle',
}


def belt_travel(turn):
    """How far the elbow belt runs for a turn of the elbow pulley, mm.

    Positive is the sense of a positive turn about the elbow axis: the
    belt is a rack wrapped on the pitch circle, so its travel is that
    circle's arc and nothing else.
    """
    # Written as a plain multiplication rather than through
    # `math.radians`, because under `solid build` the turn is a symbolic
    # expression and the C library's radians() takes only floats.
    return turn * (math.pi / 180.0) * flexibles.pitch_radius(
        flexibles.ARM_DRIVEN_TEETH)


class Art2(AssemblyNode):
    """The upper arm and the forearm it carries."""

    #: The arm swings about the shoulder axis, through its own origin,
    #: stated in its own rest frame. `Art1.render()` turns this arm 180
    #: degrees about (0, 1/sqrt2, 1/sqrt2) before placing it, which
    #: carries the housing's own shoulder axis (0, 1, 0) onto this
    #: frame's (0, 0, 1) -- a 180-degree turn is its own inverse, so the
    #: housing's axis maps onto this one exactly.
    shoulder = Revolute(axis=(0.0, 0.0, 1.0), unit='deg')

    art2_body_a = parts.Art2BodyA()
    art2_body_a_window = parts.Art2BodyAWindow()
    art2_body_a_cover2 = parts.Art2BodyACover2()
    art2_body_union = parts.Art2BodyUnion()
    art2_body_b_cover = parts.Art2BodyBCover()
    art2_body_b = parts.Art2BodyB()
    common_bearing_fix_1 = parts.CommonBearingFix()
    common_bearing_fix_2 = parts.CommonBearingFix()
    common_bearing_fix_3 = parts.CommonBearingFix()
    common_bearing_fix_4 = parts.CommonBearingFix()
    art2_side_cover_1 = parts.Art2SideCover()
    art2_side_cover_2 = parts.Art2SideCover()
    tensioner_body_1 = parts.Art3TensionerBody()
    tensioner_body_2 = parts.Art3TensionerBody()
    tensioner_pulley_1 = parts.Art3TensionerPulley()
    tensioner_pulley_2 = parts.Art3TensionerPulley()
    bearing_625zz_1 = CATALOGUE['Bearing_625ZZ']()
    bearing_625zz_2 = CATALOGUE['Bearing_625ZZ']()
    bearing_625zz_3 = CATALOGUE['Bearing_625ZZ']()
    bearing_625zz_4 = CATALOGUE['Bearing_625ZZ']()
    optic_sensor_1 = CATALOGUE['OpticSensor']()
    optic_sensor_2 = CATALOGUE['OpticSensor']()
    tensioner_shaft_1 = CATALOGUE['4x14mm']()
    tensioner_shaft_2 = CATALOGUE['4x14mm']()
    bearing_mf84zz_1 = CATALOGUE['Bearing_MF84ZZ']()
    bearing_mf84zz_2 = CATALOGUE['Bearing_MF84ZZ']()
    magnet_1 = CATALOGUE['Magnet']()
    magnet_2 = CATALOGUE['Magnet']()
    magnet_3 = CATALOGUE['Magnet']()
    magnet_4 = CATALOGUE['Magnet']()
    magnet_5 = CATALOGUE['Magnet']()
    magnet_6 = CATALOGUE['Magnet']()
    magnet_7 = CATALOGUE['Magnet']()
    magnet_8 = CATALOGUE['Magnet']()
    magnet_9 = CATALOGUE['Magnet']()
    magnet_10 = CATALOGUE['Magnet']()
    magnet_11 = CATALOGUE['Magnet']()
    magnet_12 = CATALOGUE['Magnet']()
    elbow_axle = CATALOGUE['5x128mm']()

    elbow_belt = flexibles.ElbowBelt()

    art3 = Art3()

    #: Every screw and nut the parts' own holes imply, derived
    #: rather than invented; see `simulation.fasteners`.
    screws = fasteners.declare_screws(GROUP)
    nuts = fasteners.declare_nuts(GROUP)

    # The belt does not slip: what it feeds past a point is the arc the
    # pulley it wraps has turned through, and the arc is measured in the
    # frame the belt is drawn in, which is this arm's. The elbow pulley's
    # turn here is the elbow joint's own coordinate, so the belt reads it
    # directly; the drive pulley's turn here is `Art1`'s `drive` less the
    # shoulder, which is the same arc at the other end of the 20:117 pair.
    art3.elbow.drives(elbow_belt.travel, ratio=belt_travel(1.0))

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, PLACEMENT)
        # The forearm's own frame sits at the elbow, turned a quarter turn
        # about this frame's X so that its own Y runs along the elbow axis.
        self.art3.rotate(90.0, [1.0, 0.0, 0.0])
        self.art3.translate([0.0, ELBOW_ALONG_ARM + ELBOW_ACROSS_FOREARM,
                             ELBOW_ACROSS_ARM])
        # The belt is drawn in its own XY plane, which is this frame's, so
        # it needs only to be lifted onto its pulleys' land.
        self.elbow_belt.translate([0.0, 0.0, BELT_PLANE_Z])
