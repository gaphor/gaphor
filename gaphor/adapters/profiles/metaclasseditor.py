"""
Metaclass item editors.
"""

import gtk

from gaphor.core import _, inject, transactional
from gaphor.ui.interfaces import IPropertyPage
from zope import interface, component
from gaphor.diagram import items
from gaphor.adapters.propertypages import create_hbox_label, watch_attribute

class MetaclassNameEditor(object):
    """
    Metaclass name editor. Provides editable combo box entry with
    predefined list of names of UML classes.
    """

    interface.implements(IPropertyPage)

    order = 10

    NAME_LABEL = _('Name')

    CLASSES = [
        'Artifact',
        'Association',
        'Class',
        'Component',
        'Dependency',
        'Node',
    ]


    def __init__(self, context):
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    
    def construct(self):
        page = gtk.VBox()

        subject = self.context.subject
        if not subject:
            return page

        hbox = create_hbox_label(self, page, self.NAME_LABEL)
        model = gtk.ListStore(str)
        for c in self.CLASSES:
            model.append([c])

        cb = gtk.ComboBoxEntry(model, 0)

        completion = gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_minimum_key_length(1)
        completion.set_text_column(0)
        cb.child.set_completion(completion)

        entry = cb.child
        entry.set_text(subject and subject.name or '')
        hbox.pack_start(cb)
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
        self.context.subject.name = entry.get_text()
        
component.provideAdapter(MetaclassNameEditor,
        adapts=[items.MetaclassItem], name='Properties')


