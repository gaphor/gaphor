#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Activity partition property page.
"""
from __future__ import absolute_import
import gtk
from gaphor.core import _, inject, transactional
from gaphor.ui.interfaces import IPropertyPage
from gaphor.diagram import items
from zope import interface, component
from gaphor.adapters.propertypages import NamedItemPropertyPage


class PartitionPropertyPage(NamedItemPropertyPage):
    """
    Partition property page.
    """
    interface.implements(IPropertyPage)
    component.adapts(items.PartitionItem)

    element_factory = inject('element_factory')

    def construct(self):
        item = self.item

        page = super(PartitionPropertyPage, self).construct()

        if item.subject:
            if not item._toplevel:
                hbox = gtk.HBox(spacing=12)
                button = gtk.CheckButton(_('External'))
                button.set_active(item.subject.isExternal)
                button.connect('toggled', self._on_external_change)
                hbox.pack_start(button)
                page.pack_start(hbox, expand=False)
            else:
                pass
                #hbox = gtk.HBox(spacing=12)
                #button = gtk.CheckButton(_('Dimension'))
                #button.set_active(item.subject.isDimension)
                #button.connect('toggled', self._on_dimension_change)

        return page

    @transactional
    def _on_external_change(self, button):
        item = self.item
        if item.subject:
            item.subject.isExternal = button.get_active()
        item.request_update()


component.provideAdapter(PartitionPropertyPage, name='Properties')


# vim:sw=4:et:ai
