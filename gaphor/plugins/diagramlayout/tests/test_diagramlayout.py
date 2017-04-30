from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.application import Application
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase


class DiagramLayoutTestCase(TestCase):
    services = TestCase.services + ['main_window', 'ui_manager', 'properties', 'action_manager', 'diagram_layout']

    def testDiagramLayout(self):
        elemfact = Application.get_service('element_factory')
        diagram_layout = Application.get_service('diagram_layout')

        diagram = elemfact.create(uml2.Diagram)
        c1 = diagram.create(items.ClassItem, subject=elemfact.create(uml2.Class))
        c2 = diagram.create(items.ClassItem, subject=elemfact.create(uml2.Class))

        c2.matrix.translate(100, 100)
        c2.request_update()

        diagram_layout.layout_diagram(diagram)

# vim:sw=4:et:ai
