from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.classes.interface import InterfaceItem
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.classes.klass import ClassItem


def test_interface_realization_multiple_connection(create, element_factory):
    c1 = create(InterfaceItem, UML.Interface)
    c2 = create(ClassItem, UML.Class)
    rel1 = create(InterfaceRealizationItem)

    connect(rel1, rel1.head, c1)
    connect(rel1, rel1.tail, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    rel2 = diagram2.create(InterfaceRealizationItem)

    connect(rel2, rel2.head, c3)
    connect(rel2, rel2.tail, c4)

    assert rel1.subject is rel2.subject


def test_interface_realization_reconnect_in_new_diagram(create, element_factory):
    c1 = create(InterfaceItem, UML.Interface)
    c2 = create(ClassItem, UML.Class)
    rel = create(InterfaceRealizationItem)

    connect(rel, rel.head, c1)
    connect(rel, rel.tail, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(InterfaceItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    rel2 = diagram2.create(InterfaceRealizationItem)

    connect(rel2, rel2.head, c3)
    connect(rel2, rel2.tail, c4)
    assert rel.subject is rel2.subject

    c5 = diagram2.create(InterfaceItem, subject=element_factory.create(UML.Interface))
    connect(rel2, rel2.head, c5)

    assert rel.subject is not rel2.subject
    assert rel.subject.supplier is c1.subject
    assert rel.subject.client is c2.subject
    assert rel2.subject.supplier is c5.subject
    assert rel2.subject.client is c4.subject


def test_interface_realization_reconnect_twice_in_new_diagram(create, element_factory):
    c1 = create(InterfaceItem, UML.Interface)
    c2 = create(ClassItem, UML.Class)
    rel = create(InterfaceRealizationItem)

    connect(rel, rel.head, c1)
    connect(rel, rel.tail, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(InterfaceItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    rel2 = diagram2.create(InterfaceRealizationItem)

    connect(rel2, rel2.head, c3)
    connect(rel2, rel2.tail, c4)
    assert rel.subject is rel2.subject

    c5 = diagram2.create(InterfaceItem, subject=element_factory.create(UML.Interface))
    connect(rel2, rel2.head, c5)
    connect(rel2, rel2.head, c3)

    assert rel.subject is rel2.subject
    assert rel.subject.supplier is c1.subject
    assert rel.subject.client is c2.subject
