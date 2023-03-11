"""A Property-based test.

Generate a bunch of diagrams and auto-layout them.
"""

from __future__ import annotations

import itertools
from typing import Iterable

import pytest
from hypothesis.control import assume, cleanup
from hypothesis.errors import UnsatisfiedAssumption
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
    run_state_machine_as_test,
)
from hypothesis.strategies import data, integers, sampled_from

from gaphor.application import Session
from gaphor.C4Model.toolbox import c4
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.core.modeling.element import Element, generate_id, uuid_generator
from gaphor.diagram.group import can_group
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.tests.fixtures import allow, connect
from gaphor.plugins.autolayout import AutoLayout
from gaphor.RAAML.toolbox import fta, stpa
from gaphor.SysML.toolbox import blocks, internal_blocks, requirements
from gaphor.ui.filemanager import load_default_model
from gaphor.diagram.group import change_owner
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


@pytest.mark.skip(
    reason="This test takes too long since Hypothesis 6.68.1 and should be refactored"
)
@pytest.mark.hypothesis
def test_auto_layouting():
    run_state_machine_as_test(AutoLayouting)


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


class AutoLayouting(RuleBasedStateMachine):
    @property
    def model(self) -> ElementFactory:
        return self.session.get_service("element_factory")  # type: ignore[no-any-return]

    @property
    def auto_layout(self) -> AutoLayout:
        return self.session.get_service("auto_layout")  # type: ignore[no-any-return]

    @property
    def transaction(self) -> Transaction:
        return Transaction(self.session.get_service("event_manager"))

    def select(self, expression=None):
        elements = ordered(self.model.select(expression))
        assume(elements)
        return sampled_from(elements)

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
        self.diagram = next(self.model.select(Diagram))

    @rule(
        tooldef=tooldef(),
        data=data(),
        x=integers(min_value=0, max_value=2000),
        y=integers(min_value=0, max_value=2000),
    )
    def add_item_to_diagram(self, tooldef, data, x, y):
        with self.transaction:
            item = tooldef.item_factory(self.diagram)
            item.matrix.translate(x, y)
            self.diagram.update_now({item})

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
    def connect_relation(self, data):
        relation = data.draw(self.relations(self.diagram))
        handle = data.draw(sampled_from([relation.head, relation.tail]))
        self._connect_relation(data, relation, handle)

    def _connect_relation(self, data, relation, handle):
        target = data.draw(self.targets(relation, handle))
        with self.transaction:
            connect(relation, handle, target)

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

    @invariant()
    def check_auto_layout(self):
        self.auto_layout.layout(self.diagram)


def ordered(elements: Iterable[Element]) -> list[Element]:
    return sorted(elements, key=lambda e: e.id)
