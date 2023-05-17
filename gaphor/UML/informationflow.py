"""Support functions for information flow

And by extension SysML item flow.
"""

from gaphor.core.format import format
from gaphor.diagram.presentation import Presentation
from gaphor.diagram.shapes import Text, cairo_state
from gaphor.UML.classes.association import get_center_pos
from gaphor.UML.recipes import stereotypes_str


def shape_information_flow(presentation: Presentation) -> list[Text]:
    return [
        Text(
            text=lambda: ", ".join(
                presentation.subject.informationFlow[:].conveyed[:].name
            )
        ),
        # Also support SysML ItemFlow:
        Text(
            text=lambda: stereotypes_str(
                presentation.subject.informationFlow[0].itemProperty.type,
                raaml_stereotype_workaround(
                    presentation.subject.informationFlow[0].itemProperty.type
                ),
            )
            if presentation.subject.informationFlow
            else ""
        ),
        Text(
            text=lambda: format(
                presentation.subject.informationFlow[0].itemProperty, type=True
            )
            if presentation.subject.informationFlow
            else ""
        ),
    ]


def watch_information_flow(presentation: Presentation) -> None:
    presentation.watch("subject[Connector].informationFlow.informationSource")
    presentation.watch("subject[Connector].informationFlow.conveyed.name")
    presentation.watch("subject[Connector].informationFlow[ItemFlow].itemProperty.name")
    presentation.watch(
        "subject[Connector].informationFlow[ItemFlow].itemProperty.type.name"
    )
    presentation.watch(
        "subject[Connector].informationFlow[ItemFlow].itemProperty.type.appliedStereotype.classifier.name"
    )


def draw_information_flow(presentation: Presentation, context) -> None:
    subject = presentation.subject
    if not subject or not subject.informationFlow:
        return

    handles = presentation.handles()
    pos, angle = get_center_pos(handles)
    inv = (
        1
        if (subject.end[0].role in subject.informationFlow[:].informationTarget)
        else -1
    )
    with cairo_state(context.cairo) as cr:
        cr.translate(*pos)
        cr.rotate(angle)
        cr.move_to(0, 0)
        cr.line_to(12 * inv, 8)
        cr.line_to(12 * inv, -8)
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
