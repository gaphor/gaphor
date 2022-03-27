"""A Property-based test.

This is a property based/model based/monkey test.

It starts a user session and performs all sorts of user
actions:
- create/delete elements
- create/delete diagrams
- connect, disconnect
- change owner element
- undo, redo
- copy, paste

Some tips:
- the model is leading. Just draw from the model with the proper filters
- do not perform `assume()` calls in a transaction

To do:
- Create tests for actions, interactions, states
- Create tests for SysML tools (combined with UML?)
"""

from __future__ import annotations

import itertools
from functools import singledispatch
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

from gaphor.application import Session
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram, ElementFactory, StyleSheet
from gaphor.core.modeling.element import generate_id, uuid_generator
from gaphor.diagram.deletable import deletable
from gaphor.diagram.drop import drop
from gaphor.diagram.group import can_group
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.storage import storage
from gaphor.storage.xmlwriter import XMLWriter
from gaphor.ui.filemanager import load_default_model
from gaphor.ui.namespacemodel import change_owner
from gaphor.UML import diagramitems
from gaphor.UML.toolbox import actions, classes, deployments, profiles, use_cases


def test_model_consistency():
    run_state_machine_as_test(ModelConsistency)


def tooldef():
    return sampled_from(
        list(
            itertools.chain(
                classes.tools,
                deployments.tools,
                use_cases.tools,
                profiles.tools,
                actions.tools,
            )
        )
    )


class ModelConsistency(RuleBasedStateMachine):
    @property
    def model(self) -> ElementFactory:
        return self.session.get_service("element_factory")  # type: ignore[no-any-return]

    @property
    def transaction(self) -> Transaction:
        return Transaction(self.session.get_service("event_manager"))

    def select(self, expression=None):
        elements = ordered(self.model.select(expression))
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

    @rule()
    def create_diagram(self):
        with self.transaction:
            self.model.create(Diagram)

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
            diagram.update_now({item})

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
        # Do not delete StyleSheet: it will be re-created on load,
        # causing test invariants to fail. It can't be created
        # dynamically, because such changes require a transaction.
        elements = self.select(lambda e: not isinstance(e, StyleSheet) and deletable(e))
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

    @rule(data=data())
    def change_owner(self, data):
        parent = data.draw(self.select())
        element = data.draw(
            self.select(lambda e: e is not parent and can_group(parent, e))
        )
        with self.transaction as tx:
            changed = change_owner(parent, element)
            if not changed:
                tx.rollback()
        assume(changed)

    @rule(data=data())
    def drop(self, data):
        diagram = data.draw(self.diagrams())
        element = data.draw(self.select())
        with self.transaction as tx:
            item = drop(element, diagram, 0, 0)
            if not item:
                tx.rollback()
        assume(item)

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
        for relation in self.model.select(LinePresentation):
            subject = relation.subject
            diagram = relation.diagram
            head = get_connected(diagram, relation.head)
            tail = get_connected(diagram, relation.tail)

            if head and tail:
                check_relation(relation, head, tail)
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


@singledispatch
def check_relation(relation: object, head, tail):
    assert False, f"No comparison function for {relation}"


@check_relation.register
def _(relation: diagramitems.DependencyItem, head, tail):
    subject = relation.subject
    assert subject
    assert subject.supplier is head.subject
    assert subject.client is tail.subject


@check_relation.register
def _(relation: diagramitems.GeneralizationItem, head, tail):
    subject = relation.subject
    assert subject
    assert subject.specific is head.subject
    assert subject.general is tail.subject


@check_relation.register
def _(relation: diagramitems.InterfaceRealizationItem, head, tail):
    subject = relation.subject
    assert subject
    assert subject.contract is head.subject
    assert subject.implementatingClassifier is tail.subject


@check_relation.register
def _(relation: diagramitems.ContainmentItem, head, tail):
    assert not relation.subject
    # subject ownership can not be checked, since
    # it can be changed by the group functionality.


@check_relation.register
def _(relation: diagramitems.AssociationItem, head, tail):
    subject = relation.subject
    targets = [m.type for m in subject.memberEnd]
    assert head.subject in targets
    assert tail.subject in targets


@check_relation.register
def _(relation: diagramitems.ExtensionItem, head, tail):
    subject = relation.subject
    targets = [m.type for m in subject.memberEnd]
    assert head.subject in targets
    assert tail.subject in targets


@check_relation.register
def _(relation: diagramitems.ControlFlowItem, head, tail):
    subject = relation.subject
    assert subject
    assert subject.source is head.subject
    assert subject.target is tail.subject


@check_relation.register
def _(relation: diagramitems.ObjectFlowItem, head, tail):
    subject = relation.subject
    assert subject
    assert subject.source is head.subject
    assert subject.target is tail.subject
