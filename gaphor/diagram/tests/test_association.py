"""
Unnit tests for AssociationItem.
"""

import unittest
from zope import component

from gaphor.application import Application
from gaphor import UML
from gaphor.diagram.association import AssociationItem
from gaphor.diagram.klass import ClassItem
from gaphor.diagram.interfaces import IConnect
from gaphas import View


class AssociationItemTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory', 'adapter_loader'])
        self.element_factory = Application.get_service('element_factory')
        self.diagram = diagram = self.element_factory.create(UML.Diagram)
        self.view = View(diagram.canvas)
        self.assoc = diagram.create(AssociationItem)
        self.class1 = diagram.create(ClassItem, subject=self.element_factory.create(UML.Class))
        self.class2 = diagram.create(ClassItem, subject=self.element_factory.create(UML.Class))
        pass

    def tearDown(self):
        Application.shutdown()

    def test_create1(self):
        """
        Create an association and test properties.
        """
        adapter = component.queryMultiAdapter((self.class1, self.assoc), IConnect)
        assert adapter
        adapter.connect(self.assoc.head, self.assoc.head.x, self.assoc.head.y)

        assert self.assoc.head.connected_to

        adapter = component.queryMultiAdapter((self.class2, self.assoc), IConnect)
        adapter.connect(self.assoc.tail, self.assoc.tail.x, self.assoc.tail.y)

        assert self.assoc.tail.connected_to
        assert self.assoc.subject
        assert isinstance(self.assoc.subject, UML.Association)
        assert self.assoc.head_end.subject
        assert self.assoc.tail_end.subject

        assert self.assoc.show_direction == False

        self.assoc.show_direction = True
        assert self.assoc.show_direction == True

        self.assoc.subject.name = 'flying'

    def test_create_with_view(self):
        """ Like test_create, but now with a view attached.
        """
        view = View(canvas=self.diagram.canvas)
        self.test_create1()

# vim:sw=4:et:ai
