"""
Adapters for the Property Editor.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.

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

import gobject
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


class EditableTreeModel(gtk.ListStore):
    """
    Editable GTK tree model based on ListStore model.

    Every row is represented by a list of editable values. Last column
    contains an object, which is being edited (this column is not
    displayed). When editable value in first column is set to empty string
    then object is deleted.

    Last row is empty and contains no object to edit. It allows to enter
    new values.

    When model is edited, then item is requested to be updated on canvas.

    Attributes:
    - _item: diagram item owning tree model
    """
    element_factory = inject('element_factory')

    def __init__(self, item, cols=None):
        """
        Create new model.

        Parameters:
        - _item: diagram item owning tree model
        - cols: model columns, defaults to [str, object]
        """
        if cols is None:
            cols = (str, object)
        super(EditableTreeModel, self).__init__(*cols)
        self._item = item

        for data in self._get_rows():
            self.append(data)
        self._add_empty()


    def _get_rows(self):
        """
        Return rows to be edited. Last row has to contain object being
        edited.
        """
        raise NotImplemented


    def _create_object(self):
        """
        Create new object.
        """
        raise NotImplemented


    def _set_object_value(self, row, col, value):
        """
        Update row's column with a value.
        """
        raise NotImplemented


    def _swap_objects(self, o1, o2):
        """
        Swap two objects. If objects are swapped, then return ``True``.
        """
        raise NotImplemented


    def _get_object(self, iter):
        """
        Get object from ``iter``.
        """
        path = self.get_path(iter)
        return self[path][-1]


    def swap(self, a, b):
        """
        Swap two list rows.
        Parameters:
        - a: path to first row
        - b: path to second row
        """
        if not a or not b:
            return
        o1 = self[a][-1]
        o2 = self[b][-1]
        if o1 and o2 and self._swap_objects(o1, o2):
            self._item.request_update(matrix=False)
            super(EditableTreeModel, self).swap(a, b)


    def _add_empty(self):
        """
        Add empty row to the end of the model.
        """
        self.append([None] * self.get_n_columns())


    def iter_prev(self, iter):
        """
        Get previous GTK tree iterator to ``iter``.
        """
        i = self.get_path(iter)[0]
        if i == 0:
            return None
        return self.get_iter((i - 1,))


    @transactional
    def set_value(self, iter, col, value):
        path = self.get_path(iter)
        row = self[path]

        if col == 0 and not value and row[-1]:
            # kill row and delete object if text of first column is empty
            self.remove(iter)

        elif value and col == 0 and not row[-1]:
            # create new object
            obj = self._create_object()
            row[-1] = obj
            self._set_object_value(row, col, value)
            self._add_empty()

        elif row[-1]:
            self._set_object_value(row, col, value)
        self._item.request_update(matrix=False)


    def remove(self, iter):
        """
        Remove object from GTK model and destroy it.
        """
        obj = self._get_object(iter)
        if obj:
            obj.unlink()
            #self._item.request_update(matrix=False)
            return super(EditableTreeModel, self).remove(iter)
        else:
            return iter



class ClassAttributes(EditableTreeModel):
    """
    GTK tree model to edit class attributes.
    """
    def _get_rows(self):
        for attr in self._item.subject.ownedAttribute:
            if not attr.association:
                yield [attr.render(), attr.isStatic, attr]


    def _create_object(self):
        attr = self.element_factory.create(UML.Property)
        self._item.subject.ownedAttribute = attr
        return attr


    @transactional
    def _set_object_value(self, row, col, value):
        attr = row[-1]
        if col == 0:
            attr.parse(value)
            row[0] = attr.render()
        elif col == 1:
            attr.isStatic = not attr.isStatic
            row[1] = attr.isStatic

    def _swap_objects(self, o1, o2):
        return self._item.subject.ownedAttribute.swap(o1, o2)



class ClassOperations(EditableTreeModel):
    """
    GTK tree model to edit class operations.
    """
    def _get_rows(self):
        for operation in self._item.subject.ownedOperation:
            yield [operation.render(), operation]


    def _create_object(self):
        operation = self.element_factory.create(UML.Operation)
        self._item.subject.ownedOperation = operation
        return operation


    @transactional
    def _set_object_value(self, row, col, value):
        operation = row[-1]
        operation.parse(value)
        row[0] = operation.render()


    def _swap_objects(self, o1, o2):
        return self._item.subject.ownedOperation.swap(o1, o2)



class CommunicationMessageModel(EditableTreeModel):
    """
    GTK tree model for list of messages on communication diagram.
    """
    def __init__(self, item, cols=None, inverted=False):
        self.inverted = inverted
        super(CommunicationMessageModel, self).__init__(item, cols)

    def _get_rows(self):
        if self.inverted:
            for message in self._item._inverted_messages:
                yield [message.name, message]
        else:
            for message in self._item._messages:
                yield [message.name, message]


    def remove(self, iter):
        """
        Remove message from message item and destroy it.
        """
        message = self._get_object(iter)
        item = self._item
        super(CommunicationMessageModel, self).remove(iter)
        item.remove_message(message, self.inverted)


    def _create_object(self):
        item = self._item
        subject = item.subject
        message = self.element_factory.create(UML.Message)
        if self.inverted:
            # inverted message goes in different direction, than subject
            message.sendEvent = subject.receiveEvent
            message.receiveEvent = subject.sendEvent
        else:
            # additional message goes in the same direction as subject
            message.sendEvent = subject.sendEvent
            message.receiveEvent = subject.receiveEvent
        item.add_message(message, self.inverted)
        return message


    def _set_object_value(self, row, col, value):
        message = row[-1]
        message.name = value
        row[0] = value
        self._item.set_message_text(message, value, self.inverted)


    def _swap_objects(self, o1, o2):
        return self._item.swap_messages(o1, o2, self.inverted)



@transactional
def remove_on_keypress(tree, event):
    """
    Remove selected items from GTK model on ``backspace`` keypress.
    """
    k = gtk.gdk.keyval_name(event.keyval).lower()
    if k == 'backspace' or k == 'kp_delete':
        model, iter = tree.get_selection().get_selected()
        if iter:
            model.remove(iter)


@transactional
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
        

@transactional
def on_text_cell_edited(renderer, path, value, model, col=0):
    """
    Update editable tree model based on fresh user input.
    """
    iter = model.get_iter(path)
    model.set_value(iter, col, value)


@transactional
def on_bool_cell_edited(renderer, path, model, col):
    """
    Update editable tree model based on fresh user input.
    """
    iter = model.get_iter(path)
    model.set_value(iter, col, renderer.get_active())


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
            if widget.props.has_focus:
                return
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
    hbox = gtk.HBox(spacing=12)
    label = gtk.Label(label)
    label.set_alignment(0.0, 0.5)
    adapter.size_group.add_widget(label)
    hbox.pack_start(label, expand=False)
    page.pack_start(hbox, expand=False)
    return hbox


def create_tree_view(model, names, tip='', ro_cols=None):
    """
    Create a tree view for a editable tree model.

    :Parameters:
     model
        Model, for which tree view is created.
     names
        Names of columns.
     tip
        User interface tool tip for tree view.
     ro_cols
        Collection of indices pointing read only columns.
    """
    if ro_cols is None:
        ro_cols = set()

    tree_view = gtk.TreeView(model)
    tree_view.set_rules_hint(True)
    
    n = model.get_n_columns() - 1
    for name, i in zip(names, range(n)):
        col_type = model.get_column_type(i)
        if col_type == gobject.TYPE_STRING:
            renderer = gtk.CellRendererText()
            renderer.set_property('editable', i not in ro_cols)
            renderer.set_property('is-expanded', True)
            renderer.connect('edited', on_text_cell_edited, model, i)
            col = gtk.TreeViewColumn(name, renderer, text=i)
            col.set_expand(True)
            tree_view.append_column(col)
        elif col_type == gobject.TYPE_BOOLEAN:
            renderer = gtk.CellRendererToggle()
            renderer.set_property('activatable', i not in ro_cols)
            renderer.connect('toggled', on_bool_cell_edited, model, i)
            col = gtk.TreeViewColumn(name, renderer, active=i)
            col.set_expand(False)
            tree_view.append_column(col)

    tree_view.connect('key_press_event', remove_on_keypress)
    tree_view.connect('key_press_event', swap_on_keypress)

    tip = tip + """
Press ENTER to edit item, BS/DEL to remove item.
Use -/= to move items up or down.\
    """
    tree_view.set_tooltip_text(tip)

    return tree_view



class CommentItemPropertyPage(object):
    """
    Property page for Comments
    """
    interface.implements(IPropertyPage)
    component.adapts(UML.Comment)

    order = 0

    def __init__(self, subject):
        self.subject = subject

    def construct(self):
        subject = self.subject
        page = gtk.VBox()

        if not subject:
            return page

        label = gtk.Label(_('Comment'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        page.pack_start(label, expand=False)

        buffer = gtk.TextBuffer()
        if subject.body:
            buffer.set_text(subject.body)
        text_view = gtk.TextView()
        text_view.set_buffer(buffer)
        text_view.show()
        text_view.set_size_request(-1, 100)
        page.pack_start(text_view)
        page.set_data('default', text_view)

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
        self.subject.body = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        
component.provideAdapter(CommentItemPropertyPage, name='Properties')


class NamedElementPropertyPage(object):
    """
    An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    interface.implements(IPropertyPage)
    component.adapts(UML.NamedElement)

    order = 10

    NAME_LABEL = _('Name')

    def __init__(self, subject):
        assert isinstance(subject, UML.NamedElement)
        self.subject = subject
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    
    def construct(self):
        page = gtk.VBox()

        subject = self.subject
        if not subject:
            return page

        hbox = create_hbox_label(self, page, self.NAME_LABEL)
        entry = gtk.Entry()        
        entry.set_text(subject and subject.name or '')
        hbox.pack_start(entry)
        page.set_data('default', entry)

        # monitor subject.name attribute
        changed_id = entry.connect('changed', self._on_name_change)

        def handler(event):
            if event.element is subject and event.new_value is not None:
                entry.handler_block(changed_id)
                entry.set_text(event.new_value)
                entry.handler_unblock(changed_id)
        watch_attribute(type(subject).name, entry, handler)

        page.show_all()
        return page

    @transactional
    def _on_name_change(self, entry):
        self.subject.name = entry.get_text()
        
component.provideAdapter(NamedElementPropertyPage, name='Properties')


class NamedItemPropertyPage(NamedElementPropertyPage):
    """
    Base class for named item based adapters.
    """

    def __init__(self, item):
        self.item = item
        super(NamedItemPropertyPage, self).__init__(item.subject)


class ClassPropertyPage(NamedElementPropertyPage):
    """
    Adapter which shows a property page for a class view.
    """

    component.adapts(UML.Class)

    def __init__(self, subject):
        super(ClassPropertyPage, self).__init__(subject)
        
    def construct(self):
        page = super(ClassPropertyPage, self).construct()

        if not self.subject:
            return page

        # Abstract toggle
        hbox = gtk.HBox()
        label = gtk.Label('')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton(_("Abstract"))
        button.set_active(self.subject.isAbstract)
        
        button.connect('toggled', self._on_abstract_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        hbox.show_all()

        return page

    @transactional
    def _on_abstract_change(self, button):
        self.subject.isAbstract = button.get_active()

component.provideAdapter(ClassPropertyPage, name='Properties')


class InterfacePropertyPage(NamedItemPropertyPage):
    """
    Adapter which shows a property page for an interface view.
    """

    component.adapts(items.InterfaceItem)

    def construct(self):
        page = super(InterfacePropertyPage, self).construct()
        item = self.item

        # Fold toggle
        hbox = gtk.HBox()
        label = gtk.Label('')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton(_("Folded"))
        button.set_active(item.folded)
        button.connect('toggled', self._on_fold_change)

        connected_items = [c.item for c in item.canvas.get_connections(connected=item)]
        allowed = (items.DependencyItem, items.ImplementationItem)
        can_fold = len(connected_items) == 0 \
            or len(connected_items) == 1 and isinstance(connected_items[0], allowed)

        button.set_sensitive(can_fold)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        hbox.show_all()

        return page

    @transactional
    def _on_fold_change(self, button):
        item = self.item

        connected_items = [c.item for c in item.canvas.get_connections(connected=item)]
        assert len(connected_items) <= 1

        line = None
        if len(connected_items) == 1:
            line = connected_items[0]


        fold = button.get_active()

        if fold:
            item.folded = item.FOLDED_PROVIDED
        else:
            item.folded = item.FOLDED_NONE

        if line:
            if fold and isinstance(line, items.DependencyItem):
                item.folded = item.FOLDED_REQUIRED

            line._solid = fold
            constraint = line.head.connection_data
            constraint.ratio_x = 0.5
            constraint.ratio_y = 0.5
            line.request_update()


component.provideAdapter(InterfacePropertyPage, name='Properties')




class AttributesPage(object):
    """
    An editor for attributes associated with classes and interfaces.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    order = 20

    element_factory = inject('element_factory')

    def __init__(self, context):
        super(AttributesPage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        if not self.context.subject:
            return page

        # Show attributes toggle
        hbox = gtk.HBox()
        label = gtk.Label('')
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton(_('Show attributes'))
        button.set_active(self.context.show_attributes)
        button.connect('toggled', self._on_show_attributes_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        self.model = ClassAttributes(self.context, (str, bool, object))
        
        tip = """\
Add and edit class attributes according to UML syntax. Attribute syntax examples
- attr
- + attr: int
- # /attr: int
"""
        tree_view = create_tree_view(self.model, (_('Attributes'), _('S')), tip)

        page.pack_start(tree_view)

        return page
        

    @transactional
    def _on_show_attributes_change(self, button):
        self.context.show_attributes = button.get_active()
        self.context.request_update()
        

component.provideAdapter(AttributesPage, name='Attributes')


class OperationsPage(object):
    """
    An editor for operations associated with classes and interfaces.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    order = 30

    element_factory = inject('element_factory')

    def __init__(self, context):
        super(OperationsPage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        if not self.context.subject:
            return page

        # Show operations toggle
        hbox = gtk.HBox()
        label = gtk.Label("")
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton(_("Show operations"))
        button.set_active(self.context.show_operations)
        button.connect('toggled', self._on_show_operations_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        self.model = ClassOperations(self.context)
        tip = """\
Add and edit class operations according to UML syntax. Operation syntax examples
- call()
- + call(a: int, b: str)
- # call(a: int: b: str): bool
"""
        tree_view = create_tree_view(self.model, (_('Operation'),), tip)
        page.pack_start(tree_view)

        return page
        
    @transactional
    def _on_show_operations_change(self, button):
        self.context.show_operations = button.get_active()
        self.context.request_update()


component.provideAdapter(OperationsPage, name='Operations')



class DependencyPropertyPage(object):
    """
    Dependency item editor.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.DependencyItem)

    order = 0

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

        hbox = create_hbox_label(self, page, '')

        button = gtk.CheckButton(_('Automatic'))
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

    component.adapts(items.AssociationItem)

    NAVIGABILITY = [None, False, True]

    def construct_end(self, title, end):

        if not end.subject:
            return None

        # TODO: use gtk.Frame here
        frame = gtk.Frame('%s (: %s)' % (title, end.subject.type.name))
        vbox = gtk.VBox()
        vbox.set_border_width(6)
        vbox.set_spacing(6)
        frame.add(vbox)

        #label = gtk.Label(title)
        #label.set_alignment(0.0, 0.5)
        #self.size_group.add_widget(label)
        #vbox.pack_start(label, expand=False)

        entry = gtk.Entry()
        entry.set_text(render_attribute(end.subject, multiplicity=True) or '')

        # monitor subject attribute (all, cause it contains many children)
        changed_id = entry.connect('changed', self._on_end_name_change, end)
        def handler(event):
            entry.handler_block(changed_id)
            entry.set_text(render_attribute(end.subject, multiplicity=True) or '')
            entry.handler_unblock(changed_id)
        watch_attribute(None, entry, handler)

        vbox.pack_start(entry)

        entry.set_tooltip_text("""\
Enter attribute name and multiplicity, for example
- name
- name [1]
- name [1..2]
- 1..2
- [1..2]\
""")

        combo = gtk.combo_box_new_text()
        for t in ('public (+)', 'protected (#)', 'package (~)', 'private (-)'):
            combo.append_text(t)
        
        combo.set_active(['public', 'protected', 'package', 'private'].index(end.subject.visibility))

        combo.connect('changed', self._on_visibility_change, end)
        vbox.pack_start(combo, expand=False)

        combo = gtk.combo_box_new_text()
        for t in ('Unknown navigation', 'Not navigable', 'Navigable'):
            combo.append_text(t)
        
        nav = UML.model.get_navigability(self.subject, end.subject)
        combo.set_active(self.NAVIGABILITY.index(nav))

        combo.connect('changed', self._on_navigability_change, end)
        vbox.pack_start(combo, expand=False)

        combo = gtk.combo_box_new_text()
        for t in ('No aggregation', 'Shared', 'Composite'):
            combo.append_text(t)
        
        combo.set_active(['none', 'shared', 'composite'].index(end.subject.aggregation))

        combo.connect('changed', self._on_aggregation_change, end)
        vbox.pack_start(combo, expand=False)
        
        return frame

    def construct(self):
        page = super(AssociationPropertyPage, self).construct()
        
        if not self.subject:
            return page

        hbox = gtk.HBox()
        label = gtk.Label('')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton(_('Show direction'))
        button.set_active(self.item.show_direction)
        button.connect('toggled', self._on_show_direction_change)
        hbox.pack_start(button)

        button = gtk.Button(_('Invert Direction'))
        button.connect('clicked', self._on_invert_direction_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        box = self.construct_end(_('Head'), self.item.head_end)
        if box:
            page.pack_start(box, expand=False)

        box = self.construct_end(_('Tail'), self.item.tail_end)
        if box:
            page.pack_start(box, expand=False)

        page.show_all()

        self.update()

        return page

    def update(self):
        pass

    @transactional
    def _on_show_direction_change(self, button):
        self.item.show_direction = button.get_active()

    @transactional
    def _on_invert_direction_change(self, button):
        self.item.invert_direction()

    @transactional
    def _on_end_name_change(self, entry, end):
        end.subject.parse(entry.get_text())

    @transactional
    def _on_visibility_change(self, combo, end):
        end.subject.visibility = ('public', 'protected', 'package', 'private')[combo.get_active()]

    @transactional
    def _on_navigability_change(self, combo, end):
        nav = self.NAVIGABILITY[combo.get_active()]
        UML.model.set_navigability(self.item.subject, end.subject, nav)

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

    order = 400

    def __init__(self, item):
        super(LineStylePage, self).__init__()
        self.item = item
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()

        hbox = gtk.HBox()
        label = gtk.Label('')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton(_('Orthogonal'))
        button.set_active(self.item.orthogonal)
        button.connect('toggled', self._on_orthogonal_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        hbox = gtk.HBox()
        label = gtk.Label('')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton(_('Horizontal'))
        button.set_active(self.item.horizontal)
        button.connect('toggled', self._on_horizontal_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        page.show_all()

        return page

    @transactional
    def _on_orthogonal_change(self, button):
        self.item.orthogonal = button.get_active()

    @transactional
    def _on_horizontal_change(self, button):
        self.item.horizontal = button.get_active()

component.provideAdapter(LineStylePage, name='Style')


class ObjectNodePropertyPage(NamedItemPropertyPage):
    """
    """

    component.adapts(items.ObjectNodeItem)

    ORDERING_VALUES = ['unordered', 'ordered', 'LIFO', 'FIFO']

    def construct(self):
        page = super(ObjectNodePropertyPage, self).construct()

        subject = self.subject
        
        if not subject:
            return page

        hbox = create_hbox_label(self, page, _('Upper bound'))
        entry = gtk.Entry()        
        entry.set_text(subject.upperBound and subject.upperBound.value or '')
        entry.connect('changed', self._on_upper_bound_change)
        hbox.pack_start(entry)

        hbox = create_hbox_label(self, page, '')
        combo = gtk.combo_box_new_text()
        for v in self.ORDERING_VALUES:
            combo.append_text(v)
        combo.set_active(self.ORDERING_VALUES.index(subject.ordering))
        combo.connect('changed', self._on_ordering_change)
        hbox.pack_start(combo, expand=False)

        hbox = create_hbox_label(self, page, '')
        button = gtk.CheckButton(_('Ordering'))
        button.set_active(self.item.show_ordering)
        button.connect('toggled', self._on_ordering_show_change)
        hbox.pack_start(button, expand=False)

        return page


    def update(self):
        pass

    @transactional
    def _on_upper_bound_change(self, entry):
        value = entry.get_text().strip()
        self.item.set_upper_bound(value)

    @transactional
    def _on_ordering_change(self, combo):
        value = self.ORDERING_VALUES[combo.get_active()]
        self.subject.ordering = value

    @transactional
    def _on_ordering_show_change(self, button):
        self.item.show_ordering = button.get_active()
        self.item.set_ordering(self.subject.ordering)


component.provideAdapter(ObjectNodePropertyPage, name='Properties')


class JoinNodePropertyPage(NamedItemPropertyPage):
    """
    """

    component.adapts(items.ForkNodeItem)

    def construct(self):
        page = super(JoinNodePropertyPage, self).construct()

        subject = self.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        if isinstance(subject, UML.JoinNode):
            hbox = create_hbox_label(self, page, _('Join specification'))
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
        self.item.set_join_spec(value)


component.provideAdapter(JoinNodePropertyPage, name='Properties')


class FlowPropertyPage(NamedElementPropertyPage):
    """
    """

    component.adapts(UML.ControlFlow)

    def construct(self):
        page = super(FlowPropertyPage, self).construct()

        subject = self.subject
        
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
        self.subject.guard.value = value


component.provideAdapter(FlowPropertyPage, name='Properties')


class ComponentPropertyPage(NamedItemPropertyPage):
    """
    """

    component.adapts(items.ComponentItem)

    def construct(self):
        page = super(ComponentPropertyPage, self).construct()

        subject = self.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        button = gtk.CheckButton(_('Indirectly instantiated'))
        button.set_active(subject.isIndirectlyInstantiated)
        button.connect('toggled', self._on_ii_change)
        hbox.pack_start(button, expand=False)

        return page

    def update(self):
        pass

    @transactional
    def _on_ii_change(self, button):
        """
        Called when user clicks "Indirectly instantiated" check button.
        """
        subject = self.subject
        if subject:
            subject.isIndirectlyInstantiated = button.get_active()


component.provideAdapter(ComponentPropertyPage, name='Properties')


class MessagePropertyPage(NamedItemPropertyPage):
    """
    """

    component.adapts(items.MessageItem)

    element_factory = inject('element_factory')

    NAME_LABEL = _('Message')

    MESSAGE_SORT = (
        ('Call', 'synchCall'),
        ('Asynchronous', 'asynchCall'),
        ('Signal', 'asynchSignal'),
        ('Create', 'createMessage'),
        ('Delete', 'deleteMessage'),
        ('Reply', 'reply'))

    def construct(self):
        page = super(MessagePropertyPage, self).construct()

        item = self.item
        subject = item.subject

        if not subject:
            return page

        if item.is_communication():
            hbox = gtk.HBox()

            self._messages = CommunicationMessageModel(item)
            tree_view = create_tree_view(self._messages, (_('Message'),))
            tree_view.set_headers_visible(False)
            frame = gtk.Frame(label=_('Additional Messages'))
            frame.add(tree_view)
            hbox.pack_start(frame)

            self._inverted_messages = CommunicationMessageModel(item, inverted=True)
            tree_view = create_tree_view(self._inverted_messages, (_('Message'),))
            tree_view.set_headers_visible(False)
            frame = gtk.Frame(label=_('Inverted Messages'))
            frame.add(tree_view)
            hbox.pack_end(frame)

            page.pack_start(hbox)

        else:
            hbox = create_hbox_label(self, page, _('Message sort'))

            sort_data = self.MESSAGE_SORT
            lifeline = None
            cinfo = item.canvas.get_connection(item.tail)
            if cinfo:
                lifeline = cinfo.connected

            # disallow connecting two delete messages to a lifeline
            if lifeline and lifeline.is_destroyed \
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

        item = self.item
        subject = item.subject
        lifeline = None
        cinfo = item.canvas.get_connection(item.tail)
        if cinfo:
            lifeline = cinfo.connected

        #
        # allow only one delete message to connect to lifeline's lifetime
        # destroyed status can be changed only by delete message itself
        #
        if lifeline:
            if subject.messageSort == 'deleteMessage' \
                    or not lifeline.is_destroyed:
                is_destroyed = ms == 'deleteMessage'
                lifeline.is_destroyed = is_destroyed
                lifeline.request_update()

        subject.messageSort = ms
        item.request_update()
         

component.provideAdapter(MessagePropertyPage, name='Properties')


# vim:sw=4:et:ai
