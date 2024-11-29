"""Transaction support for Gaphor."""

from __future__ import annotations

import logging

from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback

log = logging.getLogger(__name__)


class TransactionError(Exception):
    """Errors related to the transaction module."""


class Transaction:
    """The transaction.

    On start and end of a transaction an event is emitted.
    Transactions can be nested. Events are only emitted when the
    outermost transaction begins and finishes.

    Note that transactions are a global construct.

    >>> import gaphor.core.eventmanager
    >>> event_manager = gaphor.core.eventmanager.EventManager()

    Transactions can be nested. If the outermost transaction is committed or
    rolled back, an event is emitted.

    It's most convenient to use ``Transaction`` as a context manager:

    >>> with Transaction(event_manager) as ctx:
    ...     ... # do actions
    ...     # in case the transaction should be rolled back:
    ...     ctx.rollback()

    Events can be handled programmatically, although this is discouraged:

    >>> tx = Transaction(event_manager)
    >>> tx.commit()

    """

    _stack: list[Transaction] = []

    def __init__(self, event_manager, context=None):
        """Initialize the transaction.

        If this is the first transaction in the stack, a
        :obj:`~gaphor.event.TransactionBegin` event is emitted.
        """
        self.event_manager = event_manager
        self.context = context

        self._need_rollback = False
        if not self._stack:
            self._handle(TransactionBegin(self.context))
        self._stack.append(self)

    def commit(self):
        """Commit the transaction.

        The transaction is closed. A :obj:`~gaphor.event.TransactionCommit` event is emitted.
        If the transaction needs to be rolled back,
        a :obj:`~gaphor.event.TransactionRollback` event is emitted instead.
        """

        self._close()
        if not self._stack:
            if self._need_rollback:
                self._handle(TransactionRollback(self.context))
            else:
                self._handle(TransactionCommit(self.context))

    def rollback(self):
        """Roll-back the transaction.

        First, the transaction is closed.
        A :obj:`~gaphor.event.TransactionRollback` event is emitted.
        """

        self.mark_rollback()
        self.commit()

    @classmethod
    def mark_rollback(cls):
        """Mark the transaction for rollback.

        This operation itself will not close the transaction,
        instead it will allow you to elegantly revert changes.
        """
        for tx in cls._stack:
            tx._need_rollback = True  # noqa: SLF001

    @classmethod
    def in_transaction(cls) -> bool:
        """Are you running inside a transaction?"""
        return bool(cls._stack)

    def _close(self):
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
        """Provide ``with``-statement transaction support."""
        return TransactionContext(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Provide ``with``-statement transaction support.

        If an error occurred, the transaction is rolled back. Otherwise,
        it is committed.
        """

        if exc_type and not self._need_rollback:
            log.error(
                "Transaction terminated due to an exception, performing a rollback",
            )
            self.mark_rollback()
        self.commit()


class TransactionContext:
    """A simple context for a transaction.

    Can only perform a rollback.
    """

    def __init__(self, tx: Transaction) -> None:
        self._tx = tx

    def rollback(self) -> None:
        self._tx.mark_rollback()
