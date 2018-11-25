"""
Formatting of UML model elements into text tests.
"""

import unittest

from gaphor.application import Application
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.umlfmt import format
import gaphor.UML.uml2 as UML

factory = ElementFactory()


class AttributeTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        factory.flush()

    def test_simple_format(self):
        """Test simple attribute formatting
        """
        a = factory.create(UML.Property)
        a.name = "myattr"
        self.assertEqual("+ myattr", format(a))

        a.typeValue = "int"
        self.assertEqual("+ myattr: int", format(a))
