# ruff: noqa: F401,F811
from gaphor import UML
from gaphor.conftest import (
    create,
    diagram,
    element_factory,
    event_manager,
    modeling_language,
)
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.classes import AssociationItem, ClassItem
from gaphor.UML.classes.associationpropertypages import AssociationPropertyPage
from gaphor.UML.classes.classestoolbox import composite_association_config


def test_connect_composite_association(create, diagram):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    composite_association_config(a)

    property_page = AssociationPropertyPage(a.subject)
    _widget = property_page.construct()

    connect(a, a.head, c1)
    connect(a, a.tail, c2)
