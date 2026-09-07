"""Measure the design's own geometry: meshes, holes, pockets, overlaps.

A measurement tool, like `freecad_doc`. Nothing in the model imports it at
build time; what it reads is written into `docs/measurements.md` and
transcribed into `simulation/layout.py` and `simulation/fasteners.py`,
where the framework's source tracking can see it.
"""

from __future__ import annotations

import itertools
import math
import os

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_SurfaceType

from simulation import layout

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
STEP_DIR = os.path.join(PROJECT, 'step')

#: Which sub-assembly each one hangs from, so a world placement can be
#: composed. `None` means the root itself carries it.
PARENT = {
    'AssemblyBase': None,
    'AssemblyArt1': None,
    'AssemblyArt2': 'AssemblyArt1',
    'AssemblyArt3': 'AssemblyArt2',
    'AssemblyArt4': 'AssemblyArt3',
    'AssemblyArt56': 'AssemblyArt4',
}

_shapes = {}


def part_shape(name):
    """The exact solid of one published printed part, in its own frame."""
    if name not in _shapes:
        _shapes[name] = cq.importers.importStep(
            os.path.join(STEP_DIR, name + '.step')).val()
    return _shapes[name]


def location(placed):
    axis = cq.Vector(*placed.axis)
    if axis.Length < 1e-9:
        axis = cq.Vector(0, 0, 1)
    return cq.Location(cq.Vector(*placed.translate), axis, placed.angle)


def group_location(group):
    """Where a sub-assembly's own frame sits in the machine frame."""
    if group == 'root':
        return cq.Location()
    return location(layout.link('root', group))


def placed_shape(group, label, phase=0.0):
    """One printed instance's solid, in the machine frame.

    `phase` turns the part about its own Z first, which is how a printed
    gear is put on its shaft.
    """
    placed = layout.link(group, label)
    where = group_location(group) * location(placed)
    if phase:
        where = where * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1),
                                    phase)
    return part_shape(layout.part_name(placed)).located(where)


def shared_volume(a, b):
    solids = a.intersect(b).Solids()
    return sum(s.Volume() for s in solids)


# --- fastener features ----------------------------------------------------

#: Radii the design cuts for fasteners, measured across the whole machine.
CLEARANCE_RADII = {1.70: 'M3', 2.10: 'M4'}
#: Radius of the socket-head counterbore the design cuts.
HEAD_RADIUS = 2.95
#: Distance from a hex pocket's axis to each of its six flats: a 5.5 mm
#: nut with 0.3 mm of print clearance.
POCKET_FLAT = 2.90


def cylindrical_faces(shape):
    """Every cylindrical face, with its radius, axis and axial extent."""
    out = []
    for face in shape.Faces():
        adaptor = BRepAdaptor_Surface(face.wrapped)
        if adaptor.GetType() != GeomAbs_SurfaceType.GeomAbs_Cylinder:
            continue
        cylinder = adaptor.Cylinder()
        direction = cylinder.Axis().Direction()
        point = cylinder.Axis().Location()
        box = face.BoundingBox()
        out.append({
            'radius': cylinder.Radius(),
            'axis': (direction.X(), direction.Y(), direction.Z()),
            'point': (point.X(), point.Y(), point.Z()),
            'bounds': (box.xmin, box.ymin, box.zmin,
                       box.xmax, box.ymax, box.zmax),
        })
    return out


def planar_faces(shape):
    out = []
    for face in shape.Faces():
        adaptor = BRepAdaptor_Surface(face.wrapped)
        if adaptor.GetType() != GeomAbs_SurfaceType.GeomAbs_Plane:
            continue
        plane = adaptor.Plane()
        normal = plane.Axis().Direction()
        point = plane.Location()
        box = face.BoundingBox()
        out.append({
            'normal': (normal.X(), normal.Y(), normal.Z()),
            'point': (point.X(), point.Y(), point.Z()),
            'area': face.Area(),
            'bounds': (box.xmin, box.ymin, box.zmin,
                       box.xmax, box.ymax, box.zmax),
        })
    return out


# --- mesh windows --------------------------------------------------------


def trimmed_mate(driver, driven, margin=1.0):
    """The mate, cut down to the box the driver sweeps through.

    Sweeping a gear pair means one boolean per phase, and the crown plate
    is thirteen megabytes of STEP: intersecting the whole of it once per
    degree costs minutes. Only the teeth the pinion can reach matter, so
    the mate is trimmed to the driver's own bounding box once, and the
    sweep then runs on a solid the size of the pinion.
    """
    box = placed_shape(*driver).BoundingBox()
    trim = (cq.Workplane('XY')
            .box(box.xlen + 2 * margin, box.ylen + 2 * margin,
                 box.zlen + 2 * margin)
            .translate(((box.xmin + box.xmax) / 2,
                        (box.ymin + box.ymax) / 2,
                        (box.zmin + box.zmax) / 2)).val())
    return placed_shape(*driven).intersect(trim)


def mesh_window(driver, driven, pitch, step=1.0, mate=None,
                start=0.0, end=None, tolerance=1e-3):
    """Where a printed gear clears its mate, sweeping one tooth pitch.

    `driver` and `driven` are (group, label) pairs; `pitch` is 360 divided
    by the driver's tooth count.

    Some of Thor's pairs never reach zero: a pinion's rim can foul the
    shoulder above the teeth it drives whatever phase it is put on, and
    that overlap is a property of the two parts, not of the phase. The
    sweep therefore reports the **floor** — the least volume any phase
    achieves — and calls a phase clear when it is within `tolerance` of
    that floor. A floor above zero is a finding about the design and
    belongs in the seats inventory; the window around it is still the
    pair's backlash and the bound its engagement contracts use.
    """
    if mate is None:
        mate = trimmed_mate(driver, driven)
    if end is None:
        end = pitch
    samples = []
    phase = start
    while phase < end - 1e-9:
        volume = shared_volume(placed_shape(*driver, phase=phase), mate)
        samples.append((round(phase, 3), round(volume, 4)))
        phase = round(phase + step, 6)
    floor = min(v for _, v in samples)
    clear = [p for p, v in samples if v <= floor + tolerance]
    runs = []
    for value in clear:
        if runs and abs(value - runs[-1][-1] - step) < 1e-6:
            runs[-1].append(value)
        else:
            runs.append([value])
    if len(runs) > 1 and runs[0][0] == 0.0 and \
            abs(runs[-1][-1] + step - pitch) < 1e-6:
        runs[0] = [v - pitch for v in runs[-1]] + runs[0]
        runs.pop()
    widest = max(runs, key=len) if runs else []
    centre = (widest[0] + widest[-1]) / 2.0 if widest else None
    return {'samples': samples, 'window': widest, 'floor': round(floor, 4),
            'centre': None if centre is None else round(centre % pitch, 3),
            'width': round(widest[-1] - widest[0], 3) if widest else 0.0}


# --- fastener stacks ------------------------------------------------------
#
# The design models no fastener at all, so every screw and nut in the model
# is derived from the printed parts' own geometry: the holes they cut for a
# shank, the counterbores they cut for a head, and the hex pockets they cut
# for a nut. Nothing here is chosen; the only judgement is which end of a
# stack a head goes on, and a stack the rule cannot settle is reported
# rather than given a default.

#: Standard M3 lengths, mm, in the sizes a hardware shop sells.
M3_LENGTHS = (6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70,
              80, 90, 100, 110, 120, 130, 140, 150)
#: Standard M4 lengths, mm.
M4_LENGTHS = (8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50)

#: An M3 nut is 2.40 thick and 5.5 across flats; the design's pockets are
#: 5.80, a 0.3 mm print clearance.
NUT_THICKNESS = {'M3': 2.40, 'M4': 3.20}
#: A socket head is 5.5 across and 3.0 tall for M3.
HEAD_DIAMETER = {'M3': 5.50, 'M4': 7.00}
HEAD_HEIGHT = {'M3': 3.00, 'M4': 4.00}

#: How far apart two parts' holes may be along one axis and still be one
#: fastener. Beyond this the cluster crosses a gap in the machine and is
#: two fasteners, not one long screw.
STACK_GAP = 1.0
#: How far a thread must stand past its nut.
NUT_PROTRUSION = 0.5

#: How close two axes must be to be the same axis.
AXIS_TOLERANCE = 1e-4
LINE_TOLERANCE = 0.15


def _unit(vector):
    length = math.sqrt(sum(v * v for v in vector))
    return tuple(v / length for v in vector)


def _canonical(direction):
    direction = _unit(direction)
    for value in direction:
        if abs(value) > 1e-9:
            return direction if value > 0 else tuple(-v for v in direction)
    return direction


def _along(point, origin, direction):
    return sum((p - o) * d for p, o, d in zip(point, origin, direction))


def _perpendicular_distance(point, origin, direction):
    along = _along(point, origin, direction)
    return math.sqrt(sum((p - o - along * d) ** 2
                         for p, o, d in zip(point, origin, direction)))


def local_shape(group, label, phase=0.0):
    """One printed instance's solid, in its **sub-assembly's** own frame."""
    placed = layout.link(group, label)
    where = location(placed)
    if phase:
        where = where * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1),
                                    phase)
    return part_shape(layout.part_name(placed)).located(where)


def fastener_features(group, phases=None):
    """Every fastener-sized hole, counterbore and hex pocket in one link.

    Fasteners are derived one sub-assembly at a time, in that
    sub-assembly's own frame, because a screw holds one rigid link
    together: two parts a screw joins cannot move relative to each other,
    so they are parts of one link by definition. Deriving in world
    coordinates instead would let a cluster reach across a joint and
    invent a screw through it.

    `phases` maps a design label to the phase the model puts that part on,
    so a gear's holes are found where the model actually has them.
    """
    phases = phases or {}
    holes, heads, pockets = [], [], []
    for placed in layout.printed(group):
        label = placed.label
        shape = local_shape(group, label, phase=phases.get(label, 0.0))
        where = label
        for face in cylindrical_faces(shape):
            radius = round(face['radius'], 2)
            kind = CLEARANCE_RADII.get(radius)
            if kind is not None:
                holes.append(dict(face, part=where, kind=kind))
            elif abs(radius - HEAD_RADIUS) < 0.06:
                heads.append(dict(face, part=where))
        pockets.extend(_hex_pockets(shape, where))
    return holes, heads, pockets


def _hex_pockets(shape, where):
    """Six planes 2.90 from a common axis, sixty degrees apart: a nut trap."""
    planes = [p for p in planar_faces(shape) if p['area'] < 30.0]
    found = []
    for face in cylindrical_faces(shape):
        if abs(round(face['radius'], 2) - 1.70) > 0.05:
            continue
        axis = _canonical(face['axis'])
        origin = face['point']
        flats = []
        for plane in planes:
            if abs(sum(n * a for n, a in zip(plane['normal'], axis))) > 0.02:
                continue
            offset = sum((p - o) * n for p, o, n
                         in zip(plane['point'], origin, plane['normal']))
            if abs(abs(offset) - POCKET_FLAT) > 0.06:
                continue
            flats.append(plane)
        if len(flats) < 5:
            continue
        starts = [_along((b[0], b[1], b[2]), origin, axis)
                  for b in (f['bounds'] for f in flats)]
        ends = [_along((b[3], b[4], b[5]), origin, axis)
                for b in (f['bounds'] for f in flats)]
        low = min(min(starts), min(ends))
        high = max(max(starts), max(ends))
        found.append({'part': where, 'axis': axis, 'point': origin,
                      'span': (low, high)})
    return found


def cluster_axes(features):
    """Group features onto shared axis lines."""
    clusters = []
    for feature in features:
        axis = _canonical(feature['axis'])
        point = feature['point']
        for cluster in clusters:
            if abs(sum(a * b for a, b in zip(axis, cluster['axis']))) < \
                    1.0 - AXIS_TOLERANCE:
                continue
            if _perpendicular_distance(point, cluster['point'],
                                       cluster['axis']) > LINE_TOLERANCE:
                continue
            cluster['members'].append(feature)
            break
        else:
            clusters.append({'axis': axis, 'point': point,
                             'members': [feature]})
    return clusters


def _span_of(face, origin, axis):
    x0, y0, z0, x1, y1, z1 = face['bounds']
    values = [_along((x, y, z), origin, axis)
              for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    return min(values), max(values)


def _merge(spans, gap):
    ordered = sorted(spans)
    merged = []
    for low, high in ordered:
        if merged and low <= merged[-1][1] + gap:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
        else:
            merged.append((low, high))
    return merged


def fastener_stacks(group, phases=None):
    """Every screw one link's own holes imply, and its nut.

    Returns a list of dicts: the axis and its origin in the link's own
    frame, the two ends of the stack along it, which parts it passes
    through, whether a head counterbore and a nut pocket were found and
    where, the size, and the shortest standard length that spans it. A
    stack the head rule cannot settle carries `undecided`; a stack that
    passes through one part with neither a counterbore nor a pocket is
    marked `unclassified`, because nothing in the geometry says whether it
    takes a screw at all.
    """
    holes, heads, pockets = fastener_features(group, phases)
    clusters = cluster_axes(holes)
    stacks = []
    for cluster in clusters:
        axis, origin = cluster['axis'], cluster['point']
        kind = 'M4' if any(h['kind'] == 'M4' for h in cluster['members']) \
            else 'M3'
        spans = [_span_of(hole, origin, axis) for hole in cluster['members']]
        for low, high in _merge(spans, STACK_GAP):
            parts = sorted({hole['part'] for hole, span
                            in zip(cluster['members'], spans)
                            if span[0] < high + STACK_GAP
                            and span[1] > low - STACK_GAP})
            counterbores = [_span_of(head, origin, axis) for head in heads
                            if abs(sum(a * b for a, b
                                       in zip(_canonical(head['axis']), axis)))
                            > 1.0 - AXIS_TOLERANCE
                            and _perpendicular_distance(head['point'], origin,
                                                        axis) < LINE_TOLERANCE
                            and low - STACK_GAP < _span_of(head, origin,
                                                           axis)[1]
                            and _span_of(head, origin, axis)[0] <
                            high + STACK_GAP]
            traps = [pocket['span'] for pocket in pockets
                     if abs(sum(a * b for a, b in zip(pocket['axis'], axis)))
                     > 1.0 - AXIS_TOLERANCE
                     and _perpendicular_distance(pocket['point'], origin,
                                                 axis) < LINE_TOLERANCE
                     and low - STACK_GAP < pocket['span'][1]
                     and pocket['span'][0] < high + STACK_GAP]
            stacks.append(_describe(axis, origin, low, high, parts, kind,
                                    counterbores, traps))
    return stacks


def _describe(axis, origin, low, high, parts, kind, counterbores, traps):
    """Turn one contiguous hole stack into the screw it takes."""
    head_end = None
    if counterbores:
        near = min(c[0] for c in counterbores)
        far = max(c[1] for c in counterbores)
        head_end = 'low' if abs(near - low) < abs(far - high) else 'high'
    nut_end = None
    nut_span = None
    if traps:
        near = min(t[0] for t in traps)
        far = max(t[1] for t in traps)
        nut_end = 'low' if abs(near - low) < abs(far - high) else 'high'
        nut_span = (round(near, 3), round(far, 3))
    if head_end is None and nut_end is not None:
        head_end = 'high' if nut_end == 'low' else 'low'
    undecided = head_end is None
    if undecided:
        head_end = 'low'
    grip = high - low
    needed = grip + NUT_PROTRUSION
    if nut_end is not None:
        needed += NUT_THICKNESS[kind]
    lengths = M3_LENGTHS if kind == 'M3' else M4_LENGTHS
    length = next((value for value in lengths if value >= needed),
                  lengths[-1])
    unclassified = (len(parts) < 2 and not counterbores and not traps)
    return {'axis': axis, 'origin': origin, 'low': round(low, 3),
            'high': round(high, 3), 'grip': round(grip, 3), 'kind': kind,
            'parts': parts, 'head_end': head_end, 'nut_end': nut_end,
            'counterbored': bool(counterbores), 'length': length,
            'undecided': undecided, 'unclassified': unclassified,
            'nut_span': nut_span}
