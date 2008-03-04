"""
Test transition item and state vertices connections.
"""

from gaphor.tests import TestCase
from zope import component
from gaphor import UML
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect

class TransitionConnectorTestCase(TestCase):

    services = ['element_factory', 'adapter_loader']

    def test_vertex_connect(self):
        """Test transition to state vertex connection
        """
        factory = self.element_factory

        v1 = self.create(items.StateItem, UML.State)
        v2 = self.create(items.StateItem, UML.State)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        adapter = component.queryMultiAdapter((v1, t), IConnect)
        assert adapter is not None
        
        # connect head of transition to a state
        adapter.connect(t.head)
        assert t.subject is None

        adapter = component.queryMultiAdapter((v2, t), IConnect)
        assert adapter is not None

        # connect tail of transition to a second state
        adapter.connect(t.tail)
        assert t.subject is not None

        assert len(factory.lselect(lambda e: e.isKindOf(UML.Transition))) == 1
        
        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]
        assert t.subject.source == v1.subject
        assert t.subject.target == v2.subject


    def test_vertex_disconnect(self):
        """Test transition and state vertices disconnection
        """
        factory = self.element_factory

        v1 = self.create(items.StateItem, UML.State)
        v2 = self.create(items.StateItem, UML.State)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        adapter = component.queryMultiAdapter((v1, t), IConnect)
        assert adapter is not None
        
        # connect head of transition to a state
        adapter.connect(t.head)
        assert t.subject is None

        adapter = component.queryMultiAdapter((v2, t), IConnect)
        assert adapter is not None

        # connect tail of transition to a second state
        adapter.connect(t.tail)
        assert t.subject is not None

        assert len(factory.lselect(lambda e: e.isKindOf(UML.Transition))) == 1
        
        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]

        adapter.disconnect(t.tail)
        assert t.subject is None

        adapter.disconnect(t.head)
        assert t.subject is None


    def test_initial_pseudostate_connect(self):
        """Test transition and initial pseudostate connection
        """
        factory = self.element_factory

        v1 = self.create(items.InitialPseudostateItem, UML.Pseudostate)
        assert v1._connected == False # not connected
        v2 = self.create(items.StateItem, UML.State)
        assert v1.subject.kind == 'initial'

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect head of transition to an initial pseudostate
        adapter = component.queryMultiAdapter((v1, t), IConnect)
        assert adapter is not None
        adapter.connect(t.head)
        assert t.subject is None
        assert v1._connected == True # psuedostate connected

        # connect tail of transition to a state
        adapter = component.queryMultiAdapter((v2, t), IConnect)
        assert adapter is not None
        adapter.connect(t.tail)
        assert t.subject is not None

        assert len(factory.lselect(lambda e: e.isKindOf(UML.Transition))) == 1
        
        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]

        # we should not be able to connect two transitions to initial
        # pseudostate
        t2 = self.create(items.TransitionItem)
        adapter = component.queryMultiAdapter((v1, t2), IConnect)
        assert adapter is not None
        adapter.connect(t.head)
        # connection to `t2` should not be possible as v1 is already connected
        # to `t`
        assert t2.head.connected_to is None
        assert v1._connected == True # psuedostate remains connected


    def test_initial_pseudostate_disconnect(self):
        """Test transition and initial pseudostate disconnection
        """
        factory = self.element_factory

        v1 = self.create(items.InitialPseudostateItem, UML.Pseudostate)
        assert v1._connected == False # not connected
        v2 = self.create(items.StateItem, UML.State)
        assert v1.subject.kind == 'initial'

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect head of transition to an initial pseudostate
        adapter = component.queryMultiAdapter((v1, t), IConnect)
        assert adapter is not None
        adapter.connect(t.head)
        assert t.subject is None

        assert v1._connected == True # psuedostate connected

        adapter.disconnect(t.head)
        assert v1._connected == False # psuedostate disconnected


    def test_initial_pseudostate_tail_connect(self):
        """Test transition tail and initial pseudostate connection
        """
        factory = self.element_factory

        v1 = self.create(items.InitialPseudostateItem, UML.Pseudostate)
        assert v1._connected == False # not connected
        v2 = self.create(items.StateItem, UML.State)
        assert v1.subject.kind == 'initial'

        t = self.create(items.TransitionItem)
        assert t.subject is None

        # connect head of transition to an initial pseudostate
        adapter = component.queryMultiAdapter((v1, t), IConnect)
        assert adapter is not None
        adapter.connect(t.tail)
        assert t.tail.connected_to is None, 'no tail connection should be possible'
        assert v1._connected == False # psuedostate not connected


    def test_final_state_connect(self):
        """Test transition to final state connection
        """
        factory = self.element_factory

        v1 = self.create(items.StateItem, UML.State)
        v2 = self.create(items.FinalStateItem, UML.FinalState)

        t = self.create(items.TransitionItem)
        assert t.subject is None

        adapter = component.queryMultiAdapter((v1, t), IConnect)
        assert adapter is not None
        
        # connect head of transition to a state
        adapter.connect(t.head)
        assert t.subject is None

        adapter = component.queryMultiAdapter((v2, t), IConnect)
        assert adapter is not None

        # connect tail of transition to final state
        adapter.connect(t.tail)
        assert t.subject is not None

        assert len(factory.lselect(lambda e: e.isKindOf(UML.Transition))) == 1
        
        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]
        assert t.subject.source == v1.subject
        assert t.subject.target == v2.subject


    def test_final_state_head_connect(self):
        """Test transition head to final state connection
        """
        factory = self.element_factory

        v = self.create(items.FinalStateItem, UML.FinalState)
        t = self.create(items.TransitionItem)

        adapter = component.queryMultiAdapter((v, t), IConnect)
        assert adapter is not None

        # connect head of transition to final state
        adapter.connect(t.head)
        # no connection as only tail of transition can be connected
        assert t.head.connected_to is None


# vim:sw=4:et:ai
