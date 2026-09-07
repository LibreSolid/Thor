"""The transcribed layout has not drifted from the design's own assembly.

`layout.LINKS` is a transcription. The framework's source tracking cannot
see a zip file read at runtime, so the numbers have to live in Python; this
test is what keeps them honest. It re-reads every
``freecad-src/Assembly*.FCStd`` and compares entry for entry, in both
directions, so an upstream change or a hand edit fails here rather than
quietly serving a wrong machine.
"""

import math
import unittest

from simulation import layout
from simulation.tools.freecad_doc import SUB_ASSEMBLIES, read_assembly

TRANSLATION_TOLERANCE = 0.001   # mm
ANGLE_TOLERANCE = 0.001         # degrees


def same_rotation(axis_a, angle_a, axis_b, angle_b):
    """Two (axis, angle) pairs naming the same rotation.

    A rotation has two spellings — the axis negated and the angle taken the
    other way round the circle — and a zero rotation has any axis at all.
    """
    angle_a %= 360.0
    angle_b %= 360.0
    if min(angle_a, 360.0 - angle_a) < ANGLE_TOLERANCE:
        return min(angle_b, 360.0 - angle_b) < ANGLE_TOLERANCE
    dot = sum(x * y for x, y in zip(axis_a, axis_b))
    if dot < 0:
        axis_b = tuple(-v for v in axis_b)
        angle_b = 360.0 - angle_b
        dot = -dot
    if abs(dot - 1.0) > 1e-4:
        return False
    return abs(angle_a - angle_b) < ANGLE_TOLERANCE


class LayoutDriftTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.assembly = read_assembly()

    def test_every_group_is_transcribed(self):
        self.assertEqual(set(layout.LINKS),
                         {'root'} | set(SUB_ASSEMBLIES))

    def test_the_same_instances_are_present(self):
        for group, read in self.assembly.items():
            transcribed = [p.label for p in layout.LINKS[group]]
            self.assertEqual(transcribed, [r['label'] for r in read],
                             'instances of %s differ' % group)

    def test_every_placement_agrees(self):
        for group, read in self.assembly.items():
            for placed, source in zip(layout.LINKS[group], read):
                where = '%s/%s' % (group, placed.label)
                for axis_name, a, b in zip('xyz', placed.translate,
                                           source['translate']):
                    self.assertAlmostEqual(
                        a, b, delta=TRANSLATION_TOLERANCE,
                        msg='%s: %s translation' % (where, axis_name))
                self.assertEqual(placed.component, source['component'],
                                 '%s: component' % where)
                self.assertTrue(
                    same_rotation(placed.axis, placed.angle,
                                  source['axis'], source['angle']),
                    '%s: rotation %s/%s against %s/%s'
                    % (where, placed.axis, placed.angle,
                       source['axis'], source['angle']))

    def test_every_printed_instance_names_a_published_step_file(self):
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for group in layout.LINKS:
            if group == 'root':
                continue          # the root's sources are sub-assemblies
            for placed in layout.printed(group):
                path = os.path.join(root, 'step',
                                    layout.part_name(placed) + '.step')
                self.assertTrue(os.path.exists(path),
                                '%s: no %s' % (placed.label, path))

    def test_the_joint_heights_are_the_assembly_s_own(self):
        shoulder = layout.link('root', 'AssemblyArt2')
        wrist = layout.link('root', 'AssemblyArt56')
        art3 = layout.link('root', 'AssemblyArt3')
        pulley = layout.link('AssemblyArt3', 'Art3Pulley_Art3Pulley')
        self.assertAlmostEqual(shoulder.translate[2], layout.SHOULDER_Z,
                               delta=TRANSLATION_TOLERANCE)
        self.assertAlmostEqual(wrist.translate[2], layout.WRIST_Z,
                               delta=TRANSLATION_TOLERANCE)
        # The Art3 link is turned 180 degrees about Y, so a height inside it
        # subtracts from the link's own.
        self.assertAlmostEqual(art3.translate[2] - pulley.translate[2],
                               layout.ELBOW_Z, delta=TRANSLATION_TOLERANCE)


if __name__ == '__main__':
    unittest.main()
