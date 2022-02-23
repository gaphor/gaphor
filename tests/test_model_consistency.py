"""A Property-based test."""

import itertools
from io import StringIO

from hypothesis.control import assume, cleanup
from hypothesis.errors import UnsatisfiedAssumption
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
    run_state_machine_as_test,
)
from hypothesis.strategies import data, integers, lists, sampled_from

from gaphor import UML
from gaphor.application import Session
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram, ElementFactory, StyleSheet
from gaphor.core.modeling.element import generate_id, uuid_generator
from gaphor.diagram.deletable import deletable
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.storage import storage
from gaphor.storage.xmlwriter import XMLWriter
from gaphor.ui.filemanager import load_default_model
from gaphor.UML import diagramitems
from gaphor.UML.classes.classestoolbox import classes


def test_model_consistency():
    run_state_machine_as_test(ModelConsistency)


def tooldef():
    return sampled_from(classes.tools)


class ModelConsistency(RuleBasedStateMachine):
    @property
    def model(self) -> ElementFactory:
        return self.session.get_service("element_factory")  # type: ignore[no-any-return]

    @property
    def transaction(self) -> Transaction:
        return Transaction(self.session.get_service("event_manager"))

    def select(self, predicate):
        elements = ordered(self.model.select(predicate))
        assume(elements)
        return sampled_from(elements)

    def diagrams(self):
        return self.select(lambda e: isinstance(e, Diagram))

    def relations(self, diagram):
        relations = [
            p
            for p in diagram.presentation
            if isinstance(p, diagramitems.DependencyItem)
        ]
        assume(relations)
        return sampled_from(ordered(relations))

    def targets(self, relation, handle):
        return self.select(
            lambda e: isinstance(e, diagramitems.ClassItem)
            and e.diagram is relation.diagram
            and allow(relation, handle, e)
        )

    @initialize()
    def new_session(self):
        generate_id(map(str, itertools.count()))
        cleanup(lambda: generate_id(uuid_generator()))

        self.session = Session()
        copy_service = self.session.get_service("copy")
        copy_service.clear()

        load_default_model(self.model)
        self.fully_pasted_items = set()

    def create_diagram(self):
        with self.transaction:
            return self.model.create(Diagram)

    @rule(
        tooldef=tooldef(),
        data=data(),
        x=integers(min_value=0, max_value=2000),
        y=integers(min_value=0, max_value=2000),
    )
    def add_item_to_diagram(self, tooldef, data, x, y):
        diagram = data.draw(self.diagrams())
        with self.transaction:
            item = tooldef.item_factory(diagram)
            item.matrix.translate(x, y)

        # Do best effort to connect a line, no problem if it fails
        if isinstance(item, LinePresentation):
            self.try_connect_relation(data, item, item.head)
            self.try_connect_relation(data, item, item.tail)

    def try_connect_relation(self, data, item, handle):
        try:
            self._connect_relation(data, item, handle)
        except UnsatisfiedAssumption:
            pass

    @rule(data=data())
    def delete_element(self, data):
        elements = self.select(
            lambda e: not isinstance(e, (Diagram, StyleSheet, UML.Package))
            and deletable(e)
        )
        element = data.draw(elements)
        with self.transaction:
            element.unlink()

    @rule(data=data())
    def connect_relation(self, data):
        diagram = data.draw(self.diagrams())
        relation = data.draw(self.relations(diagram))
        handle = data.draw(sampled_from([relation.head, relation.tail]))
        self._connect_relation(data, relation, handle)

    def _connect_relation(self, data, relation, handle):
        target = data.draw(self.targets(relation, handle))
        with self.transaction:
            connect(relation, handle, target)

    @rule(data=data())
    def disconnect_relation(self, data):
        diagram = data.draw(self.diagrams())
        relation = data.draw(self.relations(diagram))
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
        diagram = data.draw(self.diagrams())
        assume(diagram.ownedPresentation)
        copy_service = self.session.get_service("copy")
        # Take from model, to ensure order.
        items = data.draw(
            lists(
                sampled_from(ordered(diagram.ownedPresentation)),
                min_size=1,
                unique=True,
            )
        )
        copy_service.copy(items)

    @rule(data=data())
    def paste_link(self, data):
        copy_service = self.session.get_service("copy")
        assume(copy_service.can_paste())
        diagram = data.draw(self.diagrams())
        copy_service.paste_link(diagram)

    @rule(data=data())
    def paste_full(self, data):
        copy_service = self.session.get_service("copy")
        assume(copy_service.can_paste())
        diagram = data.draw(self.diagrams())
        new_items = copy_service.paste_full(diagram)
        self.fully_pasted_items.update(new_items)

    @invariant()
    def check_relations(self):
        relation: diagramitems.DependencyItem
        for relation in self.model.select(diagramitems.DependencyItem):  # type: ignore[assignment]
            subject = relation.subject
            diagram = relation.diagram
            head = get_connected(diagram, relation.head)
            tail = get_connected(diagram, relation.tail)

            if head and tail:
                assert subject
                assert subject.supplier is head.subject
                assert subject.client is tail.subject
            elif relation not in self.fully_pasted_items:
                assert not subject

    @invariant()
    def check_save_and_load(self):
        new_model = ElementFactory()
        try:
            with StringIO() as buffer:
                storage.save(XMLWriter(buffer), self.model)
                buffer.seek(0)
                storage.load(
                    buffer,
                    factory=new_model,
                    modeling_language=self.session.get_service("modeling_language"),
                )

            assert (
                self.model.size() == new_model.size()
            ), f"{self.model.lselect()} != {new_model.lselect()}"
        except Exception:
            with open("falsifying_model.gaphor", "w") as out:
                storage.save(XMLWriter(out), self.model)
            raise


def get_connected(diagram, handle):
    """Get item connected to a handle."""
    if cinfo := diagram.connections.get_connection(handle):
        return cinfo.connected
    return None


def ordered(elements):
    return sorted(elements, key=lambda e: e.id)  # type: ignore[no-any-return]
