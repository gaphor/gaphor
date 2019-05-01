"""The element editor is a utility window used for editing elements."""

import logging

from gi.repository import Gtk
from zope.component import adapter, getAdapters
from zope.interface import implementer

from gaphor.UML import Presentation
from gaphor.UML.event import AssociationChangeEvent
from gaphor.core import _, inject, action, build_action_group
from gaphor.interfaces import IActionProvider
from gaphor.ui.interfaces import IUIComponent, IPropertyPage
from gaphor.ui.event import DiagramSelectionChange

log = logging.getLogger(__name__)


@implementer(IUIComponent, IActionProvider)
class ElementEditor(object):
    """The ElementEditor class is a utility window used to edit UML elements.
    It will display the properties of the currently selected element in the
    diagram."""

    element_factory = inject("element_factory")
    main_window = inject("main_window")
    component_registry = inject("component_registry")

    title = _("Element Editor")
    size = (275, -1)
    resizable = True
    placement = "floating"
    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="edit">
            <separator />
            <menuitem action="ElementEditor:open" />
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        """Constructor. Build the action group for the element editor window.
        This will place a button for opening the window in the toolbar.
        The widget attribute is a PropertyEditor."""

        self.action_group = build_action_group(self)
        self.window = None
        self.vbox = None
        self._current_item = None
        self._expanded_pages = {_("Properties"): True}

    @action(
        name="ElementEditor:open",
        label=_("_Editor"),
        stock_id="gtk-edit",
        accel="<Primary>e",
    )
    def open_elementeditor(self):
        """Display the element editor when the toolbar button is toggled.  If
        active, the element editor is displayed.  Otherwise, it is hidden."""

        if not self.window:
            self.open()

    def open(self):
        """Display the ElementEditor window."""
        window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        window.set_transient_for(self.main_window.window)
        window.set_title(self.title)
        vbox = Gtk.VBox()

        window.add(vbox)
        vbox.show()
        window.show()

        self.window = window
        self.vbox = vbox

        diagrams = self.main_window.get_ui_component("diagrams")
        current_view = diagrams.get_current_view()
        if current_view:
            focused_item = current_view.focused_item
            if focused_item:
                self._selection_change(focused_item=focused_item)

        # Make sure we recieve
        self.component_registry.register_handler(self._selection_change)
        self.component_registry.register_handler(self._element_changed)

        window.connect("destroy", self.close)

    def close(self, _widget=None):
        """Hide the element editor window and deactivate the toolbar button.
        Both the widget and event parameters default to None and are
        idempotent if set."""

        log.debug("ElementEditor.close")
        self.component_registry.unregister_handler(self._selection_change)
        self.component_registry.unregister_handler(self._element_changed)
        self.window = None
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
                for name, adapter in getAdapters([item.subject], IPropertyPage):
                    adaptermap[name] = (adapter.order, name, adapter)
        except AttributeError:
            pass
        for name, adapter in getAdapters([item], IPropertyPage):
            adaptermap[name] = (adapter.order, name, adapter)

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
                    expander.set_label("<b>%s</b>" % name)
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

    @adapter(DiagramSelectionChange)
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
            self.vbox.pack_start(label, expand=False, padding=10)
            label.show()
            return
        self.create_pages(item)

    @adapter(AssociationChangeEvent)
    def _element_changed(self, event):
        element = event.element
        if event.property is Presentation.subject:
            if element is self._current_item:
                self.clear_pages()
                self.create_pages(self._current_item)


# vim:sw=4:et:ai
