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

import contextlib
import itertools
from functools import singledispatch
from io import StringIO
from typing import Iterable

import hypothesis
from gaphas.connector import Handle
from hypothesis import reproduce_failure, settings  # noqa
from hypothesis.control import assume, cleanup
from hypothesis.errors import UnsatisfiedAssumption
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
)
from hypothesis.strategies import data, integers, lists, sampled_from

from gaphor import UML
from gaphor.application import Session
from gaphor.C4Model.toolbox import c4
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram, ElementFactory, Presentation, StyleSheet
from gaphor.core.modeling.element import Element, generate_id, uuid_generator
from gaphor.diagram.copypaste import copy_full, paste_full, paste_link
from gaphor.diagram.deletable import deletable
from gaphor.diagram.drop import drop
from gaphor.diagram.group import can_group, change_owner
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.support import get_diagram_item_metadata
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.RAAML.toolbox import fta, stpa
from gaphor.storage import storage
from gaphor.SysML.toolbox import blocks, internal_blocks, requirements
from gaphor.ui.filemanager import load_default_model
from gaphor.UML import diagramitems
from gaphor.UML.toolbox import (
    actions,
    classes,
    deployments,
    interactions,
    profiles,
    states,
    use_cases,
)


def tooldef():
    return sampled_from(
        list(
            itertools.chain(
                # UML
                classes.tools,
                deployments.tools,
                use_cases.tools,
                profiles.tools,
                actions.tools,
                interactions.tools,
                states.tools,
                # C4
                c4.tools,
                # SysML
                blocks.tools,
                internal_blocks.tools,
                requirements.tools,
                # RAAML
                stpa.tools,
                fta.tools,
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
        self.copy_buffer: object = None

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
            diagram.update({item})

        # Do best effort to connect a line, no problem if it fails
        if isinstance(item, LinePresentation):
            self.try_connect_relation(data, item, item.head)
            self.try_connect_relation(data, item, item.tail)

    def try_connect_relation(self, data, item, handle):
        with contextlib.suppress(UnsatisfiedAssumption):
            self._connect_relation(data, item, handle)

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
        # Take from model, to ensure order.
        items = data.draw(
            lists(
                sampled_from(ordered(diagram.ownedPresentation)),
                min_size=1,
                unique=True,
            )
        )
        self.copy_buffer = copy_full(items)

    @rule(data=data())
    def paste_link(self, data):
        assume(self.copy_buffer)
        diagram = data.draw(self.diagrams())
        with self.transaction:
            paste_link(self.copy_buffer, diagram)

    @rule(data=data())
    def paste_full(self, data):
        assume(self.copy_buffer)
        diagram = data.draw(self.diagrams())
        with self.transaction:
            new_items = paste_full(self.copy_buffer, diagram)
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
                storage.save(buffer, self.model)
                buffer.seek(0)
                storage.load(
                    buffer,
                    element_factory=new_model,
                    modeling_language=self.session.get_service("modeling_language"),
                )

            assert (
                self.model.size() == new_model.size()
            ), f"{self.model.lselect()} != {new_model.lselect()}"
            assert {e.id for e in self.model} == {e.id for e in new_model}
        except Exception:
            with open("falsifying_model.gaphor", "w", encoding="utf") as out:
                storage.save(out, self.model)
            raise


def get_connected(diagram: Diagram, handle: Handle) -> Presentation | None:
    """Get item connected to a handle."""
    if cinfo := diagram.connections.get_connection(handle):
        return cinfo.connected  # type: ignore[no-any-return]
    return None


def ordered(elements: Iterable[Element]) -> list[Element]:
    return sorted(elements, key=lambda e: e.id)


@singledispatch
def check_relation(relation: Presentation, head: Presentation, tail: Presentation):
    subject = relation.subject
    assert subject

    metadata = get_diagram_item_metadata(type(relation))
    assert metadata, f"No comparison function for {relation}"
    assert metadata["head"].get(subject) is head.subject
    assert metadata["tail"].get(subject) is tail.subject


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
def _(relation: diagramitems.MessageItem, head, tail):
    subject = relation.subject
    assert subject
    assert isinstance(subject.sendEvent, UML.MessageOccurrenceSpecification)
    assert isinstance(subject.receiveEvent, UML.MessageOccurrenceSpecification)
    assert subject.sendEvent.covered is head.subject
    assert subject.receiveEvent.covered is tail.subject


ModelConsistency.TestCase.settings = settings(
    max_examples=5,
    stateful_step_count=100,
    deadline=20000,
    phases=[hypothesis.Phase.generate],
)
TestModelConsistency = ModelConsistency.TestCase
