from gaphor.tests import TestCase

from gaphor import UML
from gaphor.core import transactional


class UndoRedoBugTestCase(TestCase):

    services = TestCase.services + ["undo_manager"]

    def setUp(self):
        super().setUp()
        self.undo_manager = self.get_service("undo_manager")

    @transactional
    def create_with_attribute(self):
        self.class_ = self.element_factory.create(UML.Class)
        self.attribute = self.element_factory.create(UML.Property)
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
        assert self.undo_manager.can_undo()

        self.undo_manager.undo_transaction()

        assert self.attribute in self.class_.ownedAttribute

        self.undo_manager.redo_transaction()


# vi:sw=4:et:ai
