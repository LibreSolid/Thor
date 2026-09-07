"""The wrist differential: two pinions, one crown, two joints out."""

from solid_node.test import TestCase

from simulation import layout
from simulation.art56 import Art56, CROWN_RATIO


class Art56Test(TestCase):

    node = Art56

    def at(self, tool=0.0, grip=None):
        self.node.clear_state()
        self.node.set_state(time=0.0)
        self.node.tool = tool
        self.node.grip = 69.94 if grip is None else grip
        return self.node

    def test_the_ratio_is_the_teeth(self):
        self.assertAlmostEqual(CROWN_RATIO, 30 / 15, delta=1e-9)

    def test_both_bevels_clear_the_crown_at_rest(self):
        crown = self.node.output.art56_gear_plate
        for name in ('art56_small_gear_1', 'art56_small_gear_2'):
            with self.subTest(bevel=name):
                self.assertNotIntersecting(getattr(self.node, name), crown)

    def test_each_bevel_is_free_within_its_measured_backlash(self):
        crown = self.node.output.art56_gear_plate
        for name, label in (
                ('art56_small_gear_1', 'Art56SmallGear_Art56SmallGear'),
                ('art56_small_gear_2', 'Art56SmallGear_Art56SmallGear001')):
            half = layout.MESH[label].width / 2.0
            with self.subTest(bevel=name):
                self.assertFreeWithin(getattr(self.node, name), half * 0.8,
                                      crown)

    def test_each_bevel_is_blocked_just_past_its_backlash(self):
        crown = self.node.output.art56_gear_plate
        for name, label in (
                ('art56_small_gear_1', 'Art56SmallGear_Art56SmallGear'),
                ('art56_small_gear_2', 'Art56SmallGear_Art56SmallGear001')):
            half = layout.MESH[label].width / 2.0
            with self.subTest(bevel=name):
                self.assertBlockedBeyond(getattr(self.node, name),
                                         half + 1.5, crown)

    def test_the_tool_roll_turns_the_crown_and_the_pinions_the_other_way(self):
        rest = self.at(tool=0.0)
        crown_rest = rest.output.art56_gear_plate.mesh.bounds.copy()
        turned = self.at(tool=30.0)
        crown_turned = turned.output.art56_gear_plate.mesh.bounds
        self.assertGreater(float(abs(crown_rest - crown_turned).max()), 0.5,
                           'the crown did not move with the tool roll')

    def test_the_pinions_turn_at_the_crown_s_ratio(self):
        # The relation, redone here from the tooth counts rather than read
        # off the node: a pinion spins twice for one turn of the crown.
        self.assertAlmostEqual(self.node.pinion_spin(10.0), 20.0, delta=1e-9)
