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

        self.assertEquals('Blah', flow._name.text)

        flow.subject = None

        self.assertEquals('', flow._name.text)


    def test_guard(self):
        """
        Test updating of flow guard text.
        """
        flow = self.create(items.FlowItem, UML.ControlFlow)

        self.assertEquals('', flow._guard.text)

        flow.subject.guard = 'GuardMe'
        self.assertEquals('GuardMe', flow._guard.text)

        flow.subject = None
        self.assertEquals('', flow._guard.text)


    def test_persistence(self):
        """
        TODO: Test connector item saving/loading
        """
        pass



# vim:sw=4:et:ai
