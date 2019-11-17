"""
Extension item connection adapter tests.
"""

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.profiles.extension import ExtensionItem
from gaphor.tests import TestCase


class ExtensionConnectorTestCase(TestCase):
    """
    Extension item connection adapter tests.
    """

    def test_class_glue(self):
        """Test extension item gluing to a class."""

        ext = self.create(ExtensionItem)
        cls = self.create(ClassItem, UML.Class)

        # cannot connect extension item tail to a class
        glued = self.allow(ext, ext.tail, cls)
        assert not glued

    def test_stereotype_glue(self):
        """Test extension item gluing to a stereotype."""

        ext = self.create(ExtensionItem)
        st = self.create(ClassItem, UML.Stereotype)

        # test precondition
        assert isinstance(st.subject, UML.Stereotype)

        # can connect extension item head to a Stereotype UML metaclass,
        # because it derives from Class UML metaclass
        glued = self.allow(ext, ext.head, st)
        assert glued

    def test_glue(self):
        """Test extension item glue
        """
        ext = self.create(ExtensionItem)
        st = self.create(ClassItem, UML.Stereotype)
        cls = self.create(ClassItem, UML.Class)

        glued = self.allow(ext, ext.tail, st)
        assert glued

        self.connect(ext, ext.tail, st)

        glued = self.allow(ext, ext.head, cls)
        assert glued

    def test_connection(self):
        """Test extension item connection
        """
        ext = self.create(ExtensionItem)
        st = self.create(ClassItem, UML.Stereotype)
        cls = self.create(ClassItem, UML.Class)

        self.connect(ext, ext.tail, st)
        self.connect(ext, ext.head, cls)
