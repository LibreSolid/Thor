"""Thor: a 3D-printed six-axis robot arm, assembled from its own parts.

The whole machine, in the frame its FreeCAD assembly uses: Z up, origin on
the mounting face of `BaseBot`. Seven sliders drive it, and every one is a
thing a maker can predict before they move it — this is a six-axis arm and
its axes are its meaning:

======  ====================================================  =======
driver  what it measures                                      unit
======  ====================================================  =======
art1    the base's yaw about Z                                degrees
art2    the shoulder's roll about Y, 202.0 up                 degrees
art3    the forearm's roll in the machine frame, not          degrees
        relative to the upper arm (see below)
art4    the forearm's yaw about its own axis                  degrees
art5    the wrist's roll about Y, 556.0 up                    degrees
art6    the tool's roll about the wrist output axis           degrees
grip    the clear opening between the two jaws                mm
======  ====================================================  =======

`art3` is absolute because the machine is: the belt that sets the elbow
runs from a pulley carried by the shoulder housing, not by the upper arm,
so swinging the shoulder leaves the forearm pointing the same way. Drive
`art2` alone and watch the elbow: nothing about the forearm's direction
changes, and no elbow motor turns.

Everything else follows from those seven: the motors turn at their gearing,
the belts are redrawn between their pulleys, the optical discs turn with
the shafts they read, and the wrist's two motors both turn for either wrist
joint, because a differential is what resolves them.
"""

from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, Instruction

from simulation import layout
from simulation.art1 import Art1
from simulation.base import Base
from simulation.gripper import OPEN

#: How far the base can yaw before its wiring runs out, degrees. The design
#: publishes no joint limits, so this is the full turn the slewing bearing
#: allows, stated as an assumption in the README.
BASE_TRAVEL = (-180.0, 180.0)
#: The shoulder's travel, bounded by the arm meeting the base behind it.
SHOULDER_TRAVEL = (-90.0, 90.0)
#: The elbow's absolute travel.
ELBOW_TRAVEL = (-135.0, 135.0)
#: The forearm's yaw, wrist roll and tool roll.
FOREARM_TRAVEL = (-180.0, 180.0)
WRIST_TRAVEL = (-105.0, 105.0)
TOOL_TRAVEL = (-180.0, 180.0)

#: Rated joint rates, degrees per second, from the slowest thing in each
#: train: the base and shoulder run through planetary gearboxes and their
#: own ring reductions, the wrist through a two-to-one belt and a
#: two-to-one differential.
RATES = {'art1': 30.0, 'art2': 25.0, 'art3': 30.0,
         'art4': 60.0, 'art5': 45.0, 'art6': 60.0}
#: How fast the gripper's servo closes the jaws, millimetres per second.
GRIP_RATE = 45.0


def duration(**targets):
    """How long a move takes at the joint rates the mechanism allows."""
    seconds = [abs(value) / RATES[name]
               for name, value in targets.items() if name in RATES]
    if 'grip' in targets:
        seconds.append(abs(targets['grip'] - OPEN) / GRIP_RATE)
    return max(1.0, round(max(seconds or [0.0]), 1))


class Thor(AssemblyNode):
    """The complete robot: base, arm, wrist and gripper."""

    art1 = Driver(default=0.0, range=BASE_TRAVEL, unit='deg')
    art2 = Driver(default=0.0, range=SHOULDER_TRAVEL, unit='deg')
    art3 = Driver(default=0.0, range=ELBOW_TRAVEL, unit='deg')
    art4 = Driver(default=0.0, range=FOREARM_TRAVEL, unit='deg')
    art5 = Driver(default=0.0, range=WRIST_TRAVEL, unit='deg')
    art6 = Driver(default=0.0, range=TOOL_TRAVEL, unit='deg')
    grip = Driver(default=OPEN, range=(0.0, OPEN), unit='mm')

    base = Base()
    shoulder = Art1()

    # Every driver reaches the freedom it names, wherever that freedom
    # lives: a relation walks the tree by path, so nothing between the
    # root and a joint five levels down has to carry a value it does not
    # itself use. `art3` is the one that is not a joint, because it is
    # not a freedom of one body: it is the forearm's angle in the machine
    # frame, and the shoulder housing works out the elbow from it.
    art1.drives(base.yaw)
    art1.drives(shoulder.yaw)
    art2.drives(shoulder.art2.shoulder)
    art3.drives(shoulder.elbow_absolute)
    art4.drives(shoulder.art2.art3.art4.yaw)
    art5.drives(shoulder.art2.art3.art4.art56.wrist)
    art6.drives(shoulder.art2.art3.art4.art56.output.tool)
    grip.drives(shoulder.art2.art3.art4.art56.output.gripper.grip)

    instructions = {
        'Home': Instruction(
            {'art1': 0.0, 'art2': 0.0, 'art3': 0.0, 'art4': 0.0,
             'art5': 0.0, 'art6': 0.0, 'grip': OPEN},
            duration=4.0),
        'Ready': Instruction(
            {'art1': 0.0, 'art2': 35.0, 'art3': -55.0, 'art4': 0.0,
             'art5': 20.0, 'art6': 0.0, 'grip': OPEN},
            duration=3.0),
        'Reach': Instruction(
            {'art1': 0.0, 'art2': 60.0, 'art3': -20.0, 'art4': 0.0,
             'art5': -40.0, 'art6': 0.0, 'grip': OPEN},
            duration=3.0),
        'Pick': Instruction(
            {'art1': 0.0, 'art2': 60.0, 'art3': -20.0, 'art4': 0.0,
             'art5': -40.0, 'art6': 0.0, 'grip': 12.0},
            duration=2.0),
        'Place': Instruction(
            {'art1': 90.0, 'art2': 60.0, 'art3': -20.0, 'art4': 0.0,
             'art5': -40.0, 'art6': 90.0, 'grip': OPEN},
            duration=5.0),
        # Folded to the elbow's own limit, not past it: -160 was outside
        # ELBOW_TRAVEL, which is the sort of thing a range is for.
        'Park': Instruction(
            {'art1': 0.0, 'art2': 80.0, 'art3': -135.0, 'art4': 0.0,
             'art5': 80.0, 'art6': 0.0, 'grip': 0.0},
            duration=5.0),
    }

    def render(self):
        self.shoulder.translate(
            list(layout.link('root', 'AssemblyArt1').translate))
