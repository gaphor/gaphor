"""The element editor is a utility window used for editing elements."""

import importlib.resources
import logging
from typing import Optional

from gi.repository import Gtk

from gaphor.abc import ActionProvider
from gaphor.core import action, event_handler, gettext
from gaphor.core.modeling import Presentation
from gaphor.core.modeling.event import AssociationUpdated
from gaphor.diagram.propertypages import PropertyPages
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramSelectionChanged

log = logging.getLogger(__name__)


def new_builder():
    builder = Gtk.Builder()
    builder.set_translation_domain("gaphor")
    with importlib.resources.path("gaphor.ui", "elementeditor.glade") as glade_file:
        builder.add_from_file(str(glade_file))
    return builder


class ElementEditor(UIComponent, ActionProvider):
    """The ElementEditor class is a utility window used to edit UML elements.
    It will display the properties of the currently selected element in the
    diagram."""

    title = gettext("Element Editor")
    size = (275, -1)

    def __init__(self, event_manager, element_factory, diagrams):
        """Constructor. Build the action group for the element editor window.
        This will place a button for opening the window in the toolbar.
        The widget attribute is a PropertyEditor."""
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.diagrams = diagrams
        self.vbox: Optional[Gtk.Box] = None
        self._current_item = None
        self._expanded_pages = {gettext("Properties"): True}

    def open(self):
        """Display the ElementEditor pane."""
        builder = new_builder()

        self.revealer = builder.get_object("elementeditor")
        self.vbox = builder.get_object("editors")

        current_view = self.diagrams.get_current_view()
        self._selection_change(focused_item=current_view and current_view.focused_item)

        # Make sure we receive
        self.event_manager.subscribe(self._selection_change)
        self.event_manager.subscribe(self._element_changed)

        self.revealer.show_all()

        return self.revealer

    @action(name="win.show-editors", shortcut="<Primary>e", state=False)
    def toggle_editor_visibility(self, active):
        self.revealer.set_reveal_child(active)

    def close(self, widget=None):
        """Hide the element editor window and deactivate the toolbar button.
        Both the widget and event parameters default to None and are
        idempotent if set."""

        self.event_manager.unsubscribe(self._selection_change)
        self.event_manager.unsubscribe(self._element_changed)
        self.vbox = None
        self._current_item = None
        return True

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
                page.show_all()
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
    def _selection_change(self, event=None, focused_item=None):
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

        if item is None:
            label = Gtk.Label()
            label.set_markup("<b>No item selected</b>")
            label.set_name("no-item-selected")
            self.vbox.pack_start(child=label, expand=False, fill=True, padding=10)
            label.show()
            return
        self.create_pages(item)

    @event_handler(AssociationUpdated)
    def _element_changed(self, event):
        if event.property is Presentation.subject:  # type: ignore[misc] # noqa: F821
            element = event.element
            if element is self._current_item:
                self.clear_pages()
                self.create_pages(self._current_item)
