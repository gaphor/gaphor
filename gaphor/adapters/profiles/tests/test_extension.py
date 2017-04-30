"""
Extension item connection adapter tests.
"""

from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests import TestCase


class ExtensionConnectorTestCase(TestCase):
    """
    Extension item connection adapter tests.
    """

    def test_class_glue(self):
        """Test extension item glueing to a class
        """
        ext = self.create(items.ExtensionItem)
        cls = self.create(items.ClassItem, uml2.Class)

        # cannot connect extension item tail to a class
        glued = self.allow(ext, ext.tail, cls)
        self.assertFalse(glued)

    def test_stereotype_glue(self):
        """Test extension item glueing to a stereotype
        """
        ext = self.create(items.ExtensionItem)
        st = self.create(items.ClassItem, uml2.Stereotype)

        # test precondition
        assert type(st.subject) is uml2.Stereotype

        # can connect extension item head to a Stereotype UML metaclass,
        # because it derives from Class UML metaclass
        glued = self.allow(ext, ext.head, st)
        self.assertTrue(glued)

    def test_glue(self):
        """Test extension item glue
        """
        ext = self.create(items.ExtensionItem)
        st = self.create(items.ClassItem, uml2.Stereotype)
        cls = self.create(items.ClassItem, uml2.Class)

        glued = self.allow(ext, ext.tail, st)
        self.assertTrue(glued)

        self.connect(ext, ext.tail, st)

        glued = self.allow(ext, ext.head, cls)
        self.assertTrue(glued)

    def test_connection(self):
        """Test extension item connection
        """
        ext = self.create(items.ExtensionItem)
        st = self.create(items.ClassItem, uml2.Stereotype)
        cls = self.create(items.ClassItem, uml2.Class)

        self.connect(ext, ext.tail, st)
        self.connect(ext, ext.head, cls)
