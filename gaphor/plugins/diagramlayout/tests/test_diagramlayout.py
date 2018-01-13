#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.application import Application
from gaphor.tests.testcase import TestCase


class DiagramLayoutTestCase(TestCase):

    services = TestCase.services + ['main_window', 'ui_manager', 'properties', 'action_manager', 'diagram_layout']


    def testDiagramLayout(self):
        elemfact = Application.get_service('element_factory')
        diagram_layout = Application.get_service('diagram_layout')

        diagram = elemfact.create(uml2.Diagram)
        c1 = diagram.create(items.ClassItem, subject=elemfact.create(uml2.Class))
        c2 = diagram.create(items.ClassItem, subject=elemfact.create(uml2.Class))

        c2.matrix.translate(100, 100)
        c2.request_update()

        diagram_layout.layout_diagram(diagram)



# vim:sw=4:et:ai
