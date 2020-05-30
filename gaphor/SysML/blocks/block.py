from gaphor.core import gettext
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
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
from gaphor.SysML.sysml import Block
from gaphor.UML.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
    stereotype_compartments,
    stereotype_watches,
)
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.UML.umlfmt import format_attribute


@represents(Block)
class BlockItem(ElementPresentation[Block], Classified):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_attributes", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch(
            "show_parts", self.update_shapes
        ).watch(
            "show_references", self.update_shapes
        ).watch(
            "subject[NamedElement].name"
        ).watch(
            "subject[NamedElement].namespace.name"
        ).watch(
            "subject[Classifier].isAbstract", self.update_shapes
        ).watch(
            "subject[Class].ownedAttribute.aggregation", self.update_shapes
        )
        attribute_watches(self, "Block")
        operation_watches(self, "Block")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=False)

    show_operations: attribute[int] = attribute("show_operations", int, default=False)

    show_parts: attribute[int] = attribute("show_parts", int, default=False)

    show_references: attribute[int] = attribute("show_references", int, default=False)

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject, ["block"]),
                    style={"min-width": 0, "min-height": 0},
                ),
                EditableText(
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
            *(
                self.show_parts
                and self.subject
                and [
                    self.block_compartment(
                        gettext("parts"),
                        lambda a: a.association and a.aggregation == "composite",
                    )
                ]
                or []
            ),
            *(
                self.show_references
                and self.subject
                and [
                    self.block_compartment(
                        gettext("references"),
                        lambda a: a.association and a.aggregation != "composite",
                    )
                ]
                or []
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            style={
                "min-width": 100,
                "min-height": 50,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

    def block_compartment(self, name, predicate):
        # We need to fix the attribute value, since the for loop changes it.
        def lazy_format(attribute):
            return lambda: format_attribute(attribute) or gettext("unnamed")

        return Box(
            Text(
                text=name,
                style={
                    "padding": (0, 0, 4, 0),
                    "font-size": 10,
                    "font-style": FontStyle.ITALIC,
                },
            ),
            *(
                Text(text=lazy_format(attribute), style={"text-align": TextAlign.LEFT})
                for attribute in self.subject.ownedAttribute
                if predicate(attribute)
            ),
            style={"padding": (4, 4, 4, 4), "min-height": 8},
            draw=draw_top_separator,
        )
