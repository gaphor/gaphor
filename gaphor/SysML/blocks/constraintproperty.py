"""Constraint Property item."""

from dataclasses import replace

from gaphas.connector import LinePort
from gaphas.constraint import constraint
from gaphas.position import Position

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.umlfmt import format_property


class ConstraintPropertyItem(Named, ElementPresentation[UML.Property]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        # Create new Position variables for the inner ports
        self._inner_top_left = Position(0, 0)
        self._inner_top_right = Position(0, 0)
        self._inner_bottom_right = Position(0, 0)
        self._inner_bottom_left = Position(0, 0)

        # Constrain the inner positions relative to the outer handles
        h_nw, h_ne, h_se, h_sw = self.handles()
        offset = 8  # Use a positive offset to bring the ports inside

        c = diagram.connections.add_constraint
        c(self, constraint(vertical=(h_nw.pos, self._inner_top_left), delta=offset))
        c(self, constraint(horizontal=(h_nw.pos, self._inner_top_left), delta=offset))

        c(self, constraint(vertical=(self._inner_top_right, h_ne.pos), delta=offset))
        c(self, constraint(horizontal=(h_ne.pos, self._inner_top_right), delta=offset))

        c(self, constraint(vertical=(self._inner_bottom_right, h_se.pos), delta=offset))
        c(
            self,
            constraint(horizontal=(self._inner_bottom_right, h_se.pos), delta=offset),
        )

        c(self, constraint(vertical=(h_sw.pos, self._inner_bottom_left), delta=offset))
        c(
            self,
            constraint(horizontal=(self._inner_bottom_left, h_sw.pos), delta=offset),
        )

        # Create the list of ports ONCE and store it
        self._ports = [
            LinePort(self._inner_top_left, self._inner_top_right),
            LinePort(self._inner_top_right, self._inner_bottom_right),
            LinePort(self._inner_bottom_right, self._inner_bottom_left),
            LinePort(self._inner_bottom_left, self._inner_top_left),
        ]

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[Property].name")
        self.watch("subject[Property].type.name")
        self.watch("subject[Property].typeValue")
        self.watch("subject[Property].lowerValue")
        self.watch("subject[Property].upperValue")
        self.watch("subject[Property].aggregation", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def ports(self):
        """
        Return the list of consistent port objects.
        """
        return self._ports

    def update_shapes(self, event=None):
        def draw_rounded_border(box, context, bounding_box):
            new_style = context.style.copy()
            new_style["border-radius"] = 25
            new_context = replace(context, style=new_style)
            draw_border(box, new_context, bounding_box)

        self.shape = Box(
            # First compartment with the property name
            CssNode(
                "compartment",
                self.subject,
                Box(
                    CssNode(
                        "name",
                        self.subject,
                        Text(
                            text=lambda: format_property(
                                self.subject, type=True, multiplicity=True
                            )
                            or "",
                        ),
                    ),
                ),
            ),
            # Second, invisible compartment to push the first to the top
            CssNode(
                "compartment",
                self.subject,
                Box(draw=lambda box, context, bounding_box: None),
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            draw=draw_rounded_border,
        )
