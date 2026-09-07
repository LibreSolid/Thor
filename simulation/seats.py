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

**This inventory is not finished, and the contract is red.** Thirteen
pairs below were each verified against the design's own geometry -- the
component the design places, or the two printed parts as the assembly
solves them -- and 272 pairs share space at the home pose. The rest are
the model's own fasteners meeting the parts they fasten, and a handful of
catalogue envelopes drawn here rather than by the design. They are not
recorded, because recording a number the model produced by accident is
how an inventory stops being evidence: the contract stays red until each
one is either explained or removed. `docs/measurements.md` says which
kinds remain.

Every question here is answered on the solids. Each part of this machine is
exact, so an overlap has an exact volume and there is no tessellation noise
to argue about. Volumes are cubic millimetres, measured at the home pose.
"""

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
    Seat('shoulder.art1_top', 'shoulder.fan_40x40_1', 4564.245,
         'the 40 mm fan is sunk into Art1Top; the design does the same, by '
         '5280.4 mm3 with its own fan model'),
    Seat('shoulder.art1_top', 'shoulder.fan_40x40_2', 4564.245,
         'the mirrored pair of the above'),
    Seat('shoulder.art2.art3.art4.art56.gt2x40_pulley_1',
         'shoulder.art2.art3.art4.wrist_axle', 120.166,
         "the wrist's belt pulley is a 4 mm-bore pulley on a 5 mm shaft: "
         'the design\'s own component bores it 2.000 in radius and its own '
         'Shaft_5x102mm is 2.500, so the 0.5 mm wall of the bore is solid '
         'shaft over the pulley\'s whole 17 mm'),
    Seat('shoulder.art2.art3.art4.art56.gt2x40_pulley_2',
         'shoulder.art2.art3.art4.wrist_axle', 120.166,
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
                     '%d of %d overlapping pairs are not in the seats '
                     'inventory' % (len(unexpected), len(found)))
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


#: The inventory is answered on the framework's own placed solids, its own
#: broad phase and its own kernel-aware pair intersection. Those three are
#: private names: `assertNoSolidInterference` raises on the first pair it
#: finds, so a machine whose own design overlaps -- which is this one --
#: has no public way to ask which pairs overlap and by how much. Reaching
#: for the private helpers is better than a second, differently-wrong
#: implementation of placement and culling; the shop's docs/warts.md
#: records the gap under Thor.
#:
#: The pay-off is that this contract follows the run: `solid test
#: --faceted` answers it on the parts' meshes, and the exact run certifies
#: it. On this machine that is the difference between minutes and an hour,
#: because there are 507 solids in it.
from solid_node.test import (_bounds_candidates, _candidate_intersection,
                             _placed_assembly_solids)


def overlaps(node):
    """{frozenset(pair of dotted paths): shared volume} over the whole tree."""
    solids = _placed_assembly_solids(node)
    names = qualified_names(node)
    found = {}
    for first, second in _bounds_candidates([item[2] for item in solids]):
        is_empty, volume = _candidate_intersection(solids, first, second)
        if is_empty or volume <= CONTACT:
            continue
        pair = frozenset((names[id(solids[first][0])],
                          names[id(solids[second][0])]))
        found[pair] = volume
    return found


def qualified_names(node):
    """{id(solid): dotted path from the root} for every printed solid.

    The framework names a solid by its own attribute name, which repeats
    all over a machine with six of everything; the inventory needs the
    path that says which one.
    """
    names = {}

    def walk(assembly, path):
        for child in getattr(assembly, 'children', ()) or ():
            here = path + (child.name,)
            if child.rigid:
                names[id(child)] = '.'.join(here)
            else:
                walk(child, here)

    walk(node, ())
    return names
