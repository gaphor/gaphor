"""
Unnit tests for AssociationItem.
"""

from zope import component
from gaphor.diagram.interfaces import IConnect
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram.items import AssociationItem, ClassItem, InterfaceItem, \
    UseCaseItem, ActorItem


class AssociationItemTestCase(TestCase):

    services = TestCase.services + ['element_dispatcher']

    def setUp(self):
        super(AssociationItemTestCase, self).setUp()
        self.assoc = self.create(AssociationItem)
        self.class1 = self.create(ClassItem, UML.Class)
        self.class2 = self.create(ClassItem, UML.Class)


    def test_create(self):
        """Test association creation and its basic properties
        """
        self.connect(self.assoc, self.assoc.head, self.class1)
        self.connect(self.assoc, self.assoc.tail, self.class2)

        self.assertTrue(isinstance(self.assoc.subject, UML.Association))
        self.assertTrue(self.assoc.head_end.subject is not None)
        self.assertTrue(self.assoc.tail_end.subject is not None)

        self.assertFalse(self.assoc.show_direction)

        self.assoc.show_direction = True
        self.assertTrue(self.assoc.show_direction)


    def test_invert_direction(self):
        """Test association direction inverting
        """
        self.connect(self.assoc, self.assoc.head, self.class1)
        self.connect(self.assoc, self.assoc.tail, self.class2)

        head_subject = self.assoc.subject.memberEnd[0]
        tail_subject = self.assoc.subject.memberEnd[1]

        self.assoc.invert_direction()

        self.assertTrue(head_subject is self.assoc.subject.memberEnd[1])
        self.assertTrue(tail_subject is self.assoc.subject.memberEnd[0])


    def test_association_end_updates(self):
        """Test association end navigability connected to a class"""
        from gaphas.canvas import Canvas
        canvas = Canvas()
        c1 = self.create(ClassItem, UML.Class)
        c2 = self.create(ClassItem, UML.Class)
        a = self.create(AssociationItem)

        self.connect(a, a.head, c1)
        c = self.get_connected(a.head)
        self.assertTrue(c is c1)

        self.connect(a, a.tail, c2)
        c = self.get_connected(a.tail)
        self.assertTrue(c is c2)

        assert a.subject.memberEnd, a.subject.memberEnd

        assert a.subject.memberEnd[0] is a.head_end.subject
        assert a.subject.memberEnd[1] is a.tail_end.subject
        assert a.subject.memberEnd[0].name is None

        dispatcher = self.get_service('element_dispatcher')
        print dispatcher._handlers.has_key((a.subject.memberEnd[0], UML.Property.name))
        print '*' * 60
        a.subject.memberEnd[0].name = 'blah'
        print '*' * 60
        self.diagram.canvas.update()

        assert a.head_end._name == '+ blah', a.head_end.get_name()

    def test_association_orthogonal(self):
        c1 = self.create(ClassItem, UML.Class)
        c2 = self.create(ClassItem, UML.Class)
        a = self.create(AssociationItem)

        self.connect(a, a.head, c1)
        c = self.get_connected(a.head)
        self.assertTrue(c is c1)

        a.matrix.translate(100, 100)
        self.connect(a, a.tail, c2)
        c = self.get_connected(a.tail)
        self.assertTrue(c is c2)

        try:
            a.orthogonal = True
        except ValueError:
            pass # Expected, hanve only 2 handles, need 3 or more
        else:
            assert False, 'Can not set line to orthogonal with less than 3 handles'

# vim:sw=4:et:ai
