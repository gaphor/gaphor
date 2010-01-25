
from gaphor import UML
from gaphor.diagram import items
from gaphor.services.copyservice import CopyService
from gaphor.application import Application
from gaphor.tests.testcase import TestCase


class CopyServiceTestCase(TestCase):

    services = TestCase.services + ['gui_manager', 'action_manager', 'properties']

    def test_init(self):
        service = CopyService()
        service.init(Application)
        # No exception? ok!

    def test_copy(self):
        service = CopyService()
        service.init(Application)
        ef = Application.get_service('element_factory')
        diagram = ef.create(UML.Diagram)
        ci = diagram.create(items.CommentItem, subject=ef.create(UML.Comment))

        service.copy([ci])
        assert diagram.canvas.get_all_items() == [ ci ]

        service.paste(diagram)

        assert len(diagram.canvas.get_all_items()) == 2, diagram.canvas.get_all_items()
    
    def test_copy_named_item(self):
        service = CopyService()
        service.init(Application)

        ef = Application.get_service('element_factory')
        diagram = ef.create(UML.Diagram)
        c = diagram.create(items.ClassItem, subject=ef.create(UML.Class))

        c.name = 'Name'

        import gobject
        self.assertEquals(0, gobject.main_depth())

        diagram.canvas.update_now()
        i = list(diagram.canvas.get_all_items())
        self.assertEquals(1, len(i), i)
        self.assertEquals('Name', i[0]._name.text)

        service.copy([c])
        assert diagram.canvas.get_all_items() == [ c ]

        service.paste(diagram)

        i = diagram.canvas.get_all_items()

        self.assertEquals(2, len(i), i)

        diagram.canvas.update_now()

        self.assertEquals('Name', i[0]._name.text)
        self.assertEquals('Name', i[1]._name.text)

# vim:sw=4:et
