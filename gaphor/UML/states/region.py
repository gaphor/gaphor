from gaphor.diagram.shapes import Box, CssNode, Text, draw_top_separator


def region_compartment(subject):
    if not subject:
        return

    for index, region in enumerate(subject.region):
        yield _create_region_compartment(region, index)


def _create_region_compartment(region, index):
    return CssNode(
        "region",
        region,
        Box(
            Text(
                text=lambda: region.name or "",
            ),
            draw=draw_top_separator,
        ),
    )
