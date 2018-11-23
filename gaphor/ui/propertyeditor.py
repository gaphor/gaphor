"""
"""

import logging

from builtins import object
from gi.repository import Gtk
from zope import component

from gaphor.UML import Presentation
from gaphor.UML.interfaces import IAssociationChangeEvent
from gaphor.core import _, inject
from gaphor.ui.interfaces import IPropertyPage, IDiagramSelectionChange

log = logging.getLogger(__name__)

class PropertyEditor(object):
    """
    The Property Editor pane.

    TODO: How to order pages?
    TODO: Save expanded pages
    """

    component_registry = inject('component_registry')

    def __init__(self):
        super(PropertyEditor, self).__init__()
        self._current_item = None
        #self._default_tab = _('Properties')
        #self._last_tab = self._default_tab
        self._expanded_pages = { _('Properties') : True }

    def construct(self):
        self.vbox = Gtk.VBox()
        self._selection_change()

        # Make sure we recieve
        self.component_registry.register_handler(self._selection_change)
        self.component_registry.register_handler(self._element_changed)
        #self.component_registry.register_handler(self._new_item_on_diagram)

        return self.vbox

    def get_adapters(self, item):
        """
        Return an ordered list of (order, name, adapter).
        """
        adaptermap = {}
        try:
            if item.subject:
                for name, adapter in component.getAdapters([item.subject,], IPropertyPage):
                    adaptermap[name] = (adapter.order, name, adapter)
        except AttributeError:
            pass
        for name, adapter in component.getAdapters([item,], IPropertyPage):
            adaptermap[name] = (adapter.order, name, adapter)

        adapters = sorted(adaptermap.values())
        return adapters

    def create_pages(self, item):
        """
        Load all tabs that can operate on the given item.
        """
        adapters = self.get_adapters(item)

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
                    expander.set_label('<b>%s</b>' % name)
                    expander.add(page)
                    expander.show_all()
                    expander.set_expanded(self._expanded_pages.get(name, False))
                    expander.connect_after('activate', self.on_expand, name)
                    self.vbox.pack_start(expander, False, True, 0)
                page.show_all()
            except Exception as e:
                log.error('Could not construct property page for ' + name, exc_info=True)


    def clear_pages(self):
        """
        Remove all tabs from the notebook.
        """
        for page in self.vbox.get_children():
            page.destroy()


    def on_expand(self, widget, name):
        self._expanded_pages[name] = widget.get_expanded()


    @component.adapter(IDiagramSelectionChange)
    def _selection_change(self, event=None):
        """
        Called when a diagram item receives focus.

        This reloads all tabs based on the current selection.
        """
        item = event and event.focused_item
        if item is self._current_item:
            return

        self._current_item = item
        self.clear_pages()

        if item is None:
            label = Gtk.Label()
            label.set_markup('<b>No item selected</b>')
            self.vbox.pack_start(label, expand=False, padding=10)
            label.show()
            return
        self.create_pages(item)

    @component.adapter(IAssociationChangeEvent)
    def _element_changed(self, event):
        element = event.element
        if event.property is Presentation.subject:
            if element is self._current_item:
                self.clear_pages()
                self.create_pages(self._current_item)

    #@component.adapter(Presentation, IElementCreateEvent)
    def _new_item_on_diagram(self, item, event):
        if self.notebook.get_n_pages() > 0:
            self.select_tab(self._default_tab)
            page = self.notebook.get_nth_page(self.notebook.get_current_page())
            default = page.get_data('default')
            if default:
                default.grab_focus()


# vim:sw=4:et:ai
