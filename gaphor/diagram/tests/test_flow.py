import gaphor.UML as UML
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase

class FlowTestCase(TestCase):
    def test_flow(self):
        self.create(items.FlowItem, UML.ControlFlow)

# vim:sw=4:et:ai
