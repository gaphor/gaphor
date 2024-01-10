from typing import Callable

from gaphor.core.modeling import Presentation
from gaphor.diagram.shapes import CssNode, Shape, Text
from gaphor.UML.recipes import stereotypes_str


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
