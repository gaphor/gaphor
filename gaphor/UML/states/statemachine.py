from __future__ import annotations

from gaphas.types import Pos

from gaphor import UML
from gaphor.core import gettext
from gaphor.core.modeling.element import Element
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import FontWeight, TextAlign, VerticalAlign
from gaphor.core.styling.properties import JustifyContent
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import BoundedBox, Box, Text, draw_border, draw_top_separator
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches


@represents(UML.StateMachine)
class StateMachineItem(Classified, ElementPresentation[UML.StateMachine]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self._region_boxes = []
        self.watch("show_stereotypes", self.update_shapes)
        self.watch("show_regions", self.update_shapes)
        self.watch("subject[NamedElement].name")
        self.watch("subject[StateMachine].region.name")
        self.watch("subject[StateMachine].region", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)
    show_regions: attribute[int] = attribute("show_regions", int, default=True)

    def update_shapes(self, event=None):
        self._region_boxes = (
            list(region_compartment(self.subject)) if self.show_regions else []
        )
        self.shape = Box(
            Box(
                Text(
                    text=lambda: UML.recipes.stereotypes_str(
                        self.subject, [gettext("statemachine")]
                    ),
                ),
                Text(
                    text=lambda: self.subject.name or "",
                    style={"font-weight": FontWeight.BOLD},
                ),
                style={"padding": (4, 4, 4, 4)},
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            Box(
                *(self._region_boxes),
                style={"justify-content": JustifyContent.STRETCH},
            ),
            style={
                "vertical-align": VerticalAlign.TOP
                if (self.diagram and self.children) or self.show_regions
                else VerticalAlign.MIDDLE,
            },
            draw=draw_border,
        )

    def subject_at_point(self, pos: Pos) -> Element | None:
        region: UML.Region
        return next(
            (
                region
                for region, bounds in zip(self.subject.region, self._region_boxes)
                if pos in bounds
            ),
            self.subject,
        )


def region_compartment(subject):
    if not subject:
        return

    for index, region in enumerate(subject.region):
        yield _create_region_compartment(region, index)


def _create_region_compartment(region, index):
    return BoundedBox(
        Text(
            text=lambda: region.name or "",
            style={"text-align": TextAlign.LEFT},
        ),
        style={
            "padding": (4, 4, 4, 4),
            "min-height": 100,
            "vertical-align": VerticalAlign.TOP,
            "dash-style": (7, 3) if index > 0 else (),
        },
        draw=draw_top_separator,
    )
