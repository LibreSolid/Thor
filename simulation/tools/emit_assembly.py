"""Emit the skeleton of a sub-assembly module from the design's own assembly.

Run from the project root, e.g.::

    python -m simulation.tools.emit_assembly AssemblyArt1

It writes one declared child per placed instance, named after the part or
component the design uses, and the label-to-attribute map `render()` places
them by. The emitted module is a starting point: motion, ports and grouping
are written by hand on top of it.
"""

import re
import sys
from collections import Counter

from simulation import layout

#: Bought components whose geometry is a printed part after all.
MIRRORED_PARTS = {'GripperFinger_sym': 'GripperFingerMirrored'}


#: Component labels that begin with a digit, which no attribute may.
SHAFT_NAMES = {'4x14mm': 'shaft_4x14', '5x14.5mm': 'shaft_5x14_5',
               '5x32mm': 'shaft_5x32', '5x128mm': 'shaft_5x128',
               'Shaft_5x102mm': 'shaft_5x102'}


def snake(name):
    if name in SHAFT_NAMES:
        return SHAFT_NAMES[name]
    name = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', name)
    name = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', '_', name)
    name = name.replace('.', '_').replace('-', '_')
    return re.sub(r'_+', '_', name).strip('_').lower()


def kind(placed):
    """What a placed instance is an instance of."""
    if placed.source is not None:
        return layout.part_name(placed)
    return placed.component


def attribute_names(group):
    """One attribute name per instance, numbered where a kind repeats."""
    kinds = [kind(p) for p in layout.links(group)]
    totals = Counter(kinds)
    seen = Counter()
    names = {}
    for placed, this in zip(layout.links(group), kinds):
        base = snake(this)
        if totals[this] > 1:
            seen[this] += 1
            base = '%s_%d' % (base, seen[this])
        names[placed.label] = base
    return names


def emit(group):
    names = attribute_names(group)
    lines = ['PLACEMENT = {']
    for placed in layout.links(group):
        lines.append('    %r: %r,' % (placed.label, names[placed.label]))
    lines.append('}')
    lines.append('')
    lines.append('')
    lines.append('# declared children')
    for placed in layout.links(group):
        this = kind(placed)
        if placed.source is not None:
            call = 'parts.%s()' % this
        elif this in MIRRORED_PARTS:
            call = 'parts.%s()' % MIRRORED_PARTS[this]
        else:
            call = 'CATALOGUE[%r]()' % this
        lines.append('    %s = %s' % (names[placed.label], call))
    return '\n'.join(lines)


if __name__ == '__main__':
    print(emit(sys.argv[1]))
