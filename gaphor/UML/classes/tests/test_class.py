"""Test classes."""

from gaphor import UML
from gaphor.core.modeling import UpdateContext
from gaphor.core.modeling.diagram import FALLBACK_STYLE, Diagram
from gaphor.UML.classes.klass import ClassItem


def compartments(item):
    return item.shape.children[1:]


def context():
    return UpdateContext(style=FALLBACK_STYLE)


def test_compartments(element_factory):
    """Test creation of classes and working of compartments."""
    diagram = element_factory.create(Diagram)
    klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    assert 2 == len(compartments(klass))
    assert 0 == len(compartments(klass)[0].child.children)
    assert 0 == len(compartments(klass)[1].child.children)

    diagram.update({klass})

    assert 50 == float(klass.min_height)
    assert 100 == float(klass.min_width)

    attr = element_factory.create(UML.Property)
    attr.name = 4 * "x"  # about 44 pixels
    klass.subject.ownedAttribute = attr

    diagram.update({klass})

    assert 1 == len(compartments(klass)[0].child.children)
    assert compartments(klass)[0].size(context()) >= (40, 15)

    oper = element_factory.create(UML.Operation)
    oper.name = 4 * "x"  # about 44 pixels
    klass.subject.ownedOperation = oper

    oper = element_factory.create(UML.Operation)
    oper.name = 6 * "x"  # about 66 pixels
    klass.subject.ownedOperation = oper

    diagram.update({klass})
    assert 2 == len(compartments(klass)[1].child.children)
    assert compartments(klass)[1].size(context()) > (60.0, 34.0)


def test_attribute_removal(element_factory):
    diagram = element_factory.create(Diagram)
    klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    diagram.update({klass})

    attr = element_factory.create(UML.Property)
    attr.name = "blah1"
    klass.subject.ownedAttribute = attr

    attr2 = element_factory.create(UML.Property)
    attr2.name = "blah2"
    klass.subject.ownedAttribute = attr2

    attr = element_factory.create(UML.Property)
    attr.name = "blah3"
    klass.subject.ownedAttribute = attr

    assert len(compartments(klass)[0].child.children) == 3

    attr2.unlink()

    assert len(compartments(klass)[0].child.children) == 2


def test_compartment_resizing(element_factory):
    diagram = element_factory.create(Diagram)
    klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    klass.subject.name = "Class1"

    diagram.update({klass})

    attr = element_factory.create(UML.Property)
    attr.name = "blah"
    klass.subject.ownedAttribute = attr

    oper = element_factory.create(UML.Operation)
    oper.name = "method"
    klass.subject.ownedOperation = oper

    assert klass.width == 100

    attr.name = "x" * 25

    diagram.update({klass})

    width = klass.width
    assert width >= 170.0
