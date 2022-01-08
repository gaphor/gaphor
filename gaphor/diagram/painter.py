"""The painter module provides different painters for parts of the diagram.

Painters can be swapped in and out.

Each painter takes care of a layer in the diagram (such as grid, items
and handles).
"""

from __future__ import annotations

from cairo import LINE_JOIN_ROUND
from gi.repository import GLib, Pango, PangoCairo

from gaphor.core.modeling.diagram import DrawContext, StyledDiagram, StyledItem
from gaphor.diagram.selection import Selection


class ItemPainter:
    def __init__(self, selection: Selection | None = None):
        self.selection: Selection = selection or Selection()

    def paint_item(self, item, cr):
        selection = self.selection
        diagram = item.diagram
        style = diagram.style(StyledItem(item, selection))

        cr.save()
        try:
            cr.set_line_join(LINE_JOIN_ROUND)
            cr.set_source_rgba(*style["color"])
            cr.transform(item.matrix_i2c.to_cairo())

            item.draw(
                DrawContext(
                    cairo=cr,
                    style=style,
                    selected=(item in selection.selected_items),
                    focused=(item is selection.focused_item),
                    hovered=(item is selection.hovered_item),
                    dropzone=(item is selection.dropzone_item),
                )
            )

        finally:
            cr.restore()

    def paint(self, items, cr):
        """Draw the items."""
        for item in items:
            self.paint_item(item, cr)


class DiagramTypePainter:
    def __init__(self, diagram):
        self.diagram = diagram

    def paint(self, _items, cr):
        diagram = self.diagram
        if not diagram.diagramType:
            return
        style = diagram.style(StyledDiagram(diagram))
        layout = PangoCairo.create_layout(cr)
        escape = GLib.markup_escape_text
        layout.set_markup(
            f"<b>{escape(diagram.diagramType)}</b> {escape(diagram.name)}", length=-1
        )

        font_family = style.get("font-family")
        font_size = style.get("font-size")

        fd = Pango.FontDescription.new()
        fd.set_family(font_family)
        fd.set_absolute_size(font_size * Pango.SCALE)
        layout.set_font_description(fd)

        w, h = layout.get_pixel_size()
        cr.save()
        try:
            cr.identity_matrix()
            cr.set_line_width(1)

            cr.move_to(-1, 12 + h)
            cr.line_to(12 + w, 12 + h)
            cr.line_to(18 + w, 8 + h / 2)
            cr.line_to(18 + w, -1)
            cr.line_to(-1, -1)

            cr.set_source_rgba(1.0, 1.0, 1.0, 0.6)
            cr.fill_preserve()
            cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
            cr.stroke()
            cr.move_to(6, 8)
            PangoCairo.show_layout(cr, layout)
        finally:
            cr.restore()
