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
from gaphor.services.diagramexportmanager import DiagramExportManager

class DiagramExportManagerTestCase(unittest.TestCase):
    
    def setUp(self):
        Application.init(services=['main_window', 'properties', 'element_factory', 'diagram_export_manager', 'action_manager', 'ui_manager' ])

    def shutDown(self):
        Application.shutdown()

    def test_init(self):
        des = DiagramExportManager()
        des.init(None)

    def test_init_from_application(self):
        Application.get_service('diagram_export_manager')
        Application.get_service('main_window')


# vim:sw=4:et:ai
