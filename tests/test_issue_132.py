
from __future__ import absolute_import
from gaphor.tests import TestCase
from gaphor.ui.namespace import NamespaceModel
from gaphor.UML import uml2
from gaphor.core import transactional


class UndoRedoBugTestCase(TestCase):

    services = TestCase.services + ['undo_manager']

    def setUp(self):
        super(UndoRedoBugTestCase, self).setUp()
        self.undo_manager = self.get_service('undo_manager')
        self.namespace = NamespaceModel(self.element_factory)

    @transactional
    def create_with_attribute(self):
        self.class_ = self.element_factory.create(uml2.Class)
        self.attribute = self.element_factory.create(uml2.Property)
        self.class_.ownedAttribute = self.attribute

    # Fix:  Remove operation should be transactional ;)
    @transactional
    def remove_attribute(self):
        self.attribute.unlink()


    def test_bug_with_attribute(self):
        """
        Does not trigger the error.
        """
        self.create_with_attribute()
        assert len(self.class_.ownedAttribute) == 1
        assert self.attribute.namespace is self.class_, self.attribute.namespace

        self.remove_attribute()
        assert len(self.class_.ownedAttribute) == 0
        assert self.attribute.namespace is None

        self.undo_manager.undo_transaction()

        assert self.attribute in self.class_.ownedAttribute

        self.undo_manager.redo_transaction()


# vi:sw=4:et:ai
