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
from gaphas.aspect import Connector
from gaphor.core import inject, Transaction, transactional

from gaphor.diagram.interfaces import IEditor, IConnect
from gaphor.diagram.diagramline import DiagramLine


@Connector.when_type(DiagramLine)
class DiagramItemConnector(Connector.default):
    """
    Handle Tool (acts on item handles) that uses the IConnect protocol
    to connect items to one-another.

    It also adds handles to lines when a line is grabbed on the middle of
    a line segment (points are drawn by the LineSegmentPainter).
    """
    def allow(self, sink):
        adapter = component.queryMultiAdapter((sink.item, self.item), IConnect)
        return adapter and adapter.allow(self.handle, sink.port)


    @transactional
    def connect(self, sink):
        """
        Create connection at handle level and at model level.
        """
        handle = self.handle
        item = self.item
        cinfo = item.canvas.get_connection(handle)

        try:
            callback = DisconnectHandle(self.item, self.handle)
            if cinfo and cinfo.connected is sink.item:
                # reconnect only constraint - leave model intact
                log.debug('performing reconnect constraint')
                constraint = sink.port.constraint(item.canvas, item, handle, sink.item)
                item.canvas.reconnect_item(item, handle, constraint=constraint)
            else:
                if cinfo:
                    # first disconnect but disable disconnection handle as
                    # reconnection is going to happen
                    adapter = component.queryMultiAdapter((sink.item, item), IConnect)
                    if adapter and adapter.CAN_RECONNECT:
                        cinfo.callback.disable = True
                    self.disconnect()
                # new connection
                self.connect_handle(sink, callback=callback)
                # adapter requires both ends to be connected.
                reconnect = cinfo is not None
                self.model_connect(sink, reconnect)
        except Exception, e:
            log.error('Error during connect', e)


    def model_connect(self, sink, reconnect):
        """
        Connecting requires the handles to be connected before the model
        level connection is made.

        Note that once this method is called, the glue() method has done that
        for us.
        """
        handle = self.handle
        item = self.item

        adapter = component.queryMultiAdapter((sink.item, item), IConnect)
        log.debug('Connect on model level ' + str(adapter))

        assert adapter is not None
        assert handle in adapter.line.handles()
        assert sink.port in adapter.element.ports()

        if reconnect and adapter.CAN_RECONNECT:
            log.debug('Performing reconnection')
            adapter.reconnect(handle, sink.port)
        else:
            log.debug('Performing connection')
            adapter.connect(handle, sink.port)


    @transactional
    def disconnect(self):
        super(DiagramItemConnector, self).disconnect()



class DisconnectHandle(object):
    """
    Callback for items disconnection using the adapters.

    This is an object so disconnection data can be serialized/deserialized
    using pickle.

    :Variables:
     item
        Connecting item.
     handle
        Handle of connecting item.
     disable
        If set, then disconnection is disabled.
    """
    def __init__(self, item, handle):
        self.item = item
        self.handle = handle
        self.disable = False


    def __call__(self):
        handle = self.handle
        item = self.item
        canvas = self.item.canvas
        cinfo = canvas.get_connection(handle)

        if self.disable:
            log.debug('Not disconnecting %s.%s (disabled)' % (item, handle))
        else:
            log.debug('Disconnecting %s.%s' % (item, handle))
            if cinfo:
                adapter = component.queryMultiAdapter((cinfo.connected, item), IConnect)
                adapter.disconnect(handle)



class TextEditTool(Tool):
    """
    Text edit tool. Allows for elements that can adapt to the 
    IEditable interface to be edited.
    """

    def create_edit_window(self, x, y, text, editor):
        """
        Create a popup window with some editable text.
        """
        view = self.view
        window = gtk.Window()
        window.set_property('decorated', False)
        window.set_property('skip-taskbar-hint', True)
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
                       buffer, editor)
        text_view.connect('key-press-event', self._on_key_press_event,
                          buffer, editor)
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
            log.debug('Found editor %r' % editor)
            x, y = view.get_matrix_v2i(item).transform_point(event.x, event.y)
            if editor.is_editable(x, y):
                text = editor.get_text()
                # get item at cursor
                self.create_edit_window(event.x, event.y, text, editor)
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
        assert not self._tx
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

    def handle(self, event):
        # For double click: button_press, double_click, button_release
        #print 'event', self.EVENT_HANDLERS.get(event.type)
        if self.EVENT_HANDLERS.get(event.type) in ('on_button_press',):
            assert not self._tx
            self._tx = Transaction()

        try:
            super(TransactionalToolChain, self).handle(event)
        finally:
            if self._tx and self.EVENT_HANDLERS.get(event.type) in ('on_button_release', 'on_double_click', 'on_triple_click'):
                self._tx.commit()
                self._tx = None


def DefaultTool():
    """
    The default tool chain build from HoverTool, ItemTool and HandleTool.
    """
    from gaphor.ui.groupingtools import GroupItemTool

    chain = TransactionalToolChain()
    chain.append(HoverTool())
    chain.append(ConnectHandleTool())
    chain.append(ItemTool())
    chain.append(TextEditTool())
    chain.append(RubberbandTool())
    return chain


# vim:sw=4:et:ai
