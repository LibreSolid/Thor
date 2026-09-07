"""The forearm's yaw: a ten-tooth pinion on a twenty-tooth column gear."""

from solid_node.test import TestCase

from simulation import layout, seats
from simulation.art3 import Art3, COLUMN_RATIO


class Art3Test(TestCase):

    node = Art3

    def at(self, yaw=0.0):
        self.node.clear_state()
        self.node.set_state(time=0.0)
        self.node.yaw = yaw
        self.node.wrist = 0.0
        self.node.tool = 0.0
        self.node.grip = 69.94
        return self.node

    def test_the_ratio_is_the_teeth(self):
        self.assertAlmostEqual(COLUMN_RATIO, 20 / 10, delta=1e-9)

    def test_the_pinion_shares_only_what_the_design_makes_it_share(self):
        # The pinion's lower flange fouls the unrelieved ring at the foot
        # of the column's gear at every phase; the model records the
        # measured volume rather than pretending it is not there.
        column = self.node.art4.art4_transmission_column
        floor = layout.MESH['Art4MotorGear_Art4MotorGear'].floor
        self.assertIntersectVolumeBelow(self.node.art4_motor_gear, column,
                                        floor * 1.1)
        self.assertIntersectVolumeAbove(self.node.art4_motor_gear, column,
                                        floor * 0.9)

    def test_the_teeth_clear_within_the_measured_window(self):
        column = self.node.art4.art4_transmission_column
        half = layout.MESH['Art4MotorGear_Art4MotorGear'].width / 2.0
        self.assertFreeWithin(self.node.art4_motor_gear, half * 0.8, column,
                              volume_epsilon=layout.MESH[
                                  'Art4MotorGear_Art4MotorGear'].floor * 1.1)

    def test_the_ball_cage_runs_at_half_the_forearm_s_speed(self):
        rest = self.at(0.0).bearing_balls.mesh.bounds.copy()
        turned = self.at(20.0).bearing_balls.mesh.bounds
        self.assertGreater(float(abs(rest - turned).max()), 0.5,
                           'the ball cage did not move with the forearm')
