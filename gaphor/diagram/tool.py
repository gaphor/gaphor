"""
Tools for handling items on the canvas.

Although Gaphas has quite a few useful tools, some tools need to be extended:
 - PlacementTool: should perform undo
 - HandleTool: shoudl support adapter based connection protocol
 - TextEditTool: should support adapter based edit protocol
"""

import gtk
from zope import component

import gaphas
from gaphas.geometry import distance_point_point
from gaphas.tool import Tool, HandleTool, ItemTool, ToolChain

from gaphor.application import Application
from gaphor.transaction import Transaction, transactional

from interfaces import IEditor, IConnect

__version__ = '$Revision$'


class ConnectHandleTool(HandleTool):
    """
    Handle Tool (acts on item handles) that uses the IConnect protocol
    to connect items to one-another.
    """

    def glue(self, view, item, handle, wx, wy):
        """
        Find the nearest item that the handle may connect to.

        This is done by iterating over all items and query for an IConnect
        adapter for (itered_item, @item). If such an adapter exists, the
        glue position is determined. The item with the glue point closest
        to the handle will be glued to.

        view: The view
        item: The item who's about to connect, owner of handle
        handle: the handle to connect
        wx, wy: handle position in world coordinates
        """
        canvas = view.canvas
        i2w = view.canvas.get_matrix_i2w
        w2i = view.canvas.get_matrix_w2i
        min_dist, dummy = view.transform_distance_c2w(10, 0)
        glue_pos_w = (0, 0)
        glue_item = None
        for i in canvas.get_all_items():
            if i is item:
                continue
            adapter = component.queryMultiAdapter((i, item), IConnect)
            if adapter:
                x, y = w2i(i).transform_point(wx, wy)
                pos = adapter.glue(handle, x, y)
                if pos:
                    d = i.point(x, y)
                    if d <= min_dist:
                        min_dist = d
                        glue_pos_w = i2w(i).transform_point(*pos)
                        glue_item = i

        dist, _ = view.transform_distance_c2w(10, 0)
        if min_dist < dist:
            x, y = w2i(item).transform_point(*glue_pos_w)
            handle.x = x
            handle.y = y

        # Return the glued item, this can be used by connect() to
        # determine which item it should connect to
        return glue_item

    def connect(self, view, item, handle, wx, wy):
        """
        Find an item near @handle that @item can connect to and connect.
        
        This is done by attempting a glue() operation. If there is something
        to glue (the handles are already positioned), the IConnect.connect
        is called for (glued_item, item).
        """
        glue_item = self.glue(view, item, handle, wx, wy)

        if glue_item:
            adapter = component.queryMultiAdapter((glue_item, item), IConnect)
            x, y = view.canvas.get_matrix_w2i(glue_item).transform_point(wx, wy)
            adapter.connect(handle, x, y)

            return True
        elif handle and handle.connected_to:
            #adapter = component.queryMultiAdapter((handle.connected_to, item), IConnect)
            #adapter.disconnect(handle)
            handle.disconnect()
        return False

    def disconnect(self, view, item, handle):
        """
        Disconnect the handle from the element by removing constraints.
        Do not yet release the connection on model level, since the handle
        may be connected to the same item on some other place.
        """
        if handle.connected_to:
            adapter = component.queryMultiAdapter((handle.connected_to, item), IConnect)
            adapter.disconnect_constraints(handle)
        

class PopupItemTool(ItemTool):
    """
    An item tool with the extended ability to display a popup menu on
    a right mouse click.
    """

    def __init__(self):
        ItemTool.__init__(self, buttons=(1, 3))

    def on_button_press(self, context, event):
        if not ItemTool.on_button_press(self, context, event):
            return False
        if event.button == 3:
            view = context.view
            item = view.focused_item
            context.ungrab()
            # Display popup menu using after-event signal
            if item:
                popup_menu = item.get_popup_menu()
                if popup_menu:
                    mainwin = Application.get_service('gui_manager').main_window
                    mainwin._construct_popup_menu(menu_def=popup_menu,
                                                  event=event)
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
        text_view = gtk.TextView()
        text_view.set_buffer(buffer)
        text_view.show()
        window.add(text_view)
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
        widget.destroy()

    def on_double_click(self, context, event):
        view = context.view
        item = view.hovered_item
        if item:
            try:
                editor = IEditor(item)
            except TypeError:
                # Could not adapt to IEditor
                return False
            x, y = view.transform_point_c2i(item, event.x, event.y)
            if editor.is_editable(x, y):
                text = editor.get_text()
                # get item at cursor
                self.create_edit_window(context.view, event.x, event.y,
                                        text, editor)
                return True

    def _on_key_press_event(self, widget, event, buffer, editor):
        #self.
        if event.keyval == gtk.keysyms.Return:
            pass
            #widget.get_toplevel().destroy()
        elif event.keyval == gtk.keysyms.Escape:
            widget.get_toplevel().destroy()

    def _on_focus_out_event(self, widget, event, buffer, editor):
        self.submit_text(widget, buffer, editor)


class PlacementTool(gaphas.tool.PlacementTool):
    """
    PlacementTool is used to place items on the canvas.
    """

    def __init__(self, item_factory, action_id, handle_index=-1):
        """
        item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        gaphas.tool.PlacementTool.__init__(self, factory=item_factory,
                                           handle_tool=ConnectHandleTool(),
                                           handle_index=handle_index)
        self.action_id = action_id
        self.is_released = False
        self._tx = None

    def on_button_press(self, context, event):
        self._tx = Transaction()
        self.is_released = False
        view = context.view
        view.unselect_all()
        if gaphas.tool.PlacementTool.on_button_press(self, context, event):
            try:
                opposite = self.new_item.opposite(self.new_item.handles()[self._handle_index])
            except (KeyError, AttributeError):
                pass
            else:
                # Connect opposite handle first, using the HandleTool's
                # mechanisms
                wx, wy = view.canvas.get_matrix_i2w(self.new_item, calculate=True).transform_point(opposite.x, opposite.y)
                item = self.handle_tool.glue(view, self.new_item, opposite, wx, wy)
                if item:
                    self.handle_tool.connect(view, self.new_item, opposite, wx, wy)
            
    def on_button_release(self, context, event):
        self.is_released = True
        try:
            if Application.get_service('properties')('reset-tool-after-create', False):
                pool = Application.get_service('action_manager')
                pool.get_action('Pointer').active = True
            return gaphas.tool.PlacementTool.on_button_release(self, context, event)
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

    def grab(self, tool):
        ToolChain.grab(self, tool)
        self._tx = Transaction()

    def ungrab(self, tool):
        ToolChain.ungrab(self, tool)
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


from gaphas.tool import ToolChain, HoverTool, ItemTool, RubberbandTool


def DefaultTool():
    """
    The default tool chain build from HoverTool, ItemTool and HandleTool.
    """
    chain = TransactionalToolChain()
    chain.append(HoverTool())
    chain.append(ConnectHandleTool())
    chain.append(PopupItemTool())
    chain.append(TextEditTool())
    chain.append(RubberbandTool())
    return chain


# vim:sw=4:et:ai
