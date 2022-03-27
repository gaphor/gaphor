import logging

import pytest

from gaphor import UML
from gaphor.application import Application
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.classes import AssociationItem, ClassItem, GeneralizationItem
from gaphor.UML.interactions import MessageItem
from gaphor.UML.interactions.interactionstoolbox import reflexive_message_config


@pytest.fixture
def application():
    app = Application()
    yield app
    app.shutdown()


@pytest.fixture
def session(application):
    return application.new_session()


@pytest.fixture
def event_manager(session):
    return session.get_service("event_manager")


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def undo_manager(session):
    return session.get_service("undo_manager")


def test_class_association_undo_redo(event_manager, element_factory, undo_manager):
    diagram, ci1, ci2, a = set_up_class_and_association(event_manager, element_factory)

    undo_manager.clear_undo_stack()
    assert not undo_manager.can_undo()

    with Transaction(event_manager):
        ci2.unlink()

    assert undo_manager.can_undo()

    def get_connected(handle):
        """Get item connected to line via handle."""
        cinfo = diagram.connections.get_connection(handle)
        if cinfo:
            return cinfo.connected
        return None

    assert ci1 == get_connected(a.head)
    assert None is get_connected(a.tail)

    for i in range(3):
        assert 9 == len(diagram.connections.solver.constraints)

        undo_manager.undo_transaction()

        assert 18 == len(diagram.connections.solver.constraints)

        assert ci1 == get_connected(a.head)
        assert ci2.id == get_connected(a.tail).id

        undo_manager.redo_transaction()


def set_up_class_and_association(event_manager, element_factory):
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    assert 0 == len(diagram.connections.solver.constraints)

    with Transaction(event_manager):
        ci1 = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    assert 8 == len(diagram.connections.solver.constraints)

    with Transaction(event_manager):
        ci2 = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    assert 16 == len(diagram.connections.solver.constraints)

    with Transaction(event_manager):
        a = diagram.create(AssociationItem)

        connect(a, a.head, ci1)
        connect(a, a.tail, ci2)

    # Diagram, Association, 2x Class, Property, LiteralSpecification
    assert 12 == len(element_factory.lselect())
    assert 18 == len(diagram.connections.solver.constraints)

    return diagram, ci1, ci2, a


def test_diagram_item_can_undo_and_redo(
    event_manager, element_factory, undo_manager, caplog
):
    caplog.set_level(logging.INFO)
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    with Transaction(event_manager):
        cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        cls.subject.name = "name"
        cls.matrix.translate(10, 10)

    undo_manager.undo_transaction()
    undo_manager.redo_transaction()
    new_cls = diagram.ownedPresentation[0]
    assert new_cls.matrix.tuple() == (1, 0, 0, 1, 10, 10)
    assert new_cls.subject, element_factory.select()
    assert new_cls.subject.name == "name"
    assert not caplog.records


def test_diagram_item_should_not_end_up_in_element_factory(
    event_manager, element_factory, undo_manager
):
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    with Transaction(event_manager):
        cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    undo_manager.undo_transaction()
    undo_manager.redo_transaction()

    assert cls not in element_factory.lselect(), element_factory.lselect()


def test_delete_and_undo_diagram_item(event_manager, element_factory, undo_manager):
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    with Transaction(event_manager):
        subject = element_factory.create(UML.Class)
        subject.name = "Name"
        cls = diagram.create(ClassItem, subject=subject)

    with Transaction(event_manager):
        cls.unlink()

    undo_manager.undo_transaction()

    new_cls = diagram.ownedPresentation[0]
    new_elem = element_factory.lookup(subject.id)

    assert new_cls in new_elem.presentation
    assert new_cls.subject
    assert new_elem.name == "Name"


def test_delete_and_undo_model_element(event_manager, element_factory, undo_manager):
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    with Transaction(event_manager):
        subject = element_factory.create(UML.Class)
        subject.name = "Name"
        diagram.create(ClassItem, subject=subject)

    with Transaction(event_manager):
        subject.unlink()

    undo_manager.undo_transaction()

    new_cls = diagram.ownedPresentation[0]
    new_elem = element_factory.lookup(subject.id)

    assert new_cls in new_elem.presentation
    assert new_cls.subject
    assert new_elem.name == "Name"


def test_deleted_diagram_item_should_not_end_up_in_element_factory(
    event_manager, element_factory, undo_manager
):
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)
        cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    with Transaction(event_manager):
        cls.unlink()

    undo_manager.undo_transaction()

    assert cls not in element_factory.lselect(), element_factory.lselect()

    undo_manager.redo_transaction()

    assert cls not in element_factory.lselect(), element_factory.lselect()


def test_undo_should_not_cause_warnings(
    event_manager, element_factory, undo_manager, caplog
):
    caplog.set_level(logging.INFO)
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    with Transaction(event_manager):
        diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    assert not caplog.records

    undo_manager.undo_transaction()

    assert not diagram.ownedPresentation
    assert not caplog.records


def test_can_undo_connected_generalization(
    event_manager, element_factory, undo_manager, caplog
):
    caplog.set_level(logging.INFO)
    with Transaction(event_manager):
        diagram: Diagram = element_factory.create(Diagram)
        general = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        specific = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    with Transaction(event_manager):
        generalization = diagram.create(GeneralizationItem)
        connect(generalization, generalization.head, general)
        connect(generalization, generalization.tail, specific)

    assert not caplog.records

    undo_manager.undo_transaction()

    assert not list(diagram.select(GeneralizationItem))
    assert not caplog.records

    undo_manager.redo_transaction()
    new_generalization_item = next(diagram.select(GeneralizationItem))
    new_generalization = next(element_factory.select(UML.Generalization))

    assert len(list(diagram.select(GeneralizationItem))) == 1
    assert len(element_factory.lselect(UML.Generalization)) == 1
    assert new_generalization_item.subject is new_generalization
    assert not caplog.records


def test_can_undo_connected_association(
    event_manager, element_factory, undo_manager, caplog
):
    caplog.set_level(logging.INFO)
    with Transaction(event_manager):
        diagram: Diagram = element_factory.create(Diagram)
        parent = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        child = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    with Transaction(event_manager):
        association = diagram.create(AssociationItem)
        connect(association, association.head, parent)
        connect(association, association.tail, child)

    assert not caplog.records

    undo_manager.undo_transaction()

    assert not list(diagram.select(AssociationItem))
    assert not caplog.records

    undo_manager.redo_transaction()
    new_association_item = next(diagram.select(AssociationItem))
    new_association = next(element_factory.select(UML.Association))

    assert len(list(diagram.select(AssociationItem))) == 1
    assert len(element_factory.lselect(UML.Association)) == 1

    assert len(new_association.memberEnd) == 2
    assert new_association_item.subject is new_association
    assert new_association_item.head_subject
    assert new_association_item.tail_subject
    assert not caplog.records


def test_can_undo_diagram_with_content(event_manager, element_factory, undo_manager):
    with Transaction(event_manager):
        diagram: Diagram = element_factory.create(Diagram)
        diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    with Transaction(event_manager):
        diagram.unlink()

    undo_manager.undo_transaction()

    new_diagram = element_factory.lookup(diagram.id)

    assert new_diagram
    assert new_diagram.ownedPresentation


def test_reflexive_message_undo(event_manager, element_factory, undo_manager):
    with Transaction(event_manager):
        diagram: Diagram = element_factory.create(Diagram)

    with Transaction(event_manager):
        message = diagram.create(MessageItem)
        reflexive_message_config(message)

    undo_manager.undo_transaction()
