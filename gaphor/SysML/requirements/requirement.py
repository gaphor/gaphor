from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    DEFAULT_HEIGHT,
    Classified,
    ElementPresentation,
)
from gaphor.diagram.shapes import (
    Box,
    CssNode,
    Text,
    draw_border,
    draw_top_separator,
)
from gaphor.diagram.support import represents
from gaphor.SysML.sysml import Requirement
from gaphor.UML.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
)
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment


@represents(Requirement)
class RequirementItem(Classified, ElementPresentation[Requirement]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_text", self.update_shapes).watch(
            "show_stereotypes", self.update_shapes
        ).watch("show_attributes", self.update_shapes).watch(
            "show_operations", self.update_shapes
        ).watch("subject.name").watch("subject.namespace.name").watch(
            "subject[Classifier].isAbstract", self.update_shapes
        ).watch("subject[AbstractRequirement].externalId", self.update_shapes).watch(
            "subject[AbstractRequirement].text", self.update_shapes
        )
        attribute_watches(self, "Requirement")
        operation_watches(self, "Requirement")
        stereotype_watches(self)

    show_text: attribute[int] = attribute("show_text", int, default=True)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=False)

    show_operations: attribute[int] = attribute("show_operations", int, default=False)

    def update_shapes(self, event=None):
        # reset height so requirement block is reduced to minimum required height
        self.height = DEFAULT_HEIGHT
        self.shape = Box(
            name_compartment(self, lambda: [self.diagram.gettext("requirement")]),
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
            draw=draw_border,
        )

    def id_and_text_compartment(self):
        subject = self.subject
        if subject and (subject.externalId or (subject.text and self.show_text)):
            return CssNode(
                "compartment",
                self.subject,
                Box(
                    *(
                        [
                            CssNode(
                                "id",
                                None,
                                Text(text=lambda: f"Id: {subject.externalId}"),
                            )
                        ]
                        if subject and subject.externalId
                        else []
                    ),
                    *(
                        [
                            CssNode(
                                "text", None, Text(text=lambda: f"Text: {subject.text}")
                            )
                        ]
                        if subject and subject.text and self.show_text
                        else []
                    ),
                    draw=draw_top_separator,
                ),
            )
        return Box()
