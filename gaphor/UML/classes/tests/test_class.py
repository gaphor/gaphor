"""Test classes."""

from gaphor import UML
from gaphor.core.modeling import UpdateContext
from gaphor.core.modeling.diagram import FALLBACK_STYLE
from gaphor.tests.testcase import TestCase
from gaphor.UML.classes.klass import ClassItem


def compartments(item):
    return item.shape.children[1:]


def context():
    return UpdateContext(style=FALLBACK_STYLE)


class ClassTestCase(TestCase):
    def test_compartments(self):
        """Test creation of classes and working of compartments."""
        element_factory = self.element_factory
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

        assert 2 == len(compartments(klass))
        assert 0 == len(compartments(klass)[0].children)
        assert 0 == len(compartments(klass)[1].children)

        diagram.update_now((klass,))

        assert 54 == float(klass.min_height)  # min_height
        assert 100 == float(klass.min_width)

        attr = element_factory.create(UML.Property)
        attr.name = 4 * "x"  # about 44 pixels
        klass.subject.ownedAttribute = attr

        diagram.update_now((klass,))

        assert 1 == len(compartments(klass)[0])
        assert compartments(klass)[0].size(context()) > (44.0, 20.0)

        oper = element_factory.create(UML.Operation)
        oper.name = 4 * "x"  # about 44 pixels
        klass.subject.ownedOperation = oper

        oper = element_factory.create(UML.Operation)
        oper.name = 6 * "x"  # about 66 pixels
        klass.subject.ownedOperation = oper

        diagram.update_now((klass,))
        assert 2 == len(compartments(klass)[1])
        assert compartments(klass)[1].size(context()) > (63.0, 34.0)

    def test_attribute_removal(self):

        element_factory = self.element_factory
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        diagram.update_now((klass,))

        attr = element_factory.create(UML.Property)
        attr.name = "blah1"
        klass.subject.ownedAttribute = attr

        attr2 = element_factory.create(UML.Property)
        attr2.name = "blah2"
        klass.subject.ownedAttribute = attr2

        attr = element_factory.create(UML.Property)
        attr.name = "blah3"
        klass.subject.ownedAttribute = attr

        assert len(compartments(klass)[0]) == 3

        attr2.unlink()

        assert len(compartments(klass)[0]) == 2

    def test_compartment_resizing(self):
        element_factory = self.element_factory
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        klass.subject.name = "Class1"

        diagram.update_now((klass,))

        attr = element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        oper = element_factory.create(UML.Operation)
        oper.name = "method"
        klass.subject.ownedOperation = oper

        assert klass.width == 100

        attr.name = "x" * 25

        diagram.update_now((klass,))

        width = klass.width
        assert width >= 170.0
