import gtk
from interfaces import *
from gaphor.diagram import items
from zope import component
from gaphor.UML.uml2 import LiteralSpecification

#class TestDiagramElement(object):
    #interface.implements(DiagramItem)
    
class NamedItemPropertyPage(gtk.Table):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended."""
    def __init__(self, context):
        super(NamedItemPropertyPage, self).__init__(rows=1, columns=1)

        self.context = context
        
        self.attach(gtk.Label("Name"), 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0)
        nameEntry = gtk.Entry()        
        nameEntry.set_text(context.subject.name or '')
        nameEntry.connect('changed', self.changeName)
        self.attach(nameEntry, 1, 2, 0, 1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=0)
    
    def changeName(self, entry):
        self.context.subject.name = entry.get_text()
        
component.provideAdapter(
    factory=NamedItemPropertyPage,
    adapts=[items.NamedItem],
    provides=IDetailsPage,
    name='Properties')
    
    
class PropertyPropertyPage(NamedItemPropertyPage):
    """Adapter which shows a property page for a property (attributes etc.)."""
        
        
component.provideAdapter(
    factory=PropertyPropertyPage,
    adapts=[items.AttributeItem],
    provides=IDetailsPage,
    name='Properties')


class ClassPropertyPage(NamedItemPropertyPage):
    """Adapter which shows a property page for a class view."""
    def __init__(self, context):
        super(ClassPropertyPage, self).__init__(context)
        
        # Abstract toggle
        self.attach(gtk.Label("Abstract"), 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0)
        abstractCheckButton = gtk.CheckButton()
        abstractCheckButton.set_active(context.subject.isAbstract)
        abstractCheckButton.connect('toggled', self.changeAbstract)
        self.attach(abstractCheckButton, 1, 2, 1, 2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=0)
        
        # Attributes
        attributes = gtk.ListStore(str)      
        for attr in context.subject.ownedAttribute:
            attributes.append([attr.name])
        attributesTreeView = gtk.TreeView(attributes)
        attributesTreeView.set_rules_hint(True)
        
        textRenderer = gtk.CellRendererText()
        
        attributesColumn = gtk.TreeViewColumn('Attributes', textRenderer, text=0)
        
        attributesTreeView.append_column(attributesColumn)
        self.attach(attributesTreeView, 0, 2, 2, 3, xoptions=gtk.FILL|gtk.EXPAND, yoptions=0)
        
    def changeName(self, entry):
        self.context.subject.name = entry.get_text()
        
    def changeAbstract(self, checkButton):
        self.context.subject.isAbstract=checkButton.get_active()
        
        
component.provideAdapter(
    factory=ClassPropertyPage,
    adapts=[items.ClassItem],
    provides=IDetailsPage,
    name='Properties')

class TaggedValuePage(gtk.VBox):
    """An editor for tagged values associated with elements."""
    def __init__(self, context):
        super(TaggedValuePage, self).__init__()
        self.context = context
        
        taggedValues = gtk.ListStore(str, str)
        
        
        for taggedValue in self.context.subject.taggedValue:
            tag, value = taggedValue.value.split("=")
            taggedValues.append([tag, value])
        taggedValues.append(['',''])
        
        self.taggedValues = taggedValues
        
        treeView = gtk.TreeView(taggedValues)
        treeView.set_rules_hint(True)
        
        tagTextRenderer = gtk.CellRendererText()
        tagTextRenderer.set_property('editable', True)
        tagTextRenderer.connect("edited", self.cellEdited, 0)
        
        valueTextRenderer = gtk.CellRendererText()
        valueTextRenderer.set_property('editable', True)
        valueTextRenderer.connect("edited", self.cellEdited, 1)
        
        tagColumn = gtk.TreeViewColumn('Tag', tagTextRenderer, text=0)
        treeView.append_column(tagColumn)
        valueColumn = gtk.TreeViewColumn('Value', valueTextRenderer, text=1)
        treeView.append_column(valueColumn)
        
        self.pack_start(treeView)
        
    def cellEdited(self, cellrenderertext, path, new_text, col):
        self.taggedValues[path][col]=new_text

        iter = self.taggedValues.get_iter(path)
        
        if not new_text and not self.taggedValues[path][1-col] and self.isLastRow(self.taggedValues, iter):
            self.taggedValues.remove(iter)
        
        # Create a new row to enter next value
        elif new_text and not self.isLastRow(self.taggedValues, iter):
            self.taggedValues.append(['',''])
            
        self.updateTaggedValuesInModel()
    
    def updateTaggedValuesInModel(self):
        """Write the current list out the model."""
        klass = self.context.subject
        while klass.taggedValue:
            klass.taggedValue[0].unlink()
        for tag, value in self.taggedValues:
            taggedValue = klass._factory.create(LiteralSpecification)
            taggedValue.value = "%s=%s"%(tag, value)
            klass.taggedValue.append(taggedValue)
        
    def isLastRow(self, model, iter):
        return bool(model.iter_next(iter))
        
        
        
component.provideAdapter(
    factory=TaggedValuePage,
    adapts=[items.NamedItem],
    provides=IDetailsPage,
    name='Tagged values')
    

class ObjectInspector(gtk.Notebook):
    def __init__(self):
        super(ObjectInspector, self).__init__()
        self.set_scrollable(False)
        self.set_show_border(True)
    
    def loadTabsForCurrentItem(self, item):
        """Load all tabs that can operate on the given item."""
        for name, adapter in component.getAdapters(
            [item,], IDetailsPage):
            self.prepend_page(adapter, gtk.Label(name))
        self.show_all()
        
    def clearAllTabs(self):
        """Remove all tabs from the notebook."""
        [self.remove_page(0) for i in range(self.get_n_pages())]
        
    def __call__(self, event):
        """Called when a diagram item receives focus.
        
        This reloads all tabs based on the current selection."""
        diagramItem = event.focused_item
        self.clearAllTabs()
        if diagramItem is None:
            return
        self.loadTabsForCurrentItem(diagramItem)
        
