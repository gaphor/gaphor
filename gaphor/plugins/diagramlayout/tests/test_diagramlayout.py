
import unittest

from gaphor import UML
from gaphor.diagram import items
from gaphor.plugins.diagramlayout import DiagramLayout
from gaphor.application import Application

class DiagramLayoutTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory', 'gui_manager', 'properties', 'action_manager', 'diagram_layout', 'property_based_dispatcher'])

    def tearDown(self):
        Application.shutdown()

    def testDiagramLayout(self):
        elemfact = Application.get_service('element_factory')
        diagram_layout = Application.get_service('diagram_layout')

        diagram = elemfact.create(UML.Diagram)
        c1 = diagram.create(items.ClassItem, subject=elemfact.create(UML.Class))
        c2 = diagram.create(items.ClassItem, subject=elemfact.create(UML.Class))

        c2.matrix.translate(100, 100)
        c2.request_update()

        diagram_layout.layout_diagram(diagram)



# vim:sw=4:et:ai
