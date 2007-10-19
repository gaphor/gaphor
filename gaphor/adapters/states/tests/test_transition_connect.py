"""
Test transition item connections.
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

        v1 = self.create(items.StateItem)
        v2 = self.create(items.StateItem)

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
        
        assert t.subject.source == v1.subject.outgoing
        assert t.subject.target == v2.subject.incoming


    def test_vertex_connect(self):
        """Test transition and state vertices disconnection
        """
        factory = self.element_factory

        v1 = self.create(items.StateItem)
        v2 = self.create(items.StateItem)

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
        
        assert t.subject.source == v1.subject.outgoing
        assert t.subject.target == v2.subject.incoming

        adapter.disconnect(t.tail)
        assert t.subject is None

        adapter.disconnect(t.head)
        assert t.subject is None


# vim:sw=4:et:ai
