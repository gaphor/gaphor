"""
Unnit tests for AssociationItem.
"""

from gaphor.tests import TestCase
from zope import component

from gaphor import UML
from gaphor.diagram.classes.association import AssociationItem
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.items import InterfaceItem
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


    def test_navigability_at_class(self):
        """Test association end navigability connected to a class"""
        c1 = self.create(ClassItem, UML.Class)
        c2 = self.create(ClassItem, UML.Class)

        a = self.create(AssociationItem)

        adapter = component.queryMultiAdapter((c1, a), IConnect)
        assert adapter
        adapter.connect(a.head)
        assert a.head.connected_to

        adapter = component.queryMultiAdapter((c2, a), IConnect)
        adapter.connect(a.tail)
        assert a.tail.connected_to

        head = a._head_end

        head._set_navigability(True)
        assert head.subject.class_ == c2.subject
        assert head.subject.owningAssociation is None

        head._set_navigability(False)
        assert head.subject.class_ is None
        assert head.subject.owningAssociation == a.subject

        head._set_navigability(None)
        assert head.subject.class_ is None
        assert head.subject.owningAssociation is None


    def test_navigability_at_interface(self):
        """Test association end navigability connected to an interface"""
        c1 = self.create(InterfaceItem, UML.Interface)
        c2 = self.create(InterfaceItem, UML.Interface)

        a = self.create(AssociationItem)

        adapter = component.queryMultiAdapter((c1, a), IConnect)
        assert adapter
        adapter.connect(a.head)
        assert a.head.connected_to

        adapter = component.queryMultiAdapter((c2, a), IConnect)
        adapter.connect(a.tail)
        assert a.tail.connected_to

        head = a._head_end

        head._set_navigability(True)
        assert head.subject.interface_ == c2.subject
        assert head.subject.owningAssociation is None

        head._set_navigability(False)
        assert head.subject.interface_ is None
        assert head.subject.owningAssociation == a.subject

        head._set_navigability(None)
        assert head.subject.interface_ is None
        assert head.subject.owningAssociation is None

# vim:sw=4:et:ai
