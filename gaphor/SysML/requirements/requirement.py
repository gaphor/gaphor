from gaphor.diagram.presentation import from_package_str
from gaphor.diagram.shapes import (
    Box,
    EditableText,
    FontStyle,
    FontWeight,
    Text,
    TextAlign,
    VerticalAlign,
    draw_border,
    draw_top_separator,
)
from gaphor.diagram.support import represents
from gaphor.SysML.sysml import Requirement
from gaphor.UML.classes.klass import (
    ClassItem,
    attributes_compartment,
    operations_compartment,
    stereotype_compartments,
)
from gaphor.UML.modelfactory import stereotypes_str


@represents(Requirement)
class RequirementItem(ClassItem):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.show_attributes = False
        self.show_operations = False
        self.watch("subject[AbstractRequirement].externalId", self.update_shapes)
        self.watch("subject[AbstractRequirement].text", self.update_shapes)

    def additional_stereotypes(self):
        return ["requirement"]

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(
                        self.subject, self.additional_stereotypes()
                    ),
                    style={"min-width": 0, "min-height": 0},
                ),
                EditableText(
                    text=lambda: self.subject.name or "",
                    style={
                        "font-weight": FontWeight.BOLD,
                        "font-style": FontStyle.ITALIC
                        if self.subject and self.subject.isAbstract
                        else FontStyle.NORMAL,
                    },
                ),
                Text(
                    text=lambda: from_package_str(self),
                    style={"font-size": 10, "min-width": 0, "min-height": 0},
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
                "min-width": 100,
                "min-height": 50,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

    def id_and_text_compartment(self):
        subject: Requirement = self.subject  # type: ignore[assignment]
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
