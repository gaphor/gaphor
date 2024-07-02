"""State diagram item."""

from __future__ import annotations

from gaphas.types import Pos

from gaphor import UML
from gaphor.core.modeling.element import Element
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation, Named, text_name
from gaphor.diagram.shapes import Box, CssNode, Text, draw_top_separator, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.states.region import region_compartment


@represents(UML.State)
class StateItem(ElementPresentation[UML.State], Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)
        self._region_heights = []
        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[State].entry.name", self.update_shapes)
        self.watch("subject[State].exit.name", self.update_shapes)
        self.watch("subject[State].doActivity.name", self.update_shapes)
        self.watch("subject[State].region.name")
        self.watch("subject[State].region", self.update_shapes)
        self.watch("show_regions", self.update_shapes)

    show_regions: attribute[int] = attribute("show_regions", int, default=True)

    def update_shapes(self, event=None):
        region_boxes = (
            list(region_compartment(self.subject)) if self.show_regions else []
        )
        compartment = Box(
            Text(
                text=lambda: self.subject.entry.name
                and f"entry / {self.subject.entry.name}"
                or "",
            ),
            Text(
                text=lambda: self.subject.exit.name
                and f"exit / {self.subject.exit.name}"
                or "",
            ),
            Text(
                text=lambda: self.subject.doActivity.name
                and f"do / {self.subject.doActivity.name}"
                or "",
            ),
            draw=draw_top_separator,
        )
        if not any(t.text() for t in compartment.children):  # type: ignore[attr-defined]
            compartment = Box()

        self.shape = Box(
            CssNode(
                "compartment",
                None,
                Box(
                    text_stereotypes(self),
                    text_name(self),
                ),
            ),
            CssNode("compartment", self.subject, compartment),
            *(
                region_boxes
                and [
                    CssNode(
                        "regions",
                        None,
                        Box(
                            *(region_boxes),
                        ),
                    )
                ]
                or []
            ),
            draw=draw_state,
        )

    def update(self, context):
        super().update(context)
        self._region_heights = [h for _w, h in self._shape.children[-1].child.sizes]  # type: ignore[union-attr]

    def region_at_point(self, pos: Pos) -> Element | None:
        region_offset = self.height - sum(self._region_heights)
        _x, y = pos
        for region, h in zip(self.subject.region, self._region_heights):
            region_offset += h
            if y < region_offset:
                return region
        return self.subject


def draw_state(box, context, bounding_box):
    cr = context.cairo
    dx = 15
    dy = 8
    ddx = 0.4 * dx
    ddy = 0.4 * dy
    width = bounding_box.width
    height = bounding_box.height

    cr.move_to(0, dy)
    cr.curve_to(0, ddy, ddx, 0, dx, 0)
    cr.line_to(width - dx, 0)
    cr.curve_to(width - ddx, 0, width, ddy, width, dy)
    cr.line_to(width, height - dy)
    cr.curve_to(width, height - ddy, width - ddx, height, width - dx, height)
    cr.line_to(dx, height)
    cr.curve_to(ddx, height, 0, height - ddy, 0, height - dy)
    cr.close_path()

    stroke(context, fill=True)
