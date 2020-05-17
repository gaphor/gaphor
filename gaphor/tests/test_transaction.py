"""Unit tests for transactions in Gaphor."""
import pytest

from gaphor.core import event_handler
from gaphor.core.eventmanager import EventManager
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback
from gaphor.transaction import Transaction, TransactionError

begins = []
commits = []
rollbacks = []


@event_handler(TransactionBegin)
def handle_begins(event):
    """Store TransactionBegin events in begins."""
    begins.append(event)


@event_handler(TransactionCommit)
def handle_commits(event):
    """Store TransactionCommit events in commits."""
    commits.append(event)


@event_handler(TransactionRollback)
def handle_rollback(event):
    """Store TransactionRollback events in rollbacks."""
    rollbacks.append(event)


@pytest.fixture
def event_manager():
    event_manager = EventManager()

    event_manager.subscribe(handle_begins)
    event_manager.subscribe(handle_commits)
    event_manager.subscribe(handle_rollback)

    del begins[:]
    del commits[:]
    del rollbacks[:]

    yield event_manager

    event_manager.unsubscribe(handle_begins)
    event_manager.unsubscribe(handle_commits)
    event_manager.unsubscribe(handle_rollback)


def test_transaction_commit(event_manager):
    """Test committing a transaction."""

    tx = Transaction(event_manager)

    assert tx._stack, "Transaction has no stack"
    assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
    assert 0 == len(commits), "Incorrect number of TransactionCommit events"
    assert 0 == len(rollbacks), "Incorrect number of TransactionRollback events"

    tx.commit()

    assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
    assert 1 == len(commits), "Incorrect number of TransactionCommit events"
    assert 0 == len(rollbacks), "Incorrect number of TransactionRollback events"
    assert not tx._stack, "Transaction stack is not empty"

    with pytest.raises(TransactionError):
        tx.commit()


def test_transaction_rollback(event_manager):
    """Test rolling back a transaction."""

    tx = Transaction(event_manager)

    assert tx._stack, "Transaction has no stack"
    assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
    assert 0 == len(commits), "Incorrect number of TransactionCommit events"
    assert 0 == len(rollbacks), "Incorrect number of TransactionRollback events"

    tx.rollback()

    assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
    assert 0 == len(commits), "Incorrect number of TransactionCommit events"
    assert 1 == len(rollbacks), "Incorrect number of TransactionRollback events"

    assert not tx._stack, "Transaction stack is not empty"


def test_transaction_commit_after_rollback(event_manager):
    """Test committing one transaction after rolling back another
    transaction."""

    tx1 = Transaction(event_manager)
    tx2 = Transaction(event_manager)

    tx2.rollback()
    tx1.commit()

    assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
    assert 0 == len(commits), "Incorrect number of TransactionCommit events"
    assert 1 == len(rollbacks), "Incorrect number of TransactionRollback events"


def test_transaction_rollback_after_commit(event_manager):
    """Test committing one transaction after rolling back another
    transaction."""

    tx1 = Transaction(event_manager)
    tx2 = Transaction(event_manager)

    tx2.commit()
    tx1.rollback()

    assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
    assert 0 == len(commits), "Incorrect number of TransactionCommit events"
    assert 1 == len(rollbacks), "Incorrect number of TransactionRollback events"


def test_transaction_stack(event_manager):
    """Test the transaction stack."""

    tx1 = Transaction(event_manager)
    tx2 = Transaction(event_manager)

    with pytest.raises(TransactionError):
        tx1.commit()

    tx2.rollback()
    tx1.rollback()


def test_transaction_context(event_manager):
    """Test the transaction context manager."""

    with Transaction(event_manager) as tx:

        assert isinstance(tx, Transaction), "Context is not a Transaction instance"
        assert Transaction._stack, "Transaction instance has no stack inside a context"

    assert not Transaction._stack, "Transaction stack should be empty"


def test_transaction_context_error(event_manager):
    """Test the transaction context manager with errors."""

    with pytest.raises(TypeError, match="transaction error"):
        with Transaction(event_manager):
            raise TypeError("transaction error")
