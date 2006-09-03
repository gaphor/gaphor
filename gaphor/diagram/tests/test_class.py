"""
Test classes.
"""

import unittest

from gaphor import UML
from gaphor.diagram.klass import ClassItem


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
        self.assertEqual(40, float(klass.min_height))
        self.assertEqual(20, float(klass.min_width))

        attr = UML.create(UML.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        diagram.canvas.update()
        self.assertEqual(1, len(klass._compartments[0]))
        self.assertEqual((43.0, 18.0), klass._compartments[0].get_size())

    
