"""The forearm: the column it turns on, and the two motors that drive the wrist.

`Art4` is everything that turns with the forearm's own yaw: the
transmission column whose twenty-tooth gear the elbow motor's pinion
drives, the shells around it, the two wrist motors on their holders, and
the fork that carries the wrist.

The two motors do not drive one joint each. Each reaches, through its own
GT2 belt and a two-to-one pulley pair, one of the wrist's bevel pinions;
what the maker sees as wrist roll and tool roll is their sum and their
difference. Turning `art5` alone turns both motors the same way about the
wrist axis; turning `art6` alone turns them opposite ways. See
`simulation.art56` for the differential itself.

Measured on the design's own parts: the transmission column's gear has
twenty teeth to the elbow pinion's ten, on 27.85 mm centres against a
nominal 27.0, and the wrist's belt pulleys have forty teeth to the
motors' twenty.
"""

import math

from solid_node.node import AssemblyNode, RotationalPort, TranslationalPort

from simulation import fasteners, flexibles, layout, parts, placing
from simulation.art56 import Art56
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyArt4'

#: The wrist axis, in this frame: the line the fork's two bearings and the
#: 102 mm axle share, 111.5 above the forearm's own origin.
WRIST_AXIS = (0.0, 1.0, 0.0)
WRIST_HEIGHT = 111.5
#: How far the wrist's own frame is turned about Z inside this one.
WRIST_TURN = 90.0

#: Teeth on the transmission column's gear and on the elbow motor's pinion.
COLUMN_TEETH = 20
ELBOW_PINION_TEETH = 10

#: Teeth on the wrist belt pulleys and on the motor pulleys that drive them.
WRIST_PULLEY_TEETH = 40
MOTOR_PULLEY_TEETH = 20

#: How far a motor turns for one turn of the wrist pulley it drives.
BELT_RATIO = WRIST_PULLEY_TEETH / MOTOR_PULLEY_TEETH

#: The design's own belt loops are not placed on their pulleys; the model
#: draws each belt from the pulleys it runs on instead. See
#: `simulation.flexibles` and design.md, Findings.
BELTS = ('Belt_GT2-208mm001', 'Belt_GT2-208mm002')

#: Where each belt's own plane stands in this frame. A belt is drawn in
#: its own XY with the motor pulley on +X, so a quarter turn about X
#: stands it up; the second belt is the same shape turned end for end
#: about Z, because the assembly puts its motor pulley on -X. The motor
#: pulley axis crosses this frame at x = +/-24.0, z = 33.6 and the wrist
#: pulley on the fork's axis 77.9 above it, and the plane is the middle of
#: the land the two pulleys share.
BELT_PLANE_Y = -flexibles.WRIST_BELT_PLANE
BELT_PLANES = (
    ('wrist_belt_1', 0.0, (0.0, -BELT_PLANE_Y, 33.6)),
    ('wrist_belt_2', 180.0, (0.0, BELT_PLANE_Y, 33.6)),
)

PLACEMENT = {
    'Art4TransmissionColumn_Art4TransmissionColumn':
        'art4_transmission_column',
    'Art4BodyBot_Art4BodyBot': 'art4_body_bot',
    'Art4Body_Art4Body': 'art4_body',
    'Art4BodyFan_Art4BodyFan': 'art4_body_fan_1',
    'Art4BodyFan_Art4BodyFan001': 'art4_body_fan_2',
    'Art56MotorHolderA_Art56MotorHolderA': 'art56_motor_holder_a_1',
    'Art56MotorHolderA_Art56MotorHolderA001': 'art56_motor_holder_a_2',
    'Stepper_Nema17x34001': 'wrist_motor_1',
    'Stepper_Nema17x34002': 'wrist_motor_2',
    'Art56MotorHolderB_Art56MotorHolderB': 'art56_motor_holder_b_1',
    'Art56MotorHolderB_Art56MotorHolderB001': 'art56_motor_holder_b_2',
    'Pulley_GT2x20001': 'motor_pulley_1',
    'Pulley_GT2x20002': 'motor_pulley_2',
    'Bearing_625ZZ001': 'bearing_625zz_1',
    'Bearing_625ZZ002': 'bearing_625zz_2',
    'Fan_40x40001': 'fan_40x40_1',
    'Fan_40x40002': 'fan_40x40_2',
    'Art4BearingFix_Art4BearingFix': 'art4_bearing_fix_1',
    'Art4BearingFix_Art4BearingFix001': 'art4_bearing_fix_2',
    'Shaft_5x102mm001': 'wrist_axle',
    'Art4Optodisk_Art4Optodisk': 'art4_optodisk',
    'MicroEndstop001': 'micro_endstop',
    'M8Connector001': 'm8_connector',
}

#: Which motor drives which wrist pulley, read off the assembly: motor 2
#: sits on the -y side and its pulley shares the belt band with the wrist
#: pulley the design calls M005; motor 1 is the +y pair.
MOTOR_DRIVES = {
    'Pulley_GT2x20001': ('motor_pulley_1', 'Stepper_Nema17x34002'),
    'Pulley_GT2x20002': ('motor_pulley_2', 'Stepper_Nema17x34001'),
}


def belt_travel(turn):
    """How far a wrist belt runs for a turn of its wrist pulley, mm.

    The belt is a rack wrapped on the forty-tooth pulley's pitch circle,
    so what it feeds is that circle's arc.
    """
    # Written as a plain multiplication rather than through
    # `math.radians`, because under `solid build` the turn is a symbolic
    # expression and the C library's radians() takes only floats.
    return turn * (math.pi / 180.0) * flexibles.pitch_radius(
        flexibles.WRIST_DRIVEN_TEETH)


class Art4(AssemblyNode):
    """The forearm and the wrist it carries."""

    #: The wrist's roll about the fork's axis, degrees.
    wrist = RotationalPort(unit='deg')
    #: The tool's roll about the wrist output axis, degrees.
    tool = RotationalPort(unit='deg')
    #: The gripper's clear opening, mm.
    grip = TranslationalPort(unit='mm')

    art4_transmission_column = parts.Art4TransmissionColumn()
    art4_body_bot = parts.Art4BodyBot()
    art4_body = parts.Art4Body()
    art4_body_fan_1 = parts.Art4BodyFan()
    art4_body_fan_2 = parts.Art4BodyFan()
    art56_motor_holder_a_1 = parts.Art56MotorHolderA()
    art56_motor_holder_a_2 = parts.Art56MotorHolderA()
    art56_motor_holder_b_1 = parts.Art56MotorHolderB()
    art56_motor_holder_b_2 = parts.Art56MotorHolderB()
    wrist_motor_1 = CATALOGUE['Stepper_Nema17x34']()
    wrist_motor_2 = CATALOGUE['Stepper_Nema17x34']()
    motor_pulley_1 = CATALOGUE['Pulley_GT2x20']()
    motor_pulley_2 = CATALOGUE['Pulley_GT2x20']()
    bearing_625zz_1 = CATALOGUE['Bearing_625ZZ']()
    bearing_625zz_2 = CATALOGUE['Bearing_625ZZ']()
    fan_40x40_1 = CATALOGUE['Fan_40x40']()
    fan_40x40_2 = CATALOGUE['Fan_40x40']()
    art4_bearing_fix_1 = parts.Art4BearingFix()
    art4_bearing_fix_2 = parts.Art4BearingFix()
    wrist_axle = CATALOGUE['Shaft_5x102mm']()
    art4_optodisk = parts.Art4Optodisk()
    micro_endstop = CATALOGUE['MicroEndstop']()
    m8_connector = CATALOGUE['M8Connector']()

    wrist_belt_1 = flexibles.WristBelt()
    wrist_belt_2 = flexibles.WristBelt()

    art56 = Art56()

    #: Every screw and nut the parts' own holes imply, derived
    #: rather than invented; see `simulation.fasteners`.
    screws = fasteners.declare_screws(GROUP)
    nuts = fasteners.declare_nuts(GROUP)

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, PLACEMENT)
        # The wrist sits on the fork's axis, turned a quarter turn so that
        # its own +X runs along this frame's +Y. Rotation before
        # translation, as everywhere else in this model.
        self.art56.rotate(WRIST_TURN, [0.0, 0.0, 1.0])
        self.art56.translate([0.0, 0.0, WRIST_HEIGHT])
        for attribute, turn, offset in BELT_PLANES:
            belt = getattr(self, attribute)
            belt.rotate(90.0, [1.0, 0.0, 0.0])
            if turn:
                belt.rotate(turn, [0.0, 0.0, 1.0])
            belt.translate(list(offset))

    def pinion_turns(self, wrist, tool):
        """Each wrist pinion's absolute turn about the wrist axis.

        The pinion the design puts on -x of the wrist frame gets the sum
        and the one on +x the difference: that is the differential, seen
        from outside.
        """
        spin = self.art56.pinion_spin(tool)
        return wrist + spin, wrist - spin

    def simulate(self):
        wrist = placing.bound(self.wrist)
        tool = placing.bound(self.tool)
        self.art56.tool = self.tool
        self.art56.grip = self.grip
        # The wrist frame's own +X is this frame's +Y, and its origin is on
        # the fork's axis, so the roll is a turn about its own X.
        self.art56.rotate(wrist, [1.0, 0.0, 0.0])
        left, right = self.pinion_turns(wrist, tool)
        for label, turn in (('Pulley_GT2x20001', left),
                            ('Pulley_GT2x20002', right)):
            pulley_attribute, motor_label = MOTOR_DRIVES[label]
            # An open belt turns both its pulleys the same way about the
            # same axis; the pulley signs differ only because the design
            # places the two of them facing opposite ways.
            about_axis = BELT_RATIO * turn
            pulley_sign = placing.axis_sign(layout.link(GROUP, label),
                                            WRIST_AXIS)
            getattr(self, pulley_attribute).rotate(
                pulley_sign * about_axis, [0.0, 0.0, 1.0])
            motor_sign = placing.axis_sign(layout.link(GROUP, motor_label),
                                           WRIST_AXIS)
            motor = getattr(self, PLACEMENT[motor_label])
            motor.spin = motor_sign * about_axis
        # Each belt feeds the arc its own wrist pulley turns through --
        # about the wrist axis, and in this frame, which is what makes it
        # the pulley's turn relative to the belt's own plane.
        self.wrist_belt_1.travel = belt_travel(left)
        self.wrist_belt_2.travel = belt_travel(right)
