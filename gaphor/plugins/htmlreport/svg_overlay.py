"""SVG post-processing to add clickable overlay regions.

After Cairo renders an SVG, this module parses it and injects
transparent clickable <a> elements over diagram items so they
link to element detail views in the HTML report.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from gaphas.geometry import Rectangle
from gaphas.item import NW, SE
from gaphas.painter import FreeHandPainter, PainterChain

from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import Diagram, StyledDiagram
from gaphor.diagram.export import calc_bounding_box, diagram_type_height
from gaphor.diagram.painter import DiagramTypePainter, ItemPainter
from gaphor.diagram.presentation import (
    AttachedPresentation,
    ElementPresentation,
    LinePresentation,
)

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"


def compute_svg_offset(diagram: Diagram, padding: int = 8) -> tuple[float, float]:
    """Compute the translation offset applied during SVG export.

    This replicates the logic from render() in gaphor/diagram/export.py
    so we can map item coordinates to SVG coordinates.
    """
    items = list(diagram.get_all_items())
    diagram.update(diagram.ownedPresentation)

    model = diagram.model
    style_sheet = model.style_sheet or StyleSheet()
    item_painter = ItemPainter(compute_style=style_sheet.compute_style)
    sloppiness = style_sheet.compute_style(StyledDiagram(diagram)).get(
        "line-style", 0.0
    )
    painter = PainterChain().append(
        FreeHandPainter(item_painter, sloppiness) if sloppiness else item_painter
    )
    painter.append(DiagramTypePainter(diagram, style_sheet.compute_style))

    type_padding = diagram_type_height(diagram)
    bounding_box = calc_bounding_box(items, painter)

    tx = -bounding_box.x + padding
    ty = -bounding_box.y + padding + type_padding
    return tx, ty


def item_svg_bounds(item, tx: float, ty: float) -> Rectangle | None:
    """Get item bounds in SVG coordinates.

    Returns None if the item has no subject (nothing to link to).
    """
    if item.subject is None:
        return None

    if isinstance(item, ElementPresentation):
        transform = item.matrix_i2c.transform_point
        x0, y0 = transform(*item.handles()[NW].pos)
        x1, y1 = transform(*item.handles()[SE].pos)
        return Rectangle(x0 + tx, y0 + ty, x1=x1 + tx, y1=y1 + ty)

    if isinstance(item, (LinePresentation, AttachedPresentation)):
        transform = item.matrix_i2c.transform_point
        points = [transform(*h.pos) for h in item.handles()]
        if not points:
            return None
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return Rectangle(min(xs) + tx, min(ys) + ty, x1=max(xs) + tx, y1=max(ys) + ty)

    return None


def inject_overlays(svg_path: str, diagram: Diagram, padding: int = 8) -> None:
    """Parse an exported SVG and inject clickable overlay elements.

    For each item with a subject, adds a transparent clickable region
    that links to ``#element/{subject.id}`` in the HTML report.
    """
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xlink", XLINK_NS)

    tree = ET.parse(svg_path)
    root = tree.getroot()

    tx, ty = compute_svg_offset(diagram, padding)

    items = list(diagram.get_all_items())

    for item in items:
        bounds = item_svg_bounds(item, tx, ty)
        if bounds is None:
            continue

        subject_id = item.subject.id
        href = f"#element/{subject_id}"

        a_elem = ET.SubElement(root, f"{{{SVG_NS}}}a")
        a_elem.set("href", href)
        a_elem.set("target", "_parent")

        if isinstance(item, LinePresentation):
            # For lines, draw a transparent wide polyline for easy clicking
            transform = item.matrix_i2c.transform_point
            points = [transform(*h.pos) for h in item.handles()]
            points_str = " ".join(f"{x + tx},{y + ty}" for x, y in points)
            polyline = ET.SubElement(a_elem, f"{{{SVG_NS}}}polyline")
            polyline.set("points", points_str)
            polyline.set("stroke", "transparent")
            polyline.set("stroke-width", "12")
            polyline.set("fill", "none")
            polyline.set("style", "cursor: pointer;")
        else:
            # For elements, draw a transparent rect
            rect = ET.SubElement(a_elem, f"{{{SVG_NS}}}rect")
            rect.set("x", str(bounds.x))
            rect.set("y", str(bounds.y))
            rect.set("width", str(bounds.width))
            rect.set("height", str(bounds.height))
            rect.set("fill", "transparent")
            rect.set("style", "cursor: pointer;")

    tree.write(svg_path, xml_declaration=True, encoding="unicode")
