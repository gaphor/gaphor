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
"""
Test transition item and state vertices connections.
"""

from __future__ import absolute_import
from gaphor.tests import TestCase
from gaphor.UML import uml2
from gaphor.diagram import items

class TransitionConnectorTestCase(TestCase):

    services = TestCase.services

    def test_vertex_connect(self):
        """Test transition to state vertex connection
        """
        v1 = self.create(items.StateItem, uml2.State)
        v2 = self.create(items.StateItem, uml2.State)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect vertices with transition
        self.connect(t, t.head, v1)
        self.connect(t, t.tail, v2)
        
        self.assertTrue(t.subject is not None)

        self.assertEquals(1, len(self.kindof(uml2.Transition)))
        
        self.assertEquals(t.subject, v1.subject.outgoing[0])
        self.assertEquals(t.subject, v2.subject.incoming[0])
        self.assertEquals(t.subject.source, v1.subject)
        self.assertEquals(t.subject.target, v2.subject)


    def test_vertex_reconnect(self):
        """Test transition to state vertex reconnection
        """
        v1 = self.create(items.StateItem, uml2.State)
        v2 = self.create(items.StateItem, uml2.State)
        v3 = self.create(items.StateItem, uml2.State)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect: v1 -> v2
        self.connect(t, t.head, v1)
        self.connect(t, t.tail, v2)

        s = t.subject
        s.name = 'tname'
        s.guard.specification = 'tguard'

        # reconnect: v1 -> v3
        self.connect(t, t.tail, v3)
        
        self.assertSame(s, t.subject)
        self.assertEquals(1, len(self.kindof(uml2.Transition)))
        
        self.assertEquals(t.subject, v1.subject.outgoing[0])
        self.assertEquals(t.subject, v3.subject.incoming[0])
        self.assertEquals(t.subject.source, v1.subject)
        self.assertEquals(t.subject.target, v3.subject)

        self.assertEquals(0, len(v2.subject.incoming))
        self.assertEquals(0, len(v2.subject.outgoing))


    def test_vertex_disconnect(self):
        """Test transition and state vertices disconnection
        """
        t = self.create(items.TransitionItem)
        v1 = self.create(items.StateItem, uml2.State)
        v2 = self.create(items.StateItem, uml2.State)

        self.connect(t, t.head, v1)
        self.connect(t, t.tail, v2)
        assert t.subject is not None

        self.assertEquals(1, len(self.kindof(uml2.Transition)))
        
        # test preconditions
        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]

        self.disconnect(t, t.tail)
        self.assertTrue(t.subject is None)

        self.disconnect(t, t.head)
        self.assertTrue(t.subject is None)


    def test_initial_pseudostate_connect(self):
        """Test transition and initial pseudostate connection
        """
        v1 = self.create(items.InitialPseudostateItem, uml2.Pseudostate)
        v2 = self.create(items.StateItem, uml2.State)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect head of transition to an initial pseudostate
        self.connect(t, t.head, v1)
        self.assertTrue(t.subject is None)

        # connect tail of transition to a state
        self.connect(t, t.tail, v2)
        self.assertTrue(t.subject is not None)

        self.assertEquals(1, len(self.kindof(uml2.Transition)))
        
        # test preconditions
        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]

        # we should not be able to connect two transitions to initial
        # pseudostate
        t2 = self.create(items.TransitionItem)
        # connection to `t2` should not be possible as v1 is already connected
        # to `t`
        glued = self.allow(t2, t2.head, v1)
        self.assertFalse(glued)
        self.assertTrue(self.get_connected(t2.head) is None)


    def test_initial_pseudostate_disconnect(self):
        """Test transition and initial pseudostate disconnection
        """
        v1 = self.create(items.InitialPseudostateItem, uml2.Pseudostate)
        v2 = self.create(items.StateItem, uml2.State)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect head of transition to an initial pseudostate
        self.connect(t, t.head, v1)
        self.assertTrue(self.get_connected(t.head))

        # perform the test
        self.disconnect(t, t.head)
        self.assertFalse(self.get_connected(t.head))


    def test_initial_pseudostate_tail_glue(self):
        """Test transition tail and initial pseudostate glueing
        """
        v1 = self.create(items.InitialPseudostateItem, uml2.Pseudostate)
        t = self.create(items.TransitionItem)
        assert t.subject is None

        # no tail connection should be possible
        glued = self.allow(t, t.tail, v1)
        self.assertFalse(glued)


    def test_final_state_connect(self):
        """Test transition to final state connection
        """
        v1 = self.create(items.StateItem, uml2.State)
        v2 = self.create(items.FinalStateItem, uml2.FinalState)
        t = self.create(items.TransitionItem)

        # connect head of transition to a state
        self.connect(t, t.head, v1)

        # check if transition can connect to final state
        glued = self.allow(t, t.tail, v2)
        self.assertTrue(glued)
        # and connect tail of transition to final state
        self.connect(t, t.tail, v2)
        self.assertTrue(t.subject is not None)

        self.assertEquals(1, len(self.kindof(uml2.Transition)))
        
        self.assertEquals(t.subject, v1.subject.outgoing[0])
        self.assertEquals(t.subject, v2.subject.incoming[0])
        self.assertEquals(t.subject.source, v1.subject)
        self.assertEquals(t.subject.target, v2.subject)


    def test_final_state_head_glue(self):
        """Test transition head to final state connection
        """
        v = self.create(items.FinalStateItem, uml2.FinalState)
        t = self.create(items.TransitionItem)

        glued = self.allow(t, t.head, v)
        self.assertFalse(glued)


# vim:sw=4:et:ai
