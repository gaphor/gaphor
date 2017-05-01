from __future__ import absolute_import

from six.moves import range

from gaphor.UML import uml2
from gaphor.core import transactional
from gaphor.diagram import items
from gaphor.tests import TestCase


class UndoTest(TestCase):
    services = TestCase.services + ['undo_manager']

    def test_class_association_undo_redo(self):
        factory = self.element_factory
        undo_manager = self.get_service('undo_manager')

        ci1 = self.create(items.ClassItem, uml2.Class)
        self.assertEquals(6, len(self.diagram.canvas.solver.constraints))

        ci2 = self.create(items.ClassItem, uml2.Class)
        self.assertEquals(12, len(self.diagram.canvas.solver.constraints))

        a = self.create(items.AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        # Diagram, Association, 2x Class, Property, LiteralSpecification
        self.assertEquals(8, len(factory.lselect()))
        self.assertEquals(14, len(self.diagram.canvas.solver.constraints))

        @transactional
        def delete_class():
            ci2.unlink()

        undo_manager.clear_undo_stack()
        self.assertFalse(undo_manager.can_undo())

        delete_class()

        self.assertTrue(undo_manager.can_undo())

        self.assertEquals(ci1, self.get_connected(a.head))
        self.assertEquals(None, self.get_connected(a.tail))

        for i in range(3):
            # Diagram, Class
            # self.assertEquals(2, len(factory.lselect()), factory.lselect())

            self.assertEquals(7, len(self.diagram.canvas.solver.constraints))

            undo_manager.undo_transaction()

            self.assertEquals(14, len(self.diagram.canvas.solver.constraints))

            self.assertEquals(ci1, self.get_connected(a.head))
            self.assertEquals(ci2, self.get_connected(a.tail))

            undo_manager.redo_transaction()

# vim:sw=4:et:ai
