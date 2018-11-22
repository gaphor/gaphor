import gaphor.UML as UML
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase

class FlowTestCase(TestCase):

    def test_flow(self):
        self.create(items.FlowItem, UML.ControlFlow)


    def test_name(self):
        """
        Test updating of flow name text.
        """
        flow = self.create(items.FlowItem, UML.ControlFlow)
        flow.subject.name = 'Blah'

        self.assertEqual('Blah', flow._name.text)

        flow.subject = None

        self.assertEqual('', flow._name.text)


    def test_guard(self):
        """
        Test updating of flow guard text.
        """
        flow = self.create(items.FlowItem, UML.ControlFlow)

        self.assertEqual('', flow._guard.text)

        flow.subject.guard = 'GuardMe'
        self.assertEqual('GuardMe', flow._guard.text)

        flow.subject = None
        self.assertEqual('', flow._guard.text)


    def test_persistence(self):
        """
        TODO: Test connector item saving/loading
        """
        pass



# vim:sw=4:et:ai
