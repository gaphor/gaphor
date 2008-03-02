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
    """

    def __init__(self):
        super(PropertyEditor, self).__init__()
        self._current_item = None
        self._default_tab = _('Properties')
        self._last_tab = self._default_tab
    
    def construct(self):
        self.notebook = gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_show_border(True)
        self.notebook.set_tab_pos(gtk.POS_LEFT)
        self.notebook.connect('switch-page', self._on_switch_page)
        
        # Make sure we recieve 
        Application.register_handler(self._selection_change)
        Application.register_handler(self._element_changed)
        Application.register_handler(self._new_item_on_diagram)
        
        return self.notebook

    def create_tabs_for_item(self, item):
        """
        Load all tabs that can operate on the given item.
        """
        last_tab = self._last_tab
        for name, adapter in component.getAdapters([item,], IPropertyPage):
            try:
                page = adapter.construct()
                self.notebook.prepend_page(page, gtk.Label(name))
            except Exception, e:
                log.error('Could not construct property page for ' + name, e)
        self.notebook.show_all()

        self.select_tab(last_tab)
        
            
    def select_tab(self, name):
        # Show the last selected tab again.
        for page_num in range(0, self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(page_num)
            label_text = self.notebook.get_tab_label_text(page)
            if label_text == name:
                self.notebook.set_current_page(page_num)
                self._last_tab = name
                break
        

    def clear_all_tabs(self):
        """
        Remove all tabs from the notebook.
        """
        last_tab = self._last_tab
        while self.notebook.get_n_pages():
            self.notebook.remove_page(0)
        self._last_tab = last_tab
        
    def _on_switch_page(self, notebook, page, page_num):
        page = self.notebook.get_nth_page(page_num)
        label_text = self.notebook.get_tab_label_text(page)
        self._last_tab = label_text

    @component.adapter(IDiagramSelectionChange)
    def _selection_change(self, event):
        """
        Called when a diagram item receives focus.
        
        This reloads all tabs based on the current selection.
        """
        item = event.focused_item
        if item is self._current_item:
            return

        self._current_item = item
        self.clear_all_tabs()

        if item is None:
            return
        self.create_tabs_for_item(item)

    @component.adapter(IAssociationChangeEvent)
    def _element_changed(self, event):
        element = event.element
        if event.property is Presentation.subject:
            if element is self._current_item:
                self.clear_all_tabs()
                self.create_tabs_for_item(self._current_item)

    @component.adapter(Presentation, IElementCreateEvent)
    def _new_item_on_diagram(self, item, event):
        if self.notebook.get_n_pages() > 0:
            self.select_tab(self._default_tab)
            page = self.notebook.get_nth_page(self.notebook.get_current_page())
            default = page.get_data('default')
            if default:
                default.grab_focus()
        

# vim:sw=4:et:ai
