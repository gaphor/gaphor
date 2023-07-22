"""Test issues where associations are copied and pasted, deleted, etc.

Scenario's:
* Class and association are pasted in a new diagram
* Class and association are pasted in a new diagram and original association is deleted
* Class and association are pasted in a new diagram and new association is deleted
* Association is pasted in a new diagram and reconnected to the class (same subject as original)
* Association is pasted and directly deleted
* Class and association are pasted in a new diagram and one end is connected to a different class

What's the behavior we're looking for?

* If an association has >1 presentations, it can only connect to those same types ()
* If an association has ==1 presentation, it can reconnect to another type, association is updated
"""

import pytest

from gaphor import UML
from gaphor.application import Session
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.diagram.copypaste import copy_full, paste_link
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import diagramitems
from gaphor.UML.recipes import set_navigability


@pytest.fixture
def session():
    session = Session()
    yield session
    session.shutdown()


@pytest.fixture
def event_manager(session):
    return session.get_service("event_manager")


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def diagram(event_manager, element_factory):
    with Transaction(event_manager):
        return element_factory.create(Diagram)


@pytest.fixture
def class_and_association_with_copy(diagram, event_manager, element_factory):
    with Transaction(event_manager):
        c = diagram.create(
            diagramitems.ClassItem, subject=element_factory.create(UML.Class)
        )

        a = diagram.create(diagramitems.AssociationItem)
        connect(a, a.handles()[0], c)
        connect(a, a.handles()[1], c)

        set_navigability(a.subject, a.subject.memberEnd[0], True)

        copy_buffer = copy_full({a, c})
        new_diagram = element_factory.create(Diagram)
        pasted_items = paste_link(copy_buffer, new_diagram)

    aa = pasted_items.pop()
    if not isinstance(aa, diagramitems.AssociationItem):
        aa = pasted_items.pop()

    return c, a, aa


def test_delete_copied_associations(class_and_association_with_copy, event_manager):
    c, a, aa = class_and_association_with_copy

    assert a.subject.memberEnd[0].type
    assert a.subject.memberEnd[1].type
    assert a.subject.memberEnd[0].type is c.subject
    assert a.subject.memberEnd[1].type is c.subject
    assert a.subject.memberEnd[0] is a.head_subject
    assert a.subject.memberEnd[1] is a.tail_subject
    assert a.subject.memberEnd[0] in a.subject.memberEnd[1].type.ownedAttribute

    # Delete the copy and all is fine

    with Transaction(event_manager):
        aa.unlink()

    assert a.subject.memberEnd[0].type
    assert a.subject.memberEnd[1].type
    assert a.subject.memberEnd[0].type is c.subject
    assert a.subject.memberEnd[1].type is c.subject
    assert a.subject.memberEnd[0] is a.head_subject
    assert a.subject.memberEnd[1] is a.tail_subject
    assert a.subject.memberEnd[0] in a.subject.memberEnd[1].type.ownedAttribute


def test_delete_original_association(class_and_association_with_copy, event_manager):
    c, a, aa = class_and_association_with_copy

    assert aa.subject.memberEnd[0].type
    assert aa.subject.memberEnd[1].type
    assert aa.subject.memberEnd[0].type is c.subject
    assert aa.subject.memberEnd[1].type is c.subject
    assert aa.subject.memberEnd[0] is aa.head_subject
    assert aa.subject.memberEnd[1] is aa.tail_subject
    assert aa.subject.memberEnd[0] in aa.subject.memberEnd[1].type.ownedAttribute

    # Now, when the original is deleted, the model is changed and made invalid

    with Transaction(event_manager):
        a.unlink()

    assert aa.subject.memberEnd[0].type
    assert aa.subject.memberEnd[1].type
    assert aa.subject.memberEnd[0].type is c.subject
    assert aa.subject.memberEnd[1].type is c.subject
    assert aa.subject.memberEnd[0] is aa.head_subject
    assert aa.subject.memberEnd[1] is aa.tail_subject
    assert aa.subject.memberEnd[0] in aa.subject.memberEnd[1].type.ownedAttribute
