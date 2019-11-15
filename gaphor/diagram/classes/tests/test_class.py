"""
Test classes.
"""

from gaphas.canvas import instant_cairo_context

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.tests.testcase import TestCase


def compartments(item):
    return item.shape.children[1:]


class ClassTestCase(TestCase):
    def test_compartments(self):
        """
        Test creation of classes and working of compartments
        """
        element_factory = self.element_factory
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

        assert 2 == len(compartments(klass))
        assert 0 == len(compartments(klass)[0].children)
        assert 0 == len(compartments(klass)[1].children)
        # assert (10, 10) == klass._compartments[0].get_size()

        diagram.canvas.update()

        # assert (10, 10) == klass._compartments[0].get_size()
        assert 54 == float(klass.min_height)  # min_height
        assert 100 == float(klass.min_width)

        attr = element_factory.create(UML.Property)
        attr.name = 4 * "x"  # about 44 pixels
        klass.subject.ownedAttribute = attr

        diagram.canvas.update()
        assert 1 == len(compartments(klass)[0])
        assert compartments(klass)[0].size(instant_cairo_context()) > (44.0, 20.0)

        oper = element_factory.create(UML.Operation)
        oper.name = 4 * "x"  # about 44 pixels
        klass.subject.ownedOperation = oper

        oper = element_factory.create(UML.Operation)
        oper.name = 6 * "x"  # about 66 pixels
        klass.subject.ownedOperation = oper

        diagram.canvas.update()
        assert 2 == len(compartments(klass)[1])
        assert compartments(klass)[1].size(instant_cairo_context()) > (63.0, 34.0)

    def test_attribute_removal(self):

        element_factory = self.element_factory
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        diagram.canvas.update()

        attr = element_factory.create(UML.Property)
        attr.name = "blah1"
        klass.subject.ownedAttribute = attr

        attr2 = element_factory.create(UML.Property)
        attr2.name = "blah2"
        klass.subject.ownedAttribute = attr2

        attr = element_factory.create(UML.Property)
        attr.name = "blah3"
        klass.subject.ownedAttribute = attr

        assert 3 == len(compartments(klass)[0])

        attr2.unlink()

        assert 2 == len(compartments(klass)[0])

    def test_compartment_resizing(self):
        element_factory = self.element_factory
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        klass.subject.name = "Class1"

        diagram.canvas.update()

        attr = element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        oper = element_factory.create(UML.Operation)
        oper.name = "method"
        klass.subject.ownedOperation = oper

        assert 100 == klass.width

        attr.name = "x" * 25

        diagram.canvas.update()

        width = klass.width
        assert width >= 170.0
