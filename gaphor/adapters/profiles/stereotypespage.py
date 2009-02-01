"""
Stereotype property page.
"""

import gtk
from gaphor.core import _, inject, transactional
from gaphor.ui.interfaces import IPropertyPage
from gaphor.diagram import items
from zope import interface, component
from gaphor import UML
from gaphor.adapters.propertypages import create_tree_view


class StereotypeAttributes(gtk.TreeStore):
    """
    GTK tree model to edit instance specifications of stereotypes.
    """

    element_factory = inject('element_factory')

    def __init__(self, item):
        gtk.TreeStore.__init__(self, str, str, object, object, object)
        self.item = item
        self.refresh()

    def refresh(self):
        self.clear()
        applied = UML.model.get_applied_stereotypes(self.item.subject)
        instances = self.item.subject.appliedStereotype

        # map attributes to slots
        slots = {}
        for obj in instances:
            for slot in obj.slot:
                slots[slot.definingFeature] = slot

        for st, obj in zip(applied, instances):
            parent = self.append(None, (st.name, '', st, None, None))
            for attr in st.ownedAttribute:
                if not attr.association:
                    slot = slots.get(attr)
                    value = slot.value[0].value if slot is not None else ''
                    data = (attr.name, value, attr, obj, slot)
                    self.append(parent, data)


    def set_value(self, iter, col, value):
        """
        Set value of stereotype property applied to an UML element.

        Slot is created if instance Create valuChange value of instance spe
        """
        if col != 1: # only editing of 2nd column is allowed
            return

        path = self.get_path(iter)
        row = self[path]
        name, old_value, attr, obj, slot = row
        if isinstance(attr, UML.Stereotype):
            return # don't edit stereotype rows

        log.debug('editing %s' % list(row))

        if slot is None and not value:
            return # nothing to do and don't create slot without value

        if slot is None:
            slot = UML.model.add_slot(self.element_factory, obj, attr)

        assert slot

        if value:
            slot.value[0].value = value
        else:
            # no value, then remove slot
            del obj.slot[slot]
            slot = None
            value = ''

        row[1] = value
        row[4] = slot
        log.debug('slots %s' % obj.slot)



class StereotypePage(object):

    interface.implements(IPropertyPage)

    element_factory = inject('element_factory')

    def __init__(self, context):
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()
        subject = self.context.subject
        if subject is None:
            return

        applied = set(UML.model.get_applied_stereotypes(subject))
        stereotypes = UML.model.get_stereotypes(self.element_factory, subject)
        for i, stereotype in enumerate(stereotypes):
            if (i % 3) == 0:
                hbox = gtk.HBox(spacing=20)
                page.pack_start(hbox, expand=False)
            button = gtk.CheckButton(label=stereotype.name)
            button.set_active(stereotype in applied)
            button.connect('toggled', self._on_stereotype_selected, stereotype)
            hbox.pack_start(button, expand=False)

        # show stereotypes attributes toggle
        hbox = gtk.HBox()
        label = gtk.Label(_('Show stereotypes attributes'))
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.show_stereotypes_attrs)
        button.connect('toggled', self._on_show_stereotypes_attrs_change)
        hbox.pack_start(button)
        page.pack_start(hbox, expand=False)

        # stereotype attributes
        self.model = StereotypeAttributes(self.context)
        t = '%s / %s' % (_('Stereotype'), _('Attribute'))
        tree_view = create_tree_view(self.model, (t, _('Value')), ro_cols=(0,))
        page.pack_start(tree_view)

        page.show_all()
        return page


    @transactional
    def _on_stereotype_selected(self, button, stereotype):
        subject = self.context.subject
        if button.get_active():
            UML.model.apply_stereotype(self.element_factory, subject, stereotype)
        else:
            UML.model.remove_stereotype(subject, stereotype)
        self.model.refresh()

        
    @transactional
    def _on_show_stereotypes_attrs_change(self, button):
        self.context.show_stereotypes_attrs = button.get_active()
        self.context.request_update()

        
component.provideAdapter(StereotypePage,
        adapts=[items.ElementItem],
        name='Stereotypes')
component.provideAdapter(StereotypePage,
        adapts=[items.LineItem],
        name='Stereotypes')


# vim:sw=4:et:ai
