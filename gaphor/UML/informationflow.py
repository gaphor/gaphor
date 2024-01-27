"""Support functions for information flow

And by extension SysML item flow.
"""

from gaphor.core.format import format
from gaphor.diagram.presentation import Presentation
from gaphor.diagram.shapes import Box, CssNode, Shape, Text, cairo_state
from gaphor.UML.classes.association import get_center_pos
from gaphor.UML.recipes import stereotypes_str


def shape_information_flow(presentation: Presentation, attribute: str) -> list[Shape]:
    return [
        Text(
            text=lambda: ", ".join(
                getattr(presentation.subject, attribute)[:].conveyed[:].name
            )
        ),
        # Also support SysML ItemFlow:
        CssNode(
            "itemflow",
            None,
            Box(
                CssNode(
                    "stereotypes",
                    None,
                    Text(
                        text=lambda: stereotypes_str(
                            iflow[0].itemProperty.type,
                            raaml_stereotype_workaround(iflow[0].itemProperty.type),
                        )
                        if (iflow := getattr(presentation.subject, attribute))
                        else ""
                    ),
                ),
                CssNode(
                    "property",
                    None,
                    Text(
                        text=lambda: format(iflow[0].itemProperty, type=True)
                        if (iflow := getattr(presentation.subject, attribute))
                        else ""
                    ),
                ),
            ),
        ),
    ]


def watch_information_flow(
    presentation: Presentation, cast: str, attribute: str
) -> None:
    presentation.watch(f"subject[{cast}].{attribute}.informationSource")
    presentation.watch(f"subject[{cast}].{attribute}.conveyed.name")
    presentation.watch(f"subject[{cast}].{attribute}[ItemFlow].itemProperty.name")
    presentation.watch(f"subject[{cast}].{attribute}[ItemFlow].itemProperty.type.name")
    presentation.watch(
        f"subject[{cast}].{attribute}[ItemFlow].itemProperty.type.appliedStereotype.classifier.name"
    )


def draw_information_flow(presentation: Presentation, context, invert: bool) -> None:
    handles = presentation.handles()
    pos, angle = get_center_pos(handles)
    f = 1 if invert else -1
    with cairo_state(context.cairo) as cr:
        cr.translate(*pos)
        cr.rotate(angle)
        cr.move_to(0, 0)
        cr.line_to(12 * f, 8)
        cr.line_to(12 * f, -8)
        cr.fill()


def raaml_stereotype_workaround(element):
    """This is a temporary fix to ensure ItemFlow is showing proper stereotypes
    for Controller, Feedback and ControlAction from RAAML."""
    if not element:
        return ()

    name: str = type(element).__name__
    if name in {"Controller", "Feedback", "ControlAction"}:
        return (name[0].lower() + name[1:],)
    return ()
