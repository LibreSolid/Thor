"""Where the design's own parts already share space, and by how much.

Thor's FreeCAD assembly is a drawing of one pose, and at that pose several
pairs of its printed parts occupy the same space. Some of those the model
resolves the way a builder would — a printed pinion goes on its shaft at an
angle that meshes, and `simulation.layout.MESH` records the angle measured
for each pair. The rest are the design's own, and the model neither hides
them nor pretends they are tolerable: it records exactly which pairs, and
how much, and fails when the set changes.

That is the point of an inventory rather than an epsilon. A new overlap
fails because it is not in the list; a healed one fails because the list
says it should be there; a changed one fails because its volume moved. An
epsilon would have passed all three.

Every question here is answered on the solids. Each part of this machine is
exact, so an overlap has an exact volume and there is no tessellation noise
to argue about. Volumes are cubic millimetres, measured at the home pose.
"""

import itertools
import math
from collections import namedtuple

#: One recorded overlap: the two printed solids, by their dotted paths from
#: the root, and the volume they share.
Seat = namedtuple('Seat', 'first second volume note')

#: How far a measured volume may move before the contract calls it changed.
TOLERANCE = 0.10

#: Volumes at or below this are contact rather than interference: the exact
#: kernel answers a tangency as a sliver of a few thousandths of a cubic
#: millimetre, and a model that called those interference would have
#: nothing to say about the real ones.
CONTACT = 0.05

INVENTORY = (
    # --- the design's own, verified against its own components ---
    Seat('shoulder.art2.art3.art4.art56.output.art56_gear_plate',
         'shoulder.art2.art3.art4.art56.output.gripper.gripper_bot',
         3248.868,
         "the gripper base's mounting boss is sunk into the crown plate it "
         'bolts to; neither part rebates for the other'),
    Seat('shoulder.art1_top', 'shoulder.fan_40x40_1', 4834.506,
         'the 40 mm fan is sunk into Art1Top; the design does the same, by '
         '5280.4 mm3 with its own fan model'),
    Seat('shoulder.art1_top', 'shoulder.fan_40x40_2', 4834.506,
         'the mirrored pair of the above'),
    Seat('shoulder.art2.art3.art4.art4_motor_gear',
         'shoulder.art2.art3.art4.art4_transmission_column', 24.299,
         "the forearm pinion's lower flange fouls the unrelieved ring at "
         "the foot of the column's gear, at every phase"),
    Seat('shoulder.art2.art3.art3_body',
         'shoulder.art2.art3.art4.art4_optodisk', 24.074,
         "the forearm's encoder disc passes through the elbow body's wall "
         'rather than running in a slot cut for it'),
    Seat('shoulder.art2.art3.art4.art56.output.gripper.gripper_bot',
         'shoulder.art2.art3.art4.art56.output.gripper.servomotor', 322.950,
         'the servo is let into the gripper body; the design does the same, '
         'by 12.9 mm3 with its own servo model'),
    Seat('shoulder.art2.art2_body_a', 'shoulder.art2.art2_body_a_cover2',
         0.202, 'the shoulder plate and its cover share a hair of their seat'),
    Seat('base.art1_gear_motor', 'shoulder.art1_bot', 0.196,
         'the base pinion stands 2 mm taller than the ring gear it drives '
         'and its top rim cuts the rim above the teeth, at every phase'),
    Seat('base.bearing_16014zz', 'shoulder.art1_top', 0.210,
         'the slewing bearing in its seat'),
    Seat('shoulder.art2.art3.art4.art56.output.gripper.gripper_bot',
         'shoulder.art2.art3.art4.art56.output.gripper.gripper_top', 0.127,
         'contact between the two jaw plates'),
    Seat('shoulder.art2.art3.art3_body',
         'shoulder.art2.art3.yaw_motor.body', 0.446,
         "the forearm motor's body in its seat; the design's own motor "
         'model gives the same 0.446 mm3'),
)


def expected_pairs():
    """The unordered pairs the inventory names."""
    return {frozenset((seat.first, seat.second)) for seat in INVENTORY}


def assert_inventory(test, node):
    """The printed solids sharing space are exactly the ones recorded."""
    found = overlaps(node)
    expected = expected_pairs()
    unexpected = sorted(tuple(sorted(pair)) + (round(volume, 3),)
                        for pair, volume in found.items()
                        if pair not in expected)
    test.assertEqual(unexpected, [],
                     'printed solids share space the seats inventory does '
                     'not record')
    missing = sorted(tuple(sorted(pair))
                     for pair in expected - set(found))
    test.assertEqual(missing, [],
                     'the seats inventory records overlaps that are no '
                     'longer there')
    for seat in INVENTORY:
        volume = found[frozenset((seat.first, seat.second))]
        test.assertAlmostEqual(
            volume, seat.volume, delta=max(TOLERANCE, seat.volume * TOLERANCE),
            msg='%s and %s share %.3f mm3, not the %.3f recorded'
                % (seat.first, seat.second, volume, seat.volume))


#: Verdicts are cached on the pair and their **relative** placement, so a
#: sweep only pays for the pairs whose placement actually changed. Two
#: parts of one link never move relative to each other, however far the
#: machine swings, and are therefore compared once.
_verdicts = {}


def overlaps(node):
    """{frozenset(pair): shared volume} for every overlapping pair."""
    solids = list(placed_solids(node))
    found = {}
    for (name_a, shape_a, matrix_a), (name_b, shape_b, matrix_b) in \
            itertools.combinations(solids, 2):
        if not _boxes_touch(_world_box(shape_a, matrix_a),
                            _world_box(shape_b, matrix_b)):
            continue
        relative = _compose(_invert(matrix_a), matrix_b)
        key = (name_a, name_b, _rounded(relative))
        if key not in _verdicts:
            moved = _apply(shape_b, relative)
            _verdicts[key] = sum(
                piece.Volume() for piece in shape_a.intersect(moved).Solids())
        volume = _verdicts[key]
        if volume > CONTACT:
            found[frozenset((name_a, name_b))] = volume
    return found


def placed_solids(node, path=(), matrix=None):
    """(dotted path, exact solid in its own frame, world matrix) per solid."""
    if matrix is None:
        matrix = _IDENTITY
    for child in getattr(node, 'children', ()) or ():
        here = path + (child.name,)
        # A node's own operations apply before any of its ancestors'.
        composed = _compose(matrix, _matrix_of(child.operations))
        if child.rigid:
            yield '.'.join(here), child.shape(), composed
        else:
            yield from placed_solids(child, here, composed)


# --- placement arithmetic -------------------------------------------------
#
# A node's placement is the ordered list of operations it carries. Their
# published form is the one the viewer document uses — ['r', angle, axis]
# and ['t', vector] — and under a bound instant every entry is a number,
# which is the only state these contracts run in.

_IDENTITY = (((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
             (0.0, 0.0, 0.0))


def _rotation(axis, degrees):
    length = math.sqrt(sum(v * v for v in axis)) or 1.0
    x, y, z = (v / length for v in axis)
    c = math.cos(math.radians(degrees))
    s = math.sin(math.radians(degrees))
    d = 1.0 - c
    return ((x * x * d + c, x * y * d - z * s, x * z * d + y * s),
            (y * x * d + z * s, y * y * d + c, y * z * d - x * s),
            (z * x * d - y * s, z * y * d + x * s, z * z * d + c))


def _compose(outer, inner):
    Ra, ta = outer
    Rb, tb = inner
    R = tuple(tuple(sum(Ra[i][k] * Rb[k][j] for k in range(3))
                    for j in range(3)) for i in range(3))
    t = tuple(sum(Ra[i][k] * tb[k] for k in range(3)) + ta[i]
              for i in range(3))
    return R, t


def _invert(matrix):
    R, t = matrix
    Ri = tuple(tuple(R[j][i] for j in range(3)) for i in range(3))
    ti = tuple(-sum(Ri[i][k] * t[k] for k in range(3)) for i in range(3))
    return Ri, ti


def _matrix_of(operations):
    matrix = _IDENTITY
    for operation in operations:
        serialized = operation.serialized
        if serialized[0] == 'r':
            _, angle, axis = serialized
            step = (_rotation([float(v) for v in axis], float(angle)),
                    (0.0, 0.0, 0.0))
        elif serialized[0] == 't':
            step = (_IDENTITY[0], tuple(float(v) for v in serialized[1]))
        else:
            raise ValueError('unknown operation %r' % (serialized,))
        matrix = _compose(step, matrix)
    return matrix


def _rounded(matrix, places=6):
    R, t = matrix
    return (tuple(tuple(round(v, places) for v in row) for row in R),
            tuple(round(v, places) for v in t))


def _apply(shape, matrix):
    from OCP.gp import gp_Trsf
    from OCP.TopLoc import TopLoc_Location
    import cadquery as cq

    R, t = matrix
    trsf = gp_Trsf()
    trsf.SetValues(R[0][0], R[0][1], R[0][2], t[0],
                   R[1][0], R[1][1], R[1][2], t[1],
                   R[2][0], R[2][1], R[2][2], t[2])
    return cq.Shape.cast(shape.wrapped.Moved(TopLoc_Location(trsf)))


def _world_box(shape, matrix):
    box = shape.BoundingBox()
    R, t = matrix
    corners = [(x, y, z)
               for x in (box.xmin, box.xmax)
               for y in (box.ymin, box.ymax)
               for z in (box.zmin, box.zmax)]
    points = [tuple(sum(R[i][k] * c[k] for k in range(3)) + t[i]
                    for i in range(3)) for c in corners]
    return tuple(min(p[i] for p in points) for i in range(3)) + \
        tuple(max(p[i] for p in points) for i in range(3))


def _boxes_touch(a, b, tolerance=0.05):
    return all(a[i] < b[i + 3] + tolerance and b[i] < a[i + 3] + tolerance
               for i in range(3))
