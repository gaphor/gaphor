"""
Tools for handling items on the canvas.

Although Gaphas has quite a few useful tools, some tools need to be extended:
 - PlacementTool: should perform undo
 - HandleTool: should support adapter based connection protocol
 - TextEditTool: should support adapter based edit protocol
"""

import logging

from gaphas.aspect import Connector as ConnectorAspect
from gaphas.aspect import InMotion as InMotionAspect
from gaphas.aspect import ItemConnector
from gaphas.guide import GuidedItemInMotion
from gaphas.tool import ConnectHandleTool, HoverTool, ItemTool
from gaphas.tool import PlacementTool as _PlacementTool
from gaphas.tool import RubberbandTool, Tool, ToolChain
from gi.repository import Gdk

from gaphor.core import Transaction, transactional
from gaphor.diagram.connectors import Connector
from gaphor.diagram.event import DiagramItemPlaced
from gaphor.diagram.grouping import Group
from gaphor.diagram.inlineeditors import InlineEditor
from gaphor.diagram.presentation import ElementPresentation, Presentation

# cursor to indicate grouping
IN_CURSOR_TYPE = Gdk.CursorType.DIAMOND_CROSS

# cursor to indicate ungrouping
OUT_CURSOR_TYPE = Gdk.CursorType.CROSSHAIR

log = logging.getLogger(__name__)


@ConnectorAspect.register(Presentation)
class DiagramItemConnector(ItemConnector):
    """
    Handle Tool (acts on item handles) that uses the Connector protocol
    to connect items to one-another.

    It also adds handles to lines when a line is grabbed on the middle of
    a line segment (points are drawn by the LineSegmentPainter).
    """

    def allow(self, sink):
        adapter = Connector(sink.item, self.item)
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
                adapter = Connector(sink.item, item)
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
                adapter = Connector(sink.item, item)
                self.connect_handle(sink, callback=callback)
                adapter.connect(handle, sink.port)
        except Exception:
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
            log.debug(f"Not disconnecting {item}.{handle} (disabled)")
        else:
            log.debug(f"Disconnecting {item}.{handle}")
            if cinfo:
                adapter = Connector(cinfo.connected, item)
                adapter.disconnect(handle)


class TextEditTool(Tool):
    """
    Text edit tool. Allows for elements that can adapt to the
    IEditable interface to be edited.
    """

    def on_key_press(self, event):
        view = self.view
        item = view.hovered_item
        if (
            item
            and event.type == Gdk.EventType.KEY_PRESS
            and event.key.keyval == Gdk.KEY_F2
        ):
            return InlineEditor(item, view)
        return False

    def on_double_click(self, event):
        view = self.view
        item = view.hovered_item
        if item:
            x, y = view.get_matrix_v2i(item).transform_point(event.x, event.y)
            return InlineEditor(item, view, (x, y))
        return False


class PlacementTool(_PlacementTool):
    """
    PlacementTool is used to place items on the canvas.
    """

    def __init__(self, view, item_factory, event_manager, handle_index=-1):
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
        self.event_manager = event_manager
        self._parent = None

    @classmethod
    def new_item_factory(_class, item_class, subject_class=None, config_func=None):
        """
        ``config_func`` may be a function accepting the newly created item.
        """

        def item_factory(diagram, parent=None):
            if subject_class:
                element_factory = diagram.model
                subject = element_factory.create(subject_class)
            else:
                subject = None

            item = diagram.create(item_class, subject=subject)
            if config_func:
                config_func(item)

            adapter = Group(parent, item)
            if parent and adapter.can_contain():
                adapter.group()
                diagram.canvas.reparent(item, parent=parent)

            return item

        item_factory.item_class = item_class  # type: ignore[attr-defined] # noqa: F821
        return item_factory

    @transactional
    def create_item(self, pos):
        """
        Create an item directly.
        """
        return self._create_item(pos)

    def on_button_press(self, event):
        view = self.view
        view.unselect_all()
        if super().on_button_press(event):
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
                view.canvas.update_matrices([self.new_item])
                view.update_matrix(self.new_item)

                vpos = event.x, event.y

                item = self.handle_tool.glue(self.new_item, opposite, vpos)
                if item:
                    self.handle_tool.connect(self.new_item, opposite, vpos)
            return True
        return False

    def on_button_release(self, event):
        self.event_manager.handle(DiagramItemPlaced(self.new_item))
        return super().on_button_release(event)

    def on_motion_notify(self, event):
        """
        Change parent item to dropzone state if it can accept diagram item
        object to be created.
        """
        if self.grabbed_handle:
            return self.handle_tool.on_motion_notify(event)

        view = self.view

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

    def _create_item(self, pos):
        """
        Create diagram item and place it within parent's boundaries.
        """
        parent = self._parent
        view = self.view
        diagram = view.canvas.diagram
        try:
            item = super()._create_item(pos, diagram=diagram, parent=parent)
        finally:
            self._parent = None
            view.dropzone_item = None
            view.get_window().set_cursor(None)
        return item


@InMotionAspect.register(Presentation)
class DropZoneInMotion(GuidedItemInMotion):
    def move(self, pos):
        """
        Move the item. x and y are in view coordinates.
        """
        super().move(pos)
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
        super().stop_move()
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
                old_parent.update_shapes()
                old_parent.request_update()

            if new_parent:
                adapter = Group(new_parent, item)
                if adapter and adapter.can_contain():
                    adapter.group()

                canvas.reparent(item, new_parent)
                m = canvas.get_matrix_c2i(new_parent)
                item.matrix *= m
                new_parent.update_shapes()
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
