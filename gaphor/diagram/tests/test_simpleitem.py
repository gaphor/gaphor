"""
Unnit tests for simple items.
"""

import unittest

from gaphor import UML
from gaphor.diagram.simpleitem import Line, Box, Ellipse
from gaphas import View


class SimpleItemTestCase(unittest.TestCase):

    def setUp(self):
        self.diagram = diagram = UML.ElementFactory().create(UML.Diagram)
        self.view = View(diagram.canvas)

    def tearDown(self):
        pass

    def test_line(self):
        """
        """
        self.diagram.create(Line)
        
    def test_box(self):
        """
        """
        self.diagram.create(Line)

    def test_ellipse(self):
        """
        """
        self.diagram.create(Ellipse)


# vim:sw=4:et:ai
