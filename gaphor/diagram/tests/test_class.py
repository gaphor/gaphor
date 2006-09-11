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
        diagram = UML.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=UML.create(UML.Class))

        self.assertEqual(2, len(klass._compartments))
        self.assertEqual(0, len(klass._compartments[0]))
        self.assertEqual(0, len(klass._compartments[1]))
        self.assertEqual((10, 10), klass._compartments[0].get_size())
        
        diagram.canvas.update()

        self.assertEqual((10, 10), klass._compartments[0].get_size())
        self.assertEqual(55, float(klass.min_height)) # 35 + 2 * 10
        self.assertEqual(10, float(klass.min_width))

        attr = UML.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        diagram.canvas.update()
        self.assertEqual(1, len(klass._compartments[0]))
        self.assertEqual((43.0, 18.0), klass._compartments[0].get_size())

        oper = UML.create(UML.Operation)
        oper.name = 'method'
        klass.subject.ownedOperation = oper

        diagram.canvas.update()
        self.assertEqual(1, len(klass._compartments[1]))
        self.assertEqual((43.0, 18.0), klass._compartments[0].get_size())

    def test_editable(self):
        """Test classifier editor
        """
        diagram = UML.create(UML.Diagram)
        klass = diagram.create(ClassItem, subject=UML.create(UML.Class))
        klass.subject.name = 'Class1'

        diagram.canvas.update()

        attr = UML.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        oper = UML.create(UML.Operation)
        oper.name = 'method'
        klass.subject.ownedOperation = oper

        diagram.canvas.update()

        edit = IEditor(klass)

        self.assertEqual('ClassifierItemEditor', edit.__class__.__name__)

        self.assertEqual(True, edit.is_editable(10, 10))

        # Test the inner working of the editor
        self.assertEqual(klass, edit._edit)
        self.assertEqual('Class1', edit.get_text())

        # The attribute:
        y = klass.NAME_COMPARTMENT_HEIGHT + 8 
        self.assertEqual(True, edit.is_editable(30, y))
        self.assertEqual(attr, edit._edit.subject)
        self.assertEqual('+ blah', edit.get_text())

        y += klass.compartments[0].height
        # The operation
        self.assertEqual(True, edit.is_editable(30, y))
        self.assertEqual(oper, edit._edit.subject)
        self.assertEqual('+ method()', edit.get_text())

