from typing import Callable

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext, Presentation
from gaphor.diagram.presentation import text_name
from gaphor.diagram.shapes import Box, CssNode, Shape, Text
from gaphor.UML.recipes import stereotypes_str


def name_compartment(
    presentation: Presentation,
    additional_stereotypes: Callable[[], list[str]] | None = None,
    draw_icon: Callable[[Box, DrawContext, Rectangle], None] | None = None,
):
    return CssNode(
        "compartment",
        None,
        Box(
            text_stereotypes(presentation, additional_stereotypes),
            text_name(presentation),
            text_from_package(presentation),
            draw=draw_icon,
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


def text_from_package(item: Presentation):
    return CssNode("from", item.subject, Text(text=lambda: from_package_str(item)))


def from_package_str(item):
    """Display name space info when it is different, then diagram's or parent's
    namespace."""
    subject = item.subject
    diagram = item.diagram

    if not (subject and diagram):
        return False

    namespace = subject.namespace
    parent = item.parent

    # if there is a parent (i.e. interaction)
    if parent and parent.subject and parent.subject.namespace is not namespace:
        return False

    return (
        diagram.gettext("(from {namespace})").format(namespace=namespace.name)
        if namespace is not item.diagram.owner
        else ""
    )
