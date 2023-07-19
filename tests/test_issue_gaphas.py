# ruff: noqa: F401,F811
import pytest

from gaphor import UML
from gaphor.conftest import (
    create,
    diagram,
    element_factory,
    event_manager,
    modeling_language,
)
from gaphor.core import Transaction
from gaphor.diagram.tests.fixtures import connect
from gaphor.services.undomanager import UndoManager
from gaphor.UML.classes import AssociationItem, ClassItem
from gaphor.UML.sanitizerservice import SanitizerService


@pytest.fixture(autouse=True)
def sanitizer_service(event_manager):
    return SanitizerService(event_manager)


@pytest.fixture(autouse=True)
def undo_manager(event_manager, element_factory):
    return UndoManager(event_manager, element_factory)


def test_remove_class_with_association(create, diagram, element_factory, event_manager):
    with Transaction(event_manager):
        c1 = create(ClassItem, UML.Class)
        c1.subject.name = "klassitem1"
        c2 = create(ClassItem, UML.Class)
        c2.subject.name = "klassitem2"

        a = create(AssociationItem)

        assert len(list(diagram.get_all_items())) == 3

        connect(a, a.head, c1)
        connect(a, a.tail, c2)

    assert a.subject
    assert element_factory.lselect(UML.Association)[0] is a.subject

    with Transaction(event_manager):
        c1.unlink()
