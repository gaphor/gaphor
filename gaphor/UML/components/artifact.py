"""
Artifact item.
"""

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import (
    Box,
    EditableText,
    Text,
    cairo_state,
    draw_border,
    stroke,
)
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight, VerticalAlign
from gaphor.UML.classes.stereotype import stereotype_compartments


@represents(UML.Artifact)
class ArtifactItem(ElementPresentation, Classified):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype", self.update_shapes)
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject.appliedStereotype.slot", self.update_shapes)
        self.watch("subject.appliedStereotype.slot.definingFeature.name")
        self.watch("subject.appliedStereotype.slot.value", self.update_shapes)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(text=lambda: UML.model.stereotypes_str(self.subject),),
                EditableText(
                    text=lambda: self.subject.name or "",
                    style={"font-weight": FontWeight.BOLD},
                ),
                style={"padding": (4, 34, 4, 4), "min-height": 44},
                draw=draw_artifact_icon,
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            style={
                "min-width": 100,
                "min-height": 50,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border
        )


def draw_artifact_icon(box, context, bounding_box):
    cr = context.cairo

    with cairo_state(context.cairo) as cr:
        cr.set_line_width(1.0)
        ear = 5
        w = 15
        icon_margin_x = 6
        ix = bounding_box.width - icon_margin_x - w
        icon_margin_y = 12

        iy = icon_margin_y

        cr.move_to(ix + w - ear, iy)
        h = 20
        for x, y in (
            (ix + w - ear, iy + ear),
            (ix + w, iy + ear),
            (ix + w - ear, iy),
            (ix, iy),
            (ix, iy + h),
            (ix + w, iy + h),
            (ix + w, iy + ear),
        ):
            cr.line_to(x, y)
        stroke_color = context.style["color"] or (0, 0, 0, 1)
        cr.set_source_rgba(*stroke_color)
        cr.stroke()
