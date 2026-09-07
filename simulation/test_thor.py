"""What must hold of the whole machine.

The two integrity contracts are the floor: every printed solid is one
connected body, and no two of them share space they should not. Thor's own
parts already share space at the pose its FreeCAD assembly records, so the
second contract is an inventory — the set of overlapping pairs must be
exactly the set `simulation.seats` records — rather than a bare
"nothing touches".
"""

from solid_node.test import TestCase, testing_steps

from simulation import layout, seats
from simulation.gripper import OPEN
from simulation.thor import Thor

#: A pose is a full driver bank; the runner binds the declared defaults, so
#: these are the poses the contracts move the machine to.
HOME = {'art1': 0.0, 'art2': 0.0, 'art3': 0.0, 'art4': 0.0,
        'art5': 0.0, 'art6': 0.0, 'grip': OPEN}


class ThorTest(TestCase):

    node = Thor

    def pose(self, **drivers):
        state = dict(HOME)
        state.update(drivers)
        self.node.clear_state()
        self.node.set_state(**state)
        return self.node

    # -- the two integrity contracts --

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    @testing_steps(8)
    def test_assembly_integrity(self):
        seats.assert_inventory(self, self.node)

    # -- the machine stands where the design says it stands --

    def test_the_axes_are_where_the_assembly_puts_them(self):
        self.assertAlmostEqual(layout.SHOULDER_Z, 202.0, delta=0.001)
        self.assertAlmostEqual(layout.ELBOW_Z - layout.SHOULDER_Z,
                               layout.DRAWN_SHOULDER_TO_ELBOW, delta=0.001)
        self.assertAlmostEqual(layout.SHOULDER_Z,
                               layout.DRAWN_BASE_TO_SHOULDER, delta=0.001)

    def test_the_elbow_to_wrist_span_is_a_millimetre_short_of_the_drawing(self):
        # A finding, asserted so it cannot quietly change: the author's
        # drawing says 195.00 and the assembly says 194.0.
        measured = layout.WRIST_Z - layout.ELBOW_Z
        self.assertAlmostEqual(measured, 194.0, delta=0.001)
        self.assertAlmostEqual(layout.DRAWN_ELBOW_TO_WRIST - measured, 1.0,
                               delta=0.001)
