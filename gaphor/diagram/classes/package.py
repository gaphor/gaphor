"""
Package diagram item.
"""

from gaphor import UML
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.diagram.presentation import ElementPresentation, Named, from_package_str
from gaphor.diagram.shapes import Box, EditableText, Text
from gaphor.diagram.text import FontWeight
from gaphor.diagram.support import represents


@represents(UML.Package)
@represents(UML.Profile)
class PackageItem(ElementPresentation, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(
                    self.subject,
                    ("profile",) if isinstance(self.subject, UML.Profile) else (),
                ),
                style={"min-width": 0, "min-height": 0},
            ),
            EditableText(
                text=lambda: self.subject and self.subject.name or "",
                style={"font-weight": FontWeight.BOLD},
            ),
            Text(
                text=lambda: from_package_str(self),
                style={"font": "sans 8", "min-width": 0, "min-height": 0},
            ),
            style={"min-width": 50, "min-height": 70, "padding": (25, 10, 5, 10)},
            draw=draw_package,
        )

        self.watch("subject<NamedElement>.name")
        self.watch("subject<NamedElement>.namespace")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_package(box, context, bounding_box):
    cr = context.cairo
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
    cr.stroke()
