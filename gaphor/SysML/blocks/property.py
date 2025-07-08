"""Property item."""

from dataclasses import replace

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.SysML.sysml import Constraint
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.umlfmt import format_property


@represents(UML.Property)
class PropertyItem(Named, ElementPresentation[UML.Property]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[Property].name")
        self.watch("subject[Property].type.name")
        self.watch("subject[Property].typeValue")
        self.watch("subject[Property].lowerValue")
        self.watch("subject[Property].upperValue")
        self.watch("subject[Property].aggregation", self.update_shapes)
        stereotype_watches(self)
        # Add a watch for the property's type.
        # This ensures the shape updates if the type is changed to or from a Constraint.
        self.watch("subject[Property].type", self.update_shapes)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def update_shapes(self, event=None):
        """
        Update the shapes for the Property.

        This method now checks if the property is typed by a Constraint.
        If it is, it renders as a "constraint property" with rounded borders.
        Otherwise, it renders as a standard property.
        """
        if self.subject and isinstance(self.subject.type, Constraint):
            # This is a constraint property, so draw with a rounded border.
            def draw_rounded_border(box, context, bounding_box):
                new_style = context.style.copy()
                new_style["border-radius"] = 25
                new_context = replace(context, style=new_style)
                draw_border(box, new_context, bounding_box)

            self.shape = Box(
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
                *(
                    self.show_stereotypes
                    and stereotype_compartments(self.subject)
                    or []
                ),
                draw=draw_rounded_border,
            )
        else:
            # This is a standard property, draw with a normal border.
            self.shape = Box(
                CssNode(
                    "compartment",
                    self.subject,
                    Box(
                        text_stereotypes(self),
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
                *(
                    self.show_stereotypes
                    and stereotype_compartments(self.subject)
                    or []
                ),
                draw=draw_border,
            )
