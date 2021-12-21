from gaphor import UML
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.datatype import DataTypeItem
from gaphor.UML.classes.klass import ClassItem
from gaphor.UML.recipes import set_navigability


def test_connect_value_type_to_block(diagram, element_factory):
    b = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    v = diagram.create(DataTypeItem, subject=element_factory.create(UML.DataType))
    a = diagram.create(AssociationItem)

    connect(a, a.head, b)
    connect(a, a.tail, v)
    set_navigability(a.subject, a.head_end.subject, True)
    set_navigability(a.subject, a.tail_end.subject, True)
    a.tail_end.subject.aggregation = "composite"

    assert a.head_end.subject.type is b.subject
    assert a.tail_end.subject.type is v.subject
    assert a.tail_end.subject in b.subject.ownedAttribute
