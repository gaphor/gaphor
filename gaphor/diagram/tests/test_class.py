"""
Test classes.
"""

import unittest

from gaphor import UML
from gaphor.diagram.klass import ClassItem
from gaphor.diagram.interfaces import IEditor

import gaphor.adapters


class ClassTestCase(unittest.TestCase):

    def test_compartments(self):
        """Test creation of classes and working of compartments.
        """
        element_factory = UML.ElementFactory()
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

        self.assertEqual(2, len(klass._compartments))
        self.assertEqual(0, len(klass._compartments[0]))
        self.assertEqual(0, len(klass._compartments[1]))
        self.assertEqual((10, 10), klass._compartments[0].get_size())
        
        diagram.canvas.update()

        self.assertEqual((10, 10), klass._compartments[0].get_size())
        self.assertEqual(20, float(klass.min_height)) # 2 * 10
        self.assertEqual(20, float(klass.min_width))

        attr = element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        diagram.canvas.update()
        self.assertEqual(1, len(klass._compartments[0]))
        self.assertEqual((43.0, 18.0), klass._compartments[0].get_size())

        oper = element_factory.create(UML.Operation)
        oper.name = 'method'
        klass.subject.ownedOperation = oper

        diagram.canvas.update()
        self.assertEqual(1, len(klass._compartments[1]))
        self.assertEqual((43.0, 18.0), klass._compartments[0].get_size())

    def test_item_at(self):
        """
        Test working of item_at method.
        """
        element_factory = UML.ElementFactory()
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        klass.subject.name = 'Class1'

        diagram.canvas.update()

        attr = element_factory.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        oper = element_factory.create(UML.Operation)
        oper.name = 'method'
        klass.subject.ownedOperation = oper

        diagram.canvas.update()

        assert len(klass.compartments[0]) == 1
        assert len(klass.compartments[1]) == 1

        name_size = klass.get_name_size()
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

# vim:sw=4:et:ai
