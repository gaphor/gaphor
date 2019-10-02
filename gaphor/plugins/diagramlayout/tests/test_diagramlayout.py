from gaphor import UML
from gaphor.application import Application
from gaphor.diagram.classes import ClassItem
from gaphor.tests.testcase import TestCase


class DiagramLayoutTestCase(TestCase):

    services = TestCase.services + [
        "main_window",
        "properties",
        "action_manager",
        "diagram_layout",
        "import_menu",
        "export_menu",
        "tools_menu",
    ]

    def testDiagramLayout(self):
        elemfact = Application.get_service("element_factory")
        diagram_layout = Application.get_service("diagram_layout")

        diagram = elemfact.create(UML.Diagram)
        c1 = diagram.create(ClassItem, subject=elemfact.create(UML.Class))
        c2 = diagram.create(ClassItem, subject=elemfact.create(UML.Class))

        c2.matrix.translate(100, 100)
        c2.request_update()

        diagram_layout.layout_diagram(diagram)
