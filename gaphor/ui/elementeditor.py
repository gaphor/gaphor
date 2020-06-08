"""The element editor is a utility window used for editing elements."""

import importlib.resources
import logging
import textwrap
from typing import Optional

from gi.repository import GLib, Gtk

from gaphor.abc import ActionProvider
from gaphor.core import Transaction, action, event_handler, gettext
from gaphor.core.modeling import Presentation, StyleSheet
from gaphor.core.modeling.event import AssociationUpdated, AttributeUpdated, ModelReady
from gaphor.diagram.propertypages import PropertyPages
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramSelectionChanged

log = logging.getLogger(__name__)


def new_builder(*object_ids):
    builder = Gtk.Builder()
    builder.set_translation_domain("gaphor")
    with importlib.resources.path("gaphor.ui", "elementeditor.glade") as glade_file:
        builder.add_objects_from_file(str(glade_file), object_ids)
    return builder


DEFAULT_STYLE_SHEET = textwrap.dedent(
    """
    * {
     background-color: beige;
    }

    /****
     Here you can edit the
     style of the model.
     Gaphor supports a
     subset of CSS3.

     The following proper-
     ties are supported:

     * padding: Padding
     * min-width: Number
     * min-height: Number
     * line-width: Number
     * vertical-spacing: Number
     * border-radius: Number
     * background-color: Color
     * font-family: Text
     * font-size: Number
     * font-style: normal|italic
     * font-weight: normal|bold
     * text-decoration: none|underline
     * text-align: left|center|right
     * text-color: Color
     * color: Color
     * vertical-align: top|middle|bottom
     * dash-style: Sequence[Number]
     * highlight-color: Color

     Color can be a CSS3 color name,
     a rgb(r, g, b), rgba(r, g, b, a)
     or hex code (#ff00ff).

     Have fun!
    ****/
    """
)


class DelayedFunction:
    def __init__(self, delay, function):
        self._delay = delay
        self._function = function
        self._source_id = 0

    def __call__(self, *args):
        print("update timeout", args)
        if self._source_id:
            GLib.source_remove(self._source_id)

        def timeout_function():
            print("call timeout", args)
            self._function(*args)
            self._source_id = 0

        self._source_id = GLib.timeout_add(self._delay, timeout_function)


class ElementEditor(UIComponent, ActionProvider):
    """The ElementEditor class is a utility window used to edit UML elements.
    It will display the properties of the currently selected element in the
    diagram."""

    def __init__(self, event_manager, element_factory, diagrams, properties):
        """Constructor. Build the action group for the element editor window.
        This will place a button for opening the window in the toolbar.
        The widget attribute is a PropertyEditor."""
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.diagrams = diagrams
        self.properties = properties
        self.vbox: Optional[Gtk.Box] = None
        self._current_item = None
        self._expanded_pages = {}

        self.settings_stack = SettingsStack(event_manager, element_factory)

    def open(self):
        """Display the ElementEditor pane."""
        builder = new_builder("elementeditor", "style-sheet-buffer")

        self.revealer = builder.get_object("elementeditor")
        self.editor_stack = builder.get_object("editor-stack")

        self.vbox = builder.get_object("editors")

        current_view = self.diagrams.get_current_view()
        self._selection_changed(focused_item=current_view and current_view.focused_item)

        self.event_manager.subscribe(self._selection_changed)
        self.event_manager.subscribe(self._element_changed)

        self.settings_stack.open(builder)

        return self.revealer

    def close(self, widget=None):
        """Hide the element editor window and deactivate the toolbar button.
        Both the widget and event parameters default to None and are
        idempotent if set."""

        self.event_manager.unsubscribe(self._selection_changed)
        self.event_manager.unsubscribe(self._element_changed)

        self.vbox = None
        self._current_item = None

        self.settings_stack.close()

        return True

    @action(name="show-editors", shortcut="<Primary>e", state=True)
    def toggle_editor_visibility(self, active):
        self.revealer.set_reveal_child(active)

    @action(name="show-settings", state=False)
    def toggle_editor_settings(self, active):
        self.editor_stack.set_visible_child_name("settings" if active else "editors")

    @action(name="enable-style-sheet", state=False)
    def toggle_enable_style_sheet(self, active):
        self.settings_stack.toggle_enable_style_sheet(active)

    ## Diagram item editor

    def _get_adapters(self, item):
        """
        Return an ordered list of (order, name, adapter).
        """
        adaptermap = {}
        if isinstance(item, Presentation) and item.subject:
            for adapter in PropertyPages(item.subject):
                adaptermap[(adapter.order, adapter.__class__.__name__)] = adapter
        for adapter in PropertyPages(item):
            adaptermap[(adapter.order, adapter.__class__.__name__)] = adapter

        return sorted(adaptermap.items())

    def create_pages(self, item):
        """
        Load all tabs that can operate on the given item.
        """
        assert self.vbox
        adapters = self._get_adapters(item)

        for (_, name), adapter in adapters:
            try:
                page = adapter.construct()
                if not page:
                    continue
                elif isinstance(page, Gtk.Expander):
                    page.set_expanded(self._expanded_pages.get(name, True))
                    page.connect_after("activate", self.on_expand, name)
                self.vbox.pack_start(page, False, True, 0)
            except Exception:
                log.error(
                    "Could not construct property page for " + name, exc_info=True
                )

    def clear_pages(self):
        """
        Remove all tabs from the notebook.
        """
        assert self.vbox
        for page in self.vbox.get_children():
            page.destroy()

    def on_expand(self, widget, name):
        self._expanded_pages[name] = widget.get_expanded()

    @event_handler(DiagramSelectionChanged)
    def _selection_changed(self, event=None, focused_item=None):
        """
        Called when a diagram item receives focus.

        This reloads all tabs based on the current selection.
        """
        assert self.vbox
        item = event and event.focused_item or focused_item
        if item is self._current_item and self.vbox.get_children():
            return

        self._current_item = item
        self.clear_pages()

        if item:
            self.create_pages(item)
        else:
            builder = new_builder("no-item-selected")

            self.vbox.pack_start(
                child=builder.get_object("no-item-selected"),
                expand=False,
                fill=True,
                padding=0,
            )

            tips = builder.get_object("tips")

            def on_show_tips_changed(checkbox):
                active = checkbox.get_active()
                tips.show() if active else tips.hide()
                self.properties.set("show-tips", active)

            show_tips = builder.get_object("show-tips")
            show_tips.connect("toggled", on_show_tips_changed)
            show_tips.set_active(self.properties.get("show-tips", True))

    @event_handler(AssociationUpdated)
    def _element_changed(self, event: AssociationUpdated):
        if event.property is Presentation.subject:  # type: ignore[misc] # noqa: F821
            element = event.element
            if element is self._current_item:
                self.clear_pages()
                self.create_pages(self._current_item)


class SettingsStack:
    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory = element_factory

        self._on_style_sheet_changed_id = -1
        self._in_update = 0

        def tx_update_style_sheet(style_sheet, text):
            self._in_update = 1
            with Transaction(event_manager):
                style_sheet.styleSheet = text
            self._in_update = 0

        self._style_sheet_update = DelayedFunction(800, tx_update_style_sheet)

    def open(self, builder):
        self.enable_style_sheet = builder.get_object("enable-style-sheet")
        self.style_sheet_buffer = builder.get_object("style-sheet-buffer")
        self.style_sheet_view = builder.get_object("style-sheet-view")

        self.event_manager.subscribe(self._model_ready)
        self.event_manager.subscribe(self._style_sheet_changed)
        self._on_style_sheet_changed_id = self.style_sheet_buffer.connect(
            "changed", self.on_style_sheet_changed
        )

    def close(self):
        self.event_manager.unsubscribe(self._model_ready)
        self.event_manager.unsubscribe(self._style_sheet_changed)

    @property
    def style_sheet(self):
        style_sheets = self.element_factory.lselect(StyleSheet)
        return style_sheets[0] if style_sheets else None

    def toggle_enable_style_sheet(self, active):
        style_sheet = self.style_sheet
        if active and not style_sheet:
            with Transaction(self.event_manager):
                style_sheet = self.element_factory.create(StyleSheet)
                style_sheet.styleSheet = DEFAULT_STYLE_SHEET
        elif not active and style_sheet:
            with Transaction(self.event_manager):
                for style_sheet in self.element_factory.lselect(StyleSheet):
                    # Trigger style update on diagrams:
                    style_sheet.styleSheet = ""
                    style_sheet.unlink()

    def on_style_sheet_changed(self, buffer):
        style_sheet = self.style_sheet
        if style_sheet:
            text = buffer.get_text(
                buffer.get_start_iter(), buffer.get_end_iter(), False
            )

            self._style_sheet_update(style_sheet, text)

    @event_handler(ModelReady)
    def _model_ready(self, event):
        style_sheet = self.style_sheet

        self.enable_style_sheet.set_active(bool(style_sheet))

        self.style_sheet_buffer.handler_block(self._on_style_sheet_changed_id)
        self.style_sheet_buffer.set_text(style_sheet.styleSheet if style_sheet else "")
        self.style_sheet_buffer.handler_unblock(self._on_style_sheet_changed_id)

    @event_handler(AttributeUpdated)
    def _style_sheet_changed(self, event):
        style_sheet = self.style_sheet
        if not (style_sheet or self._in_update):
            return

        self.style_sheet_buffer.handler_block(self._on_style_sheet_changed_id)
        self.style_sheet_buffer.set_text(
            (style_sheet.styleSheet or "") if style_sheet else ""
        )
        self.style_sheet_buffer.handler_unblock(self._on_style_sheet_changed_id)
