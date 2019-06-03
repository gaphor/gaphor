from gaphor import UML
from gaphor.diagram.general import CommentItem
from gaphor.diagram.classes import AssociationItem, ClassItem
from gaphor.services.copyservice import CopyService
from gaphor.application import Application
from gaphor.tests.testcase import TestCase


class CopyServiceTestCase(TestCase):

    services = TestCase.services + [
        "main_window",
        "action_manager",
        "properties",
        "undo_manager",
    ]

    def test_init(self):
        service = CopyService()
        service.init(Application)
        # No exception? ok!

    def test_copy(self):
        service = CopyService()
        service.init(Application)

        ef = self.element_factory
        diagram = ef.create(UML.Diagram)
        ci = diagram.create(CommentItem, subject=ef.create(UML.Comment))

        service.copy([ci])
        assert diagram.canvas.get_all_items() == [ci]

        service.paste(diagram)

        assert len(diagram.canvas.get_all_items()) == 2, diagram.canvas.get_all_items()

    def test_copy_named_item(self):
        service = CopyService()
        service.init(Application)

        ef = self.element_factory
        diagram = ef.create(UML.Diagram)
        c = diagram.create(ClassItem, subject=ef.create(UML.Class))

        c.subject.name = "Name"

        diagram.canvas.update_now()
        i = list(diagram.canvas.get_all_items())
        assert 1 == len(i), i
        assert "Name" == i[0]._name.text

        service.copy([c])
        assert diagram.canvas.get_all_items() == [c]

        service.paste(diagram)

        i = diagram.canvas.get_all_items()

        assert 2 == len(i), i

        diagram.canvas.update_now()

        assert "Name" == i[0]._name.text
        assert "Name" == i[1]._name.text

    def _skip_test_copy_paste_undo(self):
        """
        Test if copied data is undoable.
        """
        from gaphor.storage.verify import orphan_references

        service = CopyService()
        service.init(Application)

        # Setting the stage:
        ci1 = self.create(ClassItem, UML.Class)
        ci2 = self.create(ClassItem, UML.Class)
        a = self.create(AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        assert a.subject
        assert a.head_end.subject
        assert a.tail_end.subject

        # The act: copy and paste, perform undo afterwards
        service.copy([ci1, ci2, a])

        service.paste(self.diagram)

        all_items = list(self.diagram.canvas.get_all_items())

        assert 6 == len(all_items)
        assert not orphan_references(self.element_factory)

        assert all_items[0].subject is all_items[3].subject
        assert all_items[1].subject is all_items[4].subject
        assert all_items[2].subject is all_items[5].subject

        undo_manager = self.get_service("undo_manager")

        undo_manager.undo_transaction()

        assert 3 == len(self.diagram.canvas.get_all_items())
        assert not orphan_references(self.element_factory)
