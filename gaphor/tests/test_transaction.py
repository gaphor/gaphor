"""Unit tests for transactions in Gaphor."""

from unittest import TestCase

from gaphor.core import Application, event_handler
from gaphor.transaction import Transaction, transactional, TransactionError
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback

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

        Application.init(services=["component_registry"])

        component_registry = Application.get_service("component_registry")

        component_registry.register_handler(handle_begins)
        component_registry.register_handler(handle_commits)
        component_registry.register_handler(handle_rollback)

        del begins[:]
        del commits[:]
        del rollbacks[:]

    def tearDown(self):
        """Finished with the test case.  Unregister event handlers that
        store transaction events."""

        component_registry = Application.get_service("component_registry")

        component_registry.unregister_handler(handle_begins)
        component_registry.unregister_handler(handle_commits)
        component_registry.unregister_handler(handle_rollback)

    def test_transaction_commit(self):
        """Test committing a transaction."""

        tx = Transaction()

        self.assertTrue(tx._stack, "Transaction has no stack")
        self.assertEqual(1, len(begins), "Incorrect number of TrasactionBegin events")
        self.assertEqual(
            0, len(commits), "Incorrect number of TransactionCommit events"
        )
        self.assertEqual(
            0, len(rollbacks), "Incorrect number of TransactionRollback events"
        )

        tx.commit()

        self.assertEqual(1, len(begins), "Incorrect number of TrasactionBegin events")
        self.assertEqual(
            1, len(commits), "Incorrect number of TransactionCommit events"
        )
        self.assertEqual(
            0, len(rollbacks), "Incorrect number of TransactionRollback events"
        )
        self.assertFalse(tx._stack, "Transaction stack is not empty")

        try:
            tx.commit()
        except TransactionError:
            pass
        else:
            self.fail("Commit should not have succeeded")

    def test_transaction_rollback(self):
        """Test rolling back a transaction."""

        tx = Transaction()

        self.assertTrue(tx._stack, "Transaction has no stack")
        self.assertEqual(1, len(begins), "Incorrect number of TrasactionBegin events")
        self.assertEqual(
            0, len(commits), "Incorrect number of TransactionCommit events"
        )
        self.assertEqual(
            0, len(rollbacks), "Incorrect number of TransactionRollback events"
        )

        tx.rollback()

        self.assertEqual(1, len(begins), "Incorrect number of TrasactionBegin events")
        self.assertEqual(
            0, len(commits), "Incorrect number of TransactionCommit events"
        )
        self.assertEqual(
            1, len(rollbacks), "Incorrect number of TransactionRollback events"
        )

        self.assertFalse(tx._stack, "Transaction stack is not empty")

    def test_transaction_commit_after_rollback(self):
        """Test committing one transaction after rolling back another
        transaction."""

        tx1 = Transaction()
        tx2 = Transaction()

        tx2.rollback()
        tx1.commit()

        self.assertEqual(1, len(begins), "Incorrect number of TrasactionBegin events")
        self.assertEqual(
            0, len(commits), "Incorrect number of TransactionCommit events"
        )
        self.assertEqual(
            1, len(rollbacks), "Incorrect number of TransactionRollback events"
        )

    def test_transaction_stack(self):
        """Test the transaction stack."""

        tx1 = Transaction()
        tx2 = Transaction()

        try:
            self.assertRaises(TransactionError, tx1.commit)
        finally:
            tx2.rollback()
            tx1.rollback()

    def test_transaction_context(self):
        """Test the transaction context manager."""

        with Transaction() as tx:

            self.assertTrue(
                isinstance(tx, Transaction), "Context is not a Transaction instance"
            )
            self.assertTrue(
                Transaction._stack, "Transaction instance has no stack inside a context"
            )

        self.assertFalse(Transaction._stack, "Transaction stack should be empty")

    def test_transaction_context_error(self):
        """Test the transaction context manager with errors."""

        try:
            with Transaction():
                raise TypeError("transaction error")
        except TypeError as e:
            self.assertEqual(
                "transaction error",
                str(e),
                "Transaction context manager did no raise correct exception",
            )
        else:
            self.fail(
                "Transaction context manager did not raise exception when it should have"
            )


class TransactionWithoutComponentRegistryTestCase(TestCase):
    """Test case for transactions with no component registry."""

    def test_transaction(self):
        """Test basic transaction functionality."""

        tx = Transaction()
        tx.rollback()

        tx = Transaction()
        tx.commit()
