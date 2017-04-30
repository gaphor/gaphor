"""
Unit tests for simple items.
"""

from __future__ import absolute_import

from gaphas import View

from gaphor.diagram.simpleitem import Line, Ellipse
from gaphor.tests import TestCase


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
