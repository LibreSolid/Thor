"""The upper arm: a fork of two plates, and the belt run inside it.

`Art2` is the 160 mm link between the shoulder and the elbow, built as two
plates 136 mm apart with a union piece between them. Its shoulder end
carries the sixty-tooth internal ring the two shoulder pinions run in; its
elbow end carries the bearings the forearm turns on.

The elbow's belt runs the length of this fork, from a pulley on the
shoulder axis to the pulley on the elbow axis, over two sprung idlers. The
driving pulley is carried by `Art1`, not by this arm, so the belt holds the
elbow at a fixed angle in the machine frame while the shoulder swings:
`elbow` here is the forearm's **absolute** angle, and what this node
applies is its angle relative to the upper arm.
"""

from solid_node.node import AssemblyNode, RotationalPort, TranslationalPort

from simulation import fasteners, layout, parts, placing
from simulation.art3 import Art3
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyArt2'

#: Teeth on the internal ring cut into the shoulder plate.
SHOULDER_RING_TEETH = 60

#: The elbow axis in this frame, and the height of it above this frame's
#: origin: the design puts the two plates' elbow bearings 160.0 from the
#: shoulder along the arm and 68.0 out of the plate's own plane.
ELBOW_AXIS = (0.0, 0.0, 1.0)
ELBOW_ALONG_ARM = 160.0
ELBOW_ACROSS_ARM = 68.0

#: The elbow's own axis inside the forearm's frame: 81.5 from the Art3
#: origin, along that frame's own Y.
ELBOW_PIVOT = (0.0, 0.0, 81.5)
ELBOW_PIVOT_AXIS = (0.0, 1.0, 0.0)

#: The design places its belt loop flat, in a plane the pulleys are not in;
#: the model draws the belt from its pulleys instead. See
#: `simulation.flexibles` and design.md, Findings.
BELTS = ('GT2_Belt_Art3001',)

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


class Art2(AssemblyNode):
    """The upper arm and the forearm it carries."""

    #: The shoulder's own angle in the machine frame, degrees. This node
    #: does not turn itself by it; it needs it to work out how far the
    #: elbow has moved relative to the arm.
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

    art3 = Art3()

    #: Every screw and nut the parts' own holes imply, derived
    #: rather than invented; see `simulation.fasteners`.
    screws = fasteners.declare_screws(GROUP)
    nuts = fasteners.declare_nuts(GROUP)

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, PLACEMENT)
        # The forearm's own frame sits at the elbow, turned a quarter turn
        # about this frame's X so that its own Y runs along the elbow axis.
        self.art3.rotate(90.0, [1.0, 0.0, 0.0])
        self.art3.translate([0.0, ELBOW_ALONG_ARM + 81.5, ELBOW_ACROSS_ARM])

    def simulate(self):
        shoulder = placing.bound(self.shoulder)
        elbow = placing.bound(self.elbow)
        self.art3.yaw = self.yaw
        self.art3.wrist = self.wrist
        self.art3.tool = self.tool
        self.art3.grip = self.grip
        # `elbow` is the forearm's angle in the machine frame; what the
        # upper arm sees is the difference, because the belt that sets the
        # elbow is anchored below the shoulder rather than on this arm.
        placing.rotate_about(self.art3, elbow - shoulder,
                             ELBOW_PIVOT_AXIS, ELBOW_PIVOT)
