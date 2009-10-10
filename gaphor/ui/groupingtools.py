from zope import component

import gtk

from gaphor.diagram.interfaces import IGroup
from gaphor.ui.diagramtools import PlacementTool
from gaphas.tool import ItemTool

# cursor to indicate grouping
IN_CURSOR = gtk.gdk.Cursor(gtk.gdk.DIAMOND_CROSS)

# cursor to indicate ungrouping
OUT_CURSOR = gtk.gdk.Cursor(gtk.gdk.SIZING)

class GroupPlacementTool(PlacementTool):
    """
    Try to group items when placing them on diagram.
    """

    def __init__(self, item_factory, after_handler=None, handle_index=-1):
        super(GroupPlacementTool, self).__init__(item_factory,
                after_handler,
                handle_index)

        self._parent = None


    def on_button_press(self, context, event):
        """
        If new item was placed onto diagram, then try to group it with
        parent using grouping adapter.
        """

        # first get parent
        self._parent = None
        if event.button == 1:
            context.ungrab()
            view = context.view
            self._parent = view.get_item_at_point((event.x, event.y))

        # now, place the new item
        placed = PlacementTool.on_button_press(self, context, event)

        # if there is a parent, then try to group item and parent
        if placed and self._parent:
            view = context.view
            item = view.focused_item
            
            adapter = component.queryMultiAdapter((self._parent, item), IGroup)
            if adapter and adapter.can_contain():
                adapter.group()

        return placed


    def on_motion_notify(self, context, event):
        """
        Change parent item to dropzone state if it can accept diagram item
        object to be created.
        """
        view = context.view

        if view.focused_item:
            view.unselect_item(view.focused_item)
            view.focused_item = None

        try:
            parent = view.get_item_at_point((event.x, event.y))
        except KeyError:
            # No bounding box yet.
            return

        if parent:
            adapter = component.queryMultiAdapter((parent, self._factory.item_class), IGroup)
            if adapter and adapter.can_contain():
                view.dropzone_item = parent
                view.window.set_cursor(IN_CURSOR)
            else:
                view.dropzone_item = None
                view.window.set_cursor(None)
        else:
            view.dropzone_item = None
            view.window.set_cursor(None)


    def _create_item(self, context, pos):
        """
        Create diagram item and place it within parent's boundaries.
        """
        # if no parent, then create with parent placement tool
        if not self._parent:
            return super(GroupPlacementTool, self)._create_item(context, pos)

        item = self._factory(self._parent)
        
        view = context.view
        # get item position through parent world
        x, y = view.canvas.get_matrix_c2i(self._parent).transform_point(*pos)
        item.matrix.translate(x, y)

        view.dropzone_item = None
        view.window.set_cursor(None)

        return item


class GroupItemTool(ItemTool):
    """
    Group diagram item by dropping it on another item.

    Works only for one selected item, now.
    """

    def on_motion_notify(self, context, event):
        """
        Indicate possibility of grouping/ungrouping of selected item.
        """
        super(GroupItemTool, self).on_motion_notify(context, event)
        view = context.view

        if event.state & gtk.gdk.BUTTON_PRESS_MASK and len(view.selected_items) == 1:
            item = list(view.selected_items)[0]
            parent = view.canvas.get_parent(item)

            over = view.get_item_at_point((event.x, event.y), selected=False)
            assert over is not item

            if over is parent: # do nothing when item is over parent
                view.dropzone_item = None
                view.window.set_cursor(None)
                return

            if parent and not over:  # are we going to remove from parent?
                adapter = component.queryMultiAdapter((parent, item), IGroup)
                if adapter:
                    view.window.set_cursor(OUT_CURSOR)
                    view.dropzone_item = parent

            if over:       # are we going to add to parent?
                adapter = component.queryMultiAdapter((over, item), IGroup)
                if adapter and adapter.can_contain():
                    view.dropzone_item = over
                    view.window.set_cursor(IN_CURSOR)


    def on_button_release(self, context, event):
        """
        Group item if it is dropped on parent's item. Ungroup item if it is
        moved out of its parent boundaries. Method also moves item from old
        parent to new one (regrouping).
        """
        super(GroupItemTool, self).on_button_release(context, event)
        view = context.view
        if event.button == 1 and len(view.selected_items) == 1:
            item = list(view.selected_items)[0]
            parent = view.canvas.get_parent(item)
            over = view.get_item_at_point((event.x, event.y), selected=False)
            assert over is not item

            if over is parent:
                if parent is not None:
                    parent.request_update(matrix=False)
                return

            if parent: # remove from parent
                adapter = component.queryMultiAdapter((parent, item), IGroup)
                if adapter:
                    adapter.ungroup()

                    canvas = view.canvas
                    canvas.reparent(item, None)

                    # reset item's position
                    px, py = canvas.get_matrix_c2i(parent).transform_point(0, 0)
                    item.matrix.translate(-px, -py)


            if over: # add to over (over becomes parent)
                adapter = component.queryMultiAdapter((over, item), IGroup)
                if adapter and adapter.can_contain():
                    adapter.group()

                    canvas = view.canvas
                    canvas.reparent(item, over)

                    # reset item's position
                    x, y = canvas.get_matrix_i2c(over).transform_point(0, 0)
                    item.matrix.translate(-x, -y)


        view.dropzone_item = None
        view.window.set_cursor(None)


# vim:sw=4:et:ai
