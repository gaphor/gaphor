# vim:sw=4:et:ai

import unittest
import gaphor.diagram as diagram
import gaphor.UML as UML

class TestCase(unittest.TestCase):
    """
    Test case basic, abstract class.
    """
    def setUp(self):
        self.factory = UML.ElementFactory()

        self.pkg = self.factory.create(UML.Package)
        self.dgm = self.factory.create(UML.Diagram)
        self.dgm.package = self.pkg


    def createItem(self, ui_item_cls, item_cls):
        item = self.dgm.create(ui_item_cls)
        item.package = self.pkg
        item.subject = self.factory.create(item_cls)
        return item


    def createFlow(self):
        return self.createItem(diagram.FlowItem, UML.ControlFlow)


    def createActionItem(self):
        return self.createItem(diagram.ActionItem, UML.ActivityNode)


    def createObjectNode(self):
        return self.createItem(diagram.ObjectNodeItem, UML.ObjectNode)


    def createDecisionNode(self):
        return self.createItem(diagram.DecisionNodeItem, UML.DecisionNode)


    def connectNodes(self, source, target, flow):
        source.connect_handle(flow.handles[0])
        target.connect_handle(flow.handles[-1])


    def disconnectNodes(self, flow):
        source = flow.handles[0].connected_to
        target = flow.handles[-1].connected_to
        source.disconnect_handle(flow.handles[0])
        target.disconnect_handle(flow.handles[-1])



