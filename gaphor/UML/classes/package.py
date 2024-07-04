"""Package diagram item."""

from gaphor import UML
from gaphor.diagram.presentation import (
    ElementPresentation,
    Named,
    text_name,
)
from gaphor.diagram.shapes import Box, cairo_state, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(UML.Package)
@represents(UML.Profile)
class PackageItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=70, height=70)

        self.watch("children", self.update_shapes)
        self.watch("subject.name")
        self.watch("subject.namespace.name")
        self.watch("subject.appliedStereotype.classifier.name")

    def update_shapes(self, event=None):
        self.shape = Box(
            text_stereotypes(
                self,
                lambda: [self.diagram.gettext("profile")]
                if isinstance(self.subject, UML.Profile)
                else [],
            ),
            text_name(self),
            text_from_package(self),
            draw=draw_package,
        )


def draw_package(box, context, bounding_box):
    with cairo_state(context.cairo) as cr:
        o = 0.0
        h = bounding_box.height
        w = bounding_box.width
        x = 50
        y = 20
        cr.move_to(x, y)
        cr.line_to(x, o)
        cr.line_to(o, o)
        cr.line_to(o, h)
        cr.line_to(w, h)
        cr.line_to(w, y)
        cr.line_to(o, y)
        stroke(context, fill=True)
