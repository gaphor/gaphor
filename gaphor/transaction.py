"""Transaction support for Gaphor."""

from __future__ import annotations

import logging
from typing import Callable

from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback

log = logging.getLogger(__name__)


class TransactionError(Exception):
    """Errors related to the transaction module."""


class Transaction:
    """The transaction. On start and end of a transaction an event is emitted.

    >>> import gaphor.core.eventmanager
    >>> event_manager = gaphor.core.eventmanager.EventManager()

    Transactions can be nested. If the outermost transaction is committed or
    rolled back, an event is emitted.

    Events can be handled programmatically:

    >>> tx = Transaction(event_manager)
    >>> tx.commit()

    It can be assigned as decorator:

    >>> @transactional
    ... def foo():
    ...     pass

    Or with the ``with`` statement:

    >>> with Transaction(event_manager):
    ...     pass
    """

    _stack: list = []

    def __init__(self, event_manager):
        """Initialize the transaction.

        If this is the first transaction in the stack, a
        TransactionBegin event is emitted.
        """
        self.event_manager = event_manager

        self._need_rollback = False
        if not self._stack:
            self._handle(TransactionBegin())
        self._stack.append(self)

    def commit(self):
        """Commit the transaction.

        First, the transaction is closed. If it needs to be rolled-back,
        a TransactionRollback event is emitted. Otherwise, a
        TransactionCommit event is emitted.
        """
        self._close()
        if not self._stack:
            if self._need_rollback:
                self._handle(TransactionRollback())
            else:
                self._handle(TransactionCommit())

    def rollback(self):
        """Roll-back the transaction.

        First, the transaction is closed. Every transaction on the stack
        is then marked for roll-back.  If the stack is empty, a
        TransactionRollback event is emitted.
        """
        self._close()
        if not self._stack:
            self._handle(TransactionRollback())
        else:
            self.mark_rollback()

    def mark_rollback(self):
        for tx in self._stack:
            tx._need_rollback = True

    def _close(self):
        """Close the transaction.

        If the stack is empty, a TransactionError is raised.  If the
        last transaction on the stack isn't this transaction, a
        Transaction error is raised.
        """
        try:
            last = self._stack.pop()
        except IndexError:
            raise TransactionError("No Transaction on stack.") from None
        if last is not self:
            self._stack.append(last)
            raise TransactionError(
                "Transaction on stack is not the transaction being closed."
            )

    def _handle(self, event):
        self.event_manager.handle(event)

    def __enter__(self) -> TransactionContext:
        """Provide with-statement transaction support."""
        return TransactionContext(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Provide with-statement transaction support.

        If an error occurred, the transaction is rolled back. Otherwise,
        it is committed.
        """
        if exc_type:
            if not self._need_rollback:
                log.error(
                    "Transaction terminated due to an exception, performing a rollback",
                )
            try:
                self.rollback()
            except Exception:
                log.error("Rollback failed", exc_info=True)
                raise
        else:
            self.commit()


class TransactionContext:
    """A simple context for a transaction.

    Can only perform a rollback.
    """

    def __init__(self, tx: Transaction) -> None:
        self._tx = tx

    def rollback(self) -> None:
        self._tx.mark_rollback()


# Add a `handler(event) -> None` to receive events emitted via @transactional
subscribers: set[Callable[[object], None]] = set()


def transactional(func):
    """The transactional decorator makes a function transactional. Events are
    emitted through the (global) `subscribers` set.

    It is preferred to use the `Transaction` context manager. The
    context manager emits events in the context of the session in scope,
    whereas the `@transactional` decorator emits a global event which is
    sent to the active session.
    """
    def _transactional(*args, **kwargs):
        if __debug__ and args and hasattr(args[0], "event_manager"):
            log.warning(f"Consider using the Transaction context manager for {args[0]}")

        with Transaction(_SubscribersHandler):
            return func(*args, **kwargs)

    return _transactional


class _SubscribersHandler:
    @classmethod
    def handle(cls, event):
        global subscribers
        for o in subscribers:
            o(event)
