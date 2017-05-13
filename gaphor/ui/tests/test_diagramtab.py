#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
import unittest

from gaphor.UML import uml2
from gaphor.application import Application


class DiagramTabTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory', 'main_window', 'ui_manager', 'action_manager', 'properties', 'element_dispatcher'])
        main_window = Application.get_service('main_window')
        main_window.open()
        element_factory = Application.get_service('element_factory')
        self.element_factory = element_factory
        self.diagram = element_factory.create(uml2.Diagram)
        self.tab = main_window.show_diagram(self.diagram)
        self.assertEquals(self.tab.diagram, self.diagram)
        self.assertEquals(self.tab.view.canvas, self.diagram.canvas)
        self.assertEquals(len(element_factory.lselect()), 1)

    def tearDown(self):
        self.tab.close()
        del self.tab
        self.diagram.unlink()
        del self.diagram
        Application.shutdown()
        #assert len(self.element_factory.lselect()) == 0

    def test_creation(self):
        pass

    def test_placement(self):
        tab = self.tab
        diagram = self.diagram
        from gaphas import Element
        from gaphas.examples import Box
        box = Box()
        diagram.canvas.add(box)
        diagram.canvas.update_now()
        tab.view.request_update([box])
        
        from gaphor.diagram.comment import CommentItem
        comment = self.diagram.create(CommentItem, subject=self.element_factory.create(uml2.Comment))
        self.assertEquals(len(self.element_factory.lselect()), 2)
        
# vim:sw=4:et:ai
