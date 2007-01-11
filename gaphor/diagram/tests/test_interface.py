"""
Test classes.
"""

import unittest

from gaphor import UML
from gaphor.diagram.interface import InterfaceItem

import gaphor.adapters


class ClassTestCase(unittest.TestCase):

    def tearDown(self):
        UML.flush()
        assert len(UML.lselect()) == 0

    def test_interface(self):
        diagram = UML.create(UML.Diagram)
        klass = diagram.create(InterfaceItem, subject=UML.create(UML.Class))
        klass.subject.name = 'Interface1'

    def test_folding(self):
        diagram = UML.create(UML.Diagram)
        klass = diagram.create(InterfaceItem, subject=UML.create(UML.Class))
        klass.subject.name = 'Interface1'
        assert klass.style.name_outside == False
        klass.drawing_style = klass.DRAW_ICON
        assert klass.drawing_style == klass.DRAW_ICON
        assert klass.style.name_outside == True
        from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM
        assert klass.style.name_align == (ALIGN_CENTER, ALIGN_BOTTOM)

# vim:sw=4:et:ai
