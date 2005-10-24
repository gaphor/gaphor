# vim:sw=4:et:ai

import unittest
import gaphor.UML as UML
import gaphor.diagram as diagram

factory = UML.ElementFactory()

class TestActivityNodes(unittest.TestCase):
    def setUp(self):
        self.pkg = factory.create(UML.Package)
        self.dgm = factory.create(UML.Diagram)
        self.dgm.package = self.pkg

    def createItem(self, ui_item_cls, item_cls):
        item = self.dgm.create(ui_item_cls)
        item.package = self.pkg
        item.subject = factory.create(item_cls)
        return item

    def createFlow(self):
        return self.createItem(diagram.FlowItem, UML.ControlFlow)

    def createActionItem(self):
        return self.createItem(diagram.ActionItem, UML.ActivityNode)

    def createDecisionNode(self):
        return self.createItem(diagram.DecisionNodeItem, UML.DecisionNode)

    def connectNodes(self, source, target, flow):
        source.connect_handle(flow.handles[0])
        target.connect_handle(flow.handles[-1])

    def disconnectNodes(self, flow):
        #print '-' * 10
        #source = flow.handles[0].connected_to
        #target = flow.handles[-1].connected_to
        #source.connect_handle(flow.handles[0])
        #target.connect_handle(flow.handles[-1])
        #print '-' * 10

    def testMergeNode(self):
        """
        Create decision node UI element and add two incoming flows.
        Element subject should change to MergeNode.
        """

        dnode = self.createDecisionNode()

        assert dnode.subject.__class__ == UML.DecisionNode, 'test problem'

        f1 = self.createFlow()
        f2 = self.createFlow()

        a1 = self.createActionItem()
        a2 = self.createActionItem()

        self.connectNodes(a1, dnode, f1)
        self.connectNodes(a2, dnode, f2)

        self.dgm.canvas.update_now()

        self.assertEquals(dnode.subject.__class__, UML.MergeNode)
        self.assertEquals(dnode.combined, False)
        # fixme: check that previous subject is destroyed

        self.disconnectNodes(f2)

        self.assertEquals(dnode.subject.__class__, UML.DecisionNode)
        self.assertEquals(dnode.combined, False)

    def checkCombinedNode(self, node):
        """
        Check combined UI node element. 

        Return subject of UI node element and combined UML node.
        """
        self.assertEquals(node.combined, True)
        self.assertEquals(node.subject.__class__, UML.MergeNode)
        self.assertEquals(len(node.subject.outgoing), 1)
        combined_node = node.subject.outgoing[0].target
        self.assertEquals(combined_node.__class__, UML.DecisionNode)
        self.assertEquals(len(combined_node.incoming), 1)
        return node.subject, combined_node

    def testCombinedNodes(self):
        dnode = self.createDecisionNode()
        f1 = self.createFlow()
        f2 = self.createFlow()
        f3 = self.createFlow()
        f4 = self.createFlow()

        a1 = self.createActionItem()
        a2 = self.createActionItem()
        a3 = self.createActionItem()
        a4 = self.createActionItem()

        self.connectNodes(a1, dnode, f1)
        self.connectNodes(a2, dnode, f2)
        self.connectNodes(dnode, a3, f3)
        self.connectNodes(dnode, a4, f4)

        n1, n2 = self.checkCombinedNode(dnode)
        # node has two incoming flows: f1, f2
        self.assertEquals(len(n1.incoming), 2)
        self.assert_(f1.subject in n1.incoming)
        self.assert_(f2.subject in n1.incoming)

        # combined node has two outgoing flows: f3, f4
        self.assertEquals(len(n2.outgoing), 2)
        self.assert_(f3.subject in n2.outgoing)
        self.assert_(f4.subject in n2.outgoing)

        f5 = self.createFlow()
        a5 = self.createActionItem()
        self.connectNodes(dnode, a5, f5)

        n1, n2 = self.checkCombinedNode(dnode)
        # combined node has new outgoing flow: f5
        self.assertEquals(len(n2.outgoing), 3)
        self.assert_(f5.subject in n2.outgoing)

        # disconnect f5 outgoing flow, node still is combined node
        self.disconnectNodes(f5)
        n1, n2 = self.checkCombinedNode(dnode)
        # f5 is removed from combined node
        self.assertEquals(len(n2.outgoing), 2)
        self.assert_(f5.subject not in n2.outgoing)
        
        self.disconnectNodes(f4)
        # node should not be combined anymore
        self.assertFalse(dnode.combined)
        # f4 was outgoing flow, so UML node class should merge node
        self.assertEqual(dnode.subject.__class__, UML.MergeNode)
        # f3 should be outgoing flow of UML node
        self.assert_(f3.subject in dnode.subject.outgoing)
        # f1 and f2 should be kept as incoming nodes
        self.assert_(f1.subject in dnode.subject.incoming)
        self.assert_(f2.subject in dnode.subject.incoming)

        f4 = self.createFlow()
        self.connectNodes(dnode, a4, f4)
        self.checkCombinedNode(dnode)

        # now, disconnect f1, dnode should be non-combined decision node
        self.disconnectNodes(f1)

        self.assertFalse(dnode.combined)
        self.assertEqual(dnode.subject.__class__, UML.DecisioNode)
        self.assert_(f1.subject not in dnode.subject.incoming)


if __name__ == '__main__':
    unittest.main()
