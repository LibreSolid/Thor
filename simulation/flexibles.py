"""The toothed belts, as shapes that follow their pulleys.

Thor has three GT2 belt runs: one the length of the upper arm, from a
pulley on the shoulder axis to the 117-tooth pulley on the elbow axis, and
two in the forearm, each from a 20-tooth motor pulley to a 40-tooth pulley
on the wrist shaft.

The upper arm carries two sprung tensioner pulleys, and the belt does not
touch them: at the positions the assembly solves them to they stand
5.41 mm clear of the run (`ARM_IDLER_CLEARANCE`), which is what a
tensioner drawn retracted looks like. Drawing the belt over them anyway
produced a path 56 mm shorter than the pulleys admit, which is the
arithmetic telling you the same thing.

They are `molejo` shapes rather than solids, because a belt's shape is a
function of machine state: the teeth circulate as the joint turns. Each
belt is drawn from its own pulleys' centres and pitch radii, so it says
what the geometry says rather than what one exported pose happened to
look like.

The design does place belt solids of its own, and they are the reason
these are drawn instead: both forearm belts are placed lying flat, in a
plane their pulleys are not in, and the arm's belt is placed in a frame
that leaves it clear of both its pulleys. See design.md, Findings.

Every centre below is fixed in the frame the belt lives in — that is why
each belt has exactly one parameter, its tooth travel. The arm's belt
lives in the upper arm, where the shoulder pulley sits at the origin and
the elbow pulley 160.0 along; both forearm belts live in the forearm,
where the wrist pulleys sit on the fork's axis.
"""

import math

import molejo

from solid_node.node import MolejoNode
from solid_node.motion.ports import TranslationalPort

from simulation import materials

#: GT2's tooth pitch, mm.
GT2_PITCH = 2.0
#: Belt thickness at the back of a tooth, and tooth height, mm.
GT2_BACK = 1.38
GT2_TOOTH = 0.75
#: The belt widths the design's own pulleys admit, mm.
ARM_BELT_WIDTH = 6.0
WRIST_BELT_WIDTH = 6.0


def pitch_radius(teeth):
    """A GT2 pulley's pitch radius for a tooth count, mm."""
    return teeth * GT2_PITCH / (2 * 3.141592653589793)


def tangent(first, second):
    """The taut line from one circle to the next, as (point, point).

    Each circle carries the sense the belt runs round it: a belt bent
    backwards over an idler turns the other way, which is what makes the
    tangent between it and its neighbour an inner one rather than an outer.
    """
    x0, y0 = first['center']
    x1, y1 = second['center']
    r0 = first['radius'] * (-1.0 if first.get('turn') else 1.0)
    r1 = second['radius'] * (-1.0 if second.get('turn') else 1.0)
    dx, dy = x1 - x0, y1 - y0
    distance = math.hypot(dx, dy)
    difference = r0 - r1
    if abs(difference) > distance:
        raise ValueError('circles %r and %r admit no taut run'
                         % (first['center'], second['center']))
    base = math.atan2(dy, dx)
    offset = math.acos(difference / distance)
    angle = base + offset
    return ((x0 + r0 * math.cos(angle), y0 + r0 * math.sin(angle)),
            (x1 + r1 * math.cos(angle), y1 + r1 * math.sin(angle)))


def loop(circles):
    """The taut belt's straight runs and wrap angles around each circle.

    Returns (total length, [(circle index, wrap angle in degrees)]).

    Which of a circle's two arcs the belt takes is not a choice: the belt
    leaves along its straight run, so the sense it turns in is the sense
    that run leaves in, and the arc is measured that way. Reading the
    arrival and departure angles and taking the anticlockwise difference
    is what gets this wrong -- the two arcs of a two-pulley loop then land
    on the wrong pulleys, which is right to within a couple of degrees for
    equal pulleys and wrong by 2 mm of belt for a two-to-one pair.
    """
    count = len(circles)
    runs = [tangent(circles[i], circles[(i + 1) % count])
            for i in range(count)]
    length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in runs)
    wraps = []
    for index, circle in enumerate(circles):
        arrival = runs[index - 1][1]
        departure = runs[index][0]
        centre = circle['center']
        start = math.atan2(arrival[1] - centre[1], arrival[0] - centre[0])
        end = math.atan2(departure[1] - centre[1], departure[0] - centre[0])
        turn = (end - start) % (2 * math.pi)
        if _departs_clockwise(circle, runs[index]):
            turn = 2 * math.pi - turn
        length += turn * circle['radius']
        wraps.append((index, math.degrees(turn)))
    return length, wraps


def _departs_clockwise(circle, run):
    """Whether the belt is running clockwise where it leaves this circle.

    The radius to the departure point and the direction the belt leaves in
    are perpendicular; which way the belt is going round is the sign of
    their cross product, and nothing else.
    """
    (px, py), (qx, qy) = run
    cx, cy = circle['center']
    return (px - cx) * (qy - py) - (py - cy) * (qx - px) < 0.0


def teeth_for(circles):
    """How many GT2 teeth the loop those circles describe carries."""
    length, _ = loop(circles)
    return int(round(length / GT2_PITCH))


def _profile(width):
    """A belt cross-section: the back band, teeth cut on the inside."""
    return molejo.Polygon([(-GT2_TOOTH, -width / 2), (GT2_BACK, -width / 2),
                           (GT2_BACK, width / 2), (-GT2_TOOTH, width / 2)])


class ToothedBelt(MolejoNode):
    """A GT2 belt around ordered circles in its own XY plane.

    Subclasses declare `circles` — an ordered list of
    ``{'center': (x, y), 'radius': r}`` and optionally ``'turn'`` for a
    circle the belt is bent backwards over — and `teeth`, the number of
    teeth the loop carries. `travel` is the one parameter: advance it and
    the teeth circulate.
    """

    color = materials.BELT

    circles = ()
    teeth = 0
    width = 6.0
    path_samples = 12
    profile_samples = 4

    travel = TranslationalPort(unit='mm')

    def render(self):
        return molejo.Shape(
            profile=_profile(self.width),
            path=[molejo.Wrap(
                around=[dict(circle) for circle in self.circles],
                teeth=molejo.Teeth(pitch=GT2_PITCH, height=GT2_TOOTH,
                                   count=self.teeth),
                phase=molejo.P.travel)],
            path_samples=self.path_samples,
            profile_samples=self.profile_samples,
            loop=True)


#: The arm belt's pulleys, in the upper arm's own frame. The shoulder's
#: driving pulley sits on the shoulder axis, which is that frame's origin,
#: and the elbow pulley 160.0 along it.
ARM_DRIVE_TEETH = 20
ARM_DRIVEN_TEETH = 117
ARM_CENTRES = 160.0

#: The tensioner pulleys, from their own part and the assembly's own
#: placement of them: the running surface between the flanges is r = 6.0,
#: and the two sit at (+/-14.5, 99.85) in the upper arm's frame.
ARM_IDLER_RADIUS = 6.0
ARM_IDLER_X = 14.5
ARM_IDLER_Y = 99.85


class ElbowBelt(ToothedBelt):
    """The belt that carries the elbow, up the length of the upper arm.

    Two pulleys and nothing else. The arm's two tensioners are drawn where
    they do not reach the belt, so putting them in the path would be
    drawing a belt the machine does not have; `idler_clearance` measures
    the gap and a contract holds it.
    """

    width = ARM_BELT_WIDTH
    circles = (
        {'center': (0.0, 0.0), 'radius': pitch_radius(ARM_DRIVE_TEETH)},
        {'center': (0.0, ARM_CENTRES),
         'radius': pitch_radius(ARM_DRIVEN_TEETH)},
    )
    #: Teeth on the loop, counted from the path the circles describe
    #: rather than from the name of any part.
    teeth = 0


def idler_clearance():
    """How far a tensioner pulley's rim stands off the belt run, mm.

    Measured on the +x run, which the assembly mirrors to the other side.
    """
    (ax, ay), (bx, by) = tangent(
        {'center': (0.0, 0.0), 'radius': pitch_radius(ARM_DRIVE_TEETH)},
        {'center': (0.0, ARM_CENTRES),
         'radius': pitch_radius(ARM_DRIVEN_TEETH)})
    # The tangent solver hands back the -x run; the arm is symmetric about
    # x = 0, so the +x run is its mirror.
    ax, bx = -ax, -bx
    dx, dy = bx - ax, by - ay
    span = math.hypot(dx, dy)
    distance = abs(dx * (ARM_IDLER_Y - ay) - dy * (ARM_IDLER_X - ax)) / span
    return distance - ARM_IDLER_RADIUS


#: The wrist belts' pulleys, in the forearm's own frame: a 20-tooth motor
#: pulley 24.0 out and 77.9 below the fork's axis, and a 40-tooth pulley on
#: the axis itself.
WRIST_DRIVE_TEETH = 20
WRIST_DRIVEN_TEETH = 40
WRIST_MOTOR_X = 24.0
WRIST_CENTRES_Z = 77.9


class WristBelt(ToothedBelt):
    """One of the two belts that drive the wrist differential.

    Drawn in its own XY plane with the motor pulley on +X; the forearm
    stands it up, and the second belt is the same shape mirrored, which is
    a placement rather than another part.
    """

    width = WRIST_BELT_WIDTH
    circles = (
        {'center': (WRIST_MOTOR_X, 0.0),
         'radius': pitch_radius(WRIST_DRIVE_TEETH)},
        {'center': (0.0, WRIST_CENTRES_Z),
         'radius': pitch_radius(WRIST_DRIVEN_TEETH)},
    )
    teeth = 0


def land_overlap(first, second):
    """The height two belt lands share, as (low, high); empty is (x, x)."""
    low = max(first[0], second[0])
    high = min(first[1], second[1])
    return (low, max(low, high))


def land_centre(first, second):
    """The plane a belt on two lands must run in: the middle of both."""
    low, high = land_overlap(first, second)
    return (low + high) / 2.0


#: Each belt land, measured off the pulleys' own toothed cylinders in the
#: frame the belt runs in: the low and high end of the running surface
#: between its flanges. See docs/measurements.md.
#:
#: In the upper arm these are along the shoulder axis, and they are the
#: arm's real trouble: the drive pulley's land is 9.0 mm of height and the
#: elbow pulley's 15.0, but they share only 3.65 mm, less than the 6 mm
#: belt that has to run on both. The tensioners' land does not help -- it
#: is the elbow pulley's height, not the drive pulley's. The model centres
#: the belt in what the two do share and records the shortfall; see
#: design.md, Findings.
ARM_DRIVE_LAND = (12.650, 21.651)
ARM_DRIVEN_LAND = (18.000, 33.000)
ARM_IDLER_LAND = (18.000, 25.000)
ARM_BELT_PLANE = land_centre(ARM_DRIVE_LAND, ARM_DRIVEN_LAND)
ARM_SHARED_LAND = (land_overlap(ARM_DRIVE_LAND, ARM_DRIVEN_LAND)[1]
                   - land_overlap(ARM_DRIVE_LAND, ARM_DRIVEN_LAND)[0])

#: In the forearm, along the wrist axis, and here the design is right: the
#: motor pulley's 9.0 mm land and the wrist pulley's 7.5 mm land share the
#: whole 7.5, which carries the 6 mm belt with a millimetre to spare
#: either side. Measured on the -y belt; the +y one is its mirror.
WRIST_DRIVE_LAND = (-26.900, -17.900)
WRIST_DRIVEN_LAND = (-26.500, -19.000)
WRIST_BELT_PLANE = land_centre(WRIST_DRIVE_LAND, WRIST_DRIVEN_LAND)
WRIST_SHARED_LAND = (land_overlap(WRIST_DRIVE_LAND, WRIST_DRIVEN_LAND)[1]
                     - land_overlap(WRIST_DRIVE_LAND, WRIST_DRIVEN_LAND)[0])


# The tooth counts are the loops' own, from the pulley centres and radii
# above. A real belt has an integer count, so each is rounded, and
# `simulation/test_thor.py` holds each rounding to under half a tooth.
ElbowBelt.teeth = teeth_for(ElbowBelt.circles)
WristBelt.teeth = teeth_for(WristBelt.circles)

#: What each loop's geometry actually asks for, before rounding.
ELBOW_BELT_LENGTH = loop(ElbowBelt.circles)[0]
WRIST_BELT_LENGTH = loop(WristBelt.circles)[0]
