"""What must hold of the whole machine.

Every contract here drives the machine through its own seven drivers,
because that is the only way in: a sub-assembly's ports are bound by its
parent, so a gripper or a wrist tested on its own has nothing telling it
what to do. Parts are addressed down the tree from the root.

The two integrity contracts are the floor: every printed solid is one
connected body, and no two of them share space they should not. Thor's own
parts already share space at the pose its FreeCAD assembly records, so the
second is an inventory — the set of overlapping pairs must be exactly the
set `simulation.seats` records — rather than a bare "nothing touches".
"""

from solid_node.test import TestCase, testing_steps

from simulation import layout, seats
from simulation.art1 import ELBOW_RATIO, SHOULDER_RATIO
from simulation.art3 import COLUMN_RATIO
from simulation.art56 import CROWN_RATIO
from simulation.gripper import OPEN, crank_angle, jaw_offset
from simulation.thor import Thor

HOME = {'art1': 0.0, 'art2': 0.0, 'art3': 0.0, 'art4': 0.0,
        'art5': 0.0, 'art6': 0.0, 'grip': OPEN}

#: Where each part lives below the root, so a contract can name it.
ARM = 'shoulder.art2'
FOREARM = 'shoulder.art2.art3'
WRIST = 'shoulder.art2.art3.art4.art56'
GRIPPER = WRIST + '.output.gripper'


class ThorTest(TestCase):

    node = Thor

    def pose(self, **drivers):
        state = dict(HOME)
        state.update(drivers)
        self.node.clear_state()
        self.node.set_state(time=0.0, **state)
        return self.node

    def part(self, path):
        node = self.node
        for name in path.split('.'):
            node = next(child for child in node.children
                        if child.name == name)
        return node

    # -- the two integrity contracts --

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    @testing_steps(8)
    def test_assembly_integrity(self):
        seats.assert_inventory(self, self.node)

    # -- the machine stands where the design says it stands --

    def test_the_axes_are_where_the_assembly_puts_them(self):
        self.assertAlmostEqual(layout.SHOULDER_Z,
                               layout.DRAWN_BASE_TO_SHOULDER, delta=0.001)
        self.assertAlmostEqual(layout.ELBOW_Z - layout.SHOULDER_Z,
                               layout.DRAWN_SHOULDER_TO_ELBOW, delta=0.001)

    def test_the_elbow_to_wrist_span_is_a_millimetre_short_of_the_drawing(self):
        # A finding, asserted so it cannot quietly change: the author's
        # drawing says 195.00 and the assembly says 194.0.
        measured = layout.WRIST_Z - layout.ELBOW_Z
        self.assertAlmostEqual(measured, 194.0, delta=0.001)
        self.assertAlmostEqual(layout.DRAWN_ELBOW_TO_WRIST - measured, 1.0,
                               delta=0.001)

    # -- the transmissions --

    def test_every_ratio_is_the_teeth_the_parts_carry(self):
        # Redone here from the counts, never read off a node's derivation.
        self.assertAlmostEqual(SHOULDER_RATIO, 60 / 10, delta=1e-9)
        self.assertAlmostEqual(ELBOW_RATIO, 117 / 20, delta=1e-9)
        self.assertAlmostEqual(COLUMN_RATIO, 20 / 10, delta=1e-9)
        self.assertAlmostEqual(CROWN_RATIO, 30 / 15, delta=1e-9)

    def test_both_shoulder_pinions_clear_the_ring(self):
        self.pose()
        ring = self.part(ARM + '.art2_body_a')
        for name in ('shoulder_pinion_1', 'shoulder_pinion_2'):
            with self.subTest(pinion=name):
                self.assertNotIntersecting(self.part('shoulder.' + name),
                                           ring)

    def test_each_shoulder_pinion_is_free_within_its_backlash(self):
        self.pose()
        ring = self.part(ARM + '.art2_body_a')
        for name, label in (
                ('shoulder_pinion_1', 'Art2MotorGear_Art2MotorGear'),
                ('shoulder_pinion_2', 'Art2MotorGear_Art2MotorGear001')):
            half = layout.MESH[label].width / 2.0
            with self.subTest(pinion=name):
                self.assertFreeWithin(self.part('shoulder.' + name),
                                      half * 0.8, ring)

    def test_each_shoulder_pinion_is_blocked_past_its_backlash(self):
        self.pose()
        ring = self.part(ARM + '.art2_body_a')
        for name, label in (
                ('shoulder_pinion_1', 'Art2MotorGear_Art2MotorGear'),
                ('shoulder_pinion_2', 'Art2MotorGear_Art2MotorGear001')):
            half = layout.MESH[label].width / 2.0
            with self.subTest(pinion=name):
                self.assertBlockedBeyond(self.part('shoulder.' + name),
                                         half + 2.0, ring)

    def test_the_pinions_stay_in_mesh_through_the_shoulder_s_travel(self):
        # A tooth pitch is 36 degrees, so ten-degree steps sample it finely.
        for swing in (-20.0, -10.0, 10.0, 20.0):
            self.pose(art2=swing)
            ring = self.part(ARM + '.art2_body_a')
            for name in ('shoulder_pinion_1', 'shoulder_pinion_2'):
                with self.subTest(pinion=name, art2=swing):
                    self.assertNotIntersecting(self.part('shoulder.' + name),
                                               ring)

    def test_both_wrist_bevels_clear_the_crown(self):
        self.pose()
        crown = self.part(WRIST + '.output.art56_gear_plate')
        for name in ('art56_small_gear_1', 'art56_small_gear_2'):
            with self.subTest(bevel=name):
                self.assertNotIntersecting(self.part(WRIST + '.' + name),
                                           crown)

    def test_each_wrist_bevel_is_blocked_past_its_backlash(self):
        self.pose()
        crown = self.part(WRIST + '.output.art56_gear_plate')
        for name, label in (
                ('art56_small_gear_1', 'Art56SmallGear_Art56SmallGear'),
                ('art56_small_gear_2', 'Art56SmallGear_Art56SmallGear001')):
            half = layout.MESH[label].width / 2.0
            with self.subTest(bevel=name):
                self.assertBlockedBeyond(self.part(WRIST + '.' + name),
                                         half + 1.5, crown)

    def test_the_forearm_pinion_shares_only_its_measured_floor(self):
        # Its lower flange fouls the unrelieved ring at the foot of the
        # column's gear at every phase; the model records the volume
        # rather than pretending it is not there.
        self.pose()
        floor = layout.MESH['Art4MotorGear_Art4MotorGear'].floor
        self.assertIntersectVolumeBelow(
            self.part(FOREARM + '.art4_motor_gear'),
            self.part(FOREARM + '.art4.art4_transmission_column'),
            floor * 1.1)
        self.assertIntersectVolumeAbove(
            self.part(FOREARM + '.art4_motor_gear'),
            self.part(FOREARM + '.art4.art4_transmission_column'),
            floor * 0.9)

    # -- the elbow's absolute angle --

    def test_swinging_the_shoulder_does_not_turn_the_forearm(self):
        upright = self.forearm_height()
        self.pose(art2=25.0)
        self.assertAlmostEqual(self.forearm_height(), upright, delta=0.5)

    def test_turning_the_elbow_turns_the_forearm(self):
        upright = self.forearm_height()
        self.pose(art3=90.0)
        self.assertLess(self.forearm_height(), upright - 50.0)

    def forearm_height(self):
        bounds = self.part(FOREARM + '.art3_body').mesh.bounds
        return float(bounds[1][2] - bounds[0][2])

    # -- the gripper --

    def jaw_faces(self):
        """Each jaw's gripping face, as its distance from the tool centre.

        The jaws separate along the wrist frame's own x, which at rest is
        the machine's y.
        """
        first = self.part(GRIPPER + '.gripper_finger').mesh.vertices
        second = self.part(GRIPPER + '.gripper_finger_sym').mesh.vertices
        return abs(first[:, 1]).min(), abs(second[:, 1]).min()

    def test_the_rest_opening_is_the_measured_one(self):
        self.pose()
        near, far = self.jaw_faces()
        self.assertAlmostEqual(near + far, OPEN, delta=0.1)

    def test_the_jaws_are_symmetric_at_every_opening(self):
        for opening in (OPEN, 50.0, 30.0, 10.0, 0.0):
            self.pose(grip=opening)
            near, far = self.jaw_faces()
            with self.subTest(grip=opening):
                self.assertAlmostEqual(near, far, delta=0.05)

    def test_the_driver_is_the_clear_opening(self):
        for opening in (OPEN, 50.0, 30.0, 10.0):
            self.pose(grip=opening)
            near, far = self.jaw_faces()
            with self.subTest(grip=opening):
                self.assertAlmostEqual(near + far, opening, delta=0.1)

    def test_closed_means_closed(self):
        self.pose(grip=0.0)
        near, far = self.jaw_faces()
        self.assertLess(near + far, 0.1)
        self.assertNotIntersecting(
            self.part(GRIPPER + '.gripper_finger'),
            self.part(GRIPPER + '.gripper_finger_sym'))

    def test_the_linkage_is_a_parallelogram(self):
        # The crank arithmetic redone from the measured pin positions.
        self.assertAlmostEqual(crank_angle(OPEN), 0.0, delta=1e-6)
        self.assertAlmostEqual(jaw_offset(0.0)[0], -OPEN / 2, delta=0.05)
