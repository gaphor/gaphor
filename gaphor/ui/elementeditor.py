"""The element editor is a utility window used for editing elements."""

import importlib.resources
import logging
from typing import Iterator, Optional
from unicodedata import normalize

from babel import Locale
from gi.repository import Adw, GLib, Gtk, GtkSource

from gaphor.abc import ActionProvider
from gaphor.core import Transaction, action, event_handler
from gaphor.core.modeling import Presentation, StyleSheet
from gaphor.core.modeling.diagram import StyledItem
from gaphor.core.modeling.event import (
    AssociationUpdated,
    AttributeUpdated,
    ElementCreated,
    ModelReady,
)
from gaphor.core.styling import StyleNode
from gaphor.diagram.event import DiagramSelectionChanged
from gaphor.diagram.propertypages import PropertyPages, new_resource_builder
from gaphor.i18n import gettext, localedir
from gaphor.ui.abc import UIComponent
from gaphor.ui.csscompletion import (
    CompletionProviderWrapper,
    CssFunctionProposals,
    CssNamedColorProposals,
    CssPropertyProposals,
)
from gaphor.ui.event import ModelSelectionChanged
from gaphor.ui.modelmerge import ModelMerge

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
        self,
        event_manager,
        component_registry,
        element_factory,
        modeling_language,
        diagrams,
        properties,
    ):
        """Constructor.

        Build the action group for the element editor window. This will
        place a button for opening the window in the toolbar. The widget
        attribute is a PropertyEditor.
        """
        self.event_manager = event_manager
        self.properties = properties
        self.editors = EditorStack(
            event_manager, component_registry, diagrams, properties
        )
        self.preferences = PreferencesStack(event_manager, diagrams, element_factory)
        self.modelmerge = ModelMerge(event_manager, element_factory, modeling_language)
        self.editor_stack: Gtk.Box | None = None

    def open(self):
        """Display the ElementEditor pane."""
        builder = new_builder("elementeditor", "style-sheet-buffer")

        self.editor_stack = builder.get_object("editor-stack")

        resolve = builder.get_object("modelmerge-resolve")
        resolve.connect_after("clicked", self.on_model_ready)

        self.editors.open(builder)
        self.preferences.open(builder)
        self.modelmerge.open(builder)

        self.event_manager.subscribe(self.on_model_ready)

        self.on_model_ready(None)

        return builder.get_object("elementeditor")

    def close(self, widget=None):
        """Hide the element editor window and deactivate the toolbar button.

        Both the widget and event parameters default to None and are
        idempotent if set.
        """

        self.event_manager.unsubscribe(self.on_model_ready)

        self.editors.close()
        self.preferences.close()
        self.modelmerge.close()

        return True

    @event_handler(ModelReady)
    def on_model_ready(self, _event):
        if editor_stack := self.editor_stack:
            editor_stack.set_visible_child_name(
                "modelmerge" if self.modelmerge.needs_merge else "editors"
            )

    @action(name="show-preferences", shortcut="<Primary>semicolon", state=False)
    def toggle_editor_preferences(self, active):
        if not self.editor_stack:
            return

        if not self.editor_stack.get_mapped():
            self.editor_stack.activate_action("win.show-editors", None)
        else:
            self.editor_stack.set_visible_child_name(
                "preferences"
                if active
                else "modelmerge"
                if self.modelmerge.needs_merge
                else "editors"
            )

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
    def __init__(self, event_manager, component_registry, diagrams, properties):
        self.event_manager = event_manager
        self.component_registry = component_registry
        self.diagrams = diagrams
        self.properties = properties

        self.vbox: Optional[Gtk.Box] = None
        self._current_item = None

    def open(self, builder):
        """Display the ElementEditor pane."""
        self.vbox = builder.get_object("editors")

        current_view = self.diagrams.get_current_view()
        self._selection_changed(current_view and current_view.selection.focused_item)

        self.event_manager.subscribe(self._diagram_selection_changed)
        self.event_manager.subscribe(self._model_selection_changed)
        self.event_manager.subscribe(self._element_changed)

    def close(self):
        self.event_manager.unsubscribe(self._diagram_selection_changed)
        self.event_manager.unsubscribe(self._model_selection_changed)
        self.event_manager.unsubscribe(self._element_changed)

        self.vbox = None
        self._current_item = None

    def _get_adapters(self, item):
        """Return an ordered list of (order, name, adapter)."""
        page_map = {}
        partial = self.component_registry.partial

        if isinstance(item, Presentation) and item.subject:
            for page in PropertyPages.find(item.subject):
                page_map[(page.order, page.__name__)] = partial(page)(item.subject)

        for page in PropertyPages.find(item):
            page_map[(page.order, page.__name__)] = partial(page)(item)

        return sorted(page_map.items())

    def create_pages(self, item):
        """Load all tabs that can operate on the given item."""
        assert self.vbox
        adapters = self._get_adapters(item)

        for (_, name), adapter in adapters:
            try:
                page = adapter.construct()
                if not page:
                    continue
                self.vbox.append(page)
            except Exception:
                log.error(
                    "Could not construct property page for %s", name, exc_info=True
                )

    def clear_pages(self):
        """Remove all tabs from the notebook."""
        assert self.vbox
        while page := self.vbox.get_first_child():
            self.vbox.remove(page)

    def _selection_changed(self, item):
        """Called when a diagram item receives focus.

        This reloads all tabs based on the current selection.
        """
        assert self.vbox
        if item is self._current_item and self.vbox.get_first_child():
            return

        self._current_item = item
        self.clear_pages()

        if item:
            self.create_pages(item)
        else:
            self.show_no_item_selected()

    @event_handler(DiagramSelectionChanged)
    def _diagram_selection_changed(self, event):
        self._selection_changed(event.focused_item)

    @event_handler(ModelSelectionChanged)
    def _model_selection_changed(self, event):
        self._selection_changed(event.focused_element)

    def show_no_item_selected(self):
        assert self.vbox
        builder = new_builder("no-item-selected")

        self.vbox.append(builder.get_object("no-item-selected"))

        tips = builder.get_object("tips")

        def on_show_tips_changed(checkbox, gparam):
            active = checkbox.get_active()
            tips.set_visible(active)
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

    def __init__(self, event_manager, diagrams, element_factory):
        self.event_manager = event_manager
        self.diagrams = diagrams
        self.element_factory = element_factory
        self.lang_manager = GtkSource.LanguageManager.get_default()
        self.style_manager = Adw.StyleManager.get_default()
        self._notify_dark_id = 0
        self.lang_manager.append_search_path(
            str(importlib.resources.files("gaphor") / "ui" / "language-specs")
        )
        self._current_item = None

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
        self.css_nodes = builder.get_object("css-nodes")

        self.style_sheet_buffer.set_language(
            self.lang_manager.get_language("gaphorcss")
        )

        view_completion = self.style_sheet_view.get_completion()
        view_completion.add_provider(
            CompletionProviderWrapper(priority=3, proposals=CssFunctionProposals())
        )
        view_completion.add_provider(
            CompletionProviderWrapper(priority=-4, proposals=CssNamedColorProposals())
        )
        view_completion.add_provider(
            CompletionProviderWrapper(priority=1, proposals=CssPropertyProposals())
        )
        assert self.style_manager
        self._notify_dark_id = self.style_manager.connect(
            "notify::dark", self._on_notify_dark
        )
        self._on_notify_dark(self.style_manager, None)

        language_model = builder.get_object("language-model")
        for _code, language in self._languages:
            language_model.append(language)

        current_view = self.diagrams.get_current_view()
        self._diagram_selection_changed(
            focused_item=current_view and current_view.selection.focused_item
        )

        self.event_manager.subscribe(self._diagram_selection_changed)
        self.event_manager.subscribe(self._model_ready)
        self.event_manager.subscribe(self._style_sheet_created)
        self.event_manager.subscribe(self._style_sheet_changed)
        self.style_sheet_buffer.connect("changed", self.on_style_sheet_changed)
        self.language_dropdown.connect("notify::selected", self.on_language_changed)

        self.update()

    def close(self):
        self.event_manager.unsubscribe(self._diagram_selection_changed)
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
    def _model_ready(self, _event):
        self.update()

    @event_handler(ElementCreated)
    def _style_sheet_created(self, event: ElementCreated):
        if isinstance(event.element, StyleSheet):
            self.update()

    @event_handler(AttributeUpdated)
    def _style_sheet_changed(self, event: AttributeUpdated):
        if event.property is StyleSheet.styleSheet:
            self.update()

    @event_handler(DiagramSelectionChanged)
    def _diagram_selection_changed(self, event=None, focused_item=None):
        """Called when a diagram item receives focus.

        This rebuilds the CSS nodes view.
        """
        item = event and event.focused_item or focused_item
        if item is self._current_item:
            return

        self._current_item = item
        if not item:
            self.css_nodes.set_label(gettext("No focused item."))
        else:
            self.css_nodes.set_label(dump_css_tree(StyledItem(item)))

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


def dump_css_tree(styled_item: StyleNode) -> str:
    return "\n".join(_dump_css_tree(styled_item))


def _dump_css_tree(styled_item: StyleNode) -> Iterator[str]:
    yield styled_item.name()
    children = list(styled_item.children())
    for child in children:
        if isinstance(child, StyledItem):
            continue
        for line in _dump_css_tree(child):
            if child is children[-1]:
                if line.startswith(" "):
                    yield f"   {line}"
                else:
                    yield f" ╰╴{line}"
            elif line.startswith(" "):
                yield f" │ {line}"
            else:
                yield f" ├╴{line}"
