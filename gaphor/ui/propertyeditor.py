"""
"""


import gtk
from zope import interface, component

from interfaces import IPropertyPage, IDiagramSelectionChange


class PropertyEditor(object):
    """
    The Property Editor pane.
    """

    def __init__(self):
        super(PropertyEditor, self).__init__()
        self._current_item = None
    
    def construct(self):
        self.notebook = gtk.Notebook()
        self.notebook.set_scrollable(False)
        self.notebook.set_show_border(True)

        # Make sure we recieve 
        component.provideHandler(self._selection_change)
        
        return self.notebook

    def create_tabs_for_item(self, item):
        """
        Load all tabs that can operate on the given item.
        """
        for name, adapter in component.getAdapters([item,], IPropertyPage):
            self.notebook.prepend_page(adapter.construct(), gtk.Label(name))
        self.notebook.show_all()
        
    def clear_all_tabs(self):
        """
        Remove all tabs from the notebook.
        """
        while self.notebook.get_n_pages():
            self.notebook.remove_page(0)
        
    @component.adapter(IDiagramSelectionChange)
    def _selection_change(self, event):
        """
        Called when a diagram item receives focus.
        
        This reloads all tabs based on the current selection.
        """
        item = event.focused_item
        if item is self._current_item:
            return

        self.clear_all_tabs()
        if item is None:
            return
        self.create_tabs_for_item(item)
        self._current_item = item

        
