import os
import pkg_resources

from gaphor import UML
from gaphor.tests import TestCase
from gaphor.storage import storage
from gaphor.diagram.items import FlowItem, ActionItem


class ActionIssueTestCase(TestCase):
    def test_it(self):
        """
        Test an issue when loading a freshly created action diagram.
        """
        ef = self.element_factory
        dist = pkg_resources.get_distribution("gaphor")
        path = os.path.join(dist.location, "test-diagrams/action-issue.gaphor")
        storage.load(path, ef)

        actions = ef.lselect(lambda e: e.isKindOf(UML.Action))
        flows = ef.lselect(lambda e: e.isKindOf(UML.ControlFlow))
        self.assertEqual(3, len(actions))
        self.assertEqual(3, len(flows))

        # Actions live in partitions:
        partitions = ef.lselect(lambda e: e.isKindOf(UML.ActivityPartition))
        self.assertEqual(2, len(partitions))

        # Okay, so far the data model is saved correctly. Now, how do the
        # handles behave?
        diagrams = ef.lselect(lambda e: e.isKindOf(UML.Diagram))
        self.assertEqual(1, len(diagrams))

        canvas = diagrams[0].canvas
        assert 9 == len(canvas.get_all_items())
        # Part, Part, Act, Act, Part, Act, Flow, Flow, Flow

        for e in actions + flows:
            self.assertEqual(1, len(e.presentation), e)
        for i in canvas.select(lambda e: isinstance(e, (FlowItem, ActionItem))):
            self.assertTrue(i.subject, i)

        # Loaded as:
        #
        # actions[0] --> flows[0, 1]
        # flows[0, 2] --> actions[2]
        # flows[1] --> actions[1] --> flows[2]

        # start element:
        self.assertSame(actions[0].outgoing[0], flows[0])
        self.assertSame(actions[0].outgoing[1], flows[1])
        self.assertFalse(actions[0].incoming)

        cinfo, = canvas.get_connections(handle=flows[0].presentation[0].head)
        self.assertSame(cinfo.connected, actions[0].presentation[0])
        cinfo, = canvas.get_connections(handle=flows[1].presentation[0].head)
        self.assertSame(cinfo.connected, actions[0].presentation[0])

        # Intermediate element:
        self.assertSame(actions[1].incoming[0], flows[1])
        self.assertSame(actions[1].outgoing[0], flows[2])

        cinfo, = canvas.get_connections(handle=flows[1].presentation[0].tail)
        self.assertSame(cinfo.connected, actions[1].presentation[0])
        cinfo, = canvas.get_connections(handle=flows[2].presentation[0].head)
        self.assertSame(cinfo.connected, actions[1].presentation[0])

        # Final element:
        self.assertSame(actions[2].incoming[0], flows[0])
        self.assertSame(actions[2].incoming[1], flows[2])

        cinfo, = canvas.get_connections(handle=flows[0].presentation[0].tail)
        self.assertSame(cinfo.connected, actions[2].presentation[0])
        cinfo, = canvas.get_connections(handle=flows[2].presentation[0].tail)
        self.assertSame(cinfo.connected, actions[2].presentation[0])

        # Test the parent-child connectivity
        for a in actions:
            p, = a.inPartition
            self.assertTrue(p)
            self.assertTrue(canvas.get_parent(a.presentation[0]))
            self.assertSame(canvas.get_parent(a.presentation[0]), p.presentation[0])


# vim:sw=4:et:ai
