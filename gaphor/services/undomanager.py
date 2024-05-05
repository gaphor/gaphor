"""Undo management for Gaphor.

Undoing and redoing actions is managed through the UndoManager.

An undo action should be a callable object (called with no arguments).

An undo action should return a callable object that acts as redo function.
If None is returned the undo action is considered to be the redo action as well.

NOTE: it would be nice to use actions in conjunction with functools.partial.
"""

import logging
from typing import Callable, List

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
    ModelFlushed,
    ModelReady,
    RevertibleEvent,
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
from gaphor.transaction import Transaction

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

    def execute(self):
        self._actions.reverse()

        for act in self._actions:
            logger.debug(act.__doc__)
            act()


class UndoManagerStateChanged(ServiceEvent):
    """Event class used to send state changes on the Undo Manager."""


class _UndoManagerTransactionCommitted:
    """A transaction was committed.

    This is a subsequent event that triggers the actual commit.
    In doing so we allow other parties to handle their commit handlers first.
    """

    def __init__(self, context):
        self.context = context


class _UndoManagerTransactionRolledBack:
    """A transaction has to be rolled back."""

    def __init__(self, context):
        self.context = context


class NotInTransactionException(Exception):
    """Raised when changes occur outside a transaction."""


class UndoManager(Service, ActionProvider):
    """Simple transaction manager for Gaphor. This transaction manager supports
    nested transactions.

    The Undo manager sports an undo and a redo stack. Each stack
    contains a set of actions that can be executed, just by calling them
    (e.i action()) If something is returned by an action, that is
    considered the callable to be used to undo or redo the last
    performed action.

    Change events (attribute/association updates) are handled with priority
    by the undo manager. This is done, so that, if a transaction is rolled back,
    all changes that have been applied are rolled back. This prevents events from
    being delayed because of exceptions that occur in some other event handler.
    """

    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory: RepositoryProtocol = element_factory
        self._undo_stack: List[ActionStack] = []
        self._redo_stack: List[ActionStack] = []
        self._stack_depth = 20
        self._current_transaction = None

        event_manager.subscribe(self.ready)
        event_manager.subscribe(self.reset)
        event_manager.priority_subscribe(self.begin_transaction)
        event_manager.subscribe(self.commit_transaction)
        event_manager.subscribe(self.rollback_transaction)
        event_manager.subscribe(self._on_transaction_commit)
        event_manager.subscribe(self._on_transaction_rollback)

        event_manager.priority_subscribe(self.undo_reversible_event)
        event_manager.priority_subscribe(self.undo_create_element_event)
        event_manager.priority_subscribe(self.undo_delete_element_event)
        event_manager.priority_subscribe(self.undo_attribute_change_event)
        event_manager.priority_subscribe(self.undo_association_set_event)
        event_manager.priority_subscribe(self.undo_association_add_event)
        event_manager.priority_subscribe(self.undo_association_delete_event)
        self._action_executed()

    def shutdown(self):
        self.event_manager.unsubscribe(self.ready)
        self.event_manager.unsubscribe(self.reset)
        self.event_manager.unsubscribe(self.begin_transaction)
        self.event_manager.unsubscribe(self.commit_transaction)
        self.event_manager.unsubscribe(self.rollback_transaction)
        self.event_manager.unsubscribe(self._on_transaction_commit)
        self.event_manager.unsubscribe(self._on_transaction_rollback)

        self.event_manager.unsubscribe(self.undo_reversible_event)
        self.event_manager.unsubscribe(self.undo_create_element_event)
        self.event_manager.unsubscribe(self.undo_delete_element_event)
        self.event_manager.unsubscribe(self.undo_attribute_change_event)
        self.event_manager.unsubscribe(self.undo_association_set_event)
        self.event_manager.unsubscribe(self.undo_association_add_event)
        self.event_manager.unsubscribe(self.undo_association_delete_event)

    def clear_undo_stack(self):
        del self._undo_stack[:]

    def clear_redo_stack(self):
        del self._redo_stack[:]

    @event_handler(ModelReady)
    def ready(self, _event=None):
        self._action_executed(state_changed=False)

    @event_handler(ModelFlushed)
    def reset(self, _event=None):
        assert not self._current_transaction

        self.clear_redo_stack()
        self.clear_undo_stack()
        self._action_executed(state_changed=False)

    @event_handler(TransactionBegin)
    def begin_transaction(self, event=None):
        """Add an action to the current transaction."""
        assert not self._current_transaction
        self._current_transaction = ActionStack()

    def add_undo_action(self, action):
        """Add an action to undo."""
        if self._current_transaction:
            self._current_transaction.add(action)
            self._action_executed()
        else:
            with Transaction(self.event_manager, context="rollback"):
                action()

            raise NotInTransactionException(
                f"Updating state outside of a transaction: {action.__doc__}."
            )

    @event_handler(TransactionCommit)
    def _on_transaction_commit(self, event: TransactionCommit):
        self.event_manager.handle(_UndoManagerTransactionCommitted(event.context))

    @event_handler(_UndoManagerTransactionCommitted)
    def commit_transaction(self, event: _UndoManagerTransactionCommitted | None = None):
        assert self._current_transaction

        if event is None:
            event = _UndoManagerTransactionCommitted(None)

        if event.context != "rollback" and self._current_transaction.can_execute():
            if event.context == "undo":
                self._redo_stack.append(self._current_transaction)
            else:
                if event.context != "redo":
                    self.clear_redo_stack()
                self._undo_stack.append(self._current_transaction)
                while len(self._undo_stack) > self._stack_depth:
                    del self._undo_stack[0]

        self._current_transaction = None

        self._action_executed()

    @event_handler(TransactionRollback)
    def _on_transaction_rollback(self, event: TransactionRollback):
        self.event_manager.handle(_UndoManagerTransactionRolledBack(event.context))

    @event_handler(_UndoManagerTransactionRolledBack)
    def rollback_transaction(self, event=None):
        """Roll back the transaction we're in."""
        assert self._current_transaction

        if event and event.context in ("undo", "redo", "rollback"):
            logger.error(
                "Already performing %s, ignoring additional rollback events",
                event.context,
            )
            return

        erroneous_tx = self._current_transaction
        self._current_transaction = None
        with Transaction(self.event_manager, context="rollback"):
            try:
                erroneous_tx.execute()
            except Exception:
                logger.error("Could not rollback transaction", exc_info=True)
                raise

        self._action_executed()

    @action(name="edit-undo", shortcut="<Primary>z")
    def undo_transaction(self):
        if not self._undo_stack:
            return

        if self._current_transaction:
            logger.warning("Trying to undo a transaction, while in a transaction")
            self.commit_transaction()

        transaction = self._undo_stack.pop()
        with Transaction(self.event_manager, context="undo"):
            transaction.execute()

        self._action_executed()

    @action(
        name="edit-redo",
        shortcut="<Primary><Shift>z",
    )
    def redo_transaction(self):
        if not self._redo_stack:
            return

        assert not self._current_transaction

        transaction = self._redo_stack.pop()
        with Transaction(self.event_manager, context="redo"):
            transaction.execute()

        self._action_executed()

    def can_undo(self):
        return bool(self._current_transaction or self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)

    def _action_executed(self, state_changed=True):
        self.event_manager.handle(ActionEnabled("win.edit-undo", self.can_undo()))
        self.event_manager.handle(ActionEnabled("win.edit-redo", self.can_redo()))
        if state_changed:
            self.event_manager.handle(UndoManagerStateChanged(self))

    def lookup(self, id: str) -> Element:
        if element := self.element_factory.lookup(id):
            return element
        else:
            raise ValueError(f"Element with id {id} not found in model")

    #
    # Undo Handlers
    #

    @event_handler(RevertibleEvent)
    def undo_reversible_event(self, event: RevertibleEvent):
        element_id = event.element.id

        def undo_reversible_event():
            element = self.lookup(element_id)
            event.revert(element)

        undo_reversible_event.__doc__ = (
            f"Reverse event {event.__class__.__name__} for element {event.element}."
        )

        self.add_undo_action(undo_reversible_event)

    @event_handler(ElementCreated)
    def undo_create_element_event(self, event: ElementCreated):
        element_id = event.element.id

        def undo_create_event():
            element = self.lookup(element_id)
            element.unlink()

        undo_create_event.__doc__ = f"Undo create element {event.element}."
        del event

        self.add_undo_action(undo_create_event)

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

            def undo_delete_event():
                # If diagram is not there, for some reason, recreate it.
                # It's probably removed in the same transaction.
                try:
                    diagram: Diagram = self.lookup(diagram_id)  # type: ignore[assignment]
                except ValueError:
                    diagram = self.element_factory.create_as(Diagram, diagram_id)

                element = diagram.create_as(element_type, element_id)
                for name, ser in data.items():
                    for value in deserialize(ser, lambda ref: None):
                        element.load(name, value)

        else:

            def undo_delete_event():
                self.element_factory.create_as(element_type, element_id)

        undo_delete_event.__doc__ = f"Recreate element {element_type} ({element_id})."
        del event

        self.add_undo_action(undo_delete_event)

    @event_handler(AttributeUpdated)
    def undo_attribute_change_event(self, event: AttributeUpdated):
        attribute = event.property
        element_id = event.element.id
        value = event.old_value

        def undo_attribute_change_event():
            element = self.lookup(element_id)
            attribute.set(element, value)

        undo_attribute_change_event.__doc__ = (
            f"Revert {event.element}.{attribute.name} to {value}."
        )
        del event

        self.add_undo_action(undo_attribute_change_event)

    @event_handler(AssociationSet)
    def undo_association_set_event(self, event: AssociationSet):
        association = event.property
        if type(association) is not association_property:
            return
        element_id = event.element.id
        value_id = event.old_value and event.old_value.id

        def undo_association_set_event():
            element = self.lookup(element_id)
            value = value_id and self.lookup(value_id)
            association.set(element, value, from_opposite=True)

        undo_association_set_event.__doc__ = (
            f"Revert {event.element}.{association.name} to {event.old_value}."
        )
        del event

        self.add_undo_action(undo_association_set_event)

    @event_handler(AssociationAdded)
    def undo_association_add_event(self, event: AssociationAdded):
        association = event.property
        if type(association) is not association_property:
            return
        element_id = event.element.id
        value_id = event.new_value.id

        def undo_association_add_event():
            element = self.lookup(element_id)
            value = self.lookup(value_id)
            association.delete(element, value, from_opposite=True)

        undo_association_add_event.__doc__ = (
            f"{event.element}.{association.name} delete {event.new_value}."
        )
        del event

        self.add_undo_action(undo_association_add_event)

    @event_handler(AssociationDeleted)
    def undo_association_delete_event(self, event: AssociationDeleted):
        association = event.property
        if type(association) is not association_property:
            return
        element_id = event.element.id
        value_id = event.old_value.id
        index = event.index

        def undo_association_delete_event():
            element = self.lookup(element_id)
            value = self.lookup(value_id)
            association.set(element, value, index=index, from_opposite=True)

        undo_association_delete_event.__doc__ = (
            f"{event.element}.{association.name} add {event.old_value}."
        )
        del event

        self.add_undo_action(undo_association_delete_event)
