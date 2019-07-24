"""
Object node item.
"""

import itertools
import ast

from gaphas.state import observed, reversible_property
from gaphor import UML
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, IconBox, EditableText, Text, draw_boundry
from gaphor.diagram.support import represents


DEFAULT_UPPER_BOUND = "*"


@represents(UML.ObjectNode)
class ObjectNodeItem(ElementPresentation, Named):
    """
    Representation of object node. Object node is ordered and has upper bound
    specification.

    Ordering information can be hidden by user.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self._show_ordering = False

        self.shape = IconBox(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject),
                    style={"min-width": 0, "min-height": 0},
                ),
                EditableText(text=lambda: self.subject and self.subject.name or ""),
                style={"min-width": 50, "min-height": 30, "padding": (5, 10, 5, 10)},
                draw=draw_boundry,
            ),
            Text(
                text=lambda: self.subject
                and self.subject.upperBound not in (None, DEFAULT_UPPER_BOUND)
                and self.subject.upperBound
                and f"{{ upperBound = {self.subject.upperBound} }}",
                style={"min-width": 0, "min-height": 0},
            ),
            Text(
                text=lambda: self._show_ordering
                and self.subject
                and self.subject.ordering
                and f"{{ ordering = {self.subject.ordering} }}",
                style={"min-width": 0, "min-height": 0},
            ),
        )

        self.watch("subject<NamedElement>.name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject<ObjectNode>.upperBound")
        self.watch("subject<ObjectNode>.ordering")

    @observed
    def _set_show_ordering(self, value):
        self._show_ordering = value
        self.request_update()

    show_ordering = reversible_property(lambda s: s._show_ordering, _set_show_ordering)

    def save(self, save_func):
        save_func("show-ordering", self._show_ordering)
        super().save(save_func)

    def load(self, name, value):
        if name == "show-ordering":
            self._show_ordering = ast.literal_eval(value)
        else:
            super().load(name, value)
