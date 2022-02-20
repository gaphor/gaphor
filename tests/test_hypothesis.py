"""A Property-based test."""

from io import StringIO

from hypothesis import assume
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from hypothesis.strategies import data, sampled_from, sets

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


class ModelConsistency(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.session = Session()
        load_default_model(self.model)

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
        self._connect_relation(data, relation, relation.head)
        self._connect_relation(data, relation, relation.tail)
        return relation

    @rule(data=data())
    def delete_element(self, data):
        elements = self.model.lselect(
            lambda e: not isinstance(e, (Diagram, StyleSheet, UML.Package))
        )
        assume(elements)
        element = data.draw(sampled_from(elements))
        with self.transaction:
            element.unlink()

    @rule(data=data())
    def connect_relation(self, data):
        diagram = data.draw(sampled_from(self.model.lselect(Diagram)))
        relation = data.draw(sampled_from(self.relations(diagram)))
        handle = data.draw(sampled_from([relation.head, relation.tail]))
        self._connect_relation(data, relation, handle)

    def _connect_relation(self, data, relation, handle):
        target = data.draw(sampled_from(self.targets(relation, handle)))
        with self.transaction:
            connect(relation, handle, target)
        if get_connected(relation.diagram, relation.head) and get_connected(
            relation.diagram, relation.tail
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

    @rule(data=data())
    def copy(self, data):
        diagram = data.draw(sampled_from(self.model.lselect(Diagram)))
        assume(diagram.ownedPresentation)
        copy_service = self.session.get_service("copy")
        items = data.draw(
            sets(sampled_from(list(diagram.ownedPresentation)), min_size=1)
        )
        copy_service.copy(items)

    @rule(data=data())
    def paste_link(self, data):
        copy_service = self.session.get_service("copy")
        assume(copy_service.can_paste())
        diagram = data.draw(sampled_from(self.model.lselect(Diagram)))
        copy_service.paste_link(diagram)

    @rule(data=data())
    def paste_full(self, data):
        copy_service = self.session.get_service("copy")
        assume(copy_service.can_paste())
        diagram = data.draw(sampled_from(self.model.lselect(Diagram)))
        copy_service.paste_full(diagram)

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

    # TODO: do copy/paste


ModelConsistencyTestCase = ModelConsistency.TestCase


def get_connected(diagram, handle):
    """Get item connected to a handle."""
    cinfo = diagram.connections.get_connection(handle)
    if cinfo:
        return cinfo.connected
    return None
