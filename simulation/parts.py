"""The printed parts, read from the design's own STEP files.

Every part Thor publishes is one product in one file named after it, so a
node is the file and nothing else: no geometry is restated here, and
nothing upstream is edited. The STEP is exact, so the gear-mesh and
fastener contracts are decided on solids rather than on triangles.

Colours come from `simulation.materials`, which follows the author's own
published photographs; the STEP files themselves carry only FreeCAD's
default grey.
"""

import os

from solid_node.node import StepNode

from simulation import materials
from simulation.materials import printed_colour

STEP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'step')


def _inside_out(shape):
    """A published solid whose faces are oriented inward, left as it is.

    Two of Thor's parts are exported inside out and measure a negative
    volume. Reversing the boundary makes the volume come out positive but
    breaks every boolean the solid takes part in — the kernel answers an
    intersection with the whole of the other shape — so the model keeps
    the published orientation, which booleans correctly, and records the
    defect instead. Nothing downstream reads a signed volume.
    """
    return shape


def _largest_solid(shape):
    """The biggest solid in a file that carries more than one."""
    import cadquery as cq
    return max(shape.Solids(), key=lambda solid: solid.Volume())


def _smallest_solid(shape):
    """The smallest solid in a file that carries more than one."""
    return min(shape.Solids(), key=lambda solid: solid.Volume())


class ThorPart(StepNode):
    """A printed part, read from `step/<class name>.step`.

    The subclass names the file: `Art1Body` reads `step/Art1Body.step`.
    Each file holds exactly one product, named after the file, so no
    `part` is needed.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'step_source' not in cls.__dict__:
            cls.step_source = os.path.join(STEP_DIR, cls.__name__ + '.step')
        if 'color' not in cls.__dict__:
            cls.color = printed_colour(cls.__name__)



class Art1Body(ThorPart):
    """`step/Art1Body.step`."""


class Art1Bot(ThorPart):
    """`step/Art1Bot.step`."""


class Art1FanHolder(ThorPart):
    """`step/Art1FanHolder.step`."""


class Art1GearMotor(ThorPart):
    """`step/Art1GearMotor.step`."""


class Art1Top(ThorPart):
    """`step/Art1Top.step`."""


class Art23Optodisk(ThorPart):
    """`step/Art23Optodisk.step`."""


class Art2BodyA(ThorPart):
    """`step/Art2BodyA.step`."""


class Art2BodyACover1(ThorPart):
    """`step/Art2BodyACover1.step`."""


class Art2BodyACover2(ThorPart):
    """`step/Art2BodyACover2.step`."""


class Art2BodyAWindow(ThorPart):
    """`step/Art2BodyAWindow.step`."""


class Art2BodyB(ThorPart):
    """`step/Art2BodyB.step`."""


class Art2BodyBCover(ThorPart):
    """`step/Art2BodyBCover.step`."""


class Art2BodyUnion(ThorPart):
    """`step/Art2BodyUnion.step`."""


class Art2MotorGear(ThorPart):
    """`step/Art2MotorGear.step`, turned right side out.

    The published solid is inside out: its faces are oriented inward and
    it measures -8435.0 mm3. The geometry is right and it booleans
    correctly, so the model keeps it as published and records the defect;
    reversing it makes the volume positive and every boolean wrong.
    """

    def adjust(self, shape):
        return _inside_out(shape)


class Art2SideCover(ThorPart):
    """`step/Art2SideCover.step`."""


class Art3Body(ThorPart):
    """`step/Art3Body.step`."""


class Art3Pulley(ThorPart):
    """`step/Art3Pulley.step`."""


class Art3TensionerBody(ThorPart):
    """`step/Art3TensionerBody.step`."""


class Art3TensionerPulley(ThorPart):
    """`step/Art3TensionerPulley.step`."""


class Art4BearingFix(ThorPart):
    """`step/Art4BearingFix.step`."""


class Art4BearingRing(ThorPart):
    """`step/Art4BearingRing.step`."""


class Art4Body(ThorPart):
    """`step/Art4Body.step`."""


class Art4BodyBot(ThorPart):
    """`step/Art4BodyBot.step`, turned right side out.

    Inside out as published, measuring -113674.9 mm3. See
    `Art2MotorGear`; the same defect, left the same way.
    """

    def adjust(self, shape):
        return _inside_out(shape)


class Art4BodyFan(ThorPart):
    """`step/Art4BodyFan.step`."""


class Art4MotorFix(ThorPart):
    """`step/Art4MotorFix.step`."""


class Art4MotorGear(ThorPart):
    """`step/Art4MotorGear.step`."""


class Art4Optodisk(ThorPart):
    """`step/Art4Optodisk.step`."""


class Art4TransmissionColumn(ThorPart):
    """`step/Art4TransmissionColumn.step`."""


class Art56GearPlate(ThorPart):
    """`step/Art56GearPlate.step`."""


class Art56MotorCoverRing(ThorPart):
    """`step/Art56MotorCoverRing.step`."""


class Art56MotorHolderA(ThorPart):
    """`step/Art56MotorHolderA.step`."""


class Art56MotorHolderB(ThorPart):
    """`step/Art56MotorHolderB.step`."""


class Art56SmallGear(ThorPart):
    """`step/Art56SmallGear.step`."""


class BaseBearingFix(ThorPart):
    """`step/BaseBearingFix.step`."""


class BaseBot(ThorPart):
    """`step/BaseBot.step`."""


class BaseBoxBody(ThorPart):
    """`step/BaseBoxBody.step`."""


class BaseBoxCover(ThorPart):
    """`step/BaseBoxCover.step`."""


class BaseTop(ThorPart):
    """`step/BaseTop.step`."""


class CommonBearingFix(ThorPart):
    """`step/CommonBearingFix.step`."""


class CommonBearingFixThrough(ThorPart):
    """`step/CommonBearingFixThrough.step`."""


class GripperActiveArm(ThorPart):
    """`step/GripperActiveArm.step`, without the pin the file carries.

    The published file holds two solids: the printed arm, 2479.9 mm3, and
    a loose 3.4 by 5.0 pin of 45.4 mm3 standing in the arm's outer pivot
    hole with 0.3 mm of clearance all round. The pin is the jaw pivot, not
    part of the print: a builder slicing this file gets a loose plug
    printed inside the hole. The model takes the arm here and the pin as
    `GripperActiveArmPin`, so both are in the machine and neither is one
    printed body with the other.
    """

    def adjust(self, shape):
        return _largest_solid(shape)


class GripperActiveArmPin(ThorPart):
    """The jaw pivot pin the design ships inside `GripperActiveArm.step`."""

    step_source = os.path.join(STEP_DIR, 'GripperActiveArm.step')
    color = materials.STEEL

    def adjust(self, shape):
        return _smallest_solid(shape)


class GripperArm(ThorPart):
    """`step/GripperArm.step`."""


class GripperBot(ThorPart):
    """`step/GripperBot.step`."""


class GripperFinger(ThorPart):
    """`step/GripperFinger.step`."""


class GripperPassiveArm(ThorPart):
    """`step/GripperPassiveArm.step`, without the pin the file carries.

    The same two-solid export as `GripperActiveArm`: a 3421.4 mm3 arm and
    a 45.4 mm3 pin.
    """

    def adjust(self, shape):
        return _largest_solid(shape)


class GripperPassiveArmPin(ThorPart):
    """The jaw pivot pin the design ships inside `GripperPassiveArm.step`."""

    step_source = os.path.join(STEP_DIR, 'GripperPassiveArm.step')
    color = materials.STEEL

    def adjust(self, shape):
        return _smallest_solid(shape)


class GripperTop(ThorPart):
    """`step/GripperTop.step`."""


class GripperFingerMirrored(ThorPart):
    """`step/GripperFinger.step`, mirrored across its own YZ plane.

    The design's assembly places one `GripperFinger` and one FreeCAD
    `Part::Mirroring` of it, and publishes only the unmirrored part: a
    builder printing from `step/` or `stl/` gets two identical fingers,
    not the handed pair the assembly uses. The mirror is applied here so
    the model shows the machine the assembly describes, and the
    discrepancy is recorded as a finding rather than fixed upstream.
    """

    step_source = os.path.join(STEP_DIR, 'GripperFinger.step')
    color = printed_colour('GripperFinger')

    def adjust(self, shape):
        return shape.mirror('YZ')


#: Every printed part the design's assembly places, by the name its STEP
#: file carries. `simulation.layout.part_name` yields that name, so a
#: sub-assembly looks a part up here without restating the mapping.
BY_NAME = {
    'Art1Body': Art1Body,
    'Art1Bot': Art1Bot,
    'Art1FanHolder': Art1FanHolder,
    'Art1GearMotor': Art1GearMotor,
    'Art1Top': Art1Top,
    'Art23Optodisk': Art23Optodisk,
    'Art2BodyA': Art2BodyA,
    'Art2BodyACover1': Art2BodyACover1,
    'Art2BodyACover2': Art2BodyACover2,
    'Art2BodyAWindow': Art2BodyAWindow,
    'Art2BodyB': Art2BodyB,
    'Art2BodyBCover': Art2BodyBCover,
    'Art2BodyUnion': Art2BodyUnion,
    'Art2MotorGear': Art2MotorGear,
    'Art2SideCover': Art2SideCover,
    'Art3Body': Art3Body,
    'Art3Pulley': Art3Pulley,
    'Art3TensionerBody': Art3TensionerBody,
    'Art3TensionerPulley': Art3TensionerPulley,
    'Art4BearingFix': Art4BearingFix,
    'Art4BearingRing': Art4BearingRing,
    'Art4Body': Art4Body,
    'Art4BodyBot': Art4BodyBot,
    'Art4BodyFan': Art4BodyFan,
    'Art4MotorFix': Art4MotorFix,
    'Art4MotorGear': Art4MotorGear,
    'Art4Optodisk': Art4Optodisk,
    'Art4TransmissionColumn': Art4TransmissionColumn,
    'Art56GearPlate': Art56GearPlate,
    'Art56MotorCoverRing': Art56MotorCoverRing,
    'Art56MotorHolderA': Art56MotorHolderA,
    'Art56MotorHolderB': Art56MotorHolderB,
    'Art56SmallGear': Art56SmallGear,
    'BaseBearingFix': BaseBearingFix,
    'BaseBot': BaseBot,
    'BaseBoxBody': BaseBoxBody,
    'BaseBoxCover': BaseBoxCover,
    'BaseTop': BaseTop,
    'CommonBearingFix': CommonBearingFix,
    'CommonBearingFixThrough': CommonBearingFixThrough,
    'GripperActiveArm': GripperActiveArm,
    'GripperArm': GripperArm,
    'GripperBot': GripperBot,
    'GripperFinger': GripperFinger,
    'GripperPassiveArm': GripperPassiveArm,
    'GripperTop': GripperTop,
}
