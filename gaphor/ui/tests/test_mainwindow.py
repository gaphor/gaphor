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

from gaphor.application import Application
from gaphor.UML import uml2

class MainWindowTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory', 'properties', 'main_window', 'ui_manager', 'action_manager'])

    def tearDown(self):
        Application.shutdown()

    def test_creation(self):
        # MainWindow should be created as resource
        main_w = Application.get_service('main_window')
        main_w.open()
        self.assertEqual(main_w.get_current_diagram(), None)

    def test_show_diagram(self):
        main_w = Application.get_service('main_window')
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(uml2.Diagram)
        main_w.open()
        self.assertEqual(main_w.get_current_diagram(), None)

        main_w.show_diagram(diagram)
        
# vim:sw=4:et:ai
