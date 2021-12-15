"""Package diagram item."""

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.presentation import ElementPresentation, Named, from_package_str
from gaphor.diagram.shapes import Box, Text, cairo_state, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Package)
@represents(UML.Profile)
class PackageItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=70, height=70)

        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(
                    self.subject,
                    isinstance(self.subject, UML.Profile)
                    and (gettext("profile"),)
                    or (),
                ),
            ),
            Text(
                text=lambda: self.subject and self.subject.name or "",
                style={"font-weight": FontWeight.BOLD},
            ),
            Text(
                text=lambda: from_package_str(self),
                style={"font-size": "x-small"},
            ),
            style={"padding": (24, 12, 4, 12)},
            draw=draw_package,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject[NamedElement].namespace.name")
        self.watch("subject.appliedStereotype.classifier.name")


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
        stroke(context)
