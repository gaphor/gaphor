#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
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
