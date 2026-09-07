"""Read FreeCAD .FCStd documents without FreeCAD.

A .FCStd file is a zip holding ``Document.xml`` plus one ``.brp`` per shape.
This module reads the object graph, the placements and, on request, the
shapes, so the design's own solved assembly can be measured.

It is a measurement tool. Nothing in ``simulation/`` imports it at build
time: the numbers it produces are transcribed into ``simulation/layout.py``
and a test re-runs the probe to prove the transcription has not drifted.
"""

from __future__ import annotations

import math
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile

FREECAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'freecad-src')

SUB_ASSEMBLIES = ('AssemblyBase', 'AssemblyArt1', 'AssemblyArt2',
                  'AssemblyArt3', 'AssemblyArt4', 'AssemblyArt56')

# Object types that carry printable geometry, as opposed to datum planes,
# axes and origins, which also carry a Shape but have infinite extent.
SOLID_TYPES = frozenset({
    'Part::Feature', 'Part::FeaturePython', 'Part::Compound',
    'Part::MultiFuse', 'Part::Cut', 'Part::Mirroring',
    'Part::Sphere', 'Part::Cylinder', 'Part::Box',
    'PartDesign::Pad', 'PartDesign::Body',
})

IDENTITY = ([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            [0.0, 0.0, 0.0])


# --- small matrix helpers -------------------------------------------------

def matrix_from_quaternion(q, t):
    """FreeCAD stores rotations as (x, y, z, w)."""
    x, y, z, w = q
    R = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return R, list(t)


def compose(outer, inner):
    """The placement `inner` expressed in `outer`'s parent frame."""
    Ra, ta = outer
    Rb, tb = inner
    R = [[sum(Ra[i][k] * Rb[k][j] for k in range(3)) for j in range(3)]
         for i in range(3)]
    t = [sum(Ra[i][k] * tb[k] for k in range(3)) + ta[i] for i in range(3)]
    return R, t


def axis_angle(R):
    """The (axis, degrees) pair that reproduces R as a single rotation."""
    trace = R[0][0] + R[1][1] + R[2][2]
    cos = max(-1.0, min(1.0, (trace - 1.0) / 2.0))
    angle = math.acos(cos)
    if angle < 1e-9:
        return (0.0, 0.0, 1.0), 0.0
    if abs(angle - math.pi) < 1e-6:
        k = max(range(3), key=lambda i: R[i][i])
        axis = [0.0, 0.0, 0.0]
        axis[k] = math.sqrt(max(0.0, (R[k][k] + 1.0) / 2.0))
        for j in range(3):
            if j != k:
                axis[j] = (R[k][j] + R[j][k]) / (4.0 * axis[k])
        norm = math.sqrt(sum(v * v for v in axis))
        return tuple(v / norm for v in axis), 180.0
    s = 2.0 * math.sin(angle)
    axis = ((R[2][1] - R[1][2]) / s,
            (R[0][2] - R[2][0]) / s,
            (R[1][0] - R[0][1]) / s)
    return axis, math.degrees(angle)


def invert(M):
    """The placement that undoes M."""
    R, t = M
    Ri = [[R[j][i] for j in range(3)] for i in range(3)]
    ti = [-sum(Ri[i][k] * t[k] for k in range(3)) for i in range(3)]
    return Ri, ti


def apply_point(M, v):
    R, t = M
    return [sum(R[i][k] * v[k] for k in range(3)) + t[i] for i in range(3)]


def apply_direction(M, v):
    R, _ = M
    return [sum(R[i][k] * v[k] for k in range(3)) for i in range(3)]


# --- the document ---------------------------------------------------------

class Document:
    """One .FCStd file's object graph."""

    def __init__(self, path):
        self.path = path
        self.zip = zipfile.ZipFile(path)
        root = ET.fromstring(self.zip.read('Document.xml'))
        self.types = {o.get('name'): o.get('type')
                      for o in root.find('Objects') if o.tag == 'Object'}
        self.objects = {}
        for node in root.find('ObjectData'):
            name = node.get('name')
            obj = {'name': name, 'type': self.types.get(name), 'label': None,
                   'placement': None, 'link': None, 'group': [],
                   'elements': [], 'shape': None, 'visible': True}
            for prop in node.find('Properties'):
                children = list(prop)
                if not children:
                    continue
                value = children[0]
                key = prop.get('name')
                if key == 'Placement':
                    obj['placement'] = self._placement(value)
                elif key == 'LinkedObject':
                    obj['link'] = (value.get('file') or None, value.get('name'))
                elif key == 'Label':
                    obj['label'] = value.get('value')
                elif key == 'Group':
                    obj['group'] = [e.get('value') for e in value]
                elif key in ('ElementList', 'LinkedChildren'):
                    obj['elements'] = [e.get('value') for e in value]
                elif key == 'Shape':
                    obj['shape'] = value.get('file')
                elif key == 'Visibility':
                    obj['visible'] = value.get('value') == 'true'
            self.objects[name] = obj

    @staticmethod
    def _placement(element):
        a = element.attrib
        return {'t': (float(a['Px']), float(a['Py']), float(a['Pz'])),
                'q': (float(a['Q0']), float(a['Q1']),
                      float(a['Q2']), float(a['Q3']))}

    # -- structure --

    def part_links(self):
        """The Assembly4 part links: the children of the `Model` App::Part.

        Assembly4 solves the assembly and writes each link's resulting
        global placement into the link itself, so these placements are the
        design's own answer and not a reconstruction of it.
        """
        model = self.objects['Model']
        out = []
        for name in model['group']:
            obj = self.objects.get(name)
            if obj and obj['type'] == 'App::Link' and obj['placement']:
                out.append(obj)
        return out

    def matrix(self, obj):
        return matrix_from_quaternion(obj['placement']['q'],
                                      obj['placement']['t'])

    def internal_targets(self):
        """Names of in-document App::Parts that links point at.

        These are the bought components: the design places them but does
        not publish them as printable parts.
        """
        out = set()
        for obj in self.objects.values():
            link = obj['link']
            if link and link[0] is None:
                target = self.objects.get(link[1])
                if target is not None and target['type'] == 'App::Part':
                    out.add(link[1])
        return out

    def solid_leaves(self, name, parent=IDENTITY):
        """Yield (object, world matrix) for every solid-bearing leaf."""
        obj = self.objects.get(name)
        if obj is None:
            return
        matrix = parent
        if obj['placement']:
            matrix = compose(parent, self.matrix(obj))
        if obj['shape'] and obj['type'] in SOLID_TYPES and obj['visible']:
            yield obj, matrix
        for child in obj['group'] + obj['elements']:
            yield from self.solid_leaves(child, matrix)
        if obj['link'] and obj['link'][0] is None:
            yield from self.solid_leaves(obj['link'][1], matrix)

    def shape(self, obj, matrix=IDENTITY):
        """The leaf's OCCT shape, placed by `matrix`. Needs cadquery."""
        import cadquery as cq
        from OCP.BRep import BRep_Builder
        from OCP.BRepTools import BRepTools
        from OCP.TopoDS import TopoDS_Shape
        from OCP.gp import gp_Trsf
        from OCP.TopLoc import TopLoc_Location

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'shape.brp')
            with open(path, 'wb') as handle:
                handle.write(self.zip.read(obj['shape']))
            shape = TopoDS_Shape()
            BRepTools.Read_s(shape, path, BRep_Builder())
        R, t = matrix
        trsf = gp_Trsf()
        trsf.SetValues(R[0][0], R[0][1], R[0][2], t[0],
                       R[1][0], R[1][1], R[1][2], t[1],
                       R[2][0], R[2][1], R[2][2], t[2])
        shape.Move(TopLoc_Location(trsf))
        return cq.Shape(shape)


def open_document(name):
    return Document(os.path.join(FREECAD_DIR, name + '.FCStd'))


def component_label(document, target):
    """The label of the in-document component a link points at.

    A bought component is an `App::Part` inside the same document; its
    label (`Stepper_Nema17x34`, `Bearing_625ZZ`, `Collar5mm`) names the
    kind, where the link's own label only numbers the instance. A link
    that passes through another link is followed.
    """
    seen = set()
    while target and target not in seen:
        seen.add(target)
        obj = document.objects.get(target)
        if obj is None:
            return target
        if obj['type'] == 'App::Part':
            return obj['label']
        if obj['link'] and obj['link'][0] is None:
            target = obj['link'][1]
            continue
        return obj['label'] or target
    return target


def instance(obj, document):
    """One placed instance as plain numbers: the form layout.py records."""
    axis, angle = axis_angle(document.matrix(obj)[0])
    source, target = obj['link']
    return {
        'object': obj['name'],
        'label': obj['label'],
        'source': source,
        'component': None if source else component_label(document, target),
        'target': target,
        'translate': tuple(round(v, 4) for v in obj['placement']['t']),
        'axis': tuple(round(v, 6) for v in axis),
        'angle': round(angle, 4),
    }


def read_assembly():
    """Every placed instance of the whole machine, sub-assembly by sub-assembly.

    Returns ``{'root': [...], 'AssemblyBase': [...], ...}`` where the root
    entries place the six sub-assemblies and each other list places the
    parts inside one of them.
    """
    out = {}
    top = open_document('Assembly')
    out['root'] = [instance(o, top) for o in top.part_links()]
    for name in SUB_ASSEMBLIES:
        doc = open_document(name)
        out[name] = [instance(o, doc) for o in doc.part_links()]
    return out
