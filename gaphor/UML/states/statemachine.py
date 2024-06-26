from __future__ import annotations

from gaphas.types import Pos

from gaphor import UML
from gaphor.core.modeling.element import Element
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import Classified, ElementPresentation, text_name
from gaphor.diagram.shapes import Box, CssNode, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.states.region import region_compartment


@represents(UML.StateMachine)
class StateMachineItem(Classified, ElementPresentation[UML.StateMachine]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self._region_heights = []
        self.watch("children", self.update_shapes)
        self.watch("show_stereotypes", self.update_shapes)
        self.watch("show_regions", self.update_shapes)
        self.watch("subject.name")
        self.watch("subject[StateMachine].region.name")
        self.watch("subject[StateMachine].region", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)
    show_regions: attribute[int] = attribute("show_regions", int, default=True)

    def update_shapes(self, event=None):
        region_boxes = (
            list(region_compartment(self.subject)) if self.show_regions else []
        )
        self.shape = Box(
            CssNode(
                "compartment",
                None,
                Box(
                    text_stereotypes(
                        self, lambda: [self.diagram.gettext("statemachine")]
                    ),
                    text_name(self),
                ),
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
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
            draw=draw_border,
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
