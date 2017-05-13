#!/usr/bin/env python

# Copyright (C) 2008-2017 Arjan Molenaar <gaphor@gmail.com>
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
State items property pages.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""

from __future__ import absolute_import
import gtk

from gaphor.core import _, inject, transactional
from gaphor.diagram import items
from zope import component
from gaphor.adapters.propertypages import NamedItemPropertyPage, create_hbox_label

class TransitionPropertyPage(NamedItemPropertyPage):
    """
    Transition property page allows to edit guard specification.
    """
    element_factory = inject('element_factory')

    component.adapts(items.TransitionItem)

    def construct(self):
        page = super(TransitionPropertyPage, self).construct()

        subject = self.subject

        if not subject:
            return page

        hbox = create_hbox_label(self, page, _('Guard'))
        entry = gtk.Entry()
        v = subject.guard.specification
        entry.set_text(v if v else '')
        entry.connect('changed', self._on_guard_change)
        changed_id = entry.connect('changed', self._on_guard_change)
        hbox.pack_start(entry)

        def handler(event):
            entry.handler_block(changed_id)
            v = event.new_value
            entry.set_text(v if v else '')
            entry.handler_unblock(changed_id)

        self.watcher.watch('guard<Constraint>.specification', handler).register_handlers()
        entry.connect('destroy', self.watcher.unregister_handlers)

        return page

    def update(self):
        pass

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        self.subject.guard.specification = value


component.provideAdapter(TransitionPropertyPage, name='Properties')


class StatePropertyPage(NamedItemPropertyPage):
    """
    State property page.
    """
    element_factory = inject('element_factory')

    component.adapts(items.StateItem)

    def construct(self):
        page = super(StatePropertyPage, self).construct()

        subject = self.subject
 
        if not subject:
            return page

        hbox = create_hbox_label(self, page, _('Entry'))
        entry = gtk.Entry()
        if self.item._entry.subject:
            entry.set_text(self.item._entry.subject.name)
        entry.connect('changed', self._on_text_change, self.item.set_entry)
        hbox.pack_start(entry)

        hbox = create_hbox_label(self, page, _('Exit'))
        entry = gtk.Entry()
        if self.item._exit.subject:
            entry.set_text(self.item._exit.subject.name)
        entry.connect('changed', self._on_text_change, self.item.set_exit)
        hbox.pack_start(entry)

        hbox = create_hbox_label(self, page, _('Do Activity'))
        entry = gtk.Entry()
        if self.item._do_activity.subject:
            entry.set_text(self.item._do_activity.subject.name)
        entry.connect('changed', self._on_text_change, self.item.set_do_activity)
        hbox.pack_start(entry)

        page.show_all()

        return page

    def update(self):
        pass

    @transactional
    def _on_text_change(self, entry, method):
        value = entry.get_text().strip()
        method(value)



component.provideAdapter(StatePropertyPage, name='Properties')

