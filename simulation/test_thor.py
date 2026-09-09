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

import math

from solid_node.simulation import ScenarioTest
from solid_node.test import TestCase

from simulation import art2, art4, flexibles, layout, seats
from simulation.art1 import ELBOW_RATIO, SHOULDER_RATIO
from simulation.art3 import COLUMN_RATIO
from simulation.art56 import CROWN_RATIO
from simulation.gripper import OPEN, crank_angle, jaw_offset
from simulation.thor import (BASE_TRAVEL, ELBOW_TRAVEL, FOREARM_TRAVEL,
                            SHOULDER_TRAVEL, Thor, TOOL_TRAVEL, WRIST_TRAVEL)

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
        """Put the machine at a pose, naming every driver.

        Never `clear_state()` first, tempting as it is: the runner binds
        the declared defaults once, before the first render, and clearing
        them leaves the next test's `set_keyframe(0)` with no drivers
        bound at all. Every driver is named here instead, so the merge is
        a complete pose whatever the last test left behind.
        """
        state = dict(HOME)
        state.update(drivers)
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
        # Asked on the solids, not through `assertNoDisconnectedSolids`.
        # Every part of this machine is exact, so whether one is a single
        # body is a question its own B-rep answers exactly; the framework's
        # assertion reads the STL instead and calls `Art1Top` five bodies
        # -- the solid plus three two-triangle patches of zero volume and
        # one detached lug -- because the tessellator does not weld what
        # the solid already joins. Recorded in the shop's docs/warts.md
        # under Thor.
        self.pose()
        loose = []
        for path, solid in self.printed_solids():
            count = len(solid.shape().Solids())
            if count != 1:
                loose.append('%s is %d bodies' % (path, count))
        self.assertEqual(loose, [])

    def printed_solids(self):
        """(dotted path, node) for every printed solid below the root."""
        names = seats.qualified_names(self.node)

        def walk(assembly):
            for child in getattr(assembly, 'children', ()) or ():
                if child.rigid:
                    if child.exact:
                        yield names[id(child)], child
                else:
                    yield from walk(child)

        return list(walk(self.node))

    def test_assembly_integrity(self):
        # One instant, deliberately. Nothing in Thor is driven by the
        # timeline -- the machine moves on its seven drivers -- so sweeping
        # `time` would compare the same pose to itself, at the price of a
        # full exact scan of five hundred solids per step. Coverage of the
        # poses belongs to the scenario contract, which drives the machine.
        self.pose()
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

    # -- the belts --

    def test_each_belt_loop_is_a_whole_number_of_teeth(self):
        # A belt is made in whole teeth, so a loop the geometry asks for in
        # 231.49 of them is a real belt only because the tensioners take up
        # the rest. Half a tooth is the most that may be rounded away.
        for name, circles, teeth in (
                ('elbow', flexibles.ElbowBelt.circles,
                 flexibles.ElbowBelt.teeth),
                ('wrist', flexibles.WristBelt.circles,
                 flexibles.WristBelt.teeth)):
            with self.subTest(belt=name):
                exact = flexibles.loop(circles)[0] / flexibles.GT2_PITCH
                self.assertLess(abs(exact - teeth), 0.5)

    def test_each_belt_wraps_its_pulleys_the_whole_way_round(self):
        # The wrap angles of a closed taut loop add to a full turn. This is
        # what catches an arc put on the wrong pulley: the two of a
        # two-to-one pair still sum to 360 when they are swapped, but the
        # length is then 2 mm out, which the tooth count above rejects.
        for name, circles in (('elbow', flexibles.ElbowBelt.circles),
                              ('wrist', flexibles.WristBelt.circles)):
            with self.subTest(belt=name):
                wraps = flexibles.loop(circles)[1]
                self.assertAlmostEqual(sum(angle for _, angle in wraps),
                                       360.0, delta=1e-6)

    def test_the_smaller_pulley_takes_the_smaller_wrap(self):
        # An open belt hugs the big pulley more than the small one. Getting
        # this backwards is exactly the failure the loop arithmetic used to
        # have, and it costs 2 mm of belt in the forearm.
        for name, circles in (('elbow', flexibles.ElbowBelt.circles),
                              ('wrist', flexibles.WristBelt.circles)):
            with self.subTest(belt=name):
                wraps = dict(flexibles.loop(circles)[1])
                order = sorted(range(len(circles)),
                               key=lambda i: circles[i]['radius'])
                self.assertLess(wraps[order[0]], 180.0)
                self.assertGreater(wraps[order[-1]], 180.0)

    def test_the_arm_s_tensioners_do_not_reach_its_belt(self):
        # A finding, asserted so it cannot quietly change: the two sprung
        # tensioners are solved 5.41 mm clear of the run, which is what a
        # tensioner drawn retracted looks like. The belt is therefore drawn
        # on two pulleys, not four.
        self.assertAlmostEqual(flexibles.idler_clearance(), 5.407,
                               delta=0.005)
        self.assertEqual(len(flexibles.ElbowBelt.circles), 2)

    def test_the_arm_s_pulleys_leave_too_little_land_for_their_belt(self):
        # A finding: the drive pulley's land and the elbow pulley's share
        # 3.65 mm of height, and the belt they both carry is 6.0 mm wide.
        self.assertAlmostEqual(flexibles.ARM_SHARED_LAND, 3.651, delta=0.005)
        self.assertLess(flexibles.ARM_SHARED_LAND, flexibles.ARM_BELT_WIDTH)

    def test_the_forearm_s_pulleys_carry_their_belt(self):
        # The forearm has no such trouble, and saying so is what makes the
        # arm's shortfall a finding rather than a modelling artefact.
        self.assertAlmostEqual(flexibles.WRIST_SHARED_LAND, 7.5, delta=0.005)
        self.assertGreater(flexibles.WRIST_SHARED_LAND,
                           flexibles.WRIST_BELT_WIDTH)

    def test_each_belt_run_is_longer_than_the_belt_the_design_names(self):
        # A finding: the forearm's belts are called 208 mm and their
        # pulleys, where the assembly puts them, ask for 223.5.
        self.assertAlmostEqual(flexibles.WRIST_BELT_LENGTH, 223.524,
                               delta=0.01)
        self.assertGreater(flexibles.WRIST_BELT_LENGTH - 208.0, 15.0)

    def test_a_belt_does_not_slip_on_its_pulley(self):
        # What a belt feeds past a point is the arc of the pitch circle it
        # wraps, so one whole turn of the driven pulley must run exactly
        # one circumference of belt.
        for name, travel, teeth in (
                ('elbow', art2.belt_travel, flexibles.ARM_DRIVEN_TEETH),
                ('wrist', art4.belt_travel, flexibles.WRIST_DRIVEN_TEETH)):
            with self.subTest(belt=name):
                circumference = teeth * flexibles.GT2_PITCH
                self.assertAlmostEqual(travel(360.0), circumference,
                                       delta=1e-9)
                self.assertAlmostEqual(travel(0.0), 0.0, delta=1e-12)

    def test_the_belts_circulate_when_their_joints_move(self):
        # The belt is bound to the joint, not to the timeline: it stands
        # still at rest and runs when the joint it carries turns.
        self.pose()
        arm = self.part(ARM)
        self.assertAlmostEqual(float(arm.elbow_belt.travel.value), 0.0,
                               delta=1e-9)
        self.pose(art3=90.0)
        self.assertAlmostEqual(
            float(self.part(ARM).elbow_belt.travel.value),
            art2.belt_travel(90.0), delta=1e-6)

    # -- the elbow is the elbow's own angle --

    def test_swinging_the_shoulder_swings_the_forearm_with_the_arm(self):
        # The correction. The elbow's drive pulley is carried by the
        # shoulder housing, and that was once read as the belt holding the
        # forearm's direction in the machine frame while the shoulder
        # swings. That is true only for equal pulleys: with the motor still
        # a swing of theta turns the 117-tooth elbow pulley against the arm
        # by only -20 theta / 117. `art3` is the elbow's own angle instead,
        # so a shoulder swing carries the forearm round with the arm and
        # leaves the elbow where it was.
        # Both poses are set here. Reading the rest attitude without posing
        # first measures whatever the previous test left behind, which is
        # a contract on the alphabet rather than on the machine.
        self.pose()
        upright = self.forearm_direction()
        self.assertAlmostEqual(self.elbow_angle(), 0.0, delta=1e-9)
        self.pose(art2=25.0)
        self.assertAlmostEqual(self.forearm_direction(), upright + 25.0,
                               delta=0.01)
        self.assertAlmostEqual(self.elbow_angle(), 0.0, delta=1e-9)

    def test_turning_the_elbow_turns_only_the_forearm(self):
        # One slider, one joint: `art3` is the elbow, wherever the shoulder
        # happens to be. Asked with the shoulder off zero, because that is
        # where an absolute reading and a relative one part company.
        self.pose(art2=25.0)
        before = self.forearm_direction()
        arm = self.arm_centroid()
        self.pose(art2=25.0, art3=30.0)
        self.assertAlmostEqual(self.elbow_angle(), 30.0, delta=1e-9)
        self.assertAlmostEqual(self.forearm_direction(), before + 30.0,
                               delta=0.01)
        for axis, (was, now) in enumerate(zip(arm, self.arm_centroid())):
            with self.subTest(axis=axis):
                self.assertAlmostEqual(now, was, delta=1e-6)

    def test_the_elbow_motor_compensates_the_shoulder(self):
        # What the motor on the housing has to do for `art3` to mean the
        # joint: its pulley turns by the shoulder's own swing plus the
        # geared elbow, because the belt sees only the difference between
        # that pulley and the arm.
        for shoulder, elbow in ((0.0, 0.0), (25.0, 0.0), (0.0, 30.0),
                                (25.0, 30.0), (-40.0, -60.0)):
            self.pose(art2=shoulder, art3=elbow)
            with self.subTest(art2=shoulder, art3=elbow):
                self.assertAlmostEqual(
                    float(self.part('shoulder').drive.value),
                    shoulder + ELBOW_RATIO * elbow, delta=1e-9)

    def test_turning_the_elbow_turns_the_forearm(self):
        self.pose()
        upright = self.forearm_height()
        self.pose(art3=90.0)
        self.assertLess(self.forearm_height(), upright - 40.0)

    def forearm_height(self):
        bounds = self.part(FOREARM + '.art3_body').mesh.bounds
        return float(bounds[1][2] - bounds[0][2])

    def forearm_direction(self):
        """The forearm's attitude in the machine frame, degrees about +Y.

        Taken between two points fixed in the forearm — the elbow body and
        the wrist's crown plate — so it answers where the forearm points
        and not where the arm happened to carry it. A turn of theta about
        the shoulder axis adds theta to it.
        """
        near = self.part(FOREARM + '.art3_body').mesh.vertices.mean(axis=0)
        far = self.part(
            WRIST + '.output.art56_gear_plate').mesh.vertices.mean(axis=0)
        return math.degrees(math.atan2(float(far[0] - near[0]),
                                       float(far[2] - near[2])))

    def elbow_angle(self):
        """The elbow joint's own coordinate: the forearm against the arm."""
        return float(self.part(FOREARM).elbow.value)

    def arm_centroid(self):
        """Where the upper arm's own plate stands, in the machine frame."""
        return [float(value) for value in
                self.part(ARM + '.art2_body_a').mesh.vertices.mean(axis=0)]

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


class ThorScenarioTest(ScenarioTest):
    """The demo, driven as the viewer drives it.

    The six instructions in the order a maker would press them, each given
    the time its own mechanism takes, with the machine asked at intervals
    whether it has driven any part through another.

    The interval is coarse on purpose. Every question here is answered on
    solids -- the faceted kernel refuses seven of Thor's meshes -- and a
    whole-machine scan of five hundred solids is minutes, not milliseconds.
    A tighter cadence would not be more honest; it would be the same
    contract run more times than the session can afford, so the sample
    points are stated here rather than hidden in a period.
    """

    node = Thor

    dt = 0.1

    #: The demo, in order, with the duration each instruction declares.
    SCRIPT = ('Home', 'Ready', 'Reach', 'Pick', 'Place', 'Park')

    #: How often the machine is asked whether it is passing through itself,
    #: in seconds of scenario time.
    SAMPLE = 4.0

    def script(self, sim):
        """Trigger the demo in order; return when it ends."""
        when = 0.0
        for name in self.SCRIPT:
            sim.at(round(when / self.dt) * self.dt).trigger(name)
            when += Thor.instructions[name].duration
        return when

    def inventory_holds(self):
        seats.assert_inventory(self, self.node)

    def test_the_demo_never_drives_a_part_through_another(self):
        sim = self.simulation()
        duration = self.script(sim)
        sim.every(self.SAMPLE, self.inventory_holds)
        sim.run(duration)

    def test_every_instruction_lands_exactly_on_its_targets(self):
        for name in self.SCRIPT:
            with self.subTest(instruction=name):
                sim = self.simulation()
                instruction = Thor.instructions[name]
                sim.at(0.0).trigger(name)
                sim.run(instruction.duration)
                for driver, target in instruction.targets.items():
                    self.assertAlmostEqual(sim.state[driver], target,
                                           delta=1e-6)

    def test_no_instruction_asks_for_a_joint_the_machine_has_not_got(self):
        # A range is presentation metadata and clamps nothing, so an
        # instruction outside it is a promise the machine cannot keep and
        # only a contract catches it. `Park` asked for -160 on an elbow
        # that travels to -135.
        ranges = {'art1': BASE_TRAVEL, 'art2': SHOULDER_TRAVEL,
                  'art3': ELBOW_TRAVEL, 'art4': FOREARM_TRAVEL,
                  'art5': WRIST_TRAVEL, 'art6': TOOL_TRAVEL,
                  'grip': (0.0, OPEN)}
        for name in self.SCRIPT:
            for driver, target in Thor.instructions[name].targets.items():
                low, high = ranges[driver]
                with self.subTest(instruction=name, driver=driver):
                    self.assertGreaterEqual(target, low)
                    self.assertLessEqual(target, high)
