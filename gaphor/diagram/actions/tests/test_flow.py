import gaphor.UML as UML
from gaphor.tests.testcase import TestCase
from gaphor.diagram.actions.flow import FlowItem


class FlowTestCase(TestCase):
    def test_flow(self):
        self.create(FlowItem, UML.ControlFlow)

    def test_name(self):
        """
        Test updating of flow name text.
        """
        flow = self.create(FlowItem, UML.ControlFlow)
        flow.subject.name = "Blah"

        self.assertEqual("Blah", flow._name.text)

        flow.subject = None

        self.assertEqual("", flow._name.text)

    def test_guard(self):
        """
        Test updating of flow guard text.
        """
        flow = self.create(FlowItem, UML.ControlFlow)

        self.assertEqual("", flow._guard.text)

        flow.subject.guard = "GuardMe"
        self.assertEqual("GuardMe", flow._guard.text)

        flow.subject = None
        self.assertEqual("", flow._guard.text)
