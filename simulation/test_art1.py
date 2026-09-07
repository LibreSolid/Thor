"""The shoulder's drive: two pinions in an internal ring, and the belt's
driving pulley that makes the elbow's driver an absolute angle.
"""

from solid_node.test import TestCase, testing_steps

from simulation import layout
from simulation.art1 import Art1, ELBOW_RATIO, SHOULDER_RATIO


class Art1Test(TestCase):

    node = Art1

    def bind(self, shoulder=0.0, elbow=0.0):
        self.node.clear_state()
        self.node.set_state(time=0.0)
        self.node.shoulder = shoulder
        self.node.elbow = elbow
        return self.node

    # -- the shoulder pair --

    def test_the_ratio_is_the_teeth(self):
        # Derived from the counts in the design, not read off the node.
        self.assertAlmostEqual(SHOULDER_RATIO, 60 / 10, delta=1e-9)
        self.assertAlmostEqual(ELBOW_RATIO, 117 / 20, delta=1e-9)

    def test_both_pinions_clear_the_ring_at_rest(self):
        ring = self.node.art2.art2_body_a
        for name in ('shoulder_pinion_1', 'shoulder_pinion_2'):
            with self.subTest(pinion=name):
                self.assertNotIntersecting(getattr(self.node, name), ring)

    def test_each_pinion_is_free_within_its_measured_backlash(self):
        ring = self.node.art2.art2_body_a
        for name, label in (
                ('shoulder_pinion_1', 'Art2MotorGear_Art2MotorGear'),
                ('shoulder_pinion_2', 'Art2MotorGear_Art2MotorGear001')):
            half = layout.MESH[label].width / 2.0
            with self.subTest(pinion=name):
                self.assertFreeWithin(getattr(self.node, name), half * 0.8,
                                      ring)

    def test_each_pinion_is_blocked_just_past_its_backlash(self):
        ring = self.node.art2.art2_body_a
        for name, label in (
                ('shoulder_pinion_1', 'Art2MotorGear_Art2MotorGear'),
                ('shoulder_pinion_2', 'Art2MotorGear_Art2MotorGear001')):
            half = layout.MESH[label].width / 2.0
            with self.subTest(pinion=name):
                self.assertBlockedBeyond(getattr(self.node, name),
                                         half + 2.0, ring)

    @testing_steps(5)
    def test_the_pinions_stay_in_mesh_through_the_shoulder_s_travel(self):
        # A tooth pitch is 36 degrees; five steps over a 20 degree swing
        # samples it more finely than that.
        for swing in (-20.0, -10.0, 0.0, 10.0, 20.0):
            node = self.bind(shoulder=swing)
            ring = node.art2.art2_body_a
            for name in ('shoulder_pinion_1', 'shoulder_pinion_2'):
                with self.subTest(pinion=name, shoulder=swing):
                    self.assertNotIntersecting(getattr(node, name), ring)

    # -- the elbow's absolute angle --

    def test_swinging_the_shoulder_does_not_turn_the_forearm(self):
        first = self.bind(shoulder=0.0, elbow=0.0)
        rest = first.art2.art3.art3_body.mesh.bounds.copy()
        swung = self.bind(shoulder=25.0, elbow=0.0)
        moved = swung.art2.art3.art3_body.mesh.bounds
        # The forearm is carried around the shoulder, so its position
        # changes; its direction does not. Its own long axis is what the
        # bounding box's tallest dimension follows.
        self.assertAlmostEqual((rest[1] - rest[0])[2],
                               (moved[1] - moved[0])[2], delta=0.05)

    def test_turning_the_elbow_turns_the_forearm(self):
        rest = self.bind(shoulder=0.0, elbow=0.0)
        upright = (rest.art2.art3.art3_body.mesh.bounds[1] -
                   rest.art2.art3.art3_body.mesh.bounds[0])[2]
        bent = self.bind(shoulder=0.0, elbow=90.0)
        laid = (bent.art2.art3.art3_body.mesh.bounds[1] -
                bent.art2.art3.art3_body.mesh.bounds[0])[2]
        self.assertLess(laid, upright - 50.0)
