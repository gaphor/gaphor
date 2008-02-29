"""
Tools for handling items on the canvas.

Although Gaphas has quite a few useful tools, some tools need to be extended:
 - PlacementTool: should perform undo
 - HandleTool: shoudl support adapter based connection protocol
 - TextEditTool: should support adapter based edit protocol
"""

import gtk
from cairo import Matrix
from zope import component

from gaphas.geometry import distance_point_point, distance_point_point_fast, \
                            distance_line_point, distance_rectangle_point
from gaphas.item import Line
from gaphas.tool import Tool, HandleTool, PlacementTool as _PlacementTool
from gaphas.tool import ToolChain, HoverTool, ItemTool, RubberbandTool



from gaphor.core import inject, Transaction, transactional

from gaphor.diagram.interfaces import IEditor, IConnect

__version__ = '$Revision$'


class ConnectHandleTool(HandleTool):
    """
    Handle Tool (acts on item handles) that uses the IConnect protocol
    to connect items to one-another.

    It also adds handles to lines when a line is grabbed on the middle of
    a line segment (points are drawn by the LineSegmentPainter).

    Attributes:
     - _adapter: current adapter used to connect items
    """
    GLUE_DISTANCE = 10

    def __init__(self):
        super(ConnectHandleTool, self).__init__()
        self._adapter = None


    def glue(self, view, item, handle, vx, vy):
        """
        Find the nearest item that the handle may connect to.

        This is done by checking for an IConnect adapter for all items in the
        proximity of ``(vx, xy)``.  If such an adapter exists, the glue
        position is determined. The item with the glue point closest to the
        handle will be glued to.

        view: The view
        item: The item who's about to connect, owner of handle
        handle: the handle to connect
        vx, vy: handle position in view coordinates
        """
        # localize methods
        v2i = view.get_matrix_v2i
        i2v = view.get_matrix_i2v
        drp = distance_rectangle_point
        get_item_bounding_box = view.get_item_bounding_box
        query_adapter = component.queryMultiAdapter

        dist = self.GLUE_DISTANCE
        max_dist = dist
        glue_pos = (0, 0)
        glue_item = None
        for i in view.get_items_in_rectangle((vx - dist, vy - dist,
                                              dist * 2, dist * 2),
                                             reverse=True):
            if i is item:
                continue
            
            b = get_item_bounding_box(i)
            ix, iy = v2i(i).transform_point(vx, vy)
            if drp(b, (vx, vy)) >= max_dist:
                continue
            
            adapter = query_adapter((i, item), IConnect)
            if adapter:
                pos = adapter.glue(handle)
                self._adapter = adapter
                if pos:
                    d = i.point(ix, iy)
                    if d <= dist:
                        dist = d
                        glue_pos = pos
                        glue_item = i

        if dist < max_dist:
            handle.pos = glue_pos

        # Return the glued item, this can be used by connect() to
        # determine which item it should connect to
        return glue_item


    def connect(self, view, item, handle, vx, vy):
        """
        Find an item near ``handle`` that ``item`` can connect to and connect.
        
        This is done by attempting a glue() operation. If there is something
        to glue (the handles are already positioned), the IConnect.connect
        is called for (glued_item, item).
        """
        connected = False
        try:
            glue_item = self.glue(view, item, handle, vx, vy)

            if glue_item:
                assert handle in self._adapter.line.handles()
                self._adapter.connect(handle)

                connected = True
            elif handle and handle.connected_to:
                handle.disconnect()

        finally:
            self._adapter = None


        return connected

    def disconnect(self, view, item, handle):
        """
        Disconnect the handle from the element by removing constraints.
        Do not yet release the connection on model level, since the handle
        may be connected to the same item on some other place.
        """
        if handle.connected_to:
            adapter = component.queryMultiAdapter((handle.connected_to, item), IConnect)
            adapter.disconnect_constraints(handle)
        
    def on_button_press(self, context, event):
        """
        In addition to the normal behavior, the button press event creates
        new handles if it is activated on the middle of a line segment.
        """
        if super(ConnectHandleTool, self).on_button_press(context, event):
            return True

        view = context.view
        item = view.hovered_item
        if item and item is view.focused_item and isinstance(item, Line):
            handles = item.handles()
            x, y = context.view.get_matrix_v2i(item).transform_point(event.x, event.y)
            for h1, h2 in zip(handles[:-1], handles[1:]):
                xp = (h1.x + h2.x) / 2
                yp = (h1.y + h2.y) / 2
                if distance_point_point_fast((x,y), (xp, yp)) <= 4:
                    segment = handles.index(h1)
                    item.split_segment(segment)

                    # Reconnect all constraints:
                    for i, h in view.canvas.get_connected_items(item):
                        adapter = component.getMultiAdapter((item, i), IConnect)
                        adapter.disconnect_constraints(h)
                        adapter.connect_constraints(h)

                    self.grab_handle(item, item.handles()[segment + 1])
                    context.grab()
                    return True

    def on_button_release(self, context, event):
        grabbed_handle = self._grabbed_handle
        grabbed_item = self._grabbed_item
        if super(ConnectHandleTool, self).on_button_release(context, event):
            if grabbed_handle and grabbed_item:
                handles = grabbed_item.handles()
                if handles[0] is grabbed_handle or handles[-1] is grabbed_handle:
                    return True
                segment = handles.index(grabbed_handle)
                before = handles[segment - 1]
                after = handles[segment + 1]
                d, p = distance_line_point(before.pos, after.pos, grabbed_handle.pos)
                if d < 2:
                    grabbed_item.merge_segment(segment)

                    # Reconnect all constraints:
                    for i, h in context.view.canvas.get_connected_items(grabbed_item):
                        adapter = component.getMultiAdapter((grabbed_item, i), IConnect)
                        adapter.disconnect_constraints(h)
                        adapter.connect_constraints(h)

            return True


class TextEditTool(Tool):
    """
    Text edit tool. Allows for elements that can adapt to the 
    IEditable interface to be edited.
    """

    def create_edit_window(self, view, x, y, text, *args):
        """
        Create a popup window with some editable text.
        """
        window = gtk.Window()
        window.set_property('decorated', False)
        window.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        #window.set_modal(True)
        window.set_parent_window(view.window)
        buffer = gtk.TextBuffer()
        if text:
            buffer.set_text(text)
            startiter, enditer = buffer.get_bounds()
            buffer.move_mark_by_name('selection_bound', startiter)
            buffer.move_mark_by_name('insert', enditer)
        text_view = gtk.TextView()
        text_view.set_buffer(buffer)
        #text_view.set_border_width(2)
        text_view.set_left_margin(2)
        text_view.set_right_margin(2)
        text_view.show()
        
        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        #frame.set_border_width(1)
        frame.add(text_view)
        frame.show()

        window.add(frame)
        #window.set_border_width(1)
        window.size_allocate(gtk.gdk.Rectangle(int(x), int(y), 50, 50))
        #window.move(int(x), int(y))
        cursor_pos = view.get_toplevel().get_screen().get_display().get_pointer()
        window.move(cursor_pos[1], cursor_pos[2])
        window.connect('focus-out-event', self._on_focus_out_event,
                       buffer, *args)
        text_view.connect('key-press-event', self._on_key_press_event,
                          buffer, *args)
        #text_view.set_size_request(50, 50)
        window.show()
        #text_view.grab_focus()
        #window.set_uposition(event.x, event.y)
        #window.focus

    @transactional
    def submit_text(self, widget, buffer, editor):
        """
        Submit the final text to the edited item.
        """
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        editor.update_text(text)
        widget.get_toplevel().destroy()

    def on_double_click(self, context, event):
        view = context.view
        item = view.hovered_item
        if item:
            try:
                editor = IEditor(item)
            except TypeError:
                # Could not adapt to IEditor
                return False
            x, y = view.get_matrix_v2i(item).transform_point(event.x, event.y)
            if editor.is_editable(x, y):
                text = editor.get_text()
                # get item at cursor
                self.create_edit_window(context.view, event.x, event.y,
                                        text, editor)
                return True

    def _on_key_press_event(self, widget, event, buffer, editor):
        if event.keyval == gtk.keysyms.Return:
            self.submit_text(widget, buffer, editor)
        elif event.keyval == gtk.keysyms.Escape:
            widget.get_toplevel().destroy()

    def _on_focus_out_event(self, widget, event, buffer, editor):
        self.submit_text(widget, buffer, editor)


class PlacementTool(_PlacementTool):
    """
    PlacementTool is used to place items on the canvas.
    """

    def __init__(self, item_factory, after_handler=None, handle_index=-1):
        """
        item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        _PlacementTool.__init__(self, factory=item_factory,
                                      handle_tool=ConnectHandleTool(),
                                      handle_index=handle_index)
        self.after_handler = after_handler
        self._tx = None

    def on_button_press(self, context, event):
        self._tx = Transaction()
        view = context.view
        view.unselect_all()
        if _PlacementTool.on_button_press(self, context, event):
            try:
                opposite = self.new_item.opposite(self.new_item.handles()[self._handle_index])
            except (KeyError, AttributeError):
                pass
            else:
                # Connect opposite handle first, using the HandleTool's
                # mechanisms

                # First make sure all matrices are updated:
                view.canvas.update_matrix(self.new_item)
                view.update_matrix(self.new_item)

                vx, vy = event.x, event.y

                item = self.handle_tool.glue(view, self.new_item, opposite, vx, vy)
                if item:
                    self.handle_tool.connect(view, self.new_item, opposite, vx, vy)
            return True
        return False
            
    def on_button_release(self, context, event):
        try:
            if self.after_handler:
                self.after_handler(self.new_item)
            return _PlacementTool.on_button_release(self, context, event)
        finally:
            self._tx.commit()
            self._tx = None



class TransactionalToolChain(ToolChain):
    """
    In addition to a normal toolchain, this chain begins an undo-transaction
    at button-press and commits the transaction at button-release.
    """

    def __init__(self):
        ToolChain.__init__(self)
        self._tx = None

    def on_button_press(self, context, event):
        self._tx = Transaction()
        return ToolChain.on_button_press(self, context, event)

    def on_button_release(self, context, event):
        try:
            return ToolChain.on_button_release(self, context, event)
        finally:
            if self._tx:
                self._tx.commit()
                self._tx = None

    def on_double_click(self, context, event):
        tx = Transaction()
        try:
            return ToolChain.on_double_click(self, context, event)
        finally:
            tx.commit()

    def on_triple_click(self, context, event):
        tx = Transaction()
        try:
            return ToolChain.on_triple_click(self, context, event)
        finally:
            tx.commit()


def DefaultTool():
    """
    The default tool chain build from HoverTool, ItemTool and HandleTool.
    """
    from gaphor.ui.groupingtools import GroupItemTool

    chain = TransactionalToolChain()
    chain.append(HoverTool())
    chain.append(ConnectHandleTool())
    chain.append(GroupItemTool())
    chain.append(TextEditTool())
    chain.append(RubberbandTool())
    return chain


# vim:sw=4:et:ai
