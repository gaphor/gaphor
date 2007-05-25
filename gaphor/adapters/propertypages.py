"""
Adapters for the Property Editor

# TODO: make all labels align top-left
# Add hidden columns for list stores where i can put the actual object
# being edited.

"""

import gtk
from gaphor.core import _
from gaphor.ui.interfaces import IPropertyPage
from gaphor.diagram import items
from zope import interface, component
from gaphor.UML import LiteralSpecification

class NamedItemPropertyPage(object):
    """
    An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.NamedItem)

    def __init__(self, context):
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()
        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label(_('Name'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(self.context.subject.name or '')
        entry.connect('changed', self._on_name_change)
        hbox.pack_start(entry)
        page.show_all()
        return page

    def _on_name_change(self, entry):
        self.context.subject.name = entry.get_text()
        
component.provideAdapter(NamedItemPropertyPage, name='Properties')
    
    
class ClassPropertyPage(NamedItemPropertyPage):
    """
    Adapter which shows a property page for a class view.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    def __init__(self, context):
        super(ClassPropertyPage, self).__init__(context)
        
    def construct(self):
        page = super(ClassPropertyPage, self).construct()

        # Abstract toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Abstract"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.subject.isAbstract)
        button.connect('toggled', self._on_abstract_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        # Attributes
        hbox = gtk.HBox()
        label = gtk.Label(_("Attributes"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        attributes = gtk.ListStore(str)      
        for attr in self.context.subject.ownedAttribute:
            attributes.append([attr.render()])
        attributes.append([''])
        self.attributes = attributes

        tree_view = gtk.TreeView(attributes)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 1)
        
        # TODO: Use a hidden column that refers to the model element
        # (like in namespace view)
        attributes_column = gtk.TreeViewColumn('Attributes', renderer, text=0)
        
        tree_view.append_column(attributes_column)
        #tree_view.set_headers_visible(False)
        hbox.pack_start(tree_view, expand=True)
        hbox.show_all()

        page.pack_start(hbox, expand=True)

        return page

    def _on_abstract_change(self, button):
        self.context.subject.isAbstract = button.get_active()
        
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        self.tagged_values[path][col] = new_text

        iter = self.tagged_values.get_iter(path)
        
        if not new_text and not self.tagged_values[path][1-col] and self.is_last_row(self.tagged_values, iter):
            self.tagged_values.remove(iter)
        
        # Create a new row to enter next value
        elif new_text and not self.is_last_row(self.tagged_values, iter):
            self.tagged_values.append(['',''])
            
        self.update_tagged_values_in_model()

component.provideAdapter(ClassPropertyPage, name='Properties')


class TaggedValuePage(object):
    """
    An editor for tagged values associated with elements.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.NamedItem)

    def __init__(self, context):
        super(TaggedValuePage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        tagged_values = gtk.ListStore(str, str)
        
        for tagged_value in self.context.subject.taggedValue:
            tag, value = tagged_value.value.split("=")
            tagged_values.append([tag, value])
        tagged_values.append(['',''])
        
        self.tagged_values = tagged_values
        
        tree_view = gtk.TreeView(tagged_values)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 0)
        tag_column = gtk.TreeViewColumn('Tag', renderer, text=0)
        tree_view.append_column(tag_column)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 1)
        
        value_column = gtk.TreeViewColumn('Value', renderer, text=1)
        tree_view.append_column(value_column)
        
        page.pack_start(tree_view)
        tree_view.show_all()
        return page
        
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        self.tagged_values[path][col] = new_text

        iter = self.tagged_values.get_iter(path)
        
        if not new_text and not self.tagged_values[path][1-col] and self.is_last_row(self.tagged_values, iter):
            self.tagged_values.remove(iter)
        
        # Create a new row to enter next value
        elif new_text and not self.is_last_row(self.tagged_values, iter):
            self.tagged_values.append(['',''])
            
        self.update_tagged_values_in_model()
    
    def update_tagged_values_in_model(self):
        """
        Write the current list out the model.
        """
        klass = self.context.subject
        while klass.taggedValue:
            klass.taggedValue[0].unlink()
        for tag, value in self.tagged_values:
            taggedValue = klass._factory.create(LiteralSpecification)
            taggedValue.value = "%s=%s"%(tag, value)
            klass.taggedValue.append(taggedValue)
        
    def is_last_row(self, model, iter):
        return bool(model.iter_next(iter))
        
        
        
component.provideAdapter(
    factory=TaggedValuePage,
    adapts=[items.NamedItem],
    provides=IPropertyPage,
    name='Tagged values')
    
# vim:sw=4:et:ai
