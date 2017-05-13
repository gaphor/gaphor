#!/usr/bin/env python

# Copyright (C) 2010-2017 Arjan Molenaar <gaphor@gmail.com>
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
from __future__ import absolute_import
import gtk
import logging
from gaphor.tests import TestCase
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphas.canvas import Context

Event = Context

logging.basicConfig(level=logging.DEBUG)

class DiagramItemConnectorTestCase(TestCase):
    services = TestCase.services + [ 'main_window', 'ui_manager', 'action_manager', 'properties' ]

    def setUp(self):
        super(DiagramItemConnectorTestCase, self).setUp()
        mw = self.get_service('main_window')
        mw.open()
        mw.show_diagram(self.diagram)
        self.main_window = mw

    def test_item_reconnect(self):
        # Setting the stage:
	ci1 = self.create(items.ClassItem, uml2.Class)
        ci2 = self.create(items.ClassItem, uml2.Class)
        a = self.create(items.AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        self.assertTrue(a.subject)
        self.assertTrue(a.head_end.subject)
        self.assertTrue(a.tail_end.subject)

        the_association = a.subject

        # The act: perform button press event and button release
        view = self.main_window.get_current_diagram_view()
        
        self.assertSame(self.diagram.canvas, view.canvas)

        p = view.get_matrix_i2v(a).transform_point(*a.head.pos)

        event = Event(x=p[0], y=p[1], type=gtk.gdk.BUTTON_PRESS, state=0)

        view.do_event(event)

        self.assertSame(the_association, a.subject)

        event = Event(x=p[0], y=p[1], type=gtk.gdk.BUTTON_RELEASE, state=0)

        view.do_event(event)

        self.assertSame(the_association, a.subject)

# vim:sw=4:et:ai
