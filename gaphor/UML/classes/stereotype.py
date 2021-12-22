"""Support code for dealing with stereotypes in diagrams."""

from gaphor.core.format import format
from gaphor.core.styling import TextAlign, VerticalAlign
from gaphor.diagram.shapes import Box, Text, draw_top_separator


def stereotype_compartments(subject):
    return filter(
        None,
        (
            _create_stereotype_compartment(appliedStereotype)
            for appliedStereotype in subject.appliedStereotype
        )
        if subject
        else [],
    )


def _create_stereotype_compartment(appliedStereotype):
    def lazy_format(slot):
        return lambda: format(slot)

    slots = [slot for slot in appliedStereotype.slot if slot.value]

    if slots:
        return Box(
            Text(
                text=lazy_format(appliedStereotype.classifier[0]),
                style={"padding": (0, 0, 4, 0)},
            ),
            *(
                Text(text=lazy_format(slot), style={"text-align": TextAlign.LEFT})
                for slot in slots
            ),
            style={
                "padding": (4, 4, 4, 4),
                "min-height": 8,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_top_separator,
        )
    else:
        return None
