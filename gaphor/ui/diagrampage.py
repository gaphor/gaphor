#!/usr/bin/env python

import logging

from gaphas.freehand import FreeHandPainter
from gaphas.painter import (
    PainterChain,
    ItemPainter,
    HandlePainter,
    FocusedItemPainter,
    ToolPainter,
    BoundingBoxPainter,
)
from gaphas.view import GtkView
import gaphas.segment  # Just register the handlers in this module
from gi.repository import Gdk
from gi.repository import Gtk

from gaphor import UML
from gaphor.abc import ActionProvider
from gaphor.UML.event import ElementDeleteEvent
from gaphor.core import (
    _,
    inject,
    event_handler,
    transactional,
    action,
    build_action_group,
)
from gaphor.diagram.support import get_diagram_item
from gaphor.diagram.items import DiagramItem
from gaphor.transaction import Transaction
from gaphor.ui.diagramtoolbox import DiagramToolbox
from gaphor.ui.event import DiagramSelectionChange

log = logging.getLogger(__name__)


class DiagramPage(ActionProvider):

    event_manager = inject("event_manager")
    element_factory = inject("element_factory")
    action_manager = inject("action_manager")

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="edit">
            <placeholder name="ternary">
              <menuitem action="diagram-delete" />
              <separator />
              <menuitem action="diagram-select-all" />
              <menuitem action="diagram-unselect-all" />
              <separator />
            </placeholder>
          </menu>
          <menu action="diagram">
            <placeholder name="secondary">
              <menuitem action="diagram-zoom-in" />
              <menuitem action="diagram-zoom-out" />
              <menuitem action="diagram-zoom-100" />
              <separator />
              <menuitem action="diagram-close" />
            </placeholder>
          </menu>
        </menubar>
        <toolbar name='mainwindow-toolbar'>
          <placeholder name="left">
            <separator />
            <toolitem action="diagram-zoom-in" />
            <toolitem action="diagram-zoom-out" />
            <toolitem action="diagram-zoom-100" />
          </placeholder>
        </toolbar>
      </ui>
    """

    VIEW_TARGET_STRING = 0
    VIEW_TARGET_ELEMENT_ID = 1
    VIEW_TARGET_TOOLBOX_ACTION = 2
    VIEW_DND_TARGETS = [
        Gtk.TargetEntry.new("gaphor/element-id", 0, VIEW_TARGET_ELEMENT_ID),
        Gtk.TargetEntry.new("gaphor/toolbox-action", 0, VIEW_TARGET_TOOLBOX_ACTION),
    ]

    def __init__(self, diagram):
        self.diagram = diagram
        self.view = None
        self.widget = None
        self.action_group = build_action_group(self)
        self.toolbox = None
        self.event_manager.subscribe(self._on_element_delete)

    title = property(lambda s: s.diagram and s.diagram.name or _("<None>"))

    def get_diagram(self):
        return self.diagram

    def get_view(self):
        return self.view

    def get_canvas(self):
        return self.diagram.canvas

    def construct(self):
        """
        Create the widget.

        Returns: the newly created widget.
        """
        assert self.diagram

        view = GtkView(canvas=self.diagram.canvas)
        try:
            view.set_css_name("diagramview")
        except AttributeError:
            pass  # Gtk.Widget.set_css_name() is added in 3.20
        view.drag_dest_set(
            Gtk.DestDefaults.ALL,
            DiagramPage.VIEW_DND_TARGETS,
            Gdk.DragAction.MOVE | Gdk.DragAction.COPY | Gdk.DragAction.LINK,
        )

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.add(view)
        scrolled_window.show_all()
        self.widget = scrolled_window

        view.connect("focus-changed", self._on_view_selection_changed)
        view.connect("selection-changed", self._on_view_selection_changed)
        view.connect_after("key-press-event", self._on_key_press_event)
        # view.connect("drag-drop", self._on_drag_drop)
        view.connect("drag-data-received", self._on_drag_data_received)

        self.view = view

        self.toolbox = DiagramToolbox(self.diagram, view)

        return self.widget

    @event_handler(ElementDeleteEvent)
    def _on_element_delete(self, event):
        if event.element is self.diagram:
            self.close()

    @action(name="diagram-close", stock_id="gtk-close")
    def close(self):
        """
        Tab is destroyed. Do the same thing that would
        be done if File->Close was pressed.
        """
        self.widget.destroy()
        self.event_manager.unsubscribe(self._on_element_delete)
        self.view = None

    @action(name="diagram-zoom-in", stock_id="gtk-zoom-in")
    def zoom_in(self):
        self.view.zoom(1.2)

    @action(name="diagram-zoom-out", stock_id="gtk-zoom-out")
    def zoom_out(self):
        self.view.zoom(1 / 1.2)

    @action(name="diagram-zoom-100", stock_id="gtk-zoom-100")
    def zoom_100(self):
        zx = self.view.matrix[0]
        self.view.zoom(1 / zx)

    @action(name="diagram-select-all", label="_Select all", accel="<Primary>a")
    def select_all(self):
        self.view.select_all()

    @action(
        name="diagram-unselect-all", label="Des_elect all", accel="<Primary><Shift>a"
    )
    def unselect_all(self):
        self.view.unselect_all()

    @action(name="diagram-delete", stock_id="gtk-delete")
    @transactional
    def delete_selected_items(self):
        items = self.view.selected_items
        for i in list(items):
            if isinstance(i, DiagramItem):
                i.unlink()
            else:
                if i.canvas:
                    i.canvas.remove(i)

    def set_drawing_style(self, sloppiness=0.0):
        """Set the drawing style for the diagram. 0.0 is straight,
        2.0 is very sloppy.  If the sloppiness is set to be anything
        greater than 0.0, the FreeHandPainter instances will be used
        for both the item painter and the box painter.  Otherwise, by
        default, the ItemPainter is used for the item and
        BoundingBoxPainter for the box."""

        view = self.view

        if sloppiness:

            item_painter = FreeHandPainter(ItemPainter(), sloppiness=sloppiness)
            box_painter = FreeHandPainter(BoundingBoxPainter(), sloppiness=sloppiness)

        else:

            item_painter = ItemPainter()
            box_painter = BoundingBoxPainter()

        view.painter = (
            PainterChain()
            .append(item_painter)
            .append(HandlePainter())
            .append(FocusedItemPainter())
            .append(ToolPainter())
        )

        view.bounding_box_painter = box_painter

        view.queue_draw_refresh()

    def may_remove_from_model(self, view):
        """
        Check if there are items which will be deleted from the model
        (when their last views are deleted). If so request user
        confirmation before deletion.
        """
        items = self.view.selected_items
        last_in_model = [
            i for i in items if i.subject and len(i.subject.presentation) == 1
        ]
        log.debug("Last in model: %s" % str(last_in_model))
        if last_in_model:
            return self.confirm_deletion_of_items(last_in_model)
        return True

    def confirm_deletion_of_items(self, last_in_model):
        """
        Request user confirmation on deleting the item from the model.
        """
        s = ""
        for item in last_in_model:
            s += "%s\n" % str(item)

        dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO,
            "This will remove the following selected items from the model:\n%s\nAre you sure?"
            % s,
        )
        dialog.set_transient_for(self.get_toplevel())
        value = dialog.run()
        dialog.destroy()
        if value == Gtk.ResponseType.YES:
            return True
        return False

    def _on_key_press_event(self, view, event):
        """
        Handle the 'Delete' key. This can not be handled directly (through
        GTK's accelerators) since otherwise this key will confuse the text
        edit stuff.
        """
        if view.is_focus():
            if event.keyval == Gdk.KEY_Delete and (
                event.get_state() == 0 or event.get_state() & Gdk.ModifierType.MOD2_MASK
            ):
                self.delete_selected_items()
            elif event.keyval == Gdk.KEY_BackSpace and (
                event.get_state() == 0 or event.get_state() & Gdk.ModifierType.MOD2_MASK
            ):
                self.delete_selected_items()

    def _on_view_selection_changed(self, view, selection_or_focus):
        self.event_manager.handle(
            DiagramSelectionChange(view, view.focused_item, view.selected_items)
        )

    #    def _on_drag_drop(self, view, context, x, y, time):
    #        """The signal handler for the drag-drop signal.
    #
    #        The drag-drop signal is emitted on the drop site when the user drops
    #        the data onto the widget.
    #
    #        Args:
    #            view: The view that received the drop.
    #            context (Gdk.DragContext) - The drag context.
    #            x (int): The x coordinate of the current cursor position.
    #            y (int): The y coordinate of the current cursor position.
    #            time (int): The timestamp of the motion event.
    #
    #        Returns:
    #            bool: Whether the cursor position is in the drop zone.
    #
    #        """
    #        targets = context.list_targets()
    #        # print('drag_drop on', targets)
    #        for target in targets:
    #            name = target.name()
    #            if name == "gaphor/element-id":
    #                target = Gdk.atom_intern(name, False)
    #                view.drag_get_data(context, target, time)
    #                return True
    #            elif name == "gaphor/toolbox-action":
    #                target = Gdk.atom_intern(name, False)
    #                view.drag_get_data(context, target, time)
    #                return True
    #        return False

    def _on_drag_data_received(self, view, context, x, y, data, info, time):
        """
        Handle data dropped on the canvas.
        """
        if (
            data
            and data.get_format() == 8
            and info == DiagramPage.VIEW_TARGET_TOOLBOX_ACTION
        ):
            tool = self.toolbox.get_tool(data.get_data().decode())
            tool.create_item((x, y))
            context.finish(True, False, time)
        elif (
            data
            and data.get_format() == 8
            and info == DiagramPage.VIEW_TARGET_ELEMENT_ID
        ):
            print("drag_data_received:", data.get_data(), info)
            n, p = data.get_data().decode().split("#")
            element = self.element_factory.lookup(n)
            assert element

            # TODO: use adapters to execute code below

            q = type(element)
            if p:
                q = q, p
            item_class = get_diagram_item(q)
            if isinstance(element, UML.Diagram):
                self.action_manager.execute("OpenModelElement")
            elif item_class:
                tx = Transaction()
                item = self.diagram.create(item_class)
                assert item

                x, y = view.get_matrix_v2i(item).transform_point(x, y)
                item.matrix.translate(x, y)
                item.subject = element
                tx.commit()
                view.unselect_all()
                view.focused_item = item

            else:
                log.warning(
                    "No graphical representation for UML element %s"
                    % type(element).__name__
                )
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)


# vim: sw=4:et:ai
