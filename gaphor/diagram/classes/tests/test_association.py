"""
Unnit tests for AssociationItem.
"""

from gaphor.tests import TestCase
from zope import component

from gaphor import UML
from gaphor.diagram.classes.association import AssociationItem
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.interfaces import IConnect
from gaphas import View


class AssociationItemTestCase(TestCase):

    services = ['element_factory', 'adapter_loader']

    def setUp(self):
        super(AssociationItemTestCase, self).setUp()
        self.element_factory = self.get_service('element_factory')
        self.diagram = diagram = self.element_factory.create(UML.Diagram)
        self.view = View(diagram.canvas)
        self.assoc = diagram.create(AssociationItem)
        self.class1 = diagram.create(ClassItem, subject=self.element_factory.create(UML.Class))
        self.class2 = diagram.create(ClassItem, subject=self.element_factory.create(UML.Class))


    def test_create1(self):
        """
        Create an association and test properties.
        """
        adapter = component.queryMultiAdapter((self.class1, self.assoc), IConnect)
        assert adapter
        adapter.connect(self.assoc.head)

        assert self.assoc.head.connected_to

        adapter = component.queryMultiAdapter((self.class2, self.assoc), IConnect)
        adapter.connect(self.assoc.tail)

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

    def test_invert_direction(self):
        # Connect association with classes:
        self.test_create1()

        head_subject = self.assoc.subject.memberEnd[0]
        tail_subject = self.assoc.subject.memberEnd[1]

        self.assoc.invert_direction()

        assert head_subject is self.assoc.subject.memberEnd[1]
        assert tail_subject is self.assoc.subject.memberEnd[0]


# vim:sw=4:et:ai
