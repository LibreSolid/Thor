"""Emit `simulation/fasteners.py`'s table from the printed parts' own holes.

Run from the project root:

    python -m simulation.tools.emit_fasteners

The design models no fastener at all, so every screw and nut in the model
comes from this: `simulation.tools.geometry.fastener_stacks` reads the
Ø3.4 clearance holes, the Ø5.9 socket-head counterbores and the 5.80
across-flats hex pockets out of each link's own STEP solids, clusters them
onto shared axes, splits each axis into contiguous stacks, and fits the
shortest standard length that spans each one.

`simulation/test_fasteners.py` re-runs the probe and compares the table
entry for entry, so a hand edit or an upstream change fails there.
"""

from simulation import layout
from simulation.tools.freecad_doc import SUB_ASSEMBLIES
from simulation.tools.geometry import fastener_stacks

PHASES = {label: mesh.phase for label, mesh in layout.MESH.items()}


def collect():
    out = {}
    for group in SUB_ASSEMBLIES:
        stacks = fastener_stacks(group, PHASES)
        out[group] = sorted(
            (s for s in stacks if not s['unclassified']),
            key=lambda s: (round(s['origin'][0], 3), round(s['origin'][1], 3),
                           round(s['origin'][2], 3), s['low']))
    return out


def emit():
    lines = ['STACKS = {']
    for group, stacks in collect().items():
        lines.append('    %r: (' % group)
        for s in stacks:
            lines.append(
                '        Fastener(%r, %d, (%s), (%s), %s, %s, %r, %s),' % (
                    s['kind'], s['length'],
                    ', '.join('%.6f' % v for v in s['axis']),
                    ', '.join('%.4f' % v for v in s['origin']),
                    round(s['low'], 4), round(s['high'], 4), s['head_end'],
                    None if s['nut_span'] is None
                    else '(%.4f, %.4f)' % s['nut_span']))
        lines.append('    ),')
    lines.append('}')
    return '\n'.join(lines)


if __name__ == '__main__':
    print(emit())
