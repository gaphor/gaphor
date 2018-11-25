from builtins import range
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items
from gaphor.core import transactional


class UndoTest(TestCase):

    services = TestCase.services + ["undo_manager"]

    def test_class_association_undo_redo(self):
        factory = self.element_factory
        undo_manager = self.get_service("undo_manager")

        self.assertEqual(0, len(self.diagram.canvas.solver.constraints))

        ci1 = self.create(items.ClassItem, UML.Class)
        self.assertEqual(2, len(self.diagram.canvas.solver.constraints))

        ci2 = self.create(items.ClassItem, UML.Class)
        self.assertEqual(4, len(self.diagram.canvas.solver.constraints))

        a = self.create(items.AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        # Diagram, Association, 2x Class, Property, LiteralSpecification
        self.assertEqual(6, len(factory.lselect()))
        self.assertEqual(6, len(self.diagram.canvas.solver.constraints))

        @transactional
        def delete_class():
            ci2.unlink()

        undo_manager.clear_undo_stack()
        self.assertFalse(undo_manager.can_undo())

        delete_class()

        self.assertTrue(undo_manager.can_undo())

        self.assertEqual(ci1, self.get_connected(a.head))
        self.assertEqual(None, self.get_connected(a.tail))

        for i in range(3):
            # Diagram, Class
            # self.assertEqual(2, len(factory.lselect()), factory.lselect())

            self.assertEqual(3, len(self.diagram.canvas.solver.constraints))

            undo_manager.undo_transaction()

            self.assertEqual(6, len(self.diagram.canvas.solver.constraints))

            self.assertEqual(ci1, self.get_connected(a.head))
            self.assertEqual(ci2, self.get_connected(a.tail))

            undo_manager.redo_transaction()


# vim:sw=4:et:ai
