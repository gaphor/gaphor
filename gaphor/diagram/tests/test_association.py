"""
Unnit tests for AssociationItem.
"""

import unittest
from zope import component

from gaphor import UML
from gaphor.diagram.association import AssociationItem
from gaphor.diagram.klass import ClassItem
from gaphor.diagram.interfaces import IConnect
from gaphas import View

import gaphor.adapters


class AssociationItemTestCase(unittest.TestCase):

    def setUp(self):
        self.diagram = diagram = UML.create(UML.Diagram)
        self.view = View(diagram.canvas)
        self.assoc = diagram.create(AssociationItem)
        self.class1 = diagram.create(ClassItem, subject=UML.create(UML.Class))
        self.class2 = diagram.create(ClassItem, subject=UML.create(UML.Class))
        pass

    def tearDown(self):
        #try: UML.flush()
        #except: pass
        #assert len(list(UML.select())) == 0
        pass

    def test_create1(self):
        """Create an association and test properties.
        """
        adapter = component.queryMultiAdapter((self.class1, self.assoc), IConnect)
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
