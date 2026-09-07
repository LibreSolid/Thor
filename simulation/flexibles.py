"""The toothed belts, as shapes that follow their pulleys.

Thor has three GT2 belt runs: one the length of the upper arm, from a
pulley on the shoulder axis to the 117-tooth pulley on the elbow axis over
two sprung idlers, and two in the forearm, each from a 20-tooth motor
pulley to a 40-tooth pulley on the wrist shaft.

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

from solid_node.node import MolejoNode, RotationalPort

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

    Returns (total length, [(circle index, wrap angle in degrees)]). The
    wrap angles sum to a full turn, which is what makes the result a
    closed belt rather than a set of unconnected tangents.
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
        if circle.get('turn'):
            turn = 2 * math.pi - turn
        length += turn * circle['radius']
        wraps.append((index, math.degrees(turn)))
    return length, wraps


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

    travel = RotationalPort(unit='mm')

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
#: driving pulley sits on the shoulder axis, which is that frame's origin;
#: the elbow pulley sits 160.0 along it; the two idlers press on the
#: outside of each straight run, so the belt is bent backwards over them.
ARM_DRIVE_TEETH = 20
ARM_DRIVEN_TEETH = 117
ARM_IDLER_RADIUS = 6.0
ARM_IDLER_X = 14.5
ARM_IDLER_Y = 99.85
ARM_CENTRES = 160.0


class ElbowBelt(ToothedBelt):
    """The belt that carries the elbow, up the length of the upper arm."""

    width = ARM_BELT_WIDTH
    circles = (
        {'center': (0.0, 0.0), 'radius': pitch_radius(ARM_DRIVE_TEETH)},
        {'center': (ARM_IDLER_X, ARM_IDLER_Y), 'radius': ARM_IDLER_RADIUS},
        {'center': (0.0, ARM_CENTRES),
         'radius': pitch_radius(ARM_DRIVEN_TEETH)},
        {'center': (-ARM_IDLER_X, ARM_IDLER_Y), 'radius': ARM_IDLER_RADIUS},
    )
    #: Teeth on the loop, counted from the path the circles describe
    #: rather than from the name of any part.
    teeth = 0


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


#: Where the arm belt's two pulleys put their belt lands, along the
#: shoulder axis in the upper arm's own frame. They are 7.9 mm apart: the
#: drive pulley's land is centred 17.15 and the elbow pulley's 25.0, and no
#: belt can run on both. The model draws the belt in the drive pulley's
#: plane and says so; see design.md, Findings.
ARM_DRIVE_BAND = 17.15
ARM_DRIVEN_BAND = 25.0
ARM_BAND_OFFSET = ARM_DRIVEN_BAND - ARM_DRIVE_BAND


# The tooth counts are the loops' own, from the pulley centres and radii
# above. A real belt has an integer count, so each is rounded, and
# `simulation/test_flexibles.py` holds the rounding to under half a tooth.
ElbowBelt.teeth = teeth_for(ElbowBelt.circles)
WristBelt.teeth = teeth_for(WristBelt.circles)

#: What each loop's geometry actually asks for, before rounding.
ELBOW_BELT_LENGTH = loop(ElbowBelt.circles)[0]
WRIST_BELT_LENGTH = loop(WristBelt.circles)[0]
