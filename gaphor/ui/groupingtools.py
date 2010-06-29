from zope import component

import gtk

from gaphor.diagram.interfaces import IGroup
from gaphor.ui.diagramtools import PlacementTool
from gaphas.tool import ItemTool
from gaphas.aspect import InMotion
from gaphas.guide import GuidedItemInMotion
from gaphor.diagram.elementitem import ElementItem

# cursor to indicate grouping
IN_CURSOR = gtk.gdk.Cursor(gtk.gdk.DIAMOND_CROSS)

# cursor to indicate ungrouping
OUT_CURSOR = gtk.gdk.Cursor(gtk.gdk.SIZING)

class GroupPlacementTool(PlacementTool):
    """
    Try to group items when placing them on diagram.
    """

    def __init__(self, view, item_factory, after_handler=None, handle_index=-1):
        super(GroupPlacementTool, self).__init__(view,
                item_factory, after_handler, handle_index)
        self._parent = None


    def on_motion_notify(self, event):
        """
        Change parent item to dropzone state if it can accept diagram item
        object to be created.
        """
        view = self.view

        if view.focused_item:
            view.unselect_item(view.focused_item)
            view.focused_item = None

        try:
            parent = view.get_item_at_point((event.x, event.y))
        except KeyError:
            parent = None

        if parent:
            # create dummy adapter
            adapter = component.queryMultiAdapter((parent, self._factory.item_class()), IGroup)
            if adapter and adapter.can_contain():
                view.dropzone_item = parent
                view.window.set_cursor(IN_CURSOR)
                self._parent = parent
            else:
                view.dropzone_item = None
                view.window.set_cursor(None)
                self._parent = None
            parent.request_update(matrix=False)
        else:
            if view.dropzone_item:
                view.dropzone_item.request_update(matrix=False)
            view.dropzone_item = None
            view.window.set_cursor(None)


    def _create_item(self, pos, **kw):
        """
        Create diagram item and place it within parent's boundaries.
        """
        parent = self._parent
        view = self.view
        try:
            adapter = component.queryMultiAdapter((parent, self._factory.item_class()), IGroup)
            if parent and adapter and adapter.can_contain():
                kw['parent'] = parent

            item = super(GroupPlacementTool, self)._create_item(pos, **kw)

            adapter = component.queryMultiAdapter((parent, item), IGroup)
            if parent and item and adapter:
                adapter.group()

                canvas = view.canvas
                parent.request_update(matrix=False)
        finally:
            self._parent = None
            view.dropzone_item = None
            view.window.set_cursor(None)
        return item


@InMotion.when_type(ElementItem)
class DropZoneInMotion(GuidedItemInMotion):


    def move(self, pos):
        """
        Move the item. x and y are in view coordinates.
        """
        super(DropZoneInMotion, self).move(pos)
        item = self.item
        view = self.view
        x, y = pos

        current_parent = view.canvas.get_parent(item)
        over_item = view.get_item_at_point((x, y), selected=False)

        if not over_item:
            view.dropzone_item = None
            view.window.set_cursor(None)
            return

        if current_parent and not over_item:  # are we going to remove from parent?
            adapter = component.queryMultiAdapter((current_parent, item), IGroup)
            if adapter:
                view.window.set_cursor(OUT_CURSOR)
                view.dropzone_item = current_parent
                current_parent.request_update(matrix=False)

        if over_item:
            # are we going to add to parent?
            adapter = component.queryMultiAdapter((over_item, item), IGroup)
            if adapter and adapter.can_contain():
                view.dropzone_item = over_item
                view.window.set_cursor(IN_CURSOR)
                over_item.request_update(matrix=False)


    def stop_move(self):
        """
        Motion stops: drop!
        """
        super(DropZoneInMotion, self).stop_move()
        item = self.item
        view = self.view
        canvas = view.canvas
        old_parent = view.canvas.get_parent(item)
        new_parent = view.dropzone_item
        try:

            if new_parent is old_parent:
                if old_parent is not None:
                    old_parent.request_update(matrix=False)
                return

            if old_parent:
                adapter = component.queryMultiAdapter((old_parent, item), IGroup)
                if adapter:
                    adapter.ungroup()

                canvas.reparent(item, None)
                m = canvas.get_matrix_i2c(old_parent)
                item.matrix *= m
                old_parent.request_update()

            if new_parent:
                adapter = component.queryMultiAdapter((new_parent, item), IGroup)
                if adapter and adapter.can_contain():
                    adapter.group()

                canvas.reparent(item, new_parent)
                m = canvas.get_matrix_c2i(new_parent)
                item.matrix *= m
                new_parent.request_update()
        finally:
            view.dropzone_item = None
            view.window.set_cursor(None)

    
# vim:sw=4:et:ai
