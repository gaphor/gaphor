"""
Component item.
"""

from gaphas.state import observed, reversible_property

from gaphor import UML
from gaphor.diagram.profiles.stereotype import stereotype_compartments
from gaphor.diagram.presentation import ElementPresentation, Classified
from gaphor.diagram.shapes import Box, EditableText, Text, draw_boundry
from gaphor.diagram.text import VerticalAlign
from gaphor.diagram.support import represents


@represents(UML.Component)
class ComponentItem(ElementPresentation, Classified):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.update_shapes()

        self.watch("show_stereotypes_attrs", self.update_shapes)
        self.watch("subject<NamedElement>.name")
        self.watch("subject<Classifier>.isAbstract", self.update_shapes)
        self.watch("subject.appliedStereotype", self.update_shapes)
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject.appliedStereotype.slot", self.update_shapes)
        self.watch("subject.appliedStereotype.slot.definingFeature.name")
        self.watch("subject.appliedStereotype.slot.value", self.update_shapes)

    show_stereotypes_attrs = UML.properties.attribute("show_stereotypes_attrs", int)

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: UML.model.stereotypes_str(self.subject),
                    style={"min-width": 0, "min-height": 0},
                ),
                EditableText(text=lambda: self.subject.name or ""),
                style={"padding": (4, 4, 4, 4)},
            ),
            *(
                self.show_stereotypes_attrs
                and stereotype_compartments(self.subject)
                or []
            ),
            style={
                "min-width": 100,
                "min-height": 50,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_component,
        )
        self.request_update()

    def postload(self):
        super().postload()
        self.update_shapes()


def draw_component(box, context, bounding_box):
    draw_boundry(box, context, bounding_box)
    draw_component_icon(box, context, bounding_box)


def draw_component_icon(box, context, bounding_box):
    bar_width = 10
    bar_height = 5
    bar_padding = 5
    icon_width = 15
    icon_height = 25
    icon_margin_x = 10
    icon_margin_y = 10

    cr = context.cairo

    ix = bounding_box.width - icon_margin_x - icon_width
    iy = icon_margin_y

    cr.save()
    try:
        cr.set_line_width(1.0)
        cr.rectangle(ix, iy, icon_width, icon_height)
        cr.stroke()

        bx = ix - bar_padding
        bar_upper_y = iy + bar_padding
        bar_lower_y = iy + bar_padding * 3

        color = cr.get_source()
        cr.rectangle(bx, bar_lower_y, bar_width, bar_height)
        cr.set_source_rgb(1, 1, 1)  # white
        cr.fill_preserve()
        cr.set_source(color)
        cr.stroke()

        cr.rectangle(bx, bar_upper_y, bar_width, bar_height)
        cr.set_source_rgb(1, 1, 1)  # white
        cr.fill_preserve()
        cr.set_source(color)
        cr.stroke()
    finally:
        cr.restore()
