"""Unit tests for transactions in Gaphor."""

from unittest import TestCase

from gaphor.core import event_handler
from gaphor.transaction import Transaction, TransactionError
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback
from gaphor.services.eventmanager import EventManager


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


class TransactionTestCase(TestCase):
    """Test case for transactions with the component registry
    enabled."""

    def setUp(self):
        """Initialize Gaphor services and register transaction event
        handlers."""

        self.event_manager = EventManager()

        self.event_manager.subscribe(handle_begins)
        self.event_manager.subscribe(handle_commits)
        self.event_manager.subscribe(handle_rollback)

        del begins[:]
        del commits[:]
        del rollbacks[:]

    def tearDown(self):
        """Finished with the test case.  Unregister event handlers that
        store transaction events."""

        self.event_manager.unsubscribe(handle_begins)
        self.event_manager.unsubscribe(handle_commits)
        self.event_manager.unsubscribe(handle_rollback)

    def test_transaction_commit(self):
        """Test committing a transaction."""

        tx = Transaction(self.event_manager)

        assert tx._stack, "Transaction has no stack"
        assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
        assert 0 == len(commits), "Incorrect number of TransactionCommit events"
        assert 0 == len(rollbacks), "Incorrect number of TransactionRollback events"

        tx.commit()

        assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
        assert 1 == len(commits), "Incorrect number of TransactionCommit events"
        assert 0 == len(rollbacks), "Incorrect number of TransactionRollback events"
        assert not tx._stack, "Transaction stack is not empty"

        try:
            tx.commit()
        except TransactionError:
            pass
        else:
            self.fail("Commit should not have succeeded")

    def test_transaction_rollback(self):
        """Test rolling back a transaction."""

        tx = Transaction(self.event_manager)

        assert tx._stack, "Transaction has no stack"
        assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
        assert 0 == len(commits), "Incorrect number of TransactionCommit events"
        assert 0 == len(rollbacks), "Incorrect number of TransactionRollback events"

        tx.rollback()

        assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
        assert 0 == len(commits), "Incorrect number of TransactionCommit events"
        assert 1 == len(rollbacks), "Incorrect number of TransactionRollback events"

        assert not tx._stack, "Transaction stack is not empty"

    def test_transaction_commit_after_rollback(self):
        """Test committing one transaction after rolling back another
        transaction."""

        tx1 = Transaction(self.event_manager)
        tx2 = Transaction(self.event_manager)

        tx2.rollback()
        tx1.commit()

        assert 1 == len(begins), "Incorrect number of TrasactionBegin events"
        assert 0 == len(commits), "Incorrect number of TransactionCommit events"
        assert 1 == len(rollbacks), "Incorrect number of TransactionRollback events"

    def test_transaction_stack(self):
        """Test the transaction stack."""

        tx1 = Transaction(self.event_manager)
        tx2 = Transaction(self.event_manager)

        try:
            self.assertRaises(TransactionError, tx1.commit)
        finally:
            tx2.rollback()
            tx1.rollback()

    def test_transaction_context(self):
        """Test the transaction context manager."""

        with Transaction(self.event_manager) as tx:

            assert isinstance(tx, Transaction), "Context is not a Transaction instance"
            assert (
                Transaction._stack
            ), "Transaction instance has no stack inside a context"

        assert not Transaction._stack, "Transaction stack should be empty"

    def test_transaction_context_error(self):
        """Test the transaction context manager with errors."""

        try:
            with Transaction(self.event_manager):
                raise TypeError("transaction error")
        except TypeError as e:
            assert "transaction error" == str(
                e
            ), "Transaction context manager did no raise correct exception"
        else:
            self.fail(
                "Transaction context manager did not raise exception when it should have"
            )
