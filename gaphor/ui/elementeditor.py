"""The element editor is a utility window used for editing elements."""

import logging

from gi.repository import Gtk

from gaphor.UML import Presentation
from gaphor.UML.event import AssociationChangeEvent
from gaphor.core import _, event_handler, action
from gaphor.abc import ActionProvider
from gaphor.ui.abc import UIComponent
from gaphor.diagram.propertypages import PropertyPages
from gaphor.ui.event import DiagramSelectionChange

log = logging.getLogger(__name__)


class ElementEditor(UIComponent, ActionProvider):
    """The ElementEditor class is a utility window used to edit UML elements.
    It will display the properties of the currently selected element in the
    diagram."""

    title = _("Element Editor")
    size = (275, -1)

    def __init__(self, event_manager, element_factory, main_window):
        """Constructor. Build the action group for the element editor window.
        This will place a button for opening the window in the toolbar.
        The widget attribute is a PropertyEditor."""
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.main_window = main_window
        self.vbox = None
        self._current_item = None
        self._expanded_pages = {_("Properties"): True}

    # @action(
    #     name="ElementEditor:open",
    #     label=_("_Editor"),
    #     icon_name="dialog-information",
    #     accel="<Primary>e",
    # )
    # def open_elementeditor(self):
    #     """Display the element editor when the toolbar button is toggled.  If
    #     active, the element editor is displayed.  Otherwise, it is hidden."""

    #     if not self.window:
    #         self.open()

    def open(self):
        """Display the ElementEditor pane."""

        pane = Gtk.VBox.new(False, 0)
        header = Gtk.Button.new()
        label = Gtk.Label.new("Element Editor")
        header.add(label)
        header.connect("clicked", self._show_hide_editor)
        header.show()
        self.header = label
        pane.pack_start(header, False, False, 0)

        vbox = Gtk.VBox.new(False, 0)
        pane.pack_start(vbox, False, False, 0)

        pane.show_all()

        self.vbox = vbox

        diagrams = self.main_window.get_ui_component("diagrams")
        current_view = diagrams.get_current_view()
        if current_view:
            focused_item = current_view.focused_item
            if focused_item:
                self._selection_change(focused_item=focused_item)

        # Make sure we recieve
        self.event_manager.subscribe(self._selection_change)
        self.event_manager.subscribe(self._element_changed)

        return pane

    def _show_hide_editor(self, widget):
        if self.vbox.get_visible():
            self.vbox.set_visible(False)
            self.header.props.angle = 90
        else:
            self.vbox.set_visible(True)
            self.header.props.angle = 0

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
        try:
            if item.subject:
                for adapter in PropertyPages(item.subject):
                    adaptermap[adapter.name] = (adapter.order, adapter.name, adapter)
        except AttributeError:
            pass
        for adapter in PropertyPages(item):
            adaptermap[adapter.name] = (adapter.order, adapter.name, adapter)

        adapters = sorted(adaptermap.values())
        return adapters

    def create_pages(self, item):
        """
        Load all tabs that can operate on the given item.
        """
        adapters = self._get_adapters(item)

        first = True
        for _, name, adapter in adapters:
            try:
                page = adapter.construct()
                if page is None:
                    continue
                elif isinstance(page, Gtk.Container):
                    page.set_border_width(6)
                if first:
                    self.vbox.pack_start(page, False, True, 0)
                    first = False
                else:
                    expander = Gtk.Expander()
                    expander.set_use_markup(True)
                    expander.set_label(f"<b>{name}</b>")
                    expander.add(page)
                    expander.show_all()
                    expander.set_expanded(self._expanded_pages.get(name, True))
                    expander.connect_after("activate", self.on_expand, name)
                    self.vbox.pack_start(expander, False, True, 0)
                page.show_all()
            except Exception as e:
                log.error(
                    "Could not construct property page for " + name, exc_info=True
                )

    def clear_pages(self):
        """
        Remove all tabs from the notebook.
        """
        for page in self.vbox.get_children():
            page.destroy()

    def on_expand(self, widget, name):
        self._expanded_pages[name] = widget.get_expanded()

    @event_handler(DiagramSelectionChange)
    def _selection_change(self, event=None, focused_item=None):
        """
        Called when a diagram item receives focus.

        This reloads all tabs based on the current selection.
        """
        item = event and event.focused_item or focused_item
        if item is self._current_item:
            return

        self._current_item = item
        self.clear_pages()

        if item is None:
            label = Gtk.Label()
            label.set_markup("<b>No item selected</b>")
            self.vbox.pack_start(child=label, expand=False, fill=True, padding=10)
            label.show()
            return
        self.create_pages(item)

    @event_handler(AssociationChangeEvent)
    def _element_changed(self, event):
        element = event.element
        if event.property is Presentation.subject:  # type: ignore
            if element is self._current_item:
                self.clear_pages()
                self.create_pages(self._current_item)
