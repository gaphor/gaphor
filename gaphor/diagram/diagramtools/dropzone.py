from typing import Type

from gaphas.aspect.move import Move as MoveAspect
from gaphas.guide import GuidedItemMove
from gaphas.tool.itemtool import item_at_point
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.diagram.grouping import Group
from gaphor.diagram.presentation import (
    ElementPresentation,
    LinePresentation,
    Presentation,
)


def drop_zone_tool(
    view: GtkView, item_class: Type[Presentation]
) -> Gtk.EventController:
    ctrl = Gtk.EventControllerMotion.new(view)
    ctrl.connect("motion", on_motion, item_class)
    return ctrl


def on_motion(controller, x, y, item_class: Type[Presentation]):
    view: GtkView = controller.get_widget()
    model = view.model

    try:
        parent = item_at_point(view, (x, y))
    except KeyError:
        parent = None

    if parent:
        adapter_type = Group.registry.get_registration(type(parent), item_class)
        # Do not do in depth check id we can actually connect.
        # We can do that only when we have and item_class instance.
        if adapter_type:
            view.selection.dropzone_item = parent
        else:
            view.selection.dropzone_item = None
        model.request_update(parent, matrix=False)
    else:
        if view.selection.dropzone_item:
            model.request_update(view.selection.dropzone_item)
        view.selection.dropzone_item = None


@MoveAspect.register(ElementPresentation)
@MoveAspect.register(LinePresentation)
@MoveAspect.register(Presentation)
class DropZoneMove(GuidedItemMove):
    def move(self, pos):
        """Move the item.

        x and y are in view coordinates.
        """
        super().move(pos)
        item = self.item
        view = self.view
        x, y = pos

        current_parent = item.parent
        over_item = item_at_point(view, (x, y), selected=False)

        if not over_item:
            view.selection.dropzone_item = None
            return

        if current_parent and not over_item:
            # are we going to remove from parent?
            group = Group(current_parent, item)
            if group:
                view.selection.dropzone_item = current_parent
                current_parent.request_update(matrix=False)

        if over_item:
            # are we going to add to parent?
            group = Group(over_item, item)
            if group and group.can_contain():
                view.selection.dropzone_item = over_item
                over_item.request_update(matrix=False)

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
                    old_parent.request_update(matrix=False)
                return

            if old_parent:
                item.parent = None

                adapter = Group(old_parent, item)
                if adapter:
                    adapter.ungroup()

                old_parent.request_update()

            if new_parent:
                item.parent = new_parent

                adapter = Group(new_parent, item)
                if adapter and adapter.can_contain():
                    adapter.group()

                new_parent.request_update()
        finally:
            view.selection.dropzone_item = None
