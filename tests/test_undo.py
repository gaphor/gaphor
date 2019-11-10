from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.classes import AssociationItem, ClassItem
from gaphor.tests import TestCase


class UndoTest(TestCase):

    services = TestCase.services + ["undo_manager"]

    def test_class_association_undo_redo(self):
        factory = self.element_factory
        undo_manager = self.get_service("undo_manager")

        assert 0 == len(self.diagram.canvas.solver.constraints)

        ci1 = self.create(ClassItem, UML.Class)
        assert 2 == len(self.diagram.canvas.solver.constraints)

        ci2 = self.create(ClassItem, UML.Class)
        assert 4 == len(self.diagram.canvas.solver.constraints)

        a = self.create(AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        # Diagram, Association, 2x Class, Property, LiteralSpecification
        self.assertEqual(6, len(factory.lselect()))
        assert 6 == len(self.diagram.canvas.solver.constraints)

        @transactional
        def delete_class():
            ci2.unlink()

        undo_manager.clear_undo_stack()
        assert not undo_manager.can_undo()

        delete_class()

        assert undo_manager.can_undo()

        assert ci1 == self.get_connected(a.head)
        assert None is self.get_connected(a.tail)

        for i in range(3):
            assert 3 == len(self.diagram.canvas.solver.constraints)

            undo_manager.undo_transaction()

            assert 6 == len(self.diagram.canvas.solver.constraints)

            assert ci1 == self.get_connected(a.head)
            assert ci2 == self.get_connected(a.tail)

            undo_manager.redo_transaction()
