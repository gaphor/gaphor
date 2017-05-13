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

from gaphor.UML import uml2
from gaphor.diagram.items import FlowItem, ActionItem
from gaphor.storage import storage
from gaphor.tests import TestCase


class ActionIssueTestCase(TestCase):
    def test_it(self):
        """
        Test an issue when loading a freshly created action diagram.
        """
        ef = self.element_factory
        storage.load('test-diagrams/action-issue.gaphor', ef)

        actions = ef.lselect(lambda e: e.isKindOf(uml2.Action))
        flows = ef.lselect(lambda e: e.isKindOf(uml2.ControlFlow))
        self.assertEqual(3, len(actions))
        self.assertEqual(3, len(flows))

        # Actions live in partitions:
        partitions = ef.lselect(lambda e: e.isKindOf(uml2.ActivityPartition))
        self.assertEquals(2, len(partitions))

        # Okay, so far the data model is saved correctly. Now, how do the
        # handles behave?
        diagrams = ef.lselect(lambda e: e.isKindOf(uml2.Diagram))
        self.assertEquals(1, len(diagrams))

        canvas = diagrams[0].canvas
        assert 9 == len(canvas.get_all_items())
        # Part, Part, Act, Act, Part, Act, Flow, Flow, Flow

        for e in actions + flows:
            self.assertEquals(1, len(e.presentation), e)
        for i in canvas.select(lambda e: isinstance(e, (FlowItem, ActionItem))):
            self.assertTrue(i.subject, i)

        # Loaded as:
        # 
        # actions[1] --> flows[0, 1]
        # flows[0, 2] --> actions[0]
        # flows[1] --> actions[2] --> flows[2]

        # start element:
        self.assertSame(actions[1].outgoing[0], flows[0])
        self.assertSame(actions[1].outgoing[1], flows[1])
        self.assertFalse(actions[1].incoming)

        cinfo, = canvas.get_connections(handle=flows[0].presentation[0].head)
        self.assertSame(cinfo.connected, actions[1].presentation[0])
        cinfo, = canvas.get_connections(handle=flows[1].presentation[0].head)
        self.assertSame(cinfo.connected, actions[1].presentation[0])

        # Intermediate element:
        self.assertSame(actions[2].incoming[0], flows[1])
        self.assertSame(actions[2].outgoing[0], flows[2])

        cinfo, = canvas.get_connections(handle=flows[1].presentation[0].tail)
        self.assertSame(cinfo.connected, actions[2].presentation[0])
        cinfo, = canvas.get_connections(handle=flows[2].presentation[0].head)
        self.assertSame(cinfo.connected, actions[2].presentation[0])

        # Final element:
        self.assertSame(actions[0].incoming[0], flows[0])
        self.assertSame(actions[0].incoming[1], flows[2])

        cinfo, = canvas.get_connections(handle=flows[0].presentation[0].tail)
        self.assertSame(cinfo.connected, actions[0].presentation[0])
        cinfo, = canvas.get_connections(handle=flows[2].presentation[0].tail)
        self.assertSame(cinfo.connected, actions[0].presentation[0])

        # Test the parent-child connectivity
        for a in actions:
            p, = a.inPartition
            self.assertTrue(p)
            self.assertTrue(canvas.get_parent(a.presentation[0]))
            self.assertSame(canvas.get_parent(a.presentation[0]), p.presentation[0])

# vim:sw=4:et:ai
