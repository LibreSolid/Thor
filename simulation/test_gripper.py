"""The gripper: one servo, two meshed sector gears, two parallel jaws."""

from solid_node.test import TestCase

from simulation.gripper import Gripper, OPEN, crank_angle, jaw_offset


class GripperTest(TestCase):

    node = Gripper

    def at(self, opening):
        self.node.clear_state()
        self.node.set_state(time=0.0)
        self.node.grip = opening
        return self.node

    def jaw_faces(self, node):
        """The two gripping faces' distances from the gripper's centre."""
        first = node.gripper_finger.mesh.vertices
        second = node.gripper_finger_sym.mesh.vertices
        return abs(first[:, 0]).min(), abs(second[:, 0]).min()

    def test_the_rest_opening_is_the_measured_one(self):
        node = self.at(OPEN)
        near, far = self.jaw_faces(node)
        self.assertAlmostEqual(near + far, OPEN, delta=0.1)

    def test_the_jaws_are_symmetric_at_every_opening(self):
        for opening in (OPEN, 50.0, 30.0, 10.0, 0.0):
            with self.subTest(grip=opening):
                near, far = self.jaw_faces(self.at(opening))
                self.assertAlmostEqual(near, far, delta=0.05)

    def test_the_driver_is_the_clear_opening(self):
        for opening in (OPEN, 50.0, 30.0, 10.0):
            with self.subTest(grip=opening):
                near, far = self.jaw_faces(self.at(opening))
                self.assertAlmostEqual(near + far, opening, delta=0.1)

    def test_closed_means_closed(self):
        near, far = self.jaw_faces(self.at(0.0))
        self.assertLess(near + far, 0.1)
        self.assertNotIntersecting(self.node.gripper_finger,
                                   self.node.gripper_finger_sym)

    def test_the_linkage_is_a_parallelogram(self):
        # The crank arithmetic, redone from the measured pin positions
        # rather than read off the node.
        self.assertAlmostEqual(crank_angle(OPEN), 0.0, delta=1e-6)
        travel = jaw_offset(0.0)
        self.assertAlmostEqual(travel[0], -OPEN / 2, delta=0.05)

    def test_the_servo_body_does_not_move_with_the_horn(self):
        rest = self.at(OPEN).servomotor.mesh.bounds.copy()
        closed = self.at(0.0).servomotor.mesh.bounds
        self.assertAlmostEqual(float(abs(rest - closed).max()), 0.0,
                               delta=1e-6)
