"""
Unit tests for simple items.
"""

from __future__ import absolute_import
from gaphor.tests import TestCase
from gaphor.diagram.simpleitem import Line, Box, Ellipse
from gaphas import View


class SimpleItemTestCase(TestCase):

    def setUp(self):
        super(SimpleItemTestCase, self).setUp()
        self.view = View(self.diagram.canvas)

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
