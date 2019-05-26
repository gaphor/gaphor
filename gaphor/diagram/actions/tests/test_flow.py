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

        assert "Blah" == flow._name.text

        flow.subject = None

        assert "" == flow._name.text

    def test_guard(self):
        """
        Test updating of flow guard text.
        """
        flow = self.create(FlowItem, UML.ControlFlow)

        assert "" == flow._guard.text

        flow.subject.guard = "GuardMe"
        assert "GuardMe" == flow._guard.text

        flow.subject = None
        assert "" == flow._guard.text
