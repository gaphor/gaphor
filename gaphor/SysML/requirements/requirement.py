from gaphor.core import gettext
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import (
    Box,
    Text,
    TextAlign,
    VerticalAlign,
    draw_border,
    draw_top_separator,
)
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.SysML.sysml import Requirement
from gaphor.UML.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
    stereotype_compartments,
    stereotype_watches,
)
from gaphor.UML.recipes import stereotypes_str


@represents(Requirement)
class RequirementItem(ElementPresentation[Requirement], Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_attributes", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch(
            "subject[NamedElement].name"
        ).watch(
            "subject[NamedElement].namespace.name"
        ).watch(
            "subject[Classifier].isAbstract", self.update_shapes
        ).watch(
            "subject[AbstractRequirement].externalId", self.update_shapes
        ).watch(
            "subject[AbstractRequirement].text", self.update_shapes
        )
        attribute_watches(self, "Requirement")
        operation_watches(self, "Requirement")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=False)

    show_operations: attribute[int] = attribute("show_operations", int, default=False)

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(
                        self.subject, [gettext("requirement")]
                    ),
                ),
                Text(
                    text=lambda: self.subject.name or "",
                    width=lambda: self.width - 4,
                    style={
                        "font-weight": FontWeight.BOLD,
                        "font-style": FontStyle.ITALIC
                        if self.subject and self.subject.isAbstract
                        else FontStyle.NORMAL,
                    },
                ),
                Text(
                    text=lambda: from_package_str(self),
                    style={"font-size": "x-small"},
                ),
                style={"padding": (12, 4, 12, 4)},
            ),
            *(
                self.show_attributes
                and self.subject
                and [attributes_compartment(self.subject)]
                or []
            ),
            *(
                self.show_operations
                and self.subject
                and [operations_compartment(self.subject)]
                or []
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            self.id_and_text_compartment(),
            style={
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

    def id_and_text_compartment(self):
        subject = self.subject
        if subject and (subject.externalId or subject.text):
            return Box(
                *(
                    [
                        Text(
                            text=lambda: f"Id: {subject.externalId}",
                            style={"text-align": TextAlign.LEFT},
                        )
                    ]
                    if subject and subject.externalId
                    else []
                ),
                *(
                    [
                        Text(
                            text=lambda: f"Text: {subject.text}",
                            width=lambda: self.width - 8,
                            style={"text-align": TextAlign.LEFT},
                        )
                    ]
                    if subject and subject.text
                    else []
                ),
                style={"padding": (4, 4, 4, 4), "min-height": 8},
                draw=draw_top_separator,
            )
        else:
            return Box()
