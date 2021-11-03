"""The element editor is a utility window used for editing elements."""

import logging
from typing import Optional

from gi.repository import GLib, Gtk

from gaphor.abc import ActionProvider
from gaphor.core import Transaction, action, event_handler
from gaphor.core.modeling import Presentation, StyleSheet
from gaphor.core.modeling.event import (
    AssociationUpdated,
    AttributeUpdated,
    ElementCreated,
    ModelReady,
)
from gaphor.diagram.propertypages import PropertyPages, new_resource_builder
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramSelectionChanged

if Gtk.get_major_version() == 3:
    from gi.repository import GtkSource


log = logging.getLogger(__name__)


new_builder = new_resource_builder("gaphor.ui", "elementeditor")


class DelayedFunction:
    def __init__(self, delay, function):
        self._delay = delay
        self._function = function
        self._source_id = 0

    def __call__(self, *args):
        if self._source_id:
            GLib.source_remove(self._source_id)

        def timeout_function():
            self._function(*args)
            self._source_id = 0

        self._source_id = GLib.timeout_add(self._delay, timeout_function)


class ElementEditor(UIComponent, ActionProvider):
    """The ElementEditor class is a utility window used to edit UML elements.

    It will display the properties of the currently selected element in
    the diagram.
    """

    def __init__(self, event_manager, element_factory, diagrams, properties):
        """Constructor.

        Build the action group for the element editor window. This will
        place a button for opening the window in the toolbar. The widget
        attribute is a PropertyEditor.
        """
        self.properties = properties
        self.editors = EditorStack(event_manager, diagrams, properties)
        self.settings = SettingsStack(event_manager, element_factory)

    def open(self):
        """Display the ElementEditor pane."""
        builder = new_builder("elementeditor", "style-sheet-buffer")

        self.revealer = builder.get_object("elementeditor")
        self.revealer.set_reveal_child(self.properties.get("show-editors", True))
        self.editor_stack = builder.get_object("editor-stack")

        self.editors.open(builder)
        self.settings.open(builder)

        return self.revealer

    def close(self, widget=None):
        """Hide the element editor window and deactivate the toolbar button.

        Both the widget and event parameters default to None and are
        idempotent if set.
        """

        self.editors.close()
        self.settings.close()

        return True

    @action(
        name="show-editors",
        shortcut="<Primary>e",
        state=lambda self: self.properties.get("show-editors", True),
    )
    def toggle_editor_visibility(self, active):
        self.revealer.set_reveal_child(active)
        self.properties.set("show-editors", active)

    @action(name="show-settings", state=False)
    def toggle_editor_settings(self, active):
        self.editor_stack.set_visible_child_name("settings" if active else "editors")

    @action(
        name="reset-tool-after-create",
        state=lambda self: self.properties.get("reset-tool-after-create", True),
    )
    def reset_tool_after_create(self, active):
        self.properties.set("reset-tool-after-create", active)

    @action(
        name="remove-unused-elements",
        state=lambda self: self.properties.get("remove-unused-elements", True),
    )
    def remove_unused_elements(self, active):
        self.properties.set("remove-unused-elements", active)


class EditorStack:
    def __init__(self, event_manager, diagrams, properties):
        self.event_manager = event_manager
        self.diagrams = diagrams
        self.properties = properties

        self.vbox: Optional[Gtk.Box] = None
        self._current_item = None
        self._expanded_pages = {}

    def open(self, builder):
        """Display the ElementEditor pane."""
        self.vbox = builder.get_object("editors")

        current_view = self.diagrams.get_current_view()
        self._selection_changed(
            focused_item=current_view and current_view.selection.focused_item
        )

        self.event_manager.subscribe(self._selection_changed)
        self.event_manager.subscribe(self._element_changed)

    def close(self):
        self.event_manager.unsubscribe(self._selection_changed)
        self.event_manager.unsubscribe(self._element_changed)

        self.vbox = None
        self._current_item = None

    def _get_adapters(self, item):
        """Return an ordered list of (order, name, adapter)."""
        adaptermap = {}
        if isinstance(item, Presentation) and item.subject:
            for adapter in PropertyPages(item.subject):
                adaptermap[(adapter.order, adapter.__class__.__name__)] = adapter
        for adapter in PropertyPages(item):
            adaptermap[(adapter.order, adapter.__class__.__name__)] = adapter

        return sorted(adaptermap.items())

    def create_pages(self, item):
        """Load all tabs that can operate on the given item."""
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
                if Gtk.get_major_version() == 3:
                    self.vbox.pack_start(page, False, True, 0)
                else:
                    self.vbox.append(page)
            except Exception:
                log.error(
                    "Could not construct property page for " + name, exc_info=True
                )

    def clear_pages(self):
        """Remove all tabs from the notebook."""
        assert self.vbox
        if Gtk.get_major_version() == 3:
            for page in self.vbox.get_children():
                page.destroy()
        else:
            page = self.vbox.get_first_child()
            while page:
                self.vbox.remove(page)
                page = self.vbox.get_first_child()

    def on_expand(self, widget, name):
        self._expanded_pages[name] = widget.get_expanded()

    @event_handler(DiagramSelectionChanged)
    def _selection_changed(self, event=None, focused_item=None):
        """Called when a diagram item receives focus.

        This reloads all tabs based on the current selection.
        """
        assert self.vbox
        item = event and event.focused_item or focused_item
        children = (
            self.vbox.get_children()
            if Gtk.get_major_version() == 3
            else self.vbox.get_first_child()
        )
        if item is self._current_item and children:
            return

        self._current_item = item
        self.clear_pages()

        if item:
            self.create_pages(item)
        else:
            self.show_no_item_selected()

    def show_no_item_selected(self):
        assert self.vbox
        builder = new_builder("no-item-selected")

        if Gtk.get_major_version() == 3:
            self.vbox.pack_start(
                child=builder.get_object("no-item-selected"),
                expand=False,
                fill=True,
                padding=0,
            )
        else:
            self.vbox.append(builder.get_object("no-item-selected"))

        tips = builder.get_object("tips")

        def on_show_tips_changed(checkbox, gparam):
            active = checkbox.get_active()
            tips.show() if active else tips.hide()
            self.properties.set("show-tips", active)

        show_tips = builder.get_object("show-tips")
        show_tips.connect("notify::active", on_show_tips_changed)
        show_tips.set_active(self.properties.get("show-tips", True))
        on_show_tips_changed(show_tips, None)

    @event_handler(AssociationUpdated)
    def _element_changed(self, event: AssociationUpdated):
        if event.property is Presentation.subject:  # type: ignore[misc] # noqa: F821
            element = event.element
            if element is self._current_item:
                self.clear_pages()
                self.create_pages(self._current_item)


class SettingsStack:
    """Support code for the Settings (cog) pane."""

    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory = element_factory
        if Gtk.get_major_version() == 3:
            self.lang_manager = GtkSource.LanguageManager.get_default()

        def tx_update_style_sheet(style_sheet, text):
            self._in_update = 1
            with Transaction(event_manager):
                style_sheet.styleSheet = text
            self._in_update = 0

        self._style_sheet_update = DelayedFunction(800, tx_update_style_sheet)
        self._in_update = 0

    def open(self, builder):
        self.style_sheet_buffer = builder.get_object("style-sheet-buffer")
        self.style_sheet_view = builder.get_object("style-sheet-view")

        if Gtk.get_major_version() == 3:
            self.style_sheet_buffer.set_language(self.lang_manager.get_language("css"))

        self.event_manager.subscribe(self._model_ready)
        self.event_manager.subscribe(self._style_sheet_created)
        self.event_manager.subscribe(self._style_sheet_changed)
        self.style_sheet_buffer.connect("changed", self.on_style_sheet_changed)
        self.update_text()

    def close(self):
        self.event_manager.unsubscribe(self._model_ready)
        self.event_manager.unsubscribe(self._style_sheet_changed)
        self.event_manager.unsubscribe(self._style_sheet_created)

    @property
    def style_sheet(self):
        return next(self.element_factory.select(StyleSheet), None)

    def on_style_sheet_changed(self, buffer):
        style_sheet = self.style_sheet
        if style_sheet and not self._in_update:
            text = buffer.get_text(
                buffer.get_start_iter(), buffer.get_end_iter(), False
            )

            self._style_sheet_update(style_sheet, text)

    def update_text(self):
        style_sheet = self.style_sheet
        if not style_sheet or self._in_update:
            return

        self._in_update = 1
        self.style_sheet_buffer.set_text(style_sheet.styleSheet or "")
        self._in_update = 0

    @event_handler(ModelReady)
    def _model_ready(self, event):
        self.update_text()

    @event_handler(ElementCreated)
    def _style_sheet_created(self, event):
        if isinstance(event.element, StyleSheet):
            self.update_text()

    @event_handler(AttributeUpdated)
    def _style_sheet_changed(self, event):
        if event.property is StyleSheet.styleSheet:
            self.update_text()
