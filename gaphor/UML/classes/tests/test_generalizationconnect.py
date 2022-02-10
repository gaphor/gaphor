from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import allow, connect, get_connected
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.classes.klass import ClassItem


def test_generalization_multiple_connection(create, element_factory):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    gen1 = create(GeneralizationItem)

    connect(gen1, gen1.tail, c1)
    connect(gen1, gen1.head, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    gen2 = diagram2.create(GeneralizationItem)

    connect(gen2, gen2.tail, c3)
    connect(gen2, gen2.head, c4)

    assert gen1.subject is gen2.subject


def test_generalization_glue(create):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    glued = allow(gen, gen.tail, c1)
    assert glued

    connect(gen, gen.tail, c1)
    assert get_connected(gen, gen.tail) is c1
    assert gen.subject is None

    glued = allow(gen, gen.head, c2)
    assert glued


def test_generalization_connect(create):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(gen, gen.head, c1)
    connect(gen, gen.tail, c2)

    assert get_connected(gen, gen.head) is c1
    assert get_connected(gen, gen.tail) is c2
    assert gen.subject
    assert gen.subject.specific is c1.subject
    assert gen.subject.general is c2.subject


def test_generalization_connect_in_new_diagram(create, element_factory):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(gen, gen.head, c1)
    connect(gen, gen.tail, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    gen2 = diagram2.create(GeneralizationItem)

    connect(gen2, gen2.head, c3)
    connect(gen2, gen2.tail, c4)
    assert gen.subject is gen2.subject


def test_generalization_connect_in_new_diagram_in_opposite_direction(
    create, element_factory
):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(gen, gen.tail, c1)
    connect(gen, gen.head, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    gen2 = diagram2.create(GeneralizationItem)

    connect(gen2, gen2.head, c3)
    connect(gen2, gen2.tail, c4)
    assert gen.subject is not gen2.subject
    assert gen.subject.specific is c2.subject
    assert gen.subject.general is c1.subject
    assert gen2.subject.specific is c3.subject
    assert gen2.subject.general is c4.subject


def test_generalization_reconnect_in_same_diagram(create):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    c3 = create(ClassItem, UML.Class)
    gen = create(GeneralizationItem)

    # connect: c1 -> c2
    connect(gen, gen.head, c1)
    connect(gen, gen.tail, c2)

    s = gen.subject

    # reconnect: c2 -> c3
    connect(gen, gen.tail, c3)

    assert s is not gen.subject
    assert c1.subject is gen.subject.specific
    assert c3.subject is gen.subject.general
    assert c2.subject is not gen.subject.general


def test_generalization_reconnect_in_new_diagram(create, element_factory):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(gen, gen.head, c1)
    connect(gen, gen.tail, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    gen2 = diagram2.create(GeneralizationItem)

    connect(gen2, gen2.head, c3)
    connect(gen2, gen2.tail, c4)
    assert gen.subject is gen2.subject

    c5 = diagram2.create(ClassItem, subject=element_factory.create(UML.Class))
    connect(gen2, gen2.head, c5)

    assert gen.subject is not gen2.subject
    assert gen.subject.specific is c1.subject
    assert gen.subject.general is c2.subject
    assert gen2.subject.specific is c5.subject
    assert gen2.subject.general is c4.subject


def test_genralization_reconnect_twice_in_new_diagram(create, element_factory):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(gen, gen.head, c1)
    connect(gen, gen.tail, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    gen2 = diagram2.create(GeneralizationItem)

    connect(gen2, gen2.head, c3)
    connect(gen2, gen2.tail, c4)
    assert gen.subject is gen2.subject

    c5 = diagram2.create(ClassItem, subject=c2.subject)
    connect(gen2, gen2.head, c5)
    connect(gen2, gen2.head, c3)

    assert gen.subject is gen2.subject
    assert gen.subject.specific is c3.subject
    assert gen.subject.general is c4.subject
