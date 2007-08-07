
import unittest
from gaphor import UML
from gaphor.diagram import items
from gaphor.services.copyservice import CopyService
from gaphor.application import Application

class CopyServiceTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['gui_manager', 'action_manager', 'element_factory', 'properties'])

    def tearDown(self):
        Application.shutdown()

    def test_init(self):
        service = CopyService()
        service.init(Application)

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
    
# vim:sw=4:et
