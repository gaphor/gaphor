# vim:sw=4:et:ai

import unittest
import gaphor.UML as UML
import gaphortests

class TestActivityNodes(gaphortests.TestCase):
    def testObjectFlow(self):
        """
        Check if flow is object flow when connect to object node.
        """
        f = self.createFlow()

        ai = self.createActionItem()
        on = self.createObjectNode()

        self.connectNodes(ai, on, f)

        self.assertEqual(f.subject.__class__, UML.ObjectFlow)

