import functools
import itertools
import logging
from typing import Type

from gaphas.geometry import Rectangle
from gaphas.guide import GuidedItemMove
from gaphas.item import NW, SE
from gaphas.move import Move as MoveAspect
from gaphas.tool.itemtool import item_at_point
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.diagram.connectors import Connector
from gaphor.diagram.grouping import Group
from gaphor.diagram.presentation import (
    ElementPresentation,
    LinePresentation,
    Presentation,
)

log = logging.getLogger(__name__)


def drop_zone_tool(
    view: GtkView, item_class: Type[Presentation]
) -> Gtk.EventController:
    ctrl = (
        Gtk.EventControllerMotion.new(view)
        if Gtk.get_major_version() == 3
        else Gtk.EventControllerMotion.new()
    )
    ctrl.connect("motion", on_motion, item_class)
    return ctrl


@functools.lru_cache()
def has_registration(generic_type, parent_type, child_type):
    get_registration = generic_type.registry.get_registration
    for t1, t2 in itertools.product(parent_type.__mro__, child_type.__mro__):
        if get_registration(t1, t2):
            return True


def on_motion(controller, x, y, item_class: Type[Presentation]):
    view: GtkView = controller.get_widget()
    model = view.model

    try:
        parent = next(item_at_point(view, (x, y)), None)
    except KeyError:
        parent = None

    if parent:
        parent_type = type(parent)
        can_group = has_registration(Group, parent_type, item_class)  # type: ignore[arg-type]
        can_connect = has_registration(Connector, parent_type, item_class)  # type: ignore[arg-type]

        view.selection.dropzone_item = parent if can_group or can_connect else None
        model.request_update(parent)
    else:
        if view.selection.dropzone_item:
            model.request_update(view.selection.dropzone_item)
        view.selection.dropzone_item = None


@MoveAspect.register(ElementPresentation)
@MoveAspect.register(LinePresentation)
@MoveAspect.register(Presentation)
class DropZoneMove(GuidedItemMove):
    def start_move(self, pos):
        super().start_move(pos)
        if self.item.parent:
            self.view.selection.dropzone_item = self.item.parent

    def move(self, pos):
        """Move the item.

        x and y are in view coordinates.
        """
        super().move(pos)
        item = self.item
        view = self.view
        x, y = pos

        over_item = next(
            item_at_point(view, (x, y), exclude=view.selection.selected_items), None
        )

        if not over_item:
            view.selection.dropzone_item = None
            return

        # are we going to add to parent?
        group = Group(over_item, item)
        if group and group.can_contain():
            view.selection.dropzone_item = over_item
            over_item.request_update()

    def stop_move(self, pos):
        """Motion stops: drop!"""
        super().stop_move(pos)
        item = self.item
        view = self.view
        old_parent = item.parent
        new_parent = view.selection.dropzone_item
        try:

            if new_parent is old_parent:
                if old_parent is not None:
                    old_parent.request_update()
                return

            if old_parent:
                item.change_parent(None)

                adapter = Group(old_parent, item)
                if adapter:
                    adapter.ungroup()

                old_parent.request_update()

            if new_parent:
                grow_parent(new_parent, item)
                item.change_parent(new_parent)

                adapter = Group(new_parent, item)
                if adapter and adapter.can_contain():
                    adapter.group()

                new_parent.request_update()
        finally:
            view.selection.dropzone_item = None


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
