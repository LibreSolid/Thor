"""The fastener table has not drifted from the parts' own holes.

`simulation/fasteners.py` is a transcription of what
`simulation.tools.geometry.fastener_stacks` reads out of the printed
parts' STEP solids. The framework's source tracking cannot see a probe
that opens those files at test time, so the table has to live in Python;
this is what keeps it honest. An upstream change to a part, or a hand edit
to the table, fails here rather than quietly serving a screw that fits
nothing.
"""

import unittest

from simulation import fasteners, layout
from simulation.tools.freecad_doc import SUB_ASSEMBLIES
from simulation.tools.geometry import fastener_stacks

PHASES = {label: mesh.phase for label, mesh in layout.MESH.items()}

TOLERANCE = 0.001


class FastenerDriftTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.read = {}
        for group in SUB_ASSEMBLIES:
            stacks = fastener_stacks(group, PHASES)
            cls.read[group] = sorted(
                (s for s in stacks if not s['unclassified']),
                key=lambda s: (round(s['origin'][0], 3),
                               round(s['origin'][1], 3),
                               round(s['origin'][2], 3), s['low']))

    def test_every_link_is_transcribed(self):
        self.assertEqual(set(fasteners.STACKS), set(SUB_ASSEMBLIES))

    def test_the_same_stacks_are_present(self):
        for group, stacks in self.read.items():
            self.assertEqual(len(fasteners.STACKS[group]), len(stacks),
                             '%s: the number of fasteners has changed' % group)

    def test_every_stack_agrees(self):
        for group, stacks in self.read.items():
            for recorded, read in zip(fasteners.STACKS[group], stacks):
                where = '%s at %s' % (group, recorded.origin)
                self.assertEqual(recorded.kind, read['kind'], where)
                self.assertEqual(recorded.length, read['length'], where)
                self.assertEqual(recorded.head_end, read['head_end'], where)
                for a, b in zip(recorded.axis, read['axis']):
                    self.assertAlmostEqual(a, b, delta=TOLERANCE, msg=where)
                for a, b in zip(recorded.origin, read['origin']):
                    self.assertAlmostEqual(a, b, delta=TOLERANCE, msg=where)
                self.assertAlmostEqual(recorded.low, read['low'],
                                       delta=TOLERANCE, msg=where)
                self.assertAlmostEqual(recorded.high, read['high'],
                                       delta=TOLERANCE, msg=where)
                self.assertEqual(recorded.nut_span is None,
                                 read['nut_span'] is None, where)

    def test_the_totals_are_what_the_measurements_record(self):
        # docs/measurements.md states these; a change to either without
        # the other is a documentation drift, not a silent improvement.
        total = sum(len(v) for v in fasteners.STACKS.values())
        nuts = sum(len(fasteners.nuts_of(g)) for g in fasteners.STACKS)
        self.assertEqual(total, 181)
        self.assertEqual(nuts, 77)


if __name__ == '__main__':
    unittest.main()
