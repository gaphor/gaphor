"""
Tools for handling items on the canvas.

Although Gaphas has quite a few useful tools, some tools need to be extended:
 - PlacementTool: should perform undo
 - HandleTool: should support adapter based connection protocol
 - TextEditTool: should support adapter based edit protocol
"""

import logging

from gaphas.aspect import Connector, InMotion, ItemConnector
from gaphas.guide import GuidedItemInMotion
from gaphas.tool import (
    Tool,
    PlacementTool as _PlacementTool,
    ToolChain,
    HoverTool,
    ItemTool,
    RubberbandTool,
    ConnectHandleTool,
)
from gi.repository import Gdk
from gi.repository import Gtk

from gaphor.UML.presentation import LinePresentation
from gaphor.core import Transaction, transactional
from gaphor.diagram.diagramline import DiagramLine
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.grouping import Group
from gaphor.diagram.editors import Editor
from gaphor.diagram.connectors import IConnect

# cursor to indicate grouping
IN_CURSOR_TYPE = Gdk.CursorType.DIAMOND_CROSS

# cursor to indicate ungrouping
OUT_CURSOR_TYPE = Gdk.CursorType.CROSSHAIR

log = logging.getLogger(__name__)


@Connector.register(DiagramLine)
@Connector.register(LinePresentation)
class DiagramItemConnector(ItemConnector):
    """
    Handle Tool (acts on item handles) that uses the IConnect protocol
    to connect items to one-another.

    It also adds handles to lines when a line is grabbed on the middle of
    a line segment (points are drawn by the LineSegmentPainter).
    """

    def allow(self, sink):
        adapter = IConnect(sink.item, self.item)
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
                log.debug("performing reconnect constraint")
                constraint = sink.port.constraint(item.canvas, item, handle, sink.item)
                item.canvas.reconnect_item(item, handle, constraint=constraint)
            elif cinfo:
                # first disconnect but disable disconnection handle as
                # reconnection is going to happen
                adapter = IConnect(sink.item, item)
                try:
                    connect = adapter.reconnect
                except AttributeError:
                    connect = adapter.connect
                else:
                    cinfo.callback.disable = True
                self.disconnect()

                # new connection
                self.connect_handle(sink, callback=callback)

                # adapter requires both ends to be connected.
                connect(handle, sink.port)
            else:
                # new connection
                adapter = IConnect(sink.item, item)
                self.connect_handle(sink, callback=callback)
                adapter.connect(handle, sink.port)
        except Exception as e:
            log.error("Error during connect", exc_info=True)

    @transactional
    def disconnect(self):
        super().disconnect()


class DisconnectHandle:
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
            log.debug("Not disconnecting %s.%s (disabled)" % (item, handle))
        else:
            log.debug("Disconnecting %s.%s" % (item, handle))
            if cinfo:
                adapter = IConnect(cinfo.connected, item)
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
        window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        window.set_property("decorated", False)
        window.set_property("skip-taskbar-hint", True)
        window.set_modal(True)
        window.set_transient_for(view.get_toplevel())
        buffer = Gtk.TextBuffer()
        if text:
            buffer.set_text(text)
            startiter, enditer = buffer.get_bounds()
            buffer.move_mark_by_name("selection_bound", startiter)
            buffer.move_mark_by_name("insert", enditer)
        text_view = Gtk.TextView()
        text_view.set_buffer(buffer)
        text_view.set_left_margin(2)
        text_view.set_right_margin(2)

        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)
        frame.add(text_view)

        window.add(frame)
        r = Gdk.Rectangle()
        r.x = 0
        r.y = 0
        r.width = 70
        r.height = 50
        window.size_allocate(r)
        window.move(int(x), int(y))

        def on_button_press(widget, event):
            if event.window == view.get_window():
                self.submit_text(widget, buffer, editor)

        def on_key_press_event(widget, event):
            if event.keyval == Gdk.KEY_Return and not event.get_state() & (
                Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
            ):
                self.submit_text(widget, buffer, editor)
            elif event.keyval == Gdk.KEY_Escape:
                widget.get_toplevel().destroy()

        def on_focus_out_event(widget, event):
            print("Focus out event emitted")
            self.submit_text(widget, buffer, editor)

        window.add_events(Gdk.EventMask.FOCUS_CHANGE_MASK)
        window.connect("focus-out-event", on_focus_out_event)
        window.connect("button-press-event", on_button_press)
        text_view.connect("key-press-event", on_key_press_event)
        window.show_all()

    @transactional
    def submit_text(self, widget, buffer, editor):
        """
        Submit the final text to the edited item.
        """
        text = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), include_hidden_chars=True
        )
        editor.update_text(text)
        widget.get_toplevel().destroy()

    def on_double_click(self, event):
        view = self.view
        item = view.hovered_item
        if item:
            editor = Editor(item)
            if not editor:
                return False

            log.debug("Found editor %r" % editor)
            x, y = view.get_matrix_v2i(item).transform_point(event.x, event.y)
            if editor.is_editable(x, y):
                text = editor.get_text()
                root_coords = event.get_root_coords()
                self.create_edit_window(
                    root_coords.x_root, root_coords.y_root, text, editor
                )
                return True


class PlacementTool(_PlacementTool):
    """
    PlacementTool is used to place items on the canvas.
    """

    def __init__(self, view, item_factory, after_handler=None, handle_index=-1):
        """
        item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        _PlacementTool.__init__(
            self,
            view,
            factory=item_factory,
            handle_tool=ConnectHandleTool(),
            handle_index=handle_index,
        )
        self.after_handler = after_handler

    @transactional
    def create_item(self, pos):
        return self._create_item(pos)

    def on_button_press(self, event):
        view = self.view
        view.unselect_all()
        if _PlacementTool.on_button_press(self, event):
            try:
                opposite = self.new_item.opposite(
                    self.new_item.handles()[self._handle_index]
                )
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
        if self.after_handler:
            self.after_handler(self.new_item)
        return _PlacementTool.on_button_release(self, event)


class GroupPlacementTool(PlacementTool):
    """
    Try to group items when placing them on diagram.
    """

    def __init__(self, view, item_factory, after_handler=None, handle_index=-1):
        super(GroupPlacementTool, self).__init__(
            view, item_factory, after_handler, handle_index
        )
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
            adapter = Group(parent, self._factory.item_class())
            if adapter and adapter.can_contain():
                view.dropzone_item = parent
                cursor = Gdk.Cursor.new_for_display(
                    view.get_window().get_display(), IN_CURSOR_TYPE
                )
                view.get_window().set_cursor(cursor)
                self._parent = parent
            else:
                view.dropzone_item = None
                view.get_window().set_cursor(None)
                self._parent = None
            parent.request_update(matrix=False)
        else:
            if view.dropzone_item:
                view.dropzone_item.request_update(matrix=False)
            view.dropzone_item = None
            view.get_window().set_cursor(None)

    def _create_item(self, pos, **kw):
        """
        Create diagram item and place it within parent's boundaries.
        """
        parent = self._parent
        view = self.view
        try:
            adapter = Group(parent, self._factory.item_class())
            if parent and adapter and adapter.can_contain():
                kw["parent"] = parent

            item = super(GroupPlacementTool, self)._create_item(pos, **kw)

            adapter = Group(parent, item)
            if parent and item and adapter:
                adapter.group()

                canvas = view.canvas
                parent.request_update(matrix=False)
        finally:
            self._parent = None
            view.dropzone_item = None
            view.get_window().set_cursor(None)
        return item


@InMotion.register(ElementItem)
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
            view.get_window().set_cursor(None)
            return

        if current_parent and not over_item:
            # are we going to remove from parent?
            group = Group(current_parent, item)
            if group:
                cursor = Gdk.Cursor.new_for_display(
                    view.get_window().get_display(), OUT_CURSOR_TYPE
                )
                view.get_window().set_cursor(cursor)
                view.dropzone_item = current_parent
                current_parent.request_update(matrix=False)

        if over_item:
            # are we going to add to parent?
            group = Group(over_item, item)
            if group and group.can_contain():
                cursor = Gdk.Cursor.new_for_display(
                    view.get_window().get_display(), IN_CURSOR_TYPE
                )
                view.get_window().set_cursor(cursor)
                view.dropzone_item = over_item
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
                adapter = Group(old_parent, item)
                if adapter:
                    adapter.ungroup()

                canvas.reparent(item, None)
                m = canvas.get_matrix_i2c(old_parent)
                item.matrix *= m
                old_parent.request_update()

            if new_parent:
                adapter = Group(new_parent, item)
                if adapter and adapter.can_contain():
                    adapter.group()

                canvas.reparent(item, new_parent)
                m = canvas.get_matrix_c2i(new_parent)
                item.matrix *= m
                new_parent.request_update()
        finally:
            view.dropzone_item = None
            view.get_window().set_cursor(None)


class TransactionalToolChain(ToolChain):
    """
    In addition to a normal toolchain, this chain begins an undo-transaction
    at button-press and commits the transaction at button-release.
    """

    def __init__(self, event_manager, view=None):
        super().__init__(view)
        self.event_manager = event_manager
        self._tx = None

    def handle(self, event):
        # For double click: button_press, double_click, button_release
        # print 'event', self.EVENT_HANDLERS.get(event.type)
        if self.EVENT_HANDLERS.get(event.type) in ("on_button_press",):
            assert not self._tx
            self._tx = Transaction(self.event_manager)

        try:
            return super().handle(event)
        finally:
            if self._tx and self.EVENT_HANDLERS.get(event.type) in (
                "on_button_release",
                "on_double_click",
                "on_triple_click",
            ):
                self._tx.commit()
                self._tx = None


def DefaultTool(event_manager):
    """
    The default tool chain build from HoverTool, ItemTool and HandleTool.
    """
    chain = TransactionalToolChain(event_manager)
    chain.append(HoverTool())
    chain.append(ConnectHandleTool())
    chain.append(ItemTool())
    chain.append(TextEditTool())
    chain.append(RubberbandTool())
    return chain


# vim:sw=4:et:ai
