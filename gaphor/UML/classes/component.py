"""Component item."""

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, cairo_state, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment


@represents(UML.Component)
class ComponentItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject.name")
        self.watch("subject.namespace.name")
        self.watch("subject[Classifier].useCase", self.update_shapes)
        self.watch("children", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def update_shapes(self, event=None):
        self.shape = Box(
            name_compartment(self, draw_icon=draw_component_icon),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            draw=draw_border,
        )


def draw_component_icon(box, context, bounding_box):
    with cairo_state(context.cairo) as cr:
        stroke_color = context.style["color"]

        cr.set_line_width(1.0)
        icon_height = 20
        icon_width = 16
        icon_margin_x = 6
        ix = bounding_box.width - icon_margin_x - icon_width
        icon_margin_y = 12

        iy = icon_margin_y

        bar_padding = 4
        bx = ix - bar_padding
        bar_upper_y = iy + bar_padding
        bar_lower_y = iy + bar_padding * 3

        bar_width = 12
        bar_height = 4
        cr.set_source_rgba(*stroke_color)

        cr.rectangle(bx, bar_lower_y, bar_width, bar_height)
        cr.rectangle(bx, bar_upper_y, bar_width, bar_height)

        cr.move_to(ix, iy + bar_padding)
        cr.line_to(ix, iy)
        cr.line_to(ix + icon_width, iy)
        cr.line_to(ix + icon_width, iy + icon_height)
        cr.line_to(ix, iy + icon_height)
        cr.line_to(ix, iy + icon_height - bar_padding)
        cr.move_to(ix, iy + bar_padding * 3)
        cr.line_to(ix, iy + bar_padding * 2)

        cr.stroke()
