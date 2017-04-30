"""
Metaclass item editors.
"""

from __future__ import absolute_import
import gtk

from gaphor.core import _, inject, transactional
from gaphor.ui.interfaces import IPropertyPage
from zope import interface, component
from gaphor.diagram import items
from gaphor.adapters.propertypages import create_hbox_label, EventWatcher
from gaphor.UML import uml2

def _issubclass(c, b):
    try:
        return issubclass(c, b)
    except TypeError:
        return False


class MetaclassNameEditor(object):
    """
    Metaclass name editor. Provides editable combo box entry with
    predefined list of names of UML classes.
    """

    interface.implements(IPropertyPage)

    order = 10

    NAME_LABEL = _('Name')

    CLASSES = list(sorted(n for n in dir(uml2)
        if _issubclass(getattr(uml2, n), uml2.Element) and n != 'Stereotype'))


    def __init__(self, item):
        self.item = item
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        self.watcher = EventWatcher(item.subject)
    
    def construct(self):
        page = gtk.VBox()

        subject = self.item.subject
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
        self.watcher.watch('name', handler) \
            .register_handlers()
        entry.connect('destroy', self.watcher.unregister_handlers)
        page.show_all()
        return page

    @transactional
    def _on_name_change(self, entry):
        self.item.subject.name = entry.get_text()
        
component.provideAdapter(MetaclassNameEditor,
        adapts=[items.MetaclassItem], name='Properties')

# vim:sw=4:et:ai
