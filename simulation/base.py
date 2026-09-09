"""The base: the plinth, the electronics box, and the base motor.

Nothing here moves. The base carries the slewing bearing the whole arm
turns on, the geared motor whose pinion drives that turn, the control
board and its panel furniture, and the four fans that cool the drivers.

Every placement is the design's own, from `simulation.layout`.
"""

from solid_node.node import AssemblyNode
from solid_node.motion.ports import RotationalPort

from simulation import fasteners, layout, parts, placing
from simulation.hardware import CATALOGUE

GROUP = 'AssemblyBase'

#: The design's own instance labels, mapped to the attributes below.
PLACEMENT = {
    'BaseBot_BaseBot': 'base_bot',
    'BaseTop_BaseTop': 'base_top',
    'BaseBearingFix_BaseBearingFix': 'base_bearing_fix',
    'BaseBoxBody_BaseBoxBody': 'base_box_body',
    'BaseBoxCover_BaseBoxCover': 'base_box_cover',
    'Stepper_Nema17x40001': 'stepper_nema17x40',
    'Art1GearMotor_Art1GearMotor': 'art1_gear_motor',
    'OpticSensor001': 'optic_sensor',
    'Fan_40x40001': 'fan_40x40',
    'OnOffButton001': 'on_off_button',
    'ResetButton001': 'reset_button',
    'Fan_50x50001': 'fan_50x50_1',
    'Fan_50x50002': 'fan_50x50_2',
    'Fan_50x50003': 'fan_50x50_3',
    'Fan_50x50004': 'fan_50x50_4',
    'ArduinoMega001': 'arduino_mega',
    'JackDC001': 'jack_dc',
    'NutButton001': 'nut_button_1',
    'NutButton002': 'nut_button_2',
    'Bearing_16014zz001': 'bearing_16014zz',
}


#: Where the base pinion is put on its shaft, about its own Z: the centre
#: of the window in which it shares least with the ring gear it drives.
#: Measured, and recorded with the rest of the machine's gear pairs in
#: `simulation.layout.MESH`.
PHASES = {
    label: mesh.phase for label, mesh in layout.MESH.items()
    if label in PLACEMENT
}


#: The base's ring gear and the pinion that drives it, from the measured
#: pair in `simulation.layout.MESH`.
RING_TEETH = layout.MESH['Art1GearMotor_Art1GearMotor'].mate_teeth
PINION_TEETH = layout.MESH['Art1GearMotor_Art1GearMotor'].driver_teeth

#: How far the base pinion turns for one degree of the arm's yaw.
BASE_RATIO = RING_TEETH / PINION_TEETH

#: The base's yaw axis, in this frame.
YAW_AXIS = (0.0, 0.0, 1.0)

#: Which way each moving part's own +Z runs against that axis: the design
#: puts a pinion and the motor under it facing opposite ways, so the same
#: physical turn is one sign in one part's frame and the other in its
#: neighbour's.
PINION_SIGN = placing.axis_sign(
    layout.link(GROUP, 'Art1GearMotor_Art1GearMotor'), YAW_AXIS)
MOTOR_SIGN = placing.axis_sign(
    layout.link(GROUP, 'Stepper_Nema17x40001'), YAW_AXIS)


class Base(AssemblyNode):
    """The plinth the arm stands on.

    The base does not move: its one moving member is the base motor's
    pinion, `art1_gear_motor`, which turns as the arm above it yaws. An
    internal pair turns the same way, so the pinion follows the arm at the
    ring's ratio: fifty internal teeth in `Art1Bot` against its own ten.
    """

    #: The arm's yaw above this base, fed by the root from `art1`.
    yaw = RotationalPort(unit='deg')

    base_bot = parts.BaseBot()
    base_top = parts.BaseTop()
    base_bearing_fix = parts.BaseBearingFix()
    base_box_body = parts.BaseBoxBody()
    base_box_cover = parts.BaseBoxCover()
    stepper_nema17x40 = CATALOGUE['Stepper_Nema17x40']()
    art1_gear_motor = parts.Art1GearMotor()
    optic_sensor = CATALOGUE['OpticSensor']()
    fan_40x40 = CATALOGUE['Fan_40x40']()
    on_off_button = CATALOGUE['OnOffButton']()
    reset_button = CATALOGUE['ResetButton']()
    fan_50x50_1 = CATALOGUE['Fan_50x50']()
    fan_50x50_2 = CATALOGUE['Fan_50x50']()
    fan_50x50_3 = CATALOGUE['Fan_50x50']()
    fan_50x50_4 = CATALOGUE['Fan_50x50']()
    arduino_mega = CATALOGUE['ArduinoMega']()
    jack_dc = CATALOGUE['JackDC']()
    nut_button_1 = CATALOGUE['NutButton']()
    nut_button_2 = CATALOGUE['NutButton']()
    bearing_16014zz = CATALOGUE['Bearing_16014zz']()

    #: Every screw and nut the parts' own holes imply, derived
    #: rather than invented; see `simulation.fasteners`.
    screws = fasteners.declare_screws(GROUP)
    nuts = fasteners.declare_nuts(GROUP)

    #: An internal pair turns the same way, and the pinion turns as many
    #: times as the ring has teeth over its own. The motor's own shaft is
    #: the pinion's, so it reads the same turn through its port.
    yaw.drives(stepper_nema17x40.spin, ratio=BASE_RATIO * MOTOR_SIGN)

    def render(self):
        fasteners.place_all(self, GROUP)
        placing.place_from_design(self, GROUP, PLACEMENT, phases=PHASES)

    def simulate(self):
        # The pinion is a printed part placed by the design, so nothing
        # declares where its axis is; see README, "What still turns by
        # hand".
        self.art1_gear_motor.rotate(
            PINION_SIGN * BASE_RATIO * placing.bound(self.yaw),
            [0.0, 0.0, 1.0])
