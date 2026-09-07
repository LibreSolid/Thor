"""Emit `simulation/layout.py`'s placement tables from the design's assembly.

Run from the project root:

    python -m simulation.tools.emit_layout > simulation/_layout_tables.py

The output is pasted into `layout.py`. `simulation/test_layout.py` re-reads
the FreeCAD documents independently and fails if the two disagree, so a
hand edit or an upstream change cannot pass unnoticed.
"""

from simulation.tools.freecad_doc import SUB_ASSEMBLIES, read_assembly


def literal(value):
    if isinstance(value, tuple):
        return '(' + ', '.join(literal(v) for v in value) + ')'
    if isinstance(value, float):
        text = repr(round(value + 0.0, 4))
        return text
    return repr(value)


def emit():
    data = read_assembly()
    lines = []
    lines.append('LINKS = {')
    for group in ['root'] + list(SUB_ASSEMBLIES):
        lines.append('    %r: (' % group)
        for item in data[group]:
            lines.append('        Placed(%s, %s, %s, %s, %s, %s),' % (
                literal(item['label']),
                literal(item['source']),
                literal(item['component']),
                literal(item['translate']),
                literal(item['axis']),
                literal(item['angle'])))
        lines.append('    ),')
    lines.append('}')
    return '\n'.join(lines)


if __name__ == '__main__':
    print(emit())
