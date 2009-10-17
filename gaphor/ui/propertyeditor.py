"""
"""


import gtk
from zope import interface, component

from gaphor.core import _
from gaphor.application import Application
from gaphor.UML.interfaces import IElementCreateEvent, IAssociationChangeEvent
from gaphor.UML import Presentation
from interfaces import IPropertyPage, IDiagramSelectionChange


class PropertyEditor(object):
    """
    The Property Editor pane.

    TODO: How to order pages?
    TODO: Save expanded pages
    """

    def __init__(self):
        super(PropertyEditor, self).__init__()
        self._current_item = None
        #self._default_tab = _('Properties')
        #self._last_tab = self._default_tab
        self._expanded_pages = { _('Properties') : True }
    
    def construct(self):
        self.vbox = gtk.VBox()
        self._selection_change()

        # Make sure we recieve 
        Application.register_handler(self._selection_change)
        Application.register_handler(self._element_changed)
        #Application.register_handler(self._new_item_on_diagram)
        
        return self.vbox

    def create_pages(self, item):
        """
        Load all tabs that can operate on the given item.
        """
        adapters = []
        for name, adapter in component.getAdapters([item,], IPropertyPage):
            adapters.append((adapter.order, name, adapter))

        adapters.sort()

        for _, name, adapter in adapters:
            try:
                page = adapter.construct()
                if page is None:
                    continue
                expander = gtk.Expander()
                expander.set_label(name)
                expander.add(page)
                expander.show_all()
                expander.set_expanded(self._expanded_pages.get(name, False))
                expander.connect_after('activate', self.on_expand, name)
                self.vbox.pack_start(expander, expand=False)
            except Exception, e:
                log.error('Could not construct property page for ' + name, e)
        
            
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
            label = gtk.Label()
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
