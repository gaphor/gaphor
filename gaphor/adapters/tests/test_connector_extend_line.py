"""
Test extend item connections.
"""

from gaphor.tests import TestCase
from zope import component
from gaphor import UML
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect

class ExtendItemTestCase(TestCase):

    services = ['element_factory', 'adapter_loader']

    def test_commentline_element(self):
        """
        Test Extend item connecting to use cases.
        """
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        uc2 = self.create(items.UseCaseItem, UML.UseCase)
        extend = self.create(items.ExtendItem)

        adapter = component.queryMultiAdapter((uc1, extend), IConnect)

        handle = extend.head
        adapter.connect(handle)

        assert handle.connected_to is uc1

        adapter = component.queryMultiAdapter((uc2, extend), IConnect)

        handle = extend.tail
        adapter.connect(handle)

        assert handle.connected_to is uc2
        assert handle._connect_constraint is not None

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle._connect_constraint is None



# vim:sw=4:et:ai
