"""
Formatting of UML model elements into text tests.
"""

from __future__ import absolute_import

import unittest

import gaphor.UML.uml2 as UML
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.umlfmt import format

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
        a.name = 'myattr'
        self.assertEquals('+ myattr', format(a))

        a.typeValue = 'int'
        self.assertEquals('+ myattr: int', format(a))
