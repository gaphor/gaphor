"""
Stereotype property page.
"""

import gtk
from gaphor.core import _, inject, transactional
from gaphor.ui.interfaces import IPropertyPage
from gaphor.diagram import items
from gaphor.diagram.diagramitem import StereotypeSupport
from zope import interface, component
from gaphor import UML
from gaphor.adapters.propertypages import on_text_cell_edited, on_bool_cell_edited

class StereotypeAttributes(gtk.TreeStore):
    """
    GTK tree model to edit instance specifications of stereotypes.
    """

    element_factory = inject('element_factory')

    def __init__(self, subject):
        gtk.TreeStore.__init__(self, str, str, bool, object, object, object)
        self.subject = subject
        self.refresh()

    def refresh(self):
        self.clear()
        subject = self.subject
        stereotypes = UML.model.get_stereotypes(self.element_factory, subject)
        instances = self.subject.appliedStereotype

        # shortcut map stereotype -> slot (InstanceSpecification)
        slots = {}
        for obj in instances:
            for slot in obj.slot:
                slots[slot.definingFeature] = slot

        for st in stereotypes:
            for obj in instances:
                if st in obj.classifier:
                    break
            else:
                obj = None

            parent = self.append(None, (st.name, '', bool(obj), st, None, None))

            if obj:
                for attr in st.ownedAttribute:
                    if not attr.association:
                        slot = slots.get(attr)
                        value = slot.value if slot else ''
                        data = (attr.name, value, True, attr, obj, slot)
                        #print 'data', data
                        self.append(parent, data)
            else:
                for attr in st.ownedAttribute:
                    if not attr.association:
                        data = (attr.name, '', False, attr, None, None)
                        #print 'no data', data
                        self.append(parent, data)

    @transactional
    def set_value(self, iter, col, value):
        if col == 2:
            self.select_stereotype(iter)
        elif col == 1:
            self.set_slot_value(iter, value)
        else:
            print 'col', col

    def select_stereotype(self, iter):
        """
        Select the stereotype.
        """
        path = self.get_path(iter)
        row = self[path]
        name, old_value, is_applied, stereotype, _, _ = row
        value = not is_applied

        log.debug('selecting %s' % list(row))

        subject = self.subject
        if value:
            UML.model.apply_stereotype(self.element_factory, subject, stereotype)
        else:
            UML.model.remove_stereotype(subject, stereotype)

        row[2] = value

        # TODO: change refresh in a refresh of the data model, rather than a clear-refresh
        self.refresh()

    def set_slot_value(self, iter, value):
        """
        Set value of stereotype property applied to an UML element.

        Slot is created if instance Create valuChange value of instance spe
        """
        path = self.get_path(iter)
        row = self[path]
        name, old_value, is_applied, attr, obj, slot = row
        if isinstance(attr, UML.Stereotype):
            return # don't edit stereotype rows

        log.debug('editing %s' % list(row))

        if slot is None and not value:
            return # nothing to do and don't create slot without value

        if slot is None:
            slot = UML.model.add_slot(self.element_factory, obj, attr)

        assert slot

        if value:
            slot.value = value
        else:
            # no value, then remove slot
            del obj.slot[slot]
            slot = None
            value = ''

        row[1] = value
        row[5] = slot
        log.debug('slots %s' % obj.slot)


def create_stereotype_tree_view(model):
    """
    Create a tree view for a editable tree model.

    :Parameters:
     model
        Model, for which tree view is created.
    """
    tree_view = gtk.TreeView(model)
    tree_view.set_rules_hint(True)
    
    # Stereotype/Attributes
    col = gtk.TreeViewColumn('%s / %s' % (_('Stereotype'), _('Attribute')))
    col.set_expand(True)
    renderer = gtk.CellRendererToggle()
    renderer.set_property('active', True)
    renderer.set_property('activatable', True)
    renderer.connect('toggled', on_bool_cell_edited, model, 2)
    col.pack_start(renderer, expand=False)
    col.add_attribute(renderer, 'active', 2)
    def show_checkbox(column, cell, model, iter):
        #value = model.get_value(iter, 4)
        #cell.set_property('active', value is not None)
        value = model.get_value(iter, 3)
        cell.set_property('visible', isinstance(value, UML.Stereotype))
    col.set_cell_data_func(renderer, show_checkbox)

    renderer = gtk.CellRendererText()
    renderer.set_property('editable', False)
    renderer.set_property('is-expanded', True)
    col.pack_start(renderer, expand=False)
    col.add_attribute(renderer, 'text', 0)
    tree_view.append_column(col)

    # TODO: use col.set_cell_data_func(renderer, func, None) to toggle visibility
    # Value
    renderer = gtk.CellRendererText()
    renderer.set_property('is-expanded', True)
    renderer.connect('edited', on_text_cell_edited, model, 1)
    col = gtk.TreeViewColumn(_('Value'), renderer, text=1)
    col.set_expand(True)
    def set_editable(column, cell, model, iter):
        value = model.get_value(iter, 4)
        cell.set_property('editable', bool(value))
    col.set_cell_data_func(renderer, set_editable)
    tree_view.append_column(col)

    #tree_view.connect('key_press_event', remove_on_keypress)
    #tree_view.connect('key_press_event', swap_on_keypress)

    return tree_view



class StereotypePage(object):

    interface.implements(IPropertyPage)

    order = 40

    element_factory = inject('element_factory')

    def __init__(self, item):
        self.item = item
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()
        subject = self.item.subject
        if subject is None:
            return None

        stereotypes = UML.model.get_stereotypes(self.element_factory, subject)
        if not stereotypes:
            return None

        #applied = set(UML.model.get_applied_stereotypes(subject))
        #for i, stereotype in enumerate(stereotypes):
        #    if (i % 3) == 0:
        #        hbox = gtk.HBox(spacing=20)
        #        page.pack_start(hbox, expand=False)
        #    button = gtk.CheckButton(label=stereotype.name)
        #    button.set_active(stereotype in applied)
        #    button.connect('toggled', self._on_stereotype_selected, stereotype)
        #    hbox.pack_start(button, expand=False)

        # show stereotypes attributes toggle
        if isinstance(self.item, StereotypeSupport):
            hbox = gtk.HBox()
            label = gtk.Label('')
            hbox.pack_start(label, expand=False)
            button = gtk.CheckButton(_('Show stereotypes attributes'))
            button.set_active(self.item.show_stereotypes_attrs)
            button.connect('toggled', self._on_show_stereotypes_attrs_change)
            hbox.pack_start(button)
            page.pack_start(hbox, expand=False)

        # stereotype attributes
        self.model = StereotypeAttributes(self.item.subject)
        tree_view = create_stereotype_tree_view(self.model)
        page.pack_start(tree_view)

        page.show_all()
        return page


    #@transactional
    #def _on_stereotype_selected(self, button, stereotype):
    #    subject = self.item.subject
    #    if button.get_active():
    #        UML.model.apply_stereotype(self.element_factory, subject, stereotype)
    #    else:
    #        UML.model.remove_stereotype(subject, stereotype)
    #    self.model.refresh()

        
    @transactional
    def _on_show_stereotypes_attrs_change(self, button):
        self.item.show_stereotypes_attrs = button.get_active()
        self.item.request_update()

        
component.provideAdapter(StereotypePage,
        adapts=[UML.Element],
        name='Stereotypes')


# vim:sw=4:et:ai
