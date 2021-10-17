"""Undo management for Gaphor.

Undoing and redoing actions is managed through the UndoManager.

An undo action should be a callable object (called with no arguments).

An undo action should return a callable object that acts as redo function.
If None is returned the undo action is considered to be the redo action as well.

NOTE: it would be nice to use actions in conjunction with functools.partial.
"""

import logging
from typing import Callable, List, Optional

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.core.modeling.diagram import Diagram
from gaphor.core.modeling.element import Element, RepositoryProtocol
from gaphor.core.modeling.event import (
    AssociationAdded,
    AssociationDeleted,
    AssociationSet,
    AttributeUpdated,
    ElementCreated,
    ElementDeleted,
    ModelReady,
    RevertibeEvent,
)
from gaphor.core.modeling.presentation import Presentation
from gaphor.core.modeling.properties import association as association_property
from gaphor.diagram.copypaste import deserialize, serialize
from gaphor.event import (
    ActionEnabled,
    ServiceEvent,
    TransactionBegin,
    TransactionCommit,
    TransactionRollback,
)
from gaphor.transaction import Transaction, transactional

logger = logging.getLogger(__name__)


class ActionStack:
    """A transaction.

    Every action that is added between a begin_transaction() and a
    commit_transaction() call is recorded in a transaction, so it can be
    played back when a transaction is executed. This executing a
    transaction has the effect of performing the actions recorded, which
    will typically undo actions performed by the user.
    """

    def __init__(self):
        self._actions: List[Callable[[], None]] = []

    def add(self, action):
        self._actions.append(action)

    def can_execute(self):
        return bool(self._actions)

    @transactional
    def execute(self):
        self._actions.reverse()
        self._actions.sort(key=lambda fn: fn.__name__)

        for act in self._actions:
            logger.debug(act.__doc__)
            act()


class UndoManagerStateChanged(ServiceEvent):
    """Event class used to send state changes on the Undo Manager."""


class NotInTransactionException(Exception):
    """Raised when changes occur outside of a transaction."""


class UndoManager(Service, ActionProvider):
    """Simple transaction manager for Gaphor. This transaction manager supports
    nested transactions.

    The Undo manager sports an undo and a redo stack. Each stack
    contains a set of actions that can be executed, just by calling them
    (e.i action()) If something is returned by an action, that is
    considered the callable to be used to undo or redo the last
    performed action.
    """

    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory: RepositoryProtocol = element_factory
        self._undo_stack: List[ActionStack] = []
        self._redo_stack: List[ActionStack] = []
        self._stack_depth = 20
        self._current_transaction = None
        self._undoing = 0

        event_manager.subscribe(self.reset)
        event_manager.subscribe(self.begin_transaction)
        event_manager.subscribe(self.commit_transaction)
        event_manager.subscribe(self.rollback_transaction)
        self._register_undo_handlers()
        self._action_executed()

    def shutdown(self):
        self.event_manager.unsubscribe(self.reset)
        self.event_manager.unsubscribe(self.begin_transaction)
        self.event_manager.unsubscribe(self.commit_transaction)
        self.event_manager.unsubscribe(self.rollback_transaction)
        self._unregister_undo_handlers()

    def clear_undo_stack(self):
        self._undo_stack = []
        self._current_transaction = None

    def clear_redo_stack(self):
        del self._redo_stack[:]

    @event_handler(ModelReady)
    def reset(self, event=None):
        self.clear_redo_stack()
        self.clear_undo_stack()
        self._action_executed()

    @event_handler(TransactionBegin)
    def begin_transaction(self, event=None):
        """Add an action to the current transaction."""
        assert not self._current_transaction
        self._current_transaction = ActionStack()

    def add_undo_action(self, action, requires_transaction=True):
        """Add an action to undo."""
        if self._current_transaction:
            self._current_transaction.add(action)
            self._action_executed()
        elif requires_transaction:
            undo_stack = list(self._undo_stack)
            redo_stack = list(self._redo_stack)

            try:
                with Transaction(self.event_manager):
                    action()
            finally:
                # Restore stacks and act like nothing happened
                self._redo_stack = redo_stack
                self._undo_stack = undo_stack

            raise NotInTransactionException("Updating state outside of a transaction.")

    @event_handler(TransactionCommit)
    def commit_transaction(self, event=None):
        assert self._current_transaction

        if self._current_transaction.can_execute():
            self.clear_redo_stack()
            self._undo_stack.append(self._current_transaction)
            while len(self._undo_stack) > self._stack_depth:
                del self._undo_stack[0]

        self._current_transaction = None

        self._action_executed()

    @event_handler(TransactionRollback)
    def rollback_transaction(self, event=None):
        """Roll back the transaction we're in."""
        assert self._current_transaction

        # Store stacks
        undo_stack = list(self._undo_stack)

        erroneous_tx = self._current_transaction
        self._current_transaction = None
        try:
            with Transaction(self.event_manager):
                try:
                    erroneous_tx.execute()
                except Exception:
                    logger.error("Could not rollback transaction", exc_info=True)
        finally:
            # Discard all data collected in the rollback "transaction"
            self._undo_stack = undo_stack

        self._action_executed()

    def discard_transaction(self):

        self._current_transaction = None

        self._action_executed()

    @action(name="edit-undo", shortcut="<Primary>z")
    def undo_transaction(self):
        if not self._undo_stack:
            return

        if self._current_transaction:
            logger.warning("Trying to undo a transaction, while in a transaction")
            self.commit_transaction()
        transaction = self._undo_stack.pop()

        # Store stacks
        undo_stack = list(self._undo_stack)
        redo_stack = list(self._redo_stack)
        self._undo_stack = []

        try:
            self._undoing += 1
            with Transaction(self.event_manager):
                transaction.execute()
        finally:
            # Restore stacks and put latest tx on the redo stack
            self._redo_stack = redo_stack
            if self._undo_stack:
                self._redo_stack.extend(self._undo_stack)
            self._undo_stack = undo_stack
            self._undoing -= 1

        while len(self._redo_stack) > self._stack_depth:
            del self._redo_stack[0]

        self._action_executed()

    @action(
        name="edit-redo",
        shortcut="<Primary><Shift>z",
    )
    def redo_transaction(self):
        if not self._redo_stack:
            return

        transaction = self._redo_stack.pop()

        redo_stack = list(self._redo_stack)
        try:
            self._undoing += 1
            with Transaction(self.event_manager):
                transaction.execute()
        finally:
            self._redo_stack = redo_stack
            self._undoing -= 1

        self._action_executed()

    def in_transaction(self):
        """The undo manager is recording changes."""
        return self._current_transaction is not None

    def in_undo_transaction(self):
        """An undo or redo action is currently performed."""
        return bool(self._undoing)

    def can_undo(self):
        return bool(self._current_transaction or self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)

    def _action_executed(self, event=None):
        self.event_manager.handle(ActionEnabled("win.edit-undo", self.can_undo()))
        self.event_manager.handle(ActionEnabled("win.edit-redo", self.can_redo()))
        self.event_manager.handle(UndoManagerStateChanged(self))

    def lookup(self, id: str) -> Element:
        element: Optional[Element] = self.element_factory.lookup(id)
        if not element:
            raise ValueError(f"Element with id {id} not found in model")
        return element

    #
    # Undo Handlers
    #

    def _register_undo_handlers(self):

        logger.debug("Registering undo handlers")

        self.event_manager.subscribe(self.undo_reversible_event)
        self.event_manager.subscribe(self.undo_create_element_event)
        self.event_manager.subscribe(self.undo_delete_element_event)
        self.event_manager.subscribe(self.undo_attribute_change_event)
        self.event_manager.subscribe(self.undo_association_set_event)
        self.event_manager.subscribe(self.undo_association_add_event)
        self.event_manager.subscribe(self.undo_association_delete_event)

    def _unregister_undo_handlers(self):

        logger.debug("Unregistering undo handlers")

        self.event_manager.unsubscribe(self.undo_reversible_event)
        self.event_manager.unsubscribe(self.undo_create_element_event)
        self.event_manager.unsubscribe(self.undo_delete_element_event)
        self.event_manager.unsubscribe(self.undo_attribute_change_event)
        self.event_manager.unsubscribe(self.undo_association_set_event)
        self.event_manager.unsubscribe(self.undo_association_add_event)
        self.event_manager.unsubscribe(self.undo_association_delete_event)

    @event_handler(RevertibeEvent)
    def undo_reversible_event(self, event: RevertibeEvent):
        element_id = event.element.id

        def b_undo_reversible_event():
            element = self.lookup(element_id)
            event.revert(element)

        b_undo_reversible_event.__doc__ = (
            f"Reverse event {event.__class__.__name__} for element {event.element}."
        )

        self.add_undo_action(
            b_undo_reversible_event, requires_transaction=event.requires_transaction
        )

    @event_handler(ElementCreated)
    def undo_create_element_event(self, event: ElementCreated):
        element_id = event.element.id

        def d_undo_create_event():
            element = self.lookup(element_id)
            element.unlink()

        d_undo_create_event.__doc__ = f"Undo create element {event.element}."
        del event

        self.add_undo_action(d_undo_create_event)

    @event_handler(ElementDeleted)
    def undo_delete_element_event(self, event: ElementDeleted):
        element_type = type(event.element)
        element_id = event.element.id

        if isinstance(event.element, Presentation):
            diagram_id = event.diagram.id
            data = {}

            def save_func(name, value):
                data[name] = serialize(value)

            event.element.save(save_func)

            def b_undo_delete_event():
                diagram: Diagram = self.lookup(diagram_id)  # type: ignore[assignment]
                element = diagram.create_as(element_type, element_id)
                for name, ser in data.items():
                    for value in deserialize(ser, lambda ref: None):
                        element.load(name, value)

            undo_delete_event = b_undo_delete_event
        else:

            def a_undo_delete_event():
                self.element_factory.create_as(element_type, element_id)

            undo_delete_event = a_undo_delete_event

        undo_delete_event.__doc__ = f"Recreate element {element_type} ({element_id})."
        del event

        self.add_undo_action(undo_delete_event)

    @event_handler(AttributeUpdated)
    def undo_attribute_change_event(self, event: AttributeUpdated):
        attribute = event.property
        element_id = event.element.id
        value = event.old_value

        def c_undo_attribute_change_event():
            element = self.lookup(element_id)
            attribute._set(element, value)

        c_undo_attribute_change_event.__doc__ = (
            f"Revert {event.element}.{attribute.name} to {value}."
        )
        del event

        self.add_undo_action(c_undo_attribute_change_event)

    @event_handler(AssociationSet)
    def undo_association_set_event(self, event: AssociationSet):
        association = event.property
        if type(association) is not association_property:
            return
        element_id = event.element.id
        value_id = event.old_value and event.old_value.id

        def c_undo_association_set_event():
            element = self.lookup(element_id)
            value = value_id and self.lookup(value_id)
            association._set(element, value, from_opposite=True)

        c_undo_association_set_event.__doc__ = (
            f"Revert {event.element}.{association.name} to {event.old_value}."
        )
        del event

        self.add_undo_action(c_undo_association_set_event)

    @event_handler(AssociationAdded)
    def undo_association_add_event(self, event: AssociationAdded):
        association = event.property
        if type(association) is not association_property:
            return
        element_id = event.element.id
        value_id = event.new_value.id

        def c_undo_association_add_event():
            element = self.lookup(element_id)
            value = self.lookup(value_id)
            association._del(element, value, from_opposite=True)

        c_undo_association_add_event.__doc__ = (
            f"{event.element}.{association.name} delete {event.new_value}."
        )
        del event

        self.add_undo_action(c_undo_association_add_event)

    @event_handler(AssociationDeleted)
    def undo_association_delete_event(self, event: AssociationDeleted):
        association = event.property
        if type(association) is not association_property:
            return
        element_id = event.element.id
        value_id = event.old_value.id

        def c_undo_association_delete_event():
            element = self.lookup(element_id)
            value = self.lookup(value_id)
            association._set(element, value, from_opposite=True)

        c_undo_association_delete_event.__doc__ = (
            f"{event.element}.{association.name} add {event.old_value}."
        )
        del event

        self.add_undo_action(c_undo_association_delete_event)
