import logging
from typing import Optional

import gaphas.segment  # Just register the handlers in this module
from gaphas.freehand import FreeHandPainter
from gaphas.painter import (
    BoundingBoxPainter,
    FocusedItemPainter,
    HandlePainter,
    ItemPainter,
    PainterChain,
    ToolPainter,
)
from gaphas.view import GtkView
from gi.repository import Gdk, GLib, Gtk

from gaphor import UML
from gaphor.core import action, event_handler, gettext, transactional
from gaphor.diagram.support import get_diagram_item
from gaphor.services.properties import PropertyChanged
from gaphor.transaction import Transaction
from gaphor.ui.actiongroup import create_action_group
from gaphor.ui.diagramtoolbox import (
    TOOLBOX_ACTIONS,
    DiagramToolbox,
    TransactionalToolChain,
)
from gaphor.ui.event import DiagramSelectionChanged
from gaphor.UML.event import DiagramItemCreated, ElementDeleted

log = logging.getLogger(__name__)


class DiagramPage:

    VIEW_TARGET_STRING = 0
    VIEW_TARGET_ELEMENT_ID = 1
    VIEW_TARGET_TOOLBOX_ACTION = 2
    VIEW_DND_TARGETS = [
        Gtk.TargetEntry.new("gaphor/element-id", 0, VIEW_TARGET_ELEMENT_ID),
        Gtk.TargetEntry.new("gaphor/toolbox-action", 0, VIEW_TARGET_TOOLBOX_ACTION),
    ]

    def __init__(self, diagram, event_manager, element_factory, properties):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.properties = properties
        self.diagram = diagram
        self.view: Optional[GtkView] = None
        self.widget: Optional[Gtk.Widget] = None
        self.toolbox: Optional[DiagramToolbox] = None
        self.event_manager.subscribe(self._on_element_delete)
        self.event_manager.subscribe(self._on_sloppy_lines)
        self.event_manager.subscribe(self._on_diagram_item_created)

    title = property(lambda s: s.diagram and s.diagram.name or gettext("<None>"))

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
        view.connect("drag-data-received", self._on_drag_data_received)

        self.view = view

        self.toolbox = DiagramToolbox(
            self.diagram, view, self.element_factory, self.event_manager
        )

        self.widget.action_group = create_action_group(self, "diagram")

        shortcuts = self.get_toolbox_shortcuts()

        def shortcut_action(widget, event):
            action_name = shortcuts.get((event.keyval, event.state))
            if action_name:
                widget.get_toplevel().get_action_group("diagram").lookup_action(
                    "select-tool"
                ).change_state(GLib.Variant.new_string(action_name))

        self.widget.connect("key-press-event", shortcut_action)
        self._on_sloppy_lines()

        return self.widget

    def get_toolbox_shortcuts(self):
        shortcuts = {}
        # accelerator keys are lower case. Since we handle them in a key-press event
        # handler, we'll need the upper-case versions as well in case Shift is pressed.
        upper_offset = ord("A") - ord("a")
        for title, items in TOOLBOX_ACTIONS:
            for action_name, label, icon_name, shortcut in items:
                if shortcut:
                    key, mod = Gtk.accelerator_parse(shortcut)
                    shortcuts[key, mod] = action_name
                    shortcuts[key + upper_offset, mod] = action_name

        return shortcuts

    @event_handler(ElementDeleted)
    def _on_element_delete(self, event: ElementDeleted):
        if event.element is self.diagram:
            self.close()

    @event_handler(PropertyChanged)
    def _on_sloppy_lines(self, event: PropertyChanged = None):
        if not event or event.key == "diagram.sloppiness":
            self.set_drawing_style(event and event.new_value or 0.0)

    def close(self):
        """
        Tab is destroyed. Do the same thing that would
        be done if Close was pressed.
        """
        assert self.widget
        self.widget.destroy()
        self.event_manager.unsubscribe(self._on_element_delete)
        self.view = None

    @action(
        name="diagram.zoom-in", shortcut="<Primary>plus",
    )
    def zoom_in(self):
        assert self.view
        self.view.zoom(1.2)

    @action(
        name="diagram.zoom-out", shortcut="<Primary>minus",
    )
    def zoom_out(self):
        assert self.view
        self.view.zoom(1 / 1.2)

    @action(
        name="diagram.zoom-100", shortcut="<Primary>0",
    )
    def zoom_100(self):
        assert self.view
        zx = self.view.matrix[0]
        self.view.zoom(1 / zx)

    @action(
        name="diagram.select-all", shortcut="<Primary>a",
    )
    def select_all(self):
        assert self.view
        self.view.select_all()

    @action(name="diagram.unselect-all", shortcut="<Primary><Shift>a")
    def unselect_all(self):
        assert self.view
        self.view.unselect_all()

    @action(name="diagram.delete")
    @transactional
    def delete_selected_items(self):
        assert self.view
        items = self.view.selected_items
        for i in list(items):
            if isinstance(i, UML.Presentation):
                i.unlink()
            else:
                if i.canvas:
                    i.canvas.remove(i)

    @action(name="diagram.select-tool", state="toolbox-pointer")
    def select_tool(self, tool_name: str):
        tool = TransactionalToolChain(self.event_manager)
        if self.toolbox and self.view:
            tool.append(self.toolbox.get_tool(tool_name))
            self.view.tool = tool

    @event_handler(DiagramItemCreated)
    def _on_diagram_item_created(self, event):
        assert self.widget
        if self.properties("reset-tool-after-create", True):
            self.widget.action_group.actions.lookup_action("select-tool").activate(
                GLib.Variant.new_string("toolbox-pointer")
            )

    def set_drawing_style(self, sloppiness=0.0):
        """
        Set the drawing style for the diagram. 0.0 is straight,
        2.0 is very sloppy.  If the sloppiness is set to be anything
        greater than 0.0, the FreeHandPainter instances will be used
        for both the item painter and the box painter.  Otherwise, by
        default, the ItemPainter is used for the item and
        BoundingBoxPainter for the box.
        """
        assert self.view
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
        assert self.view
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
        assert self.widget
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
        dialog.set_transient_for(self.widget.get_toplevel())
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
        if (
            view.is_focus()
            and event.keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace)
            and (
                event.get_state() == 0 or event.get_state() & Gdk.ModifierType.MOD2_MASK
            )
        ):
            self.delete_selected_items()

    def _on_view_selection_changed(self, view, selection_or_focus):
        self.event_manager.handle(
            DiagramSelectionChanged(view, view.focused_item, view.selected_items)
        )

    def _on_drag_data_received(self, view, context, x, y, data, info, time):
        """
        Handle data dropped on the canvas.
        """
        assert self.toolbox
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
            element_id = data.get_data().decode()
            element = self.element_factory.lookup(element_id)
            assert element

            item_class = get_diagram_item(type(element))
            if item_class:
                tx = Transaction(self.event_manager)
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
