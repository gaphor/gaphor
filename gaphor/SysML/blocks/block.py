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
from gaphor.RAAML import raaml
from gaphor.SysML.sysml import Block, ValueType
from gaphor.UML.classes.klass import (
    attribute_watches,
    stereotype_compartments,
    stereotype_watches,
)
from gaphor.UML.recipes import stereotypes_str
from gaphor.UML.umlfmt import format_property


@represents(Block)
@represents(raaml.Situation)
@represents(raaml.Loss)
@represents(raaml.Hazard)
@represents(raaml.ControlStructure)
class BlockItem(ElementPresentation[Block], Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_parts", self.update_shapes
        ).watch("show_references", self.update_shapes).watch(
            "show_values", self.update_shapes
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
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_parts: attribute[int] = attribute("show_parts", int, default=False)

    show_references: attribute[int] = attribute("show_references", int, default=False)

    show_values: attribute[int] = attribute("show_values", int, default=False)

    def additional_stereotypes(self):
        if isinstance(self.subject, raaml.Situation):
            return [gettext("Situation")]
        elif isinstance(self.subject, raaml.ControlStructure):
            return [gettext("ControlStructure")]
        elif isinstance(self.subject, Block):
            return [gettext("block")]
        else:
            return ()

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(
                        self.subject, self.additional_stereotypes()
                    )
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
                self.show_parts
                and self.subject
                and [
                    self.block_compartment(
                        gettext("parts"),
                        lambda a: not a.association and a.aggregation == "composite",
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
                        lambda a: not a.association and a.aggregation != "composite",
                    )
                ]
                or []
            ),
            *(
                self.show_values
                and self.subject
                and [
                    self.block_compartment(
                        gettext("values"),
                        lambda a: isinstance(a.type, ValueType)
                        and a.aggregation == "composite",
                    )
                ]
                or []
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            style={
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

    def block_compartment(self, name, predicate):
        # We need to fix the attribute value, since the for loop changes it.
        def lazy_format(attribute):
            return lambda: format_property(attribute) or gettext("unnamed")

        return Box(
            Text(
                text=name,
                style={
                    "padding": (0, 0, 4, 0),
                    "font-size": "x-small",
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
