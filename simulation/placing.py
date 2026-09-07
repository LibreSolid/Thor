"""How a sub-assembly puts its parts where the design puts them.

Every rest placement in this model is the design's own, read out of its
FreeCAD assembly and transcribed into `simulation.layout`. A sub-assembly
therefore does not restate a single coordinate: it declares one child per
placed instance, maps the design's label to the attribute holding it, and
lets `place_from_design` apply the placement.

The mapping is the only thing written by hand. One design document can be
split across several nodes — the wrist's own parts, the output the tool
roll turns, and the gripper are three nodes over one document — so
`check_placement_partition` proves the mappings together cover the
document's instances exactly once.
"""

import math

from simulation import layout


def place_from_design(node, group, mapping, phases=()):
    """Place each mapped child at its design placement, at rest.

    `mapping` maps the design's own instance label to the attribute the
    child is held under; a label the mapping does not name belongs to
    another node and is left alone. `phases` maps a label to a rotation
    about the part's own Z applied first: how a printed gear is put on its
    shaft, measured from the mesh rather than taken from an assembly that
    never checked it.
    """
    phases = dict(phases)
    for placed in layout.links(group):
        attribute = mapping.get(placed.label)
        if attribute is None:
            continue
        child = getattr(node, attribute)
        phase = phases.get(placed.label)
        if phase:
            child.rotate(phase, [0.0, 0.0, 1.0])
        child.rotate(placed.angle, list(placed.axis))
        child.translate(list(placed.translate))


def rotate_about(child, angle, axis, point):
    """Turn a child about a line, both given in the child's own frame.

    Operations apply in the order they are appended, so bringing the line
    to the origin, turning, and carrying it back is exactly this sequence.
    A joint whose axis runs through the moving node's own origin does not
    need it; the elbow, whose axis sits 81.5 mm from the Art3 origin, does.
    """
    child.translate([-point[0], -point[1], -point[2]])
    child.rotate(angle, list(axis))
    child.translate(list(point))


def _rotation(axis, degrees):
    """The 3x3 rotation matrix for one axis and angle."""
    length = math.sqrt(sum(v * v for v in axis)) or 1.0
    x, y, z = (v / length for v in axis)
    c = math.cos(math.radians(degrees))
    s = math.sin(math.radians(degrees))
    d = 1.0 - c
    return ((x * x * d + c, x * y * d - z * s, x * z * d + y * s),
            (y * x * d + z * s, y * y * d + c, y * z * d - x * s),
            (z * x * d - y * s, z * y * d + x * s, z * z * d + c))


def into_local(placed, point=None, direction=None):
    """Carry a point or a direction from a sub-assembly's frame into a
    part's own frame.

    `simulate()` composes its operations **inside** a part's rest
    placement, so a pivot read off the assembly has to be expressed in the
    part's own coordinates before it can be turned about. The rest
    placement is `rotate(angle, axis)` then `translate(t)`, so undoing it
    is subtracting `t` and applying the rotation backwards.
    """
    R = _rotation(placed.axis, placed.angle)
    if direction is not None:
        v = direction
    else:
        v = [point[i] - placed.translate[i] for i in range(3)]
    return [sum(R[k][i] * v[k] for k in range(3)) for i in range(3)]


def bound(port, default=0.0):
    """What a port was bound to, or a default when nothing bound it.

    A port's value is symbolic in the build and in the viewer, so it can
    never be tested for truth: `port.value or 0.0` raises the moment the
    value is an expression rather than a number. Only `None` means unbound.
    """
    value = port.value
    return default if value is None else value


def axis_sign(placed, axis):
    """Whether a part's own +Z runs along `axis` or against it.

    Thor's assembly places pairs of the same part facing opposite ways —
    the two wrist pinions, the two belt pulleys on their shafts — so the
    same physical rotation is one sign in one part's frame and the other
    sign in its twin's. Reading the sign off the placement keeps that out
    of the arithmetic, where it would be a transcription error waiting to
    happen.
    """
    R = _rotation(placed.axis, placed.angle)
    own_z = [R[i][2] for i in range(3)]
    dot = sum(a * b for a, b in zip(own_z, axis))
    if abs(abs(dot) - 1.0) > 1e-3:
        raise ValueError("%s's own axis is not along %s" % (placed.label, axis))
    return 1.0 if dot > 0 else -1.0


def align_z(child, direction, point):
    """Stand a part whose own axis is +Z along `direction`, at `point`.

    Fasteners are drawn once, head down and shank along +Z, and stood up
    on the axes the printed parts' holes define. Rotation before
    translation, as everywhere else.
    """
    direction = list(direction)
    length = math.sqrt(sum(v * v for v in direction)) or 1.0
    x, y, z = (v / length for v in direction)
    if abs(z - 1.0) < 1e-9:
        pass
    elif abs(z + 1.0) < 1e-9:
        child.rotate(180.0, [1.0, 0.0, 0.0])
    else:
        # The axis that carries +Z onto the direction is their cross
        # product, and the angle between them is the arccosine of z.
        child.rotate(math.degrees(math.acos(max(-1.0, min(1.0, z)))),
                     [-y, x, 0.0])
    child.translate(list(point))


def turn_about(child, placed, angle, axis, point):
    """Turn a child about a line stated in its parent sub-assembly's frame.

    The line is carried into the child's own frame first, because that is
    the frame `simulate()` operations act in.
    """
    rotate_about(child, angle,
                 into_local(placed, direction=axis),
                 into_local(placed, point=point))


def check_placement_partition(test, group, *mappings, skip=()):
    """The mappings together name every instance of `group`, once each.

    `skip` names instances no node places: the two toothed belts, whose
    shape is not a placement but a path between pulleys.
    """
    placed = []
    for mapping in mappings:
        placed.extend(mapping)
    test.assertEqual(len(placed), len(set(placed)),
                     '%s: an instance is placed by two nodes' % group)
    designed = {p.label for p in layout.links(group)} - set(skip)
    test.assertEqual(set(placed), designed,
                     '%s: placement mappings do not match the design' % group)
