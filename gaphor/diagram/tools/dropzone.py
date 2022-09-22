from __future__ import annotations

import logging

from gaphas.geometry import Rectangle
from gaphas.guide import GuidedItemMoveMixin
from gaphas.item import NW, SE, Item
from gaphas.move import ItemMove
from gaphas.move import Move as MoveAspect
from gaphas.tool.itemtool import item_at_point
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.core.modeling import Element
from gaphor.diagram.connectors import can_connect
from gaphor.diagram.group import can_group, group, ungroup
from gaphor.diagram.presentation import (
    ElementPresentation,
    LinePresentation,
    Presentation,
)
from gaphor.UML.recipes import owner_package

log = logging.getLogger(__name__)


def drop_zone_tool(
    view: GtkView, item_class: type[Presentation], subject_class: type[Element] | None
) -> Gtk.EventController:
    ctrl = (
        Gtk.EventControllerMotion.new(view)
        if Gtk.get_major_version() == 3
        else Gtk.EventControllerMotion.new()
    )
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
        item = self.item
        view = self.view
        old_parent = item.parent
        new_parent = view.selection.dropzone_item

        if new_parent is old_parent:
            if old_parent is not None:
                old_parent.request_update()
            return

        if old_parent and ungroup(old_parent.subject, item.subject):
            item.change_parent(None)
            old_parent.request_update()

        if new_parent and item.subject and group(new_parent.subject, item.subject):
            grow_parent(new_parent, item)
            item.change_parent(new_parent)
        elif item.subject:
            diagram_parent = owner_package(item.diagram)
            group(diagram_parent, item.subject)


@MoveAspect.register(ElementPresentation)
@MoveAspect.register(LinePresentation)
@MoveAspect.register(Presentation)
class DropZoneMove(DropZoneMoveMixin, GuidedItemMoveMixin, ItemMove):
    pass


def grow_parent(parent, item):
    if not isinstance(item, ElementPresentation):
        return

    if not isinstance(parent, ElementPresentation):
        log.warning(f"Can not grow item {parent}: not an ElementPresentation")
        return

    parent_bb = _bounds(parent)
    item_bb = _bounds(item)
    item_bb.expand(20)
    new_parent_bb = parent_bb + item_bb

    c2i = parent.matrix_i2c.inverse()
    parent.handles()[NW].pos = c2i.transform_point(new_parent_bb.x, new_parent_bb.y)
    parent.handles()[SE].pos = c2i.transform_point(new_parent_bb.x1, new_parent_bb.y1)


def _bounds(item):
    transform = item.matrix_i2c.transform_point
    x0, y0 = transform(*item.handles()[NW].pos)
    x1, y1 = transform(*item.handles()[SE].pos)
    return Rectangle(x0, y0, x1=x1, y1=y1)
