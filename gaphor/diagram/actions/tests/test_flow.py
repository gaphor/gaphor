#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase

class FlowTestCase(TestCase):

    def test_flow(self):
        self.create(items.FlowItem, uml2.ControlFlow)


    def test_name(self):
        """
        Test updating of flow name text.
        """
        flow = self.create(items.FlowItem, uml2.ControlFlow)
        flow.subject.name = 'Blah'

        self.assertEquals('Blah', flow._name.text)

        flow.subject = None

        self.assertEquals('', flow._name.text)


    def test_guard(self):
        """
        Test updating of flow guard text.
        """
        flow = self.create(items.FlowItem, uml2.ControlFlow)

        self.assertEquals('', flow._guard.text)

        flow.subject.guard = 'GuardMe'
        self.assertEquals('GuardMe', flow._guard.text)

        flow.subject = None
        self.assertEquals('', flow._guard.text)


    def test_persistence(self):
        """
        TODO: Test connector item saving/loading
        """
        pass



# vim:sw=4:et:ai
