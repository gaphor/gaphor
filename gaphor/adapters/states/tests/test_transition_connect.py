"""
Test transition item and state vertices connections.
"""

from gaphor.tests import TestCase
from zope import component
from gaphor import UML
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect

class TransitionConnectorTestCase(TestCase):

    services = TestCase.services

    def test_vertex_connect(self):
        """Test transition to state vertex connection
        """
        v1 = self.create(items.StateItem, UML.State)
        v2 = self.create(items.StateItem, UML.State)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect vertices with transition
        self.connect(t, t.head, v1)
        self.connect(t, t.tail, v2)

        self.assertTrue(t.subject is not None)

        self.assertEqual(1, len(self.kindof(UML.Transition)))

        self.assertEqual(t.subject, v1.subject.outgoing[0])
        self.assertEqual(t.subject, v2.subject.incoming[0])
        self.assertEqual(t.subject.source, v1.subject)
        self.assertEqual(t.subject.target, v2.subject)


    def test_vertex_reconnect(self):
        """Test transition to state vertex reconnection
        """
        v1 = self.create(items.StateItem, UML.State)
        v2 = self.create(items.StateItem, UML.State)
        v3 = self.create(items.StateItem, UML.State)

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
        self.assertEqual(1, len(self.kindof(UML.Transition)))

        self.assertEqual(t.subject, v1.subject.outgoing[0])
        self.assertEqual(t.subject, v3.subject.incoming[0])
        self.assertEqual(t.subject.source, v1.subject)
        self.assertEqual(t.subject.target, v3.subject)

        self.assertEqual(0, len(v2.subject.incoming))
        self.assertEqual(0, len(v2.subject.outgoing))


    def test_vertex_disconnect(self):
        """Test transition and state vertices disconnection
        """
        t = self.create(items.TransitionItem)
        v1 = self.create(items.StateItem, UML.State)
        v2 = self.create(items.StateItem, UML.State)

        self.connect(t, t.head, v1)
        self.connect(t, t.tail, v2)
        assert t.subject is not None

        self.assertEqual(1, len(self.kindof(UML.Transition)))

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
        v1 = self.create(items.InitialPseudostateItem, UML.Pseudostate)
        v2 = self.create(items.StateItem, UML.State)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect head of transition to an initial pseudostate
        self.connect(t, t.head, v1)
        self.assertTrue(t.subject is None)

        # connect tail of transition to a state
        self.connect(t, t.tail, v2)
        self.assertTrue(t.subject is not None)

        self.assertEqual(1, len(self.kindof(UML.Transition)))

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
        v1 = self.create(items.InitialPseudostateItem, UML.Pseudostate)
        v2 = self.create(items.StateItem, UML.State)

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
        v1 = self.create(items.InitialPseudostateItem, UML.Pseudostate)
        t = self.create(items.TransitionItem)
        assert t.subject is None

        # no tail connection should be possible
        glued = self.allow(t, t.tail, v1)
        self.assertFalse(glued)


    def test_final_state_connect(self):
        """Test transition to final state connection
        """
        v1 = self.create(items.StateItem, UML.State)
        v2 = self.create(items.FinalStateItem, UML.FinalState)
        t = self.create(items.TransitionItem)

        # connect head of transition to a state
        self.connect(t, t.head, v1)

        # check if transition can connect to final state
        glued = self.allow(t, t.tail, v2)
        self.assertTrue(glued)
        # and connect tail of transition to final state
        self.connect(t, t.tail, v2)
        self.assertTrue(t.subject is not None)

        self.assertEqual(1, len(self.kindof(UML.Transition)))

        self.assertEqual(t.subject, v1.subject.outgoing[0])
        self.assertEqual(t.subject, v2.subject.incoming[0])
        self.assertEqual(t.subject.source, v1.subject)
        self.assertEqual(t.subject.target, v2.subject)


    def test_final_state_head_glue(self):
        """Test transition head to final state connection
        """
        v = self.create(items.FinalStateItem, UML.FinalState)
        t = self.create(items.TransitionItem)

        glued = self.allow(t, t.head, v)
        self.assertFalse(glued)


# vim:sw=4:et:ai
