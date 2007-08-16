"""
Adapters for the Property Editor

# TODO: make all labels align top-left
# Add hidden columns for list stores where i can put the actual object
# being edited.

TODO:
 - stereotypes
 - association / association ends.
 - Follow HIG guidelines:
   * Leave a 12-pixel border between the edge of the window and
     the nearest controls.
   * Leave a 12-pixel horizontal gap between a control and its label. (The gap
     may be bigger for other controls in the same group, due to differences in
     the lengths of the labels.)
   * Labels must be concise and make sense when taken out of context.
     Otherwise, users relying on screenreaders or similar assistive
     technologies will not always be able to immediately understand the
     relationship between a control and those surrounding it.
   * Assign access keys to all editable controls. Ensure that using the access
     key focuses its associated control.
 
"""

import gtk
from gaphor.core import _, inject, transactional
from gaphor.application import Application
from gaphor.ui.interfaces import IPropertyPage
from gaphor.diagram import items
from zope import interface, component
from gaphor import UML
from gaphor.UML.interfaces import IAttributeChangeEvent
from gaphor.UML.umllex import parse_attribute, render_attribute
import gaphas.item

tree_tooltip = """\
Press ENTER to edit item, backspace/DEL to remove item.
Use -/= to move up or move down.\
"""

class UMLCollection(gtk.ListStore):
    """
    UML association GTK model. 
    """
    def __init__(self, subject, attr, filter=None):
        """
        Create GTK model from UML association.

        Parameters:

            data: iterator of UML properties
        """
        super(UMLCollection, self).__init__(str, object)
        self._subject = subject
        self._attr = attr
        if filter is None:
            filter = lambda i: True
        for item in self._collection():
            if filter(item):
                self.append([item.render(), item])
        self.append(['', None])


    def _collection(self):
        return getattr(self._subject, self._attr)


    def swap(self, a, b):
        """
        Swap two items.
        """
        if not a or not b:
            return
        item1 = self[a][1]
        item2 = self[b][1]
        if self._collection().swap(item1, item2):
            super(UMLCollection, self).swap(a, b)


    def iter_prev(self, iter):
        """
        Get previous GTK tree iterator.
        """
        i = self.get_path(iter)[0]
        if i == 0:
            return None
        return self.get_iter((i - 1,))


    def remove(self, iter):
        """
        Remove item from GTK model and destroy it.
        """
        item = self[iter][1]
        if item:
            item.unlink()
            super(UMLCollection, self).remove(iter)



def remove_on_keypress(tree, event):
    """
    Remove selected items from GTK model on ``backspace`` keypress.
    """
    k = gtk.gdk.keyval_name(event.keyval).lower()
    if k == 'backspace' or k == 'kp_delete':
        model, iter = tree.get_selection().get_selected()
        if iter:
            model.remove(iter)


def swap_on_keypress(tree, event):
    """
    Swap selected and previous (or next) items.
    """
    k = gtk.gdk.keyval_name(event.keyval).lower()
    if k == 'equal' or k == 'kp_add':
        model, iter = tree.get_selection().get_selected()
        model.swap(iter, model.iter_next(iter))
        return True
    elif k == 'minus':
        model, iter = tree.get_selection().get_selected()
        model.swap(iter, model.iter_prev(iter))
        return True


class UMLComboModel(gtk.ListStore):
    """
    UML combo box model.

    Model allows to easily create a combo box with values and their labels,
    for example

        label1  ->  value1
        label2  ->  value2
        label3  ->  value3

    Labels are displayed by combo box and programmer has easy access to
    values associated with given label.

    Attributes:

    - _data: model data
    - _indices: dictionary of values' indices
    """
    def __init__(self, data):
        super(UMLComboModel, self).__init__(str)

        self._indices = {}
        self._data = data

        # add labels to underlying model and store index information
        for i, (label, value) in enumerate(data):
            self.append([label])
            self._indices[value] = i

        
    def get_index(self, value):
        """
        Return index of a ``value``.
        """
        return self._indices[value]


    def get_value(self, index):
        """
        Get value for given ``index``.
        """
        return self._data[index][1]



def create_uml_combo(data, callback):
    """
    Create a combo box using ``UMLComboModel`` model.

    Combo box is returned.
    """
    model = UMLComboModel(data)
    combo = gtk.ComboBox(model)
    cell = gtk.CellRendererText()
    combo.pack_start(cell, True)
    combo.add_attribute(cell, 'text', 0)
    combo.connect('changed', callback)
    return combo
        

@transactional
def on_cell_edited(cellrenderertext, path, new_text, page, cls, attr):
    """
    Update the model and UML element based on fresh user input.
    """
    model = page.model
    item = model[path]
    iter = model.get_iter(path)

    # Delete item if text is empty
    if not new_text:
        model.remove(iter)
        return

    # Add a new item
    if new_text and not item[1]:
        a = page.element_factory.create(cls)
        setattr(page.context.subject, attr, a)
        item[1] = a
        model.append(['', None])

    # Apply new_text to an item
    if item[1]:
        item[1].parse(new_text)
        item[0] = item[1].render()


def watch_attribute(attribute, widget, handler):
    """
    Watch attribute ``attribute`` for changes. If it changes
    ``handler(event)`` is called. When ``widget`` is destroyed, the
    handler is unregistered.
    If ``attribute`` is None, all attribute events are propagated to teh handler.
    """
    @component.adapter(IAttributeChangeEvent)
    def attribute_watcher(event):
        if attribute is None or event.property is attribute:
            handler(event)

    Application.register_handler(attribute_watcher)

    def destroy_handler(_widget):
        Application.unregister_handler(attribute_watcher)
    widget.connect('destroy', destroy_handler)



def create_hbox_label(adapter, page, label):
    """
    Create a HBox with a label for given property page adapter and page
    itself.
    """
    hbox = gtk.HBox()
    label = gtk.Label(label)
    label.set_justify(gtk.JUSTIFY_LEFT)
    adapter.size_group.add_widget(label)
    hbox.pack_start(label, expand=False)
    page.pack_start(hbox, expand=False)
    return hbox



class CommentItemPropertyPage(object):
    """
    Property page for Comments
    """
    interface.implements(IPropertyPage)
    component.adapts(items.CommentItem)

    def __init__(self, context):
        self.context = context

    def construct(self):
        subject = self.context.subject
        page = gtk.VBox()

        label = gtk.Label(_('Comment'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        page.pack_start(label, expand=False)

        buffer = gtk.TextBuffer()
        if subject.body:
            buffer.set_text(subject.body)
        text_view = gtk.TextView()
        text_view.set_buffer(buffer)
        text_view.show()
        page.pack_start(text_view)

        changed_id = buffer.connect('changed', self._on_body_change)

        def handler(event):
            if event.element is subject and event.new_value is not None:
                buffer.handler_block(changed_id)
                buffer.set_text(event.new_value)
                buffer.handler_unblock(changed_id)
        watch_attribute(type(subject).body, text_view, handler)

        page.show_all()
        return page

    @transactional
    def _on_body_change(self, buffer):
        self.context.subject.body = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        
component.provideAdapter(CommentItemPropertyPage, name='Properties')


class NamedItemPropertyPage(object):
    """
    An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    interface.implements(IPropertyPage)

    def __init__(self, context):
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    
    def construct(self):
        page = gtk.VBox()
        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        subject = self.context.subject
        if not subject:
            return page

        label = gtk.Label(_('Name'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(subject and subject.name or '')

        # monitor subject.name attribute
        changed_id = entry.connect('changed', self._on_name_change)

        def handler(event):
            if event.element is subject and event.new_value is not None:
                entry.handler_block(changed_id)
                entry.set_text(event.new_value)
                entry.handler_unblock(changed_id)
        watch_attribute(type(subject).name, entry, handler)

        hbox.pack_start(entry)
        page.show_all()
        return page

    @transactional
    def _on_name_change(self, entry):
        self.context.subject.name = entry.get_text()
        
component.provideAdapter(NamedItemPropertyPage,
                         adapts=[items.NamedItem], name='Properties')
component.provideAdapter(NamedItemPropertyPage,
                         adapts=[items.NamedLine], name='Properties')


class StereotypePage(object):

    interface.implements(IPropertyPage)

    element_factory = inject('element_factory')

    def __init__(self, context):
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()
        for i, stereotype in enumerate(self.get_stereotypes()):
            if (i % 3) == 0:
                hbox = gtk.HBox()
                page.pack_start(hbox, expand=False)
            button = gtk.CheckButton()
            button.set_active(stereotype in self.context.subject.appliedStereotype)
            button.connect('toggled', self._on_stereotype_selected, stereotype)
            hbox.pack_start(button, expand=False)
            label = gtk.Label(stereotype.name)
            label.set_justify(gtk.JUSTIFY_LEFT)
            self.size_group.add_widget(label)
            hbox.pack_start(label)
        page.show_all()
        return page

    def get_stereotypes(self):
        stereotype_list = []
        subject = self.context.subject

        # UML specs does not allow to extend stereotypes with stereotypes
        if subject and not isinstance(subject, UML.Stereotype):
            cls = type(subject)

            # find out names of classes, which are superclasses of our subject
            names = set(c.__name__ for c in cls.__mro__ if issubclass(c, UML.Element))

            # find stereotypes that extend out metaclass
            classes = self.element_factory.select(lambda e: e.isKindOf(UML.Class) and e.name in names)

            for class_ in classes:
                for extension in class_.extension:
                    yield extension.ownedEnd.type

    @transactional
    def _on_stereotype_selected(self, button, stereotype):
        subject = self.context.subject
        if button.get_active():
            subject.appliedStereotype = stereotype
        else:
            del subject.appliedStereotype[stereotype]
        
component.provideAdapter(StereotypePage,
                         adapts=[items.ElementItem], name='Stereotypes')
component.provideAdapter(StereotypePage,
                         adapts=[items.LineItem], name='Stereotypes')
    

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

        hbox.show_all()

        return page

    @transactional
    def _on_abstract_change(self, button):
        self.context.subject.isAbstract = button.get_active()

component.provideAdapter(ClassPropertyPage, name='Properties')


class InterfacePropertyPage(NamedItemPropertyPage):
    """
    Adapter which shows a property page for an interface view.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.InterfaceItem)

    def __init__(self, context):
        super(InterfacePropertyPage, self).__init__(context)
        
    def construct(self):
        page = super(InterfacePropertyPage, self).construct()

        # Fold toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Fold"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.folded)
        button.connect('toggled', self._on_fold_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        hbox.show_all()

        return page

    @transactional
    def _on_fold_change(self, button):
        self.context.folded = button.get_active()

component.provideAdapter(InterfacePropertyPage, name='Properties')


class AttributesPage(object):
    """
    An editor for attributes associated with classes and interfaces

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    element_factory = inject('element_factory')

    def __init__(self, context):
        super(AttributesPage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        # Show attributes toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Show attributes"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.show_attributes)
        button.connect('toggled', self._on_show_attributes_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        # Attributes list store:
        attrs = self.context.subject.ownedAttribute
        attributes = UMLCollection(self.context.subject, 'ownedAttribute', filter=lambda i: not i.association)

        self.model = attributes
        
        tree_view = gtk.TreeView(attributes)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect('edited', on_cell_edited,
                self, UML.Property, 'ownedAttribute')
        tag_column = gtk.TreeViewColumn('Attributes', renderer, text=0)
        tree_view.append_column(tag_column)

        tooltips = gtk.Tooltips()
        tooltips.set_tip(tree_view, tree_tooltip)

        tree_view.connect('key_press_event', remove_on_keypress)
        tree_view.connect('key_press_event', swap_on_keypress)
        
        page.pack_start(tree_view)
        tree_view.show_all()

        return page
        
    @transactional
    def _on_show_attributes_change(self, button):
        self.context.show_attributes = button.get_active()
        self.context.request_update()
        

component.provideAdapter(AttributesPage, name='Attributes')


class OperationsPage(object):
    """
    An editor for operations associated with classes and interfaces

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    element_factory = inject('element_factory')

    def __init__(self, context):
        super(OperationsPage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        # Show operations toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Show operations"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.show_operations)
        button.connect('toggled', self._on_show_operations_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        # Operations list store:
        operations = UMLCollection(self.context.subject, 'ownedOperation')
        self.model = operations
        
        tree_view = gtk.TreeView(operations)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect('edited', on_cell_edited,
                self, UML.Operation, 'ownedOperation')
        tag_column = gtk.TreeViewColumn('Operation', renderer, text=0)
        tree_view.append_column(tag_column)

        tooltips = gtk.Tooltips()
        tooltips.set_tip(tree_view, tree_tooltip)

        tree_view.connect('key_press_event', remove_on_keypress)
        tree_view.connect('key_press_event', swap_on_keypress)
        
        page.pack_start(tree_view)
        tree_view.show_all()

        return page
        
    @transactional
    def _on_show_operations_change(self, button):
        self.context.show_operations = button.get_active()
        self.context.request_update()


component.provideAdapter(OperationsPage, name='Operations')


class TaggedValuePage(object):
    """
    An editor for tagged values associated with elements.

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.NamedItem)

    element_factory = inject('element_factory')
    def __init__(self, context):
        super(TaggedValuePage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        tagged_values = gtk.ListStore(str, str, object)

        if self.context.subject is None:
            return page
        
        for tagged_value in self.context.subject.taggedValue:
            tag, value = tagged_value.value.split("=")
            tagged_values.append([tag, value, tagged_value])
        tagged_values.append(['','', None])
        
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
        
    @transactional
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        tv = self.tagged_values[path]

        tv[col] = new_text

        iter = self.tagged_values.get_iter(path)

        # Delete tagged value if both tag and value are empty
        if not tv[0] and not tv[1] and tv[2]:
            tv[2].unlink()
            self.tagged_values.remove(iter)
        
        # Add a new tagged value:
        elif (tv[0] or tv[1]) and not tv[2]:
            tag = self.element_factory.create(UML.LiteralSpecification)
            tag.value = "%s=%s"%(tv[0], tv[1])
            self.context.subject.taggedValue.append(tag)
            tv[2] = tag
            self.tagged_values.append(['','', None])
        
component.provideAdapter(TaggedValuePage, name='Tagged values')


class DependencyPropertyPage(object):
    """
    An editor for tagged values associated with elements.

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.DependencyItem)

    element_factory = inject('element_factory')

    DEPENDENCY_TYPES = (
        (_('Dependency'), UML.Dependency),
        (_('Usage'), UML.Usage),
        (_('Realization'), UML.Realization),
        (_('Implementation'), UML.Implementation))

    def __init__(self, context):
        super(DependencyPropertyPage, self).__init__()
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()

        hbox = create_hbox_label(self, page, _('Dependency type'))

        self.combo = create_uml_combo(self.DEPENDENCY_TYPES,
            self._on_dependency_type_change)
        hbox.pack_start(self.combo, expand=False)

        hbox = create_hbox_label(self, page, _('Automatic'))

        button = gtk.CheckButton()
        button.set_active(self.context.auto_dependency)
        button.connect('toggled', self._on_auto_dependency_change)
        hbox.pack_start(button)

        page.show_all()

        self.update()

        return page


    def update(self):
        """
        Update dependency type combo box.
        """
        combo = self.combo
        context = self.context
        index = combo.get_model().get_index(context.dependency_type)
        combo.set_active(index)


    @transactional
    def _on_dependency_type_change(self, combo):
        subject = self.context.subject
        if subject:
            combo = self.combo
            cls = combo.get_model().get_value(combo.get_active())
            self.element_factory.swap_element(subject, cls)
            self.context.dependency_type = cls


    @transactional
    def _on_auto_dependency_change(self, button):
        self.context.auto_dependency = button.get_active()


component.provideAdapter(DependencyPropertyPage, name='Properties')


class AssociationPropertyPage(NamedItemPropertyPage):
    """
    """

    interface.implements(IPropertyPage)
    component.adapts(items.AssociationItem)

    def __init__(self, context):
        super(AssociationPropertyPage, self).__init__(context)
        #self.context = context
        #self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct_end(self, title, end):
        hbox = gtk.HBox()
        label = gtk.Label(title)
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        entry = gtk.Entry()
        entry.set_text(render_attribute(end.subject, multiplicity=True) or '')

        # monitor subject attribute (all, cause it contains many children)
        changed_id = entry.connect('changed', self._on_end_name_change, end)
        def handler(event):
            entry.handler_block(changed_id)
            entry.set_text(render_attribute(end.subject, multiplicity=True) or '')
            entry.handler_unblock(changed_id)
        watch_attribute(None, entry, handler)

        hbox.pack_start(entry)

        tooltips = gtk.Tooltips()
        tooltips.set_tip(entry, """\
Enter attribute name and multiplicity, for example
- name
- name [1]
- name [1..2]
- 1..2
- [1..2]\
""")

        combo = gtk.combo_box_new_text()
        for t in ('Unknown navigation', 'Not navigable', 'Navigable'):
            combo.append_text(t)
        
        combo.set_active([None, False, True].index(end.navigability))

        combo.connect('changed', self._on_navigability_change, end)
        hbox.pack_start(combo, expand=False)

        combo = gtk.combo_box_new_text()
        for t in ('No aggregation', 'Shared', 'Composite'):
            combo.append_text(t)
        
        combo.set_active(['none', 'shared', 'composite'].index(end.subject.aggregation))

        combo.connect('changed', self._on_aggregation_change, end)
        hbox.pack_start(combo, expand=False)
        
        return hbox

    def construct(self):
        page = super(AssociationPropertyPage, self).construct()
        
        if not self.context.subject:
            return page

        hbox = gtk.HBox()
        label = gtk.Label(_('Show direction'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.show_direction)
        button.connect('toggled', self._on_show_direction_change)
        hbox.pack_start(button)

        button = gtk.Button(_('Invert direction'))
        button.connect('clicked', self._on_invert_direction_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        hbox = self.construct_end(_('Head'), self.context.head_end)
        page.pack_start(hbox, expand=False)

        hbox = self.construct_end(_('Tail'), self.context.tail_end)
        page.pack_start(hbox, expand=False)

        page.show_all()

        self.update()

        return page

    def update(self):
        pass

    @transactional
    def _on_show_direction_change(self, button):
        self.context.show_direction = button.get_active()

    @transactional
    def _on_invert_direction_change(self, button):
        self.context.invert_direction()

    @transactional
    def _on_end_name_change(self, entry, end):
        end.subject.parse(entry.get_text())

    @transactional
    def _on_navigability_change(self, combo, end):
        end.navigability = (None, False, True)[combo.get_active()]

    @transactional
    def _on_aggregation_change(self, combo, end):
        end.subject.aggregation = ('none', 'shared', 'composite')[combo.get_active()]

component.provideAdapter(AssociationPropertyPage, name='Properties')


class LineStylePage(object):
    """
    Basic line style properties: color, orthogonal, etc.
    """

    interface.implements(IPropertyPage)
    component.adapts(gaphas.item.Line)

    def __init__(self, context):
        super(LineStylePage, self).__init__()
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()

        hbox = gtk.HBox()
        label = gtk.Label(_('Orthogonal'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.orthogonal)
        button.connect('toggled', self._on_orthogonal_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        hbox = gtk.HBox()
        label = gtk.Label(_('horizontal'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.horizontal)
        button.connect('toggled', self._on_horizontal_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        page.show_all()

        return page

    @transactional
    def _on_orthogonal_change(self, button):
        self.context.orthogonal = button.get_active()

    @transactional
    def _on_horizontal_change(self, button):
        self.context.horizontal = button.get_active()

component.provideAdapter(LineStylePage, name='Style')


class ObjectNodePropertyPage(NamedItemPropertyPage):
    """
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ObjectNodeItem)

    ORDERING_VALUES = ['unordered', 'ordered', 'LIFO', 'FIFO']

    def construct(self):
        page = super(ObjectNodePropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label(_('Upper Bound'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(subject.upperBound and subject.upperBound.value or '')
        entry.connect('changed', self._on_upper_bound_change)
        hbox.pack_start(entry)

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label('Ordering')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        combo = gtk.combo_box_new_text()
        for v in self.ORDERING_VALUES:
            combo.append_text(v)
        combo.set_active(self.ORDERING_VALUES.index(subject.ordering))
        combo.connect('changed', self._on_ordering_change)
        hbox.pack_start(combo, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.show_ordering)
        button.connect('toggled', self._on_ordering_show_change)
        hbox.pack_start(button, expand=False)

        label = gtk.Label('show')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        return page


    def update(self):
        pass

    @transactional
    def _on_upper_bound_change(self, entry):
        value = entry.get_text().strip()
        self.context.set_upper_bound(value)

    @transactional
    def _on_ordering_change(self, combo):
        value = self.ORDERING_VALUES[combo.get_active()]
        self.context.set_ordering(value)

    @transactional
    def _on_ordering_show_change(self, button):
        self.context.show_ordering = button.get_active()
        self.context.set_ordering(self.context.subject.ordering)


component.provideAdapter(ObjectNodePropertyPage, name='Properties')


class JoinNodePropertyPage(NamedItemPropertyPage):
    """
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ForkNodeItem)

    def construct(self):
        page = super(JoinNodePropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        if isinstance(subject, UML.JoinNode):
            label = gtk.Label(_('Join Specification'))
            label.set_justify(gtk.JUSTIFY_LEFT)
            self.size_group.add_widget(label)
            hbox.pack_start(label, expand=False)
            entry = gtk.Entry()        
            entry.set_text(subject.joinSpec and subject.joinSpec.value or '')
            entry.connect('changed', self._on_join_spec_change)
            hbox.pack_start(entry)

        return page

    def update(self):
        pass

    @transactional
    def _on_join_spec_change(self, entry):
        value = entry.get_text().strip()
        self.context.set_join_spec(value)


component.provideAdapter(JoinNodePropertyPage, name='Properties')


class FlowPropertyPage(NamedItemPropertyPage):
    """
    """

    interface.implements(IPropertyPage)
    component.adapts(items.FlowItem)

    def construct(self):
        page = super(FlowPropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label(_('Guard'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(subject.guard and subject.guard.value or '')
        entry.connect('changed', self._on_guard_change)
        hbox.pack_start(entry)

        return page

    def update(self):
        pass

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        self.context.set_guard(value)


component.provideAdapter(FlowPropertyPage, name='Properties')


class ComponentPropertyPage(NamedItemPropertyPage):
    interface.implements(IPropertyPage)
    component.adapts(items.ComponentItem)

    def construct(self):
        page = super(ComponentPropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        button = gtk.CheckButton()
        button.set_active(subject.isIndirectlyInstantiated)
        button.connect('toggled', self._on_ii_change)
        hbox.pack_start(button, expand=False)

        label = gtk.Label(_('Indirectly Instantiated'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)

        return page

    def update(self):
        pass

    @transactional
    def _on_ii_change(self, button):
        """
        Called when user clicks "Indirectly Instantiated" check button.
        """
        subject = self.context.subject
        if subject:
            subject.isIndirectlyInstantiated = button.get_active()


component.provideAdapter(ComponentPropertyPage, name='Properties')


class MessagePropertyPage(NamedItemPropertyPage):
    interface.implements(IPropertyPage)
    component.adapts(items.MessageItem)

    MESSAGE_SORT = (
        ('Call', 'synchCall'),
        ('Asynchronous', 'asynchCall'),
        ('Signal', 'asynchSignal'),
        ('Create', 'createMessage'),
        ('Delete', 'deleteMessage'),
        ('Reply', 'reply'))

    def construct(self):
        page = super(MessagePropertyPage, self).construct()

        context = self.context
        subject = context.subject
        
        if not subject:
            return page
        hbox = create_hbox_label(self, page, _('Message sort'))


        sort_data = self.MESSAGE_SORT
        lifeline = context.tail.connected_to

        # disallow connecting two delete messages to a lifeline
        if lifeline and lifeline.lifetime.is_destroyed \
                and subject.messageSort != 'deleteMessage':
            sort_data = list(sort_data)
            assert sort_data[4][1] == 'deleteMessage'
            del sort_data[4]

        combo = self.combo = create_uml_combo(sort_data,
                self._on_message_sort_change)
        hbox.pack_start(combo, expand=False)

        index = combo.get_model().get_index(subject.messageSort)
        combo.set_active(index)

        return page


    @transactional
    def _on_message_sort_change(self, combo):
        """
        Update message item's message sort information.
        """
        combo = self.combo
        ms = combo.get_model().get_value(combo.get_active())

        context = self.context
        subject = context.subject
        lifeline = context.tail.connected_to

        #
        # allow only one delete message to connect to lifeline's lifetime
        # destroyed status can be changed only by delete message itself
        #
        if lifeline and subject.messageSort == 'deleteMessage' \
                or not lifeline.lifetime.is_destroyed:
            is_destroyed = ms == 'deleteMessage'
            lifeline.lifetime.is_destroyed = is_destroyed
            lifeline.request_update()

        subject.messageSort = ms
        context.request_update()
         

component.provideAdapter(MessagePropertyPage, name='Properties')


# vim:sw=4:et:ai
