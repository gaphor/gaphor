from typing import Callable

from gaphor.core.modeling import Presentation
from gaphor.diagram.presentation import text_from_package, text_name
from gaphor.diagram.shapes import Box, CssNode, Shape, Text
from gaphor.UML.recipes import stereotypes_str


def name_compartment(
    presentation: Presentation,
    additional_stereotypes: Callable[[], list[str]] | None = None,
):
    return CssNode(
        "compartment",
        None,
        Box(
            text_stereotypes(presentation, additional_stereotypes),
            text_name(presentation),
            text_from_package(presentation),
        ),
    )


def text_stereotypes(
    item: Presentation, additional_stereotypes: Callable[[], list[str]] | None = None
) -> Shape:
    return CssNode(
        "stereotypes",
        item.subject,
        Text(
            text=lambda: stereotypes_str(
                item.subject, additional_stereotypes() if additional_stereotypes else ()
            ),
        ),
    )
