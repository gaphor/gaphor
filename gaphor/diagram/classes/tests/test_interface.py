"""
Test classes.
"""

from zope import component
from gaphor.tests.testcase import TestCase
from gaphor import UML
from gaphor.diagram.interfaces import IConnect
from gaphor.diagram.classes.interface import InterfaceItem
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.classes.dependency import DependencyItem
from gaphor.diagram.classes.implementation import ImplementationItem


class ClassTestCase(TestCase):

    services = [ 'element_factory', 'adapter_loader' ]

    def test_interface(self):
        diagram = self.element_factory.create(UML.Diagram)
        klass = diagram.create(InterfaceItem, subject=self.element_factory.create(UML.Class))
        klass.subject.name = 'Interface1'

    def test_folding(self):
        diagram = self.element_factory.create(UML.Diagram)
        klass = diagram.create(InterfaceItem, subject=self.element_factory.create(UML.Interface))
        klass.subject.name = 'Interface1'
        assert klass.style.name_outside == False
        klass.drawing_style = klass.DRAW_ICON
        assert klass.drawing_style == klass.DRAW_ICON
        #assert klass.style.name_outside == True
        #from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM
        #assert klass.style.name_align == (ALIGN_CENTER, ALIGN_BOTTOM)

    def test_folding_required_provided(self):

        class1 = self.create(ClassItem, UML.Class)
        class2 = self.create(ClassItem, UML.Class)

        item = self.create(InterfaceItem, UML.Interface)
        item.folded = True
        assert item.drawing_style == item.DRAW_ICON
        assert not item._draw_required
        assert not item._draw_provided

        # Connect Usage dependency: should result in required interface

        usage = self.create(DependencyItem, UML.Usage)
        adapter = component.queryMultiAdapter((class1, usage), IConnect)
        adapter.connect(usage.tail)

        adapter = component.queryMultiAdapter((item, usage), IConnect)
        adapter.connect(usage.head)

        assert item.subject.supplierDependency, item.subject.supplierDependency
        assert usage.head.connected_to is item
        assert item._draw_required
        assert not item._draw_provided

        # TODO: check drawing state of dependency
        
        # Connect Implementation: should result in provided interface

        impl = self.create(ImplementationItem, UML.Implementation)
        adapter = component.queryMultiAdapter((class2, impl), IConnect)
        adapter.connect(impl.tail)

        adapter = component.queryMultiAdapter((item, impl), IConnect)
        adapter.connect(impl.head)

        assert item.subject in impl.subject.contract
        assert usage.head.connected_to is item
        assert item._draw_required
        assert item._draw_provided

# vim:sw=4:et:ai
