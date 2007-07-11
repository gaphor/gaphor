"""
Test classes.
"""

import unittest

from gaphor import UML
from gaphor.diagram.interface import InterfaceItem

import gaphor.adapters


class ClassTestCase(unittest.TestCase):

    def setUp(self):
        self.element_factory = UML.ElementFactory()

    def tearDown(self):
        #self.element_factory.flush()
        #assert len(self.element_factory.lselect()) == 0
        pass

    def test_interface(self):
        diagram = self.element_factory.create(UML.Diagram)
        klass = diagram.create(InterfaceItem, subject=self.element_factory.create(UML.Class))
        klass.subject.name = 'Interface1'

    def test_folding(self):
        diagram = self.element_factory.create(UML.Diagram)
        klass = diagram.create(InterfaceItem, subject=self.element_factory.create(UML.Class))
        klass.subject.name = 'Interface1'
        assert klass.style.name_outside == False
        klass.drawing_style = klass.DRAW_ICON
        assert klass.drawing_style == klass.DRAW_ICON
        #assert klass.style.name_outside == True
        #from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM
        #assert klass.style.name_align == (ALIGN_CENTER, ALIGN_BOTTOM)

# vim:sw=4:et:ai
