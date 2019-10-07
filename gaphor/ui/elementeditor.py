"""The element editor is a utility window used for editing elements."""

import logging

from gi.repository import Gtk

from gaphor.UML import Presentation
from gaphor.UML.event import AssociationChangeEvent
from gaphor.core import _, primary, event_handler, action, toggle_action
from gaphor.abc import ActionProvider
from gaphor.ui.abc import UIComponent
from gaphor.diagram.propertypages import PropertyPages
from gaphor.ui.event import DiagramSelectionChange

log = logging.getLogger(__name__)


def icon_button(icon_name, action_name, tooltip_text=None):
    b = Gtk.Button()
    image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    b.add(image)
    b.set_action_name(action_name)
    if tooltip_text:
        b.set_tooltip_text(tooltip_text)
    b.show_all()
    return b


def undo_buttons():
    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    box.get_style_context().add_class("linked")
    box.pack_start(
        icon_button(
            "edit-undo-symbolic", "win.edit-undo", _("Undo") + f" ({primary()}-Z)"
        ),
        False,
        False,
        0,
    )
    box.pack_start(
        icon_button(
            "edit-redo-symbolic", "win.edit-redo", _("Redo") + f" ({primary()}-Shift-Z)"
        ),
        False,
        True,
        0,
    )
    box.show()
    return box


def zoom_buttons():
    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    box.get_style_context().add_class("linked")
    box.pack_start(
        icon_button(
            "zoom-in-symbolic",
            "win.diagram-zoom-in",
            _("Zoom in") + f" ({primary()}-+)",
        ),
        False,
        False,
        0,
    )
    box.pack_start(
        icon_button(
            "zoom-original-symbolic",
            "win.diagram-zoom-100",
            _("Zoom 100%") + f" ({primary()}-0)",
        ),
        False,
        False,
        0,
    )
    box.pack_start(
        icon_button(
            "zoom-out-symbolic",
            "win.diagram-zoom-out",
            _("Zoom out") + f" ({primary()}--)",
        ),
        False,
        False,
        0,
    )
    box.show()
    return box


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

    def open(self):
        """Display the ElementEditor pane."""

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 2)

        toolbar = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        toolbar.pack_start(undo_buttons(), False, False, 0)
        toolbar.pack_end(zoom_buttons(), False, False, 0)
        vbox.pack_start(toolbar, False, False, 0)
        toolbar.show()

        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(sep, False, False, 0)
        sep.show()

        label = Gtk.Label.new(_("Element Editor"))
        vbox.pack_start(label, False, False, 0)
        label.show()

        vbox.show()
        self.vbox = vbox

        diagrams = self.main_window.get_ui_component("diagrams")
        current_view = diagrams.get_current_view()
        self._selection_change(focused_item=current_view and current_view.focused_item)

        # Make sure we recieve
        self.event_manager.subscribe(self._selection_change)
        self.event_manager.subscribe(self._element_changed)

        revealer = Gtk.Revealer.new()
        revealer.add(vbox)
        revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        revealer.show()
        self.revealer = revealer

        return revealer

    @toggle_action(name="win.show-editors", active=False)
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
        for page in self.vbox.get_children()[3:]:
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

    @event_handler(AssociationChangeEvent)
    def _element_changed(self, event):
        element = event.element
        if event.property is Presentation.subject:  # type: ignore
            if element is self._current_item:
                self.clear_pages()
                self.create_pages(self._current_item)
