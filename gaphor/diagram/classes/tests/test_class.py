"""
Test classes.
"""

from gaphor import UML
from gaphor.tests.testcase import TestCase
from gaphor.diagram.classes.klass import ClassItem


class ClassTestCase(TestCase):
    def test_compartments(self):
        """
        Test creation of classes and working of compartments
        """
        element_factory = self.element_factory
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

        assert 2 == len(klass._compartments)
        assert 0 == len(klass._compartments[0])
        assert 0 == len(klass._compartments[1])
        assert (10, 10) == klass._compartments[0].get_size()

        diagram.canvas.update()

        assert (10, 10) == klass._compartments[0].get_size()
        assert 50 == float(klass.min_height)  # min_height
        assert 100 == float(klass.min_width)

        attr = element_factory.create(UML.Property)
        attr.name = 4 * "x"  # about 44 pixels
        klass.subject.ownedAttribute = attr

        diagram.canvas.update()
        assert 1 == len(klass._compartments[0])
        assert klass._compartments[0].get_size() > (44.0, 20.0)

        oper = element_factory.create(UML.Operation)
        oper.name = 4 * "x"  # about 44 pixels
        klass.subject.ownedOperation = oper

        oper = element_factory.create(UML.Operation)
        oper.name = 6 * "x"  # about 66 pixels
        klass.subject.ownedOperation = oper

        diagram.canvas.update()
        assert 2 == len(klass._compartments[1])
        assert klass._compartments[1].get_size() > (63.0, 34.0)

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

        diagram.canvas.update()
        assert 3 == len(klass._compartments[0])

        attr2.unlink()

        diagram.canvas.update()
        assert 2 == len(klass._compartments[0])

    def test_item_at(self):
        """
        Test working of item_at method
        """
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

        diagram.canvas.update()

        assert len(klass.compartments[0]) == 1
        assert len(klass.compartments[1]) == 1

        name_size = klass._header_size
        assert klass.item_at(10, 10) is klass
        assert klass.item_at(name_size[0] - 1, name_size[1] - 1) is klass

        padding = klass.style.compartment_padding
        vspacing = klass.style.compartment_vspacing
        x = padding[-1] + 1
        y = name_size[1] + padding[0] + 2
        assert klass.item_at(x, y) is not None, klass.item_at(x, y)
        assert klass.item_at(x, y).subject is attr, klass.item_at(x, y).subject

        y = name_size[1] + klass.compartments[0].height + padding[0] + 2
        assert klass.item_at(x, y) is not None, klass.item_at(x, y)
        assert klass.item_at(x, y).subject is oper, klass.item_at(x, y).subject

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
        assert width > 170.0
