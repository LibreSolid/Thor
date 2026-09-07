"""The components Thor is built from but does not draw.

The design's FreeCAD assembly places motors, bearings, pulleys, shafts,
magnets, fans, sensors, a servo and the control board, but publishes none
of them as printable parts: they are bought. They are drawn here from
catalogue dimensions, in the frames those FreeCAD components use, so a
placement transcribed from the assembly lands them correctly without any
correction. `docs/measurements.md` records the frames and where each
number was read.

Every class is exact, so bearing seats, motor faces and pulley bores can be
argued about on solids.
"""

import cadquery as cq

from solid_node.node import AssemblyNode, CadQueryNode, RotationalPort
from solid_node.parameters import Count, Length, Ratio

from simulation import materials, placing

#: Half the diagonal across a NEMA 17 body once its corners are cut, mm.
#: Measured on the design's own component: the body is 42.30 square and the
#: cut corners leave a 53.84 mm diagonal.
NEMA17_SIDE = 42.30
NEMA17_CORNER_RADIUS = 26.92
#: The stack between the end caps is very slightly narrower.
NEMA17_STACK_SIDE = 42.00
NEMA17_STACK_CORNER_RADIUS = 25.10
NEMA17_CAP_LENGTH = 8.0


def _nema_section(side, corner_radius):
    """A NEMA body cross-section: a square with its corners cut to a circle."""
    return (cq.Workplane('XY').rect(side, side).extrude(1)
            .intersect(cq.Workplane('XY').circle(corner_radius).extrude(1)))


class MotorShaft(CadQueryNode):
    """A motor's output shaft with its flat, its root at the origin.

    A separate part because it is the only piece of a motor that moves:
    the body is bolted to its holder and the shaft turns inside it.
    """

    color = materials.STEEL

    diameter = Length(5.0, min=0)
    length = Length(20.0, min=0)
    #: Depth of the flat milled on the shaft, measured from the far side.
    flat = Length(0.5, min=0)

    def render(self):
        shaft = (cq.Workplane('XY').circle(self.diameter / 2)
                 .extrude(self.length))
        if self.flat > 0:
            cut = (cq.Workplane('XY')
                   .box(self.diameter, self.diameter, self.length,
                        centered=(False, True, False))
                   .translate((self.diameter / 2 - self.flat, 0, 0)))
            shaft = shaft.cut(cut)
        return shaft


class StepperBody(CadQueryNode):
    """A NEMA 17 body with its pilot boss, and nothing that turns.

    The origin is the **back** face and +Z runs toward the shaft, which is
    how the design's own component is drawn: its flange face is therefore
    at `body_length`, and a holder placed at that height in the assembly
    lands on it. Measured on the design's `Stepper_Nema17x34`: body 34.0
    to the flange and a Ø22 pilot boss 2.0 deep.
    """

    color = materials.MOTOR_BODY

    body_length = Length(34.0, min=0)
    boss_diameter = Length(22.0, min=0)
    boss_length = Length(2.0, min=0)

    def render(self):
        cap = NEMA17_CAP_LENGTH
        stack = self.body_length - 2 * cap
        body = (_nema_section(NEMA17_SIDE, NEMA17_CORNER_RADIUS)
                .faces('>Z').wires().toPending()
                .workplane().extrude(cap - 1))
        body = body.union(
            _nema_section(NEMA17_STACK_SIDE, NEMA17_STACK_CORNER_RADIUS)
            .faces('>Z').wires().toPending().workplane()
            .extrude(stack - 1).translate((0, 0, cap)))
        body = body.union(
            _nema_section(NEMA17_SIDE, NEMA17_CORNER_RADIUS)
            .faces('>Z').wires().toPending().workplane()
            .extrude(cap - 1).translate((0, 0, self.body_length - cap)))
        boss = (cq.Workplane('XY').circle(self.boss_diameter / 2)
                .extrude(self.boss_length)
                .translate((0, 0, self.body_length)))
        return body.union(boss)


class Stepper(AssemblyNode):
    """A NEMA 17 stepper: a fixed body and a shaft that turns in it.

    `spin` is the shaft's rotation about its own axis, in degrees. The
    body never moves relative to whatever holds it.
    """

    body_length = Length(34.0, min=0)
    boss_diameter = Length(22.0, min=0)
    boss_length = Length(2.0, min=0)
    shaft_diameter = Length(5.0, min=0)
    shaft_length = Length(20.0, min=0)
    shaft_flat = Length(0.5, min=0)

    spin = RotationalPort(unit='deg')

    body = StepperBody(body_length=body_length,
                       boss_diameter=boss_diameter,
                       boss_length=boss_length)
    shaft = MotorShaft(diameter=shaft_diameter, length=shaft_length,
                       flat=shaft_flat)

    def render(self):
        self.shaft.translate([0.0, 0.0, self.body_length])

    def simulate(self):
        self.shaft.rotate(placing.bound(self.spin), [0.0, 0.0, 1.0])


class GearBoxBody(CadQueryNode):
    """A NEMA 17 with a planetary gearbox on its face, and no shaft.

    Measured on the design's `Nema17_GearBox`: a 33 mm NEMA 17 body, a
    7 mm adapter plate at 41.5 square, a Ø36 gearbox barrel 20.3 mm long,
    then 18 mm of Ø6 output shaft, which is a part of its own.
    """

    color = materials.MOTOR_BODY

    body_length = Length(33.0, min=0)
    plate_length = Length(7.0, min=0)
    plate_side = Length(41.5, min=0)
    barrel_diameter = Length(36.0, min=0)
    barrel_length = Length(20.3, min=0)

    def render(self):
        cap = NEMA17_CAP_LENGTH
        stack = self.body_length - 2 * cap
        body = (_nema_section(NEMA17_SIDE, NEMA17_CORNER_RADIUS)
                .faces('>Z').wires().toPending().workplane().extrude(cap - 1))
        body = body.union(
            _nema_section(NEMA17_STACK_SIDE, NEMA17_STACK_CORNER_RADIUS)
            .faces('>Z').wires().toPending().workplane()
            .extrude(stack - 1).translate((0, 0, cap)))
        body = body.union(
            _nema_section(NEMA17_SIDE, NEMA17_CORNER_RADIUS)
            .faces('>Z').wires().toPending().workplane()
            .extrude(cap - 1).translate((0, 0, self.body_length - cap)))
        plate = (_nema_section(self.plate_side, NEMA17_CORNER_RADIUS)
                 .faces('>Z').wires().toPending().workplane()
                 .extrude(self.plate_length - 1)
                 .translate((0, 0, self.body_length)))
        barrel_z = self.body_length + self.plate_length
        barrel = (cq.Workplane('XY').circle(self.barrel_diameter / 2)
                  .extrude(self.barrel_length).translate((0, 0, barrel_z)))
        return body.union(plate).union(barrel)


class GearedStepper(AssemblyNode):
    """A NEMA 17 with a planetary gearbox, and a shaft that turns in it.

    `spin` is the output shaft's rotation about its own axis, in degrees.
    """

    body_length = Length(33.0, min=0)
    plate_length = Length(7.0, min=0)
    plate_side = Length(41.5, min=0)
    barrel_diameter = Length(36.0, min=0)
    barrel_length = Length(20.3, min=0)
    shaft_diameter = Length(6.0, min=0)
    shaft_length = Length(18.0, min=0)
    shaft_flat = Length(0.5, min=0)

    output_z = body_length + plate_length + barrel_length

    spin = RotationalPort(unit='deg')

    body = GearBoxBody(body_length=body_length, plate_length=plate_length,
                       plate_side=plate_side,
                       barrel_diameter=barrel_diameter,
                       barrel_length=barrel_length)
    shaft = MotorShaft(diameter=shaft_diameter, length=shaft_length,
                       flat=shaft_flat)

    def render(self):
        self.shaft.translate([0.0, 0.0, self.output_z])

    def simulate(self):
        self.shaft.rotate(placing.bound(self.spin), [0.0, 0.0, 1.0])


class BallBearing(CadQueryNode):
    """A shielded ball bearing, bore centred on the origin, one face at z=0.

    Drawn as the three things a builder can see: the inner ring, the outer
    ring, and the shield between them. A flanged bearing carries its flange
    at the z=0 end, as `Bearing_MF84ZZ` is drawn in the design.
    """

    color = materials.STEEL

    bore = Length(min=0)
    outer_diameter = Length(min=0)
    width = Length(min=0)
    #: Zero for an unflanged bearing.
    flange_diameter = Length(0.0, min=0)
    flange_width = Length(0.6, min=0)
    #: Fraction of the ring gap each race takes; the rest is the shield.
    race_fraction = Ratio(0.28, min=0, max=0.5)

    def render(self):
        r_bore = self.bore / 2
        r_out = self.outer_diameter / 2
        gap = r_out - r_bore
        race = gap * self.race_fraction
        inner = (cq.Workplane('XY').circle(r_bore + race).circle(r_bore)
                 .extrude(self.width))
        outer = (cq.Workplane('XY').circle(r_out).circle(r_out - race)
                 .extrude(self.width))
        shield = (cq.Workplane('XY').circle(r_out - race).circle(r_bore + race)
                  .extrude(self.width - 0.4).translate((0, 0, 0.2)))
        part = inner.union(outer).union(shield)
        if self.flange_diameter > 0:
            flange = (cq.Workplane('XY').circle(self.flange_diameter / 2)
                      .circle(r_out - race).extrude(self.flange_width))
            part = part.union(flange)
        return part


class BearingBall(CadQueryNode):
    """One loose ball of the printed slewing race in the forearm.

    The design arrays thirty-six Ø6 balls on a 35 mm pitch radius between
    `Art4BearingRing` and its seat.
    """

    color = materials.BRIGHT_STEEL

    diameter = Length(6.0, min=0)

    def render(self):
        return cq.Workplane('XY').sphere(self.diameter / 2)


class Shaft(CadQueryNode):
    """A ground steel rod, one end at the origin, running along +Z."""

    color = materials.STEEL

    diameter = Length(5.0, min=0)
    length = Length(min=0)

    def render(self):
        return (cq.Workplane('XY').circle(self.diameter / 2)
                .extrude(self.length))


class PulleyGT2(CadQueryNode):
    """An aluminium GT2 toothed pulley, one flange face at z=0.

    GT2's tooth pitch is 2 mm, so the pitch diameter is `teeth * 2 / pi`
    and the tooth tips stand 0.254 mm inside it. Measured against the
    design's own components: a 20-tooth pulley's tips read 6.07 against a
    computed 6.11, and a 40-tooth pulley's read 12.49 against 12.47.
    """

    color = materials.ALUMINIUM

    teeth = Count(20, min=8)
    flange_diameter = Length(18.0, min=0)
    flange_width = Length(1.0, min=0)
    belt_width = Length(9.0, min=0)
    hub_diameter = Length(18.0, min=0)
    hub_length = Length(4.6, min=0)
    bore = Length(5.0, min=0)

    #: GT2 pitch, mm.
    tooth_pitch = 2.0
    #: How far the tooth tips stand inside the pitch circle, mm.
    tip_offset = 0.254

    pitch_radius = teeth * tooth_pitch / 3.141592653589793 / 2
    tip_radius = pitch_radius - tip_offset

    def render(self):
        flange = (cq.Workplane('XY').circle(self.flange_diameter / 2)
                  .extrude(self.flange_width))
        land = (cq.Workplane('XY').circle(self.tip_radius)
                .extrude(self.belt_width)
                .translate((0, 0, self.flange_width)))
        hub_z = self.flange_width + self.belt_width
        hub = (cq.Workplane('XY').circle(self.hub_diameter / 2)
               .extrude(self.hub_length).translate((0, 0, hub_z)))
        total = hub_z + self.hub_length
        bore = (cq.Workplane('XY').circle(self.bore / 2).extrude(total + 2)
                .translate((0, 0, -1)))
        return flange.union(land).union(hub).cut(bore)


class ShaftCollar(CadQueryNode):
    """A clamping shaft collar, centred on the origin.

    Measured on the design's `Collar5mm`: Ø10 by 5 wide on a Ø5 bore, with
    a clamping boss standing 0.87 mm proud on +Y.
    """

    color = materials.ALUMINIUM

    bore = Length(5.0, min=0)
    outer_diameter = Length(10.0, min=0)
    width = Length(5.0, min=0)
    boss_reach = Length(5.87, min=0)
    boss_width = Length(6.0, min=0)

    def render(self):
        body = (cq.Workplane('XY').circle(self.outer_diameter / 2)
                .extrude(self.width).translate((0, 0, -self.width / 2)))
        boss = (cq.Workplane('XY')
                .box(self.boss_width, self.boss_reach, self.width * 0.7,
                     centered=(True, False, True)))
        bore = (cq.Workplane('XY').circle(self.bore / 2)
                .extrude(self.width + 2).translate((0, 0, -self.width / 2 - 1)))
        return body.union(boss).cut(bore)


class Magnet(CadQueryNode):
    """A neodymium disc magnet, one face at z=0."""

    color = materials.MAGNET

    diameter = Length(8.0, min=0)
    thickness = Length(1.0, min=0)

    def render(self):
        return (cq.Workplane('XY').circle(self.diameter / 2)
                .extrude(self.thickness))


class Fan(CadQueryNode):
    """An axial cooling fan, centred on its axis with one face at z=0."""

    color = materials.FAN

    side = Length(40.0, min=0)
    thickness = Length(10.0, min=0)
    #: The bore the blades run in.
    aperture = Length(37.0, min=0)
    hub_diameter = Length(16.0, min=0)

    def render(self):
        frame = (cq.Workplane('XY').box(self.side, self.side, self.thickness,
                                        centered=(True, True, False))
                 .cut(cq.Workplane('XY').circle(self.aperture / 2)
                      .extrude(self.thickness)))
        hub = (cq.Workplane('XY').circle(self.hub_diameter / 2)
               .extrude(self.thickness * 0.7))
        # The strut reaches the frame it holds. Stopping it a half
        # millimetre short of the bore, as it did, leaves the hub a second
        # body floating in the middle of the fan -- which is what
        # assertNoDisconnectedSolids is for. It never leaves the square
        # frame's own envelope, so it cannot foul the shroud.
        strut = (cq.Workplane('XY')
                 .box(self.side, 2.0, 1.6,
                      centered=(True, True, False))
                 .translate((0, 0, self.thickness * 0.35)))
        return frame.union(hub).union(strut)


class ServoHorn(CadQueryNode):
    """The servo's round horn, its hub face at z=0 and the disc below it.

    Measured on the design's `ServomotorWheelHorn`: a Ø21 disc 2.3 thick
    with a Ø8.86 hub standing 3.2 above it.
    """

    color = materials.PLASTIC_BLACK

    disc_diameter = Length(21.0, min=0)
    disc_thickness = Length(2.3, min=0)
    hub_diameter = Length(8.86, min=0)
    hub_length = Length(3.2, min=0)

    def render(self):
        disc = (cq.Workplane('XY').circle(self.disc_diameter / 2)
                .extrude(self.disc_thickness))
        hub = (cq.Workplane('XY').circle(self.hub_diameter / 2)
               .extrude(self.hub_length)
               .translate((0, 0, self.disc_thickness)))
        return disc.union(hub)


class ServoMotor(CadQueryNode):
    """A standard-size hobby servo.

    Drawn in the design's own frame, which puts the origin on the horn's
    axis rather than on the servo body: the body sits 21.0 to 61.6 away
    along -Y, the mounting tabs reach from -14.0 to -68.6, and the output
    boss stands at (4.0, -31.0). Measured on the design's `Servomotor`.
    """

    color = materials.MOTOR_BODY

    body_length = Length(40.6, min=0)
    body_width = Length(19.8, min=0)
    body_height = Length(40.48, min=0)
    tab_length = Length(54.6, min=0)
    tab_thickness = Length(2.5, min=0)
    #: Distance from the origin to the near face of the body, along -Y.
    body_offset = Length(21.0, min=0)
    #: Height of the tab plane below the origin.
    tab_z = Length(11.07, min=0)
    boss_diameter = Length(11.2, min=0)
    boss_height = Length(5.35, min=0)
    boss_x = Length(4.0)
    boss_y = Length(-31.0)

    def render(self):
        y0 = -self.body_offset - self.body_length
        body = (cq.Workplane('XY')
                .box(self.body_width, self.body_length, self.body_height,
                     centered=(True, False, False))
                .translate((4.0, y0, -self.body_height + 5.35 - 4.0)))
        tab_y = -(self.body_offset + self.body_length + self.tab_length) / 2
        tabs = (cq.Workplane('XY')
                .box(self.body_width, self.tab_length, self.tab_thickness,
                     centered=(True, True, True))
                .translate((4.0, y0 + self.body_length / 2, -self.tab_z)))
        boss = (cq.Workplane('XY').circle(self.boss_diameter / 2)
                .extrude(self.boss_height)
                .translate((self.boss_x, self.boss_y, 0)))
        return body.union(tabs).union(boss)


class OptoInterrupter(CadQueryNode):
    """A slotted optical switch on its little carrier board.

    An envelope: the design's own component is a supplier model and the
    model needs only where it is and how much room it takes. Measured on
    `OpticSensor`: a 35.0 x 11.0 x 2.2 board carrying a 20.5 x 10.2 fork
    9.3 tall.
    """

    color = materials.PCB

    board_length = Length(35.0, min=0)
    board_width = Length(11.0, min=0)
    board_thickness = Length(2.2, min=0)
    fork_length = Length(20.5, min=0)
    fork_width = Length(10.2, min=0)
    fork_height = Length(9.3, min=0)
    #: The gap the optical disc passes through.
    slot_width = Length(6.0, min=0)

    def render(self):
        board = (cq.Workplane('XY')
                 .box(self.board_length, self.board_width,
                      self.board_thickness, centered=(True, True, False)))
        fork = (cq.Workplane('XY')
                .box(self.fork_length, self.fork_width, self.fork_height,
                     centered=(True, True, False))
                .translate((0.23, -0.16, self.board_thickness)))
        slot = (cq.Workplane('XY')
                .box(self.slot_width, self.fork_width + 2,
                     self.fork_height, centered=(True, True, False))
                .translate((0.23, -0.16,
                            self.board_thickness + self.fork_height * 0.35)))
        return board.union(fork).cut(slot)


class MicroEndstop(CadQueryNode):
    """A micro switch with its lever, in the design's own corner frame.

    Measured on `MicroEndstot`: a 12.6 x 5.8 x 9.4 body with a 12.4 long
    lever, its origin at the body's near bottom corner.
    """

    color = materials.PLASTIC_BLACK

    body_length = Length(12.6, min=0)
    body_width = Length(5.8, min=0)
    body_height = Length(9.4, min=0)
    pin_length = Length(11.2, min=0)
    pin_drop = Length(3.2, min=0)
    lever_thickness = Length(0.4, min=0)

    def render(self):
        body = (cq.Workplane('XY')
                .box(self.body_length, self.body_width, self.body_height,
                     centered=(False, False, False)))
        pins = (cq.Workplane('XY')
                .box(self.pin_length, 2.8, self.pin_drop,
                     centered=(False, False, False))
                .translate((0.7, 1.5, -self.pin_drop)))
        lever = (cq.Workplane('XY')
                 .box(9.0, 4.0, self.lever_thickness,
                      centered=(False, False, False))
                 .rotate((3.9, 0, 6.95), (3.9, 1, 6.95), 14.0)
                 .translate((3.9, 0.9, 6.95)))
        return body.union(pins).union(lever)


class ArduinoMega(CadQueryNode):
    """The control board, as its envelope and mounting outline.

    Measured on the design's `ArduinoMega`: 108.8 x 53.2 board, standing
    1.63 below and 13.18 above its own datum, with the origin 58.07 from
    the near end.
    """

    color = materials.PCB

    length = Length(108.8, min=0)
    width = Length(53.2, min=0)
    board_thickness = Length(1.63, min=0)
    component_height = Length(13.18, min=0)

    def render(self):
        board = (cq.Workplane('XY')
                 .box(self.length, self.width, self.board_thickness,
                      centered=(True, True, False))
                 .translate((-3.67, 0, -self.board_thickness)))
        # The tallest thing on the board, not a slab the size of it: the
        # box the design puts it in is cut for the connectors, and a solid
        # block the width of the board fouls its walls.
        block = (cq.Workplane('XY')
                 .box(self.length * 0.55, self.width * 0.55,
                      self.component_height, centered=(True, True, False))
                 .translate((-3.67, 0, 0)))
        return board.union(block)


class PanelSwitch(CadQueryNode):
    """A 16 mm panel switch, its bezel face at z=0 and its body below.

    One class covers both switches the design fits: the latching on/off
    button reaches 36 mm behind the panel, the momentary reset button
    38.6 mm, and each carries a bezel 1.5 to 2.0 proud.
    """

    color = materials.PLASTIC_BLACK

    bezel_diameter = Length(17.8, min=0)
    bezel_height = Length(1.5, min=0)
    thread_diameter = Length(16.0, min=0)
    body_diameter = Length(15.8, min=0)
    body_length = Length(36.0, min=0)
    terminal_width = Length(8.7, min=0)

    def render(self):
        bezel = (cq.Workplane('XY').circle(self.bezel_diameter / 2)
                 .extrude(self.bezel_height))
        thread = (cq.Workplane('XY').circle(self.thread_diameter / 2)
                  .extrude(11.0).translate((0, 0, -11.0)))
        body = (cq.Workplane('XY').circle(self.body_diameter / 2)
                .extrude(self.body_length - 17.0)
                .translate((0, 0, -(self.body_length - 6.0))))
        tail = (cq.Workplane('XY')
                .box(self.terminal_width, 1.78, 6.0,
                     centered=(True, True, False))
                .translate((0, 0, -self.body_length)))
        return bezel.union(thread).union(body).union(tail)


class PanelPushButton(CadQueryNode):
    """The momentary reset button, which the design draws lying along -Y.

    Same 16 mm panel switch as `PanelSwitch`, but its component is modelled
    with the body running away from the bezel along -Y rather than -Z, so
    it is drawn that way here and the assembly's placement lands it
    unchanged. Measured on `ResetButton`: bezel at y=+2.0, body reaching
    to y=-38.6, envelope 18.9 across; the bezel is 2.0 proud.
    """

    color = materials.PLASTIC_BLACK

    bezel_diameter = Length(18.9, min=0)
    bezel_height = Length(2.0, min=0)
    thread_diameter = Length(16.0, min=0)
    body_diameter = Length(15.8, min=0)
    body_length = Length(38.6, min=0)
    terminal_width = Length(8.7, min=0)

    def render(self):
        switch = PanelSwitch(
            bezel_diameter=self.bezel_diameter,
            bezel_height=self.bezel_height,
            thread_diameter=self.thread_diameter,
            body_diameter=self.body_diameter,
            body_length=self.body_length,
            terminal_width=self.terminal_width).render()
        return switch.rotate((0, 0, 0), (1, 0, 0), -90)


class DcJack(CadQueryNode):
    """A 2.1 mm panel-mount barrel jack, in the design's own frame."""

    color = materials.PLASTIC_BLACK

    width = Length(11.0, min=0)
    height = Length(12.7, min=0)
    reach = Length(18.2, min=0)

    def render(self):
        return (cq.Workplane('XY')
                .box(self.width, self.reach, self.height,
                     centered=(True, False, True))
                .translate((0, -22.0, 0)))


class PanelNut(CadQueryNode):
    """The knurled nut that holds a 16 mm panel switch, centred on z=0."""

    color = materials.STEEL

    across_flats = Length(19.0, min=0)
    outer_diameter = Length(21.94, min=0)
    thickness = Length(3.0, min=0)
    bore = Length(16.2, min=0)

    def render(self):
        body = (cq.Workplane('XY').circle(self.outer_diameter / 2)
                .extrude(self.thickness)
                .translate((0, 0, -self.thickness / 2))
                .intersect(cq.Workplane('XY')
                           .box(self.outer_diameter * 2, self.across_flats,
                                self.thickness)))
        bore = (cq.Workplane('XY').circle(self.bore / 2)
                .extrude(self.thickness + 2)
                .translate((0, 0, -self.thickness / 2 - 1)))
        return body.cut(bore)


class M8Connector(CadQueryNode):
    """An M8 panel connector, in the design's own frame."""

    color = materials.PLASTIC_BLACK

    barrel_diameter = Length(10.0, min=0)
    body_length = Length(21.0, min=0)
    thread_diameter = Length(9.9, min=0)
    thread_length = Length(2.2, min=0)
    flat_width = Length(10.0, min=0)

    def render(self):
        body = (cq.Workplane('YZ').circle(self.barrel_diameter / 2)
                .extrude(self.body_length)
                .translate((-18.0, 0, 0)))
        thread = (cq.Workplane('YZ').circle(self.thread_diameter / 2)
                  .extrude(self.thread_length)
                  .translate((-17.2, 0, 0)))
        # The design's own connector is flatted on both sides to 10.0 wide.
        flats = (cq.Workplane('XY')
                 .box(self.body_length + 4, self.flat_width,
                      self.barrel_diameter + 2)
                 .translate((-8.0, 0, 0)))
        return body.union(thread).intersect(flats)


class BearingBalls(AssemblyNode):
    """The loose balls of the printed slewing race in the forearm.

    The design arrays thirty-six Ø6 balls on a 35 mm pitch radius about the
    forearm's yaw axis, running between `Art4BearingRing` and the seat cut
    into `Art3Body`. They are a component, not a printed part: `count` and
    `pitch_radius` are the design's own array values.
    """

    count = Count(36, min=1)
    pitch_radius = Length(35.0, min=0)
    diameter = Length(6.0, min=0)

    balls = BearingBall(diameter=diameter).repeat(count)

    def render(self):
        import math
        step = 360.0 / int(self.count)
        for index, ball in enumerate(self.balls):
            angle = math.radians(index * step)
            ball.translate([self.pitch_radius * math.cos(angle),
                            self.pitch_radius * math.sin(angle), 0.0])


# --- the catalogue --------------------------------------------------------
#
# One factory per component the design's assembly places, keyed by the label
# that component carries in the FreeCAD documents. `simulation.layout`
# records that label on every bought instance, so a sub-assembly names the
# component and never restates its dimensions.
#
# The two GT2 belts the design places are not here: a belt is a flexible
# part whose shape follows its pulleys, and it lives in
# `simulation.flexibles`.

def _stepper_nema17x34():
    return Stepper(body_length=34.0, shaft_length=20.0)


def _stepper_nema17x40():
    return Stepper(body_length=40.0, shaft_length=20.1)


def _nema17_gearbox():
    return GearedStepper()


def _bearing_625zz():
    return BallBearing(bore=5.0, outer_diameter=16.0, width=5.0)


def _bearing_mf84zz():
    return BallBearing(bore=4.0, outer_diameter=8.0, width=3.0,
                       flange_diameter=9.2, flange_width=0.6)


def _bearing_16014zz():
    return BallBearing(bore=70.0, outer_diameter=110.0, width=13.0)


def _pulley_gt2x20():
    return PulleyGT2(teeth=20, flange_diameter=18.0, belt_width=9.0,
                     hub_diameter=18.0, hub_length=4.6, bore=5.0)


def _pulley_gt2x40_m4():
    return PulleyGT2(teeth=40, flange_diameter=28.0, flange_width=1.0,
                     belt_width=7.5, hub_diameter=18.0, hub_length=8.5,
                     bore=4.0)


CATALOGUE = {
    'Stepper_Nema17x34': _stepper_nema17x34,
    'Stepper_Nema17x40': _stepper_nema17x40,
    'Nema17_GearBox': _nema17_gearbox,
    'Bearing_625ZZ': _bearing_625zz,
    'Bearing_MF84ZZ': _bearing_mf84zz,
    'Bearing_16014zz': _bearing_16014zz,
    'BearingBalls': BearingBalls,
    'Pulley_GT2x20': _pulley_gt2x20,
    # The design's modified pulley differs from the stock one only in where
    # its grub screw is drawn, and that screw is drawn 5.3 mm clear of the
    # pulley body in both components (see design.md, Findings): the model
    # draws the pulley and omits the detached screw.
    'Pulley_GT2x20_Modified': _pulley_gt2x20,
    'GT2x40PulleyM4': _pulley_gt2x40_m4,
    '4x14mm': lambda: Shaft(diameter=4.0, length=14.0),
    '5x14.5mm': lambda: Shaft(diameter=5.0, length=14.5),
    '5x32mm': lambda: Shaft(diameter=5.0, length=32.0),
    '5x128mm': lambda: Shaft(diameter=5.0, length=128.0),
    'Shaft_5x102mm': lambda: Shaft(diameter=5.0, length=102.0),
    'Collar5mm': ShaftCollar,
    'Magnet': Magnet,
    'Fan_40x40': Fan,
    'Fan_50x50': lambda: Fan(side=50.0, thickness=11.0, aperture=46.0,
                             hub_diameter=20.0),
    'Servomotor': ServoMotor,
    'ServomotorWheelHorn': ServoHorn,
    'OpticSensor': OptoInterrupter,
    'MicroEndstop': MicroEndstop,
    'ArduinoMega': ArduinoMega,
    'OnOffButton': PanelSwitch,
    'ResetButton': PanelPushButton,
    'JackDC': DcJack,
    'NutButton': PanelNut,
    'M8Connector': M8Connector,
}
