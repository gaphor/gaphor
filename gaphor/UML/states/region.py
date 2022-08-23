from gaphor.core.styling import JustifyContent, TextAlign
from gaphor.diagram.shapes import BoundedBox, Text, draw_top_separator


def region_compartment(subject):
    if not subject:
        return

    for index, region in enumerate(subject.region):
        yield _create_region_compartment(region, index)


def _create_region_compartment(region, index):
    return BoundedBox(
        Text(
            text=lambda: region.name or "",
            style={"text-align": TextAlign.LEFT},
        ),
        style={
            "padding": (4, 4, 4, 4),
            "min-height": 100,
            "justify-content": JustifyContent.START,
            "dash-style": (7, 3) if index > 0 else (),
        },
        draw=draw_top_separator,
    )
