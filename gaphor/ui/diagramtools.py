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
from gaphas.tool import Tool, HandleTool, PlacementTool as _PlacementTool, \
    ToolChain, HoverTool, ItemTool, RubberbandTool, ConnectHandleTool
from gaphas.aspect import Connector, ItemConnector
from gaphor.core import inject, Transaction, transactional

from gaphor.diagram.interfaces import IEditor, IConnect
from gaphor.diagram.diagramline import DiagramLine


@Connector.when_type(DiagramLine)
class DiagramItemConnector(ItemConnector):
    """
    Handle Tool (acts on item handles) that uses the IConnect protocol
    to connect items to one-another.

    It also adds handles to lines when a line is grabbed on the middle of
    a line segment (points are drawn by the LineSegmentPainter).
    """
    reconnect = False

    def glue(self, vpos):
        """
        Determine if item and glue item can glue/connect using connection
        adapters.
        """
        sink = super(DiagramItemConnector, self).glue(vpos)
        if sink:
            adapter = component.queryMultiAdapter((sink.item, self.item), IConnect)
            if adapter and adapter.allow(self.handle, sink.port):
                return sink


    def connect(self, sink):
        """
        Create connection at handle level and at model level.
        """
        super(DiagramItemConnector, self).connect(sink)
        self.model_connect(sink)


    def model_connect(self, sink):
        """
        Connecting requires the handles to be connected before the model
        level connection is made.

        Note that once this method is called, the glue() method has done that
        for us.
        """
        handle = self.handle
        item = self.item
        cinfo = item.canvas.get_connection(handle)
        try:
            adapter = component.queryMultiAdapter((sink.item, item), IConnect)
            assert adapter is not None
            assert handle in adapter.line.handles()
            assert sink.port in adapter.element.ports()

            if self.reconnect:
                adapter.reconnect(handle, sink.port)
            else:
                adapter.connect(handle, sink.port)
        finally:
            self.reconnect = cinfo.callback.reconnect = False


    def connect_handle(self, sink, callback=None):
        callback = DisconnectHandle(self.item, self.handle)
        super(DiagramItemConnector, self).connect_handle(sink, callback)


class DisconnectHandle(object):
    """
    Callback for items disconnection using the adapters.

    :Variables:
     item
        Connecting item.
     handle
        Handle of connecting item.
     reconnect
        Reconnection indicator.
    """
    def __init__(self, item, handle):
        self.item = item
        self.handle = handle
        self.reconnect = None


    def __call__(self):
        handle = self.handle
        item = self.item
        canvas = self.item.canvas
        cinfo = canvas.get_connection(handle)

        if cinfo and not self.reconnect:
            adapter = component.queryMultiAdapter((cinfo.connected, item), IConnect)
            adapter.disconnect(handle)



class TextEditTool(Tool):
    """
    Text edit tool. Allows for elements that can adapt to the 
    IEditable interface to be edited.
    """

    def create_edit_window(self, x, y, text, *args):
        """
        Create a popup window with some editable text.
        """
        view = self.view
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

    def on_double_click(self, event):
        view = self.view
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
                self.create_edit_window(event.x, event.y,
                                        text, editor)
                return True

    def _on_key_press_event(self, widget, event, buffer, editor):
        if event.keyval == gtk.keysyms.Return and \
                not event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK):
            self.submit_text(widget, buffer, editor)
        elif event.keyval == gtk.keysyms.Escape:
            widget.get_toplevel().destroy()

    def _on_focus_out_event(self, widget, event, buffer, editor):
        self.submit_text(widget, buffer, editor)


class PlacementTool(_PlacementTool):
    """
    PlacementTool is used to place items on the canvas.
    """

    def __init__(self, view, item_factory, after_handler=None, handle_index=-1):
        """
        item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        _PlacementTool.__init__(self, view, factory=item_factory,
                                      handle_tool=ConnectHandleTool(),
                                      handle_index=handle_index)
        self.after_handler = after_handler
        self._tx = None

    @transactional
    def create_item(self, pos):
        return self._create_item(pos)

    def on_button_press(self, event):
        self._tx = Transaction()
        view = self.view
        view.unselect_all()
        if _PlacementTool.on_button_press(self, event):
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

                vpos = event.x, event.y

                item = self.handle_tool.glue(self.new_item, opposite, vpos)
                if item:
                    self.handle_tool.connect(self.new_item, opposite, vpos)
            return True
        return False
            
    def on_button_release(self, event):
        try:
            if self.after_handler:
                self.after_handler(self.new_item)
            return _PlacementTool.on_button_release(self, event)
        finally:
            self._tx.commit()
            self._tx = None



class TransactionalToolChain(ToolChain):
    """
    In addition to a normal toolchain, this chain begins an undo-transaction
    at button-press and commits the transaction at button-release.
    """

    def __init__(self, view=None):
        super(TransactionalToolChain, self).__init__(view)
        self._tx = None

    def on_button_press(self, event):
        self._tx = Transaction()
        return ToolChain.on_button_press(self, event)

    def on_button_release(self, event):
        try:
            return ToolChain.on_button_release(self, event)
        finally:
            if self._tx:
                self._tx.commit()
                self._tx = None

    def on_double_click(self, event):
        tx = Transaction()
        try:
            return ToolChain.on_double_click(self, event)
        finally:
            tx.commit()

    def on_triple_click(self, event):
        tx = Transaction()
        try:
            return ToolChain.on_triple_click(self, event)
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
