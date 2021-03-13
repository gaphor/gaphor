"""Majority vote gate item definition."""

from math import pi

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.core.styling import VerticalAlign
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.UML.modelfactory import stereotypes_str


@represents(raaml.MAJORITY_VOTE)
class MajorityVoteItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            Text(
                # TODO: Make this text align to center
                text="m",
                style={
                    "font-weight": FontWeight.BOLD,
                    "font-size": "large",
                    "padding": (25, 4, 0, 4),
                },
            ),
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject, ["MAJORITY_VOTE"]),
                ),
                Text(
                    text=lambda: self.subject.name or "",
                    width=lambda: self.width - 4,
                    style={
                        "font-weight": FontWeight.BOLD,
                        "font-style": FontStyle.NORMAL,
                    },
                ),
                Text(
                    text=lambda: from_package_str(self),
                    style={"font-size": "x-small"},
                ),
                style={
                    "padding": (20, 4, 0, 4),
                    "min-height": 30,
                },
            ),
            style={"vertical-align": VerticalAlign.BOTTOM},
            draw=draw_majority_vote_gate,
        )


def draw_majority_vote_gate(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    left = bounding_box.width / 3.0
    right = bounding_box.width * 2.0 / 3.0
    wall_top = bounding_box.height / 4.0 + 4.0
    wall_bottom = bounding_box.height - 40

    # Left wall
    cr.move_to(left, wall_bottom)
    cr.line_to(left, wall_top)

    # Right wall
    cr.move_to(right, wall_bottom)
    cr.line_to(right, wall_top)

    # Top arc
    rx = right - left
    ry = bounding_box.height - 50
    cr.move_to(left, wall_top)
    cr.save()
    cr.translate(left + rx / 2.0, wall_top)
    cr.scale(rx / 2.0, ry / 2.0)
    cr.arc(0.0, 0.0, 1.0, pi, 0)
    cr.restore()

    # Bottom arc
    ry = bounding_box.height / 6.0
    cr.move_to(left, wall_bottom)
    cr.save()
    cr.translate(left + rx / 2.0, wall_bottom)
    cr.scale(rx / 2.0, ry / 2.0)
    cr.arc(0.0, 0.0, 1.0, pi, 0)
    cr.restore()

    stroke(context)
