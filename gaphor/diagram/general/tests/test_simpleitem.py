"""Unit tests for simple items."""

from gaphas import View

from gaphor.diagram.general.simpleitem import Ellipse, Line
from gaphor.tests import TestCase


class SimpleItemTestCase(TestCase):
    def setUp(self):
        super().setUp()
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
