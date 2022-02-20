"""A Property-based test."""

from io import StringIO

import pytest
from hypothesis import assume
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from hypothesis.strategies import data, sampled_from

from gaphor import UML
from gaphor.application import Session
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram, ElementFactory, StyleSheet
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.storage import storage
from gaphor.storage.xmlwriter import XMLWriter
from gaphor.ui.filemanager import load_default_model
from gaphor.UML import diagramitems
from gaphor.UML.classes.dependency import DependencyItem

N_DIAGRAMS = 5


class ModelConsistency(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.session = Session()
        load_default_model(self.model)
        for _ in range(N_DIAGRAMS):
            self.create_diagram()

    @property
    def model(self) -> ElementFactory:
        return self.session.get_service("element_factory")  # type: ignore[no-any-return]

    @property
    def transaction(self) -> Transaction:
        return Transaction(self.session.get_service("event_manager"))

    def relations(self, diagram):
        relations = [
            p
            for p in diagram.presentation
            if isinstance(p, diagramitems.DependencyItem)
        ]
        assume(relations)
        return relations

    def targets(self, relation, handle):
        targets = self.model.lselect(
            lambda e: isinstance(e, diagramitems.ClassItem)
            and e.diagram is relation.diagram
            and allow(relation, handle, e)
        )
        assume(targets)
        return targets

    def create_diagram(self):
        with self.transaction:
            return self.model.create(Diagram)

    @rule(data=data())
    def create_class(self, data):
        diagram = data.draw(sampled_from(self.model.lselect(Diagram)))
        with self.transaction:
            return diagram.create(
                diagramitems.ClassItem, subject=self.model.create(UML.Class)
            )

    @rule(data=data())
    def create_dependency(self, data):
        diagram = data.draw(sampled_from(self.model.lselect(Diagram)))
        with self.transaction:
            relation = diagram.create(diagramitems.DependencyItem)
        self.connect_relation(data, relation, relation.head)
        self.connect_relation(data, relation, relation.tail)
        return relation

    @rule(data=data())
    def delete_element(self, data):
        elements = self.model.lselect(
            lambda e: not isinstance(e, (Diagram, StyleSheet))
        )
        assume(elements)
        element = data.draw(sampled_from(elements))
        with self.transaction:
            element.unlink()

    @rule(data=data())
    def connect_relation(self, data, relation=None, handle=None):
        diagram = (relation and relation.diagram) or data.draw(
            sampled_from(self.model.lselect(Diagram))
        )
        relation = relation or data.draw(sampled_from(self.relations(diagram)))
        handle = handle or data.draw(sampled_from([relation.head, relation.tail]))
        target = data.draw(sampled_from(self.targets(relation, handle)))
        with self.transaction:
            connect(relation, handle, target)
        if get_connected(diagram, relation.head) and get_connected(
            diagram, relation.tail
        ):
            assert relation.subject

    @rule(data=data())
    def disconnect_relation(self, data):
        diagram = data.draw(sampled_from(self.model.lselect(Diagram)))
        relation = data.draw(sampled_from(self.relations(diagram)))
        handle = data.draw(sampled_from([relation.head, relation.tail]))
        with self.transaction:
            disconnect(relation, handle)

    @rule()
    def undo(self):
        undo_manager = self.session.get_service("undo_manager")
        assume(undo_manager.can_undo())
        undo_manager.undo_transaction()

    @rule()
    def redo(self):
        undo_manager = self.session.get_service("undo_manager")
        assume(undo_manager.can_redo())
        undo_manager.redo_transaction()

    @invariant()
    def check_relations(self):
        relation: DependencyItem
        for relation in self.model.select(diagramitems.DependencyItem):  # type: ignore[assignment]
            subject = relation.subject
            diagram = relation.diagram
            head = get_connected(diagram, relation.head)
            tail = get_connected(diagram, relation.tail)

            is_not_connected = not subject and not (head and tail)
            is_connected = subject and head and tail
            assert is_not_connected or (
                is_connected
                and subject.supplier is head.subject
                and subject.client is tail.subject
            )

    @invariant()
    def can_save_and_load(self):
        new_model = ElementFactory()
        with StringIO() as buffer:
            storage.save(XMLWriter(buffer), self.model)
            buffer.seek(0)
            storage.load(
                buffer,
                factory=new_model,
                modeling_language=self.session.get_service("modeling_language"),
            )

        assert (
            new_model.size() == self.model.size()
        ), f"{new_model.lselect()} != {self.model.lselect()}"

    # TODO: do copy/paste, undo/redo


ModelConsistencyTestCase = ModelConsistency.TestCase


def get_connected(diagram, handle):
    """Get item connected to a handle."""
    cinfo = diagram.connections.get_connection(handle)
    if cinfo:
        return cinfo.connected
    return None


@pytest.fixture
def interactions():
    return ModelConsistency()


class DataStub:
    def draw(self, data):
        return data.get_element(0)


def test_create_class(interactions: ModelConsistency, data=DataStub()):
    klass = interactions.create_class(data)
    assert klass
    assert klass in interactions.model


def test_create_dependency(interactions: ModelConsistency, data=DataStub()):
    for _ in range(10):
        interactions.create_class(data)

    relation = interactions.create_dependency(data)

    assert relation
    assert relation in interactions.model
    assert relation.subject


@pytest.mark.skip
def test_reconnect_dependency(interactions: ModelConsistency, data=DataStub()):
    classes = [interactions.create_class(data) for _ in range(10)]

    relation = interactions.create_dependency(data)
    connect(relation, relation.head, classes[0])
    connect(relation, relation.tail, classes[1])
    interactions.connect_relation(data)

    assert relation.subject.supplier
    assert relation.subject.client


@pytest.mark.skip
def test_disconnect_dependency(interactions: ModelConsistency, data=DataStub()):
    for _ in range(10):
        interactions.create_class(data)

    relation = interactions.create_dependency(data)
    interactions.disconnect_relation(data)

    assert not relation.subject
    assert bool(get_connected(relation.diagram, relation.head)) != bool(
        get_connected(relation.diagram, relation.tail)
    )
