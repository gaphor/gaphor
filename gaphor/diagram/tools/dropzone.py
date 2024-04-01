from __future__ import annotations

from gaphas.guide import GuidedItemMoveMixin
from gaphas.item import Item
from gaphas.move import ItemMove
from gaphas.move import Move as MoveAspect
from gaphas.tool.itemtool import item_at_point
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.core.modeling import Element
from gaphor.diagram.connectors import can_connect
from gaphor.diagram.drop import drop
from gaphor.diagram.group import can_group
from gaphor.diagram.presentation import (
    ElementPresentation,
    LinePresentation,
    Presentation,
)


def drop_zone_tool(
    item_class: type[Presentation], subject_class: type[Element] | None
) -> Gtk.EventController:
    ctrl = Gtk.EventControllerMotion.new()
    ctrl.connect("motion", on_motion, item_class, subject_class)
    return ctrl


def on_motion(
    controller,
    x,
    y,
    item_class: type[Presentation],
    subject_class: type[Element] | None,
):
    view: GtkView = controller.get_widget()
    model = view.model

    try:
        parent = next(item_at_point(view, (x, y)), None)
    except KeyError:
        parent = None

    if parent and subject_class:
        view.selection.dropzone_item = (
            parent
            if can_group(parent.subject, subject_class)
            or can_connect(parent, item_class)  # type: ignore[arg-type]
            else None
        )
        model.request_update(parent)
    else:
        if view.selection.dropzone_item:
            model.request_update(view.selection.dropzone_item)
        view.selection.dropzone_item = None


class DropZoneMoveMixin:
    view: GtkView
    item: Item

    def start_move(self, pos):
        super().start_move(pos)  # type: ignore[misc]
        if self.item.parent:
            self.view.selection.dropzone_item = self.item.parent

    def move(self, pos):
        """Move the item.

        x and y are in view coordinates.
        """
        super().move(pos)  # type: ignore[misc]
        item = self.item
        view = self.view
        x, y = pos

        over_item = next(
            item_at_point(view, (x, y), exclude=view.selection.selected_items), None
        )

        if not over_item:
            view.selection.dropzone_item = None
            return

        if item.subject and can_group(over_item.subject, item.subject):
            view.selection.dropzone_item = over_item
            over_item.request_update()

    def stop_move(self, pos):
        """Motion stops: drop!"""
        super().stop_move(pos)  # type: ignore[misc]
        new_parent = self.view.selection.dropzone_item
        self.drop(new_parent, pos)

    def drop(self, new_parent, pos):
        if new_parent:
            drop(
                self.item,
                new_parent,
                *self.view.get_matrix_v2i(new_parent).transform_point(*pos),
            )
        else:
            drop(
                self.item,
                self.item.diagram,
                *self.view.matrix.inverse().transform_point(*pos),
            )


@MoveAspect.register(ElementPresentation)
@MoveAspect.register(LinePresentation)
@MoveAspect.register(Presentation)
class DropZoneMove(DropZoneMoveMixin, GuidedItemMoveMixin, ItemMove):
    pass
