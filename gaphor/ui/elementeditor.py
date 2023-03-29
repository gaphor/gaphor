"""The element editor is a utility window used for editing elements."""

import importlib.resources
import logging
from typing import Optional
from unicodedata import normalize

from babel import Locale
from gi.repository import GLib, Gtk, GtkSource

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
from gaphor.i18n import localedir
from gaphor.ui.abc import UIComponent
from gaphor.ui.csscompletion import (
    CssFunctionCompletionProvider,
    CssNamedColorsCompletionProvider,
    CssPropertyCompletionProvider,
)
from gaphor.ui.event import DiagramSelectionChanged
from gaphor.ui.modelmerge import ModelMerge
from gaphor.event import ModelLoaded


log = logging.getLogger(__name__)

if Gtk.get_major_version() != 3:
    from gi.repository import Adw

    GtkSource.init()

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
            try:
                self._function(*args)
            finally:
                self._source_id = 0

        self._source_id = GLib.timeout_add(self._delay, timeout_function)


class ElementEditor(UIComponent, ActionProvider):
    """The ElementEditor class is a utility window used to edit UML elements.

    It will display the properties of the currently selected element in
    the diagram.
    """

    def __init__(
        self, event_manager, element_factory, modeling_language, diagrams, properties
    ):
        """Constructor.

        Build the action group for the element editor window. This will
        place a button for opening the window in the toolbar. The widget
        attribute is a PropertyEditor.
        """
        self.event_manager = event_manager
        self.properties = properties
        self.editors = EditorStack(event_manager, diagrams, properties)
        self.preferences = PreferencesStack(event_manager, element_factory)
        self.modelmerge = ModelMerge(event_manager, element_factory, modeling_language)

    def open(self):
        """Display the ElementEditor pane."""
        builder = new_builder("elementeditor", "style-sheet-buffer")

        self.revealer = builder.get_object("elementeditor")
        self.revealer.set_reveal_child(self.properties.get("show-editors", True))
        self.editor_stack = builder.get_object("editor-stack")

        resolve = builder.get_object("modelmerge-resolve")
        resolve.connect_after("clicked", self.on_model_loaded)

        self.editors.open(builder)
        self.preferences.open(builder)
        self.modelmerge.open(builder)

        self.event_manager.subscribe(self.on_model_loaded)

        self.on_model_loaded(None)

        return self.revealer

    def close(self, widget=None):
        """Hide the element editor window and deactivate the toolbar button.

        Both the widget and event parameters default to None and are
        idempotent if set.
        """

        self.event_manager.unsubscribe(self.on_model_loaded)

        self.editors.close()
        self.preferences.close()
        self.modelmerge.close()

        return True

    @event_handler(ModelLoaded)
    def on_model_loaded(self, event):
        self.editor_stack.set_visible_child_name(
            "modelmerge" if self.modelmerge.needs_merge else "editors"
        )

    @action(
        name="show-editors",
        shortcut="F9",
        state=lambda self: self.properties.get("show-editors", True),  # type: ignore[no-any-return]
    )
    def toggle_editor_visibility(self, active):
        self.revealer.set_reveal_child(active)
        self.properties.set("show-editors", active)

    @action(name="show-preferences", shortcut="<Primary>comma", state=False)
    def toggle_editor_preferences(self, active):
        if not self.revealer.get_child_revealed():
            self.revealer.activate_action("win.show-editors", None)

        self.editor_stack.set_visible_child_name(
            "preferences"
            if active
            else "modelmerge"
            if self.modelmerge.needs_merge
            else "editors"
        )

    @action(
        name="reset-tool-after-create",
        state=lambda self: self.properties.get("reset-tool-after-create", True),  # type: ignore[no-any-return]
    )
    def reset_tool_after_create(self, active):
        self.properties.set("reset-tool-after-create", active)

    @action(
        name="remove-unused-elements",
        state=lambda self: self.properties.get("remove-unused-elements", True),  # type: ignore[no-any-return]
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
                self.vbox.append(page)
            except Exception:
                log.error(
                    f"Could not construct property page for {name}", exc_info=True
                )

    def clear_pages(self):
        """Remove all tabs from the notebook."""
        assert self.vbox
        while page := self.vbox.get_first_child():
            self.vbox.remove(page)

    def on_expand(self, widget, name):
        self._expanded_pages[name] = widget.get_expanded()

    @event_handler(DiagramSelectionChanged)
    def _selection_changed(self, event=None, focused_item=None):
        """Called when a diagram item receives focus.

        This reloads all tabs based on the current selection.
        """
        assert self.vbox
        item = event and event.focused_item or focused_item
        if item is self._current_item and self.vbox.get_first_child():
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


class PreferencesStack:
    """Support code for the Preferences (cog) pane."""

    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.lang_manager = GtkSource.LanguageManager.get_default()
        self.style_manager = (
            None if Gtk.get_major_version() == 3 else Adw.StyleManager.get_default()
        )
        self._notify_dark_id = 0
        self.lang_manager.append_search_path(
            str(importlib.resources.files("gaphor") / "ui" / "language-specs")
        )

        def tx_update_style_sheet(style_sheet, text):
            self._in_update = 1
            with Transaction(event_manager):
                style_sheet.styleSheet = text
            self._in_update = 0

        self._style_sheet_update = DelayedFunction(800, tx_update_style_sheet)
        self._in_update = 0

        self._languages = [
            (None, "English"),
            *sorted(
                (
                    (d.name, Locale.parse(d.name).get_language_name().title())
                    for d in localedir.iterdir()
                    if d.is_dir()
                ),
                key=lambda k: normalize("NFC", k[1]).casefold(),
            ),
        ]

    def open(self, builder):
        self.language_dropdown = builder.get_object("language-dropdown")
        self.style_sheet_buffer = builder.get_object("style-sheet-buffer")
        self.style_sheet_view = builder.get_object("style-sheet-view")

        self.style_sheet_buffer.set_language(
            self.lang_manager.get_language("gaphorcss")
        )

        view_completion = self.style_sheet_view.get_completion()
        view_completion.add_provider(CssFunctionCompletionProvider())
        view_completion.add_provider(CssNamedColorsCompletionProvider())
        view_completion.add_provider(CssPropertyCompletionProvider())
        assert self.style_manager
        self._notify_dark_id = self.style_manager.connect(
            "notify::dark", self._on_notify_dark
        )
        self._on_notify_dark(self.style_manager, None)

        language_model = builder.get_object("language-model")
        for _code, language in self._languages:
            language_model.append(language)

        self.event_manager.subscribe(self._model_ready)
        self.event_manager.subscribe(self._style_sheet_created)
        self.event_manager.subscribe(self._style_sheet_changed)
        self.style_sheet_buffer.connect("changed", self.on_style_sheet_changed)
        self.language_dropdown.connect("notify::selected", self.on_language_changed)

        self.update()

    def close(self):
        self.event_manager.unsubscribe(self._model_ready)
        self.event_manager.unsubscribe(self._style_sheet_changed)
        self.event_manager.unsubscribe(self._style_sheet_created)
        if self._notify_dark_id and self.style_manager:
            self._notify_dark_id = self.style_manager.disconnect(self._notify_dark_id)

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

    def update(self):
        style_sheet = self.style_sheet
        if not style_sheet or self._in_update:
            return

        self._in_update = 1
        self.style_sheet_buffer.set_text(style_sheet.styleSheet or "")
        self.language_dropdown.set_selected(
            next(
                (
                    i
                    for i, (code, _) in enumerate(self._languages)
                    if code == style_sheet.naturalLanguage
                ),
                0,
            )
        )
        self._in_update = 0

    @event_handler(ModelReady)
    def _model_ready(self, event):
        self.update()

    @event_handler(ElementCreated)
    def _style_sheet_created(self, event):
        if isinstance(event.element, StyleSheet):
            self.update()

    @event_handler(AttributeUpdated)
    def _style_sheet_changed(self, event):
        if event.property is StyleSheet.styleSheet:
            self.update()

    def on_language_changed(self, dropdown, _gparam):
        if (style_sheet := self.style_sheet) and not self._in_update:
            with Transaction(self.event_manager):
                code, _name = self._languages[dropdown.get_selected()]
                style_sheet.naturalLanguage = code

    def _on_notify_dark(self, style_manager, _gparam):
        scheme_manager = GtkSource.StyleSchemeManager.get_default()
        scheme = scheme_manager.get_scheme(
            "Adwaita-dark" if style_manager.get_dark() else "Adwaita"
        )
        self.style_sheet_buffer.set_style_scheme(scheme)
